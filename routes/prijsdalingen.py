"""
Prijsdalingenpagina's: /aanbiedingen en /aanbiedingen/<categorie>.

Zie prijsdalingen.py voor het waarom en de spelregels. De URL heet
"aanbiedingen" omdat dat het woord is waarop gezocht wordt (Google Trends,
16 september 2026: "wasmachine aanbieding", "droger aanbieding"); de
inhoud zijn uitsluitend gemeten prijsdalingen, geen winkelacties.
"""

from flask import Blueprint, render_template, abort, current_app

from models import Category
import prijsdalingen

prijsdalingen_bp = Blueprint('prijsdalingen', __name__)


def _structured_data(category, lijst):
    """ItemList met de apparaten, zodat Google de lijst als lijst leest."""
    site = current_app.config['SITE_URL']
    return {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': f"Prijsdalingen {category.name.lower()} deze week",
        'numberOfItems': len(lijst),
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': i + 1,
                'url': f"{site}/product/{d['product'].slug}",
                'name': d['product'].title,
            }
            for i, d in enumerate(lijst[:50])
        ],
    }


@prijsdalingen_bp.route('/aanbiedingen')
def overzicht():
    rijen = prijsdalingen.overzicht()
    totaal = sum(n for _, n, _ in rijen)
    return render_template(
        'prijsdalingen_overzicht.html',
        rijen=rijen,
        totaal=totaal,
        venster=prijsdalingen.VENSTER_DAGEN,
        drempel_pct=int(prijsdalingen.DREMPEL_PCT * 100),
        drempel_eur=int(prijsdalingen.DREMPEL_EUR),
    )


@prijsdalingen_bp.route('/aanbiedingen/<slug>')
def categorie(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    lijst = prijsdalingen.dalingen_voor(category)
    # Onder de ondergrens bestaat de pagina niet: geen dunne pagina's. De
    # categorielinks en de sitemap gebruiken dezelfde grens.
    if len(lijst) < prijsdalingen.MIN_PER_PAGINA:
        abort(404)
    goedkoopste = sum(1 for d in lijst if d['goedkoopste'])
    return render_template(
        'prijsdalingen.html',
        category=category,
        lijst=lijst,
        aantal=len(lijst),
        goedkoopste=goedkoopste,
        grootste=lijst[0],
        venster=prijsdalingen.VENSTER_DAGEN,
        drempel_pct=int(prijsdalingen.DREMPEL_PCT * 100),
        drempel_eur=int(prijsdalingen.DREMPEL_EUR),
        structured_data=_structured_data(category, lijst),
        andere=[(c, n) for c, n, _ in prijsdalingen.overzicht() if c.id != category.id],
    )
