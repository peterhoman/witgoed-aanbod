"""Controle 10 okt: Witgoedhuis ging van ~140 naar 856 leverbare aanbiedingen.
Klopt dat? 12 willekeurige leverbare Witgoedhuis-aanbiedingen: onze prijs
tegen de prijs op witgoedhuis.nl (de winkelpagina, niet de trackinglink),
plus hoeveel nieuw zijn sinds 8 okt. Alleen lezen.
Draaien: railway run -s Postgres python scripts/controle_witgoedhuis_sprong.py
"""
import os
import re
import sys
import urllib.request

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select date(created_at), count(*) from offers where retailer='witgoedhuis' and is_available
             group by 1 order by 1""")
print('leverbare witgoedhuis-aanbiedingen per aanmaakdag:', c.fetchall())
c.execute("""select count(*) filter (where o2.price is not null and o.price < o2.price - 0.5),
                    count(*)
             from offers o
             left join lateral (select min(price) price from offers x
                                where x.product_id=o.product_id and x.retailer<>'witgoedhuis' and x.is_available) o2 on true
             where o.retailer='witgoedhuis' and o.is_available""")
print('witgoedhuis goedkoopste / totaal leverbaar:', c.fetchone())
c.execute("""select o.price, o.url, p.title from offers o join products p on p.id=o.product_id
             where o.retailer='witgoedhuis' and o.is_available order by random() limit 12""")
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
for prijs, url, titel in c.fetchall():
    try:
        h = urllib.request.urlopen(urllib.request.Request(url, headers=KOP), timeout=30).read().decode('utf-8', 'ignore')
        m = re.search(r'"price"\s*:\s*"?([\d.]+)', h) or re.search(r'itemprop="price"[^>]*content="([\d.]+)', h)
        voorraad = 'InStock' in h
        site = float(m.group(1)) if m else None
        print(f"{'OK    ' if site and abs(site - float(prijs)) < 1 else 'ANDERS'} wij {float(prijs):8.2f} | site {site} "
              f"| voorraad {voorraad} | {titel[:50]}")
    except Exception as e:  # noqa: BLE001
        print('fout', type(e).__name__, url[:70])
