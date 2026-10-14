"""Herschreven teksten (na 13 okt) die toch nog 'niet bekend' of 'label onbekend'
zeggen bij een EPREL-treffer. Alleen lezen.
Draaien: railway run -s Postgres python scripts/meting_herschreven_nog_onbekend.py
"""
import os
import re
import sys

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select p.slug, p.ai_description from products p
             join ai_content a on a.product_id = p.id and a.content_type = 'beschrijving'
             where p.is_available and a.generated_at >= '2026-10-13'
               and exists (select 1 from eprel_data e where e.product_id = p.id and e.gevonden)
               and (p.ai_description ilike '%%niet bekend%%' or p.ai_description ilike '%%geen specificaties%%')""")
rijen = c.fetchall()
label = [r for r in rijen if re.search(r'energie(label|klasse)[^.]{0,60}(niet bekend|onbekend|ontbreekt)', r[1], re.I)]
print('herschreven met nog "niet bekend"/"geen specificaties":', len(rijen), '| waarvan label onbekend:', len(label))
for slug, t in rijen[:4]:
    zin = [z for z in re.split(r'(?<=[.!?])\s', t) if re.search('niet bekend|geen specificaties', z, re.I)]
    print('-', slug[:60], '|', zin[0][:200] if zin else '')
