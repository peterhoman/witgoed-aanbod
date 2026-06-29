from flask import Blueprint, render_template, request, jsonify
from models import Product, Category
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)


@products_bp.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_available=True).first_or_404()

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_available == True
    ).limit(6).all()

    return render_template('product.html', product=product, related_products=related_products)


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

    return render_template('search.html', results=results.items, pagination=results,
                         query=query, categories=categories, selected_category=category_filter,
                         available_brands=available_brands, selected_brands=brand_filter)


@products_bp.route('/api/categories')
def api_categories():
    categories = Category.query.filter_by(parent_id=None).all()
    return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug} for c in categories])
