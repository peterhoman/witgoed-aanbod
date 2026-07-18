"""
SEO routes (sitemap, robots.txt)
"""

from flask import Blueprint, render_template_string, current_app
from models import Product, Category, Guide, utcnow
from filter_helpers import compute_brand_facet, compute_spec_facets, compute_global_brand_index, slugify
from routes.main import SUBCATEGORY_SPECS

seo_bp = Blueprint('seo', __name__)

def _lastmod(dt=None):
    """Datum voor <lastmod> als YYYY-MM-DD.

    utcnow().isoformat() gaf een tijdstip zonder tijdzone mee; Search Console
    keurde daardoor elke URL af met "Ongeldige datum". Alleen de datum is
    volgens het sitemap-protocol altijd geldig, en preciezer heeft Google
    hem niet nodig.
    """
    return (dt or utcnow()).strftime('%Y-%m-%d')


@seo_bp.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml"""
    products = Product.query.filter_by(is_available=True).all()
    categories = Category.query.filter_by(parent_id=None).all()

    sitemap_entries = []

    # Homepage
    sitemap_entries.append({
        'loc': f"{current_app.config['SITE_URL']}/",
        'lastmod': _lastmod(),
        'priority': '1.0'
    })

    # Merken A-Z + per-merk-pagina (over alle categorieën heen)
    sitemap_entries.append({
        'loc': f"{current_app.config['SITE_URL']}/merken",
        'lastmod': _lastmod(),
        'priority': '0.6'
    })
    for merk in compute_global_brand_index((p.brand, 1) for p in products):
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/merk/{merk['slug']}",
            'lastmod': _lastmod(),
            'priority': '0.5'
        })

    # Category pages + hun merk-/energielabel-facetpagina's (long-tail SEO;
    # zelfde live-databerekening als de categoriepagina zelf, dus een
    # facetpagina staat hier alleen als hij ook echt producten heeft).
    for category in categories:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}",
            'lastmod': _lastmod(),
            'priority': '0.8'
        })
        cat_products = [p for p in products if p.category_id == category.id]
        for brand in compute_brand_facet(cat_products):
            sitemap_entries.append({
                'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}/merk/{slugify(brand['value'])}",
                'lastmod': _lastmod(),
                'priority': '0.5'
            })
        for facet in compute_spec_facets(cat_products):
            if 'energielabel' not in facet['key'].lower():
                continue
            letters_gezien = set()
            for option in facet['options']:
                letter = option['value'].strip()[:1].lower()
                if letter and letter not in letters_gezien:
                    letters_gezien.add(letter)
                    sitemap_entries.append({
                        'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}/energielabel/{letter}",
                        'lastmod': _lastmod(),
                        'priority': '0.5'
                    })
        # Subcategorie-pagina's (voorlader/bovenlader, warmtepomp/condens):
        # ongelimiteerd berekenen, want dit zijn geen priority-specs en
        # kunnen buiten de standaard top-6 vallen.
        subtype_key = SUBCATEGORY_SPECS.get(category.slug)
        if subtype_key:
            for facet in compute_spec_facets(cat_products, max_filters=999, max_options=999):
                if facet['key'] != subtype_key:
                    continue
                for option in facet['options']:
                    sitemap_entries.append({
                        'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}/type/{slugify(option['value'])}",
                        'lastmod': _lastmod(),
                        'priority': '0.5'
                    })

    # Product pages
    for product in products:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/product/{product.slug}",
            'lastmod': _lastmod(product.updated_at),
            'priority': '0.6'
        })

    # Guides
    guides = Guide.query.filter_by(post_type='guide').all()
    for guide in guides:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/gidsen/{guide.slug}",
            'lastmod': _lastmod(guide.created_at),
            'priority': '0.7'
        })

    # Blog posts
    blog_posts = Guide.query.filter_by(post_type='blog').all()
    for post in blog_posts:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/blog/{post.slug}",
            'lastmod': _lastmod(post.created_at),
            'priority': '0.6'
        })

    # Legal pages
    legal_pages = ['over-ons', 'privacy', 'disclaimer', 'cookies', 'voorwaarden', 'contact']
    for page in legal_pages:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/{page}",
            'lastmod': _lastmod(),
            'priority': '0.5'
        })

    sitemap_xml = render_template_string('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for entry in entries %}
    <url>
        <loc>{{ entry.loc }}</loc>
        <lastmod>{{ entry.lastmod }}</lastmod>
        <priority>{{ entry.priority }}</priority>
    </url>
{% endfor %}
</urlset>''', entries=sitemap_entries)

    return sitemap_xml, 200, {'Content-Type': 'application/xml'}


@seo_bp.route('/robots.txt')
def robots():
    """Generate robots.txt"""
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: {current_app.config['SITE_URL']}/sitemap.xml

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /
"""
    return robots_txt, 200, {'Content-Type': 'text/plain'}
