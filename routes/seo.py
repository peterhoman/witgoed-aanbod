"""
SEO routes (sitemap, robots.txt)
"""

from flask import Blueprint, render_template_string, current_app
from models import Product, Category
from datetime import datetime

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml"""
    products = Product.query.filter_by(is_available=True).all()
    categories = Category.query.filter_by(parent_id=None).all()

    sitemap_entries = []

    # Homepage
    sitemap_entries.append({
        'loc': f"{current_app.config['SITE_URL']}/",
        'lastmod': datetime.utcnow().isoformat(),
        'priority': '1.0'
    })

    # Category pages
    for category in categories:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}",
            'lastmod': datetime.utcnow().isoformat(),
            'priority': '0.8'
        })

    # Product pages
    for product in products:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/product/{product.slug}",
            'lastmod': product.updated_at.isoformat() if product.updated_at else datetime.utcnow().isoformat(),
            'priority': '0.6'
        })

    # Legal pages
    legal_pages = ['privacy', 'disclaimer', 'cookies', 'voorwaarden', 'contact']
    for page in legal_pages:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/{page}",
            'lastmod': datetime.utcnow().isoformat(),
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
