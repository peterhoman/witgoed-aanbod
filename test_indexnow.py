"""IndexNow (indexnow.py): welke adressen worden gemeld, in welke stukken,
met welk bericht. Draaien: python test_indexnow.py
"""
import sys
from datetime import date
sys.path.insert(0, '.')

import indexnow

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra else ''))
    if not ok:
        fouten += 1

# 1. Alleen adressen met een datum vanaf 'sinds', zonder 'overig', zonder dubbelen.
per_soort = {
    'producten': [
        {'loc': 'https://www.witgoedaanbod.nl/product/a', 'lastmod': '2026-09-22'},
        {'loc': 'https://www.witgoedaanbod.nl/product/b', 'lastmod': '2026-09-21'},
        {'loc': 'https://www.witgoedaanbod.nl/product/c', 'lastmod': '2026-09-20'},
        {'loc': 'https://www.witgoedaanbod.nl/product/a', 'lastmod': '2026-09-22'},
    ],
    'categorieen': [
        {'loc': 'https://www.witgoedaanbod.nl/category/drogers', 'lastmod': '2026-09-22'},
        {'loc': 'https://www.witgoedaanbod.nl/category/ovens', 'lastmod': '2026-08-01'},
    ],
    'overig': [
        {'loc': 'https://www.witgoedaanbod.nl/', 'lastmod': '2026-09-22'},
        {'loc': 'https://www.witgoedaanbod.nl/pers', 'lastmod': '2026-09-22'},
    ],
    'gidsen': [{'loc': 'https://www.witgoedaanbod.nl/gidsen/x', 'lastmod': None}],
}
uit = indexnow.gewijzigde_adressen(per_soort, date(2026, 9, 21))
check('gewijzigde adressen', uit == [
    'https://www.witgoedaanbod.nl/category/drogers',
    'https://www.witgoedaanbod.nl/product/a',
    'https://www.witgoedaanbod.nl/product/b',
], repr(uit))

# 2. Stukken van hooguit 10.000.
lijst = [f'https://www.witgoedaanbod.nl/product/{i}' for i in range(25001)]
stukken = indexnow.berichten(lijst)
check('stukken van 10.000', [len(s) for s in stukken] == [10000, 10000, 5001])

# 3. Het bericht zelf, met een neppe verzender.
verstuurd = []
def poster(body):
    verstuurd.append(body)
    return 202
uitkomst = indexnow.verstuur(uit, 'www.witgoedaanbod.nl', 'sleutel123',
                             'https://www.witgoedaanbod.nl/indexnow-sleutel123.txt', poster=poster)
check('één bericht, status 202', uitkomst == [(3, 202)], repr(uitkomst))
b = verstuurd[0]
check('bericht: host', b['host'] == 'www.witgoedaanbod.nl')
check('bericht: key + keyLocation', b['key'] == 'sleutel123' and b['keyLocation'].endswith('/indexnow-sleutel123.txt'))
check('bericht: urlList', b['urlList'] == uit)

# 4. Niets te melden: geen bericht.
check('leeg = geen bericht', indexnow.verstuur([], 'h', 'k', 'l', poster=poster) == [] and len(verstuurd) == 1)

# 5. Sleutelbestand-pad.
check('sleutelbestand', indexnow.sleutelbestand('abc') == '/indexnow-abc.txt')

print(f"\n{fouten} fout")
sys.exit(1 if fouten else 0)
