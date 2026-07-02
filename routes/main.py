from flask import Blueprint, render_template, request, redirect
from models import Category, Product
from sqlalchemy import or_
from filter_helpers import compute_brand_facet, compute_spec_facets, parse_spec_filters

main_bp = Blueprint('main', __name__)


@main_bp.route('/set-language/<lang>')
def set_language(lang):
    response = redirect(request.referrer or '/')
    if lang in ('nl', 'en'):
        response.set_cookie('lang', lang, max_age=60 * 60 * 24 * 365)
    return response


@main_bp.route('/')
def index():
    featured_products = Product.query.filter_by(is_available=True).limit(12).all()
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('index.html', featured_products=featured_products, categories=categories)


@main_bp.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)

    brand_filter = request.args.getlist('brand')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 10000, type=float)
    selected_specs = parse_spec_filters(request.args.getlist('spec'))

    # Unfiltered set, used to compute facet options + counts (same approach
    # as the existing available_brands in routes/products.py)
    all_category_products = Product.query.filter_by(category_id=category.id, is_available=True).all()
    brand_facet = compute_brand_facet(all_category_products)
    spec_facets = compute_spec_facets(all_category_products)

    q = Product.query.filter_by(category_id=category.id, is_available=True)
    q = q.filter(Product.price.between(min_price, max_price))

    if brand_filter:
        q = q.filter(or_(*[Product.brand.ilike(b) for b in brand_filter]))

    for key, values in selected_specs.items():
        q = q.filter(Product.specs[key].as_string().in_(values))

    sort = request.args.get('sort', '')
    if sort == 'price_asc':
        q = q.order_by(Product.price.asc())
    elif sort == 'price_desc':
        q = q.order_by(Product.price.desc())

    products = q.paginate(page=page, per_page=24)

    return render_template(
        'category.html',
        category=category,
        products=products.items,
        pagination=products,
        brand_facet=brand_facet,
        spec_facets=spec_facets,
        selected_brands=brand_filter,
        selected_specs=selected_specs,
        min_price=min_price,
        max_price=max_price,
        selected_sort=sort,
    )
