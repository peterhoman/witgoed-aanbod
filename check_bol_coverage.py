"""
Onderzoeksscript (leest alleen, wijzigt niets).

Beantwoordt de vraag: als we een nieuwe categorie zouden toevoegen, hebben Bol
en MediaMarkt dan allebei aanbod - en overlappen ze op EAN, zodat er echt iets
te vergelijken valt?

Draaien op Railway (waar de Bol-sleutels geldig zijn):

    /opt/venv/bin/python check_bol_coverage.py

Raakt de database niet aan.
"""

import os
import re
import sys

from sync_products import BolAPI
import sync_mediamarkt as smm

# Kandidaat-categorieën: (naam, Bol-zoektermen, patroon voor MediaMarkt-titels)
KANDIDATEN = [
    ('Kookplaten', ['Kookplaat', 'Inductiekookplaat'],
     r'kookplaat|inductiekookplaat|keramische kookplaat|gaskookplaat'),
    ('Fornuizen', ['Fornuis'],
     r'fornuis|gasfornuis|inductiefornuis'),
    ('Afzuigkappen', ['Afzuigkap'],
     r'afzuigkap|dampkap|wasemkap'),
    ('Koffiemachines', ['Koffiemachine', 'Espressomachine', 'Koffiezetapparaat'],
     r'koffie|espresso|volautomatische|senseo|nespresso|dolce gusto|percolator'),
    ('Waterkokers', ['Waterkoker'], r'waterkoker'),
    ('Broodroosters', ['Broodrooster'], r'broodrooster'),
    ('Blenders', ['Blender'], r'\bblender|sapcentrifuge|slowjuicer'),
    ('Keukenmachines', ['Keukenmachine', 'Foodprocessor'],
     r'keukenmachine|foodprocessor|standmixer|kitchenmachine'),
    ('Strijkijzers', ['Strijkijzer', 'Stoomstation'], r'strijkijzer|stoomstation|kledingstomer'),
]

# Ter controle: twee categorieën die de site al heeft. Hun overlap kennen we
# (ongeveer), dus die getallen laten zien of de meting klopt.
REFERENTIE = [
    ('Wasmachines (bestaand)', ['Wasmachines'], r'wasmachine|wasautomaat'),
    ('Koelkasten (bestaand)', ['Koelkasten'],
     r'koelkast|koel[-\s]?vries|vrieskast|vriezer'),
]


def mediamarkt_per_categorie(token):
    """Alle MediaMarkt-witgoed ophalen en per kandidaat-patroon de EANs verzamelen."""
    records = smm.collect_feed_products(token)
    witgoed = [r for r in records.values()
               if not r['from_main_feed'] or r['category_path'] in smm.WITGOED_CATEGORY_PATHS]
    print(f"[+] MediaMarkt: {len(witgoed)} producten in de witgoed-takken\n")
    return witgoed


def bol_eans(api, termen, limit=150):
    eans = {}
    for term in termen:
        for item in api.search_products(term, limit=limit):
            ean = str(item.get('ean') or '')
            if ean:
                eans[ean] = item.get('title', '')
    return eans


def main():
    token = os.getenv('TRADEDOUBLER_TOKEN')
    if not token:
        sys.exit('TRADEDOUBLER_TOKEN ontbreekt')

    api = BolAPI(os.getenv('BOL_CLIENT_ID'), os.getenv('BOL_CLIENT_SECRET'))
    if not api.authenticate():
        sys.exit('Bol-authenticatie mislukt: controleer BOL_CLIENT_ID / BOL_CLIENT_SECRET')

    witgoed = mediamarkt_per_categorie(token)

    kop = f"{'categorie':<24}{'Bol':>7}{'MediaMarkt':>12}{'beide':>8}{'% van Bol':>11}"
    print(kop)
    print('-' * len(kop))

    for naam, termen, patroon in REFERENTIE + KANDIDATEN:
        mm = {r['ean'] for r in witgoed if re.search(patroon, r['title'], re.IGNORECASE)}
        bol = bol_eans(api, termen)
        # accessoires uit de Bol-resultaten weren, net als de echte sync doet
        bol = {e: t for e, t in bol.items()
               if not any(k in t.lower() for k in smm.EXCLUDE_KEYWORDS)}
        beide = set(bol) & mm
        pct = (len(beide) / len(bol) * 100) if bol else 0
        print(f"{naam:<24}{len(bol):>7}{len(mm):>12}{len(beide):>8}{pct:>10.0f}%")

    print("\nBol-aantallen zijn zoekresultaten (max 150 per term), niet het hele Bol-assortiment.")
    print("'beide' = zelfde streepjescode bij Bol en MediaMarkt = een pagina met twee prijzen.")


if __name__ == '__main__':
    main()
