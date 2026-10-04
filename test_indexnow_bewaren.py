"""IndexNow-uitkomsten bewaren (indexnow.py, app.py): de kolom 'soort' komt
erbij op een bestaande tabel, en de melding na een adresopschoning wordt als
eigen ronde bewaard. Draait op een tijdelijke sqlite-database, raakt Bing
niet. Draaien: python test_indexnow_bewaren.py
"""
import os
import sqlite3
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'indexnow_test.db')
# Een tabel zoals hij sinds 3 oktober op productie staat: zonder 'soort'.
con = sqlite3.connect(pad)
con.execute('CREATE TABLE indexnow_rondes (id INTEGER PRIMARY KEY, wanneer DATETIME NOT NULL, '
            'adressen INTEGER NOT NULL, statussen VARCHAR(200) NOT NULL, fout VARCHAR(200))')
con.execute("INSERT INTO indexnow_rondes (wanneer, adressen, statussen) VALUES ('2026-10-04 07:30:00', 12, '200')")
con.commit()
con.close()
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import create_app  # noqa: E402
import indexnow  # noqa: E402

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra else ''))
    if not ok:
        fouten += 1

app = create_app('development')
with app.app_context():
    from models import IndexNowRonde
    check('kolom soort toegevoegd, oude rij blijft', IndexNowRonde.query.count() == 1)

    # Bing nabootsen: 10.000 adressen per bericht, dus 2 berichten bij 10.001.
    verstuurd = []
    echte_post = indexnow._post
    indexnow._post = lambda body: verstuurd.append(body) or 200
    try:
        adressen = [f'https://www.witgoedaanbod.nl/product/p-{i}' for i in range(10001)]
        uit = indexnow.meld_verhuisde_adressen(adressen, 'https://www.witgoedaanbod.nl', 'sleutel123')
    finally:
        indexnow._post = echte_post
    check('twee berichten verstuurd', len(verstuurd) == 2, len(verstuurd))
    check('host zonder https', verstuurd[0]['host'] == 'www.witgoedaanbod.nl', verstuurd[0]['host'])
    check('uitkomst teruggegeven', uit['berichten'] == [{'adressen': 10000, 'status': 200},
                                                        {'adressen': 1, 'status': 200}], uit)

    s = indexnow.status()
    check('laatste ronde = adresopschoning', s['soort'] == 'adresopschoning' and s['adressen'] == 10001, s)
    check('oude ronde telt als dagelijks', s['laatste_rondes'][-1]['soort'] == 'dagelijks',
          s['laatste_rondes'])
    check('statussen bewaard', s['laatste_rondes'][0]['statussen'] == '200,200')

    # Een fout bij Bing mag niet doorslaan en moet bewaard worden.
    def kapot(body):
        raise ConnectionError('geen verbinding')
    indexnow._post = kapot
    try:
        uit = indexnow.meld_verhuisde_adressen(['https://www.witgoedaanbod.nl/product/x'],
                                               'https://www.witgoedaanbod.nl', 'k')
    finally:
        indexnow._post = echte_post
    check('fout bewaard, niet doorgegooid', 'geen verbinding' in (indexnow.status()['fout'] or ''), uit)

print()
print('ALLES GOED' if not fouten else f'{fouten} FOUT(EN)')
sys.exit(1 if fouten else 0)
