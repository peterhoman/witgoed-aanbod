"""
SEO routes (sitemap, robots.txt)
"""

from flask import Blueprint, abort, render_template_string, current_app
from models import Product, Category, Guide, utcnow
from filter_helpers import (compute_brand_facet, compute_spec_facets,
                            compute_global_brand_index, energielabel_letter, slugify)
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


def _laatste_wijziging_per_product():
    """{product_id: moment van de laatste échte inhoudswijziging}.

    Hiervoor stond in elke <lastmod> gewoon de datum van vandaag. Dat is voor
    3281 URL's tegelijk waar noch bruikbaar: als een sitemap elke dag beweert
    dat alles veranderd is terwijl de pagina's identiek blijven, leert Google
    binnen enkele weken om lastmod op dit domein te negeren. Dan is het
    instrument weg waarmee je een hercrawl uitlokt op de pagina's die wél
    veranderd zijn.

    products.updated_at is hier ongeschikt: sync_products zet
    product.last_synced onvoorwaardelijk bij elke sync, en dat maakt de rij
    dirty, dus onupdate=utcnow schuift updated_at ook elke sync op. Dan meet
    je de sync, niet de wijziging.

    price_history meet wel het echte ding: models.log_price schrijft alleen een
    rij weg als de prijs afwijkt van de laatst bekende. Het laatste prijspunt
    is dus het laatste moment waarop deze pagina inhoudelijk veranderde. Zonder
    prijshistorie valt het terug op de aanmaakdatum.
    """
    from models import db, PriceHistory
    rijen = (db.session.query(PriceHistory.product_id,
                              db.func.max(PriceHistory.recorded_at))
             .group_by(PriceHistory.product_id).all())
    return {pid: moment for pid, moment in rijen}


def _nieuwste(momenten):
    """Het meest recente moment uit een reeks, of None als er niets in zit."""
    momenten = [m for m in momenten if m]
    return max(momenten) if momenten else None


# De sitemap is opgesplitst per soort pagina, met /sitemap.xml als index. Reden:
# Search Console rapporteert dekking per ingediende sitemap. Met alles in één
# bestand zag je één percentage over 3281 URL's — 137 geïndexeerd — zonder te
# weten of dat productpagina's, categoriepagina's of facetpagina's waren. Per
# soort is af te lezen wat wel en niet aanslaat, en dus of een ingreep werkt.
SOORTEN = {
    'producten': 'productpagina',
    'categorieen': 'categoriepagina',
    'merken': 'merkpagina (alle categorieen)',
    'merk-per-categorie': 'merk binnen een categorie',
    'facetten': 'energielabel- en subtypepagina',
    'gidsen': 'koopgids en blog',
    'overig': 'homepage en juridische paginas',
}


def _bouw_entries():
    """Alle sitemap-regels, gegroepeerd als {soort: [entry, ...]}."""
    products = Product.query.filter_by(is_available=True).all()
    categories = Category.query.filter_by(parent_id=None).all()

    # Per product het moment van de laatste echte wijziging; daaruit volgen de
    # datums van alle overzichtspagina's. Eén extra query voor de hele sitemap.
    gewijzigd = _laatste_wijziging_per_product()

    def product_moment(p):
        return gewijzigd.get(p.id) or p.created_at

    def moment_van(selectie):
        return _nieuwste(product_moment(p) for p in selectie)

    per_merk_globaal = {}
    for p in products:
        sleutel = slugify(p.brand or '')
        if sleutel:
            per_merk_globaal[sleutel] = _nieuwste(
                [per_merk_globaal.get(sleutel), product_moment(p)])

    sitemap_entries = []

    # Homepage
    sitemap_entries.append({
        'loc': f"{current_app.config['SITE_URL']}/",
        'lastmod': _lastmod(moment_van(products)),
        'priority': '1.0',
        'soort': 'overig'
    })

    # Merken A-Z + per-merk-pagina (over alle categorieën heen)
    sitemap_entries.append({
        'loc': f"{current_app.config['SITE_URL']}/merken",
        'lastmod': _lastmod(moment_van(products)),
        'priority': '0.6',
        'soort': 'overig'
    })
    for merk in compute_global_brand_index((p.brand, 1) for p in products):
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/merk/{merk['slug']}",
            'lastmod': _lastmod(per_merk_globaal.get(merk['slug'])),
            'priority': '0.5',
            'soort': 'merken'
        })

    # Category pages + hun merk-/energielabel-facetpagina's (long-tail SEO;
    # zelfde live-databerekening als de categoriepagina zelf, dus een
    # facetpagina staat hier alleen als hij ook echt producten heeft).
    for category in categories:
        cat_products = [p for p in products if p.category_id == category.id]
        cat_moment = moment_van(cat_products)
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}",
            'lastmod': _lastmod(cat_moment),
            'priority': '0.8',
            'soort': 'categorieen'
        })
        for brand in compute_brand_facet(cat_products):
            merk_slug = slugify(brand['value'])
            sitemap_entries.append({
                'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}/merk/{merk_slug}",
                'lastmod': _lastmod(moment_van(
                    p for p in cat_products if slugify(p.brand or '') == merk_slug)),
                'priority': '0.5',
                'soort': 'merk-per-categorie'
            })
        # Buiten de facetlus: er kan meer dan één veld zijn waar "energielabel"
        # in de naam zit, en dan gaf een per-facet ontdubbeling dezelfde URL
        # twee keer. Een sitemap die een URL herhaalt is geen ramp, maar het is
        # wel de soort slordigheid waarop de rest van dit bestand wordt
        # afgerekend.
        letters_gezien = set()
        for facet in compute_spec_facets(cat_products):
            if 'energielabel' not in facet['key'].lower():
                continue
            for option in facet['options']:
                # Alleen kale letters A t/m G: op "Energielabel niet van
                # toepassing" ontstond anders een ovens-facetpagina voor
                # label E, met één pizzaoven erop.
                letter = energielabel_letter(option['value'])
                letter = letter.lower() if letter else None
                if letter and letter not in letters_gezien:
                    letters_gezien.add(letter)
                    sitemap_entries.append({
                        'loc': f"{current_app.config['SITE_URL']}/category/{category.slug}/energielabel/{letter}",
                        'lastmod': _lastmod(moment_van(
                            p for p in cat_products
                            if (energielabel_letter((p.specs or {}).get('Waarde energielabel')) or '').lower() == letter)),
                        'priority': '0.5',
                        'soort': 'facetten'
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
                        'lastmod': _lastmod(moment_van(
                            p for p in cat_products
                            if str((p.specs or {}).get(subtype_key) or '').strip() == option['value'])),
                        'priority': '0.5',
                        'soort': 'facetten'
                    })

    # Product pages. Slugs kunnen speciale tekens bevatten (De'Longhi,
    # "Hot & Cold", ’); het sitemap-protocol wil URL's percent-gecodeerd
    # (%26 i.p.v. &) vóórdat de XML-escaping eroverheen gaat. De pagina's
    # werken ook zonder, maar zo is er geen enkele interpretatieruimte
    # voor crawlers.
    from urllib.parse import quote
    for product in products:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/product/{quote(product.slug, safe='-._~')}",
            # Niet product.updated_at: dat schuift bij elke sync op omdat
            # last_synced onvoorwaardelijk wordt gezet. Zie
            # _laatste_wijziging_per_product.
            'lastmod': _lastmod(product_moment(product)),
            'priority': '0.6',
            'soort': 'producten'
        })

    # Guides
    guides = Guide.query.filter_by(post_type='guide').all()
    for guide in guides:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/gidsen/{guide.slug}",
            'lastmod': _lastmod(guide.created_at),
            'priority': '0.7',
            'soort': 'gidsen'
        })

    # Blog posts
    blog_posts = Guide.query.filter_by(post_type='blog').all()
    for post in blog_posts:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/blog/{post.slug}",
            'lastmod': _lastmod(post.created_at),
            'priority': '0.6',
            'soort': 'gidsen'
        })

    # Legal pages
    # productteksten staat erbij zodra de eigen beschrijvingen live zijn: het
    # is de verantwoording waar elke productpagina naar verwijst, en Google
    # vraagt daar expliciet om waar inhoud grotendeels automatisch ontstaat.
    legal_pages = ['over-ons', 'privacy', 'disclaimer', 'cookies', 'voorwaarden',
                   'retourneren', 'contact', 'productteksten']
    for page in legal_pages:
        sitemap_entries.append({
            'loc': f"{current_app.config['SITE_URL']}/{page}",
            'lastmod': _lastmod(),
            'priority': '0.5',
            'soort': 'overig'
        })

    per_soort = {soort: [] for soort in SOORTEN}
    for entry in sitemap_entries:
        per_soort[entry['soort']].append(entry)
    return per_soort


def _urlset(entries):
    xml = render_template_string('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for entry in entries %}
    <url>
        <loc>{{ entry.loc }}</loc>
        <lastmod>{{ entry.lastmod }}</lastmod>
        <priority>{{ entry.priority }}</priority>
    </url>
{% endfor %}
</urlset>''', entries=entries)
    return xml, 200, {'Content-Type': 'application/xml'}


@seo_bp.route('/sitemap.xml')
def sitemap():
    """Sitemap-index: verwijst naar één bestand per soort pagina.

    Deze URL blijft wat hij was, want hij staat zo in Search Console en in
    robots.txt. Een index op dezelfde plek hoeft daar niet opnieuw ingediend te
    worden; Google leest de onderliggende bestanden vanzelf en rapporteert de
    dekking per bestand.
    """
    per_soort = _bouw_entries()
    onderdelen = []
    for soort in SOORTEN:
        entries = per_soort.get(soort) or []
        if not entries:
            continue
        onderdelen.append({
            'loc': f"{current_app.config['SITE_URL']}/sitemap-{soort}.xml",
            # De nieuwste datum uit dit bestand; zo weet Google welk onderdeel
            # het opnieuw moet ophalen zonder ze alle zeven te lezen.
            'lastmod': max(e['lastmod'] for e in entries),
        })

    xml = render_template_string('''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for deel in onderdelen %}
    <sitemap>
        <loc>{{ deel.loc }}</loc>
        <lastmod>{{ deel.lastmod }}</lastmod>
    </sitemap>
{% endfor %}
</sitemapindex>''', onderdelen=onderdelen)
    return xml, 200, {'Content-Type': 'application/xml'}


@seo_bp.route('/sitemap-<soort>.xml')
def sitemap_deel(soort):
    """Eén sitemapbestand per soort pagina; zie SOORTEN."""
    if soort not in SOORTEN:
        abort(404)
    return _urlset(_bouw_entries().get(soort) or [])


@seo_bp.route('/robots.txt')
def robots():
    """Generate robots.txt.

    AI-crawlers (GPTBot, ClaudeBot, PerplexityBot, ...) worden BEWUST
    toegelaten (SEO-audit 24-07): AI-zoekmachines citeren juist
    vergelijkingscontent, en elke vermelding met bronlink is een gratis
    verkeerskanaal. De expliciete Allow-regels documenteren die keuze —
    zonder deze regels was het een stilzwijgende default geweest.
    """
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/

Sitemap: {current_app.config['SITE_URL']}/sitemap.xml

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

# AI-zoekmachines en -assistenten: bewust welkom (antwoorden met
# bronvermelding naar onze vergelijkingen zijn een verkeerskanaal).
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /
"""
    return robots_txt, 200, {'Content-Type': 'text/plain'}
