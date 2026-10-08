"""Linkcontrole 8 okt (vraag SEO-chat): per winkel naar welk netwerk de
doorklik gaat, of de publisher-/site-ID's erin zitten, hoeveel leverbare
aanbiedingen geen tracking hebben, twee steekproeven per winkel (doel-URL
uit de trackinglink gehaald, niet aangeklikt), en de doorklikteller van de
laatste 30 dagen. Alleen lezen; er gaat geen enkel verzoek naar een
affiliate-netwerk.
Draaien: railway run -s Postgres python scripts/meting_linkcontrole.py
"""
import collections
import os
import re
import sys
from urllib.parse import parse_qsl, unquote, urlsplit

import psycopg2

sys.stdout.reconfigure(encoding='utf-8')
c = psycopg2.connect(os.environ['DATABASE_PUBLIC_URL']).cursor()

ID_CONTROLE = {
    'awin1.com': ('awin', r'awinaffid=2969655'),
    'tradedoubler.com': ('tradedoubler', r'(a=|a\()3490179'),
    'ds1.nl': ('daisycon', r'si=428244|li=|wi=428244'),
    'tradetracker': ('tradetracker', r'512985|336332'),
    'tt=': ('tradetracker-direct', r'_512985_'),
    'partner.bol.com': ('bol-partner', r'[?&]s=\d+'),
    'bit.ly': ('bitly (bol)', r'.'),
}


def netwerk_van(link):
    for teken, (naam, patroon) in ID_CONTROLE.items():
        if teken in link:
            return naam, bool(re.search(patroon, link))
    return 'GEEN TRACKING (kale winkel-URL)', False


def doel_uit(link):
    """De winkel-URL uit een trackinglink halen, zonder hem op te vragen."""
    q = dict(parse_qsl(urlsplit(link).query, keep_blank_values=True))
    for sleutel in ('ued', 'url', 'dl', 'r', 'u'):
        if q.get(sleutel, '').startswith('http'):
            return unquote(q[sleutel])
    m = re.search(r'url\((https?[^)]+)\)', link)
    if m:
        return unquote(m.group(1))
    return '(doel niet uit de link te halen)'


c.execute("""select retailer, id, coalesce(nullif(affiliate_url,''), url), url, product_id
             from offers where is_available order by retailer, id""")
per_winkel = collections.defaultdict(list)
for winkel, oid, link, url, pid in c.fetchall():
    per_winkel[winkel].append((oid, link or '', url or '', pid))

for winkel, rijen in sorted(per_winkel.items()):
    soorten = collections.Counter()
    zonder_id = 0
    for oid, link, url, pid in rijen:
        naam, id_ok = netwerk_van(link)
        soorten[naam] += 1
        zonder_id += (not id_ok)
    print(f'\n== {winkel}: {len(rijen)} leverbaar | netwerk: {dict(soorten)} | zonder juist ID: {zonder_id}')
    for oid, link, url, pid in (rijen[:1] + rijen[len(rijen) // 2:len(rijen) // 2 + 1]):
        print(f'   steekproef aanbieding {oid}:')
        print(f'     link : {link[:230]}')
        print(f'     doel : {doel_uit(link)[:160]}')
        print(f'     winkel-url in db: {url[:160]}')

# Bol-terugvalknop: producten zonder aanbieding gebruiken products.affiliate_url.
c.execute("""select count(*), count(*) filter (where affiliate_url is null or affiliate_url = '')
             from products where is_available""")
print('\nproducten leverbaar / zonder products.affiliate_url:', c.fetchone())

c.execute("""select datum, soort, aantal from page_views
             where datum >= current_date - 30 and (soort like 'uit-%%' or soort like 'klik-%%')
             order by datum""")
dag = collections.defaultdict(dict)
for datum, soort, aantal in c.fetchall():
    dag[datum][soort] = aantal
totaal = collections.Counter()
print('\n== per dag: uit-* (echte doorkliks met kaartje) | klik-browser | klik-zonder-kaartje | overige klik-*')
for datum in sorted(dag):
    d = dag[datum]
    uit = {k[4:]: v for k, v in d.items() if k.startswith('uit-')}
    totaal.update(uit)
    rest = {k: v for k, v in d.items() if k.startswith('klik-') and k not in ('klik-browser', 'klik-zonder-kaartje')}
    print(f'  {datum} uit {sum(uit.values()):4} {uit} | browser {d.get("klik-browser", 0)} | '
          f'zonder kaartje {d.get("klik-zonder-kaartje", 0)} | {rest}')
print('\n30 dagen uit-* per winkel:', dict(totaal), 'totaal', sum(totaal.values()))
