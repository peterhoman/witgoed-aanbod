"""
Demo: Add sample products to database
For testing the affiliate site without API
"""

from app import create_app
from models import db, Product, Category

DEMO_PRODUCTS = [
    {
        'ean': '8718025010041',
        'title': 'Samsung WW90T534DAW Wasmachine 9kg',
        'brand': 'Samsung',
        'price': 459.00,
        'category_slug': 'wasmachines',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/8718025010041_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/samsung-ww90t534daw/9200000087654321/',
    },
    {
        'ean': '4242003933799',
        'title': 'Miele WCA 020 WCS Wasmachine 9kg',
        'brand': 'Miele',
        'price': 899.00,
        'category_slug': 'wasmachines',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/4242003933799_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/miele-wca-020-wcs/9200000098765432/',
    },
    {
        'ean': '8699751000036',
        'title': 'Arçelik 7081 Wasmachine 7kg',
        'brand': 'Arçelik',
        'price': 279.99,
        'category_slug': 'wasmachines',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/8699751000036_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/arccelik-7081/9200000054321098/',
    },
    {
        'ean': '8021144620450',
        'title': 'Indesit MTWE 91483 WK EU Wasmachine 9kg',
        'brand': 'Indesit',
        'price': 349.00,
        'category_slug': 'wasmachines',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/8021144620450_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/indesit-mtwe-91483-wk-eu/9200000076543210/',
    },
    {
        'ean': '8806084419645',
        'title': 'LG DLHC1455W Wasdroger 8kg',
        'brand': 'LG',
        'price': 799.00,
        'category_slug': 'wasdroogcombinaties',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/8806084419645_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/lg-dlhc1455w/9200000098765111/',
    },
    {
        'ean': '5412210052000',
        'title': 'Beko DTLCE70051W Droger 7kg',
        'brand': 'Beko',
        'price': 249.99,
        'category_slug': 'drogers',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/5412210052000_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/beko-dtlce70051w/9200000076543222/',
    },
    {
        'ean': '8592181073305',
        'title': 'Gorenje RK6192LW Koelkast 192L',
        'brand': 'Gorenje',
        'price': 329.00,
        'category_slug': 'koelkasten',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/8592181073305_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/gorenje-rk6192lw/9200000087654222/',
    },
    {
        'ean': '4242003920006',
        'title': 'Miele G7100 SC Vaatwasser 14 couvert',
        'brand': 'Miele',
        'price': 1199.00,
        'category_slug': 'vaatwassers',
        'image_url': 'https://images.bol.com/images/shared/pdpImages/500x500/4242003920006_1.jpg',
        'bol_url': 'https://www.bol.com/nl/p/miele-g7100-sc/9200000099876543/',
    },
]

def add_demo_products():
    """Add demo products to database"""
    app = create_app()

    with app.app_context():
        print("[+] Adding demo products...")

        for prod_data in DEMO_PRODUCTS:
            ean = prod_data['ean']

            # Check if exists
            product = Product.query.filter_by(ean=ean).first()
            if product:
                print(f"[*] Product {ean} already exists, skipping")
                continue

            # Get category
            category = Category.query.filter_by(slug=prod_data['category_slug']).first()
            if not category:
                print(f"[!] Category {prod_data['category_slug']} not found")
                continue

            # Create product
            slug = f"{prod_data['title'][:50].lower().replace(' ', '-')}-{ean}"

            product = Product(
                ean=ean,
                title=prod_data['title'],
                brand=prod_data['brand'],
                price=prod_data['price'],
                image_url=prod_data['image_url'],
                bol_url=prod_data['bol_url'],
                category_id=category.id,
                slug=slug,
                is_available=True,
                description=f"High-quality {prod_data['brand']} {prod_data['title'].lower()}. Available on Bol.com.",
                ai_meta_description=f"Buy {prod_data['brand']} {prod_data['title']} - €{prod_data['price']:.2f} on Bol.com"
            )

            db.session.add(product)
            print(f"[+] Added: {prod_data['title']} (€{prod_data['price']})")

        db.session.commit()
        print("[+] Demo products added successfully!")


if __name__ == '__main__':
    add_demo_products()
