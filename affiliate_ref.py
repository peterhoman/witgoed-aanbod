"""Eigen kenmerk (clickref) aan affiliate-links toevoegen.

Aanleiding: de eerste Coolblue-verkoop (15-07, €19,90 commissie) was in
Awin niet te herleiden tot een product — de Click ref-kolom was leeg.
Elk netwerk heeft een eigen parameternaam voor zo'n kenmerk; wij sturen
het EAN mee, zodat elke transactie in het netwerk-dashboard direct laat
zien welk product op de site de klik startte.

- Awin (Coolblue): &clickref=EAN op awin1.com-deeplinks.
- TradeTracker (Expert): &r=EAN op tc.tradetracker.net-links (bestaand
  leeg r= wordt gevuld, anders toegevoegd).
- Tradedoubler (MediaMarkt): &epi=EAN op click?p=-links; bij de
  matrix-notatie (click?a(..)p(..)) wordt epi(EAN) ingevoegd.

Onbekend linkformaat -> URL ongewijzigd terug (liever geen kenmerk dan
een kapotte link).
"""
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


def _zet_query_param(url, naam, waarde):
    delen = urlsplit(url)
    params = dict(parse_qsl(delen.query, keep_blank_values=True))
    params[naam] = waarde
    return urlunsplit(delen._replace(query=urlencode(params)))


def voeg_clickref_toe(url, netwerk, ean):
    if not url or not ean:
        return url
    try:
        if netwerk == 'awin' and 'awin1.com' in url:
            return _zet_query_param(url, 'clickref', str(ean))
        if netwerk == 'tradetracker' and 'tradetracker' in url:
            return _zet_query_param(url, 'r', str(ean))
        if netwerk == 'tradedoubler' and 'tradedoubler.com' in url:
            if 'click?p=' in url or 'click?a=' in url:
                return _zet_query_param(url, 'epi', str(ean))
            if 'click?' in url and '(' in url:
                # Matrix-notatie: click?a(x)p(y)... -> epi(EAN) invoegen
                return url.replace('click?', f'click?epi({ean})', 1)
    except Exception:
        pass
    return url
