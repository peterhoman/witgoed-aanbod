"""Teksten (van voor 13 okt) met 'ontbreekt' bij een EPREL-treffer, en of de pagina het label toont.
Alleen lezen. Draaien: railway run -s Postgres python scripts/meting_ontbreekt.py
"""
import os, sys
import psycopg2
sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select count(*) from products p join eprel_data e on e.product_id=p.id and e.gevonden
             join ai_content a on a.product_id=p.id and a.content_type='beschrijving'
             where p.is_available and a.generated_at < '2026-10-13' and p.ai_description ilike '%%ontbreekt%%'""")
print('oud + EPREL + "ontbreekt":', c.fetchone()[0])
