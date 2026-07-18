from datetime import timedelta

from flask import Blueprint, render_template, request, jsonify, current_app
from models import Product, Category, Guide
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)


def _product_structured_data(product):
    """Schema.org Product + AggregateOffer voor rich results in Google.

    De EAN gaat mee als gtin13: daarmee kan Google het apparaat koppelen aan
    zijn productkennisgraaf en prijzen/winkels in de zoekresultaten tonen —
    voor een prijsvergelijker de belangrijkste SEO-bouwsteen.
    """
    site_url = current_app.config['SITE_URL']
    offers = product.available_offers

    data = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': product.title,
        'url': f"{site_url}/product/{product.slug}",
    }
    if product.image_url:
        data['image'] = product.image_url
    if product.brand:
        data['brand'] = {'@type': 'Brand', 'name': product.brand}
    ean = (product.ean or '').strip()
    if len(ean) == 13 and ean.isdigit():
        data['gtin13'] = ean
    description = product.ai_description or product.description
    if description:
        data['description'] = description[:500]
    if product.category:
        data['category'] = product.category.name

    if offers:
        prices = [o.price for o in offers]
        data['offers'] = {
            '@type': 'AggregateOffer',
            'priceCurrency': 'EUR',
            'lowPrice': min(prices),
            'highPrice': max(prices),
            'offerCount': len(offers),
            'offers': [{
                '@type': 'Offer',
                'price': o.price,
                'priceCurrency': 'EUR',
                'availability': 'https://schema.org/InStock',
                'url': o.link,
                'seller': {'@type': 'Organization', 'name': o.retailer_name},
                # We syncen elke ~12u; een prijs die net gecontroleerd is
                # blijft dus ruim binnen 24u geldig. Voorkomt dat Google een
                # stilzwijgend verouderde prijs als "definitief" behandelt.
                'priceValidUntil': ((o.last_synced or product.last_synced)
                                    + timedelta(hours=24)).strftime('%Y-%m-%d'),
            } for o in offers],
        }

    breadcrumbs = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home',
             'item': f"{site_url}/"},
            {'@type': 'ListItem', 'position': 2, 'name': product.category.name,
             'item': f"{site_url}/category/{product.category.slug}"},
            {'@type': 'ListItem', 'position': 3, 'name': product.title},
        ],
    }
    return [data, breadcrumbs]


@products_bp.route('/product/<slug>')
def product_detail(slug):
    # Ook niet-leverbare producten tonen (met "tijdelijk niet leverbaar"):
    # gidsen en YouTube-video's linken hierheen, en een 404 breekt die links
    # terwijl het apparaat vaak gewoon terugkomt in de winkel-feeds.
    product = Product.query.filter_by(slug=slug).first_or_404()

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_available == True
    ).limit(6).all()

    # Koopgidsen en blogartikelen uit dezelfde categorie: elke productpagina
    # linkt zo naar de adviescontent (interne links voor SEO + hulp bij kiezen).
    category_guides = (Guide.query
                       .filter_by(category_id=product.category_id)
                       .order_by(Guide.post_type.desc(), Guide.created_at.desc())
                       .limit(5).all())

    from price_chart import build_price_history
    from energy_costs import bereken_energiekosten
    return render_template('product.html', product=product,
                           related_products=related_products,
                           category_guides=category_guides,
                           structured_data=_product_structured_data(product),
                           price_history=build_price_history(product),
                           energiekosten=bereken_energiekosten(product))


@products_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 10000, type=float)
    brand_filter = request.args.getlist('brand')
    page = request.args.get('page', 1, type=int)

    q = Product.query.filter(Product.is_available == True)

    if query:
        q = q.filter(
            or_(
                Product.title.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%'),
                Product.brand.ilike(f'%{query}%'),
                Product.ean.ilike(f'%{query}%')
            )
        )

    if category_filter:
        q = q.filter(Product.category_id == category_filter)

    q = q.filter(Product.price.between(min_price, max_price))

    if brand_filter:
        q = q.filter(or_(*[Product.brand.ilike(b) for b in brand_filter]))

    results = q.paginate(page=page, per_page=24)
    categories = Category.query.filter_by(parent_id=None).all()

    available_brands = sorted(set(p.brand for p in Product.query.filter(Product.is_available == True).all() if p.brand))

    from routes.main import _pros_cons_by_ean
    return render_template('search.html', results=results.items, pagination=results,
                         query=query, categories=categories, selected_category=category_filter,
                         available_brands=available_brands, selected_brands=brand_filter,
                         min_price=min_price, max_price=max_price,
                         pros_cons_by_ean=_pros_cons_by_ean())


@products_bp.route('/vergelijk')
def compare():
    ids_param = request.args.get('ids', '')
    ids = []
    for raw_id in ids_param.split(','):
        raw_id = raw_id.strip()
        if raw_id.isdigit():
            product_id = int(raw_id)
            if product_id not in ids:
                ids.append(product_id)
    ids = ids[:3]

    products = []
    if ids:
        found = Product.query.filter(Product.id.in_(ids)).all()
        by_id = {p.id: p for p in found}
        products = [by_id[i] for i in ids if i in by_id]

    spec_keys = []
    for product in products:
        for key in (product.specs or {}).keys():
            if key not in spec_keys:
                spec_keys.append(key)

    return render_template('compare.html', products=products, spec_keys=spec_keys)


@products_bp.route('/verlanglijst')
def wishlist():
    # Zelfde opzet als /vergelijk: de lijst zelf staat alleen lokaal bij de
    # bezoeker (localStorage, geen account); deze pagina zoekt op basis van
    # de ID's in de URL de actuele productgegevens op, zodat prijs en foto
    # altijd live zijn i.p.v. de (mogelijk verouderde) waarde uit de browser.
    ids_param = request.args.get('ids', '')
    ids = []
    for raw_id in ids_param.split(','):
        raw_id = raw_id.strip()
        if raw_id.isdigit():
            product_id = int(raw_id)
            if product_id not in ids:
                ids.append(product_id)

    products = []
    if ids:
        found = Product.query.filter(Product.id.in_(ids)).all()
        by_id = {p.id: p for p in found}
        products = [by_id[i] for i in ids if i in by_id]

    return render_template('wishlist.html', products=products)


@products_bp.route('/api/categories')
def api_categories():
    categories = Category.query.filter_by(parent_id=None).all()
    return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug} for c in categories])
