"""Controle 7 okt: staan de proefproducten met een verse datum in de sitemap
(dan zaten ze in de IndexNow-ronde), en hoeveel EPREL-treffers zijn er nu.
Alleen lezen. Draaien: python scripts/controle_proef_7_okt.py
"""
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
B = 'https://www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}


def haal(pad):
    return urllib.request.urlopen(urllib.request.Request(B + pad, headers=KOP), timeout=120).read().decode()


sm = haal('/sitemap-producten.xml')
datum = dict(re.findall(r'<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>', sm))
lijst = [l.split('\t')[0].strip() for l in open('scripts/aanvulling_100.txt', encoding='utf-8') if l.strip()]
erin = [a for a in lijst if a in datum]
vers = [a for a in erin if datum[a][:10] >= '2026-10-06']
print('proeflijst in sitemap:', len(erin), 'van', len(lijst), '| met datum 6 of 7 okt:', len(vers))
print('oudste datums:', sorted({datum[a][:10] for a in erin})[:3])
e = json.loads(haal('/api/eprel'))
print('eprel:', {k: v for k, v in e.items() if not isinstance(v, (dict, list))})
