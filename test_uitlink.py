"""Kaartje voor de doorklik (uitlink.py) en de route die het controleert.

Draaien: python test_uitlink.py
"""
import sys
sys.path.insert(0, '.')

from uitlink import kaartje_geldig, maak_kaartje

fouten = 0
def check(naam, ok):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam)
    fouten += (not ok)

S = 'geheim'
nu = 1_790_000_000
k = maak_kaartje(S, 'a', 123, nu=nu)
check('vers kaartje geldig', kaartje_geldig(k, S, 'a', 123, nu=nu + 60))
check('na 11 uur nog geldig', kaartje_geldig(k, S, 'a', 123, nu=nu + 11 * 3600))
check('na 13 uur verlopen', not kaartje_geldig(k, S, 'a', 123, nu=nu + 13 * 3600))
check('andere aanbieding ongeldig', not kaartje_geldig(k, S, 'a', 124, nu=nu))
check('andere soort ongeldig', not kaartje_geldig(k, S, 'p', 123, nu=nu))
check('andere sleutel ongeldig', not kaartje_geldig(k, 'anders', 'a', 123, nu=nu))
check('geen kaartje ongeldig', not kaartje_geldig(None, S, 'a', 123, nu=nu))
check('rommel ongeldig', not kaartje_geldig('abc', S, 'a', 123, nu=nu)
      and not kaartje_geldig('x.y', S, 'a', 123, nu=nu))
check('tijdstempel uit de toekomst ongeldig', not kaartje_geldig(
    maak_kaartje(S, 'a', 123, nu=nu + 3600), S, 'a', 123, nu=nu))
check('vervalste tijdstempel ongeldig', not kaartje_geldig(
    f"{nu + 100}.{k.split('.')[1]}", S, 'a', 123, nu=nu + 100))


# De route zelf, tegen de lokale demodatabase.
import re
from app import create_app
app = create_app()
c = app.test_client()
B = {'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Site': 'same-origin',
     'User-Agent': 'Mozilla/5.0 (test)'}
h = c.get('/category/wasmachines').get_data(as_text=True)
product_url = re.findall(r'href="(/product/[^"]+)"', h)[0]
pagina = c.get(product_url).get_data(as_text=True)
links = re.findall(r'href="(/uit/aanbieding/\d+\?k=[^"]+)"', pagina)
check('productpagina geeft winkelknoppen met kaartje', bool(links))
if links:
    link = links[0].replace('&amp;', '&')
    kaal = link.split('?')[0]
    r = c.get(link, headers=B)
    check('met kaartje: doorgestuurd naar de winkel', r.status_code == 302
          and '/product/' not in r.headers['Location'])
    r = c.get(kaal, headers=B)
    check('zonder kaartje: terug naar de productpagina', r.status_code == 302
          and '/product/' in r.headers['Location'])
    r = c.get(kaal + '?k=1.abc', headers=B)
    check('vals kaartje: terug naar de productpagina', r.status_code == 302
          and '/product/' in r.headers['Location'])
    # 5 okt 2026: elke klik met een geldig kaartje krijgt de link mét
    # vergoeding (offer.link), welk Railway-knooppunt er ook in de kop staat.
    from models import Offer
    with app.app_context():
        aanbieding = Offer.query.get(int(re.search(r'/uit/aanbieding/(\d+)', link).group(1)))
        vergoedingslink = aanbieding.link
    for knooppunt in (None, 'ams1', 'us-west2', 'europe-west4-drams3a'):
        koppen = dict(B, **({'X-Railway-Edge': knooppunt} if knooppunt else {}))
        r = c.get(link, headers=koppen)
        check(f'met kaartje via {knooppunt or "geen kop"}: link met vergoeding',
              r.status_code == 302 and r.headers['Location'] == vergoedingslink)
    r = c.get(link, headers={'User-Agent': 'python-requests/2'})
    check('robot blijft 403', r.status_code == 403)

print(f"\n{fouten} fout")
sys.exit(1 if fouten else 0)
