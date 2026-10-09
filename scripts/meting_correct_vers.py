"""Correct.nl: loopt de feedprijs mee met de prijs op de site?
Vaste steekproef van 20 witgoedproducten (scripts/correct_steekproef.json,
gekozen op 9 okt 2026), elke keer feedprijs tegen de prijs op
correct.nl/products/<handle>.js (de winkelpagina, niet de trackinglink).
De uitkomst per dag komt in scripts/correct_versheid.json, zodat 9, 10 en
11 okt naast elkaar liggen. Alleen lezen.
Draaien: python scripts/meting_correct_vers.py
"""
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
from sync_mediamarkt import classify  # noqa: E402

URL = ('https://daisycon.io/datafeed/?media_id=428244&program_id=17400&standard_id=6'
       '&language_code=nl&locale_id=1&type=xml&records=100')
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
STEEKPROEF = 'scripts/correct_steekproef.json'
LOGBOEK = 'scripts/correct_versheid.json'

feed, url, n = {}, URL, 0
while url and n < 400:
    with urllib.request.urlopen(urllib.request.Request(url, headers=KOP), timeout=180) as r:
        nxt = r.headers.get('X-Next-Url')
        b = ET.fromstring(r.read())
    for p in b.iter('product'):
        i = p.find('product_info')
        dl = urllib.parse.parse_qs(urllib.parse.urlparse(i.findtext('link') or '').query).get('dl', [''])[0]
        handle = dl.split('products/')[-1].split('?')[0].strip('/')
        feed[handle] = {'titel': i.findtext('title') or '', 'prijs': float(i.findtext('price') or 0),
                        'model': i.findtext('model') or '', 'voorraad': i.findtext('in_stock')}
    url, n = nxt, n + 1
    time.sleep(0.2)

if os.path.exists(STEEKPROEF):
    handles = json.load(open(STEEKPROEF, encoding='utf-8'))
else:
    kandidaten = sorted(h for h, v in feed.items()
                        if v['voorraad'] == 'true' and classify(v['titel']) and v['prijs'] >= 150
                        and not v['model'].upper().endswith('B'))
    random.seed(9)
    handles = random.sample(kandidaten, 20)
    json.dump(handles, open(STEEKPROEF, 'w', encoding='utf-8'), indent=1)

vandaag, klopt, gemeten = {}, 0, 0
for h in handles:
    f = feed.get(h)
    try:
        js = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'https://www.correct.nl/products/{h}.js', headers=KOP), timeout=30).read())
        site = js['price'] / 100
    except Exception as e:  # noqa: BLE001
        site = None
        print('site-fout', type(e).__name__, h[:60])
    fp = f['prijs'] if f else None
    vandaag[h] = {'feed': fp, 'site': site}
    if fp is not None and site is not None:
        gemeten += 1
        ok = abs(fp - site) < 1
        klopt += ok
        print(f"{'OK    ' if ok else 'ANDERS'} feed {fp:8.2f} | site {site:8.2f} | {f['titel'][:55]}")
    elif fp is None:
        print('niet meer in de feed:', h[:60])
print(f'\n{date.today()}: feedprijs = siteprijs bij {klopt} van {gemeten}')

log = json.load(open(LOGBOEK, encoding='utf-8')) if os.path.exists(LOGBOEK) else {}
log[str(date.today())] = vandaag
json.dump(log, open(LOGBOEK, 'w', encoding='utf-8'), indent=1)
if len(log) > 1:
    dagen = sorted(log)
    print('\nfeedprijs per dag (alleen waar iets veranderde):')
    for h in handles:
        reeks = [(d, log[d].get(h, {}).get('feed'), log[d].get(h, {}).get('site')) for d in dagen]
        if len({(x[1], x[2]) for x in reeks}) > 1:
            print('  ', h[:45], ' | '.join(f'{d[5:]} feed {fp} site {sp}' for d, fp, sp in reeks))
