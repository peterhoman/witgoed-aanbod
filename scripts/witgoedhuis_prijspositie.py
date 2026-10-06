"""Bij hoeveel gekoppelde apparaten is Witgoedhuis de goedkoopste, en hoeveel
scheelt het met de op één na goedkoopste? Leest de prijsregels van onze
productpagina's (alleen lezen). Draaien: python scripts/witgoedhuis_prijspositie.py
"""
import html
import re
import statistics
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
B = 'https://www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=KOP), timeout=60).read().decode('utf-8', 'replace')


def prijs(tekst):
    return float(tekst.replace('.', '').replace(',', '.'))


sm = get(B + '/sitemap-producten.xml')
adressen = re.findall(r'<loc>([^<]+)</loc>', sm)
uitkomst = []
for adres in adressen:
    h = get(adres) if False else None
uitkomst = []
# Alleen pagina's waar Witgoedhuis op staat: eerst de winkelbijdrage gebruiken
# is niet per product beschikbaar, dus alle pagina's met het logo zoeken via
# de feed-EAN's.
sys.path.insert(0, '.')
from sync_witgoedhuis import FEED_URL_DEFAULT, _feed_records  # noqa: E402
feed = set(_feed_records(FEED_URL_DEFAULT))
kandidaten = [a for a in adressen if a.rsplit('-', 1)[-1].lstrip('0') in feed]
print('pagina\'s met een Witgoedhuis-EAN:', len(kandidaten))
for adres in kandidaten:
    h = get(adres)
    rijen = re.findall(r'<li class="offer-row[^"]*">.*?alt="([^"]+)".*?class="offer-price">([^<]+)<', h, re.S)
    prijzen = [(winkel, prijs(re.sub(r'[^\d,.]', '', html.unescape(p)))) for winkel, p in rijen]
    if not any(w == 'Witgoedhuis' for w, _ in prijzen):
        continue
    prijzen.sort(key=lambda x: x[1])
    wh = next(p for w, p in prijzen if w == 'Witgoedhuis')
    anderen = [p for w, p in prijzen if w != 'Witgoedhuis']
    uitkomst.append({'winkels': len(prijzen), 'wh': wh, 'laagste_ander': min(anderen) if anderen else None,
                     'goedkoopste': prijzen[0][0] == 'Witgoedhuis' and (not anderen or wh < min(anderen))})
    time.sleep(0.2)

n = len(uitkomst)
alleen = [u for u in uitkomst if u['laagste_ander'] is None]
goedkoopst = [u for u in uitkomst if u['goedkoopste'] and u['laagste_ander'] is not None]
gelijk = [u for u in uitkomst if u['laagste_ander'] is not None and abs(u['wh'] - u['laagste_ander']) < 0.01]
print(f'Witgoedhuis op {n} productpagina\'s; daarvan enige winkel: {len(alleen)}')
print(f'Witgoedhuis goedkoopste (met andere winkels erbij): {len(goedkoopst)}; gelijk met de goedkoopste andere: {len(gelijk)}')
if goedkoopst:
    verschil = [u['laagste_ander'] - u['wh'] for u in goedkoopst]
    pct = [100 * (u['laagste_ander'] - u['wh']) / u['laagste_ander'] for u in goedkoopst]
    print(f'  voorsprong op de op één na goedkoopste: mediaan € {statistics.median(verschil):.2f} '
          f'({statistics.median(pct):.1f}%), gemiddeld € {statistics.mean(verschil):.2f}, '
          f'kleinste € {min(verschil):.2f}, grootste € {max(verschil):.2f}')
duurder = [u for u in uitkomst if u['laagste_ander'] is not None and u['wh'] > u['laagste_ander'] + 0.01]
if duurder:
    print(f'Witgoedhuis duurder dan de goedkoopste: {len(duurder)}; mediaan € '
          f"{statistics.median([u['wh'] - u['laagste_ander'] for u in duurder]):.2f} meer")
print('aantal winkels per pagina (met Witgoedhuis):',
      sorted(__import__('collections').Counter(u['winkels'] for u in uitkomst).items()))
