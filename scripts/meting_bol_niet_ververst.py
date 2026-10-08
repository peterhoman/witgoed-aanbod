"""Meting 8 okt: welke Bol-aanbiedingen zijn langer dan 3 dagen niet ververst,
per categorie en leverbaarheid. Alleen lezen.
Draaien: railway run -s Postgres python scripts/meting_bol_niet_ververst.py
"""
import os
import sys

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""
    select cat.slug, o.is_available, count(*), min(o.last_synced), max(o.last_synced)
    from offers o join products p on p.id = o.product_id join categories cat on cat.id = p.category_id
    where o.retailer = 'bol' and o.last_synced < now() - interval '3 days'
    group by 1, 2 order by 3 desc""")
for r in c.fetchall():
    print(r)
c.execute("""
    select date_trunc('day', o.last_synced)::date, count(*) from offers o
    where o.retailer = 'bol' group by 1 order by 1 desc limit 8""")
print('bol per dag laatst ververst:', c.fetchall())
c.execute("select started_at, finished_at, products_synced, products_updated from sync_logs order by id desc limit 6")
for r in c.fetchall():
    print('synclog', r)
