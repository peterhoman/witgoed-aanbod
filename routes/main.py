from flask import Blueprint, render_template, request
from models import Category, Product

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    featured_products = Product.query.filter_by(is_available=True).limit(12).all()
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('index.html', featured_products=featured_products, categories=categories)


@main_bp.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)

    products = Product.query.filter_by(category_id=category.id, is_available=True).paginate(page=page, per_page=24)

    return render_template('category.html', category=category, products=products.items, pagination=products)
