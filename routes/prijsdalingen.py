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
import prijsverschillen

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


_MAANDEN = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
            'augustus', 'september', 'oktober', 'november', 'december']


def _datum_tekst(dt):
    return f"{dt.day} {_MAANDEN[dt.month - 1]} {dt.year}" if dt else ''


@prijsdalingen_bp.route('/onderzoek/prijsverschillen-witgoed')
def prijsverschillen_witgoed():
    """De publicatie met prijsverschillen tussen winkels (prijsverschillen.py).

    Bedoeld als pagina waar andere sites naar linken; ververst vanzelf
    (cache zes uur), de datum bovenaan is de stand van de cijfers.
    """
    d = prijsverschillen.cijfers()
    if not d.get('apparaten', 1):
        abort(404)
    site = current_app.config['SITE_URL']
    structured = {
        '@context': 'https://schema.org',
        '@type': 'Dataset',
        'name': f"Prijsverschillen witgoed tussen Nederlandse winkels ({d['stand'].year})",
        'description': (f"Verschil tussen de laagste en hoogste prijs van hetzelfde apparaat bij "
                        f"{d['aantal_winkels']} Nederlandse winkels, over {d['totaal']['apparaten']} "
                        f"apparaten. Gemiddeld EUR {int(d['totaal']['gem_eur'])}."),
        'url': f"{site}/onderzoek/prijsverschillen-witgoed",
        'creator': {'@type': 'Organization', 'name': 'WitgoedAanbod.nl', 'url': site},
        'dateModified': d['stand'].strftime('%Y-%m-%d'),
        'temporalCoverage': f"{d['historie_sinds'].strftime('%Y-%m-%d') if d['historie_sinds'] else ''}/{d['stand'].strftime('%Y-%m-%d')}",
        'license': 'https://creativecommons.org/licenses/by/4.0/',
    }
    return render_template(
        'prijsverschillen.html',
        d=d,
        stand_tekst=_datum_tekst(d['stand']),
        sinds_tekst=_datum_tekst(d['historie_sinds']),
        structured_data=structured,
    )
