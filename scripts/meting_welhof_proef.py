"""Meting Welhof-voorbeeldfeed (7 okt): conditie, EAN-kwaliteit, overlap met
onze catalogus en prijsverschil bij nieuwe producten. Alleen lezen.
Draaien: python scripts/meting_welhof_proef.py <pad-naar-csv>
"""
import collections
import csv
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
rijen = list(csv.DictReader(open(sys.argv[1], encoding='utf-8-sig')))
print('rijen:', len(rijen), '| unieke product_id:', len({r['product_id'] for r in rijen}))
print('conditie:', collections.Counter(r['condition'] for r in rijen).most_common())
print('categorie:', collections.Counter(r['merchant_product_category_path'].split(' > ')[1] if ' > ' in r['merchant_product_category_path'] else r['merchant_product_category_path'] for r in rijen).most_common(12))
print('in_stock:', collections.Counter(r['in_stock'] for r in rijen).most_common())
ean_ok = [r for r in rijen if re.fullmatch(r'\d{8}|\d{12,14}', r['ean'].strip())]
print('geldige EAN:', len(ean_ok), '| dubbele EAN:', sum(1 for _, n in collections.Counter(r['ean'] for r in ean_ok).items() if n > 1))
print('oude prijs != prijs:', sum(1 for r in rijen if r['product_price_old'] != r['price']))

sm = urllib.request.urlopen(urllib.request.Request('https://www.witgoedaanbod.nl/sitemap-producten.xml', headers=KOP),
                            timeout=120).read().decode()
bij_ons = {}
for a in re.findall(r'<loc>([^<]+)</loc>', sm):
    m = re.search(r'-(\d{8,14})$', a)
    if m:
        bij_ons[m.group(1)] = a
per_conditie = collections.defaultdict(lambda: [0, 0])
voorbeelden = []
for r in ean_ok:
    e = r['ean'].strip()
    treffer = e in bij_ons or e.zfill(13) in bij_ons or e.lstrip('0') in bij_ons
    per_conditie[r['condition']][0] += 1
    per_conditie[r['condition']][1] += treffer
    if treffer and 'nieuw' in r['condition'].lower() and len(voorbeelden) < 15:
        voorbeelden.append((e, r['price'], bij_ons.get(e) or bij_ons.get(e.zfill(13)) or bij_ons.get(e.lstrip('0'))))
print('overlap met onze sitemap per conditie (totaal, bij ons):', dict(per_conditie))

# Prijsvergelijking bij nieuwe producten die wij hebben: lees onze laagste prijs uit de pagina (JSON-LD).
for e, prijs, adres in voorbeelden:
    try:
        h = urllib.request.urlopen(urllib.request.Request(adres, headers=KOP), timeout=60).read().decode()
        m = re.search(r'"lowPrice"\s*:\s*"?([\d.]+)', h) or re.search(r'"price"\s*:\s*"?([\d.]+)', h)
        print(f'  {e}: Welhof {prijs} | wij laagste {m.group(1) if m else "?"} | {adres.rsplit("/", 1)[-1][:60]}')
    except Exception as ex:  # noqa: BLE001
        print('  ', e, 'fout', ex)
