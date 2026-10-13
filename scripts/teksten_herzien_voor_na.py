"""Herziening EPREL-teksten (13 okt 2026): vóór de herziening de oude
openingszinnen vastleggen, erna vergelijken. Alleen lezen.
    railway run -s Postgres python scripts/teksten_herzien_voor_na.py voor
    railway run -s Postgres python scripts/teksten_herzien_voor_na.py na
"""
import json
import os
import re
import sys

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
BESTAND = 'scripts/teksten_herzien_voor.json'
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()


def eerste_zin(t):
    return re.split(r'(?<=[.!?])\s', (t or '').strip(), 1)[0]


if sys.argv[1] == 'voor':
    c.execute("""select p.id, p.slug, p.ai_description from products p
                 where p.is_available and exists (select 1 from eprel_data e where e.product_id = p.id and e.gevonden)
                   and (p.id in (select product_id from catalogus_aanvullingen where product_id is not null)
                        or p.ai_description ilike '%%niet bekend%%' or p.ai_description ilike '%%geen specificaties%%')""")
    rijen = {str(i): {'slug': s, 'oud': eerste_zin(t)} for i, s, t in c.fetchall()}
    json.dump(rijen, open(BESTAND, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('vastgelegd:', len(rijen))
else:
    voor = json.load(open(BESTAND, encoding='utf-8'))
    c.execute("""select p.id, p.ai_description,
                        (select max(generated_at) from ai_content a where a.product_id = p.id
                         and a.content_type = 'beschrijving')
                 from products p where p.id = any(%s)""", ([int(i) for i in voor],))
    herschreven, nog = 0, []
    nu = {}
    for pid, tekst, wanneer in c.fetchall():
        nu[str(pid)] = tekst
        if wanneer and wanneer.isoformat() >= '2026-10-13':
            herschreven += 1
    c.execute("""select count(*) from products p
                 where p.is_available and exists (select 1 from eprel_data e where e.product_id = p.id and e.gevonden)
                   and (p.ai_description ilike '%%niet bekend%%' or p.ai_description ilike '%%geen specificaties%%')""")
    rest = c.fetchone()[0]
    c.execute("""select count(*) from products p
                 where p.is_available and exists (select 1 from eprel_data e where e.product_id = p.id and e.gevonden)
                   and p.ai_description ~* 'energie(label|klasse)[^.]{0,60}(niet bekend|onbekend|ontbreekt)'""")
    label = c.fetchone()[0]
    print(f'herschreven: {herschreven} van {len(voor)} | nog "niet bekend"/"geen specificaties" met EPREL: {rest} '
          f'| waarvan label onbekend: {label}')
    for pid in list(voor)[:400]:
        if voor[pid]['oud'] != eerste_zin(nu.get(pid)) and 'energie' in voor[pid]['oud'].lower() + (nu.get(pid) or '').lower():
            print('\n', 'https://www.witgoedaanbod.nl/product/' + voor[pid]['slug'])
            print('   oud:', voor[pid]['oud'][:200])
            print('   nieuw:', eerste_zin(nu.get(pid))[:200])
            if (nog := nog + [pid]) and len(nog) >= 3:
                break
