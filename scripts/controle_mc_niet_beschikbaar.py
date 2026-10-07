"""Controle: geven de producten die Merchant Center 'productpagina niet
beschikbaar' noemt bij ons een gewone pagina (200)? Zoekt ze op in de
sitemap en in de Merchant-feed. Alleen lezen.
Draaien: python scripts/controle_mc_niet_beschikbaar.py woord1 woord2 ...
"""
import http.client
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
B = 'www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
sm = urllib.request.urlopen(urllib.request.Request(f'https://{B}/sitemap-producten.xml', headers=KOP),
                            timeout=120).read().decode()
adressen = re.findall(r'<loc>([^<]+)</loc>', sm)
feed = urllib.request.urlopen(urllib.request.Request(f'https://{B}/feeds/google-merchant.xml', headers=KOP),
                              timeout=180).read().decode()
for woord in sys.argv[1:]:
    w = woord.lower()
    treffers = [a for a in adressen if w in a]
    infeed = re.findall(r'<link>([^<]*' + re.escape(w) + r'[^<]*)</link>', feed, re.I)
    print(f'{woord}: sitemap {len(treffers)}, feed {len(infeed)}')
    for a in (treffers or infeed)[:2]:
        pad = a.split(B, 1)[-1]
        c = http.client.HTTPSConnection(B, timeout=60)
        c.request('GET', pad, headers=KOP)
        r = c.getresponse()
        print('   ', r.status, pad[:90], r.getheader('Location') or '')
