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
    # Standaardplek volgens de documentatie: /<sleutel>.txt in de root. De
    # oude naam /indexnow-<sleutel>.txt blijft ook bestaan (routes/seo.py).
    return f'/{sleutel}.txt'


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
        try:
            if not sleutel:
                _laatste['fout'] = 'INDEXNOW_KEY ontbreekt'
                logger.warning('indexnow: geen sleutel, niets gemeld')
                return
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
        finally:
            _bewaar()


def meld_verhuisde_adressen(adressen, site, sleutel):
    """Meld oude en nieuwe adressen na een adresopschoning en bewaar de uitkomst.

    Tot 4 oktober 2026 werd deze melding (catalogus_uitzonderingen) verstuurd
    zonder dat het antwoord van Bing ergens bleef; of de 462 verhuizingen van
    3 oktober zijn aangekomen, was daardoor niet na te gaan. Nu komt de
    uitkomst als ronde met soort 'adresopschoning' in indexnow_rondes, naast
    de dagelijkse. Geeft [(aantal, statuscode)] terug; gooit niets.
    """
    uitkomst = {'adressen': len(adressen), 'berichten': [], 'fout': None}
    try:
        host = site.split('://', 1)[-1].rstrip('/')
        stukken = verstuur(adressen, host, sleutel, f"{site}{sleutelbestand(sleutel)}")
        uitkomst['berichten'] = [{'adressen': n, 'status': s} for n, s in stukken]
        logger.info('indexnow: %d verhuisde adressen gemeld: %s',
                    len(adressen), [s for _, s in stukken])
    except Exception as e:
        uitkomst['fout'] = str(e)[:200]
        logger.warning('indexnow: verhuisde adressen melden mislukt: %s', e)
    _bewaar(uitkomst, soort='adresopschoning')
    return uitkomst


def _bewaar(uitkomst=None, soort='dagelijks'):
    """Schrijf de uitkomst van deze ronde weg (models.IndexNowRonde) en houd
    de laatste dertig. Mislukt het bewaren, dan blijft de ronde zelf geslaagd.
    Zonder `uitkomst`: de dagelijkse ronde uit _laatste."""
    uitkomst = uitkomst or _laatste
    try:
        from models import db, IndexNowRonde
        db.session.add(IndexNowRonde(
            adressen=uitkomst['adressen'],
            statussen=','.join(str(b['status']) for b in uitkomst['berichten'])[:200],
            fout=uitkomst['fout'], soort=soort))
        db.session.commit()
        oud = IndexNowRonde.query.order_by(IndexNowRonde.wanneer.desc()).offset(30).all()
        for rij in oud:
            db.session.delete(rij)
        if oud:
            db.session.commit()
    except Exception as e:
        logger.warning('indexnow: uitkomst bewaren mislukt: %s', e)


def status():
    """Voor /api/sync-status: de laatste ronde uit de database (blijft staan
    na een uitrol), anders wat dit proces nog in het geheugen heeft."""
    try:
        from models import IndexNowRonde
        rijen = IndexNowRonde.query.order_by(IndexNowRonde.wanneer.desc()).limit(7).all()
        if rijen:
            r = rijen[0]
            return {
                'wanneer': r.wanneer.isoformat(timespec='seconds'),
                'adressen': r.adressen,
                'berichten': [{'status': int(s)} for s in r.statussen.split(',') if s.strip().isdigit()],
                'fout': r.fout,
                'soort': r.soort or 'dagelijks',
                'laatste_rondes': [{'wanneer': x.wanneer.isoformat(timespec='seconds'),
                                    'soort': x.soort or 'dagelijks',
                                    'adressen': x.adressen, 'statussen': x.statussen,
                                    'fout': x.fout} for x in rijen],
            }
    except Exception:
        pass
    return dict(_laatste)
