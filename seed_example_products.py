#!/usr/bin/env python
"""
Seed the database with a small set of real, hand-picked example products.

Purpose: give the site genuine, non-empty content while waiting for
Bol.com affiliate API approval (which is required before automatic
syncing can start). These are clearly flagged with is_example=True and
shown with a "Voorbeeldproduct" badge on the site - see templates.

Product info (title/brand/price/image) is sourced from real, currently
listed Bol.com products. Descriptions below are written independently,
not copied from Bol.com's own marketing copy. Links point to a Bol.com
search results page for that exact product (not an affiliate link -
we don't have affiliate tracking access yet).

Safe to re-run: existing example products (matching the EXAMPLE-prefixed
EAN) are replaced rather than duplicated.
"""

from urllib.parse import quote_plus
from app import create_app
from models import db, Category, Offer, PriceAlert, PriceHistory, Product

WASMACHINES = [
    {
        'ean': 'EXAMPLE0000001',
        'title': 'Hisense WF5I1045BBQ Wasmachine',
        'brand': 'Hisense',
        'price': 499.00,
        'image_url': 'https://media.s-bol.com/jmGgWnD7O1ol/g5pAGBD/550x771.jpg',
        'description': 'Ruime wasmachine met een vulgewicht van 10,5 kg, geschikt voor grote gezinnen. Centrifugeert op 1400 toeren per minuut en heeft energielabel A.',
        'specs': {'Vulgewicht': '10.5 kg', 'Toerental': '1400', 'Energielabel': 'A', 'Type': 'Voorlader'},
    },
    {
        'ean': 'EXAMPLE0000002',
        'title': 'AEG LR8686UC4 8000 PowerCare UniversalDose',
        'brand': 'AEG',
        'price': 749.00,
        'image_url': 'https://media.s-bol.com/RzmOqlGApGEY/E9Oq4og/550x771.jpg',
        'description': 'Wasmachine uit AEG\'s 8000-serie met automatische wasmiddeldosering. Vulgewicht van 8 kg en energielabel A, tot 40% zuiniger dan vereist.',
        'specs': {'Vulgewicht': '8 kg', 'Energielabel': 'A (-40%)', 'Type': 'Voorlader', 'Extra': 'Automatische wasmiddeldosering (UniversalDose)'},
    },
    {
        'ean': 'EXAMPLE0000003',
        'title': 'CHiQ CW07123863AX Wasmachine',
        'brand': 'CHiQ',
        'price': 316.66,
        'image_url': 'https://media.s-bol.com/NqpWOWjPrLw6/Ro5O4Az/550x741.jpg',
        'description': 'Compacte en voordelige wasmachine met een vulgewicht van 7 kg, geschikt voor kleinere huishoudens. Energielabel A.',
        'specs': {'Vulgewicht': '7 kg', 'Energielabel': 'A', 'Type': 'Voorlader', 'Geluidsniveau': '69 dB', 'Extra': 'Beladingssensor, AI Smart-functie'},
    },
    {
        'ean': 'EXAMPLE0000004',
        'title': 'Samsung WW90CGC04AAHEN Ecobubble 5000',
        'brand': 'Samsung',
        'price': 499.00,
        'image_url': 'https://media.s-bol.com/gGzvREnYzjDY/qgRYWG/550x770.jpg',
        'description': 'Wasmachine uit Samsung\'s Ecobubble-serie, wast op lage temperaturen dankzij bubbeltechnologie. Vulgewicht 9 kg, energielabel A.',
        'specs': {'Vulgewicht': '9 kg', 'Energielabel': 'A (-10%)', 'Type': 'Voorlader', 'Geluidsniveau': '72 dB', 'Extra': 'Beladingssensor, Ecobubble-technologie'},
    },
    {
        'ean': 'EXAMPLE0000005',
        'title': 'Inventum VWM8010B Wasmachine',
        'brand': 'Inventum',
        'price': 419.00,
        'image_url': 'https://media.s-bol.com/7RMA0gpn0xKQ/k54QL9Y/550x766.jpg',
        'description': 'Betaalbare wasmachine van Inventum met een vulgewicht van 8 kg en een centrifugesnelheid van 1400 toeren per minuut.',
        'specs': {'Vulgewicht': '8 kg', 'Toerental': '1400', 'Energielabel': 'A-10%', 'Type': 'Voorlader'},
    },
    {
        'ean': 'EXAMPLE0000006',
        'title': 'CHiQ CFL100-14586IM3XA Space Pro',
        'brand': 'CHiQ',
        'price': 384.00,
        'image_url': 'https://media.s-bol.com/JmlEpPxAv3vo/Ro5O6gR/550x745.jpg',
        'description': 'Ruime wasmachine met 10 kg vulgewicht en 1400 toeren centrifugesnelheid, geschikt voor grotere wasladingen.',
        'specs': {'Vulgewicht': '10 kg', 'Toerental': '1400', 'Energielabel': 'A-30%', 'Type': 'Voorlader', 'Geluidsniveau': '76 dB', 'Extra': 'Beladingssensor, stoomwassen, Quick Wash'},
    },
]

KOELKASTEN = [
    {
        'ean': 'EXAMPLE0000101',
        'title': 'Bosch KGN492IAF Serie 4 Koel-vriescombinatie',
        'brand': 'Bosch',
        'price': 1238.00,
        'image_url': 'https://media.s-bol.com/KNJrQqkGlZpG/rkWKDBw/286x840.jpg',
        'description': 'Ruime koel-vriescombinatie van 203 cm hoog met No Frost-techniek, zodat er nooit meer ontdooid hoeft te worden. Inhoud 440 liter, energielabel A.',
        'specs': {'Inhoud': '440 liter', 'Type': 'Koel-vriescombinatie', 'Energielabel': 'A', 'Afmetingen (h x b)': '203 x 70 cm', 'Ontdooisysteem': 'No Frost'},
    },
    {
        'ean': 'EXAMPLE0000102',
        'title': 'TZS First Austria Mini Koelkast',
        'brand': 'TZS FIRST AUSTRIA',
        'price': 159.95,
        'image_url': 'https://media.s-bol.com/pDonnGL9x66V/VOkAEnz/550x646.jpg',
        'description': 'Compacte tafelmodel-koelkast, ideaal voor een studentenkamer of als bijzet-koelkast. Inhoud 30 liter en met 22 dB erg stil in gebruik.',
        'specs': {'Inhoud': '30 liter', 'Type': 'Tafelmodel', 'Afmetingen (h)': '47 cm', 'Geluidsniveau': '22 dB'},
    },
    {
        'ean': 'EXAMPLE0000103',
        'title': 'CHiQ FBM157L42 Koel-vriescombinatie',
        'brand': 'CHiQ',
        'price': 249.00,
        'image_url': 'https://media.s-bol.com/qqB4g6L0zpq0/1wkMKq0/282x840.jpg',
        'description': 'Compacte koel-vriescombinatie met een inhoud van 157 liter, geschikt voor kleinere keukens. Low Frost-techniek beperkt ijsvorming.',
        'specs': {'Inhoud': '157 liter', 'Type': 'Koel-vriescombinatie', 'Energielabel': 'E', 'Afmetingen (h)': '144 cm', 'Ontdooisysteem': 'Low Frost'},
    },
    {
        'ean': 'EXAMPLE0000104',
        'title': 'CHiQ FBM228NE4DE Koel-vriescombinatie',
        'brand': 'CHiQ',
        'price': 384.00,
        'image_url': 'https://media.s-bol.com/NgwyO8O2qqEz/qxWoro3/279x840.jpg',
        'description': 'Koel-vriescombinatie met waterdispenser en No Frost-techniek. Inhoud van 231 liter, geschikt voor middelgrote huishoudens.',
        'specs': {'Inhoud': '231 liter', 'Type': 'Koel-vriescombinatie', 'Energielabel': 'E', 'Afmetingen (h)': '170 cm', 'Ontdooisysteem': 'No Frost', 'Extra': 'Waterdispenser'},
    },
]

CATEGORY_PRODUCTS = {
    'wasmachines': WASMACHINES,
    'koelkasten': KOELKASTEN,
}


def bol_search_url(title):
    """Non-affiliate fallback link: a Bol.com search for this exact product title."""
    return f"https://www.bol.com/nl/nl/s/?searchtext={quote_plus(title)}"


def slugify(title, ean):
    return f"{title[:50].lower().replace(' ', '-').replace('/', '-')}-{ean.lower()}"


def _verwijder_voorbeeldproducten():
    """Verwijder eerder gezaaide voorbeeldproducten, mét alles wat eraan hangt.

    Dit stond hier als Product.query.filter_by(is_example=True).delete(). Zo'n
    bulk-delete slaat de ORM-cascade over, dus de aanbiedingen en de
    prijshistorie van die producten bleven staan als weesrijen. In de
    ontwikkeldatabase liep dat op tot 141 aanbiedingen bij 10 producten.

    Dat is niet alleen rommel. SQLite hergebruikt de id's van verwijderde
    rijen, dus een nieuw product krijgt het nummer van een oud en erft diens
    aanbiedingen -- of het aanmaken loopt vast op de unieke sleutel
    (product_id, retailer). Dat laatste gebeurde bij het testen van de
    prijsverloop-grafiek.

    Expliciet verwijderen in plaats van op de cascade vertrouwen: PriceHistory
    heeft alleen een ondelete='CASCADE' op databaseniveau, en SQLite handhaaft
    dat alleen met PRAGMA foreign_keys aan. Die staat standaard uit.
    """
    ids = [rij[0] for rij in db.session.query(Product.id).filter_by(is_example=True).all()]
    if ids:
        PriceAlert.query.filter(PriceAlert.product_id.in_(ids)).delete(synchronize_session=False)
        PriceHistory.query.filter(PriceHistory.product_id.in_(ids)).delete(synchronize_session=False)
        Offer.query.filter(Offer.product_id.in_(ids)).delete(synchronize_session=False)
        Product.query.filter(Product.id.in_(ids)).delete(synchronize_session=False)
    return len(ids)


def _ruim_weesrijen_op():
    """Aanbiedingen en prijshistorie die naar een verdwenen product wijzen.

    Opruimen van wat eerdere runs hebben laten liggen; met de functie hierboven
    ontstaan er geen nieuwe meer.
    """
    bestaande = db.session.query(Product.id)
    weg = 0
    for model in (Offer, PriceHistory):
        weg += model.query.filter(~model.product_id.in_(bestaande)).delete(
            synchronize_session=False)
    return weg


def seed():
    app = create_app()

    with app.app_context():
        # Remove any previously seeded example products so this script is safely re-runnable
        verwijderd = _verwijder_voorbeeldproducten()
        wezen = _ruim_weesrijen_op()
        db.session.commit()
        if verwijderd or wezen:
            print(f"[i] {verwijderd} oude voorbeeldproducten verwijderd, "
                  f"{wezen} weesrijen opgeruimd")

        total = 0
        for category_slug, items in CATEGORY_PRODUCTS.items():
            category = Category.query.filter_by(slug=category_slug).first()
            if not category:
                print(f"[!] Category '{category_slug}' not found, skipping its example products")
                continue

            for item in items:
                product = Product(
                    ean=item['ean'],
                    title=item['title'],
                    brand=item['brand'],
                    price=item['price'],
                    image_url=item['image_url'],
                    bol_url=bol_search_url(item['title']),
                    description=item['description'],
                    specs=item.get('specs', {}),
                    category_id=category.id,
                    slug=slugify(item['title'], item['ean']),
                    retailer='bol',
                    is_available=True,
                    is_example=True,
                )
                db.session.add(product)
                total += 1
                print(f"[+] Added example product: {item['title']}")

        db.session.commit()
        print(f"\n[+] Seeded {total} example products")


if __name__ == '__main__':
    seed()
