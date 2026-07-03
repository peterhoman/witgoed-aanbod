"""
Bol.com Marketing Catalog API Sync Script
Fetches products from Bol.com Marketing Catalog API and stores in database
"""

import os
import requests
import base64
import time
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from app import create_app
from models import db, Product, Category, SyncLog
from bitly_helper import get_bitly_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BolAPI:
    """Bol.com Marketing Catalog API client"""

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        # v1, niet v4: het werkende bol-affiliate-page-project draait op v1 en
        # v4 gaf op dit account overal 403 "Unauthorized Request"
        self.base_url = "https://api.bol.com/marketing/catalog/v1"
        self.token_url = "https://login.bol.com/token"
        self.token = None
        self.token_expires = None
        self.rate_limit_remaining = 10
        self.rate_limit_reset = None

    def _get_basic_auth_header(self):
        """Generate Basic Authentication header"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def authenticate(self):
        """Get OAuth token from Bol.com using Client Credentials flow"""
        try:
            response = requests.post(
                f"{self.token_url}?grant_type=client_credentials",
                headers={
                    "Authorization": self._get_basic_auth_header(),
                    "Accept": "application/json"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get('access_token')
            expires_in = data.get('expires_in', 299)
            self.token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 10)
            logger.info("[+] Authenticated successfully with Marketing Catalog API")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"[!] Authentication failed: {e}")
            return False

    def _refresh_token_if_needed(self):
        """Refresh token if expired"""
        if self.token_expires and datetime.utcnow() >= self.token_expires:
            logger.info("[*] Token expired, refreshing...")
            self.authenticate()

    def _handle_rate_limit(self, response):
        """Handle rate limit headers and backoff if needed"""
        self.rate_limit_remaining = int(response.headers.get('x-ratelimit-remaining', 1))
        self.rate_limit_reset = int(response.headers.get('x-ratelimit-reset', 0))

        if response.status_code == 429:
            wait_time = self.rate_limit_reset - int(time.time())
            wait_time = max(wait_time, 1)
            logger.warning(f"[!] Rate limited! Waiting {wait_time} seconds...")
            time.sleep(wait_time)
            return True

        if self.rate_limit_remaining < 5:
            logger.info(f"[*] Rate limit low ({self.rate_limit_remaining} remaining). Waiting 1 second...")
            time.sleep(1)

        return False

    def get_headers(self):
        """Return headers for API requests"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "nl",
            "Accept": "application/json"
        }

    def _validate_ean(self, ean):
        """Validate EAN format (must be 13 digits)"""
        if not ean or len(str(ean)) != 13 or not str(ean).isdigit():
            return False
        return True

    def fetch_product(self, ean):
        """Fetch single product by EAN"""
        self._refresh_token_if_needed()

        if not self._validate_ean(ean):
            logger.warning(f"[!] Invalid EAN format: {ean}")
            return None

        params = {
            "country-code": "NL",
            "include-image": True,
            "include-offer": True,
            "include-rating": True,
            "include-specifications": True
        }

        try:
            response = requests.get(
                f"{self.base_url}/products/{ean}",
                headers=self.get_headers(),
                params=params,
                timeout=15
            )

            if self._handle_rate_limit(response):
                return self.fetch_product(ean)

            if response.status_code == 401:
                logger.error("[!] Unauthorized - token invalid. Re-authenticating...")
                self.authenticate()
                return self.fetch_product(ean)

            if response.status_code == 404:
                logger.debug(f"[*] Product {ean} not found")
                return None

            if response.status_code == 406:
                logger.error("[!] Not Acceptable - language/country code issue")
                return None

            if response.status_code == 400:
                logger.error(f"[!] Bad Request: {response.text}")
                return None

            if response.status_code == 500:
                logger.error("[!] Bol.com server error (500)")
                return None

            if response.status_code == 503:
                logger.warning("[!] Bol.com service unavailable (503). Retrying...")
                time.sleep(5)
                return self.fetch_product(ean)

            if response.status_code == 200:
                return response.json()

            logger.error(f"[!] Unexpected status code: {response.status_code}")
            return None

        except requests.exceptions.Timeout:
            logger.error(f"[!] Timeout fetching {ean}")
            return None
        except Exception as e:
            logger.error(f"[!] Error fetching product {ean}: {e}")
            return None

    def search_products(self, query, limit=100):
        """Search products by query via GET /products/search.

        v1 pagineert met page-size/page (niet "limit") en levert de lijst
        onder de sleutel "results". include-image/include-offer zorgen dat
        elk zoekresultaat direct bruikbaar is als de losse detail-call
        niets oplevert.
        """
        self._refresh_token_if_needed()

        results = []
        page = 1
        while len(results) < limit:
            params = {
                "country-code": "NL",
                "search-term": query,
                "include-image": "true",
                "include-offer": "true",
                "sort": "POPULARITY",
                "page-size": 50,
                "page": page,
            }
            try:
                response = requests.get(
                    f"{self.base_url}/products/search",
                    headers=self.get_headers(),
                    params=params,
                    timeout=15
                )

                if self._handle_rate_limit(response):
                    continue  # 429: opnieuw dezelfde pagina proberen

                if response.status_code == 404:
                    break  # "Page N is not available" — geen resultaten meer

                if response.status_code != 200:
                    logger.error(f"[!] Search failed for '{query}': {response.status_code} {response.text[:300]}")
                    break

                data = response.json()
                page_items = data.get('results', data.get('products', []))
                if not page_items:
                    break
                results.extend(page_items)
                if len(page_items) < 50:
                    break
                page += 1

            except Exception as e:
                logger.error(f"[!] Search error for '{query}': {e}")
                break

        return results[:limit]


def extract_specs(prod_data):
    """Normalize Bol.com API 'specifications' field into a flat {name: value} dict.

    The Marketing Catalog API groups specifications, e.g.:
    "specifications": [{"values": [{"key": "Vulgewicht", "value": "9 kg"}, ...]}, ...]

    This is defensive since the exact shape should be reconfirmed against a
    live API response once Bol.com API access is approved.
    """
    specs = {}
    raw_specs = prod_data.get('specifications', [])

    if isinstance(raw_specs, dict):
        return {str(k): str(v) for k, v in raw_specs.items() if v}

    if isinstance(raw_specs, list):
        for group in raw_specs:
            if not isinstance(group, dict):
                continue
            values = group.get('values', group.get('specifications', []))
            if isinstance(values, list):
                for item in values:
                    if not isinstance(item, dict):
                        continue
                    key = item.get('key') or item.get('name')
                    value = item.get('value')
                    if key and value:
                        specs[str(key)] = str(value)

    return specs


# Zoeken op term ("Wasmachines") levert ook wasmiddel, doseerbollen,
# textielverf enz. op. Twee vangnetten, zelfde aanpak als bewezen in
# bol-affiliate-page: een minimumprijs per categorie plus een
# uitsluitlijst met accessoire-woorden in de titel.
# Hoeveel zoekresultaten per categorie worden opgehaald (vóór filtering).
# Hoofdcategorieën wat ruimer; na de prijs-/trefwoordfilters blijft daar
# grofweg de helft tot twee derde van over op de site.
SEARCH_LIMITS = {
    'wasmachines': 150,
    'koelkasten': 150,
}
DEFAULT_SEARCH_LIMIT = 100

MIN_PRICES = {
    'wasmachines': 150,
    'drogers': 150,
    'wasdroogcombinaties': 300,
    'koelkasten': 130,
    'vaatwassers': 150,
    'magnetrons': 50,
    'ovens': 100,
    'stofzuigers': 50,
}

EXCLUDE_KEYWORDS = [
    'tablet', 'wasmiddel', 'reinig', 'ontkalk', 'lijm', 'verf', 'pods',
    'doseer', 'wasbol', 'hoes', 'slang', 'stofzuigerzak', 'geurbooster',
    'wasparfum', 'verhoger', 'onderstel', 'trillingsdemper', 'wasmand',
    'droogrek', 'strijkplank', 'wasverzachter', 'capsule', 'navulling',
    'magnetronschaal', 'ovenschaal', 'bakplaat', 'ovenwant', 'wasstrips',
    'stapelkit', 'tussenstuk', 'afvoerslang', 'aanvoerslang', 'filterzak',
]

# De v1-zoekresultaten bevatten geen merkveld; herken het merk uit de titel.
KNOWN_BRANDS = [
    'Samsung', 'LG', 'Bosch', 'Siemens', 'AEG', 'Miele', 'Whirlpool', 'Beko',
    'Haier', 'Hisense', 'Indesit', 'Bauknecht', 'Zanussi', 'Electrolux',
    'Inventum', 'CHiQ', 'Sharp', 'Candy', 'Hoover', 'Etna', 'ATAG', 'Smeg',
    'Liebherr', 'Dyson', 'Philips', 'Rowenta', 'Nilfisk', 'Tefal', 'Bissell',
    'Panasonic', 'Exquisit', 'Salora', 'Tomado', 'Princess', 'TriStar',
    'Blaupunkt', 'Grundig', 'Gorenje', 'Pelgrim', 'Boretti', 'Frilec',
    'Bomann', 'Severin', 'Medion', 'Vestfrost', 'Scandomestic', 'Karcher',
    'Kärcher', 'Shark', 'Rooboost', 'Eufy', 'iRobot', 'Roborock', 'Ecovacs',
]


def guess_brand(title):
    """Herken een bekend merk in de producttitel (heel woord, hoofdletterongevoelig)."""
    import re
    for brand in KNOWN_BRANDS:
        if re.search(rf'\b{re.escape(brand)}\b', title, re.IGNORECASE):
            return brand
    return None


def sync_products():
    """Main sync function - fetches products from Bol.com Marketing Catalog API"""
    app = create_app()

    with app.app_context():
        client_id = os.getenv('BOL_CLIENT_ID')
        client_secret = os.getenv('BOL_CLIENT_SECRET')

        if not client_id or not client_secret:
            logger.error("[!] Missing Bol.com credentials. Set BOL_CLIENT_ID and BOL_CLIENT_SECRET")
            return

        sync_log = SyncLog(started_at=datetime.utcnow())
        db.session.add(sync_log)
        db.session.flush()

        logger.info(f"[+] Starting Marketing Catalog API sync... (Log ID: {sync_log.id})")

        bitly_token = os.getenv('BITLY_TOKEN')
        bitly_client = get_bitly_client(bitly_token)
        if bitly_client:
            logger.info("[+] Bit.ly URL shortening enabled")
        else:
            logger.warning("[!] Bit.ly token not set - using full affiliate URLs")

        api = BolAPI(client_id, client_secret)

        if not api.authenticate():
            logger.error("[!] Failed to authenticate with Bol.com")
            sync_log.finished_at = datetime.utcnow()
            sync_log.products_synced = 0
            sync_log.products_updated = 0
            db.session.commit()
            return

        total_synced = 0
        total_updated = 0
        total_errors = 0

        categories = [
            ('Wasmachines', 'wasmachines'),
            ('Drogers', 'drogers'),
            ('Wasdroogcombinaties', 'wasdroogcombinaties'),
            ('Koelkasten', 'koelkasten'),
            ('Vaatwassers', 'vaatwassers'),
            ('Magnetrons', 'magnetrons'),
            ('Ovens', 'ovens'),
            ('Stofzuigers', 'stofzuigers'),
        ]

        for category_name, category_slug in categories:
            logger.info(f"[*] Searching products for {category_name}...")

            category = Category.query.filter_by(slug=category_slug).first()
            if not category:
                logger.warning(f"[!] Category {category_name} not found in database")
                continue

            search_results = api.search_products(category_name, limit=SEARCH_LIMITS.get(category_slug, DEFAULT_SEARCH_LIMIT))

            if not search_results:
                logger.warning(f"[*] No products found for {category_name}")
                continue

            logger.info(f"[*] Found {len(search_results)} results for {category_name}")

            category_real_products_synced = 0
            seen_eans = set()
            min_price = MIN_PRICES.get(category_slug, 0)

            for result in search_results:
                try:
                    ean = result.get('ean') or result.get('id')
                    if not ean:
                        continue

                    # Accessoires (wasmiddel, doseerbollen, verf...) op titel
                    # weren vóór de dure detail-call
                    result_title = (result.get('title') or '').lower()
                    if any(kw in result_title for kw in EXCLUDE_KEYWORDS):
                        logger.debug(f"[-] Skipped accessory: {result.get('title')}")
                        continue

                    logger.debug(f"[*] Fetching details for EAN: {ean}")
                    # Detail-call voor specs; lukt die niet, dan is het
                    # zoekresultaat zelf (met include-image/include-offer)
                    # genoeg om het product op te voeren.
                    prod_data = api.fetch_product(ean) or result

                    product = Product.query.filter_by(ean=ean).first()

                    title = prod_data.get('title', 'Unknown')
                    price = 0
                    image_url = ''

                    # v1 gebruikt 'offer'/'image' (enkelvoud, object); wees
                    # tolerant voor een eventuele 'offers'/'images'-lijstvorm
                    offers = prod_data.get('offers') or ([prod_data['offer']] if prod_data.get('offer') else [])
                    if offers:
                        price = float(offers[0].get('price', 0) or 0)

                    images = prod_data.get('images') or ([prod_data['image']] if prod_data.get('image') else [])
                    if images:
                        image_url = images[0].get('url', '')

                    specs = extract_specs(prod_data)
                    brand = specs.get('Merk') or prod_data.get('brand') or guess_brand(title)

                    if price < min_price:
                        # geen koopbaar aanbod, of te goedkoop om een echt
                        # apparaat te zijn (accessoireprijs) — overslaan
                        logger.debug(f"[-] Skipped (price {price} < {min_price}): {title}")
                        continue

                    slug = f"{title[:50].lower().replace(' ', '-').replace('/', '-')}-{ean}"
                    # De echte productpagina-URL zit in de API-respons ('url');
                    # zelf bol.com/nl/p/{ean} opbouwen gaf een 404 op de knop.
                    # Uiterste fallback: een bol-zoekpagina op de titel.
                    bol_url = (prod_data.get('url') or result.get('url')
                               or f"https://www.bol.com/nl/nl/s/?searchtext={quote_plus(title)}")

                    if product:
                        product.title = title
                        product.brand = brand or product.brand
                        product.price = price
                        product.image_url = image_url
                        product.bol_url = bol_url
                        product.retailer = 'bol'
                        product.specs = specs
                        product.affiliate_url = product.generate_short_affiliate_url(bitly_client, site_id='1528790')
                        product.is_available = True
                        product.last_synced = datetime.utcnow()
                        total_updated += 1
                        category_real_products_synced += 1
                        logger.debug(f"[+] Updated: {title}")
                    else:
                        product = Product(
                            ean=ean,
                            title=title,
                            brand=brand,
                            price=price,
                            image_url=image_url,
                            bol_url=bol_url,
                            category_id=category.id,
                            slug=slug,
                            retailer='bol',
                            specs=specs,
                            is_available=True,
                            last_synced=datetime.utcnow()
                        )
                        product.affiliate_url = product.generate_short_affiliate_url(bitly_client, site_id='1528790')
                        db.session.add(product)
                        total_synced += 1
                        category_real_products_synced += 1
                        logger.debug(f"[+] Added: {title}")

                    seen_eans.add(str(ean))

                except Exception as e:
                    logger.error(f"[!] Error processing product: {e}")
                    total_errors += 1
                    continue

            db.session.commit()
            logger.info(f"[+] {category_name}: {len(search_results)} checked, {category_real_products_synced} kept")

            if category_real_products_synced > 0:
                removed = Product.query.filter_by(category_id=category.id, is_example=True).delete()
                # Ruim ook eerder gesyncte producten op die niet meer door de
                # filters komen (bv. de accessoires uit de eerste sync-run)
                stale = Product.query.filter(
                    Product.category_id == category.id,
                    Product.is_example == False,
                    ~Product.ean.in_(seen_eans),
                ).delete(synchronize_session=False)
                if removed or stale:
                    db.session.commit()
                    logger.info(f"[+] {category_name}: removed {removed} example product(s) and {stale} stale/filtered product(s)")

        sync_log.finished_at = datetime.utcnow()
        sync_log.products_synced = total_synced
        sync_log.products_updated = total_updated
        db.session.commit()

        logger.info(f"[+] Sync complete!")
        logger.info(f"    - New products: {total_synced}")
        logger.info(f"    - Updated products: {total_updated}")
        logger.info(f"    - Errors: {total_errors}")


if __name__ == '__main__':
    sync_products()
