"""Linkcontrole: Bol-aanbieding van de Philips EP2336/40 (titel) met een URL
die 'ep2236' noemt. Alleen lezen.
Draaien: railway run -s Postgres python scripts/meting_bol_ep2336.py
"""
import os
import sys

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select p.title, p.ean, p.slug, o.url from offers o join products p on p.id = o.product_id
             where o.retailer = 'bol' and (p.title ilike %s or o.url ilike %s)""", ('%2336%', '%ep2236%'))
for r in c.fetchall():
    print(r)
