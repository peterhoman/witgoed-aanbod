"""Correct.nl: klopt de feedprijs met de prijs op de site, en wat is
'Koopjeskelder'? 20 witgoedproducten uit de feed, de winkelpagina zelf
opgevraagd (correct.nl, niet de trackinglink). Alleen lezen.
Draaien: python scripts/meting_correct_vers.py
"""
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import os  # noqa: E402
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
from sync_mediamarkt import classify  # noqa: E402

URL = ('https://daisycon.io/datafeed/?media_id=428244&program_id=17400&standard_id=6'
       '&language_code=nl&locale_id=1&type=xml&records=100')
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
rijen, url, n = [], URL, 0
while url and n < 400:
    with urllib.request.urlopen(urllib.request.Request(url, headers=KOP), timeout=180) as r:
        nxt = r.headers.get('X-Next-Url')
        b = ET.fromstring(r.read())
    for p in b.iter('product'):
        i = p.find('product_info')
        t = i.findtext('title') or ''
        if i.findtext('in_stock') == 'true' and classify(t) and float(i.findtext('price') or 0) >= 150:
            rijen.append({k: (i.findtext(k) or '') for k in ('title', 'ean', 'price', 'link', 'condition')})
    url, n = nxt, n + 1
    time.sleep(0.2)

dubbel = {}
for r in rijen:
    dubbel.setdefault(r['ean'], []).append(r['price'])
print('witgoed-rijen:', len(rijen), '| EANs met meer dan één rij:', sum(1 for v in dubbel.values() if len(v) > 1))

random.seed(9)
klopt = 0
steek = random.sample(rijen, 20)
for r in steek:
    dl = urllib.parse.parse_qs(urllib.parse.urlparse(r['link']).query).get('dl', [''])[0]
    handle = dl.split('products/')[-1].split('?')[0].strip('/')
    try:
        js = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'https://www.correct.nl/products/{handle}.js', headers=KOP), timeout=30).read())
        site = js['price'] / 100
        tags = [t for t in js.get('tags', []) if re.search(r'koop|outlet|b-keus|showroom|demo|schade', t, re.I)]
        ok = abs(site - float(r['price'])) < 1
        klopt += ok
        print(f"{'OK  ' if ok else 'ANDERS'} feed {float(r['price']):7.2f} | site {site:7.2f} | "
              f"{len(dubbel[r['ean']])} rij(en) | {tags} | {r['title'][:55]}")
    except Exception as e:  # noqa: BLE001
        print('fout', type(e).__name__, handle[:60])
    time.sleep(0.5)
print(f'\nfeedprijs = siteprijs bij {klopt} van {len(steek)}')
