"""Witgoedhuis.nl-sync via de Daisycon-productfeed (programma 6570, media 428244).

Waarom deze winkel erbij komt (6 oktober 2026)
----------------------------------------------
Peters besluit van 5 oktober: ook als Witgoedhuis zelden de goedkoopste is,
geeft een extra winkel in de vergelijking de bezoeker vertrouwen dat de
laagste prijs echt de laagste is; bij één of twee winkels zoekt hij verder.
Gemeten op 5 oktober: 714 producten in de feed, 123 gedeeld op EAN, waarvan
30 bij ons nog maar één winkel hadden. Steekproef 15 van 15: prijs en
voorraad klopten met witgoedhuis.nl. De feed werd tot 1 oktober wekenlang
niet ververst; vanaf 5 en 6 oktober wel weer dagelijks. Bevriest hij
opnieuw, dan haalt verouderde_aanbiedingen.py de aanbiedingen na drie dagen
vanzelf van de site.

Zelfde offers-only-recept als Voordeligwitgoed: geen nieuwe producten,
alleen aanbiedingen op EAN koppelen aan apparaten die al op de site staan.
Alleen nieuwe apparaten (condition = new): Witgoedhuis verkoopt geen
tweedehands, maar het veld bestaat, dus we controleren het.

Feed: XML, per pagina 100 producten, volgende pagina in de kop X-Next-Url.
Geen API-sleutel: het media-ID in het adres is de sleutel. De link in de
feed is de Daisycon-trackinglink (ds1.nl); het gewone winkeladres staat in
de parameter dl.
"""
import logging
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from affiliate_ref import voeg_clickref_toe
from app import create_app
from ean_match import ean_sleutel
from models import (Offer, Product, SyncLog, db, log_price,
                    prijssprong_melding, utcnow)

logger = logging.getLogger(__name__)

RETAILER = 'witgoedhuis'

FEED_URL_DEFAULT = ('https://daisycon.io/datafeed/?media_id=428244&program_id=6570'
                    '&standard_id=6&language_code=nl&locale_id=1&type=xml&records=100')

# Veiligheidsklep tegen halflege feeds, zelfde als bij de andere winkels.
MIN_FEED_RATIO = 0.5
MAX_PAGINAS = 50  # 100 per pagina; de feed telt er rond de 700


def _veld(info, naam):
    e = info.find(naam)
    return (e.text or '').strip() if e is not None and e.text else ''


def _getal(tekst):
    try:
        return float(tekst)
    except (TypeError, ValueError):
        return None


def _winkeladres(link):
    """Gewoon witgoedhuis.nl-adres uit de parameter dl van de Daisycon-link."""
    dl = urllib.parse.parse_qs(urllib.parse.urlparse(link).query).get('dl', [''])[0]
    if not dl:
        return None
    return dl if dl.startswith('http') else 'https://www.witgoedhuis.nl/' + dl.lstrip('/')


def _record(info):
    """Eén feedproduct -> record, of None als het niet bruikbaar is."""
    ean = _veld(info, 'ean')
    prijs = _getal(_veld(info, 'price'))
    link = _veld(info, 'link')
    if not ean or not prijs or not link:
        return None
    if _veld(info, 'condition') not in ('', 'new'):
        return None
    if _veld(info, 'in_stock').lower() != 'true':
        return None
    oud = _getal(_veld(info, 'price_old'))
    foto = None
    for e in info.iter('location'):
        if e.text:
            foto = e.text.strip()
            break
    return ean_sleutel(ean), {
        'price': prijs,
        'strikethrough_price': oud if (oud and oud > prijs) else None,
        'url': _winkeladres(link),
        'affiliate_url': voeg_clickref_toe(link, 'daisycon', ean),
        'image_url': foto,
        'delivery_cost': _getal(_veld(info, 'price_shipping')),
    }


def _feed_records(feed_url):
    """Alle feedpagina's ophalen en terugbrengen tot {ean-sleutel: record}."""
    records, url, paginas = {}, feed_url, 0
    while url and paginas < MAX_PAGINAS:
        req = urllib.request.Request(url, headers={'User-Agent': 'witgoedaanbod-sync/1.0'})
        with urllib.request.urlopen(req, timeout=180) as resp:
            volgende = resp.headers.get('X-Next-Url')
            boom = ET.fromstring(resp.read())
        for product in boom.iter('product'):
            info = product.find('product_info')
            if info is None:
                continue
            uitkomst = _record(info)
            if uitkomst:
                records[uitkomst[0]] = uitkomst[1]
        url, paginas = volgende, paginas + 1
        time.sleep(0.5)
    return records


def sync_witgoedhuis():
    """Witgoedhuis-aanbiedingen koppelen aan bestaande producten."""
    app = create_app()

    with app.app_context():
        sync_log = SyncLog(started_at=utcnow())
        db.session.add(sync_log)
        db.session.commit()

        logger.info("[+] Witgoedhuis-feed downloaden...")
        records = _feed_records(os.getenv('WITGOEDHUIS_FEED_URL', FEED_URL_DEFAULT))
        logger.info(f"[+] {len(records)} feedproducten met EAN, prijs en voorraad")

        matched = updated = 0
        prijssprongen = []
        seen_product_ids = set()

        for product in Product.query.filter_by(is_example=False).all():
            record = records.get(ean_sleutel(product.ean))
            if record is None:
                continue
            offer = Offer.query.filter_by(product_id=product.id, retailer=RETAILER).first()
            if not offer:
                offer = Offer(product_id=product.id, retailer=RETAILER)
                db.session.add(offer)
                matched += 1
            else:
                sprong = prijssprong_melding(offer.price, record['price'])
                if sprong:
                    prijssprongen.append(f"{product.ean}: {sprong}")
                updated += 1
            offer.price = record['price']
            offer.strikethrough_price = record['strikethrough_price']
            offer.url = record['url'] or record['affiliate_url']
            offer.affiliate_url = record['affiliate_url']
            offer.delivery_time = None  # staat niet in de feed
            offer.delivery_cost = record['delivery_cost']
            offer.is_available = True
            offer.last_synced = utcnow()
            if not product.image_url and record['image_url']:
                product.image_url = record['image_url']
            log_price(product.id, RETAILER, record['price'])
            product.refresh_pricing()
            seen_product_ids.add(product.id)

        db.session.commit()

        removed = 0
        bestaand = Offer.query.filter_by(retailer=RETAILER).count()
        if bestaand and len(seen_product_ids) < bestaand * MIN_FEED_RATIO:
            melding = (f"Feed leverde maar {len(seen_product_ids)} van de "
                       f"{bestaand} bekende aanbiedingen; opruimen overgeslagen")
            logger.error(f"[!] {melding}.")
            sync_log.errors = melding
        else:
            stale = Offer.query.filter(
                Offer.retailer == RETAILER,
                ~Offer.product_id.in_(seen_product_ids) if seen_product_ids else True,
            ).all()
            for offer in stale:
                product = offer.product
                db.session.delete(offer)
                removed += 1
                if product is not None:
                    db.session.flush()
                    product.refresh_pricing()
            db.session.commit()

        from price_alerts import check_price_alerts
        check_price_alerts()

        if prijssprongen:
            sync_log.errors = (((sync_log.errors + ' | ') if sync_log.errors else '')
                               + 'Prijssprong >50% (feed checken): '
                               + '; '.join(prijssprongen[:15]))[:2000]
        sync_log.finished_at = utcnow()
        sync_log.products_synced = matched
        sync_log.products_updated = updated
        sync_log.products_hidden = removed
        db.session.commit()

        logger.info("[+] Witgoedhuis-sync klaar")
        logger.info(f"    - Nieuwe aanbiedingen: {matched}")
        logger.info(f"    - Bijgewerkte aanbiedingen: {updated}")
        logger.info(f"    - Verlopen aanbiedingen verwijderd: {removed}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sync_witgoedhuis()
