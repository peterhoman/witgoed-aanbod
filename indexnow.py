"""IndexNow: Bing (en Yandex, Naver, Seznam) dagelijks vertellen welke
pagina's veranderd zijn, zodat ze die snel opnieuw ophalen.

Gebouwd 22 september 2026 op verzoek van het linkplan. Google doet niet mee
aan IndexNow; voor Google blijft de sitemap met eerlijke <lastmod> het
instrument. Bing en DuckDuckGo zijn samen zo'n 6% van de Nederlandse
zoekmarkt en pakken kleine sites hiermee sneller op.

Hoe het werkt
- Sleutel: config.INDEXNOW_KEY. Bing controleert het eigendom door
  /indexnow-<sleutel>.txt op te halen (route in routes/seo.py); dat bestand
  bevat alleen de sleutel. Geen geheim: het is een openbaar bestand.
- Eén keer per dag (planner, 07:30 UTC, na de ochtendsyncs) worden alle
  sitemap-adressen verzameld waarvan de sitemapdatum gisteren of vandaag is.
  Dat is dezelfde datumlogica als de sitemap zelf (routes/seo.py: nieuw
  prijspunt, nieuwe winkel, weer leverbaar), dus we melden alleen wat echt
  veranderd is. De soort 'overig' (homepage, juridische pagina's) blijft
  buiten beschouwing: die krijgt in de sitemap altijd de datum van vandaag.
- Verstuurd als JSON-POST naar api.indexnow.org, hooguit 10.000 adressen per
  bericht. Antwoord 200 of 202 = ontvangen; 403 = sleutel klopt niet (dan is
  het sleutelbestand niet bereikbaar); 422 = adres hoort niet bij deze host;
  429 = te veel berichten.
- De uitkomst van de laatste ronde staat op /api/sync-status onder 'indexnow'.
"""
import logging
from datetime import date, datetime, timedelta, timezone

logger = logging.getLogger(__name__)

EINDPUNT = 'https://api.indexnow.org/IndexNow'
MAX_PER_BERICHT = 10000
NIET_MELDEN = ('overig',)

# Uitkomst van de laatste ronde, voor de meetpagina. Leeft in het geheugen van
# het proces; na een herstart staat hier weer 'nog niet gedraaid'.
_laatste = {'wanneer': None, 'adressen': 0, 'berichten': [], 'fout': None}


def sleutelbestand(sleutel):
    """Pad van het sleutelbestand op de eigen site."""
    return f'/indexnow-{sleutel}.txt'


def gewijzigde_adressen(per_soort, sinds):
    """Sitemap-adressen met een datum op of na `sinds` (een date), zonder
    dubbelen, gesorteerd. `per_soort` is de uitkomst van routes.seo._bouw_entries."""
    grens = sinds.strftime('%Y-%m-%d')
    adressen = set()
    for soort, entries in per_soort.items():
        if soort in NIET_MELDEN:
            continue
        for e in entries:
            if (e.get('lastmod') or '') >= grens and e.get('loc'):
                adressen.add(e['loc'])
    return sorted(adressen)


def berichten(adressen, per_bericht=MAX_PER_BERICHT):
    """Adressen in stukken van hooguit `per_bericht`."""
    return [adressen[i:i + per_bericht] for i in range(0, len(adressen), per_bericht)]


def _post(body):
    import requests
    antwoord = requests.post(EINDPUNT, json=body, timeout=30,
                             headers={'Content-Type': 'application/json; charset=utf-8'})
    return antwoord.status_code


def verstuur(adressen, host, sleutel, sleutel_adres, poster=None):
    """Meldt de adressen; geeft [(aantal, statuscode)] per bericht terug.
    `poster` is inwisselbaar voor de test."""
    poster = poster or _post
    uit = []
    for stuk in berichten(adressen):
        body = {'host': host, 'key': sleutel, 'keyLocation': sleutel_adres, 'urlList': stuk}
        uit.append((len(stuk), poster(body)))
    return uit


def meld_gewijzigde_adressen(app):
    """Plannertaak: verzamel wat gisteren of vandaag veranderde en meld het."""
    with app.app_context():
        from routes.seo import _bouw_entries
        site = app.config['SITE_URL']
        sleutel = app.config.get('INDEXNOW_KEY')
        host = site.split('://', 1)[-1].rstrip('/')
        nu = datetime.now(timezone.utc).replace(tzinfo=None)
        _laatste.update({'wanneer': nu.isoformat(timespec='seconds'), 'adressen': 0,
                         'berichten': [], 'fout': None})
        if not sleutel:
            _laatste['fout'] = 'INDEXNOW_KEY ontbreekt'
            logger.warning('indexnow: geen sleutel, niets gemeld')
            return
        try:
            adressen = gewijzigde_adressen(_bouw_entries(), date.today() - timedelta(days=1))
            _laatste['adressen'] = len(adressen)
            if not adressen:
                logger.info('indexnow: geen gewijzigde adressen, niets gemeld')
                return
            uitkomsten = verstuur(adressen, host, sleutel, f"{site}{sleutelbestand(sleutel)}")
            _laatste['berichten'] = [{'adressen': n, 'status': s} for n, s in uitkomsten]
            logger.info('indexnow: %d adressen gemeld in %d bericht(en): %s',
                        len(adressen), len(uitkomsten), [s for _, s in uitkomsten])
        except Exception as e:  # een mislukte melding mag de planner niet raken
            _laatste['fout'] = str(e)[:200]
            logger.warning('indexnow: melden mislukt: %s', e)


def status():
    """Voor /api/sync-status."""
    return dict(_laatste)
