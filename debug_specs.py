#!/usr/bin/env python
"""
Eenmalig diagnosescript: print de RUWE 'specifications' die de Marketing
Catalog API v1 teruggeeft voor 1 echt gesynct product.

We weten dat product.specs leeg is voor echte producten (extract_specs()
in sync_products.py levert niets op), maar niet zeker waarom: mogelijk
klopt de veldnaam-aanname in extract_specs niet met wat v1 echt teruggeeft.
Dit script laat de ruwe JSON zien zodat extract_specs() precies op de
echte vorm afgestemd kan worden, in plaats van verder te gokken.

Verwijderen zodra het specs-probleem is opgelost.
"""

import os
import json
from app import create_app
from models import Product
from sync_products import BolAPI


def main():
    app = create_app()
    with app.app_context():
        product = Product.query.filter_by(is_example=False).first()
        if not product:
            print("Geen echt (niet-voorbeeld) product gevonden in de database.")
            return
        ean = product.ean
        print(f"Test met: {product.title} (EAN {ean})")

    client_id = os.getenv('BOL_CLIENT_ID')
    client_secret = os.getenv('BOL_CLIENT_SECRET')
    api = BolAPI(client_id, client_secret)

    if not api.authenticate():
        print("Authenticatie mislukt.")
        return

    data = api.fetch_product(ean)
    if data is None:
        print("fetch_product() gaf None terug (zie foutmelding hierboven).")
        return

    print()
    print("=== Alle top-level sleutels in de respons ===")
    print(list(data.keys()))

    print()
    print("=== Ruwe 'specificationGroups' ===")
    print(json.dumps(data.get('specificationGroups', 'GEEN specificationGroups-sleutel aanwezig'), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
