"""Steekproef: klopt 'in_stock' en de prijs uit de Witgoedhuis-feed met hun eigen
site? Gebruikt het gewone winkeladres uit de parameter dl van de link (geen
affiliate-link volgen). Alleen lezen. Draaien: python scripts/steekproef_witgoedhuis_voorraad.py
"""
import html
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
FEED = ('https://daisycon.io/datafeed/?media_id=428244&program_id=6570&standard_id=6'
        '&language_code=nl&locale_id=1&type=xml&records=100')
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36',
       'Accept-Language': 'nl-NL'}


def open_url(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=KOP), timeout=60)


items, url = [], FEED
while url:
    r = open_url(url)
    for p in ET.fromstring(r.read()).iter('product'):
        info = p.find('product_info') if p.find('product_info') is not None else p
        def veld(naam):
            e = info.find(naam)
            return (e.text or '').strip() if e is not None and e.text else ''
        items.append({'titel': veld('title'), 'prijs': veld('price'), 'link': veld('link'),
                      'categorie': veld('category')})
    url = r.headers.get('X-Next-Url')
witgoed = [i for i in items if i['categorie'] in ('Koelkasten', 'Wassen', 'Drogen', 'Vaatwasser',
                                                  'Afzuigkap', 'Kookplaat inbouw', 'Koken', 'Keuken')]
random.seed(5)
steekproef = random.sample(witgoed or items, min(15, len(witgoed or items)))
uitverkocht = prijs_fout = gelezen = 0
for i in steekproef:
    dl = urllib.parse.parse_qs(urllib.parse.urlparse(i['link']).query).get('dl', [''])[0]
    if not dl:
        print('geen dl-parameter:', i['titel'][:50])
        continue
    winkel = dl if dl.startswith('http') else 'https://www.witgoedhuis.nl/' + dl.lstrip('/')
    try:
        h = open_url(winkel).read().decode('utf-8', 'replace')
    except Exception as e:
        print('kon niet laden:', winkel[:70], type(e).__name__)
        continue
    gelezen += 1
    tekst = html.unescape(re.sub(r'<[^>]+>', ' ', h)).lower()
    weg = any(w in tekst for w in ('uitverkocht', 'niet op voorraad', 'niet leverbaar', 'out of stock'))
    prijzen = re.findall(r'"price":\s*"?([\d.]+)', h)
    feedprijs = float(i['prijs'] or 0)
    klopt = any(abs(float(p) - feedprijs) <= 1 for p in prijzen) if prijzen else None
    uitverkocht += weg
    prijs_fout += klopt is False
    print(f"{'UITVERKOCHT' if weg else 'leverbaar  '} prijs {'?' if klopt is None else ('ok ' if klopt else 'ANDERS')}"
          f" feed {feedprijs:>7.2f} site {prijzen[:1]}  {i['titel'][:50]}")
    time.sleep(1)
print(f'\n{gelezen} gelezen: {uitverkocht} uitverkocht ondanks "op voorraad", {prijs_fout} met andere prijs')
