"""Hoeveel leverbare producten (buiten de proef) hebben een eigen tekst die
zegt dat label/energie niet bekend is, terwijl er een EPREL-treffer is?
Alleen lezen. Draaien: railway run -s Postgres python scripts/meting_teksten_zonder_eprel.py
"""
import os
import sys

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select count(*),
                    count(*) filter (where p.ai_description ilike '%%niet bekend%%'
                                     or p.ai_description ilike '%%geen specificaties%%'),
                    count(*) filter (where p.ai_description ~* 'energie(label|klasse)[^.]{0,60}(niet bekend|onbekend|ontbreekt)')
             from products p join eprel_data e on e.product_id = p.id and e.gevonden
             where p.is_available and p.ai_description is not null
               and p.id not in (select product_id from catalogus_aanvullingen where product_id is not null)""")
print('buiten de proef, met EPREL: totaal / tekst zegt "niet bekend"/"geen specificaties" / zegt label onbekend:', c.fetchone())
