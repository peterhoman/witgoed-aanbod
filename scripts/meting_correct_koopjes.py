"""Correct.nl: hoe herken je Koopjeskelder (opendoos/demo, alleen afhalen) in
de feed, en hoe vers is de feed? Hypothese uit twee voorbeelden: model eindigt
op 'B' en de Shopify-handle eindigt op '-1'. Getoetst tegen de tag
'koopjeskelder' op correct.nl/products/<handle>.js. Alleen lezen.
Draaien: python scripts/meting_correct_koopjes.py
"""
import collections
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
from sync_mediamarkt import classify  # noqa: E402

URL = ('https://daisycon.io/datafeed/?media_id=428244&program_id=17400&standard_id=6'
       '&language_code=nl&locale_id=1&type=xml&records=100')
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
alle, witgoed, url, n = [], [], URL, 0
while url and n < 400:
    with urllib.request.urlopen(urllib.request.Request(url, headers=KOP), timeout=180) as r:
        nxt = r.headers.get('X-Next-Url')
        b = ET.fromstring(r.read())
    for p in b.iter('product'):
        i = p.find('product_info')
        dl = urllib.parse.parse_qs(urllib.parse.urlparse(i.findtext('link') or '').query).get('dl', [''])[0]
        rij = {'titel': i.findtext('title') or '', 'model': i.findtext('model') or '', 'ean': i.findtext('ean') or '',
               'prijs': i.findtext('price') or '', 'handle': dl.split('products/')[-1].split('?')[0],
               'upd': (p.findtext('update_date') or '')[:10], 'voorraad': i.findtext('in_stock')}
        alle.append(rij)
        if rij['voorraad'] == 'true' and classify(rij['titel']) and float(rij['prijs'] or 0) >= 150:
            witgoed.append(rij)
    url, n = nxt, n + 1
    time.sleep(0.2)


def kenmerk(r):
    return r['model'].upper().endswith('B') and bool(re.search(r'-\d+$', r['handle']))


print('feed', len(alle), '| witgoed', len(witgoed))
print('heel de feed: model op B', sum(r['model'].upper().endswith('B') for r in alle),
      '| handle op -<cijfer>', sum(bool(re.search(r'-\d+$', r['handle'])) for r in alle),
      '| beide', sum(kenmerk(r) for r in alle))
kk = [r for r in witgoed if kenmerk(r)]
print('witgoed met kenmerk (model B + handle -N):', len(kk))
print('update_date witgoed per maand:', sorted(collections.Counter(r['upd'][:7] for r in witgoed).items()))


def tags(handle):
    js = json.loads(urllib.request.urlopen(urllib.request.Request(
        f'https://www.correct.nl/products/{handle}.js', headers=KOP), timeout=30).read())
    return [t.lower() for t in js.get('tags', [])], js['price'] / 100


random.seed(4)
uitkomst = collections.Counter()
for groep, rijen in (('kenmerk', kk), ('geen kenmerk', [r for r in witgoed if not kenmerk(r)])):
    for r in random.sample(rijen, min(15, len(rijen))):
        try:
            t, prijs = tags(r['handle'])
            uitkomst[(groep, 'koopjeskelder' in t)] += 1
        except Exception:  # noqa: BLE001
            uitkomst[(groep, 'fout')] += 1
        time.sleep(0.4)
print('toets tegen de site-tag (groep, heeft tag koopjeskelder):', dict(uitkomst))

# Randgevallen: alleen model op B, of alleen handle op -N.
for naam, rijen in (('alleen model B', [r for r in witgoed if r['model'].upper().endswith('B') and not kenmerk(r)]),
                    ('alleen handle -N', [r for r in witgoed if re.search(r'-\d+$', r['handle']) and not kenmerk(r)])):
    telling = collections.Counter()
    for r in rijen[:20]:
        try:
            t, _ = tags(r['handle'])
            telling['koopjeskelder' in t] += 1
        except Exception:  # noqa: BLE001
            telling['fout'] += 1
        time.sleep(0.4)
    print(naam, len(rijen), 'getoetst:', dict(telling))
