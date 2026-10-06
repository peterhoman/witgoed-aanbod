"""Controle: geeft de Witgoedhuis-feed (Daisycon) weer antwoord? Alleen lezen,
alleen de eerste pagina. Draaien: python scripts/controle_witgoedhuis_feed.py
"""
import sys
import urllib.error
import urllib.request

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from sync_witgoedhuis import FEED_URL_DEFAULT  # noqa: E402

try:
    r = urllib.request.urlopen(urllib.request.Request(FEED_URL_DEFAULT, headers={'User-Agent': 'Mozilla/5.0'}),
                               timeout=120)
    inhoud = r.read()
    print('status', r.status, '| bytes', len(inhoud), '| producten op pagina 1:', inhoud.count(b'<product>'))
except urllib.error.HTTPError as e:
    print('status', e.code, e.reason)
except Exception as e:  # noqa: BLE001
    print('fout', type(e).__name__, e)
