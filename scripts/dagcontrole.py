"""Dagelijkse storingscontrole (alleen lezen), zie docs/START-HIER.md.
Draaien: python scripts/dagcontrole.py
"""
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
B = 'https://www.witgoedaanbod.nl'


def get(url, kop=False):
    req = urllib.request.Request(url, method='HEAD' if kop else 'GET',
                                 headers={'User-Agent': 'Mozilla/5.0 dagcontrole'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r if kop else r.read().decode('utf-8', 'replace')


print('== gezondheid')
print(get(B + '/api/gezondheid').strip())

d = json.loads(get(B + '/api/prijssprongen?dagen=1'))
print('\n== prijssprongen 1 dag:', {k: d[k] for k in ('sprongen', 'teruggesprongen', 'prijswijzigingen_in_periode')})
for x in d['lijst']:
    print('  ', x['winkel'], x['ean'], x['van'], '->', x['naar'], 'terug' if x['teruggesprongen'] else '')

t = json.loads(get(B + '/api/teksten/diagnose'))
print('\n== teksten: leverbaar zonder tekst', t['leverbaar_zonder_tekst'], '| sleutel', t['ai_sleutel_aanwezig'])
e = json.loads(get(B + '/api/eprel'))
print('== eprel: al opgezocht', e['al_opgezocht'], '| afgebroken door', e['laatste_ronde_afloop']['afgebroken_door'])

s = json.loads(get(B + '/api/sync-status'))
print('\n== winkels niet ververst 3d:', {w['winkel']: w['niet_ververst_3d'] for w in s['winkelbijdrage']})
print('== indexnow:', {k: s['indexnow'].get(k) for k in ('wanneer', 'soort', 'adressen', 'fout')},
      [b.get('status') for b in s['indexnow'].get('berichten', [])])
for p in s['paginaweergaven'][:2]:
    uit = {k: v for k, v in p.items() if k.startswith('uit-')}
    print(f"== {p['datum']}: echte doorkliks (uit-*) {sum(uit.values())} {uit}")
    print(f"   tegengehouden zonder kaartje {p.get('klik-zonder-kaartje', 0)}, buiten Europa {p.get('klik-buiten-europa', 0)}")
for log in s['laatste_synclogs'][:5]:
    if log['fouten']:
        print('== synclog melding:', log['gestart'][:16], log['fouten'][:200])

sm = get(B + '/sitemap-producten.xml')
eerste = re.search(r'<loc>([^<]+)</loc>', sm).group(1)
h = get(eerste)
print('\n== sjabloonsporen op', eerste.rsplit('/', 1)[-1], ':', len(re.findall(r'#\}|\{%|%\}|\{#', h)))

r = get('https://daisycon.io/datafeed/?media_id=428244&program_id=6570&standard_id=6'
        '&language_code=nl&locale_id=1&type=xml&records=5', kop=True)
print('\n== Witgoedhuis-feed: Last-Modified', r.headers.get('Last-Modified'),
      '| X-Total-Count', r.headers.get('X-Total-Count'))
