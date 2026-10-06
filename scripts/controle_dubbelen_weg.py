"""Controle: zijn de drie dubbele kleurvarianten weg en sturen hun adressen door?
Plus welke nieuwe producten er in hun plaats kwamen. Alleen lezen.
Draaien: python scripts/controle_dubbelen_weg.py [wachtseconden]
"""
import http.client
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
time.sleep(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
B = 'www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36'}
for pad in ['/product/miele-fns-4382-d-vrijstaande-diepvries-4002516741725',
            '/product/miele-kfn-4795-ad-vrijstaande-koel-vriescombinatie-4002516742104',
            '/product/miele-kfn-4799-ad-obsw-matt-125-gala-edition-koel--4002516711698']:
    c = http.client.HTTPSConnection(B, timeout=60)
    c.request('GET', pad, headers=KOP)
    r = c.getresponse()
    print(r.status, pad.rsplit('/', 1)[-1][:50], '->', (r.getheader('Location') or '').rsplit('/', 1)[-1])
sm = urllib.request.urlopen(urllib.request.Request(f'https://{B}/sitemap-producten.xml', headers=KOP),
                            timeout=120).read().decode()
na = set(re.findall(r'<loc>([^<]+)</loc>', sm))
lijst = {l.split('\t')[0] for l in open('scripts/aanvulling_100.txt', encoding='utf-8')}
voor = set(re.findall(r'<loc>([^<]+)</loc>', open('scripts/sitemap_voor_aanvulling.xml', encoding='utf-8').read()))
print('van de proeflijst nog in de sitemap:', len(lijst & na), 'van', len(lijst))
print('nieuw sinds vanochtend, niet in de proeflijst:', sorted(a.rsplit('/', 1)[-1] for a in (na - voor - lijst)))
