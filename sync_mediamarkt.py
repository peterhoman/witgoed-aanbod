"""
MediaMarkt productfeed sync (via Tradedoubler)

Haalt de MediaMarkt-productfeed op, filtert het witgoed eruit en zet per
apparaat een MediaMarkt-aanbieding (Offer) in de database. Bestaat het
apparaat al door de Bol-sync, dan wordt het via de EAN-streepjescode aan
datzelfde product gekoppeld; anders komt er een nieuw product bij met
MediaMarkt als enige aanbieder.

De affiliate-link hoeven we niet zelf op te bouwen: de feed levert per
product een kant-en-klare Tradedoubler-deeplink (productUrl) met onze
source-ID er al in verwerkt.
"""

import gc
import io
import json
import os
import re
import requests
from app import create_app
from models import db, Product, Category, Offer, SyncLog, utcnow, log_price
from sync_products import EXCLUDE_KEYWORDS, MIN_PRICES, guess_brand
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RETAILER = 'mediamarkt'
BASE_URL = "https://api.tradedoubler.com/1.0"

# De hoofdfeed (hele MediaMarkt-catalogus, ~12.000 producten).
MAIN_FEED_ID = 23056

# Aanvullende categoriefeeds. Die zijn grotendeels een deelverzameling van de
# hoofdfeed, maar niet volledig: ze worden op een ander moment ververst,
# waardoor er tientallen producten (vooral stofzuigers) alleen hierin staan.
# Ontdubbeling gebeurt op EAN, dus overlap is ongevaarlijk.
EXTRA_FEED_IDS = [
    50615,  # Koelkasten
    50619,  # Wassen en drogen
    50622,  # Stofzuigers
]

# products.json geeft nooit meer dan 1000 resultaten terug (offset >= 1000
# levert een HTTP 400). Voor de hoofdfeed gebruiken we daarom het
# productsUnlimited-endpoint, dat de complete feed in één keer levert.
PAGE_SIZE = 100
MAX_PAGES = 10

# Levert een sync minder dan dit deel van de bekende aanbiedingen op, dan gaan
# we ervan uit dat de feed hapert en ruimen we niets op. MediaMarkt haalt
# geregeld producten uit de verkoop, maar nooit de helft in één keer.
MIN_FEED_RATIO = 0.5

# MediaMarkt's eigen categorie-indeling is één niveau diep. Al het witgoed zit
# in deze drie takken; de rest (Computer, Gaming, Telefonie, Tv, ...) valt
# hiermee meteen af.
WITGOED_CATEGORY_PATHS = {
    'Grote keukenapparatuur',
    'Kleine keukenapparatuur',
    'Huishouden',
}

# Binnen die takken bepaalt de producttitel in welke categorie van de site het
# apparaat hoort. Het EERSTE passende patroon wint, dus de volgorde is bepalend:
#  - een wasdroogcombinatie bevat zowel "was" als "droog";
#  - een fornuis heet vaak "Fornuis met oven", een kookplaat "Inductiekookplaat
#    met ovenaansluiting" - beide moeten vóór het ovenpatroon staan;
#  - een afzuigkap kan "voor inductiekookplaat" in de titel hebben.
CATEGORY_PATTERNS = [
    ('wasdroogcombinaties', r'was[-\s]?droog|wasdroogcombinatie|washer[-\s]?dryer'),
    ('wasmachines', r'wasmachine|wasautomaat'),
    ('drogers', r'droger|droogkast|droogautomaat'),
    ('koelkasten', r'koelkast|koel[-\s]?vries|vrieskast|vriezer|wijnklimaatkast|wijnkoelkast'),
    ('vaatwassers', r'vaatwas'),
    ('magnetrons', r'magnetron'),
    ('afzuigkappen', r'afzuigkap|dampkap|wasemkap'),
    ('fornuizen', r'fornuis'),
    ('kookplaten', r'kookplaat|kookveld|kooktoestel'),
    # "volautomatisch" bewust niet als los woord: te algemeen. Elke echte
    # koffiemachine bevat "koffie" of "espresso" in de titel.
    ('koffiemachines', r'koffie|espresso|senseo|nespresso|dolce gusto|percolator|cafetiere'),
    ('ovens', r'\boven\b|inbouwoven|combi[-\s]?oven|stoomoven|bakoven|airfryer|heteluchtfriteuse'),
    ('stofzuigers', r'stofzuiger|kruimeldief'),
]


def classify(title):
    """Bepaal in welke categorie van de site dit apparaat hoort, of None."""
    for slug, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return slug
    return None


def _get_field(product, name):
    """Waarde uit de losse 'fields'-lijst van de feed (category_path, from_price...)."""
    for field in product.get('fields', []):
        if field.get('name') == name:
            return field.get('value')
    return None


def _parse_price(value):
    """'179.00 EUR' of '143.99' -> 179.0 / 143.99; onbruikbaar -> None."""
    if not value:
        return None
    match = re.search(r'[\d.]+', str(value))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None


def fetch_full_feed(token, feed_id):
    """Hele feed in één keer (alleen de hoofdfeed ondersteunt dit endpoint).

    De feed is ~31 MB. Rechtstreeks uit de netwerkstroom lezen scheelt het
    dubbel in geheugen houden van de ruwe tekst; deze sync draait in hetzelfde
    proces als de website.
    """
    url = f"{BASE_URL}/productsUnlimited.json;fid={feed_id}"
    with requests.get(url, params={'token': token}, timeout=300, stream=True) as response:
        response.raise_for_status()
        response.raw.decode_content = True
        return json.load(io.TextIOWrapper(response.raw, encoding='utf-8')).get('products', [])


def fetch_paged_feed(token, feed_id):
    """Kleine feeds (< 1000 producten) pagina voor pagina."""
    products = []
    for page in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}/products.json;page={page};pageSize={PAGE_SIZE};fid={feed_id}"
        response = requests.get(url, params={'token': token}, timeout=60)
        response.raise_for_status()
        response.encoding = 'utf-8'
        batch = response.json().get('products', [])
        products.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
    return products


def normalize(product, from_main_feed):
    """Zet een feedproduct om in het handjevol velden dat wij nodig hebben.

    De hoofdfeed bevat 12.000+ producten met lange beschrijvingen; die hele
    structuur vasthouden kost ruim 80 MB. Alleen het nodige overhouden houdt
    het geheugengebruik van de webserver laag.
    """
    ean = str((product.get('identifiers') or {}).get('ean') or '')
    title = (product.get('name') or '').strip()
    if not ean or not title:
        return None

    offers = product.get('offers') or []
    if not offers:
        return None
    offer = offers[0]

    history = offer.get('priceHistory') or []
    if not history:
        return None
    price = _parse_price((history[0].get('price') or {}).get('value'))
    if not price or price <= 0:
        return None

    # from_price is MediaMarkt's adviesprijs; alleen tonen als er echt een
    # korting is (zelfde regel als bij de Bol-sync).
    advies = _parse_price(_get_field(product, 'from_price'))

    # 'inStock' is een AANTAL, geen ja/nee. Alles boven 0 is leverbaar.
    try:
        in_stock = int(offer.get('inStock') or 0)
    except (TypeError, ValueError):
        in_stock = 0

    return {
        'ean': ean,
        'title': title,
        'brand': product.get('brand'),
        'description': product.get('description'),
        'image_url': (product.get('productImage') or {}).get('url', ''),
        'category_path': _get_field(product, 'category_path'),
        'price': price,
        'strikethrough_price': advies if advies and advies > price else None,
        'affiliate_url': offer.get('productUrl'),
        'is_available': in_stock > 0 or offer.get('availability') == 'in stock',
        'from_main_feed': from_main_feed,
    }


def collect_feed_products(token):
    """Alle feeds ophalen, uitdunnen en ontdubbelen op EAN (hoofdfeed eerst)."""
    by_ean = {}

    logger.info(f"[*] Hoofdfeed {MAIN_FEED_ID} ophalen...")
    raw = fetch_full_feed(token, MAIN_FEED_ID)
    logger.info(f"[+] Hoofdfeed: {len(raw)} producten ontvangen")
    for product in raw:
        record = normalize(product, from_main_feed=True)
        if record:
            by_ean.setdefault(record['ean'], record)
    # De ruwe feed mag meteen weg; hij is veruit het grootste object in geheugen.
    del raw
    gc.collect()

    for feed_id in EXTRA_FEED_IDS:
        before = len(by_ean)
        try:
            extra = fetch_paged_feed(token, feed_id)
        except requests.exceptions.RequestException as e:
            # Een aanvullende feed is een bonus, geen voorwaarde: de hoofdfeed
            # bevat het overgrote deel. Val niet om op een tijdelijke storing.
            logger.warning(f"[!] Aanvullende feed {feed_id} overgeslagen: {e}")
            continue
        for product in extra:
            record = normalize(product, from_main_feed=False)
            if record:
                by_ean.setdefault(record['ean'], record)
        logger.info(f"[+] Feed {feed_id}: {len(extra)} producten, {len(by_ean) - before} nieuw")
        del extra

    gc.collect()
    return by_ean


def sync_mediamarkt():
    """Hoofdfunctie: feed ophalen, filteren en aanbiedingen bijwerken."""
    app = create_app()

    with app.app_context():
        token = os.getenv('TRADEDOUBLER_TOKEN')
        if not token:
            logger.error("[!] TRADEDOUBLER_TOKEN ontbreekt - MediaMarkt-sync overgeslagen")
            return

        sync_log = SyncLog(started_at=utcnow())
        db.session.add(sync_log)
        db.session.flush()
        logger.info(f"[+] MediaMarkt-sync gestart (Log ID: {sync_log.id})")

        try:
            feed_products = collect_feed_products(token)
        except requests.exceptions.RequestException as e:
            logger.error(f"[!] Feed ophalen mislukt: {e}")
            sync_log.finished_at = utcnow()
            sync_log.errors = str(e)
            db.session.commit()
            return

        categories = {c.slug: c for c in Category.query.all()}
        added = updated = skipped = 0
        seen_product_ids = set()

        for ean, record in feed_products.items():
            title = record['title']

            # Producten uit de aanvullende categoriefeeds zijn al voorgefilterd
            # en hoeven niet in de drie witgoed-takken van de hoofdfeed te zitten.
            if record['from_main_feed'] and record['category_path'] not in WITGOED_CATEGORY_PATHS:
                continue

            lowered = title.lower()
            if any(keyword in lowered for keyword in EXCLUDE_KEYWORDS):
                skipped += 1
                continue

            category_slug = classify(title)
            if not category_slug:
                continue
            category = categories.get(category_slug)
            if not category:
                logger.warning(f"[!] Categorie {category_slug} bestaat niet in de database")
                continue

            if record['price'] < MIN_PRICES.get(category_slug, 0):
                # te goedkoop voor een echt apparaat - vrijwel zeker een accessoire
                skipped += 1
                continue

            product = Product.query.filter_by(ean=ean).first()
            if not product:
                product = Product(
                    ean=ean,
                    title=title,
                    brand=record['brand'] or guess_brand(title),
                    description=record['description'],
                    price=record['price'],
                    strikethrough_price=record['strikethrough_price'],
                    image_url=record['image_url'],
                    # products.bol_url is NOT NULL en bestaat alleen voor de
                    # Bol-sync. Een product dat alleen bij MediaMarkt bestaat
                    # heeft geen Bol-pagina; de knoppen op de site komen uit de
                    # aanbiedingen, niet uit dit veld.
                    bol_url='',
                    category_id=category.id,
                    subcategory=record['category_path'],
                    slug=f"{title[:50].lower().replace(' ', '-').replace('/', '-')}-{ean}",
                    retailer=RETAILER,
                    specs={},
                    is_available=record['is_available'],
                    last_synced=utcnow(),
                )
                db.session.add(product)
                db.session.flush()  # product.id nodig voor de aanbieding
                added += 1
            else:
                # Bestaat het apparaat al (meestal via Bol), dan laten we titel,
                # foto en specs met rust: dat is de identiteit van het product,
                # niet de aanbieding. Uitzondering: een ontbrekende foto vullen
                # we alsnog aan (kapotte afbeelding op de site).
                if not product.image_url and record['image_url']:
                    product.image_url = record['image_url']
                updated += 1

            offer = Offer.query.filter_by(product_id=product.id, retailer=RETAILER).first()
            if not offer:
                offer = Offer(product_id=product.id, retailer=RETAILER)
                db.session.add(offer)

            offer.price = record['price']
            offer.strikethrough_price = record['strikethrough_price']
            offer.url = record['affiliate_url']
            offer.affiliate_url = record['affiliate_url']
            offer.is_available = record['is_available']
            offer.last_synced = utcnow()
            if record['is_available']:
                log_price(product.id, RETAILER, record['price'])

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

        logger.info("[+] MediaMarkt-sync klaar")
        logger.info(f"    - Nieuwe producten (alleen MediaMarkt): {added}")
        logger.info(f"    - Gekoppeld aan bestaand product: {updated}")
        logger.info(f"    - Overgeslagen (accessoire/te goedkoop): {skipped}")
        logger.info(f"    - Verlopen aanbiedingen verwijderd: {removed_offers}")
        logger.info(f"    - Producten verwijderd (nergens meer te koop): {removed_products}")


def _cleanup(seen_product_ids):
    """Aanbiedingen weghalen die niet meer in de feed staan, en producten die
    daardoor bij geen enkele winkel meer te koop zijn."""
    bestaand = Offer.query.filter_by(retailer=RETAILER).count()

    # Veiligheidsklep. Komt de feed door een storing leeg of half terug, dan zou
    # blind opruimen het hele MediaMarkt-aanbod van de site vegen. Bij een
    # verdachte terugval slaan we het opruimen over: verouderde prijzen zijn
    # minder erg dan een lege site, en de volgende sync (over 12 uur) herstelt
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
        # Producten zonder aanbiedingen niet meer verwijderen maar als
        # "tijdelijk niet leverbaar" markeren: koopgidsen en YouTube-video's
        # linken naar productpagina's, en een 404 breekt die links (en de
        # commissie) terwijl het apparaat vaak gewoon terugkomt in de feed.
        if product and not product.offers and product.retailer == RETAILER:
            product.refresh_pricing()  # zet is_available op False
            removed_products += 1
    if removed_products:
        db.session.commit()

    return len(stale), removed_products


if __name__ == '__main__':
    sync_mediamarkt()
