"""Controle na uitrol: doorsturen van te kleine filterstappen (alleen lezen, volgt
geen doorverwijzing). Draaien: python scripts/controle_doorsturen_live.py [wachtseconden]
"""
import http.client
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
time.sleep(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
PADEN = ['/category/wasdroogcombinaties/toerental/1200-1400-toeren',
         '/category/wasdroogcombinaties/toerental/1400-1600-toeren',
         '/category/wasmachines/toerental/tot-1200-toeren',
         '/category/wasdroogcombinaties/toerental/onzin',
         '/category/vaatwassers/vulgewicht/vanaf-11-kg']
for pad in PADEN:
    c = http.client.HTTPSConnection('www.witgoedaanbod.nl', timeout=60)
    c.request('GET', pad, headers={'User-Agent': 'Mozilla/5.0 controle'})
    r = c.getresponse()
    print(r.status, pad, '->', r.getheader('Location') or '')
