"""
Bol.com Product Sync Script
Fetches products from Bol.com API and stores in database
"""

import os
import requests
from datetime import datetime
from app import create_app
from models import db, Product, Category, SyncLog
import json

class BolAPI:
    """Bol.com API client - using Open Partner API"""

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.bol.com/v2"
        self.token = None

    def authenticate(self):
        """Get OAuth token from Bol.com"""
        auth_url = f"{self.base_url}/oauth/token"

        try:
            response = requests.post(
                auth_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get('access_token')
            print(f"[+] Authenticated successfully")
            return True
        except Exception as e:
            print(f"[!] Authentication failed: {e}")
            return False

    def get_headers(self):
        """Return headers with auth token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    def fetch_products(self, category_name, limit=50):
        """Fetch products for a category"""
        if not self.token:
            self.authenticate()

        url = f"{self.base_url}/products"
        params = {
            "search": category_name,
            "limit": limit
        }

        try:
            response = requests.get(url, headers=self.get_headers(), params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get('products', [])
        except Exception as e:
            print(f"[!] Error fetching products for {category_name}: {e}")
            return []


def sync_products():
    """Main sync function"""
    app = create_app()

    with app.app_context():
        # Credentials from environment
        client_id = os.getenv('BOL_CLIENT_ID')
        client_secret = os.getenv('BOL_CLIENT_SECRET')

        if not client_id or not client_secret:
            print("[!] Missing Bol.com credentials. Set BOL_CLIENT_ID and BOL_CLIENT_SECRET")
            return

        # Initialize sync log
        sync_log = SyncLog(started_at=datetime.utcnow())
        db.session.add(sync_log)
        db.session.flush()

        print(f"[+] Starting sync... (Log ID: {sync_log.id})")

        # Categories to sync
        categories = [
            ('Wasmachines', 'wasmachines'),
            ('Drogers', 'drogers'),
            ('Wasdroogcombinaties', 'wasdroogcombinaties'),
            ('Koelkasten', 'koelkasten'),
            ('Vaatwassers', 'vaatwassers'),
            ('Magnetrons', 'magnetrons'),
            ('Ovens', 'ovens'),
        ]

        api = BolAPI(client_id, client_secret)

        total_synced = 0
        total_updated = 0

        for category_name, category_slug in categories:
            print(f"[*] Syncing {category_name}...")

            # Get category from DB
            category = Category.query.filter_by(slug=category_slug).first()
            if not category:
                print(f"[!] Category {category_name} not found in database")
                continue

            # Fetch products
            products = api.fetch_products(category_name, limit=50)

            for prod_data in products:
                try:
                    ean = prod_data.get('ean') or str(prod_data.get('id', ''))
                    if not ean:
                        continue

                    # Check if product exists
                    product = Product.query.filter_by(ean=ean).first()

                    # Prepare product data
                    price = float(prod_data.get('price', 0) or 0)
                    title = prod_data.get('title', 'Unknown')
                    image_url = prod_data.get('image', '')
                    bol_url = prod_data.get('url', f"https://www.bol.com/nl/p/{ean}/")

                    # Generate slug
                    slug = f"{title[:50].lower().replace(' ', '-')}-{ean}"

                    if product:
                        # Update existing
                        product.title = title
                        product.price = price
                        product.image_url = image_url
                        product.bol_url = bol_url
                        product.is_available = True
                        product.last_synced = datetime.utcnow()
                        total_updated += 1
                    else:
                        # Create new
                        product = Product(
                            ean=ean,
                            title=title,
                            price=price,
                            image_url=image_url,
                            bol_url=bol_url,
                            category_id=category.id,
                            slug=slug,
                            is_available=True,
                            last_synced=datetime.utcnow()
                        )
                        db.session.add(product)
                        total_synced += 1

                except Exception as e:
                    print(f"[!] Error processing product: {e}")
                    continue

            db.session.commit()
            print(f"[+] {category_name}: {total_synced + total_updated} products processed")

        # Update sync log
        sync_log.finished_at = datetime.utcnow()
        sync_log.products_synced = total_synced
        sync_log.products_updated = total_updated
        db.session.commit()

        print(f"[+] Sync complete!")
        print(f"    - New products: {total_synced}")
        print(f"    - Updated products: {total_updated}")


if __name__ == '__main__':
    sync_products()
