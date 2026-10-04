"""Controle na uitrol: koelkasten per hoogte op productie (alleen lezen).
Draaien: python scripts/controle_hoogte_live.py
"""
import html
import re
import time
import urllib.request

B = 'https://www.witgoedaanbod.nl'
SLUGS = ['tot-90-cm', '90-130-cm', '130-170-cm', '170-180-cm', '180-190-cm', 'vanaf-190-cm']


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 controle'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''


time.sleep(int(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else 0)
for slug in SLUGS:
    code, h = get(f'{B}/category/koelkasten/hoogte/{slug}')
    titel = html.unescape(re.search(r'<title>([^<]*)', h).group(1)) if code == 200 else '-'
    noindex = 'noindex' in h
    print(f'{slug:14} {code} {"NOINDEX " if noindex else ""}{titel}')
code, h = get(f'{B}/category/koelkasten')
print('links op /category/koelkasten:', sum(f'/category/koelkasten/hoogte/{s}"' in h for s in SLUGS), 'van 6')
code, s = get(f'{B}/sitemap-kenmerken.xml')
print('in sitemap:', sum(f'/koelkasten/hoogte/{x}<' in s for x in SLUGS), 'van 6;',
      'wasmachines-hoogte in sitemap:', '/wasmachines/hoogte/' in s)
