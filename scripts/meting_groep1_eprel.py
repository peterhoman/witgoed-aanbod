"""Groep 1 (witgoed bij 2+ niet-Bol-winkels, niet op de site): merken, en een
EPREL-steekproef. Leest scripts/meting_feeds_overlap.json. Alleen lezen.
Draaien: python scripts/meting_groep1_eprel.py
"""
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')
from eprel import groepen_voor, zoek  # noqa: E402

d = json.load(open('scripts/meting_feeds_overlap.json', encoding='utf-8'))['ontbreekt']
groep1 = [dict(v, ean=e) for e, v in d.items() if len(v['winkels']) >= 2]
print('groep 1:', len(groep1))
merken = Counter((v['titel'].split() or ['?'])[0].upper().strip(',-') for v in groep1)
print('merken (top 15):', merken.most_common(15))
combis = Counter('+'.join(v['winkels']) for v in groep1)
print('winkelcombinaties:', combis.most_common(6))

kan = [v for v in groep1 if groepen_voor(v['cat'], v['titel'])]
print(f'in een EPREL-productgroep (koelkast, was, vaat, droog, oven, afzuigkap): {len(kan)}')
random.seed(6)
steek = random.sample(kan, min(80, len(kan)))
uit = Counter()
for v in steek:
    try:
        r = zoek(v['cat'], v['titel'], pauze=0.4)
        uit['gevonden' if r.get('gevonden') else ('geen typenummer' if not r.get('gezocht') else 'niet gevonden')] += 1
    except Exception as e:
        uit['fout ' + type(e).__name__] += 1
print(f'EPREL-steekproef van {len(steek)}:', dict(uit))
print('voorbeelden titels:', [v['titel'][:60] for v in random.sample(groep1, 8)])
