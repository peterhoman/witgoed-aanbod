"""Controle na uitrol: staat Witgoedhuis op de site? (alleen lezen, volgt geen
doorverwijzing naar de winkel). Draaien: python scripts/controle_witgoedhuis_live.py [wachtseconden]
"""
import http.client
import json
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
time.sleep(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
B = 'https://www.witgoedaanbod.nl'
KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129 Safari/537.36',
       'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Dest': 'document'}


def get(pad):
    return urllib.request.urlopen(urllib.request.Request(B + pad, headers=KOP), timeout=120).read().decode()


print(get('/api/gezondheid').strip())
s = json.loads(get('/api/sync-status'))
print('\nwitgoedhuis in winkelbijdrage:', [w for w in s['winkelbijdrage'] if w['winkel'] == 'witgoedhuis'])
print('laatste sync witgoedhuis:', s['laatste_sync_per_winkel'].get('witgoedhuis'))
print('laatste synclogs:', [(l['gestart'][:16], l['synced'], l['updated'], l['fouten'][:80]) for l in s['laatste_synclogs'][:3]])

# Een product dat Witgoedhuis voert: de Bosch-wasmachine uit de meting, of het
# eerste gedeelde product uit de feed.
sys.path.insert(0, ".")
from sync_witgoedhuis import FEED_URL_DEFAULT, _feed_records  # noqa: E402
sys.path.insert(0, '.')
records = _feed_records(FEED_URL_DEFAULT)
sm = get('/sitemap-producten.xml')
gevonden = 0
for adres in re.findall(r'<loc>https://[^/]+(/product/[^<]+)</loc>', sm):
    ean = adres.rsplit('-', 1)[-1].lstrip('0')
    if ean in records:
        h = get(adres)
        knop = re.search(r'href="(/uit/aanbieding/\d+\?k=[^"]+)"[^>]*>[^<]*</a>\s*</[^>]+>\s*', h)
        staat = 'Witgoedhuis' in h
        print(f"\n{adres[9:60]}: Witgoedhuis op de pagina: {staat}")
        if staat:
            gevonden += 1
            # Klik op de Witgoedhuis-knop zonder te volgen: waar zou hij heen gaan?
            for m in re.finditer(r'href="(/uit/aanbieding/(\d+)\?k=[^"]+)"', h):
                c = http.client.HTTPSConnection('www.witgoedaanbod.nl', timeout=60)
                c.request('GET', m.group(1).replace('&amp;', '&'), headers=dict(KOP, Referer=B + adres))
                naar = c.getresponse().getheader('Location') or ''
                if 'ds1.nl' in naar:
                    print('   Witgoedhuis-knop gaat naar:', naar[:120])
                    break
        if gevonden >= 2:
            break
