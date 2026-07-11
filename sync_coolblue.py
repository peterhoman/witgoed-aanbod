"""
Coolblue productfeed sync (via Awin)

Haalt de Coolblue-prijsvergelijkersfeed op (Awin Create-a-Feed), filtert het
witgoed eruit en zet per apparaat een Coolblue-aanbieding (Offer) in de
database. Bestaat het apparaat al door de Bol- of MediaMarkt-sync, dan wordt
het via de EAN-streepjescode aan datzelfde product gekoppeld; anders komt er
een nieuw product bij met Coolblue als enige aanbieder.

De affiliate-link hoeven we niet zelf op te bouwen: de feed levert per product
een kant-en-klare Awin-deeplink (aw_deep_link) met onze publisher-ID erin.
"""

import csv
import gzip
import io
import os
import re
import requests
from app import create_app
from models import db, Product, Category, Offer, SyncLog, utcnow
from sync_products import EXCLUDE_KEYWORDS, MIN_PRICES, guess_brand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RETAILER = 'coolblue'

# Feed 95930: "Alle producten pricecomparison/prijsvergelijkers publishers".
# Speciaal door Coolblue samengesteld voor prijsvergelijkers, met EAN-kolom
# (de gewone full feed heeft alleen 'upc'). ~16.000 producten, hele winkel.
FEED_ID = 95930

# Alleen de kolommen die we echt gebruiken; scheelt downloadgrootte.
FEED_COLUMNS = [
    'ean', 'product_name', 'brand_name', 'description', 'merchant_image_url',
    'aw_deep_link', 'merchant_deep_link', 'search_price', 'base_price',
    'product_type', 'delivery_time', 'condition',
]

# Levert een sync minder dan dit deel van de bekende aanbiedingen op, dan gaan
# we ervan uit dat de feed hapert en ruimen we niets op (zelfde veiligheidsklep
# als de MediaMarkt-sync).
MIN_FEED_RATIO = 0.5

# Coolblue's product_type is netjes gevuld en fijnmazig: accessoires (filters,
# stofzuigerzakken, ontkalkers) hebben hun eigen type en vallen er vanzelf
# buiten. Alles wat hier niet in staat, slaan we over.
PRODUCT_TYPE_MAP = {
    'wasmachines': 'wasmachines',
    'wasdrogers': 'drogers',
    'was-droogcombinaties': 'wasdroogcombinaties',
    'koelkasten': 'koelkasten',
    'vriezers': 'koelkasten',
    'wijnklimaatkasten': 'koelkasten',
    'vaatwassers': 'vaatwassers',
    'magnetrons': 'magnetrons',
    'ovens': 'ovens',
    'stofzuigers': 'stofzuigers',
    'robotstofzuigers': 'stofzuigers',
    'volautomatische espressomachines': 'koffiemachines',
    'halfautomatische espressomachines': 'koffiemachines',
    'filterkoffieapparaten': 'koffiemachines',
    'cup- en padmachines': 'koffiemachines',
    'fornuizen': 'fornuizen',
    'kookplaten': 'kookplaten',
    'afzuigkappen': 'afzuigkappen',
}

# 'friteuses' omvat zowel airfryers (horen bij Ovens & Airfryers) als klassieke
# oliefriteuses (verkopen we niet); de titel maakt het onderscheid.
AIRFRYER_PATTERN = re.compile(r'airfryer|hetelucht', re.IGNORECASE)


def classify(product_type, title):
    """Bepaal in welke categorie van de site dit apparaat hoort, of None."""
    slug = PRODUCT_TYPE_MAP.get(product_type)
    if slug:
        return slug
    if product_type == 'friteuses' and AIRFRYER_PATTERN.search(title):
        return 'ovens'
    return None


def _parse_price(value):
    """'601' of '487.99' -> 601.0 / 487.99; onbruikbaar -> None."""
    if not value:
        return None
    try:
        return float(str(value).replace(',', '.'))
    except ValueError:
        return None


def feed_url(apikey):
    columns = '%2C'.join(FEED_COLUMNS)
    return (
        f"https://productdata.awin.com/datafeed/download/apikey/{apikey}"
        f"/fid/{FEED_ID}/format/csv/language/nl/delimiter/%2C"
        f"/compression/gzip/columns/{columns}/"
    )


def fetch_feed(apikey):
    """Feed downloaden (gzip-CSV, ~4 MB) en als lijst dicts teruggeven."""
    response = requests.get(feed_url(apikey), timeout=300)
    response.raise_for_status()
    text = gzip.decompress(response.content).decode('utf-8')
    return list(csv.DictReader(io.StringIO(text)))


def normalize(row):
    """Zet een feedregel om in het handjevol velden dat wij nodig hebben."""
    ean = (row.get('ean') or '').strip()
    title = (row.get('product_name') or '').strip()
    if not ean or not title:
        return None

    # De prijsvergelijkersfeed hoort alleen nieuwe producten te bevatten;
    # refurbished zit in aparte feeds. Extra slot op de deur.
    if (row.get('condition') or 'new').strip().lower() not in ('new', ''):
        return None

    price = _parse_price(row.get('search_price'))
    if not price or price <= 0:
        return None

    # base_price is Coolblue's adviesprijs; alleen tonen bij echte korting
    # (zelfde regel als bij de Bol- en MediaMarkt-sync).
    advies = _parse_price(row.get('base_price'))

    # Vrijwel alles in de feed is per direct leverbaar ("morgen in huis");
    # alleen pre-orders en downloads niet.
    delivery = (row.get('delivery_time') or '').strip().lower()
    is_available = delivery not in ('pre-order', 'download')

    return {
        'ean': ean,
        'title': title,
        'brand': (row.get('brand_name') or '').strip() or None,
        'description': row.get('description'),
        'image_url': row.get('merchant_image_url') or '',
        'product_type': (row.get('product_type') or '').strip().lower(),
        'price': price,
        'strikethrough_price': advies if advies and advies > price else None,
        'affiliate_url': row.get('aw_deep_link'),
        'url': row.get('merchant_deep_link'),
        'is_available': is_available,
    }


def sync_coolblue():
    """Hoofdfunctie: feed ophalen, filteren en aanbiedingen bijwerken."""
    app = create_app()

    with app.app_context():
        apikey = os.getenv('AWIN_FEED_APIKEY')
        if not apikey:
            logger.error("[!] AWIN_FEED_APIKEY ontbreekt - Coolblue-sync overgeslagen")
            return

        sync_log = SyncLog(started_at=utcnow())
        db.session.add(sync_log)
        db.session.flush()
        logger.info(f"[+] Coolblue-sync gestart (Log ID: {sync_log.id})")

        try:
            rows = fetch_feed(apikey)
        except requests.exceptions.RequestException as e:
            logger.error(f"[!] Feed ophalen mislukt: {e}")
            sync_log.finished_at = utcnow()
            sync_log.errors = str(e)
            db.session.commit()
            return
        logger.info(f"[+] Feed: {len(rows)} producten ontvangen")

        categories = {c.slug: c for c in Category.query.all()}
        added = updated = skipped = 0
        seen_product_ids = set()
        seen_eans = set()

        for row in rows:
            record = normalize(row)
            if not record:
                continue
            if record['ean'] in seen_eans:
                continue

            title = record['title']
            category_slug = classify(record['product_type'], title)
            if not category_slug:
                continue
            category = categories.get(category_slug)
            if not category:
                logger.warning(f"[!] Categorie {category_slug} bestaat niet in de database")
                continue

            lowered = title.lower()
            if any(keyword in lowered for keyword in EXCLUDE_KEYWORDS):
                skipped += 1
                continue

            if record['price'] < MIN_PRICES.get(category_slug, 0):
                # te goedkoop voor een echt apparaat - vrijwel zeker een accessoire
                skipped += 1
                continue

            seen_eans.add(record['ean'])

            product = Product.query.filter_by(ean=record['ean']).first()
            if not product:
                product = Product(
                    ean=record['ean'],
                    title=title,
                    brand=record['brand'] or guess_brand(title),
                    description=record['description'],
                    price=record['price'],
                    strikethrough_price=record['strikethrough_price'],
                    image_url=record['image_url'],
                    # products.bol_url is NOT NULL en bestaat alleen voor de
                    # Bol-sync; zie de MediaMarkt-sync voor dezelfde afweging.
                    bol_url='',
                    category_id=category.id,
                    subcategory=record['product_type'],
                    slug=f"{title[:50].lower().replace(' ', '-').replace('/', '-')}-{record['ean']}",
                    retailer=RETAILER,
                    specs={},
                    is_available=record['is_available'],
                    last_synced=utcnow(),
                )
                db.session.add(product)
                db.session.flush()  # product.id nodig voor de aanbieding
                added += 1
            else:
                # Bestaat het apparaat al (via Bol of MediaMarkt), dan laten we
                # titel, foto en specs met rust: dat is de identiteit van het
                # product, niet de aanbieding.
                updated += 1

            offer = Offer.query.filter_by(product_id=product.id, retailer=RETAILER).first()
            if not offer:
                offer = Offer(product_id=product.id, retailer=RETAILER)
                db.session.add(offer)

            offer.price = record['price']
            offer.strikethrough_price = record['strikethrough_price']
            offer.url = record['url']
            offer.affiliate_url = record['affiliate_url']
            offer.is_available = record['is_available']
            offer.last_synced = utcnow()

            seen_product_ids.add(product.id)

        db.session.commit()

        removed_offers, removed_products = _cleanup(seen_product_ids)

        # Prijs en voorraad van het product afleiden uit de aanbiedingen, zodat
        # het prijsfilter en de sortering de goedkoopste winkel volgen.
        for product in Product.query.filter(Product.id.in_(seen_product_ids)).all():
            product.refresh_pricing()
        db.session.commit()

        sync_log.finished_at = utcnow()
        sync_log.products_synced = added
        sync_log.products_updated = updated
        sync_log.products_hidden = removed_products
        db.session.commit()

        logger.info("[+] Coolblue-sync klaar")
        logger.info(f"    - Nieuwe producten (alleen Coolblue): {added}")
        logger.info(f"    - Gekoppeld aan bestaand product: {updated}")
        logger.info(f"    - Overgeslagen (accessoire/te goedkoop): {skipped}")
        logger.info(f"    - Verlopen aanbiedingen verwijderd: {removed_offers}")
        logger.info(f"    - Producten verwijderd (nergens meer te koop): {removed_products}")


def _cleanup(seen_product_ids):
    """Aanbiedingen weghalen die niet meer in de feed staan, en producten die
    daardoor bij geen enkele winkel meer te koop zijn."""
    bestaand = Offer.query.filter_by(retailer=RETAILER).count()

    # Veiligheidsklep: komt de feed door een storing leeg of half terug, dan
    # zou blind opruimen het hele Coolblue-aanbod van de site vegen. Bij een
    # verdachte terugval slaan we het opruimen over; de volgende sync herstelt
    # het vanzelf.
    if bestaand and len(seen_product_ids) < bestaand * MIN_FEED_RATIO:
        logger.error(
            f"[!] Feed leverde maar {len(seen_product_ids)} van de {bestaand} bekende "
            f"aanbiedingen; opruimen overgeslagen om dataverlies te voorkomen."
        )
        return 0, 0

    if not seen_product_ids:
        return 0, 0

    stale = Offer.query.filter(
        Offer.retailer == RETAILER,
        ~Offer.product_id.in_(seen_product_ids),
    ).all()

    orphan_candidates = {offer.product_id for offer in stale}
    for offer in stale:
        db.session.delete(offer)
    db.session.commit()

    removed_products = 0
    for product_id in orphan_candidates:
        product = db.session.get(Product, product_id)
        # Alleen producten opruimen die wij hebben aangemaakt: een Bol- of
        # MediaMarkt-product zonder aanbiedingen is een probleem van die syncs.
        if product and not product.offers and product.retailer == RETAILER:
            db.session.delete(product)
            removed_products += 1
    if removed_products:
        db.session.commit()

    return len(stale), removed_products


if __name__ == '__main__':
    sync_coolblue()
