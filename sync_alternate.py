"""Alternate.nl-sync via de TradeTracker-productfeed (campagne #904).

Bewust "offers-only", net als Expert: Alternate verkoopt vooral pc's en
elektronica, dus de feed bevat veel niet-witgoed. We maken géén nieuwe
producten aan maar koppelen Alternate-aanbiedingen op EAN aan apparaten
die al op de site staan — het EAN-matchen filtert het niet-witgoed
vanzelf weg.

De feed ("Algemeen nieuw": JSON, ~26.600 producten, elk uur ververst
door TradeTracker) bevat per product een kant-en-klare trackinglink
(URL) en prijs, maar wijkt op drie punten af van de Expert-feed:
- het EAN heet hier GTIN (13 cijfers, soms met voorloopnul zoals bij
  Amerikaanse UPC-codes -> matchen op EAN zonder voorloopnullen);
- de van-prijs heet Adviesprijs (i.p.v. fromPrice);
- er staat een derde niet-leverbaar in ('niet op voorraad'/'preorder'),
  die slaan we over zodat er geen koopknop naar een uitverkocht
  product komt. Gaat iets uit voorraad, dan ruimt de sync de
  aanbieding daarna vanzelf op.
De feed-URL bevat alleen publieke ID's (site 512985, feed 1594453) en
is dus geen geheim; overschrijfbaar via ALTERNATE_FEED_URL.
"""
import json
import logging
import os
import urllib.request

from affiliate_ref import voeg_clickref_toe
from app import create_app
from models import db, Product, Offer, SyncLog, utcnow, log_price, prijssprong_melding
from ean_match import ean_sleutel

logger = logging.getLogger(__name__)

RETAILER = 'alternate'
FEED_URL_DEFAULT = ('https://pf.tradetracker.net/?aid=512985&encoding=utf-8'
                    '&type=json&fid=1594453&categoryType=2&additionalType=2')
# Veiligheidsklep tegen halflege feeds (zelfde aanpak als de andere winkels)
MIN_FEED_RATIO = 0.5


def _eerste(waarde):
    """TradeTracker levert property-waarden als lijst: ['x'] -> 'x'."""
    if isinstance(waarde, list):
        return waarde[0] if waarde else None
    return waarde




def _feed_records(feed_url):
    """Feed downloaden en terugbrengen tot {ean-sleutel: record}."""
    req = urllib.request.Request(feed_url,
                                 headers={'User-Agent': 'witgoedaanbod-sync/1.0'})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.load(resp)

    records = {}
    for p in data.get('products', []):
        props = p.get('properties') or {}
        if _eerste(props.get('availability')) != 'op voorraad':
            continue
        ean = _eerste(props.get('GTIN'))
        prijs = (p.get('price') or {}).get('amount')
        url = p.get('URL')
        if not ean or not prijs or not url:
            continue
        van_prijs = _eerste(props.get('Adviesprijs'))
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
            'strikethrough_price': van_prijs if (van_prijs and van_prijs > float(prijs)) else None,
            'url': voeg_clickref_toe(url, 'tradetracker', ean),
            'image_url': images[0] if images else None,
            'delivery_time': levertijd,
            'delivery_cost': verzendkosten,
        }
    return records


def sync_alternate():
    """Alternate-aanbiedingen koppelen aan bestaande producten (EAN-match)."""
    app = create_app()

    with app.app_context():
        sync_log = SyncLog(started_at=utcnow())
        db.session.add(sync_log)
        db.session.commit()

        feed_url = os.getenv('ALTERNATE_FEED_URL', FEED_URL_DEFAULT)
        logger.info("[+] Alternate-feed downloaden...")
        records = _feed_records(feed_url)
        logger.info(f"[+] {len(records)} feedproducten met EAN en prijs")

        matched = updated = 0
        prijssprongen = []
        seen_product_ids = set()

        # Ook niet-leverbare producten meenemen: een apparaat dat bij de
        # andere winkels uit het assortiment is, kan via Alternate weer
        # leverbaar worden (en de pagina herstelt dan vanzelf).
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

        # Opruimen: Alternate-aanbiedingen van producten die niet meer in de
        # feed staan. Producten zelf blijven altijd bestaan (andere winkels
        # of "tijdelijk niet leverbaar").
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

        logger.info("[+] Alternate-sync klaar")
        logger.info(f"    - Nieuwe Alternate-aanbiedingen: {matched}")
        logger.info(f"    - Bijgewerkte aanbiedingen: {updated}")
        logger.info(f"    - Verlopen aanbiedingen verwijderd: {removed}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sync_alternate()
