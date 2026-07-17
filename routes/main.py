import time

from flask import Blueprint, render_template, request, redirect, current_app
from models import Category, Product, Guide
from sqlalchemy import or_
from filter_helpers import compute_brand_facet, compute_spec_facets, parse_spec_filters

main_bp = Blueprint('main', __name__)

# Filteropties en meta-description per categorie veranderen alleen bij een
# sync, maar werden bij elk bezoek opnieuw berekend over álle producten in
# de categorie (alle specs-JSON parsen) — goed voor ~0,7s extra TTFB op de
# belangrijkste commerciële pagina's. Cache met korte TTL; gunicorn draait
# met 1 worker dus een procescache volstaat.
_FACET_CACHE = {}
_FACET_TTL = 15 * 60  # seconden


def _category_facets(category):
    nu = time.time()
    hit = _FACET_CACHE.get(category.id)
    if hit and nu - hit[0] < _FACET_TTL:
        return hit[1]
    producten = Product.query.filter_by(category_id=category.id,
                                        is_available=True).all()
    data = (compute_brand_facet(producten),
            compute_spec_facets(producten),
            _category_meta_description(category, producten))
    _FACET_CACHE[category.id] = (nu, data)
    return data


def _category_meta_description(category, products):
    """Unieke meta-description per categorie: aantal, merken en vanaf-prijs.

    De templates hadden één generieke tekst voor elke categorie; Google toont
    dan overal hetzelfde fragment. Concrete aantallen en merknamen maken het
    fragment onderscheidend en klikwaardiger.
    """
    count = len(products)
    # Merken ontdubbelen zonder hoofdlettergevoeligheid: de feeds leveren
    # hetzelfde merk in verschillende schrijfwijzen ("AEG" naast "Aeg"),
    # wat anders dubbel in de meta-description belandt.
    brands, seen = [], set()
    for p in products:
        key = (p.brand or '').strip().lower()
        if key and key not in seen:
            seen.add(key)
            brands.append(p.brand.strip())
        if len(brands) == 3:
            break
    prices = [p.lowest_price for p in products if p.lowest_price]
    parts = [f"Vergelijk {count} {category.name.lower()} op prijs en specificaties"]
    if brands:
        parts.append(f"van o.a. {', '.join(brands)}")
    if prices:
        parts.append(f"al vanaf € {min(prices):.0f}".replace('.', ','))
    tekst = ' '.join(parts) + ". Vind de laagste prijs bij Bol, Coolblue en MediaMarkt."
    return tekst[:160]


def _category_structured_data(category, page_products):
    """ItemList + BreadcrumbList JSON-LD voor een categoriepagina."""
    site_url = current_app.config['SITE_URL']
    item_list = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': category.name,
        'itemListElement': [{
            '@type': 'ListItem',
            'position': i,
            'url': f"{site_url}/product/{p.slug}",
        } for i, p in enumerate(page_products, 1)],
    }
    breadcrumbs = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home',
             'item': f"{site_url}/"},
            {'@type': 'ListItem', 'position': 2, 'name': category.name},
        ],
    }
    return [item_list, breadcrumbs]


@main_bp.route('/api/sync-status')
def sync_status():
    """Diagnose-overzicht van de syncs (alleen-lezen, geen gevoelige data).

    Railway-logs zijn vanuit de ontwikkelomgeving niet bereikbaar; dit
    endpoint maakt zichtbaar of de scheduler jobs heeft ingepland, wanneer
    de laatste syncs draaiden en of de prijshistorie zich vult. Staat in
    robots.txt onder Disallow /api/.
    """
    from flask import jsonify
    from models import db, Offer, PriceHistory, SyncLog

    jobs = []
    try:
        from scheduler import scheduler
        jobs = [{'naam': j.name, 'volgende_run': str(j.next_run_time)}
                for j in scheduler.get_jobs()]
    except Exception as e:
        jobs = [{'fout': str(e)}]

    logs = (SyncLog.query.order_by(SyncLog.started_at.desc()).limit(5).all())
    laatste_sync_per_winkel = {
        r: str(db.session.query(db.func.max(Offer.last_synced))
               .filter(Offer.retailer == r).scalar())
        for r in ('bol', 'mediamarkt', 'coolblue')
    }
    import os
    return jsonify({
        'omgeving': {
            'flask_env': os.getenv('FLASK_ENV'),
            'railway_environment': os.getenv('RAILWAY_ENVIRONMENT'),
        },
        'scheduler_jobs': jobs,
        'laatste_synclogs': [{
            'gestart': str(l.started_at),
            'klaar': str(l.finished_at),
            'synced': l.products_synced,
            'updated': l.products_updated,
            'fouten': (l.errors or '')[:300],
        } for l in logs],
        'laatste_sync_per_winkel': laatste_sync_per_winkel,
        'prijshistorie_rijen': PriceHistory.query.count(),
    })


@main_bp.route('/set-language/<lang>')
def set_language(lang):
    response = redirect(request.referrer or '/')
    if lang in ('nl', 'en'):
        response.set_cookie('lang', lang, max_age=60 * 60 * 24 * 365)
    return response


def _guide_video_id(guide):
    """YouTube-video-ID uit de gidstekst, of None als er geen video in zit.

    Gebruikt voor de thumbnail + 'Met video'-badge in het gidsenoverzicht:
    gidsen met video moeten daar opvallen tussen de tekstgidsen.
    """
    import re
    m = re.search(r'youtube(?:-nocookie)?\.com/embed/([\w-]+)', guide.content or '')
    return m.group(1) if m else None


@main_bp.route('/gidsen')
def guides():
    all_guides = Guide.query.filter_by(post_type='guide').order_by(Guide.created_at.desc()).all()
    video_ids = {g.id: _guide_video_id(g) for g in all_guides}
    return render_template('guides.html', guides=all_guides, video_ids=video_ids)


@main_bp.route('/gidsen/<slug>')
def guide_detail(slug):
    guide = Guide.query.filter_by(slug=slug).first_or_404()
    from guide_cards import render_guide_content
    return render_template('guide_detail.html', guide=guide,
                           rendered_content=render_guide_content(guide.content))


@main_bp.route('/blog')
def blog():
    posts = Guide.query.filter_by(post_type='blog').order_by(Guide.created_at.desc()).all()
    return render_template('blog.html', posts=posts)


@main_bp.route('/blog/<slug>')
def blog_detail(slug):
    post = Guide.query.filter_by(slug=slug, post_type='blog').first_or_404()
    return render_template('guide_detail.html', guide=post)


@main_bp.route('/')
def index():
    categories = Category.query.filter_by(parent_id=None).all()

    # 1 product per categorie (goedkoopste, sluit aan bij "laagste prijzen"),
    # zodat de homepage de breedte van de site laat zien i.p.v. willekeurig
    # meerdere producten uit dezelfde categorie.
    featured_products = []
    for cat in categories[:5]:
        cheapest = (Product.query.filter_by(category_id=cat.id, is_available=True)
                    .order_by(Product.price.asc()).first())
        if cheapest:
            featured_products.append(cheapest)

    latest_blog_posts = Guide.query.filter_by(post_type='blog').order_by(Guide.created_at.desc()).limit(3).all()

    # Geen aparte categorie-afbeeldingen in het model; gebruik de foto van
    # een echt product uit die categorie als representatief plaatje voor
    # de carousel op de homepage.
    category_cards = []
    for cat in categories:
        sample_product = Product.query.filter_by(category_id=cat.id, is_available=True).first()
        category_cards.append({
            'category': cat,
            'image_url': sample_product.image_url if sample_product else None,
        })

    return render_template(
        'index.html',
        featured_products=featured_products,
        category_cards=category_cards,
        latest_blog_posts=latest_blog_posts,
    )


@main_bp.route('/category/<slug>')
def category(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)

    brand_filter = request.args.getlist('brand')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 10000, type=float)
    selected_specs = parse_spec_filters(request.args.getlist('spec'))

    # Filteropties + meta-description uit de cache (zie _category_facets)
    brand_facet, spec_facets, meta_description = _category_facets(category)

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
    category_guide = Guide.query.filter_by(category_id=category.id, post_type='guide').first()

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
        category_guide=category_guide,
        meta_description=meta_description,
        structured_data=_category_structured_data(category, products.items),
    )
