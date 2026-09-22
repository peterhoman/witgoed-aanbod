"""Bezoekersbron uit de koppen van een verzoek (pageviews.bezoekersbron).

Draaien: python test_bezoekersbron.py
"""
import sys
sys.path.insert(0, '.')

from pageviews import bezoekersbron

B = {'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'document'}   # gewone browser

GEVALLEN = [
    # (koppen, verwacht)
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.google.com/'}, ('google', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.google.nl/search?q=lg+rt90x8'}, ('google', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.google.co.uk/'}, ('google', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://gemini.google.com/'}, ('gemini', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'android-app://com.google.android.googlequicksearchbox/'}, ('google', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.bing.com/'}, ('bing', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://copilot.microsoft.com/'}, ('copilot', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://duckduckgo.com/'}, ('duckduckgo', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://search.yahoo.com/'}, ('yahoo', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://nl.search.yahoo.com/search?p=x'}, ('yahoo', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.ecosia.org/'}, ('ecosia', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://chatgpt.com/'}, ('chatgpt', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.perplexity.ai/'}, ('perplexity', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://claude.ai/'}, ('claude', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://you.com/'}, ('ai-overig', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.startpage.com/'}, ('zoekmachine-overig', '')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://yandex.ru/'}, ('zoekmachine-overig', '')),
    # Verwijzing van een andere site: domein erbij, zonder www.
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://www.tweakers.net/nieuws/1234/'}, ('verwijzing', 'tweakers.net')),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://radar.avrotros.nl/artikel/'}, ('verwijzing', 'radar.avrotros.nl')),
    # Binnen de site: niet tellen.
    ({**B, 'Sec-Fetch-Site': 'same-origin', 'Referer': 'https://www.witgoedaanbod.nl/category/drogers'}, None),
    ({**B, 'Sec-Fetch-Site': 'same-origin'}, None),
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'https://witgoedaanbod.nl/'}, None),
    # Direct: getypt, bladwijzer, uit een app zonder verwijzer.
    ({**B, 'Sec-Fetch-Site': 'none'}, ('direct', '')),
    # Van buiten maar de andere site stuurt geen verwijzer mee.
    ({**B, 'Sec-Fetch-Site': 'cross-site'}, ('extern-onbekend', '')),
    # Geen Sec-Fetch-koppen en geen verwijzer: vrijwel zeker een programma.
    ({}, ('zonder-secfetch', '')),
    # Oude browser zonder Sec-Fetch maar mét verwijzer: gewoon indelen.
    ({'Referer': 'https://www.google.nl/'}, ('google', '')),
    # Rommel in de Referer mag nooit een fout geven.
    ({**B, 'Sec-Fetch-Site': 'cross-site', 'Referer': 'http://[::1'}, ('extern-onbekend', '')),
]

fouten = 0
for koppen, verwacht in GEVALLEN:
    uit = bezoekersbron(koppen)
    ok = uit == verwacht
    print(('OK   ' if ok else 'FOUT ') + repr(uit) + '  <- ' + repr(koppen.get('Referer', koppen.get('Sec-Fetch-Site', '-'))))
    if not ok:
        fouten += 1
        print('   verwacht:', repr(verwacht))
print(f"\n{len(GEVALLEN)} gevallen, {fouten} fout")
sys.exit(1 if fouten else 0)
