import time

from flask import Blueprint, render_template, request, redirect, current_app, abort
from models import Category, Product, Guide
from sqlalchemy import or_
from filter_helpers import (compute_brand_facet, compute_spec_facets, expand_spec_values,
                            parse_spec_filters, slugify)

main_bp = Blueprint('main', __name__)

# Filteropties en meta-description per categorie veranderen alleen bij een
# sync, maar werden bij elk bezoek opnieuw berekend over álle producten in
# de categorie (alle specs-JSON parsen) — goed voor ~0,7s extra TTFB op de
# belangrijkste commerciële pagina's. Cache met korte TTL; gunicorn draait
# met 1 worker dus een procescache volstaat.
_FACET_CACHE = {}
_FACET_TTL = 15 * 60  # seconden

_PROS_CONS_CACHE = {}
_PROS_CONS_TTL = 15 * 60


def _pros_cons_by_ean():
    """Redactionele pros/cons uit alle videogidsen, {ean: {...}} — zie
    guide_cards.collect_pros_cons_by_ean. Zelfde cache-patroon als
    _category_facets: er zijn maar ~10 gidsen, maar geen reden om ze op
    elke productkaart-render opnieuw te doorzoeken."""
    nu = time.time()
    hit = _PROS_CONS_CACHE.get('data')
    if hit and nu - hit[0] < _PROS_CONS_TTL:
        return hit[1]
    from guide_cards import collect_pros_cons_by_ean
    guides = Guide.query.filter_by(post_type='guide').all()
    data = collect_pros_cons_by_ean(guides)
    _PROS_CONS_CACHE['data'] = (nu, data)
    return data


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
    tekst = ' '.join(parts) + ". Vind de laagste prijs bij o.a. Bol, Coolblue, MediaMarkt, Expert en EP."
    return tekst[:160]


def _category_structured_data(category, page_products, extra_crumb=None, list_name=None):
    """ItemList + BreadcrumbList JSON-LD voor een categorie- of facetpagina.

    extra_crumb (bv. een merknaam) voegt een derde breadcrumb-niveau toe;
    zonder extra_crumb blijft dit het oorspronkelijke 2-niveau-gedrag.
    """
    site_url = current_app.config['SITE_URL']
    item_list = {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': list_name or category.name,
        'itemListElement': [{
            '@type': 'ListItem',
            'position': i,
            'url': f"{site_url}/product/{p.slug}",
        } for i, p in enumerate(page_products, 1)],
    }
    crumbs = [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f"{site_url}/"}]
    if extra_crumb:
        crumbs.append({'@type': 'ListItem', 'position': 2, 'name': category.name,
                       'item': f"{site_url}/category/{category.slug}"})
        crumbs.append({'@type': 'ListItem', 'position': 3, 'name': extra_crumb})
    else:
        crumbs.append({'@type': 'ListItem', 'position': 2, 'name': category.name})
    breadcrumbs = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': crumbs,
    }
    return [item_list, breadcrumbs]


def _category_faq(category, brand_facet, spec_facets):
    """Veelgestelde vragen voor de categoriepagina, uit LIVE aanbodsdata.

    Bewust geen verzonnen redactietekst: elke prijs, merkenteller en
    energielabel komt uit het actuele aanbod en ademt dus mee met de
    syncs. Alleen op de hoofd-categoriepagina (niet op facetpagina's,
    anders staat dezelfde FAQ op tientallen URL's). Minder dan 5
    leverbare producten -> geen FAQ (te dun om iets te beweren).
    """
    from models import db
    naam = category.name.lower()
    prijzen = sorted(r[0] for r in db.session.query(Product.price)
                     .filter(Product.category_id == category.id,
                             Product.is_available == True,
                             Product.price.isnot(None),
                             Product.price > 0).all())
    if len(prijzen) < 5:
        return []

    def euro(bedrag):
        return ('€ ' + f"{bedrag:,.0f}").replace(',', '.')

    p25 = prijzen[len(prijzen) // 4]
    p75 = prijzen[(len(prijzen) * 3) // 4]
    faq = [{
        'vraag': f"Wat kosten {naam} op dit moment?",
        'antwoord': (f"De {len(prijzen)} leverbare {naam} in onze vergelijker lopen "
                     f"van {euro(prijzen[0])} tot {euro(prijzen[-1])}; de middenmoot zit "
                     f"tussen {euro(p25)} en {euro(p75)}. Per apparaat tonen we altijd "
                     "de laagste actuele prijs, inclusief het prijsverloop over tijd."),
    }]
    if brand_facet:
        top = ", ".join(f"{b['value']} ({b['count']})" for b in brand_facet[:5])
        faq.append({
            'vraag': f"Welke merken {naam} kun je hier vergelijken?",
            'antwoord': (f"Momenteel vergelijken we {len(brand_facet)} merken, "
                         f"waaronder {top}. Via de filters of de merkenpagina's "
                         "bekijk je het aanbod per merk."),
        })
    energie = next((f for f in spec_facets
                    if 'energielabel' in f['key'].lower()), None)
    if energie and energie['options']:
        letters = sorted({o['value'].strip()[:1].upper()
                          for o in energie['options'] if o['value'].strip()})
        beste = letters[0]
        aantal = sum(o['count'] for o in energie['options']
                     if o['value'].strip().upper().startswith(beste))
        faq.append({
            'vraag': f"Wat is het zuinigste energielabel bij {naam} dat nu te koop is?",
            'antwoord': (f"Energielabel {beste} — daarvan telt onze vergelijker op dit "
                         f"moment {aantal} {naam}. Een zuiniger label betekent lagere "
                         "stroomkosten; waar de gegevens beschikbaar zijn rekenen we de "
                         "geschatte energiekosten per jaar voor je uit."),
        })
    faq.append({
        'vraag': "Hoe actueel zijn deze prijzen?",
        'antwoord': ("We verversen de prijzen van Bol, Coolblue, MediaMarkt, Expert, "
                     "Alternate en EP meerdere keren per dag, volledig automatisch via "
                     "hun officiële productfeeds. De goedkoopste leverbare aanbieding "
                     "staat altijd bovenaan; winkels kunnen hun positie niet kopen."),
    })
    return faq


@main_bp.route('/api/sync-status')
def sync_status():
    """Diagnose-overzicht van de syncs (alleen-lezen, geen gevoelige data).

    Railway-logs zijn vanuit de ontwikkelomgeving niet bereikbaar; dit
    endpoint maakt zichtbaar of de scheduler jobs heeft ingepland, wanneer
    de laatste syncs draaiden en of de prijshistorie zich vult. Staat in
    robots.txt onder Disallow /api/.
    """
    from flask import jsonify
    from models import db, Offer, PriceHistory, Product, SyncLog

    jobs = []
    try:
        from scheduler import scheduler
        jobs = [{'naam': j.name, 'volgende_run': str(j.next_run_time)}
                for j in scheduler.get_jobs()]
    except Exception as e:
        jobs = [{'fout': str(e)}]

    logs = (SyncLog.query.order_by(SyncLog.started_at.desc()).limit(5).all())
    geen_foto = db.or_(Product.image_url.is_(None), Product.image_url == '')
    laatste_sync_per_winkel = {
        r: str(db.session.query(db.func.max(Offer.last_synced))
               .filter(Offer.retailer == r).scalar())
        for r in ('bol', 'mediamarkt', 'coolblue', 'expert', 'alternate', 'ep')
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
        # Producten die de foto-placeholder tonen: de winkel-feeds hebben er
        # (nog) geen foto voor. Syncs vullen dit aan zodra een feed er wel
        # een heeft; deze lijst maakt de hardnekkige gevallen zichtbaar.
        'producten_zonder_foto': {
            'aantal': Product.query.filter(geen_foto).count(),
            'voorbeelden': [p.slug for p in Product.query.filter(geen_foto)
                            .order_by(Product.id.desc()).limit(25).all()],
        },
    })


@main_bp.route('/api/category-specs/<slug>')
def category_specs_debug(slug):
    """Alle spec-facetten van een categorie, ongelimiteerd (i.t.t. de 6 die
    de filter-zijbalk toont). Alleen-lezen diagnosetool om te zien welke
    specs er écht met welke waarden in de data staan, voordat je daarop
    bouwt (bv. voor de keuzehulp-wizard) — voorkomt gokken op key-namen die
    in productie anders geschreven blijken dan in lokale voorbeelddata."""
    from flask import jsonify
    category = Category.query.filter_by(slug=slug).first_or_404()
    producten = Product.query.filter_by(category_id=category.id, is_available=True).all()
    facets = compute_spec_facets(producten, max_filters=50, max_options=20)
    return jsonify({'aantal_producten': len(producten),
                    'facets': [{'key': f['key'], 'aantal_opties': len(f['options']),
                               'top_waarden': f['options'][:8]} for f in facets]})


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

    # 5 stuks: vult de nieuwsrij op de homepage (zelfde breedte als de
    # productkaarten-grid erboven).
    latest_blog_posts = Guide.query.filter_by(post_type='blog').order_by(Guide.created_at.desc()).limit(5).all()

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
        # Bij Kleur zitten achter één knop meerdere ruwe schrijfwijzen
        # ("Wit" en "wit"); expand_spec_values vertaalt terug naar wat er
        # daadwerkelijk in de database staat.
        q = q.filter(Product.specs[key].as_string().in_(expand_spec_values(spec_facets, key, values)))

    sort = request.args.get('sort', '')
    if sort == 'price_asc':
        q = q.order_by(Product.price.asc())
    elif sort == 'price_desc':
        q = q.order_by(Product.price.desc())

    products = q.paginate(page=page, per_page=24)

    # Heeft deze categorie een videogids (bv. "beste wasmachine 2026"), dan
    # krijgt die voorrang op de categoriepagina: een thumbnail met video
    # trekt meer klikken dan een platte tekstlink, en bezoekers die aan het
    # vergelijken zijn zien de video meteen. Zonder video valt dit terug op
    # de gewone (eerste) koopgids van de categorie.
    category_guides = Guide.query.filter_by(category_id=category.id, post_type='guide').order_by(Guide.created_at.desc()).all()
    video_guide, video_id = None, None
    for guide in category_guides:
        vid = _guide_video_id(guide)
        if vid:
            video_guide, video_id = guide, vid
            break
    category_guide = video_guide or (category_guides[0] if category_guides else None)

    from wizard import WIZARD_QUESTIONS
    has_wizard = slug in WIZARD_QUESTIONS

    # Data-gedreven FAQ + FAQPage-schema (SEO-audit punt 6); alleen hier,
    # niet op de facetpagina's (die renderen via _render_facet_page).
    faq = _category_faq(category, brand_facet, spec_facets)
    faq_jsonld = None
    if faq:
        faq_jsonld = {
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'mainEntity': [{
                '@type': 'Question',
                'name': item['vraag'],
                'acceptedAnswer': {'@type': 'Answer', 'text': item['antwoord']},
            } for item in faq],
        }

    # Subcategorie-facetlinks (voorlader/bovenlader, warmtepomp/condens):
    # los opgehaald, want deze specs zitten niet altijd in de (top-6)
    # spec_facets-cache hierboven. Alleen voor de 2 categorieën met schone
    # data (zie SUBCATEGORY_SPECS) — dus meestal helemaal geen extra query.
    subtype_options = None
    subtype_key = SUBCATEGORY_SPECS.get(slug)
    if subtype_key:
        alle_producten = Product.query.filter_by(category_id=category.id, is_available=True).all()
        subtype_options = compute_spec_facets(alle_producten, max_filters=999, max_options=999)
        subtype_options = next((f['options'] for f in subtype_options if f['key'] == subtype_key), None)

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
        video_id=video_id,
        meta_description=meta_description,
        structured_data=_category_structured_data(category, products.items),
        has_wizard=has_wizard,
        subtype_options=subtype_options,
        pros_cons_by_ean=_pros_cons_by_ean(),
        faq=faq,
        faq_jsonld=faq_jsonld,
    )


def _render_facet_page(category, extra_filter, facet_label, facet_title, meta_description, intro):
    """Gedeelde rendering voor merk-/energielabel-facetpagina's.

    In tegenstelling tot ?brand=/?spec= (client-side filters, alleen
    bereikbaar via een formulier dat Google niet invult) heeft elke
    facetpagina een eigen, crawlbare URL, titel en een uit live data
    afgeleide introtekst — geen kale doorgeklikte tabel, om hetzelfde lot
    te vermijden als de "thin" vergelijkingspagina's die Google's
    maart 2026-kernupdate afstrafte.
    """
    page = request.args.get('page', 1, type=int)
    q = (Product.query.filter_by(category_id=category.id, is_available=True)
         .filter(extra_filter).order_by(Product.price.asc()))
    products = q.paginate(page=page, per_page=24)
    if products.total == 0:
        abort(404)

    brand_facet, spec_facets, _ = _category_facets(category)

    return render_template(
        'category.html',
        category=category,
        products=products.items,
        pagination=products,
        brand_facet=brand_facet,
        spec_facets=spec_facets,
        selected_brands=[],
        selected_specs={},
        min_price=0,
        max_price=10000,
        selected_sort='',
        category_guide=None,
        video_id=None,
        meta_description=meta_description,
        structured_data=_category_structured_data(category, products.items, extra_crumb=facet_label,
                                                   list_name=facet_title),
        facet_title=facet_title,
        facet_intro=intro,
        pros_cons_by_ean=_pros_cons_by_ean(),
    )


@main_bp.route('/category/<slug>/merk/<merk_slug>')
def category_brand(slug, merk_slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    brand_facet, _, _ = _category_facets(category)
    match = next((b for b in brand_facet if slugify(b['value']) == merk_slug), None)
    if not match:
        abort(404)
    merk = match['value']

    naam_lower = category.name.lower()
    intro = (f"We volgen momenteel {match['count']} {merk}-modellen in de categorie "
            f"{naam_lower}. Bekijk per model de actuele prijs bij onze aangesloten "
            f"winkels, plus het prijsverloop over tijd.")
    meta_description = (f"Vergelijk {match['count']} {merk} {naam_lower} op prijs. "
                        f"Bekijk actuele prijzen en prijsverloop bij Bol, Coolblue, "
                        f"MediaMarkt, Expert, Alternate en EP.")[:160]

    return _render_facet_page(
        category, Product.brand.ilike(merk), merk,
        f"{merk} {category.name}", meta_description, intro,
    )


@main_bp.route('/category/<slug>/energielabel/<letter>')
def category_energielabel(slug, letter):
    category = Category.query.filter_by(slug=slug).first_or_404()
    letter = letter.upper()
    if letter not in ('A', 'B', 'C', 'D', 'E', 'F', 'G'):
        abort(404)
    _, spec_facets, _ = _category_facets(category)
    energie_facet = next((f for f in spec_facets if 'energielabel' in f['key'].lower()), None)
    match = next((o for o in (energie_facet['options'] if energie_facet else [])
                 if o['value'].strip().upper().startswith(letter)), None)
    if not match:
        abort(404)

    naam_lower = category.name.lower()
    intro = (f"Dit zijn de {match['count']} zuinigste modellen (energielabel {letter}) "
            f"in onze {naam_lower}-vergelijker, met de actuele prijs per winkel.")
    meta_description = (f"Energielabel {letter} {naam_lower} vergelijken: {match['count']} "
                        f"zuinige modellen op prijs, bij Bol, Coolblue, MediaMarkt, "
                        f"Expert, Alternate en EP.")[:160]

    return _render_facet_page(
        category, Product.specs[energie_facet['key']].as_string().ilike(f"{letter}%"),
        f"Energielabel {letter}", f"Energielabel {letter} {category.name}",
        meta_description, intro,
    )


# Subcategorie-landingspagina's: alleen waar de spec-data schoon en
# betekenisvol genoeg is (geverifieerd via /api/category-specs/<slug>).
# Koelkasten/vaatwassers hebben geen vergelijkbaar schoon type-veld —
# bewust geen pagina forceren op rommelige data (zie audit: "thin content").
SUBCATEGORY_SPECS = {
    'wasmachines': 'Top load of voorlader',
    'drogers': 'Type droger',
}


@main_bp.route('/category/<slug>/type/<waarde_slug>')
def category_subtype(slug, waarde_slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    spec_key = SUBCATEGORY_SPECS.get(slug)
    if not spec_key:
        abort(404)
    _, spec_facets, _ = _category_facets(category)
    facet = next((f for f in spec_facets if f['key'] == spec_key), None)
    if not facet:
        # Uncapped: deze spec zit niet altijd in de (top-6) sidebar-cache.
        producten = Product.query.filter_by(category_id=category.id, is_available=True).all()
        alle_facets = compute_spec_facets(producten, max_filters=999, max_options=999)
        facet = next((f for f in alle_facets if f['key'] == spec_key), None)
    match = next((o for o in (facet['options'] if facet else [])
                 if slugify(o['value']) == waarde_slug), None)
    if not match:
        abort(404)
    waarde = match['value']

    naam_lower = category.name.lower()
    intro = (f"We volgen momenteel {match['count']} {waarde.lower()}s in de categorie "
            f"{naam_lower}. Bekijk per model de actuele prijs bij onze aangesloten winkels.")
    meta_description = (f"{waarde} {naam_lower} vergelijken: {match['count']} modellen op prijs "
                        f"bij Bol, Coolblue, MediaMarkt, Expert, Alternate en EP.")[:160]

    return _render_facet_page(
        category, Product.specs[spec_key].as_string() == waarde, waarde,
        f"{waarde} {category.name}", meta_description, intro,
    )


def _global_brand_index():
    """Merk + aantal over álle categorieën heen (GROUP BY, geen volledige
    productrijen), varianten in schrijfwijze samengevoegd."""
    from models import db
    from sqlalchemy import func
    from filter_helpers import compute_global_brand_index
    rows = (db.session.query(Product.brand, func.count(Product.id))
            .filter(Product.is_available == True, Product.brand.isnot(None))
            .group_by(Product.brand).all())
    return compute_global_brand_index(rows)


@main_bp.route('/merken')
def brands_index():
    """A-Z-overzicht van alle merken die we vergelijken — long-tail
    zoekverkeer op merknaam alleen ('Bosch witgoed'), en een crawlbare
    ingang naar de per-merk-pagina's hieronder."""
    merken = _global_brand_index()
    return render_template('brands.html', merken=merken)


@main_bp.route('/merk/<merk_slug>')
def brand_detail(merk_slug):
    """Eén merk over alle categorieën heen (i.t.t. /category/<slug>/merk/<merk>,
    dat is per categorie). Voor merken die in meerdere categorieën
    voorkomen (bv. Bosch: wasmachines én koelkasten én vaatwassers)."""
    from models import db

    page = request.args.get('page', 1, type=int)
    index = _global_brand_index()
    match = next((m for m in index if m['slug'] == merk_slug), None)
    if not match:
        abort(404)
    merk = match['naam']

    q = Product.query.filter(Product.brand.ilike(merk), Product.is_available == True).order_by(Product.price.asc())
    products = q.paginate(page=page, per_page=24)

    categorie_rows = (db.session.query(Category.name)
                      .join(Product, Product.category_id == Category.id)
                      .filter(Product.brand.ilike(merk), Product.is_available == True)
                      .distinct().all())
    categorieen = sorted(r[0] for r in categorie_rows)

    intro = (f"We vergelijken momenteel {match['aantal']} {merk}-producten"
            + (f", verdeeld over {len(categorieen)} categorieën: {', '.join(categorieen[:6])}."
               if categorieen else "."))
    meta_description = (f"Vergelijk {match['aantal']} {merk}-producten op prijs bij "
                        f"Bol, Coolblue, MediaMarkt, Expert, Alternate en EP.")[:160]

    site_url = current_app.config['SITE_URL']
    structured_data = [{
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f"{site_url}/"},
            {'@type': 'ListItem', 'position': 2, 'name': 'Merken', 'item': f"{site_url}/merken"},
            {'@type': 'ListItem', 'position': 3, 'name': merk},
        ],
    }]

    return render_template('brand_detail.html', merk=merk, products=products.items,
                           pagination=products, categorieen=categorieen, intro=intro,
                           meta_description=meta_description, structured_data=structured_data,
                           pros_cons_by_ean=_pros_cons_by_ean())


@main_bp.route('/category/<slug>/keuzehulp')
def category_wizard(slug):
    """Kort vragenlijstje (3 vragen) dat mensentaal vertaalt naar dezelfde
    ?spec=-filters als de categoriepagina — zie wizard.py. Alleen voor de
    categorieën met een geconfigureerde vragenset; elders 404."""
    category = Category.query.filter_by(slug=slug).first_or_404()
    producten = Product.query.filter_by(category_id=category.id, is_available=True).all()

    from wizard import build_wizard_context
    context = build_wizard_context(slug, producten)
    if not context:
        abort(404)

    return render_template('wizard.html', category=category,
                           titel=context['titel'], vragen=context['vragen'])


@main_bp.route('/api/keuzehulp-tellen/<slug>')
def wizard_count(slug):
    """Hoeveel producten voldoen aan de tot nu toe gekozen wizard-antwoorden
    (dezelfde spec-filtersyntax als de categoriepagina). Voor de live
    '397 wasmachines'-teller tijdens het doorlopen van de wizard."""
    from flask import jsonify
    category = Category.query.filter_by(slug=slug).first_or_404()
    _, spec_facets, _ = _category_facets(category)
    q = Product.query.filter_by(category_id=category.id, is_available=True)
    for key, values in parse_spec_filters(request.args.getlist('spec')).items():
        # Zelfde vertaalslag als de categoriepagina, anders zou de teller een
        # ander aantal geven dan de pagina waar hij naartoe leidt.
        q = q.filter(Product.specs[key].as_string().in_(expand_spec_values(spec_facets, key, values)))
    return jsonify({'aantal': q.count()})
