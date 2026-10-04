"""Bestaan deze adressen op productie, en hoeveel modellen? (alleen lezen)
Draaien: python scripts/bestaan_adressen.py /pad1 /pad2 ...
Zonder argumenten: alle pagina's en 'bekijk ook'-links uit subpagina_teksten.py.
"""
import re
import sys
import urllib.request

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
B = 'https://www.witgoedaanbod.nl'


def status(pad):
    req = urllib.request.Request(B + pad, headers={'User-Agent': 'Mozilla/5.0 controle'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            h = r.read().decode('utf-8', 'replace')
            m = re.search(r': (\d+) modellen|We volgen (\d+)', h)
            n = next((g for g in m.groups() if g), '') if m else ''
            return r.status, r.geturl().replace(B, ''), n
    except urllib.error.HTTPError as e:
        return e.code, '', ''


paden = sys.argv[1:]
if not paden:
    import subpagina_teksten as st
    paden = sorted({'/category/' + '/'.join(k) for k in st.TEKSTEN}
                   | {p for v in st.TEKSTEN.values() for _, p in v.get('bekijk_ook', [])}
                   | {p for v in st.BEKIJK_OOK.values() for _, p in v})
fout = 0
for p in paden:
    code, naar, n = status(p)
    goed = code == 200 and naar.split('?')[0] == p
    fout += not goed
    if not goed or len(sys.argv) > 1:
        print(f'{"OK  " if goed else "FOUT"} {code} {p} {"-> " + naar if naar and naar != p else ""} {n}')
print(f'{len(paden)} adressen, {fout} niet in orde')
