"""Linkcontrole deel 2: Awin-ID in de Coolblue-links (a=2969655) en per winkel
2 steekproeven van de winkelpagina zelf (de doel-URL, NIET de trackinglink;
dat telt bij geen enkel netwerk als klik). Alleen lezen.
Draaien: railway run -s Postgres python scripts/meting_linkcontrole2.py
"""
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import parse_qsl, unquote, urlsplit

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()
c.execute("""select count(*), count(*) filter (where affiliate_url ~ '[?&]a=2969655(&|$)')
             from offers where is_available and retailer='coolblue'""")
print('coolblue leverbaar / met Awin-ID a=2969655:', c.fetchone())

KOP = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/129 Safari/537.36',
       'Accept-Language': 'nl-NL,nl;q=0.9'}


def doel(link, url):
    q = dict(parse_qsl(urlsplit(link).query, keep_blank_values=True))
    for s in ('url', 'r'):
        if q.get(s, '').startswith('http'):
            return unquote(q[s])
    m = re.search(r'url\((https?[^)]+)\)', link)
    if m:
        return unquote(m.group(1))
    return url  # Awin pclick en Daisycon dl: de gewone winkel-URL uit de database


c.execute("""select o.retailer, o.affiliate_url, o.url, p.title from offers o join products p on p.id = o.product_id
             where o.is_available order by o.retailer, random()""")
gezien = {}
for winkel, link, url, titel in c.fetchall():
    if gezien.get(winkel, 0) >= 2:
        continue
    gezien[winkel] = gezien.get(winkel, 0) + 1
    adres = doel(link or '', url or '')
    try:
        r = urllib.request.urlopen(urllib.request.Request(adres, headers=KOP), timeout=30)
        status, eind = r.status, r.geturl()
        html = r.read(400000).decode('utf-8', 'ignore')
        t = re.search(r'<title>([^<]{0,120})', html)
        paginatitel = t.group(1).strip() if t else ''
    except urllib.error.HTTPError as e:
        status, eind, paginatitel = e.code, adres, ''
    except Exception as e:  # noqa: BLE001
        status, eind, paginatitel = type(e).__name__, adres, ''
    print(f'{winkel:16} {status} | ons product: {titel[:50]}')
    print(f'{"":16} pagina: {paginatitel[:90]}')
    print(f'{"":16} {eind[:120]}')
