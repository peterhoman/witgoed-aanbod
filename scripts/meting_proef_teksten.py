"""Hoeveel van de proefproducten (catalogus_aanvullingen) hebben een eigen
tekst (AIContent 'beschrijving' en zichtbaar via products.ai_description)?
Alleen lezen. Draaien: railway run -s Postgres python scripts/meting_proef_teksten.py
"""
import os
import sys

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select count(*),
                    count(*) filter (where p.ai_description is not null and p.ai_description <> ''),
                    count(*) filter (where exists (select 1 from ai_content a where a.product_id = p.id
                                                   and a.content_type = 'beschrijving')),
                    count(*) filter (where p.is_available)
             from catalogus_aanvullingen ca join products p on p.id = ca.product_id""")
print('proef: totaal / zichtbare eigen tekst / tekst opgeslagen / leverbaar:', c.fetchone())
c.execute("""select p.slug, p.is_available, left(coalesce(p.ai_description, ''), 90)
             from catalogus_aanvullingen ca join products p on p.id = ca.product_id
             where p.title ilike '%%KFN 4397%%' or p.ai_description is null or p.ai_description = ''""")
for r in c.fetchall():
    print(r)
