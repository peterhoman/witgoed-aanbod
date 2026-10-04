"""Controle na uitrol: elke pagina met een geschreven tekst (subpagina_teksten.py)
op productie: bestaat hij, hoeveel modellen, staat het vragenblok erop, en
bestaan alle 'bekijk ook'-links? (alleen lezen)
Draaien: python scripts/controle_teksten_live.py [wachtseconden]
"""
import html
import re
import sys
import time
import urllib.request

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
time.sleep(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
import subpagina_teksten as st  # noqa: E402

B = 'https://www.witgoedaanbod.nl'


def get(pad):
    req = urllib.request.Request(B + pad, headers={'User-Agent': 'Mozilla/5.0 controle'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.geturl().replace(B, ''), r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, '', ''


fouten, links = [], set()
for sleutel, ruw in st.TEKSTEN.items():
    pad = '/category/' + '/'.join(sleutel)
    code, naar, h = get(pad)
    if code != 200 or naar != pad:
        fouten.append(f'{pad}: {code} {naar}')
        continue
    titel = html.unescape(re.search(r'<title>([^<]*)', h).group(1))
    n = re.search(r': (\d+) modellen', titel)
    vragen = ('Veelgestelde vragen over' in h) == bool(ruw.get('vragen'))
    kop = re.search(r'<h1[^>]*>([^<]*)', h)
    kop_ok = not ruw.get('h1') or (kop and html.unescape(kop.group(1)).strip() == ruw['h1'])
    print(f'{"OK  " if vragen and kop_ok else "FOUT"} {n.group(1) if n else "?":>4}  {pad}')
    if not (vragen and kop_ok):
        fouten.append(f'{pad}: vragenblok {vragen}, kop {kop_ok}')
    links |= {p for _, p in ruw.get('bekijk_ook', [])}
for p in sorted(links):
    code, naar, _ = get(p)
    if code != 200 or naar.split('?')[0] != p:
        fouten.append(f'link {p}: {code} {naar}')
print(f'\n{len(st.TEKSTEN)} pagina\'s, {len(links)} verschillende links gecontroleerd')
print('ALLES GOED' if not fouten else 'NIET IN ORDE:\n  ' + '\n  '.join(fouten))
