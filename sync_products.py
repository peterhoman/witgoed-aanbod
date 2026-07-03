"""
Bol.com Marketing Catalog API Sync Script
Fetches products from Bol.com Marketing Catalog API and stores in database
"""

import os
import requests
import base64
import time
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
        """Search products by query (for discovery, not for sync)"""
        self._refresh_token_if_needed()

        params = {
            "country-code": "NL",
            "search-term": query,
            "limit": limit
        }

        try:
            response = requests.get(
                f"{self.base_url}/products/search",
                headers=self.get_headers(),
                params=params,
                timeout=15
            )

            if self._handle_rate_limit(response):
                return self.search_products(query, limit)

            if response.status_code == 200:
                return response.json().get('products', [])
            logger.error(f"[!] Search failed for '{query}': {response.status_code} {response.text[:300]}")
            return []

        except Exception as e:
            logger.error(f"[!] Search error for '{query}': {e}")
            return []


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

            search_results = api.search_products(category_name, limit=100)

            if not search_results:
                logger.warning(f"[*] No products found for {category_name}")
                continue

            logger.info(f"[*] Found {len(search_results)} results for {category_name}")

            category_real_products_synced = 0

            for result in search_results:
                try:
                    ean = result.get('ean') or result.get('id')
                    if not ean:
                        continue

                    logger.debug(f"[*] Fetching details for EAN: {ean}")
                    prod_data = api.fetch_product(ean)

                    if not prod_data:
                        total_errors += 1
                        continue

                    product = Product.query.filter_by(ean=ean).first()

                    title = prod_data.get('title', 'Unknown')
                    price = 0
                    image_url = ''
                    rating = 0

                    if 'offers' in prod_data and prod_data['offers']:
                        offer = prod_data['offers'][0]
                        price = float(offer.get('price', 0) or 0)

                    if 'images' in prod_data and prod_data['images']:
                        image_url = prod_data['images'][0].get('url', '')

                    if 'rating' in prod_data:
                        rating = float(prod_data['rating'].get('score', 0) or 0)

                    specs = extract_specs(prod_data)

                    slug = f"{title[:50].lower().replace(' ', '-').replace('/', '-')}-{ean}"
                    bol_url = f"https://www.bol.com/nl/p/{ean}/"

                    if product:
                        product.title = title
                        product.price = price
                        product.image_url = image_url
                        product.rating = rating
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
                            price=price,
                            image_url=image_url,
                            rating=rating,
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

                except Exception as e:
                    logger.error(f"[!] Error processing product: {e}")
                    total_errors += 1
                    continue

            db.session.commit()
            logger.info(f"[+] {category_name}: {len(search_results)} checked")

            if category_real_products_synced > 0:
                removed = Product.query.filter_by(category_id=category.id, is_example=True).delete()
                if removed:
                    db.session.commit()
                    logger.info(f"[+] {category_name}: removed {removed} example product(s), real data now available")

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
