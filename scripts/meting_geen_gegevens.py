"""Oude teksten (van voor 13 okt) bij een EPREL-treffer die zeggen dat er geen
gegevens zijn, in andere bewoordingen dan 'niet bekend'/'geen specificaties'/'ontbreekt'.
Alleen lezen. Draaien: railway run -s Postgres python scripts/meting_geen_gegevens.py
"""
import collections, os, re, sys
import psycopg2
sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select p.slug, p.ai_description from products p
             join eprel_data e on e.product_id=p.id and e.gevonden
             join ai_content a on a.product_id=p.id and a.content_type='beschrijving'
             where p.is_available and a.generated_at < '2026-10-13'""")
rijen = c.fetchall()
print('oude teksten met EPREL-treffer:', len(rijen))
pat = re.compile(r'geen (technische |verdere |nadere )?(gegevens|specificaties|informatie|details)|niet (vastgelegd|opgenomen|beschikbaar)|onbekend', re.I)
treffers = [(s, t) for s, t in rijen if pat.search(t or '')]
print('waarvan "geen gegevens/niet vastgelegd/onbekend":', len(treffers))
zonder_label = [(s, t) for s, t in rijen if not re.search(r'energie(label|klasse)', t or '', re.I)]
print('waarvan geen woord over energielabel/-klasse:', len(zonder_label))
for s, t in treffers[:5]:
    print('-', s[:60], '|', pat.search(t).group(0), '|', t[:110].replace('\n', ' '))
