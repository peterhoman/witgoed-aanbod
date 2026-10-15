"""Controle: onze Witgoedhuis-prijs tegen de prijs op witgoedhuis.nl voor
opgegeven EAN's (de winkelpagina, niet de trackinglink). Alleen lezen.
Draaien: railway run -s Postgres python scripts/controle_witgoedhuis_eans.py EAN [EAN ...]
"""
import os
import re
import sys
import urllib.request

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
for ean in sys.argv[1:]:
    c.execute("""select o.price, o.url, p.title, o.is_available,
                        (select min(x.price) from offers x where x.product_id = p.id and x.retailer <> 'witgoedhuis'
                         and x.is_available)
                 from offers o join products p on p.id = o.product_id
                 where o.retailer = 'witgoedhuis' and p.ean = %s""", (ean,))
    rij = c.fetchone()
    if not rij:
        print(ean, 'geen witgoedhuis-aanbieding')
        continue
    prijs, url, titel, lev, ander = rij
    try:
        h = urllib.request.urlopen(urllib.request.Request(url, headers=KOP), timeout=30).read().decode('utf-8', 'ignore')
        m = re.search(r'"price"\s*:\s*"?([\d.]+)', h)
        site = float(m.group(1)) if m else None
        oud = re.search(r'"(?:highPrice|price_old|oldPrice)"\s*:\s*"?([\d.]+)', h)
    except Exception as e:  # noqa: BLE001
        site, oud = f'fout {type(e).__name__}', None
    print(f"{ean} wij {float(prijs):8.2f} | site {site} | andere winkels laagste {ander} | {titel[:45]}")
