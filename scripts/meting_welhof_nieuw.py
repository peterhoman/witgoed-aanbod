"""Meting Welhof new-only feed (8 okt): categorieën, overlap met onze
catalogus, en per overlapper ons aantal winkels en onze laagste prijs.
Alleen lezen. Draaien: python scripts/meting_welhof_nieuw.py <pad-naar-csv>
"""
import collections
import csv
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
rijen = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))
print('rijen:', len(rijen))
print('hoofdcategorie:', collections.Counter(r['merchant_product_category_path'].split(' > ')[0] for r in rijen).most_common())
huis = [r for r in rijen if r['merchant_product_category_path'].startswith('Huishouden')]
print('Huishouden-subcategorie:', collections.Counter(
    (r['merchant_product_category_path'].split(' > ') + ['', ''])[1] for r in huis).most_common(20))
print('prijs boven EUR 150:', sum(1 for r in rijen if float(r['price'] or 0) >= 150))

sm = urllib.request.urlopen(urllib.request.Request('https://www.witgoedaanbod.nl/sitemap-producten.xml', headers=KOP),
                            timeout=120).read().decode()
bij_ons = {}
for a in re.findall(r'<loc>([^<]+)</loc>', sm):
    m = re.search(r'-(\d{8,14})$', a)
    if m:
        bij_ons[m.group(1).zfill(13)] = a
overlap = [r for r in rijen if r['ean'].strip().zfill(13) in bij_ons]
print('overlap met onze catalogus:', len(overlap))
for r in overlap:
    adres = bij_ons[r['ean'].strip().zfill(13)]
    h = urllib.request.urlopen(urllib.request.Request(adres, headers=KOP), timeout=60).read().decode()
    laag = re.search(r'"lowPrice"\s*:\s*"?([\d.]+)', h)
    n = re.search(r'"offerCount"\s*:\s*"?(\d+)', h)
    print(f"  Welhof {float(r['price']):7.2f} | wij laagste {laag.group(1) if laag else '?':>7} "
          f"bij {n.group(1) if n else '?'} winkel(s) | {r['product_name'][:60]}")
