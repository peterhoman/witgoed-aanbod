"""Hoe staan typenummers met spaties in EPREL? (alleen lezen)
Draaien: python scripts/proef_eprel_spaties.py
"""
import sys
import time
import urllib.parse

import requests

sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from eprel import _BASIS, _KOP  # noqa: E402

for groep, code in [('refrigeratingappliances2019', 'KFN 4397 CD'),
                    ('refrigeratingappliances2019', 'KFN4397CD'),
                    ('refrigeratingappliances2019', 'KFN 4397'),
                    ('refrigeratingappliances2019', 'IRBc 4120-22'),
                    ('refrigeratingappliances2019', 'IRBc 4120'),
                    ('refrigeratingappliances2019', 'IRBc4120'),
                    ('washingmachines2019', 'WWD 320 WPS'),
                    ('washingmachines2019', 'WWD320')]:
    url = f"{_BASIS}/{groep}?modelIdentifier={urllib.parse.quote(code)}&limit=5"
    r = requests.get(url, headers=_KOP, timeout=30)
    hits = r.json().get('hits', []) if r.status_code == 200 else []
    print(f'{code:15} {r.status_code} {len(hits)} treffers:', [h.get('modelIdentifier') for h in hits][:5])
    time.sleep(1)
