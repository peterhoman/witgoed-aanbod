"""Controle: bij een prijssprong uit de dagcontrole de productpagina openen
en per winkel de laatste prijspunten tonen (actie afgelopen of fout?).
Alleen lezen. Draaien: python scripts/controle_prijssprongen.py EAN [EAN ...]
"""
import collections
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
B = 'https://www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
sm = urllib.request.urlopen(urllib.request.Request(B + '/sitemap-producten.xml', headers=KOP), timeout=120).read().decode()
adressen = re.findall(r'<loc>([^<]+)</loc>', sm)
for ean in sys.argv[1:]:
    adres = next((a for a in adressen if a.endswith(ean)), None)
    if not adres:
        print(ean, 'niet in sitemap')
        continue
    h = urllib.request.urlopen(urllib.request.Request(adres, headers=KOP), timeout=60).read().decode()
    punten = re.findall(r'(\d+ \w+): &#8364; ([\d.,]+) \(([^)]+)\)', h)
    per_winkel = collections.defaultdict(list)
    for datum, prijs, winkel in punten:
        per_winkel[winkel].append(f'{datum} {prijs}')
    print(ean, adres.rsplit('/', 1)[-1][:55])
    for winkel, rij in per_winkel.items():
        print('   ', winkel, '|', ' > '.join(rij[-3:]))
