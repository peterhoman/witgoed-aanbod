"""Controle na uitrol van het afronden (alleen lezen).
Draaien: python scripts/controle_afronden_live.py [wachtseconden]
"""
import html
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
time.sleep(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
B = 'https://www.witgoedaanbod.nl'
PAGINAS = ['koelkasten/breedte/50-60-cm', 'koelkasten/breedte/60-70-cm',
           'koelkasten/geluid/zeer-stil', 'koelkasten/geluid/stil',
           'wasmachines/toerental/1200-1400-toeren', 'wasmachines/toerental/1400-1600-toeren',
           'wasmachines/toerental/vanaf-1600-toeren', 'wasdroogcombinaties/toerental/1400-1600-toeren']


def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 controle'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''


for p in PAGINAS:
    code, h = get(f'{B}/category/{p}')
    kop = re.search(r'<h1[^>]*>([^<]*)', h)
    aantal = re.search(r'We volgen (\d+)|: (\d+) modellen', h)
    n = next((g for g in aantal.groups() if g), '?') if aantal else '?'
    print(f'{p:45} {code} {n:>4}  {html.unescape(kop.group(1)).strip() if kop else ""}')
