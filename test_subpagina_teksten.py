"""Geschreven tekst per subpagina (subpagina_teksten.py) en de weergave ervan.

Draaien: python test_subpagina_teksten.py
"""
import re
import sys
sys.path.insert(0, '.')

import subpagina_teksten as st

fouten = 0
def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)

# 1. Invullen van aantallen en prijs.
t = st.tekst_voor(('drogers', 'type', 'warmtepompdroger'), 47, 399, 7)
check('titel met aantal en prijs', t['titel'] == 'Warmtepompdrogers vergelijken: 47 modellen vanaf € 399 | WitgoedAanbod.nl', t['titel'])
check('intro met aantal en winkels', '47 warmtepompdrogers' in t['intro'] and '7 winkels' in t['intro'])
check('geen accolades over', '{' not in t['titel'] + t['intro'])
check('eigen pagina niet in bekijk ook', all(p != '/category/drogers/type/warmtepompdroger' for _, p in t['bekijk_ook'])
      and len(t['bekijk_ook']) == 6)
t = st.tekst_voor(('drogers', 'geluid', 'stil'), 9, None, 7)
check('zonder prijs geen "vanaf € None"', 'None' not in t['titel'] and 'vanaf' not in t['titel'], t['titel'])
check('onbekend pad geeft None', st.tekst_voor(('drogers', 'type', 'bestaat-niet'), 1, 1, 7) is None
      and st.tekst_voor(None, 1, 1, 7) is None)

# 2. Elke tekst is compleet en bevat geen vaste bedragen.
for pad, ruw in st.TEKSTEN.items():
    alles = ' '.join([ruw.get('intro') or ''] + [a for _, al in ruw.get('uitleg', []) for a in al]
                     + [a for _, a in ruw.get('vragen', [])])
    # Volledige tekst (met eigen kop) of aanvulling op een zoekzin-pagina
    # (ronde 2, deel B: alleen titel, vragen en bekijk ook).
    velden = ('titel', 'h1', 'naam', 'intro') if ruw.get('h1') else ('titel', 'naam', 'vragen')
    check(f'{"/".join(pad)}: velden compleet', all(ruw.get(k) for k in velden))
    check(f'{"/".join(pad)}: geen "zeven winkels" vast in de tekst', 'zeven winkels' not in alles)
    check(f'{"/".join(pad)}: bekijk ook wijst naar /category of /gidsen',
          all(p.startswith(('/category/', '/gidsen/')) for _, p in ruw.get('bekijk_ook', [])))
    check(f'{"/".join(pad)}: geen vast bedrag in de tekst', not re.search(r'€\s*\d', alles))
    check(f'{"/".join(pad)}: titel eindigt op de sitenaam', ruw['titel'].endswith(' | WitgoedAanbod.nl'))

# 3. Het patroon van "zonder afvoer".
from zoekkenmerken import KENMERKEN
patroon = re.compile(KENMERKEN['drogers']['zonder-afvoer']['patroon'], re.I)
check('warmtepompdroger telt mee', bool(patroon.search('LG RT90X8 - Warmtepompdroger 9 kg Type droger Warmtepompdroger')))
check('condensdroger telt mee', bool(patroon.search('Beko Condensdroger 8 kg')))
check('luchtafvoerdroger telt niet mee', not patroon.search('Klarstein Jet Set condensdroger Type droger Luchtafvoerdroger'))
check('droger zonder type telt niet mee', not patroon.search('Onbekend merk wasdroger 7 kg'))

# 4. Weergave: een bestaande typepagina in de lokale demodatabase krijgt
#    tijdelijk een tekst, zodat het sjabloon echt gerenderd wordt.
from app import create_app
app = create_app()
c = app.test_client()
h = c.get('/category/wasmachines').get_data(as_text=True)
m = re.search(r'href="(/category/wasmachines/(type|energielabel)/([a-z0-9-]+))"', h)
if m:
    adres, soort, waarde = m.group(1), m.group(2), m.group(3)
    st.TEKSTEN[('wasmachines', soort, waarde)] = dict(st.TEKSTEN[('drogers', 'type', 'warmtepompdroger')])
    st.BEKIJK_OOK['wasmachines'] = [('Alle wasmachines', '/category/wasmachines'), ('Deze pagina', adres)]
    r = c.get(adres); p = r.get_data(as_text=True)
    koppen = [int(x) for x in re.findall(r'<h([1-6])', p)]
    check('typepagina rendert (200)', r.status_code == 200)
    check('kop uit de tekst', '<h1>Warmtepompdrogers vergelijken</h1>' in p)
    check('titel uit de tekst', 'Warmtepompdrogers vergelijken:' in re.search(r'<title>([^<]*)', p).group(1))
    check('bijgewerkt-regel', 'Bijgewerkt op ' in p)
    check('uitleg met tussenkop', '<h2>Hoe werkt een warmtepompdroger?</h2>' in p)
    check('vragen zichtbaar, geen FAQ-schema', 'Heeft een warmtepompdroger een afvoer nodig?' in p and 'FAQPage' not in p)
    check('bekijk ook zonder de eigen pagina', 'Alle wasmachines' in p and 'Deze pagina' not in p)
    check('precies één h1, geen kopsprong', koppen.count(1) == 1 and all(b <= a + 1 for a, b in zip(koppen, koppen[1:])))
    # Aanvulling (ronde 2, deel B): eigen kop en intro blijven staan.
    oude_h1 = None
    del st.TEKSTEN[('wasmachines', soort, waarde)]
    p0 = c.get(adres).get_data(as_text=True)
    oude_h1 = re.search(r'<h1>([^<]*)</h1>', p0).group(1)
    st.TEKSTEN[('wasmachines', soort, waarde)] = dict(st.TEKSTEN[('koelkasten', 'kenmerk', 'no-frost')])
    r = c.get(adres); p = r.get_data(as_text=True)
    check('aanvulling: rendert (200)', r.status_code == 200)
    check('aanvulling: eigen kop blijft', re.search(r'<h1>([^<]*)</h1>', p).group(1) == oude_h1, oude_h1)
    check('aanvulling: titel uit de tekst', 'No frost koelkast vergelijken:' in re.search(r'<title>([^<]*)', p).group(1))
    check('aanvulling: vragen met korte naam', '<h2>Veelgestelde vragen over no frost koelkasten</h2>' in p)
    check('aanvulling: geen leeg uitlegblok', 'subpagina-uitleg' not in p)
    check('aanvulling: eigen bekijk ook gaat voor de categorielijst',
          'Amerikaanse koelkasten' in p and 'Deze pagina' not in p)
    del st.TEKSTEN[('wasmachines', soort, waarde)]; del st.BEKIJK_OOK['wasmachines']
    r = c.get(adres); p = r.get_data(as_text=True)
    check('zonder tekst: gewone naam of oude opbouw, geen uitlegblok',
          r.status_code == 200 and 'subpagina-uitleg' not in p)
else:
    print('     (geen typepagina in de lokale database; weergave niet getest)')

print(f"\n{fouten} fout")
sys.exit(1 if fouten else 0)
