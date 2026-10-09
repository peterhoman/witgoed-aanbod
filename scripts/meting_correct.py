"""Meting Correct.nl-feed (Daisycon, programma 17400), 9 okt, vraag SEO-chat:
- hoeveel EAN's koppelen aan bestaande (leverbare) producten;
- bij hoeveel daarvan is Correct de goedkoopste (en hoeveel nieuwe vergelijkingen:
  producten die nu maar 1 winkel hebben);
- hoeveel witgoed ontbreekt bij ons terwijl Correct én een andere winkel het verkopen;
- velden: conditie, voorraad, 'Koopjeskelder', verversing (update_date), linkdomein.
Alleen lezen; de database wordt alleen gelezen, er gaat niets naar een netwerk
behalve het ophalen van de feeds zelf (zoals een sync).
Draaien: railway run -s Postgres python scripts/meting_correct.py
Ruwe uitkomst ook in scripts/meting_correct.json.
"""
import collections
import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')
PG = os.environ['DATABASE_PUBLIC_URL']
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'  # niets naar productie schrijven

import psycopg2  # noqa: E402

from catalogus_aanvulling import _feeds  # noqa: E402
from catalogus_uitzonderingen import is_geen_apparaat  # noqa: E402
from ean_match import ean_sleutel  # noqa: E402
from sync_mediamarkt import classify  # noqa: E402
from sync_products import EXCLUDE_KEYWORDS, MIN_PRICES  # noqa: E402

URL = ('https://daisycon.io/datafeed/?media_id=428244&program_id=17400&standard_id=6'
       '&language_code=nl&locale_id=1&type=xml&records=100')


def veld(info, naam):
    e = info.find(naam)
    return (e.text or '').strip() if e is not None and e.text else ''


rijen, url, paginas = [], URL, 0
while url and paginas < 400:
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'witgoedaanbod-meting/1.0'}),
                                timeout=180) as r:
        volgende = r.headers.get('X-Next-Url')
        boom = ET.fromstring(r.read())
    for p in boom.iter('product'):
        info = p.find('product_info')
        if info is None:
            continue
        rijen.append({k: veld(info, k) for k in ('ean', 'title', 'brand', 'category', 'category_path', 'price',
                                                 'price_old', 'in_stock', 'condition', 'status', 'update_date',
                                                 'link', 'model', 'description')})
    url, paginas = volgende, paginas + 1
    time.sleep(0.3)
print('feedproducten:', len(rijen), 'in', paginas, "pagina's")
print('met EAN:', sum(1 for r in rijen if r['ean']))
print('conditie:', collections.Counter(r['condition'] for r in rijen).most_common(8))
print('in_stock:', collections.Counter(r['in_stock'] for r in rijen).most_common())
print('status:', collections.Counter(r['status'] for r in rijen).most_common())
print('linkdomein:', collections.Counter(r['link'].split('/')[2] if r['link'] else '' for r in rijen).most_common(3))
upd = sorted(r['update_date'] for r in rijen if r['update_date'])
print('update_date: oudste', upd[0] if upd else '-', '| nieuwste', upd[-1] if upd else '-')
vandaag = datetime.utcnow().strftime('%Y-%m-%d')
print('bijgewerkt in de laatste 3 dagen:', sum(1 for u in upd if u[:10] >= (datetime.utcnow().date().fromordinal(datetime.utcnow().date().toordinal() - 3)).isoformat()))
koop = [r for r in rijen if 'koopjes' in (r['category'] + r['category_path'] + r['title']).lower()]
print('Koopjeskelder-vermelding:', len(koop), [r['title'][:50] for r in koop[:3]])

# Witgoed volgens onze eigen indeling.
witgoed = {}
for r in rijen:
    if not r['ean'] or r['in_stock'].lower() != 'true':
        continue
    if r['condition'] not in ('', 'new'):
        continue
    # Koopjeskelder (opendoos/demo, alleen afhalen): Correct's eigen
    # modelnummer eindigt dan op 'B' (getoetst 9 okt tegen de sitetag, zie
    # scripts/meting_correct_koopjes.py).
    if r['model'].upper().endswith('B'):
        continue
    cat = classify(r['title'])
    laag = r['title'].lower()
    try:
        prijs = float(r['price'])
    except ValueError:
        continue
    if not cat or is_geen_apparaat(r['title']) or any(w in laag for w in EXCLUDE_KEYWORDS):
        continue
    if prijs < MIN_PRICES.get(cat, 0):
        continue
    witgoed[ean_sleutel(r['ean'])] = (cat, prijs, r['title'])
print('witgoed (onze indeling, nieuw, op voorraad):', len(witgoed),
      collections.Counter(v[0] for v in witgoed.values()).most_common())

c = psycopg2.connect(PG).cursor()
c.execute("""select p.ean, p.is_available,
                    min(o.price) filter (where o.is_available),
                    count(distinct o.retailer) filter (where o.is_available)
             from products p left join offers o on o.product_id = p.id
             where not p.is_example group by p.id""")
ons = {ean_sleutel(e): (lev, laag, n) for e, lev, laag, n in c.fetchall() if e}
gekoppeld = {k: v for k, v in witgoed.items() if k in ons}
leverbaar = {k: v for k, v in gekoppeld.items() if ons[k][0] and ons[k][1]}
goedkoopst = [k for k, v in leverbaar.items() if v[1] < float(ons[k][1]) - 0.5]
gelijk = [k for k, v in leverbaar.items() if abs(v[1] - float(ons[k][1])) <= 0.5]
nieuwe_vergelijking = [k for k in leverbaar if ons[k][2] == 1]
herleefd = [k for k in gekoppeld if not ons[k][0]]
print('\nkoppelt aan een bestaand product:', len(gekoppeld), '| waarvan nu leverbaar:', len(leverbaar),
      '| waarvan nu niet leverbaar (komt terug):', len(herleefd))
print('Correct goedkoper dan onze laagste prijs:', len(goedkoopst), '| even duur:', len(gelijk))
print('van 1 naar 2 winkels (nieuwe vergelijking):', len(nieuwe_vergelijking))
verschil = sorted(float(ons[k][1]) - leverbaar[k][1] for k in goedkoopst)
if verschil:
    print('voordeel bij goedkoopste: mediaan EUR %.0f, max EUR %.0f' % (verschil[len(verschil) // 2], verschil[-1]))

# Ontbreekt bij ons, maar Correct én een andere winkel (offers-only feeds) verkopen het.
anderen = collections.defaultdict(set)
for r in _feeds():
    anderen[ean_sleutel(r[0])].add(r[6])
ontbreekt = {k: v for k, v in witgoed.items() if k not in ons}
met_ander = {k: v for k, v in ontbreekt.items() if anderen.get(k)}
print('\nwitgoed bij Correct dat niet bij ons staat:', len(ontbreekt),
      '| waarvan ook bij een andere winkel (Expert/EP/Voordeligwitgoed/Alternate/Witgoedhuis):', len(met_ander),
      collections.Counter(v[0] for v in met_ander.values()).most_common())

json.dump({'feed': len(rijen), 'witgoed': len(witgoed), 'gekoppeld': len(gekoppeld), 'leverbaar': len(leverbaar),
           'goedkoopst': len(goedkoopst), 'nieuwe_vergelijking': len(nieuwe_vergelijking), 'herleefd': len(herleefd),
           'ontbreekt': len(ontbreekt), 'ontbreekt_met_ander': len(met_ander),
           'voorbeelden_goedkoopst': [(k, leverbaar[k][2], leverbaar[k][1], float(ons[k][1])) for k in goedkoopst[:15]],
           'voorbeelden_met_ander': [(k, v[2], v[1], sorted(anderen[k])) for k, v in list(met_ander.items())[:15]]},
          open('scripts/meting_correct.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
