"""Witgoedhuis-feed (Daisycon) tegen onze catalogus: overlap op EAN, nieuwe
vergelijkingen, prijs en versheid. Alleen lezen; volgt geen affiliate-links.
Draaien: python scripts/meting_witgoedhuis.py
"""
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
FEED = ('https://daisycon.io/datafeed/?media_id=428244&program_id=6570&standard_id=6'
        '&language_code=nl&locale_id=1&type=xml&records=100')
B = 'https://www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 meting'}


def open_url(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=KOP), timeout=120)


# 1. Feed ophalen, alle pagina's.
items, url, laatst = [], FEED, None
while url:
    r = open_url(url)
    laatst = laatst or r.headers.get('Last-Modified')
    totaal = r.headers.get('X-Total-Count')
    boom = ET.fromstring(r.read())
    for p in boom.iter('product'):
        info = p.find('product_info') if p.find('product_info') is not None else p
        def veld(naam):
            e = info.find(naam)
            return (e.text or '').strip() if e is not None and e.text else ''
        items.append({'ean': veld('ean'), 'titel': veld('title'), 'prijs': veld('price'),
                      'voorraad': veld('in_stock'), 'categorie': veld('category')})
    url = r.headers.get('X-Next-Url')
    time.sleep(0.5)
print(f'Feed: {len(items)} producten (X-Total-Count {totaal}), Last-Modified {laatst}')
print('Categorieën:', Counter(i['categorie'] for i in items).most_common(10))
print('Op voorraad:', Counter(i['voorraad'] for i in items))

# 2. Onze catalogus: EAN staat achteraan in elk productadres.
sm = open_url(B + '/sitemap-producten.xml').read().decode()
onze = {}
for adres in re.findall(r'<loc>([^<]+)</loc>', sm):
    m = re.search(r'-(\d{8,14})$', adres)
    if m:
        onze[m.group(1).lstrip('0')] = adres
gedeeld = [i for i in items if i['ean'] and i['ean'].lstrip('0') in onze]
print(f'\nOnze leverbare catalogus: {len(onze)}; gedeeld op EAN: {len(gedeeld)}')

# 3. Per gedeeld apparaat: hoeveel winkels nu en onze laagste prijs.
solo = goedkoper = gelijk = duurder = 0
for i in gedeeld:
    h = open_url(onze[i['ean'].lstrip('0')]).read().decode('utf-8', 'replace')
    winkels = re.search(r'"offerCount":\s*"?(\d+)', h)
    laagste = re.search(r'"lowPrice":\s*"?([\d.]+)', h)
    if winkels and int(winkels.group(1)) == 1:
        solo += 1
    if laagste and i['prijs']:
        verschil = float(i['prijs']) - float(laagste.group(1))
        goedkoper += verschil < -1
        gelijk += abs(verschil) <= 1
        duurder += verschil > 1
    time.sleep(0.2)
print(f'Daarvan nu bij ons maar 1 winkel (wordt een nieuwe vergelijking): {solo}')
print(f'Witgoedhuis goedkoper dan onze laagste: {goedkoper}, gelijk: {gelijk}, duurder: {duurder}')
