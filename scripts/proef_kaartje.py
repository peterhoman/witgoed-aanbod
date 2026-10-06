"""Hoe oud is het kaartje op de winkelknoppen van een productpagina, en wat
antwoordt /uit/ erop? Volgt GEEN doorverwijzing naar een winkel (dan zou het
netwerk een klik tellen). Draaien: python scripts/proef_kaartje.py
"""
import http.client
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
B = 'www.witgoedaanbod.nl'
KOPPEN = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/129.0 Safari/537.36',
          'Accept-Language': 'nl-NL,nl;q=0.9', 'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Dest': 'document'}

sm = urllib.request.urlopen(urllib.request.Request(f'https://{B}/sitemap-producten.xml',
                                                   headers=KOPPEN), timeout=60).read().decode()
for pad in re.findall(r'<loc>https://[^/]+(/product/[^<]+)</loc>', sm)[100:106]:
    c = http.client.HTTPSConnection(B, timeout=60)
    c.request('GET', pad, headers=KOPPEN)
    r = c.getresponse()
    h = r.read().decode('utf-8', 'replace')
    knop = re.search(r'href="(/uit/[^"]+)"', h)
    if not knop:
        print(pad[:60], 'geen winkelknop')
        continue
    uit = knop.group(1).replace('&amp;', '&')
    ts = re.search(r'k=(\d+)\.', uit)
    leeftijd = (time.time() - int(ts.group(1))) / 3600 if ts else None
    c2 = http.client.HTTPSConnection(B, timeout=60)
    c2.request('GET', uit, headers=dict(KOPPEN, Referer=f'https://{B}{pad}'))
    r2 = c2.getresponse()
    naar = r2.getheader('Location') or ''
    soort = ('winkel' if naar.startswith('http') and B not in naar else
             'terug naar productpagina' if '/product/' in naar else naar[:60])
    print('   naar:', naar[:90])
    print(f"{pad[9:55]:46} kaartje {leeftijd:.1f} uur oud -> {r2.status} {soort}"
          if leeftijd is not None else f'{pad} geen kaartje')
    print('   cache-kop pagina:', r.getheader('Cache-Control'), '| Age:', r.getheader('Age'),
          '| edge:', r.getheader('x-railway-edge'))
    break
