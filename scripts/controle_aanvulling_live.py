"""Controle na de eerste ronde van de catalogusaanvulling (alleen lezen):
nieuwe adressen in de sitemap t.o.v. scripts/sitemap_voor_aanvulling.xml,
per categorie, winkels per pagina en EPREL-blok.
Draaien: python scripts/controle_aanvulling_live.py [wachtseconden]
"""
import re
import sys
import time
import urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
time.sleep(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
B = 'https://www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=KOP), timeout=120).read().decode('utf-8', 'replace')


voor = set(re.findall(r'<loc>([^<]+)</loc>', open('scripts/sitemap_voor_aanvulling.xml', encoding='utf-8').read()))
na = set(re.findall(r'<loc>([^<]+)</loc>', get(B + '/sitemap-producten.xml')))
nieuw = sorted(na - voor)
print(f'sitemap voor {len(voor)}, na {len(na)}, nieuw {len(nieuw)}, verdwenen {len(voor - na)}')
cats, winkels, eprel, rijen = Counter(), Counter(), 0, []
for adres in nieuw:
    h = get(adres)
    cat = re.search(r"\"item\": \"https://www.witgoedaanbod.nl/category/([a-z-]+)\", \"name\": \"[^\"]+\", \"position\": 2", h)
    n = len(re.findall(r'<li class="offer-row', h))
    heeft_eprel = 'Gegevens van het energielabel' in h
    cats[cat.group(1) if cat else '?'] += 1
    winkels[n] += 1
    eprel += heeft_eprel
    rijen.append(f'{adres}\t{cat.group(1) if cat else "?"}\t{n} winkels\t{"EPREL" if heeft_eprel else ""}')
    time.sleep(0.2)
print('per categorie:', dict(cats))
print('winkels per pagina:', dict(sorted(winkels.items())))
print('met EPREL-blok:', eprel)
open('scripts/aanvulling_adressen.txt', 'w', encoding='utf-8').write('\n'.join(rijen) + '\n')
print('lijst: scripts/aanvulling_adressen.txt')
