"""AI-tekstkosten: per dag in oktober, totaal, en het normale niveau. Alleen lezen.
Draaien: railway run -s Postgres python scripts/meting_ai_kosten.py
"""
import os, sys
import psycopg2
sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select date(generated_at), count(*), round(sum(coalesce(cost,0))::numeric, 3)
             from ai_content where content_type='beschrijving' and generated_at >= '2026-09-01'
             group by 1 order by 1""")
rijen = c.fetchall()
for d, n, e in rijen:
    if str(d) >= '2026-10-01':
        print(d, n, 'teksten, EUR', e)
okt = [r for r in rijen if str(r[0]) >= '2026-10-01']
print('oktober tot nu: ', sum(r[1] for r in okt), 'teksten, EUR', sum(float(r[2]) for r in okt))
sep = [r for r in rijen if str(r[0]) < '2026-10-01']
print('september:', sum(r[1] for r in sep), 'teksten, EUR', sum(float(r[2]) for r in sep))
c.execute("select round(avg(cost)::numeric,4) from ai_content where content_type='beschrijving' and generated_at >= '2026-10-13'")
print('gem. per tekst sinds 13 okt: EUR', c.fetchone()[0])
c.execute("select content_type, count(*), round(sum(coalesce(cost,0))::numeric,3) from ai_content where generated_at >= '2026-10-01' group by 1")
print('alle soorten okt:', c.fetchall())
