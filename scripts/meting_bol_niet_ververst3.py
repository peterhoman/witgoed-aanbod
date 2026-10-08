"""Deel 3: created_at/updated_at van de oude Bol-rijen. Alleen lezen."""
import os, sys
import psycopg2
sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select date_trunc('hour', created_at), count(*), min(last_synced), max(last_synced), min(updated_at), max(updated_at)
             from offers where retailer='bol' and last_synced < now() - interval '3 days' group by 1 order by 1""")
for r in c.fetchall(): print(r)
