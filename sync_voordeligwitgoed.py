"""Voordeligwitgoed.nl-sync via de TradeTracker-productfeed (campagne #2932).

Waarom deze winkel erbij komt
-----------------------------
Bij 70% van onze wasmachines toont de site maar één winkel. Op een
vergelijkingssite valt daar niets te vergelijken, en dat is vermoedelijk een
deel van de reden dat Google 918 pagina's kent maar niet de moeite waard
vindt. Elke winkel erbij is bij honderden apparaten het verschil tussen een
prijs en een vergelijking.

In de takenlijst stond wekenlang "aangevraagd, wachten op antwoord". Op
01-08 bleek in TradeTracker dat de campagne allang is geaccepteerd -- er
viel niets te wachten. Onder beoordeling stonden nul aanvragen.

Zelfde offers-only-recept als Expert, EP en Alternate: we maken geen nieuwe
producten aan maar koppelen aanbiedingen op EAN aan apparaten die al op de
site staan. Productcreatie vanuit deze winkel kan later alsnog.

Wat er nog moet gebeuren voordat dit werkt
------------------------------------------
Het feed-ID (fid) van campagne #2932 invullen, hieronder of via de
omgevingsvariabele VOORDELIGWITGOED_FEED_URL. Te vinden in TradeTracker
onder Promotiemateriaal -> Productfeeds. De feed-URL bevat alleen publieke
nummers (site 512985 en het feed-ID) en is geen geheim.

Zolang dat nummer ontbreekt slaat de sync zichzelf over met een leesbare
melding in /api/sync-status, in plaats van te struikelen over een adres dat
niet bestaat.
"""
import json
import logging
import os
import urllib.request

from affiliate_ref import voeg_clickref_toe
from app import create_app
from ean_match import ean_sleutel
from models import (Offer, Product, SyncLog, db, log_price,
                    prijssprong_melding, utcnow)

logger = logging.getLogger(__name__)

RETAILER = 'voordeligwitgoed'

# Feed "Algemeen" van campagne #2932: 434 producten, 1x per dag ververst door
# TradeTracker. Zelfde vorm als de andere TradeTracker-winkels; alleen fid
# verschilt. Bevat geen geheimen (site 512985 en feed 251845 zijn publieke
# nummers) en is overschrijfbaar via VOORDELIGWITGOED_FEED_URL.
FEED_URL_DEFAULT = ('https://pf.tradetracker.net/?aid=512985&encoding=utf-8'
                    '&type=json&fid=251845&categoryType=2'
                    '&additionalType=2')

# Veiligheidsklep tegen halflege feeds: levert een sync minder dan de helft
# van de bekende aanbiedingen op, dan gaan we niets opruimen. Anders wist één
# mislukte download in één keer alle aanbiedingen van deze winkel.
MIN_FEED_RATIO = 0.5


def _eerste(waarde):
    """TradeTracker levert property-waarden als lijst: ['x'] -> 'x'."""
    if isinstance(waarde, list):
        return waarde[0] if waarde else None
    return waarde


def _feed_records(feed_url):
    """Feed downloaden en terugbrengen tot {ean-sleutel: record}."""
    req = urllib.request.Request(
        feed_url, headers={'User-Agent': 'witgoedaanbod-sync/1.0'})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.load(resp)

    records = {}
    for p in data.get('products', []):
        props = p.get('properties') or {}
        # EAN heet bij sommige TradeTracker-winkels GTIN; pak wat er is.
        ean = _eerste(props.get('EAN')) or _eerste(props.get('GTIN'))
        prijs = (p.get('price') or {}).get('amount')
        url = p.get('URL')
        if not ean or not prijs or not url:
            continue
        van_prijs = (_eerste(props.get('fromPrice'))
                     or _eerste(props.get('Adviesprijs')))
        try:
            van_prijs = float(van_prijs) if van_prijs else None
        except (TypeError, ValueError):
            van_prijs = None
        images = p.get('images') or []
        try:
            verzendkosten = float(_eerste(props.get('deliveryCosts')))
        except (TypeError, ValueError):
            verzendkosten = None
        levertijd = (_eerste(props.get('deliveryTime')) or '').strip()[:120] or None
        records[ean_sleutel(ean)] = {
            'price': float(prijs),
            'strikethrough_price': (van_prijs
                                    if (van_prijs and van_prijs > float(prijs))
                                    else None),
            'url': voeg_clickref_toe(url, 'tradetracker', ean),
            'image_url': images[0] if images else None,
            'delivery_time': levertijd,
            'delivery_cost': verzendkosten,
        }
    return records


def sync_voordeligwitgoed():
    """Voordeligwitgoed-aanbiedingen koppelen aan bestaande producten."""
    app = create_app()

    with app.app_context():
        sync_log = SyncLog(started_at=utcnow())
        db.session.add(sync_log)
        db.session.commit()

        feed_url = os.getenv('VOORDELIGWITGOED_FEED_URL', FEED_URL_DEFAULT)
        if 'FEEDID_INVULLEN' in feed_url:
            logger.error("[!] Voordeligwitgoed-feed-ID nog niet ingevuld "
                         "(FEED_URL_DEFAULT of VOORDELIGWITGOED_FEED_URL) - "
                         "sync overgeslagen")
            sync_log.finished_at = utcnow()
            sync_log.errors = ('Voordeligwitgoed-feed-ID ontbreekt; te vinden '
                               'in TradeTracker onder Promotiemateriaal > '
                               'Productfeeds (campagne #2932)')
            db.session.commit()
            return

        logger.info("[+] Voordeligwitgoed-feed downloaden...")
        records = _feed_records(feed_url)
        logger.info(f"[+] {len(records)} feedproducten met EAN en prijs")

        matched = updated = 0
        prijssprongen = []
        seen_product_ids = set()

        # Ook niet-leverbare producten meenemen: een apparaat dat bij de
        # andere winkels uit het assortiment is, kan hier weer leverbaar
        # worden (en de pagina herstelt dan vanzelf).
        for product in Product.query.filter_by(is_example=False).all():
            record = records.get(ean_sleutel(product.ean))
            if record is None:
                continue
            offer = Offer.query.filter_by(product_id=product.id,
                                          retailer=RETAILER).first()
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
            offer.url = record['url']
            offer.affiliate_url = record['url']  # feed-URL ís de trackinglink
            offer.delivery_time = record['delivery_time']
            offer.delivery_cost = record['delivery_cost']
            offer.is_available = True
            offer.last_synced = utcnow()
            # Product-identiteit laten we met rust, behalve een ontbrekende
            # foto: die vullen we aan (kapotte afbeelding op de site).
            if not product.image_url and record['image_url']:
                product.image_url = record['image_url']
            log_price(product.id, RETAILER, record['price'])
            product.refresh_pricing()
            seen_product_ids.add(product.id)

        db.session.commit()

        removed = 0
        bestaand = Offer.query.filter_by(retailer=RETAILER).count()
        if bestaand and len(seen_product_ids) < bestaand * MIN_FEED_RATIO:
            logger.error(f"[!] Feed leverde maar {len(seen_product_ids)} van de "
                         f"{bestaand} bekende aanbiedingen; opruimen overgeslagen.")
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

        # Vangnet: producten zonder foto -> Icecat proberen.
        from icecat import controleer_bestaande_fotos, vul_ontbrekende_fotos
        controleer_bestaande_fotos(db, Product)
        vul_ontbrekende_fotos(db, Product)

        # Prijsalerts checken tegen de zojuist bijgewerkte prijzen.
        from price_alerts import check_price_alerts
        check_price_alerts()

        if prijssprongen:
            sync_log.errors = ('Prijssprong >50% (feed checken): '
                               + '; '.join(prijssprongen[:15]))[:2000]
        sync_log.finished_at = utcnow()
        sync_log.products_synced = matched
        sync_log.products_updated = updated
        sync_log.products_hidden = removed
        db.session.commit()

        logger.info("[+] Voordeligwitgoed-sync klaar")
        logger.info(f"    - Nieuwe aanbiedingen: {matched}")
        logger.info(f"    - Bijgewerkte aanbiedingen: {updated}")
        logger.info(f"    - Verlopen aanbiedingen verwijderd: {removed}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sync_voordeligwitgoed()
