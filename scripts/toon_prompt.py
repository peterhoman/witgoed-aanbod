"""Waarom kreeg een tekst geen EPREL-gegevens mee? Toont de EPREL-rij en de
uitkomst van eprel.koppeling_klopt voor een product (op slug). Alleen lezen,
zonder de app te starten (geen bootmigraties tegen productie).
Draaien: railway run -s Postgres python scripts/toon_prompt.py <slug>
"""
import os
import sys

import psycopg2

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')
PG = os.environ['DATABASE_PUBLIC_URL']
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
from eprel import koppeling_klopt  # noqa: E402

c = psycopg2.connect(PG).cursor()
c.execute("""select p.title, e.gezocht_op, e.modelnummer, e.productgroep, e.energieklasse,
                    (e.gegevens is not null), e.opgehaald_at
             from products p join eprel_data e on e.product_id = p.id and e.gevonden
             where p.slug = %s""", (sys.argv[1],))
for titel, gezocht, model, groep, klasse, heeft, wanneer in c.fetchall():
    print('titel     :', titel)
    print('gezocht_op:', gezocht, '| model:', model, '| groep:', groep, '| klasse:', klasse, '| gegevens:', heeft)
    print('opgehaald :', wanneer, '| koppeling_klopt:', koppeling_klopt(gezocht, model, titel))
