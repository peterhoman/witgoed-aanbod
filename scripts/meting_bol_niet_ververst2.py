"""Meting 8 okt, deel 2: waar komen de 406 oude Bol-rijen vandaan?
Alleen lezen. Draaien: railway run -s Postgres python scripts/meting_bol_niet_ververst2.py
"""
import os
import sys

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("select column_name from information_schema.columns where table_name='offers' order by ordinal_position")
print('kolommen offers:', [r[0] for r in c.fetchall()])
c.execute("""select min(o.id), max(o.id), count(*) from offers o
             where o.retailer='bol' and o.last_synced < now() - interval '3 days'""")
print('oude bol-rijen id-bereik:', c.fetchone())
c.execute("select min(id), max(id) from offers where retailer='bol' and last_synced >= now() - interval '1 day'")
print('verse bol-rijen id-bereik:', c.fetchone())
c.execute("""select p.is_available, (select count(*) from offers o2 where o2.product_id=p.id and o2.retailer<>'bol' and o2.is_available),
                    count(*)
             from offers o join products p on p.id=o.product_id
             where o.retailer='bol' and o.last_synced < now() - interval '3 days'
             group by 1, 2 order by 3 desc limit 10""")
print('product leverbaar / andere leverbare winkels / aantal:', c.fetchall())
c.execute("""select o.id, o.last_synced, p.title, p.ean from offers o join products p on p.id=o.product_id
             where o.retailer='bol' and o.last_synced < now() - interval '3 days'
             order by o.last_synced desc limit 5""")
for r in c.fetchall():
    print(r)
