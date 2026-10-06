"""Welke witgoed-EAN's verkopen onze niet-Bol-winkels die niet op de site staan?
Alleen lezen: haalt elke feed één keer op (zoals een sync), schrijft niets.
Coolblue en MediaMarkt hebben sleutels nodig; draaien met:
    railway run python scripts/meting_feeds_overlap.py
Uitkomst ook in scripts/meting_feeds_overlap.json.
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
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')  # niets schrijven naar productie

from catalogus_uitzonderingen import is_geen_apparaat  # noqa: E402
from sync_mediamarkt import MIN_PRICES, classify  # noqa: E402

KOP = {'User-Agent': 'Mozilla/5.0 meting'}
B = 'www.witgoedaanbod.nl'


def get(url, timeout=300):
    return urllib.request.urlopen(urllib.request.Request(url, headers=KOP), timeout=timeout).read()


def tradetracker(module):
    """(ean, titel, prijs) uit een TradeTracker-JSON-feed."""
    mod = __import__(module)
    data = json.loads(get(mod.FEED_URL_DEFAULT))
    uit = []
    for p in data.get('products', []):
        props = p.get('properties') or {}
        ean = props.get('EAN') or props.get('GTIN')
        ean = ean[0] if isinstance(ean, list) and ean else ean
        prijs = (p.get('price') or {}).get('amount')
        if ean and prijs:
            uit.append((str(ean), p.get('name') or '', float(prijs)))
    return uit


def witgoedhuis():
    from sync_witgoedhuis import FEED_URL_DEFAULT
    uit, url = [], FEED_URL_DEFAULT
    while url:
        req = urllib.request.Request(url, headers=KOP)
        with urllib.request.urlopen(req, timeout=180) as r:
            url = r.headers.get('X-Next-Url')
            boom = ET.fromstring(r.read())
        for p in boom.iter('product'):
            i = p.find('product_info')
            v = lambda n: ((i.find(n).text or '').strip() if i.find(n) is not None and i.find(n).text else '')
            if v('condition') in ('', 'new') and v('in_stock').lower() == 'true' and v('ean') and v('price'):
                uit.append((v('ean'), v('title'), float(v('price'))))
        time.sleep(0.5)
    return uit


def coolblue():
    import sync_coolblue as sc
    sleutel = os.getenv('AWIN_FEED_APIKEY')
    if not sleutel:
        return None
    uit = []
    for row in sc.fetch_feed(sleutel):
        r = sc.normalize(row)
        if r and r['is_available']:
            uit.append((r['ean'], r['title'], r['price'], r['product_type']))
    return uit


def mediamarkt():
    import sync_mediamarkt as sm
    sleutel = os.getenv('TRADEDOUBLER_TOKEN')
    if not sleutel:
        return None
    return [(e, r['title'], r['price'], r['category_path'], r['from_main_feed'])
            for e, r in sm.collect_feed_products(sleutel).items() if r['is_available']]


def sleutel(ean):
    return str(ean).lstrip('0')


RUW = 'scripts/meting_feeds_ruw.json'
feeds = json.load(open(RUW, encoding='utf-8')) if os.path.exists(RUW) else {}
for naam, functie in [('expert', lambda: tradetracker('sync_expert')),
                      ('ep', lambda: tradetracker('sync_ep')),
                      ('alternate', lambda: tradetracker('sync_alternate')),
                      ('voordeligwitgoed', lambda: tradetracker('sync_voordeligwitgoed')),
                      ('witgoedhuis', witgoedhuis), ('coolblue', coolblue), ('mediamarkt', mediamarkt)]:
    if feeds.get(naam) is not None:
        continue  # al opgehaald (scripts/meting_feeds_ruw.json): niet nog eens bij het netwerk
    try:
        feeds[naam] = functie()
    except Exception as e:
        print(f'{naam}: FOUT {type(e).__name__}: {e}')
        feeds[naam] = None
    print(f"{naam}: {'geen sleutel/fout' if feeds[naam] is None else len(feeds[naam])} producten", flush=True)

json.dump(feeds, open(RUW, 'w', encoding='utf-8'), ensure_ascii=False)

# Indelen zoals de site: categorie op titel (Coolblue op zijn producttype,
# zoals sync_coolblue), niet-apparaat eruit, minimumprijs. Witgoedhuis zet
# vaak alleen merk en typenummer in de titel; die feed heeft een eigen
# categorieveld, maar dat bewaren we hier niet, dus zijn titel telt zoals hij is.
from sync_coolblue import classify as coolblue_classify  # noqa: E402
per_ean = defaultdict(lambda: {'winkels': set(), 'titel': '', 'cat': None})
witgoed_per_winkel = Counter()
for winkel, rijen in feeds.items():
    for rij in rijen or []:
        ean, titel, prijs = rij[0], rij[1], rij[2]
        cat = coolblue_classify(rij[3], titel) if winkel == 'coolblue' else classify(titel)
        if not cat or is_geen_apparaat(titel) or prijs < MIN_PRICES.get(cat, 0):
            continue
        witgoed_per_winkel[winkel] += 1
        e = per_ean[sleutel(ean)]
        e['winkels'].add(winkel)
        e['titel'] = e['titel'] or titel
        e['cat'] = e['cat'] or cat
print('\nwitgoed per winkelfeed (na indeling):', dict(witgoed_per_winkel))

sitemap = get(f'https://{B}/sitemap-producten.xml').decode()
op_site = {sleutel(m.group(1)) for m in re.finditer(r'-(\d{8,14})</loc>', sitemap)}
ontbreekt = {e: v for e, v in per_ean.items() if e not in op_site}
print(f'witgoed-EAN\'s in de feeds: {len(per_ean)}, op de site: {len(per_ean) - len(ontbreekt)}, '
      f'niet op de site: {len(ontbreekt)}')

# Bestaan ze bij ons wel (niet leverbaar)? /product/x-EAN geeft dan een 301.
for e, v in ontbreekt.items():
    c = http.client.HTTPSConnection(B, timeout=60)
    c.request('GET', f'/product/x-{e}', headers=KOP)
    r = c.getresponse()
    r.read()
    v['in_database'] = r.status in (301, 302)
    time.sleep(0.15)

uitslag = {'feeds': {k: (None if v is None else len(v)) for k, v in feeds.items()},
           'witgoed_per_winkel': dict(witgoed_per_winkel),
           'ontbreekt': {e: {'winkels': sorted(v['winkels']), 'cat': v['cat'], 'titel': v['titel'],
                             'in_database': v['in_database']} for e, v in ontbreekt.items()}}
json.dump(uitslag, open('scripts/meting_feeds_overlap.json', 'w', encoding='utf-8'), ensure_ascii=False)

for groep, test in (('2 of meer winkels', lambda n: n >= 2), ('precies 2', lambda n: n == 2),
                    ('3 of meer', lambda n: n >= 3), ('1 winkel', lambda n: n == 1)):
    g = [v for v in ontbreekt.values() if test(len(v['winkels']))]
    print(f"\n== {groep}: {len(g)} (waarvan wel in onze database, niet leverbaar: "
          f"{sum(v['in_database'] for v in g)})")
    print('   per categorie:', dict(Counter(v['cat'] for v in g).most_common()))
    print('   winkels:', dict(Counter(w for v in g for w in v['winkels']).most_common()))
