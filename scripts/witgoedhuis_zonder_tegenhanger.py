"""Witgoedhuis-feedproducten zonder tegenhanger in onze leverbare catalogus:
wat zijn het, bestaan ze bij ons wel (niet leverbaar), staan ze in EPREL, en
verkopen MediaMarkt of Coolblue ze? Alleen lezen; volgt geen affiliate-links.
Draaien: python scripts/witgoedhuis_zonder_tegenhanger.py [stap]
  stap 1 = alleen indeling (snel), 2 = alles (traag, ~15 min)
"""
import http.client
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')
STAP = int(sys.argv[1]) if len(sys.argv) > 1 else 1
FEED = ('https://daisycon.io/datafeed/?media_id=428244&program_id=6570&standard_id=6'
        '&language_code=nl&locale_id=1&type=xml&records=100')
B = 'www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36',
       'Accept-Language': 'nl-NL'}

# Onze categorieën, herkend aan de feedcategorie en de titel (volgorde telt).
ONZE = [
    ('Wasdroogcombinaties', r'was-?droog|wasdroger combinatie|washer.?dryer'),
    ('Vaatwassers', r'vaatwasser|vaatwasmachine|vaatwas'),
    ('Wasmachines', r'wasmachine|wasautomaat'),
    ('Drogers', r'droger|droogtrommel'),
    ('Koelkasten', r'koelkast|koel-?vries|vriezer|vrieskast|vrieskist|wijnklimaat|koelkasten'),
    ('Afzuigkappen', r'afzuigkap|wasemkap|schouwkap|plafondunit'),
    ('Kookplaten', r'kookplaat|inductie|gaskookplaat|domino'),
    ('Fornuizen', r'fornuis'),
    ('Ovens & Airfryers', r'oven|airfryer|heteluchtfriteuse|stoomoven'),
    ('Magnetrons', r'magnetron|microgolf'),
    ('Stofzuigers', r'stofzuiger|steelzuiger|robotzuiger'),
    ('Koffiemachines', r'koffiemachine|espresso|volautomaat|koffiezet'),
]
ACCESSOIRE = (r'onderdeel|filter|beugel|houder|ontkalker|reiniger|schaal|plaat voor|'
              r'tussenstuk|stapelkit|voeten|slang|zak(ken)?\b|borstel|accessoire|'
              r'bakplaat|rooster|pan\b|pannen|set van|deurscharnier|front|plint|'
              r'koolstof|recirculatie|waterfilter|melkopschuim|kan\b|beker|schoonmaak|'
              r'set\b|strip|korf|verlenging|deur met|verbind|rails|geleider|tabs|cleaning|'
              r'onderhoud|zakken|stofzak|adapter|kit\b|bocht|buis|kabel|glazen|greep|'
              r'telescoop|uittrek|bevestig|montage|afdekplaat|lampje|lamp\b|'
              # Accessoires met alleen een typenummer als titel (6 okt nagekeken):
              # ATAG SBS10x koppelset, HPT/HPG100 bakplaten, TP/TY2240, BS2535,
              # ACC6711, Bosch HEZ ovenaccessoires, AEG TR..L. geleiders.
              r'\bsbs10\d|\bhp[tg]100|\bt[py]2240|\bbs2535|\bacc6711|\bhez\d|\btr\dl')
# Onder deze prijs is een "apparaat" in deze categorie vrijwel altijd een onderdeel.
MIN_PRIJS = {'Stofzuigers': 50, 'Koffiemachines': 60, 'Magnetrons': 50}
MIN_PRIJS_STANDAARD = 100


def open_url(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=KOP), timeout=60)


items, url = [], FEED
while url:
    r = open_url(url)
    for p in ET.fromstring(r.read()).iter('product'):
        info = p.find('product_info')
        def veld(naam):
            e = info.find(naam)
            return (e.text or '').strip() if e is not None and e.text else ''
        items.append({'ean': veld('ean').lstrip('0'), 'titel': veld('title'), 'cat': veld('category'),
                      'pad': veld('category_path'), 'prijs': veld('price'), 'merk': veld('brand')})
    url = r.headers.get('X-Next-Url')
    time.sleep(0.5)

sm = open_url(f'https://{B}/sitemap-producten.xml').read().decode()
onze = {m.group(1).lstrip('0') for m in re.finditer(r'-(\d{8,14})</loc>', sm)}
zonder = [i for i in items if i['ean'] and i['ean'] not in onze]
print(f'Feed {len(items)}, met tegenhanger {len(items) - len(zonder)}, zonder {len(zonder)}')


def soort(i):
    tekst = f"{i['cat']} {i['pad']} {i['titel']}".lower()
    if re.search(ACCESSOIRE, i['titel'].lower()):
        return 'b: accessoire/onderdeel'
    for naam, patroon in ONZE:
        if re.search(patroon, tekst):
            try:
                prijs = float(i['prijs'])
            except ValueError:
                prijs = 0
            if prijs < MIN_PRIJS.get(naam, MIN_PRIJS_STANDAARD):
                return 'b: accessoire/onderdeel'
            return 'a: ' + naam
    return 'c: ander (' + (i['cat'] or '?') + ')'


per = defaultdict(list)
for i in zonder:
    per[soort(i)].append(i)
for k in sorted(per):
    if k.startswith('a') or k.startswith('b'):
        print(f'{k:40} {len(per[k])}')
anders = Counter(k for k in per if k.startswith('c') for _ in per[k])
print('c: ander, totaal', sum(len(v) for k, v in per.items() if k.startswith('c')))
print('   ', sorted(((k[10:-1], len(v)) for k, v in per.items() if k.startswith('c')), key=lambda x: -x[1])[:12])
if STAP == 1:
    for k in sorted(per):
        if k.startswith('a'):
            print(k, [x['titel'][:40] + ' ' + x['prijs'] for x in per[k]])
    sys.exit()

# Stap 2: alleen groep a, per apparaat nagaan.
from eprel import zoek  # noqa: E402
groep_a = [i for k, v in per.items() if k.startswith('a') for i in v]
rij_uit = []
for i in groep_a:
    cat = soort(i)[3:]
    # Bestaat het bij ons (niet leverbaar)? /product/x-EAN stuurt dan door.
    c = http.client.HTTPSConnection(B, timeout=60)
    c.request('GET', f"/product/x-{i['ean']}", headers=KOP)
    r = c.getresponse()
    r.read()
    bij_ons = r.status in (301, 302) and r.getheader('Location')
    # EPREL
    try:
        e = zoek(cat, f"{i['merk']} {i['titel']}", pauze=0.5)
        eprel = 'ja' if e.get('gevonden') else ('niet gezocht' if not e.get('gezocht') else 'nee')
    except Exception:
        eprel = 'fout'
    # MediaMarkt en Coolblue op EAN (openbare zoekpagina's).
    mm = cb = None
    try:
        h = open_url(f"https://www.mediamarkt.nl/nl/search.html?query={i['ean']}").read().decode('utf-8', 'replace')
        mm = bool(re.search(r'"price":\s*\d', h))
    except Exception:
        pass
    try:
        h = open_url(f"https://www.coolblue.nl/zoeken?query={i['ean']}").read().decode('utf-8', 'replace')
        cb = 'geen resultaten' not in h.lower() and bool(re.search(r'/product/\d+/', h))
    except Exception:
        pass
    rij_uit.append({'cat': cat, 'titel': i['titel'], 'bij_ons': bool(bij_ons), 'eprel': eprel,
                    'mm': mm, 'cb': cb, 'prijs': i['prijs']})
    time.sleep(1)
json.dump(rij_uit, open('scripts/witgoedhuis_groep_a.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(f'\nGroep a: {len(rij_uit)} apparaten')
print('  bestaat bij ons maar niet leverbaar:', sum(r['bij_ons'] for r in rij_uit))
print('  EPREL:', Counter(r['eprel'] for r in rij_uit))
print('  ook bij MediaMarkt:', sum(bool(r['mm']) for r in rij_uit), '| ook bij Coolblue:',
      sum(bool(r['cb']) for r in rij_uit), '| bij geen van beide:',
      sum(not r['mm'] and not r['cb'] for r in rij_uit),
      '| Coolblue niet te lezen:', sum(r['cb'] is None for r in rij_uit))
print('  per categorie (aantal, waarvan bij ons bekend, EPREL ja, alleen Witgoedhuis):')
for cat in sorted({r['cat'] for r in rij_uit}):
    g = [r for r in rij_uit if r['cat'] == cat]
    print(f"    {cat:20} {len(g):3}  {sum(r['bij_ons'] for r in g):3}  "
          f"{sum(r['eprel'] == 'ja' for r in g):3}  {sum(not r['mm'] and not r['cb'] for r in g):3}")
