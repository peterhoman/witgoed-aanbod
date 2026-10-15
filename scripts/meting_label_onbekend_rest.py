"""Welke teksten noemen het label nog onbekend bij een EPREL-treffer, en waarom?
Alleen lezen. Draaien: railway run -s Postgres python scripts/meting_label_onbekend_rest.py
"""
import os, re, sys
import psycopg2
sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select p.slug, p.ai_description, e.productgroep, e.energieklasse,
                    (select max(generated_at) from ai_content a where a.product_id=p.id and a.content_type='beschrijving')
             from products p join eprel_data e on e.product_id=p.id and e.gevonden
             where p.is_available and p.ai_description ~* 'energie(label|klasse)[^.]{0,60}(niet bekend|onbekend|ontbreekt)'""")
for slug, t, groep, klasse, wanneer in c.fetchall():
    zin = [z for z in re.split(r'(?<=[.!?])\s', t) if re.search('energie(label|klasse)', z, re.I)]
    print(slug[:55], '|', groep, klasse, '|', wanneer, '|', zin[0][:160] if zin else '')
