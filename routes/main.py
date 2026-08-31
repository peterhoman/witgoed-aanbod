import time
from collections import Counter, defaultdict

from flask import Blueprint, render_template, request, redirect, current_app, abort
from models import Category, Product, Guide, winkel_opsomming
from sqlalchemy import or_
from filter_helpers import (compute_brand_facet, compute_spec_facets, expand_spec_values,
                            energielabel_letter, parse_spec_filters, slugify)

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

# Vertrouwenscijfers op de homepage. Ze staan er omdat Google bij de
# beoordeling van 22 aug expliciet vraagt om zichtbare betrouwbaarheid, en
# omdat de concurrentie hetzelfde doet zonder onze onderbouwing: Knibble
# zet "wij vergelijken 263 webshops" op zijn homepage. Wij hebben harder
# materiaal, maar toonden het nergens.
#
# Ze komen LIVE uit de database en worden nooit met de hand bijgewerkt --
# een geteld getal dat na een maand niet meer klopt is erger dan geen
# getal (kernregel: beweer niets wat de data niet draagt). Een uur cache,
# want dit staat op de drukste pagina van de site.
_CIJFERS_CACHE = {}
_CIJFERS_TTL = 60 * 60


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
    tekst = ' '.join(parts) + f". Vind de laagste prijs bij o.a. {winkel_opsomming()}."
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
    # Alleen kale letters A t/m G. Ovens leveren "Energielabel niet van
    # toepassing"; die waarde maakte via de eerste letter E het "zuinigste
    # label van de categorie", op gezag van één pizzaoven zonder label. Die
    # bewering stond in de FAQPage-structured-data en kon dus als rich result
    # bij Google verschijnen. Blijft er geen geldige letter over, dan vervalt
    # deze vraag -- geen antwoord is beter dan een verzonnen antwoord.
    letters = sorted({energielabel_letter(o['value'])
                      for o in (energie['options'] if energie else [])} - {None})
    if letters:
        beste = letters[0]
        aantal = sum(o['count'] for o in energie['options']
                     if energielabel_letter(o['value']) == beste)
        faq.append({
            'vraag': f"Wat is het zuinigste energielabel bij {naam} dat nu te koop is?",
            'antwoord': (f"Energielabel {beste} — daarvan telt onze vergelijker op dit "
                         f"moment {aantal} {naam}. Een zuiniger label betekent lagere "
                         "stroomkosten; waar de gegevens beschikbaar zijn rekenen we de "
                         "geschatte energiekosten per jaar voor je uit."),
        })
    faq.append({
        'vraag': "Hoe actueel zijn deze prijzen?",
        'antwoord': (f"We verversen de prijzen van {winkel_opsomming()} meerdere "
                     "keren per dag, volledig automatisch via hun officiële "
                     "productfeeds. De goedkoopste leverbare aanbieding staat altijd "
                     "bovenaan; winkels kunnen hun positie niet kopen."),
    })
    return faq


def _paginaweergaven():
    """Tellingen uit pageviews.py; faalt stil als de tabel er nog niet is."""
    try:
        from pageviews import overzicht
        return overzicht()
    except Exception as e:
        return {'nog_geen_data': str(e)[:120]}


def _winkelbijdrage():
    """Wat elke winkel bijdraagt aan de vergelijkbaarheid, niet aan de omvang.

    De vraag bij een nieuwe feed is niet "hoeveel producten heeft die winkel"
    maar "bij hoeveel apparaten maakt die winkel het verschil tussen wél en
    niet kunnen vergelijken". Expert heeft 9080 producten in de feed en dekt
    daarvan 21% van onze wasmachines -- dat eerste getal zegt niets.

    'onmisbaar' telt de apparaten met precies twee winkels waarvan deze er
    één is: verdwijnt die winkel, dan valt daar de vergelijking helemaal weg.
    Dat is de bovengrens van wat een winkel waard is. Staat dat getal laag,
    dan levert een zevende winkel waarschijnlijk ook weinig op.
    """
    from models import db, Offer

    winkels_per_product = (
        db.session.query(Offer.product_id.label('pid'),
                         db.func.count(Offer.id).label('n'))
        .filter(Offer.is_available.is_(True))
        .group_by(Offer.product_id)
        .subquery()
    )
    rijen = (
        db.session.query(
            Offer.retailer,
            db.func.count(Offer.id),
            db.func.sum(db.case((winkels_per_product.c.n == 2, 1), else_=0)),
            db.func.sum(db.case((winkels_per_product.c.n == 1, 1), else_=0)),
        )
        .join(winkels_per_product, winkels_per_product.c.pid == Offer.product_id)
        .filter(Offer.is_available.is_(True))
        .group_by(Offer.retailer)
        .all()
    )

    uit = []
    for winkel, aantal, onmisbaar, alleen in rijen:
        uit.append({
            'winkel': winkel,
            'aanbiedingen': aantal,
            # Apparaten waar deze winkel de tweede is: zonder hem geen vergelijking.
            'onmisbaar_voor': int(onmisbaar or 0),
            # Apparaten die alleen deze winkel voert: leveren nu geen vergelijking op.
            'enige_winkel_bij': int(alleen or 0),
        })
    uit.sort(key=lambda w: -w['onmisbaar_voor'])
    return uit


def _winkeldekking():
    """Per categorie en totaal: hoeveel leverbare apparaten hebben meer dan
    één leverbare aanbieding, oftewel bij hoeveel valt er iets te vergelijken.

    In SQL en niet via Product.retailer_count, want die property laadt de
    aanbiedingen per product; over duizenden producten zou dat het endpoint
    onbruikbaar traag maken.
    """
    from models import db, Category, Offer, Product

    winkels_per_product = (
        db.session.query(Offer.product_id.label('pid'),
                         db.func.count(Offer.id).label('n'))
        .filter(Offer.is_available.is_(True))
        .group_by(Offer.product_id)
        .subquery()
    )
    rijen = (
        db.session.query(
            Category.slug,
            db.func.count(Product.id),
            db.func.sum(db.case((winkels_per_product.c.n > 1, 1), else_=0)),
        )
        .select_from(Product)
        .join(Category, Category.id == Product.category_id)
        .outerjoin(winkels_per_product, winkels_per_product.c.pid == Product.id)
        .filter(Product.is_available.is_(True))
        .group_by(Category.slug)
        .all()
    )

    # Lijst en geen dict: Flask sorteert JSON-sleutels alfabetisch, waardoor
    # een gesorteerde dict zijn volgorde verliest. Zwakste categorie onderaan
    # is precies wat je wilt zien als je aan de dekking gaat werken.
    per_categorie, totaal, totaal_multi = [], 0, 0
    for slug, aantal, multi in sorted(rijen, key=lambda r: -(r[2] or 0) / max(r[1], 1)):
        multi = int(multi or 0)
        per_categorie.append({
            'categorie': slug,
            'producten': aantal,
            'meerdere_winkels': multi,
            'dekking_pct': round(100 * multi / aantal) if aantal else 0,
        })
        totaal += aantal
        totaal_multi += multi

    return {
        'totaal': {
            'producten': totaal,
            'meerdere_winkels': totaal_multi,
            'dekking_pct': round(100 * totaal_multi / totaal) if totaal else 0,
        },
        'per_categorie': per_categorie,
    }


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
        for r in ('bol', 'mediamarkt', 'coolblue', 'expert', 'alternate', 'ep',
                  'voordeligwitgoed')
    }
    import os
    return jsonify({
        # Dekking: bij hoeveel apparaten valt er daadwerkelijk iets te
        # vergelijken (meer dan één leverbare winkel). Dit is de enige harde
        # maatstaf voor wat de site onderscheidt van een webshop, en zonder
        # cookies of toestemming te meten. Berekend in SQL over de hele
        # catalogus, niet over de eerste pagina van een categorie.
        'winkeldekking': _winkeldekking(),
        # Per winkel: bij hoeveel apparaten maakt die het verschil tussen wél
        # en niet kunnen vergelijken. Bedoeld om vóór het aansluiten van een
        # zevende winkel te weten of dat de moeite waard is.
        'winkelbijdrage': _winkelbijdrage(),
        # Paginaweergaven per soort per dag (geen cookies, geen bezoekersdata).
        # 'product_per_categorie' is het cijfer om te volgen: hoeveel
        # productpagina's er per categoriepagina worden bekeken.
        'paginaweergaven': _paginaweergaven(),
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


@main_bp.route('/api/feed-velden/<winkel>')
def feed_velden_debug(winkel):
    """Welke velden een winkelfeed levert, en hoe vaak ze gevuld zijn.

    Alleen-lezen diagnosetool, zelfde soort als /api/category-specs. Aanleiding:
    het Model-veld is bij 74% van de producten leeg, en dat is precies de sleutel
    waarop de EU-energielabeldatabase (EPREL) matcht. De vraag is of een van de
    winkelfeeds een modelcode levert die wij nu weggooien.

    Voor Expert, EP en Alternate was dat lokaal al te meten -- hun TradeTracker-
    URL bevat geen sleutel. Uitkomst: Expert en EP leveren geen modelveld,
    Alternate levert MPN maar overlapt niet met onze catalogus (0 van 39 in een
    steekproef). Blijven over: MediaMarkt en Coolblue, en die feeds zitten achter
    een token dat alleen op productie staat. Vandaar dit eindpunt.

    Toont veldnamen en aantallen, en alleen bij korte identificatie-achtige
    waarden een voorbeeld -- geen beschrijvingen of andere feedinhoud, want die
    is commercieel gelicentieerd. /api/ staat op Disallow in robots.txt.
    """
    from flask import jsonify
    from collections import Counter
    grens = min(request.args.get('n', 400, type=int), 2000)

    def beschrijf(records, uitpakken=()):
        """Veldnamen tellen; genest uitpakken waar de feed een object gebruikt."""
        aanwezig, gevuld, voorbeeld = Counter(), Counter(), {}
        for r in records:
            paren = list(r.items())
            for sleutel in uitpakken:
                genest = r.get(sleutel)
                if isinstance(genest, dict):
                    paren += [(f'{sleutel}.{k}', v) for k, v in genest.items()]
            for k, v in paren:
                if isinstance(v, (dict, list)) and not (
                        isinstance(v, list) and len(v) == 1 and not isinstance(v[0], (dict, list))):
                    aanwezig[k] += 1
                    continue
                if isinstance(v, list):
                    v = v[0]
                aanwezig[k] += 1
                tekst = str(v or '').strip()
                if tekst:
                    gevuld[k] += 1
                    # Alleen korte, code-achtige waarden als voorbeeld: dat is
                    # genoeg om een modelcode te herkennen zonder feedinhoud
                    # te publiceren.
                    # Identificatievelden mogen hun waarde tonen: een
                    # modelaanduiding staat op het apparaat zelf en is geen
                    # beschrijvende feedinhoud. De rest alleen zonder spaties,
                    # zodat er nooit een stuk verkooptekst in belandt.
                    identificatie = any(w in k.lower() for w in
                                        ('model', 'mpn', 'sku', 'gtin', 'ean', 'part'))
                    if k not in voorbeeld and len(tekst) <= 40 and (
                            identificatie or ' ' not in tekst):
                        voorbeeld[k] = tekst
        return [{'veld': k, 'aanwezig': n, 'gevuld': gevuld[k],
                 'voorbeeld': voorbeeld.get(k)}
                for k, n in sorted(aanwezig.items(), key=lambda x: -gevuld[x[0]])]

    if winkel == 'mediamarkt':
        import sync_mediamarkt as sm
        token = current_app.config.get('TRADEDOUBLER_TOKEN')
        if not token:
            return jsonify({'fout': 'TRADEDOUBLER_TOKEN ontbreekt'}), 503
        # Hele feed, niet de eerste zoveel: de opbrengst hieronder moet over de
        # complete catalogus gerekend worden. Bij Coolblue bleek een steekproef
        # van 1500 nul treffers te geven, puur omdat hun feed met accessoires
        # begint en het witgoed verderop staat.
        alle = sm.fetch_full_feed(token, sm.MAIN_FEED_ID)
        velden = beschrijf(alle[:grens], uitpakken=('identifiers', 'attributes'))
        records = alle
    elif winkel == 'coolblue':
        import sync_coolblue as sc
        apikey = current_app.config.get('AWIN_FEED_APIKEY')
        if not apikey:
            return jsonify({'fout': 'AWIN_FEED_APIKEY ontbreekt'}), 503
        # Bewust ruimer dan sync_coolblue.FEED_COLUMNS: die vraagt alleen op wat
        # de site gebruikt, dus een modelkolom zou nooit meekomen. Dit zijn de
        # AWIN-kolomnamen waar een modelcode in kan zitten.
        extra = ['mpn', 'model_number', 'product_model', 'specifications',
                 'manufacturer_part_number', 'product_short_description']
        origineel = sc.FEED_COLUMNS
        try:
            sc.FEED_COLUMNS = origineel + extra
            records = sc.fetch_feed(apikey)
        finally:
            sc.FEED_COLUMNS = origineel
        velden = beschrijf(records[:grens])
    else:
        from flask import abort
        abort(404)

    # Het cijfer dat beslist: hoeveel van onze producten krijgen hier een
    # modelcode uit die ze nu niet hebben? Zonder dat getal is de rest een
    # opsomming van velden zonder opbrengst.
    from product_specs import modelnummer
    onze = {(p.ean or '').strip().lstrip('0'): p
            for p in Product.query.filter_by(is_available=True).all()}
    ean_veld = {'mediamarkt': 'identifiers.ean', 'coolblue': 'ean'}[winkel]
    code_velden = [v['veld'] for v in velden
                   if any(w in v['veld'].lower() for w in ('model', 'mpn'))
                   and v['gevuld']]

    def plat(r):
        uit = dict(r)
        for sleutel in ('identifiers', 'attributes'):
            genest = r.get(sleutel)
            if isinstance(genest, dict):
                uit.update({f'{sleutel}.{k}': v for k, v in genest.items()})
        return uit

    opbrengst = {veld: {'gematcht': 0, 'model_nu_leeg': 0, 'voorbeelden': []}
                 for veld in code_velden}
    # Per merk bijhouden of de code ook in de producttitel voorkomt. Dat is de
    # beslissende toets: een echte modelaanduiding staat in de titel
    # ("AEG AB51A4DG 5000 Animal"), een interne artikelcode niet ("900 258 69").
    # EPREL registreert op de modelaanduiding, dus alleen het eerste is bruikbaar.
    def kaal(t):
        return ''.join(c for c in str(t or '').upper() if c.isalnum())

    def is_modelcode(waarde, titel, merk):
        """Is dit een kale modelaanduiding, of iets anders?

        Twee eisen, en de tweede is er bijgekomen na een misleidend cijfer.
        MediaMarkt's model-veld bleek de volledige productnaam te bevatten
        ("Sharp Qwna1bf47eweu Vaatwasser - Vrijstaand"), waardoor de toets
        "staat de code in de titel" automatisch slaagde en 78% opleverde. Dat
        was een artefact van de meting, geen bruikbare code.

        1. De code komt voor in de titel -- twee onafhankelijke bronnen die
           hetzelfde zeggen, dus geen gok.
        2. De code is kort en bevat geen woorden. Een modelaanduiding is
           AB51A4DG of WGG244FONL, en soms "Fe 1404-20" -- Liebherr zet er een
           spatie in. Eerst wees deze toets alles met een spatie af, en daarmee
           verdween Liebherr van 68% naar 2%. Hooguit een spatie dus, en de
           lengtegrens houdt de volledige productnamen van MediaMarkt buiten
           ("AEG Tr868mb4b - Warmtepompdroger 8 Kg 63 Db" is te lang).

        EPREL registreert op de modelaanduiding, dus alleen dit is bruikbaar.
        """
        tekst = str(waarde or '').strip()
        if not (4 <= len(tekst) <= 20):
            return False
        if tekst.count(' ') > 1:
            return False
        if kaal(merk) and kaal(merk) in kaal(tekst):
            return False
        k = kaal(tekst)
        if len(k) < 4 or k not in kaal(titel):
            return False
        if not any(c.isdigit() for c in k):
            return False
        return True

    per_merk = {}
    gematcht_totaal = 0
    for r in records:
        vlak = plat(r)
        ean = str(vlak.get(ean_veld) or '').strip().lstrip('0')
        product = onze.get(ean)
        if not product:
            continue
        gematcht_totaal += 1
        for veld in code_velden:
            waarde = vlak.get(veld)
            waarde = waarde[0] if isinstance(waarde, list) and waarde else waarde
            waarde = str(waarde or '').strip()
            if not waarde:
                continue
            opbrengst[veld]['gematcht'] += 1
            merk = (product.brand or 'onbekend').strip()
            tel = per_merk.setdefault(merk, {'met_code': 0, 'in_titel': 0,
                                             'voorbeeld': None})
            tel['met_code'] += 1
            if is_modelcode(waarde, product.title, merk):
                tel['in_titel'] += 1
            elif tel['voorbeeld'] is None:
                tel['voorbeeld'] = {'code': waarde[:30],
                                    'titel': (product.title or '')[:45]}
            if not modelnummer(product):
                opbrengst[veld]['model_nu_leeg'] += 1
                if len(opbrengst[veld]['voorbeelden']) < 5:
                    opbrengst[veld]['voorbeelden'].append(
                        {'titel': (product.title or '')[:60], 'code': waarde[:40]})

    return jsonify({'winkel': winkel, 'records_in_feed': len(records),
                    'velden_beschreven_over': min(grens, len(records)),
                    'onze_producten_gevonden': gematcht_totaal,
                    'opbrengst_per_veld': opbrengst,
                    'bruikbare_modelcodes_per_merk': dict(sorted(
                        per_merk.items(), key=lambda x: -x[1]['met_code'])[:25]),
                    'velden': velden})


# Versie van de proefteksten. Elke geschreven tekst wordt onder deze sleutel
# opgeslagen en bij een volgend bezoek hergebruikt. Daardoor kost dit eindpunt
# eenmalig geld en daarna niets meer, hoe vaak het ook wordt aangeroepen -- dat
# is bewust de beveiliging, in plaats van een wachtwoord in de URL dat in
# serverlogs en browsergeschiedenis blijft staan. Opnieuw laten schrijven met
# een aangepaste instructie? Verhoog het nummer. Dat vraagt een deploy, en dat
# is precies de bedoelde drempel.
#
# v2: prijszinnen gaan niet meer mee de prompt in (v1 leverde drie teksten met
# een prijsoordeel, en die worden onwaar zodra de prijs beweegt), en elke tekst
# gaat door ai_content.controleer.
_PROEF_VERSIE = 'proef-v2'

# Hoeveel teksten er hoogstens in een enkel verzoek geschreven mogen worden.
# Naast de geldgrens per etmaal (config.AI_DAGLIMIET_EURO), want die grens
# merkt een lus pas als het geld op is; deze merkt hem meteen.
_MAX_NIEUW_PER_AANROEP = 25


def _proefselectie(limiet=16):
    """Producten die samen de breedte van de catalogus laten zien.

    Per categorie eentje met veel specificaties en eentje zonder. Die tweede
    groep is de belangrijkste van de proef: 65% van de catalogus heeft geen
    enkele specificatie, en juist daar moet blijken of er een eerlijke korte
    tekst uitkomt of opgeklopte vulling. Tien mooie producten uitkiezen zou een
    vertekend beeld geven van wat dit gaat kosten en opleveren.

    Vaste volgorde op id, zodat de selectie bij elke aanroep dezelfde is en de
    opgeslagen teksten dus ook echt hergebruikt worden.
    """
    # Eerst de producten die al een proeftekst hebben. Zonder dit koos deze
    # functie bij elke aanroep opnieuw, en omdat is_available na een sync
    # verschuift viel die keuze soms anders uit -- waarna er teksten bij
    # geschreven werden voor producten die er nog niet bij zaten. Gemeten op
    # productie: 17 rijen voor proef-v1 en 28 voor proef-v2, terwijl het er
    # 10 en 16 hadden moeten zijn. Klein bedrag, maar het is het begin van een
    # generator die zichzelf blijft voeden.
    from models import AIContent

    bestaand = [r.product_id for r in
                AIContent.query.filter_by(content_type=_PROEF_VERSIE)
                .order_by(AIContent.product_id).all() if r.product_id]
    gekozen = [p for p in Product.query.filter(Product.id.in_(bestaand)).all()] \
        if bestaand else []
    gezien = {p.id for p in gekozen}
    if len(gekozen) >= limiet:
        return gekozen[:limiet]

    for categorie in Category.query.order_by(Category.id).all():
        producten = (Product.query
                     .filter_by(category_id=categorie.id, is_available=True)
                     .order_by(Product.id).limit(150).all())
        rijk = [p for p in producten if len(p.specs or {}) >= 8]
        kaal = [p for p in producten if not (p.specs or {})]
        for kandidaat in rijk[:1] + kaal[:1]:
            if kandidaat.id not in gezien:
                gezien.add(kandidaat.id)
                gekozen.append(kandidaat)
    return gekozen[:limiet]


@main_bp.route('/api/tekstproef')
def tekstproef():
    """Tien eigen productbeschrijvingen, met de kosten erbij.

    Aanleiding: de bodytekst op de productpagina is de beschrijving van de
    leverancier en staat woordelijk ook bij Bol en bij de fabrikant. Google
    sloeg 100 van 449 beoordeelde pagina's over met "gecrawld, momenteel niet
    geindexeerd" -- een oordeel over de inhoud. Dit is de proef of eigen tekst
    beter is, en wat de hele catalogus zou kosten.

    Schrijft niets naar de productpagina's. De teksten komen in de tabel
    ai_content onder een eigen soort (zie _PROEF_VERSIE) en zijn nergens op de
    site zichtbaar. Product.ai_description blijft onaangeroerd.
    """
    from flask import jsonify, render_template_string

    from ai_content import (Budgetstop, TekstFout, besteed_vandaag,
                            bewaak_budget, controleer, moet_herschrijven,
                            schrijf_beschrijving)
    from models import AIContent, db

    sleutel = current_app.config.get('ANTHROPIC_API_KEY')
    if not sleutel:
        return jsonify({'fout': 'ANTHROPIC_API_KEY ontbreekt'}), 503

    producten = _proefselectie()
    bewaard = {r.product_id: r for r in
               AIContent.query.filter_by(content_type=_PROEF_VERSIE).all()}

    regels, nieuw_euro, nieuw_aantal = [], 0.0, 0
    for product in producten:
        rij, fout = bewaard.get(product.id), None
        # Niet "is er al een tekst?" maar "klopt de tekst nog bij de data?".
        # Een product dat er specificaties bij kreeg, krijgt een nieuwe tekst;
        # de rest komt uit de opslag en kost niets.
        if moet_herschrijven(product, rij):
            try:
                # Twee remmen voor elke aanroep, niet een keer vooraf: een lus
                # die duizend teksten maakt moet halverwege stoppen, niet pas
                # de volgende keer dat er iemand langskomt.
                if nieuw_aantal >= _MAX_NIEUW_PER_AANROEP:
                    raise Budgetstop(f"meer dan {_MAX_NIEUW_PER_AANROEP} nieuwe "
                                     f"teksten in een verzoek")
                bewaak_budget(current_app.config['AI_DAGLIMIET_EURO'])
                uitkomst = schrijf_beschrijving(
                    product,
                    model=current_app.config.get('ANTHROPIC_MODEL'),
                    api_key=sleutel)
            except Budgetstop as e:
                fout = f'gestopt door de noodrem -- {e}'
            except TekstFout as e:
                fout = str(e)
            except Exception as e:  # netwerk, ongeldige sleutel, limiet
                current_app.logger.exception("tekstproef: %s", product.slug)
                fout = f'{type(e).__name__}: {e}'
            else:
                k = uitkomst['kosten']
                # De oude tekst gaat weg: er hoort er per product en soort
                # precies een te zijn, anders bouwt elke herschrijving een
                # tweede rij op die niemand meer opruimt.
                if rij is not None:
                    db.session.delete(rij)
                rij = AIContent(
                    product_id=product.id, content_type=_PROEF_VERSIE,
                    content=uitkomst['tekst'],
                    tokens_used=(k['invoer'] + k['uitvoer']
                                 + k['cache_geschreven'] + k['cache_gelezen']),
                    cost=k['euro'], bron_specs=uitkomst['bron_specs'])
                db.session.add(rij)
                db.session.commit()
                nieuw_euro += k['euro']
                nieuw_aantal += 1

        regels.append({
            'titel': product.title,
            'slug': product.slug,
            'merk': product.brand,
            'categorie': product.category.name if product.category else '',
            'aantal_specs': len(product.specs or {}),
            # Lege regels scheiden de alinea's; het model levert platte tekst.
            'alineas': [a.strip() for a in (rij.content if rij else '').split('\n\n')
                        if a.strip()],
            'woorden': len((rij.content if rij else '').split()),
            'euro': rij.cost if rij else None,
            'fout': fout,
            # De zeef draait bij elk bezoek opnieuw, ook over teksten die uit de
            # opslag komen. Zo verandert een strengere regel meteen het oordeel
            # over alles wat er al ligt, zonder opnieuw te hoeven schrijven.
            'controle': controleer(rij.content) if rij else [],
        })

    gelukt = [r for r in regels if not r['fout']]
    schoon = [r for r in gelukt if not r['controle']]
    gemiddeld = (sum(r['euro'] or 0 for r in gelukt) / len(gelukt)) if gelukt else 0
    catalogus = Product.query.filter_by(is_available=True).count()

    return render_template_string(_PROEF_PAGINA, regels=regels, gelukt=len(gelukt),
                                  schoon=len(schoon),
                                  nieuw_aantal=nieuw_aantal,
                                  nieuw_euro=round(nieuw_euro, 4),
                                  gemiddeld=gemiddeld, catalogus=catalogus,
                                  raming=gemiddeld * catalogus,
                                  model=current_app.config.get('ANTHROPIC_MODEL'),
                                  versie=_PROEF_VERSIE,
                                  besteed=besteed_vandaag(),
                                  daglimiet=current_app.config['AI_DAGLIMIET_EURO'],
                                  maxnieuw=_MAX_NIEUW_PER_AANROEP,
                                  # Expliciet meegeven in plaats van leunen op
                                  # een default in het sjabloon: die default gold
                                  # maar op een van de drie plekken, waardoor de
                                  # proefpagina de tekst van de nalees-pagina liet
                                  # zien.
                                  is_proef=True, zichtbaar=0)


# Bewust een sjabloon in dit bestand en niet in templates/: dit is tijdelijk
# gereedschap dat na de beslissing in zijn geheel weg kan, en dan hoort er geen
# los bestand achter te blijven.
_PROEF_PAGINA = """<!doctype html><html lang="nl"><meta charset="utf-8">
<title>Tekstproef</title><meta name="robots" content="noindex">
<style>
 body{font:16px/1.6 system-ui,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem;color:#1a1a1a}
 h1{font-size:1.5rem} h2{font-size:1.05rem;margin:0 0 .2rem}
 .kop{background:#f4f4f5;border:1px solid #e4e4e7;border-radius:6px;padding:1rem 1.25rem;margin-bottom:2rem}
 .kop b{font-size:1.2rem}
 article{border-top:1px solid #e4e4e7;padding-top:1.25rem;margin-top:1.75rem}
 .meta{color:#71717a;font-size:.85rem;margin-bottom:.9rem}
 .fout{background:#fef2f2;border-left:3px solid #dc2626;padding:.6rem .9rem;color:#991b1b}
 .vlag{background:#fffbeb;border-left:3px solid #d97706;padding:.6rem .9rem;margin:.8rem 0;font-size:.9rem}
 .vlag b{color:#92400e} .vlag ul{margin:.35rem 0 0;padding-left:1.1rem}
 p.tekst{margin:.7rem 0}
</style>
<h1>Tekstproef &mdash; {{ gelukt }} van {{ regels|length }} geschreven,
    {{ schoon }} door de controle</h1>
<div class=kop>
  <p>Model: <code>{{ model }}</code> &middot; opgeslagen als <code>{{ versie }}</code>.</p>
  {% if is_proef %}
  <p>Deze teksten staan <b>nergens op de site</b>; ze zitten alleen in de tabel
     <code>ai_content</code>.</p>
  {% else %}
  <p><b>{{ zichtbaar }}</b> van de {{ catalogus }} leverbare producten tonen op
     dit moment hun eigen tekst. De rest valt terug op de beschrijving van de
     winkel: producten zonder tekst, en teksten die de controle heeft
     aangestreept.</p>
  {% endif %}
  <p>Nu nieuw geschreven: {{ nieuw_aantal }} stuks, kosten
     &euro;&nbsp;{{ '%.4f'|format(nieuw_euro) }}. De rest kwam uit de opslag en
     kostte niets &mdash; herladen van deze pagina kost dus ook niets.</p>
  {% if is_proef %}
  <p>Gemiddeld &euro;&nbsp;{{ '%.4f'|format(gemiddeld) }} per tekst.
     Voor alle {{ catalogus }} leverbare producten:
     <b>&euro;&nbsp;{{ '%.2f'|format(raming) }}</b>, of ongeveer
     <b>&euro;&nbsp;{{ '%.2f'|format(raming / 2) }}</b> met de Batch API
     (50% korting, teksten binnen 24 uur klaar).</p>
  {% else %}
  <p>Gemiddeld &euro;&nbsp;{{ '%.4f'|format(gemiddeld) }} per tekst,
     samen <b>&euro;&nbsp;{{ '%.2f'|format(raming) }}</b> tot nu toe.
     Van de {{ catalogus }} leverbare producten hebben er zoveel al een tekst
     als hierboven staat.</p>
  {% endif %}
  {% if is_proef %}
  <p><b>Noodrem:</b> &euro;&nbsp;{{ '%.2f'|format(besteed) }} van de
     &euro;&nbsp;{{ '%.2f'|format(daglimiet) }} die er per etmaal uitgegeven
     mag worden, en hoogstens {{ maxnieuw }} nieuwe teksten per verzoek.
     Daarboven stopt het uit zichzelf. Die grens geldt voor deze proefpagina en
     voor de routine die nieuwe producten bijwerkt &mdash; niet voor een batch,
     die wordt met de hand gestart.</p>
  {% endif %}
</div>
{% for r in regels %}
<article>
  <h2>{{ r.titel }}</h2>
  <p class=meta>{{ r.categorie }}{% if r.merk %} &middot; {{ r.merk }}{% endif %}
     &middot; {{ r.aantal_specs }} specificaties in de feed
     {%- if not r.fout %} &middot; {{ r.woorden }} woorden &middot;
     &euro;&nbsp;{{ '%.4f'|format(r.euro or 0) }}{% endif %}
     &middot; <a href="{{ url_for('products.product_detail', slug=r.slug) }}">bekijk de pagina</a></p>
  {% if r.fout %}<p class=fout>Mislukt: {{ r.fout }}</p>
  {% else %}
    {% if r.controle %}<div class=vlag><b>Controle: {{ r.controle|length }}
      zin(nen) tegen een harde regel</b><ul>
      {% for v in r.controle %}<li>{{ v.reden }}: &ldquo;{{ v.zin }}&rdquo;</li>{% endfor %}
      </ul></div>{% endif %}
    {% for alinea in r.alineas %}<p class=tekst>{{ alinea }}</p>{% endfor %}
  {% endif %}
</article>
{% endfor %}
</html>"""


# De soort waaronder de echte, voor de site bedoelde beschrijvingen staan --
# los van proef-v2, zodat de proefteksten niet per ongeluk live gaan.
_TEKST_SOORT = 'beschrijving'
# Een rij met deze soort is de administratie van een lopende batch: content is
# het batch-id. Bewust geen nieuwe tabel voor een veld dat hooguit een dag
# bestaat.
_BATCH_SOORT = 'batch-lopend'

# Batchstatus kort onthouden: /api/teksten/diagnose is openbaar, en zonder
# rem zou elke bezoeker een aanroep naar Anthropic veroorzaken.
_BATCHSTATUS_CACHE = {}


def _beheerslot():
    """None als de aanroeper langs mag, anders een (json, status) om terug te geven.

    Zonder AI_BEHEER_SLEUTEL in de omgeving bestaan deze eindpunten praktisch
    niet. Dat is met opzet de standaard: een openbaar adres dat een rekening
    kan opbouwen hoort niet te bestaan zolang niemand het nodig heeft. Zet de
    variabele voor de uitrol, haal hem daarna weg.
    """
    import secrets

    from flask import jsonify

    verwacht = current_app.config.get('AI_BEHEER_SLEUTEL')
    if not verwacht:
        return jsonify({'fout': 'beheereindpunten staan uit',
                        'uitleg': 'zet AI_BEHEER_SLEUTEL in de omgeving'}), 503
    # compare_digest en niet ==: een gewone vergelijking stopt bij het eerste
    # verschillende teken, en dat verschil in tijd is genoeg om een sleutel
    # teken voor teken te raden.
    gegeven = request.args.get('sleutel', '')
    if not secrets.compare_digest(gegeven, verwacht):
        return jsonify({'fout': 'ongeldige of ontbrekende sleutel'}), 403
    return None


def _zonder_tekst(limiet):
    """Leverbare producten die nog geen beschrijving hebben, op id.

    Vaste volgorde, zodat een tweede batch verdergaat waar de eerste ophield
    in plaats van dezelfde producten opnieuw te doen.
    """
    from models import AIContent

    klaar = {r.product_id for r in
             AIContent.query.filter_by(content_type=_TEKST_SOORT).all()}
    uit = []
    for product in Product.query.filter_by(is_available=True).order_by(Product.id):
        if product.id not in klaar:
            uit.append(product)
            if len(uit) >= limiet:
                break
    return uit


@main_bp.route('/api/teksten/start')
def teksten_start():
    """Levert een batch beschrijvingen in bij Anthropic. Schrijft niets live.

    Twee sloten, want dit geeft geld uit: bevestig=ja moet in de URL staan, en
    er mag er maar een tegelijk lopen. Het aantal is begrensd zodat een typefout
    in de URL niet de hele catalogus inlevert.

    De uitkomst komt niet hier binnen -- een batch mag tot 24 uur duren. Haal
    hem op met /api/teksten/ophalen.
    """
    from flask import jsonify

    from ai_content import TekstFout, dien_batch_in
    from models import AIContent, db

    geweigerd = _beheerslot()
    if geweigerd:
        return geweigerd

    sleutel = current_app.config.get('ANTHROPIC_API_KEY')
    if not sleutel:
        return jsonify({'fout': 'ANTHROPIC_API_KEY ontbreekt'}), 503
    if request.args.get('bevestig') != 'ja':
        return jsonify({'fout': 'ontbrekende bevestiging',
                        'uitleg': 'voeg ?bevestig=ja toe; dit geeft geld uit'}), 400

    lopend = AIContent.query.filter_by(content_type=_BATCH_SOORT).first()
    if lopend:
        return jsonify({'fout': 'er loopt al een batch',
                        'batch_id': lopend.content,
                        'uitleg': 'haal die eerst op met /api/teksten/ophalen'}), 409

    aantal = min(max(request.args.get('aantal', 50, type=int), 1), 3000)
    producten = _zonder_tekst(aantal)
    if not producten:
        return jsonify({'klaar': True,
                        'melding': 'elk leverbaar product heeft al een tekst'})

    try:
        batch_id = dien_batch_in(producten,
                                 model=current_app.config.get('ANTHROPIC_MODEL'),
                                 api_key=sleutel)
    except TekstFout as e:
        return jsonify({'fout': str(e)}), 400
    except Exception as e:
        current_app.logger.exception("batch inleveren mislukt")
        return jsonify({'fout': f'{type(e).__name__}: {e}'}), 502

    db.session.add(AIContent(product_id=None, content_type=_BATCH_SOORT,
                             content=batch_id, cost=0.0))
    db.session.commit()
    return jsonify({'batch_id': batch_id, 'ingeleverd': len(producten),
                    'nog_zonder_tekst': len(_zonder_tekst(3000)),
                    'volgende_stap': '/api/teksten/ophalen'})


@main_bp.route('/api/teksten/ophalen')
def teksten_ophalen():
    """Kijkt of de batch klaar is en slaat de teksten op. Nog steeds niet live.

    Veilig om vaker aan te roepen: zolang de batch niet klaar is verandert er
    niets, en na het opslaan is de administratierij weg zodat er niets dubbel
    binnenkomt.
    """
    from flask import jsonify

    from ai_content import (batch_resultaten, batch_toestand, controleer,
                            telbare_specs)
    from models import AIContent, db

    geweigerd = _beheerslot()
    if geweigerd:
        return geweigerd

    sleutel = current_app.config.get('ANTHROPIC_API_KEY')
    if not sleutel:
        return jsonify({'fout': 'ANTHROPIC_API_KEY ontbreekt'}), 503

    lopend = AIContent.query.filter_by(content_type=_BATCH_SOORT).first()
    if not lopend:
        return jsonify({'fout': 'er loopt geen batch'}), 404

    # Het id apart zetten voordat er iets met de rij gebeurt: na een delete +
    # commit is het object leeg en levert lopend.content een uitzondering op.
    # Dat was fout nummer een in de eerste versie -- de melding kwam pas na het
    # opslaan, dus hij leek onschuldig, maar hij verbergt wel elke fout die
    # ervoor gebeurt.
    batch_id = lopend.content

    try:
        toestand = batch_toestand(batch_id, sleutel)
    except Exception as e:
        current_app.logger.exception("batchstatus opvragen mislukt")
        return jsonify({'fout': f'{type(e).__name__}: {e}'}), 502
    if not toestand['klaar']:
        return jsonify({'batch_id': batch_id, 'klaar': False, **toestand})

    # Wat er al ligt slaan we over. Bij 2756 teksten duurt het opslaan minuten
    # en kapt Railway een te lang verzoek af; elke tekst wordt meteen
    # vastgelegd, dus dan is het werk tot dat punt binnen. Zonder deze regel
    # begint een tweede poging weer vooraan en loopt hij op dezelfde plek weer
    # vast. Nu boekt elke poging vooruitgang tot het een keer af is.
    al_aanwezig = {r.product_id for r in
                   AIContent.query.filter_by(content_type=_TEKST_SOORT).all()}

    opgeslagen, overgeslagen, mislukt, gevlagd, euro = 0, 0, [], 0, 0.0
    try:
        for uitkomst in batch_resultaten(batch_id, sleutel):
            if uitkomst['product_id'] in al_aanwezig:
                overgeslagen += 1
                continue
            # Per uitkomst een eigen vangnet. Een van de vijftig kan een vorm
            # hebben die de rest van de lus omgooit, en dan zou een enkel raar
            # antwoord de negenenveertig goede meesleuren -- terwijl die al
            # betaald zijn.
            try:
                if uitkomst['fout']:
                    mislukt.append({'product_id': uitkomst['product_id'],
                                    'fout': uitkomst['fout']})
                    continue
                # Per id opzoeken in plaats van de hele catalogus in het
                # geheugen: Product.query.all() zijn 2806 rijen met specs-JSON
                # en beschrijvingsteksten, en we hebben er vijftig nodig.
                product = Product.query.get(uitkomst['product_id'])
                if product is None:
                    mislukt.append({'product_id': uitkomst['product_id'],
                                    'fout': 'product bestaat niet meer'})
                    continue
                # Al een tekst? Dan die weg -- een product hoort er precies een
                # te hebben, anders stapelen herhaalde batches rijen op.
                AIContent.query.filter_by(product_id=product.id,
                                          content_type=_TEKST_SOORT).delete()
                k = uitkomst['kosten']
                db.session.add(AIContent(
                    product_id=product.id, content_type=_TEKST_SOORT,
                    content=uitkomst['tekst'],
                    tokens_used=(k['invoer'] + k['uitvoer']
                                 + k['cache_geschreven'] + k['cache_gelezen']),
                    cost=k['euro'], bron_specs=telbare_specs(product)))
                # Meteen vastleggen, niet per 25. De rollback hieronder gooit
                # alles weg wat nog niet is vastgelegd, dus met een blok van 25
                # sleepte een mislukte tekst de goede voor hem alsnog mee. In de
                # test stond er 'opgeslagen: 2' terwijl er 1 in de database
                # zat -- een melding die zichzelf tegenspreekt.
                db.session.commit()
                opgeslagen += 1
                euro += k['euro']
                if controleer(uitkomst['tekst']):
                    gevlagd += 1
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception(
                    "tekst verwerken mislukt voor %s", uitkomst.get('product_id'))
                mislukt.append({'product_id': uitkomst.get('product_id'),
                                'fout': f'{type(e).__name__}: {e}'})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("batchuitkomst verwerken mislukt")
        # De administratierij blijft staan, dus opnieuw proberen kan gewoon
        # nadat de oorzaak weg is. Batchuitkomsten blijven 29 dagen ophaalbaar.
        return jsonify({'fout': f'{type(e).__name__}: {e}',
                        'batch_id': batch_id,
                        'opgeslagen_voor_de_fout': opgeslagen,
                        'uitleg': 'de batch blijft staan; opnieuw ophalen kan'}), 500

    db.session.delete(lopend)
    db.session.commit()
    return jsonify({'batch_id': batch_id, 'klaar': True,
                    'opgeslagen': opgeslagen,
                    'overgeslagen_want_al_aanwezig': overgeslagen,
                    'gevlagd_door_controle': gevlagd,
                    'mislukt': mislukt[:25], 'aantal_mislukt': len(mislukt),
                    'kosten_euro': round(euro, 4),
                    'nog_zonder_tekst': len(_zonder_tekst(3000)),
                    'nalezen': '/api/teksten/nalezen'})


# Antwoorden van Bol kort onthouden: dit eindpunt is openbaar, en zonder rem
# zou elke bezoeker een aanroep naar de Bol-API veroorzaken. Zelfde patroon
# als _BATCHSTATUS_CACHE hierboven.
_BOL_AANBOD_CACHE = {}
_BOL_AANBOD_TTL = 10 * 60

# Hoeveel dagen vóór het gevraagde venster er nog prijsregels worden
# opgehaald, zodat elke reeks zijn vorige prijs heeft. price_history bewaart
# alleen wijzigingen: een prijs die maanden stilstaat heeft binnen een kort
# venster geen voorganger, en dan valt een sprong stilzwijgend weg.
_SPRONG_TERUGKIJK_DAGEN = 180

# Hoe kort een prijs moet terugkeren om als terugsprong te tellen. Een
# feedfout is binnen een dag hersteld (de SMEG combi-oven waarvoor deze
# meting is gebouwd ging op 29-07 heen en op 30-07 terug); een aanbieding
# duurt weken. Zonder dit venster kreeg elke aflopende actie het stempel
# 'teruggesprongen' -- 9 van de 9 op 31 aug -- en dan zegt het niets meer.
_TERUGSPRONG_VENSTER_DAGEN = 2


# Welke EPREL-velden een filterpagina waard zijn, met de indeling in
# stappen waarop een koper zoekt. Niet elk veld leent zich ervoor: een
# energie-efficiëntie-index van 46,8 zegt een koper niets, "stil (onder 70
# dB)" wel.
#
# De grenzen komen uit hoe mensen zoeken, niet uit de spreiding van de data:
# "wasmachine 9 kg", "1400 toeren", "stille vaatwasser". Vandaar ronde
# getallen en niet de kwartielen van onze eigen catalogus.
# Elke stap heeft naast de meetgrenzen ook een 'slug' (het vaste stuk van het
# webadres -- nooit meer wijzigen, anders breken geïndexeerde URL's) en een
# 'kop' met {cat} erin, die de paginatitel wordt ("Zeer stille wasmachines").
_FILTERVELDEN = {
    'noise': {
        'naam': 'geluid',
        'eenheid': 'dB',
        'stappen': [
            {'van': None, 'tot': 45, 'slug': 'zeer-stil',
             'label': 'zeer stil (tot 45 dB)', 'kop': 'Zeer stille {cat} (tot 45 dB)'},
            {'van': 45, 'tot': 60, 'slug': 'stil',
             'label': 'stil (45-60 dB)', 'kop': 'Stille {cat} (45-60 dB)'},
            {'van': 60, 'tot': 72, 'slug': 'gemiddeld-geluid',
             'label': 'gemiddeld (60-72 dB)', 'kop': '{cat} met gemiddeld geluidsniveau (60-72 dB)'},
            {'van': 72, 'tot': None, 'slug': 'vanaf-72-db',
             'label': 'luid (vanaf 72 dB)', 'kop': '{cat} vanaf 72 dB'},
        ],
    },
    'ratedCapacity': {
        'naam': 'vulgewicht',
        'eenheid': 'kg',
        'stappen': [
            {'van': None, 'tot': 7, 'slug': 'tot-7-kg',
             'label': 'tot 7 kg', 'kop': '{cat} tot 7 kg'},
            {'van': 7, 'tot': 8, 'slug': '7-8-kg',
             'label': '7-8 kg', 'kop': '{cat} 7-8 kg'},
            {'van': 8, 'tot': 9, 'slug': '8-9-kg',
             'label': '8-9 kg', 'kop': '{cat} 8-9 kg'},
            {'van': 9, 'tot': 11, 'slug': '9-11-kg',
             'label': '9-11 kg', 'kop': '{cat} 9-11 kg'},
            {'van': 11, 'tot': None, 'slug': 'vanaf-11-kg',
             'label': '11 kg en meer', 'kop': '{cat} van 11 kg en meer'},
        ],
    },
    'spinSpeedRated': {
        'naam': 'toerental',
        'eenheid': 'tpm',
        'stappen': [
            {'van': None, 'tot': 1200, 'slug': 'tot-1200-toeren',
             'label': 'tot 1200 toeren', 'kop': '{cat} tot 1200 toeren'},
            {'van': 1200, 'tot': 1400, 'slug': '1200-1400-toeren',
             'label': '1200-1400 toeren', 'kop': '{cat} met 1200-1400 toeren'},
            {'van': 1400, 'tot': 1600, 'slug': '1400-1600-toeren',
             'label': '1400-1600 toeren', 'kop': '{cat} met 1400-1600 toeren'},
            {'van': 1600, 'tot': None, 'slug': 'vanaf-1600-toeren',
             'label': '1600 toeren en meer', 'kop': '{cat} vanaf 1600 toeren'},
        ],
    },
    'waterCons': {
        'naam': 'waterverbruik',
        'eenheid': 'liter',
        'stappen': [
            {'van': None, 'tot': 10, 'slug': 'tot-10-liter',
             'label': 'tot 10 liter', 'kop': 'Zuinige {cat} (tot 10 liter water)'},
            {'van': 10, 'tot': 45, 'slug': '10-45-liter',
             'label': '10-45 liter', 'kop': '{cat} met waterverbruik 10-45 liter'},
            {'van': 45, 'tot': 55, 'slug': '45-55-liter',
             'label': '45-55 liter', 'kop': '{cat} met waterverbruik 45-55 liter'},
            {'van': 55, 'tot': None, 'slug': 'vanaf-55-liter',
             'label': 'vanaf 55 liter', 'kop': '{cat} met waterverbruik vanaf 55 liter'},
        ],
    },
    'totalVolume': {
        'naam': 'inhoud',
        'eenheid': 'liter',
        'stappen': [
            {'van': None, 'tot': 100, 'slug': 'tot-100-liter',
             'label': 'tot 100 liter', 'kop': 'Kleine {cat} (tot 100 liter)'},
            {'van': 100, 'tot': 250, 'slug': '100-250-liter',
             'label': '100-250 liter', 'kop': '{cat} van 100-250 liter'},
            {'van': 250, 'tot': 350, 'slug': '250-350-liter',
             'label': '250-350 liter', 'kop': '{cat} van 250-350 liter'},
            {'van': 350, 'tot': 450, 'slug': '350-450-liter',
             'label': '350-450 liter', 'kop': '{cat} van 350-450 liter'},
            {'van': 450, 'tot': None, 'slug': 'vanaf-450-liter',
             'label': 'vanaf 450 liter', 'kop': 'Grote {cat} (vanaf 450 liter)'},
        ],
    },
    'dimensionWidth': {
        'naam': 'breedte',
        'eenheid': 'cm',
        'stappen': [
            {'van': None, 'tot': 50, 'slug': 'smal',
             'label': 'smal (tot 50 cm)', 'kop': 'Smalle {cat} (tot 50 cm)'},
            {'van': 50, 'tot': 60, 'slug': '50-60-cm',
             'label': '50-60 cm', 'kop': '{cat} van 50-60 cm breed'},
            {'van': 60, 'tot': 70, 'slug': '60-70-cm',
             'label': '60-70 cm', 'kop': '{cat} van 60-70 cm breed'},
            {'van': 70, 'tot': None, 'slug': 'breed',
             'label': 'breed (vanaf 70 cm)', 'kop': 'Brede {cat} (vanaf 70 cm)'},
        ],
    },
}


def _eprel_waarde(gegevens, veld):
    """Waarde van een EPREL-veld als getal, met maatcorrectie voor de
    afmetingen: koelkasten staan in EPREL in millimeters (breedte 558),
    wasmachines in centimeters (breedte 60). Boven de 250 kunnen het geen
    centimeters zijn -- geen huishoudelijk apparaat is 2,5 meter breed --
    dus dan delen we door tien."""
    try:
        waarde = float((gegevens or {}).get(veld))
    except (TypeError, ValueError):
        return None
    if veld.startswith('dimension') and waarde > 250:
        waarde = waarde / 10.0
    return waarde


def _stap_voor(waarde, opzet):
    """De stap waar deze waarde in valt, of None."""
    for stap in opzet['stappen']:
        if (stap['van'] is None or waarde >= stap['van']) and \
           (stap['tot'] is None or waarde < stap['tot']):
            return stap
    return None

# Onder dit aantal apparaten is een filterpagina niet de moeite waard: een
# pagina met een handvol producten helpt een bezoeker niet en geeft Google
# nog een dunne pagina om te negeren -- precies waar deze site er al 918 van
# heeft.
_MIN_PER_FILTERPAGINA = 8


@main_bp.route('/api/filterkansen')
def filterkansen():
    """Welke filterpagina's zijn er te maken met de EPREL-gegevens? Leest alleen.

    Voorwerk, geen bouwwerk. De concurrent (Knibble) laat filteren op
    geluidsniveau, waterverbruik, kleur en kinderslot; wij hebben 28
    filterpagina's over de hele site. Elk van die pagina's mikt op een echte
    zoekopdracht ("stille wasmachine", "wasmachine 9 kg 1400 toeren"), en dat
    is waar zij hun zoekverkeer halen.

    Dat konden we niet bouwen omdat 65% van de catalogus geen enkele
    specificatie had. Sinds EPREL verandert dat, maar niet overal even snel:
    een oven levert alleen een energieklasse, een wasmachine levert geluid,
    water, vulgewicht en toerental.

    Deze pagina rekent per categorie uit hoeveel apparaten er per filterstap
    zijn, zodat de keuze op aantallen rust en niet op gevoel. Alles onder de
    _MIN_PER_FILTERPAGINA valt af -- een filterpagina met vier producten is
    voor een bezoeker nutteloos en voor Google nog een dunne pagina.
    """
    from flask import jsonify
    from sqlalchemy import func

    from models import Category, EprelData, Product, db

    rijen = EprelData.query.filter_by(gevonden=True).all()
    if not rijen:
        return jsonify({'melding': 'nog geen EPREL-gegevens opgehaald'})

    producten = {p.id: p for p in Product.query.filter(
        Product.id.in_([r.product_id for r in rijen]),
        Product.is_available.is_(True)).all()}
    categorienaam = {c.id: c.name for c in Category.query.all()}

    # Per categorie per veld per stap tellen.
    tellingen = {}
    per_categorie_totaal = {}
    for rij in rijen:
        product = producten.get(rij.product_id)
        if product is None:
            continue
        cat = categorienaam.get(product.category_id, 'onbekend')
        per_categorie_totaal[cat] = per_categorie_totaal.get(cat, 0) + 1
        gegevens = rij.gegevens or {}
        for veld, opzet in _FILTERVELDEN.items():
            waarde = _eprel_waarde(gegevens, veld)
            if waarde is None:
                continue
            stap = _stap_voor(waarde, opzet)
            if stap is not None:
                sleutel = (cat, opzet['naam'], stap['label'])
                tellingen[sleutel] = tellingen.get(sleutel, 0) + 1

    # Omzetten naar iets leesbaars, en meteen het oordeel erbij.
    kansen, te_dun = [], []
    for (cat, veld, label), aantal in sorted(tellingen.items(),
                                             key=lambda x: -x[1]):
        regel = {'categorie': cat, 'filter': veld, 'stap': label,
                 'apparaten': aantal}
        (kansen if aantal >= _MIN_PER_FILTERPAGINA else te_dun).append(regel)

    # Welke velden vult EPREL eigenlijk per categorie? Dat bepaalt wat er
    # überhaupt te filteren valt, los van de aantallen.
    dekking = {}
    for rij in rijen:
        product = producten.get(rij.product_id)
        if product is None:
            continue
        cat = categorienaam.get(product.category_id, 'onbekend')
        for veld in _FILTERVELDEN:
            if (rij.gegevens or {}).get(veld) not in (None, ''):
                dekking.setdefault(cat, {}).setdefault(
                    _FILTERVELDEN[veld]['naam'], 0)
                dekking[cat][_FILTERVELDEN[veld]['naam']] += 1

    # Filterpagina's per winkel per categorie. Die hebben GEEN EPREL nodig --
    # we weten al welke winkel welk apparaat voert. Gemeten op 01-08:
    # Slimster heeft voor wasmachines alleen al 57 filterpagina's, waaronder
    # per winkel (/wasmachines/coolblue/, /wasmachines/mediamarkt/). Wij
    # hebben er 28 over de hele site.
    #
    # En wij kunnen er iets bij zeggen wat zij niet kunnen: hoe die winkel
    # zich bij dat apparaat verhoudt tot de zes andere.
    from models import Offer

    per_winkel = {}
    rijen_offers = (db.session.query(Product.category_id, Offer.retailer,
                                     func.count(func.distinct(Product.id)))
                    .join(Offer, Offer.product_id == Product.id)
                    .filter(Product.is_available.is_(True),
                            Offer.is_available.is_(True))
                    .group_by(Product.category_id, Offer.retailer).all())
    for categorie_id, winkel, aantal in rijen_offers:
        cat = categorienaam.get(categorie_id, 'onbekend')
        per_winkel.setdefault(cat, {})[winkel] = aantal

    winkelkansen = [
        {'categorie': cat, 'winkel': winkel, 'apparaten': aantal}
        for cat, winkels in per_winkel.items()
        for winkel, aantal in winkels.items()
        if aantal >= _MIN_PER_FILTERPAGINA
    ]
    winkelkansen.sort(key=lambda k: -k['apparaten'])

    return jsonify({
        'uitleg': ('Voorwerk voor filterpagina\'s. Alles vanaf '
                   f'{_MIN_PER_FILTERPAGINA} apparaten is de moeite waard; '
                   'daaronder krijg je een dunne pagina.'),
        'eprel_gekoppeld_en_leverbaar': len(producten),
        'per_categorie': per_categorie_totaal,
        'velden_gevuld_per_categorie': dekking,
        'kansrijk': kansen,
        'te_dun': te_dun[:40],
        'aantal_kansrijk': len(kansen),
        # Kan vandaag al, zonder EPREL.
        'aantal_kansrijk_per_winkel': len(winkelkansen),
        'kansrijk_per_winkel': winkelkansen,
    })


@main_bp.route('/api/eprel')
def eprel_stand():
    """Hoe ver de EPREL-koppeling is, en wat er is binnengekomen. Leest alleen.

    Stap 1 van drie: ophalen en opslaan, zonder dat er iets van op de site
    komt. Deze pagina is de bedoeling van die stap -- eerst zien of de
    gegevens deugen, dan pas beslissen of ze op duizend pagina's mogen.

    Gemeten vooraf op een steekproef van 150 producten (30-07-2026): van de
    apparaten met een EU-energielabel is 65% terug te vinden, wat over de
    hele catalogus neerkomt op ongeveer 1.020 apparaten. Wijkt het cijfer
    hieronder daar sterk vanaf, dan klopt er iets niet aan de koppeling en
    niet aan de schatting.

    Bron van de gegevens: European Product Registry for Energy Labelling
    (EPREL), Europese Commissie.
    """
    from flask import jsonify
    from sqlalchemy import func

    from models import EprelData, Product, db

    totaal = Product.query.filter_by(is_available=True).count()
    opgehaald = EprelData.query.count()
    gevonden = EprelData.query.filter_by(gevonden=True).count()

    # De trefkans hangt volledig af van waarover je hem rekent. Een stofzuiger
    # staat niet in EPREL en kan dus nooit een treffer worden; die meetellen
    # als misser drukt het cijfer met tientallen procenten. Gemeten op 31-07:
    # 48% over alles, terwijl het over de apparaten die er echt in kunnen
    # staan rond de 70% ligt. Daarom hier allebei, met de noemer erbij.
    niet_gezocht = EprelData.query.filter_by(gezocht=False).count()
    gezocht = opgehaald - niet_gezocht
    gemist = gezocht - gevonden

    per_groep = dict(db.session.query(EprelData.productgroep,
                                      func.count(EprelData.id))
                     .filter(EprelData.gevonden.is_(True))
                     .group_by(EprelData.productgroep).all())
    per_klasse = dict(db.session.query(EprelData.energieklasse,
                                       func.count(EprelData.id))
                      .filter(EprelData.gevonden.is_(True))
                      .group_by(EprelData.energieklasse).all())

    # Een handvol treffers om met eigen ogen na te kijken: klopt het merk bij
    # het merk, en het model bij de titel? Daar valt een verkeerde koppeling
    # aan op, en dat is de enige fout die hier echt schaadt.
    rijen = (EprelData.query.filter_by(gevonden=True)
             .order_by(EprelData.id.desc()).limit(15).all())
    producten = {p.id: p for p in Product.query.filter(
        Product.id.in_([r.product_id for r in rijen])).all()} if rijen else {}
    voorbeelden = [{
        'titel': (producten[r.product_id].title or '')[:80]
                 if r.product_id in producten else None,
        'gezocht_op': r.gezocht_op,
        'eprel_model': r.modelnummer,
        'leverancier': r.leverancier,
        'registratienummer': r.registratienummer,
        'energieklasse': r.energieklasse,
        'gegevens': r.gegevens,
    } for r in rijen]

    # Missers zijn net zo leerzaam: staan er veel Miele's tussen, dan is het
    # de spatie in het typenummer en niet EPREL.
    missers = (EprelData.query.filter_by(gevonden=False)
               .order_by(EprelData.id.desc()).limit(15).all())
    mis_producten = {p.id: p for p in Product.query.filter(
        Product.id.in_([r.product_id for r in missers])).all()} if missers else {}
    niet_gevonden = [{
        'titel': (mis_producten[r.product_id].title or '')[:80]
                 if r.product_id in mis_producten else None,
        'gezocht_op': r.gezocht_op or '(geen typenummer of geen energielabel)',
    } for r in missers]

    laatste = (EprelData.query
               .order_by(EprelData.opgehaald_at.desc()).first())

    # Hoe de laatste ronde afliep. Staat 'afgebroken_door' gevuld, dan heeft
    # Brussel ons afgewezen (429 = te veel verzoeken, 403 = geweigerd) of was
    # de dienst onbereikbaar. Zonder dit zou zo'n blokkade eruitzien als "er
    # komt niets bij", en dan zoek je een week later naar de oorzaak.
    try:
        from eprel_bijwerken import LAATSTE_RONDE
        ronde = dict(LAATSTE_RONDE)
    except Exception:
        ronde = None

    return jsonify({
        'laatste_ronde_afloop': ronde,
        'bron': ('European Product Registry for Energy Labelling (EPREL), '
                 'Europese Commissie'),
        'leverbare_producten': totaal,
        'al_opgezocht': opgehaald,
        'nog_te_doen': max(totaal - opgehaald, 0),
        'gevonden': gevonden,
        'niet_gevonden': opgehaald - gevonden,
        # Kan nooit een treffer worden: soort zonder EU-energielabel, of geen
        # typenummer uit de titel te halen. Hoort niet als misser te tellen.
        'kon_niet_gezocht_worden': niet_gezocht,
        'echt_gezocht': gezocht,
        'gezocht_maar_niet_gevonden': gemist,
        # Het cijfer waar het om gaat: van de apparaten die er echt in kunnen
        # staan, hoeveel vinden we terug. Dat andere percentage staat er
        # alleen bij om te laten zien hoeveel het scheelt.
        'trefkans_pct': round(100 * gevonden / gezocht) if gezocht else None,
        'trefkans_over_alles_pct': (round(100 * gevonden / opgehaald)
                                    if opgehaald else None),
        'verwacht_over_hele_catalogus': 1020,
        'per_productgroep': per_groep,
        'per_energieklasse': per_klasse,
        'laatste_ronde': str(laatste.opgehaald_at) if laatste else None,
        'voorbeelden': voorbeelden,
        'voorbeelden_niet_gevonden': niet_gevonden,
    })


@main_bp.route('/api/bol-aanbiedingen')
def bol_aanbiedingen():
    """Wat Bol werkelijk teruggeeft voor één artikel. Leest alleen, koopt niets.

    Aanleiding, gemeten op 30-07 via /api/prijssprongen: van de zeven
    prijssprongen boven de 50% in een week waren er vijf vals (de prijs
    sprong terug), alle vijf bij Bol, en vier van de vijf bij inbouwovens.
    De SMEG SO4301M1N ging drie keer heen en weer tussen EUR 599 en
    EUR 1399.

    De sync leest de prijs als offers[0] -- de eerste aanbieding uit de
    lijst, zonder te kijken welke dat is (sync_products.py, rond regel 476).
    Twee verklaringen passen daarbij, en ze vragen om een andere reparatie:

      a. Bol geeft meerdere aanbiedingen terug en de volgorde wisselt.
         Dan pakken wij de verkeerde en moeten we bewust kiezen.
      b. Bol geeft er één, en die wisselt zelf van verkoper.
         Dan is EUR 599 op dat moment echt de prijs en is er niets kapot --
         hooguit iets om te tonen ("prijs van een andere verkoper").

    Zonder dit te weten is elke reparatie een gok, en gokken op de markup
    heeft in dit project al twee keer dagen gekost. Vandaar deze pagina, en
    pas daarna de keuze.

    Alleen EANs die in onze eigen catalogus staan: anders is dit een gratis
    doorgeefluik naar de Bol-API onder onze sleutel. Antwoorden worden tien
    minuten onthouden.
    """
    import os

    from flask import jsonify
    from models import Offer, Product

    ean = (request.args.get('ean') or '').strip()
    if not ean:
        return jsonify({
            'fout': 'geef een ean mee',
            'voorbeeld': '/api/bol-aanbiedingen?ean=8017709352523',
            'uitleg': 'alleen EANs die in deze catalogus staan',
        }), 400

    product = Product.query.filter_by(ean=ean).first()
    if product is None:
        return jsonify({'fout': 'dit ean staat niet in onze catalogus'}), 404

    nu = time.time()
    gecached = _BOL_AANBOD_CACHE.get(ean)
    if gecached and nu - gecached[0] < _BOL_AANBOD_TTL:
        antwoord = gecached[1]
    else:
        client_id = current_app.config.get('BOL_CLIENT_ID') or os.getenv('BOL_CLIENT_ID')
        geheim = current_app.config.get('BOL_CLIENT_SECRET') or os.getenv('BOL_CLIENT_SECRET')
        if not client_id or not geheim:
            return jsonify({'fout': 'BOL_CLIENT_ID/BOL_CLIENT_SECRET ontbreken'}), 503
        try:
            from sync_products import BolAPI
            api = BolAPI(client_id, geheim)
            if not api.authenticate():
                return jsonify({'fout': 'authenticatie bij Bol mislukt'}), 502
            ruw = api.fetch_product(ean)
        except Exception as e:
            return jsonify({'fout': f'{type(e).__name__}: {e}'}), 502

        if not ruw:
            antwoord = {'bol_kent_dit_ean': False}
        else:
            # Zowel de enkelvoudige als de lijstvorm, precies zoals de sync
            # ze leest -- anders meet je iets anders dan er gebeurt.
            lijst = ruw.get('offers') or ([ruw['offer']] if ruw.get('offer') else [])
            antwoord = {
                'bol_kent_dit_ean': True,
                'vorm': 'offers (lijst)' if ruw.get('offers') else (
                    'offer (enkelvoud)' if ruw.get('offer') else 'geen aanbieding'),
                'aantal_aanbiedingen': len(lijst),
                # Alle velden van de eerste aanbieding, zodat zichtbaar is
                # waarop we zouden kunnen kiezen (conditie, verkoper,
                # voorraad). Geen sleutels of tokens: dit komt uit de
                # productgegevens, niet uit onze configuratie.
                'velden_eerste_aanbieding': sorted(lijst[0].keys()) if lijst else [],
                'aanbiedingen': [{
                    k: v for k, v in aanbod.items()
                    if not isinstance(v, (dict, list))
                } for aanbod in lijst[:10]],
            }
        _BOL_AANBOD_CACHE[ean] = (nu, antwoord)

    onze = Offer.query.filter_by(product_id=product.id, retailer='bol').first()
    return jsonify({
        'ean': ean,
        'titel': (product.title or '')[:120],
        'wat_wij_nu_tonen': {
            'prijs': onze.price if onze else None,
            'laatst_opgehaald': str(onze.last_synced) if onze else None,
        },
        'wat_bol_teruggeeft': antwoord,
        'hoe_de_sync_leest': 'offers[0].price -- de eerste uit de lijst',
    })


@main_bp.route('/api/prijssprongen')
def prijssprongen():
    """Verdachte prijsbewegingen van de afgelopen dagen. Leest alleen.

    De syncs melden een sprong boven de 50% wel in SyncLog.errors, maar
    nemen de prijs daarna gewoon over -- met opzet, want een echte
    stuntprijs bestaat ook en de feed is de bron van de waarheid (zie
    models.prijssprong_melding). Het gevolg is dat zo'n melding verdwijnt
    zodra er vijf nieuwe syncs overheen zijn gegaan, en dat niemand ziet
    of het om een incident of om een patroon gaat.

    Aanleiding: EAN 8017709352523 (SMEG combi-oven) ging op 29-07 van
    EUR 1399 naar EUR 599 en op 30-07 weer terug. Een dag lang stond er
    dus EUR 599 op de site terwijl de winkel EUR 1399 rekende. Dat raakt
    precies waar deze site op drijft.

    Het onderscheid dat deze pagina maakt en het logboek niet:

    - Een echte prijsdaling blijft staan.
    - Een feed-fout springt terug naar (ongeveer) de oude prijs.

    'teruggesprongen' is daarmee het getal om op te letten. Blijft dat op
    nul, dan waren het echte prijzen en is er niets aan de hand.

    Gerekend uit price_history, niet uit de logboekregels: daar staat elke
    echte prijswijziging per winkel in, dus het werkt met terugwerkende
    kracht en over elke periode.
    """
    from datetime import timedelta

    from flask import jsonify
    from models import PriceHistory, Product, utcnow

    dagen = min(max(request.args.get('dagen', 7, type=int), 1), 90)
    drempel = min(max(request.args.get('drempel', 50, type=int), 10), 500) / 100
    grens = utcnow() - timedelta(days=dagen)

    # Ophalen doen we over een veel ruimere periode dan het venster, en dat
    # is geen slordigheid maar de reparatie van een echte fout.
    #
    # De eerste versie haalde alleen rijen uit het venster op. Maar
    # price_history bewaart alleen wijzigingen: staat een prijs al drie weken
    # op EUR 140, dan is er binnen een venster van een dag maar één regel en
    # dus geen paar om te vergelijken. Gemeten op 01-08: het synclogboek
    # meldde drie sprongen van de nacht ervoor (EUR 140 -> 240, 340 -> 540,
    # 220 -> 340) terwijl ?dagen=1 er nul rapporteerde. Een dagelijkse
    # controle die "geen fouten" zegt terwijl er drie zijn, is erger dan
    # geen controle.
    #
    # Dus: de REGELS ruim ophalen zodat elke reeks zijn voorganger heeft, en
    # daarna de SPRONGEN op het venster filteren.
    context_grens = grens - timedelta(days=_SPRONG_TERUGKIJK_DAGEN)
    rijen = (PriceHistory.query
             .filter(PriceHistory.recorded_at >= context_grens)
             .order_by(PriceHistory.product_id, PriceHistory.retailer,
                       PriceHistory.recorded_at).all())

    # Per apparaat per winkel de opeenvolgende prijzen naast elkaar leggen.
    per_reeks = {}
    for rij in rijen:
        per_reeks.setdefault((rij.product_id, rij.retailer), []).append(rij)

    in_venster = sum(1 for r in rijen if r.recorded_at >= grens)

    sprongen = []
    for (product_id, winkel), reeks in per_reeks.items():
        for vorige, huidige in zip(reeks, reeks[1:]):
            if not vorige.price or not huidige.price:
                continue
            # De sprong telt mee als hij IN het venster plaatsvond; de vorige
            # prijs mag van veel eerder zijn.
            if huidige.recorded_at < grens:
                continue
            verhouding = abs(huidige.price - vorige.price) / vorige.price
            if verhouding < drempel:
                continue
            # Hoort deze sprong bij een heen-en-weer? Dat kan op twee
            # manieren, en ze moeten allebei mee -- anders telt van een
            # uitstapje alleen de heenweg en lijkt de terugweg een echte
            # prijswijziging.
            #
            #   de heenweg : later komt de prijs weer op de oude uit
            #   de terugweg: deze prijs stond eerder in deze reeks al
            #
            # Marge van 2%, want winkels ronden af.
            def dichtbij(a, b):
                return bool(b) and abs(a - b) / b <= 0.02

            # ...maar alleen als het heen-en-weer KORT op elkaar zit.
            # Zonder tijdvenster telt ook een actiecyclus mee: de eufy X10
            # Pro stond in juli op EUR 699, ging 11 aug in de actie naar
            # EUR 429 en op 31 aug terug naar EUR 699,99. Dat is geen
            # feedfout maar een aanbieding die afloopt -- en toch werd hij
            # gemarkeerd, omdat die EUR 699 zes weken eerder ook al gold.
            # Gemeten 31 aug: 9 van de 9 sprongen kregen zo het stempel
            # 'teruggesprongen', en een alarm dat altijd afgaat wordt niet
            # meer gelezen.
            #
            # De SMEG combi-oven waar deze meting voor is gebouwd ging
            # binnen EEN DAG heen en terug. Twee etmalen is dus ruim
            # genoeg om een feedfout te vangen en smal genoeg om een
            # actieperiode met rust te laten.
            venster = timedelta(days=_TERUGSPRONG_VENSTER_DAGEN)
            later = [r for r in reeks
                     if huidige.recorded_at < r.recorded_at <= huidige.recorded_at + venster]
            eerder = [r for r in reeks
                     if vorige.recorded_at - venster <= r.recorded_at < vorige.recorded_at]
            terug = (any(dichtbij(r.price, vorige.price) for r in later)
                     or any(dichtbij(r.price, huidige.price) for r in eerder))
            sprongen.append({
                'product_id': product_id,
                'winkel': winkel,
                'van': round(vorige.price, 2),
                'naar': round(huidige.price, 2),
                'verschil_pct': round(100 * verhouding),
                'omhoog': huidige.price > vorige.price,
                'wanneer': str(huidige.recorded_at),
                'teruggesprongen': terug,
            })

    sprongen.sort(key=lambda s: (not s['teruggesprongen'], s['verschil_pct']),
                  reverse=True)

    # Pas hier de producten erbij halen, en in één query: per sprong een
    # losse lookup was de fout die de setprijs-meetpagina liet vastlopen.
    namen = {}
    if sprongen:
        ids = {s['product_id'] for s in sprongen}
        namen = {p.id: p for p in Product.query.filter(Product.id.in_(ids)).all()}
    for s in sprongen:
        product = namen.get(s['product_id'])
        s['titel'] = (product.title or '')[:90] if product else None
        s['ean'] = product.ean if product else None
        s['slug'] = product.slug if product else None

    teruggesprongen = [s for s in sprongen if s['teruggesprongen']]
    return jsonify({
        'periode_dagen': dagen,
        'drempel_pct': round(drempel * 100),
        'prijswijzigingen_in_periode': in_venster,
        # Meer regels dan er in de periode zitten: de vorige prijs van een
        # sprong is vaak ouder dan het venster (zie _SPRONG_TERUGKIJK_DAGEN).
        'prijswijzigingen_bekeken': len(rijen),
        'sprongen': len(sprongen),
        'teruggesprongen': len(teruggesprongen),
        'apparaten_met_een_sprong': len({s['product_id'] for s in sprongen}),
        'lijst': sprongen[:60],
    })


@main_bp.route('/api/teksten/diagnose')
def teksten_diagnose():
    """Wat er werkelijk in de database staat. Leest alleen, geeft niets uit.

    Bewust zonder sleutel: dit kost niets en verandert niets, en juist bij een
    storing wil je niet dat het kijken naar de toestand achter hetzelfde slot
    zit als het veroorzaken ervan.
    """
    from flask import jsonify
    from sqlalchemy import func, inspect

    from models import AIContent, db

    kolommen = [k['name'] for k in inspect(db.engine).get_columns('ai_content')]
    per_soort = dict(db.session.query(AIContent.content_type,
                                      func.count(AIContent.id))
                     .group_by(AIContent.content_type).all())
    lopend = AIContent.query.filter_by(content_type=_BATCH_SOORT).first()

    # Voortgang van een lopende batch mag hier ook staan: het zijn tellingen,
    # geen inhoud, en de server heeft de sleutel al. Zo hoeft de eigenaar niet
    # zelf te blijven pollen met zijn beheersleutel in de adresbalk.
    #
    # Wel met een korte cache: dit is een openbaar adres, en zonder rem zou
    # elke bezoeker een aanroep naar Anthropic veroorzaken.
    voortgang = None
    if lopend:
        nu = time.time()
        gecached = _BATCHSTATUS_CACHE.get(lopend.content)
        if gecached and nu - gecached[0] < 60:
            voortgang = gecached[1]
        else:
            try:
                from ai_content import batch_toestand
                voortgang = batch_toestand(
                    lopend.content, current_app.config.get('ANTHROPIC_API_KEY'))
                _BATCHSTATUS_CACHE[lopend.content] = (nu, voortgang)
            except Exception as e:
                voortgang = {'fout': f'{type(e).__name__}: {e}'}

    # Wanneer de routine voor het laatst langs is geweest. Gelijk aan
    # teksten_bijwerken._MARKERING; hier letterlijk overgenomen omdat dit
    # eindpunt verder niets uit die module gebruikt.
    laatst = AIContent.query.filter_by(
        content_type='routine-laatst-gedraaid').first()

    return jsonify({
        'kolommen_ai_content': kolommen,
        'voortgang_batch': voortgang,
        # De kolom waar de batchroute op schrijft. Ontbreekt hij, dan klapt
        # het opslaan om op een databasefout en is er niets bewaard.
        'bron_specs_aanwezig': 'bron_specs' in kolommen,
        'rijen_per_soort': per_soort,
        'lopende_batch': lopend.content if lopend else None,
        'producten_met_zichtbare_tekst': Product.query.filter(
            Product.ai_description.isnot(None)).count(),
        'leverbare_producten': Product.query.filter_by(is_available=True).count(),
        # De drie hieronder beantwoorden samen de vraag "voorziet de site
        # nieuwe producten nog vanzelf van een eigen tekst?". Zonder deze
        # cijfers zien "de sleutel is weg" en "er valt niets te schrijven" er
        # van buitenaf identiek uit: in beide gevallen komt er niets bij.
        #
        # Alleen of de sleutel er is, nooit welke. Een ja/nee is genoeg om te
        # weten of de routine uberhaupt kan schrijven, en zegt niets wat een
        # bezoeker kan misbruiken.
        'ai_sleutel_aanwezig': bool(current_app.config.get('ANTHROPIC_API_KEY')),
        'leverbaar_zonder_tekst': len(_zonder_tekst(3000)),
        'routine_laatst_gedraaid': (str(laatst.generated_at)
                                    if laatst else None),
    })


# Zinsneden waarmee het model zelf aangaf dat een artikel geen los apparaat is.
# Deze zijn afgeleid uit de 19 teksten die de controle aanstreepte plus de
# steekproef over twaalf categorieen -- niet bedacht maar afgelezen.
_AFWIJKING_PATRONEN = [
    # Let op de valkuil die dit patroon al twee keer heeft gehad.
    #
    # Ronde 1 (55 treffers) nam "twee losse apparaten" kaal mee en pakte
    # daarmee 4 zinnen die er niet horen: "twee ledspots", "twee glazen
    # plateaus", en was-droogcombinaties die juist EEN apparaat zijn ("wast en
    # droogt in een trommel, wat ruimte scheelt ten opzichte van twee losse
    # apparaten").
    #
    # Ronde 2 voegde "(titel|vermelding) noemt" toe om "de titel wijst op een
    # combinatie" te vangen -- en "de winkeltitel noemt" staat in honderden
    # gewone teksten. Dat leverde 46 nieuwe valse treffers op: strikt slechter
    # dan ronde 1. De toets was uitgevoerd op de 55 zinnen die ronde 1 al had
    # gevonden, en zo'n toets kan per definitie geen nieuwe valse treffers
    # laten zien. Toetsen op je eigen vangst bewijst niets.
    #
    # Nu alleen zinsneden die zonder omhaal over twee APPARATEN gaan.
    (r'combinatie van (twee|drie|vier) (losse )?(apparaten|toestellen)|'
     r'betreft geen los apparaat|betreft geen enkel apparaat|'
     r'bestaat (volgens de titel )?uit twee \w*\s*apparaten|'
     r'als (een|één) set wordt aangeboden|'
     r'twee \w+-typenummers|twee modelnummers|'
     r'twee losse apparaten (die samen|naast elkaar)',
     'setje: twee of meer apparaten als een artikel'),
    (r'is geen \w+ maar|gaat niet om een apparaat|betreft geen apparaat|'
     r'dit is geen',
     'geen apparaat: accessoire of onderdeel'),
]


@main_bp.route('/api/catalogus-afwijkingen')
def catalogus_afwijkingen():
    """Artikelen die volgens hun eigen beschrijving geen los apparaat zijn.

    De gegenereerde teksten zijn hier gebruikt als audit. Het model heeft bij
    elk product naar de werkelijke gegevens gekeken en waar het geen los
    apparaat betrof, schreef het dat op -- een setje wasmachine plus droger,
    of een doosje waterfilters onder Koffiemachines. Die zinnen zijn hier
    terug te vinden zonder dat er iets opnieuw gelezen of betaald hoeft te
    worden.

    Waarom dit ertoe doet: zulke artikelen vervuilen de categoriemeting. Een
    filterset van 20 euro telt mee in "de prijs van koffiemachines loopt van
    ... tot ...", en een setje van twee apparaten krijgt een pagina die uitgaat
    van een specificatietabel en een energielabel.

    Leest alleen, geeft niets uit, geen sleutel nodig.
    """
    import re

    from flask import jsonify

    from models import AIContent

    gevonden = {reden: [] for _, reden in _AFWIJKING_PATRONEN}
    producten = {p.id: p for p in Product.query.all()}
    for rij in AIContent.query.filter_by(content_type=_TEKST_SOORT).all():
        product = producten.get(rij.product_id)
        if product is None or not rij.content:
            continue
        for patroon, reden in _AFWIJKING_PATRONEN:
            m = re.search(patroon, rij.content, re.IGNORECASE)
            if m:
                # De hele zin eromheen, want het losse fragment zegt niets.
                zin = next((z for z in re.split(r'(?<=[.!?])\s+', rij.content)
                            if m.group(0).lower() in z.lower()), '')
                gevonden[reden].append({
                    'slug': product.slug,
                    # De EAN erbij: dat is in dit project de identiteit van een
                    # product (de syncs matchen erop), dus dat is waar een
                    # uitzonderingenlijst op moet werken. Een slug verandert
                    # zodra de winkel zijn titel aanpast.
                    'ean': (product.ean or '').strip(),
                    'categorie': product.category.name if product.category else '',
                    'merk': product.brand,
                    'titel': (product.title or '')[:90],
                    'zin': zin.strip()[:200],
                })
                break

    # Tweede, onafhankelijke meting: een setje heeft in de praktijk een plus in
    # de titel ("AEG LR86CB86 + AEG TR86CBC86"). Van de 55 die de teksten
    # aanwezen hadden er 51 zo'n plus, en die 4 zonder waren juist de valse.
    # De vraag die dit beantwoordt: hoeveel producten hebben die plus in totaal?
    # Zit dat rond de 51, dan is de titel op zichzelf een betrouwbaar kenmerk
    # en hoeft er geen lijst met EAN's onderhouden te worden -- ook nieuwe
    # setjes worden dan meteen herkend, zonder deploy.
    met_plus = [p for p in producten.values()
                if p.is_available and ' + ' in (p.title or '')]

    return jsonify({
        'uitleg': 'gevonden door de eigen productteksten te doorzoeken; '
                  'deze artikelen vervuilen de prijsmeting van hun categorie',
        'titeltoets': {
            'uitleg': 'producten met " + " in de titel -- tweede, onafhankelijk '
                      'kenmerk van een setje',
            'aantal': len(met_plus),
            'per_categorie': dict(Counter(
                p.category.name if p.category else '' for p in met_plus)),
            'voorbeelden': [{'slug': p.slug, 'titel': (p.title or '')[:110]}
                            for p in met_plus[:40]],
        },
        'aantallen': {reden: len(rijen) for reden, rijen in gevonden.items()},
        'per_categorie': {
            reden: dict(Counter(r['categorie'] for r in rijen))
            for reden, rijen in gevonden.items()},
        'gevallen': {reden: rijen[:60] for reden, rijen in gevonden.items()},
    })


@main_bp.route('/api/setprijzen')
def setprijzen_meting():
    """Bij hoeveel setjes lukt de vergelijking met de losse apparaten?

    Meten voordat er iets op de site komt. Bij de setjes-herkenning bleek twee
    keer dat een patroon dat op een handvol gevallen goed leek, over de hele
    catalogus iets anders deed. Deze pagina zegt hoe vaak het lukt, waar het
    misgaat, en wat de uitkomsten zijn -- dan is te zien of de zin de moeite
    waard is voordat hij ergens verschijnt.

    Leest alleen, geeft niets uit, geen sleutel nodig.
    """
    from flask import jsonify

    from catalogus_uitzonderingen import SETJE_SLUG
    from setprijs import modelcodes_uit_titel, vergelijk_met_los

    categorie = Category.query.filter_by(slug=SETJE_SLUG).first()
    if categorie is None:
        return jsonify({'fout': 'categorie Apparaatsets bestaat niet'}), 404

    setjes = Product.query.filter_by(category_id=categorie.id,
                                     is_available=True).all()
    gelukt, geen_codes, niet_gevonden = [], [], []
    for product in setjes:
        codes = modelcodes_uit_titel(product.title)
        if not codes:
            geen_codes.append({'slug': product.slug,
                               'titel': (product.title or '')[:95]})
            continue
        uitkomst = vergelijk_met_los(product)
        if uitkomst is None:
            niet_gevonden.append({'slug': product.slug, 'codes': codes,
                                  'titel': (product.title or '')[:95]})
            continue
        gelukt.append({
            'slug': product.slug,
            'titel': (product.title or '')[:80],
            'set': round(uitkomst['set'], 2),
            'los_totaal': round(uitkomst['los_totaal'], 2),
            'verschil': round(uitkomst['verschil'], 2),
            'set_goedkoper': uitkomst['set_goedkoper'],
            'noemenswaardig': uitkomst['noemenswaardig'],
            'gevonden': [{'code': a['code'], 'slug': a['product']['slug'],
                          'prijs': round(a['prijs'], 2)}
                         for a in uitkomst['apparaten']],
        })

    noemenswaardig = [g for g in gelukt if g['noemenswaardig']]
    return jsonify({
        'setjes_totaal': len(setjes),
        'vergelijking_gelukt': len(gelukt),
        'waarvan_noemenswaardig_verschil': len(noemenswaardig),
        'set_goedkoper': sum(1 for g in noemenswaardig if g['set_goedkoper']),
        'los_goedkoper': sum(1 for g in noemenswaardig if not g['set_goedkoper']),
        'mislukt_geen_typenummer': len(geen_codes),
        'mislukt_apparaat_niet_gevonden': len(niet_gevonden),
        'gelukt': gelukt[:40],
        'geen_typenummer': geen_codes[:15],
        'apparaat_niet_gevonden': niet_gevonden[:15],
    })


@main_bp.route('/api/bezorgkosten')
def bezorgkosten_meting():
    """Hoe vaak kennen we bezorgkosten, en zou de volgorde ervan veranderen?

    Aanleiding (1 augustus): Slimster zet de winkels op volgorde van prijs
    inclusief bezorgkosten; wij op kale prijs, met bezorgkosten pas als
    laatste beslisser na de levertijd. Bij een gelijke prijs van E 849 zet
    Slimster de gratis bezorgende winkel boven de winkel met E 10
    bezorgkosten, en wij mogelijk andersom. Of dat bij ons echt voorkomt --
    en hoe vaak -- is de vraag die deze pagina beantwoordt, voordat er aan
    de volgorde gesleuteld wordt.

    Twee winkels leveren geen bezorgkosten in hun feed (MediaMarkt en Bol,
    audit-punt 14); die tellen hier als 'onbekend'. Een wissel waarbij zo'n
    winkel bovenaan staat of komt is dus onzeker, en wordt apart geteld.

    Leest alleen, geeft niets uit, geen sleutel nodig.
    """
    from flask import jsonify

    from levertijd import dagen_tot_levering
    from models import Offer, db

    aanbiedingen = Offer.query.filter_by(is_available=True).all()

    # Per winkel: hoe vaak is het veld gevuld, en wat staat erin?
    per_winkel = {}
    for a in aanbiedingen:
        w = per_winkel.setdefault(a.retailer, {
            'winkel': a.retailer, 'aanbiedingen': 0, 'bekend': 0,
            'gratis': 0, 'betaald': 0, 'hoogste_betaald': None})
        w['aanbiedingen'] += 1
        if a.delivery_cost is not None:
            w['bekend'] += 1
            if a.delivery_cost == 0:
                w['gratis'] += 1
            else:
                w['betaald'] += 1
                if w['hoogste_betaald'] is None or \
                        a.delivery_cost > w['hoogste_betaald']:
                    w['hoogste_betaald'] = a.delivery_cost

    # Per product: wisselt de bovenste winkel als bezorgkosten in de prijs
    # meetellen? Onbekende kosten tellen als nul -- dezelfde aanname die de
    # huidige volgorde al maakt, zodat alleen het verschil tussen de twee
    # volgordes gemeten wordt en niet de aanname zelf.
    per_product = {}
    for a in aanbiedingen:
        per_product.setdefault(a.product_id, []).append(a)

    def kosten(a):
        return a.delivery_cost if a.delivery_cost is not None else 0

    meerdere, wissels, prijsgelijk_bovenaan = 0, [], 0
    for product_id, lijst in per_product.items():
        if len(lijst) < 2:
            continue
        meerdere += 1
        huidig = min(lijst, key=lambda a: (
            a.price, dagen_tot_levering(a.delivery_time), kosten(a),
            a.retailer or ''))
        totaal = min(lijst, key=lambda a: (
            a.price + kosten(a), dagen_tot_levering(a.delivery_time),
            a.retailer or ''))
        laagste = min(a.price for a in lijst)
        if sum(1 for a in lijst if a.price == laagste) > 1:
            prijsgelijk_bovenaan += 1
        if totaal.retailer != huidig.retailer:
            wissels.append({
                'product_id': product_id,
                'nu_bovenaan': huidig.retailer,
                'nu_prijs': huidig.price,
                'nu_bezorgkosten': huidig.delivery_cost,
                'wordt': totaal.retailer,
                'wordt_prijs': totaal.price,
                'wordt_bezorgkosten': totaal.delivery_cost,
                'scheelt_totaal': round(
                    huidig.price + kosten(huidig)
                    - totaal.price - kosten(totaal), 2),
                'onzeker': huidig.delivery_cost is None
                           or totaal.delivery_cost is None,
            })

    # Slugs erbij voor de voorbeelden, in een keer opgehaald.
    voorbeelden = sorted(wissels, key=lambda w: -w['scheelt_totaal'])[:25]
    slugs = dict(db.session.query(Product.id, Product.slug).filter(
        Product.id.in_([w['product_id'] for w in voorbeelden])).all()) \
        if voorbeelden else {}
    for w in voorbeelden:
        w['slug'] = slugs.get(w.pop('product_id'))

    return jsonify({
        'per_winkel': sorted(per_winkel.values(),
                             key=lambda w: -w['aanbiedingen']),
        'producten_met_meerdere_winkels': meerdere,
        'prijs_gelijk_bovenaan': prijsgelijk_bovenaan,
        'bovenste_winkel_wisselt': len(wissels),
        'waarvan_onzeker_door_onbekende_kosten':
            sum(1 for w in wissels if w['onzeker']),
        'scheelt_totaal_opgeteld': round(
            sum(w['scheelt_totaal'] for w in wissels), 2),
        'voorbeelden': voorbeelden,
    })


@main_bp.route('/api/teksten/publiceren')
def teksten_publiceren():
    """Zet de opgeslagen teksten op de productpagina's. Dit is de zichtbare stap.

    Alleen teksten die de controle schoon doorkomen: een aangestreepte tekst
    wordt overgeslagen en blijft in ai_content staan om nagelezen te worden.
    Zolang een product geen eigen tekst heeft, blijft de winkeltekst staan --
    anders zou er tijdens de uitrol bij duizenden producten niets staan.

    ?terugdraaien=ja maakt alles in een keer weer ongedaan. Dat is geen luxe:
    een zichtbare wijziging op 2806 pagina's hoort een knop te hebben waarmee
    hij terug kan zonder dat er iets herschreven of opnieuw betaald hoeft te
    worden. De teksten zelf blijven in ai_content staan.
    """
    from flask import jsonify

    from ai_content import controleer
    from models import AIContent, db

    geweigerd = _beheerslot()
    if geweigerd:
        return geweigerd

    if request.args.get('terugdraaien') == 'ja':
        aantal = (Product.query.filter(Product.ai_description.isnot(None))
                  .update({Product.ai_description: None}, synchronize_session=False))
        db.session.commit()
        return jsonify({'teruggedraaid': aantal,
                        'melding': 'de winkeltekst staat weer op alle pagina\'s; '
                                   'de eigen teksten staan nog in ai_content'})

    rijen = AIContent.query.filter_by(content_type=_TEKST_SOORT).all()
    producten = {p.id: p for p in Product.query.all()}
    gepubliceerd, overgeslagen = 0, []
    for rij in rijen:
        product = producten.get(rij.product_id)
        if product is None or not (rij.content or '').strip():
            continue
        vlaggen = controleer(rij.content)
        if vlaggen:
            overgeslagen.append({'slug': product.slug,
                                 'reden': vlaggen[0]['reden'],
                                 'zin': vlaggen[0]['zin'][:120]})
            continue
        product.ai_description = rij.content
        gepubliceerd += 1
    db.session.commit()

    return jsonify({'gepubliceerd': gepubliceerd,
                    'overgeslagen_door_controle': len(overgeslagen),
                    'overgeslagen': overgeslagen[:25],
                    'nog_zonder_tekst': len(_zonder_tekst(3000)),
                    'terugdraaien': '/api/teksten/publiceren?terugdraaien=ja&sleutel=...'})


@main_bp.route('/api/teksten/nalezen')
def teksten_nalezen():
    """De opgeslagen beschrijvingen, om te lezen voordat ze live gaan.

    ?vlaggen=1 toont alleen wat de controle heeft aangestreept -- dat is de
    lijst die je met de hand naloopt. Zonder filter een pagina van 25.
    """
    from flask import jsonify, render_template_string

    from ai_content import controleer
    from models import AIContent

    alleen_vlaggen = request.args.get('vlaggen') == '1'
    bladzijde = max(request.args.get('p', 1, type=int), 1)

    rijen = (AIContent.query.filter_by(content_type=_TEKST_SOORT)
             .order_by(AIContent.product_id).all())
    if not rijen:
        return jsonify({'melding': 'er staan nog geen beschrijvingen opgeslagen'})

    producten = {p.id: p for p in Product.query.all()}
    alles = []
    for rij in rijen:
        product = producten.get(rij.product_id)
        if product is None:
            continue
        alles.append({
            'titel': product.title, 'slug': product.slug, 'merk': product.brand,
            'categorie': product.category.name if product.category else '',
            'aantal_specs': len(product.specs or {}),
            'alineas': [a.strip() for a in (rij.content or '').split('\n\n') if a.strip()],
            'woorden': len((rij.content or '').split()),
            'euro': rij.cost, 'fout': None,
            'controle': controleer(rij.content or ''),
        })

    gevlagd = [r for r in alles if r['controle']]
    lijst = gevlagd if alleen_vlaggen else alles
    per_blad = 25
    deel = lijst[(bladzijde - 1) * per_blad:bladzijde * per_blad]

    return render_template_string(
        _PROEF_PAGINA, regels=deel, gelukt=len(deel), schoon=len([
            r for r in deel if not r['controle']]),
        nieuw_aantal=0, nieuw_euro=0.0,
        gemiddeld=(sum(r['euro'] or 0 for r in alles) / len(alles)) if alles else 0,
        catalogus=Product.query.filter_by(is_available=True).count(),
        raming=sum(r['euro'] or 0 for r in alles),
        model=current_app.config.get('ANTHROPIC_MODEL'),
        versie=(f"{_TEKST_SOORT} -- {len(alles)} opgeslagen, {len(gevlagd)} "
                f"aangestreept, blad {bladzijde}"),
        besteed=sum(r['euro'] or 0 for r in alles),
        daglimiet=current_app.config['AI_DAGLIMIET_EURO'],
        maxnieuw=_MAX_NIEUW_PER_AANROEP, is_proef=False,
        # Alleen leverbare producten tellen, anders staat er 2782 van 2774 en
        # komt de meter op 101,4% -- producten met een tekst die inmiddels uit
        # de handel zijn telden mee in de teller maar niet in de noemer.
        zichtbaar=Product.query.filter(Product.ai_description.isnot(None),
                                       Product.is_available.is_(True)).count())


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


def _vertrouwenscijfers():
    """Vier controleerbare cijfers over de vergelijker, of None bij twijfel.

    Elk cijfer moet uit de database komen en moet kloppen; ontbreekt er een,
    dan valt dat cijfer weg in plaats van dat er iets geschats verschijnt.
    """
    nu = time.time()
    hit = _CIJFERS_CACHE.get('data')
    if hit and nu - hit[0] < _CIJFERS_TTL:
        return hit[1]

    from models import db, Offer, PriceHistory
    from sqlalchemy import func
    data = {}
    try:
        data['apparaten'] = Product.query.filter_by(is_available=True).count()
        data['winkels'] = db.session.query(Offer.retailer).distinct().count()
        data['prijswijzigingen'] = PriceHistory.query.count()
        eerste = db.session.query(func.min(PriceHistory.recorded_at)).scalar()
        if eerste:
            # Hier opgemaakt en niet in het sjabloon: strftime('%-d') bestaat
            # niet op Windows, en dan valt de homepage lokaal om.
            maanden = ('januari', 'februari', 'maart', 'april', 'mei', 'juni',
                       'juli', 'augustus', 'september', 'oktober', 'november',
                       'december')
            data['volgen_sinds'] = '%d %s %d' % (eerste.day,
                                                 maanden[eerste.month - 1],
                                                 eerste.year)
    except Exception as fout:
        # Een homepage die het doet is belangrijker dan deze cijfers.
        current_app.logger.warning('[!] Vertrouwenscijfers mislukt: %s', fout)
        data = {}

    _CIJFERS_CACHE['data'] = (nu, data)
    return data


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
        cijfers=_vertrouwenscijfers(),
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
        winkel_options=_winkel_facet(category),
        kenmerk_options=_kenmerk_links(category),
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
    # Ruimer dan de 24 van de categoriepagina. Een facetpagina is de kortste
    # route naar zijn producten: via de categoriepagina liggen ze op diepte 3
    # tot 12 (de paginatie heeft alleen vorige/volgende, dus Google moet zich
    # er stap voor stap doorheen klikken), via het merkfacet op diepte 2.
    # Kapte dat facet ook op 24 af, dan bleef die winst weg: 31 facetten zijn
    # groter dan 24 en samen hielden ze 437 producten achter paginatie.
    # Het grootste facet telt 69 producten (Philips-koffiemachines), dus 100
    # brengt ze allemaal op één pagina met ruimte voor groei.
    products = q.paginate(page=page, per_page=100)
    if products.total == 0:
        abort(404)

    # De facetten over de GEFILTERDE verzameling rekenen, niet over de hele
    # categorie (designrapport 6 augustus, punt 1): op "Wasmachines bij
    # Coolblue" met 82 resultaten hoort bij "AEG (n)" het aantal binnen die
    # 82 te staan, niet de 32 van de categorie. Zelfde soort fout als de
    # facetreparatie van juli. Opties met telling nul vallen hierdoor
    # vanzelf weg. Bewust niet gecachet: dit zijn licht bezochte pagina's
    # en de berekening loopt over hooguit een paar honderd producten --
    # dezelfde last die de categoriepagina vóór zijn cache ook al droeg.
    gefilterd = q.all()
    brand_facet = compute_brand_facet(gefilterd)
    spec_facets = compute_spec_facets(gefilterd)

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
                        f"Bekijk actuele prijzen en prijsverloop bij "
                        f"{winkel_opsomming()}.")[:160]

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
    # Exact op een kale letter matchen, niet op startswith: ovens leveren
    # "Energielabel niet van toepassing" en dat gaf een pagina voor label E
    # met één pizzaoven erop, die ook nog in de sitemap belandde.
    match = next((o for o in (energie_facet['options'] if energie_facet else [])
                 if energielabel_letter(o['value']) == letter), None)
    if not match:
        abort(404)

    naam_lower = category.name.lower()
    aantal = match['count']
    # Niet "de n zuinigste modellen": op /energielabel/g klopt dat precies
    # andersom -- dat zijn juist de minst zuinige apparaten die wij volgen.
    # Deze formulering is waar voor elke letter, en enkelvoud leest als
    # enkelvoud in plaats van "de 1 zuinigste modellen".
    if aantal == 1:
        intro = (f"Dit is het enige model met energielabel {letter} in onze "
                 f"{naam_lower}-vergelijker, met de actuele prijs per winkel.")
    else:
        intro = (f"Dit zijn de {aantal} modellen met energielabel {letter} in onze "
                 f"{naam_lower}-vergelijker, met de actuele prijs per winkel.")
    meta_description = (f"Energielabel {letter} {naam_lower} vergelijken: {aantal} "
                        f"{'model' if aantal == 1 else 'modellen'} op prijs, bij "
                        f"{winkel_opsomming()}.")[:160]

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
                        f"bij {winkel_opsomming()}.")[:160]

    return _render_facet_page(
        category, Product.specs[spec_key].as_string() == waarde, waarde,
        f"{waarde} {category.name}", meta_description, intro,
    )


# Winkelpagina's ("Wasmachines bij Coolblue"): gemeten op 1 augustus heeft
# Slimster zo'n pagina per winkel en wij niet, terwijl /api/filterkansen er
# hier 64 telde met genoeg producten. Zelfde ondergrens als de andere
# filterpagina's, zodat route, links en sitemap nooit van mening verschillen
# over welke pagina's bestaan.
_WINKEL_FACET_CACHE = {}
_WINKEL_FACET_TTL = 15 * 60


def _winkel_facet(category):
    """[{code, label, aantal}] per winkel met genoeg leverbare producten in
    deze categorie. Eén GROUP BY, gecachet zoals _category_facets; alles
    onder _MIN_PER_FILTERPAGINA valt weg, want die pagina bestaat niet."""
    nu = time.time()
    hit = _WINKEL_FACET_CACHE.get(category.id)
    if hit and nu - hit[0] < _WINKEL_FACET_TTL:
        return hit[1]

    from sqlalchemy import func
    from models import Offer, db, retailer_label
    rijen = (db.session.query(Offer.retailer, func.count(Offer.product_id))
             .join(Product, Offer.product_id == Product.id)
             .filter(Product.category_id == category.id,
                     Product.is_available.is_(True),
                     Offer.is_available.is_(True))
             .group_by(Offer.retailer).all())
    uit = [{'code': code, 'label': retailer_label(code), 'aantal': aantal}
           for code, aantal in sorted(rijen, key=lambda r: -r[1])
           if aantal >= _MIN_PER_FILTERPAGINA]
    _WINKEL_FACET_CACHE[category.id] = (nu, uit)
    return uit


@main_bp.route('/category/<slug>/winkel/<winkel>')
def category_winkel(slug, winkel):
    category = Category.query.filter_by(slug=slug).first_or_404()
    match = next((w for w in _winkel_facet(category)
                  if w['code'] == winkel.lower()), None)
    if not match:
        abort(404)
    label, aantal = match['label'], match['aantal']

    from models import Offer, db
    naam_lower = category.name.lower()
    # De belofte die een winkel-pagina waarmaakt en een winkel-site niet:
    # je ziet er meteen of een ándere winkel goedkoper is.
    intro = (f"We volgen {aantal} {naam_lower} die nu leverbaar zijn bij "
             f"{label}. Bij elk model staat de laagste actuele prijs van al "
             f"onze aangesloten winkels — zo zie je direct of {label} de "
             f"goedkoopste is, of dat een andere winkel minder vraagt.")
    meta_description = (f"{category.name} bij {label}: vergelijk {aantal} "
                        f"modellen op prijs en zie direct of {label} of een "
                        f"andere winkel de goedkoopste is.")[:160]

    return _render_facet_page(
        category,
        Product.id.in_(db.session.query(Offer.product_id).filter(
            Offer.retailer == winkel.lower(),
            Offer.is_available.is_(True))),
        f"Bij {label}", f"{category.name} bij {label}",
        meta_description, intro,
    )


# Kenmerkpagina's ("Zeer stille wasmachines"): hetzelfde recept als de
# winkelpagina's, maar dan op de EPREL-specificaties. Elke pagina mikt op een
# echte zoekopdracht ("stille wasmachine", "wasmachine 9 kg"). De indeling in
# stappen staat in _FILTERVELDEN; alles onder _MIN_PER_FILTERPAGINA bestaat
# niet, in route, links en sitemap tegelijk.
_KENMERK_FACET_CACHE = {}
_KENMERK_FACET_TTL = 15 * 60


def _kenmerk_facet(category):
    """{(veldnaam, stapslug): {'stap':..., 'opzet':..., 'ids': [...]}} voor
    één categorie, alleen stappen met genoeg apparaten. Eén query over de
    EPREL-rijen, gecachet zoals _category_facets."""
    nu = time.time()
    hit = _KENMERK_FACET_CACHE.get(category.id)
    if hit and nu - hit[0] < _KENMERK_FACET_TTL:
        return hit[1]

    from models import EprelData, db
    rijen = (db.session.query(EprelData.gegevens, Product.id)
             .join(Product, EprelData.product_id == Product.id)
             .filter(EprelData.gevonden.is_(True),
                     Product.category_id == category.id,
                     Product.is_available.is_(True)).all())
    per_stap = {}
    for gegevens, product_id in rijen:
        for veld, opzet in _FILTERVELDEN.items():
            waarde = _eprel_waarde(gegevens, veld)
            if waarde is None:
                continue
            stap = _stap_voor(waarde, opzet)
            if stap is not None:
                per_stap.setdefault(
                    (opzet['naam'], stap['slug']),
                    {'stap': stap, 'opzet': opzet, 'ids': []},
                )['ids'].append(product_id)
    uit = {sleutel: info for sleutel, info in per_stap.items()
           if len(info['ids']) >= _MIN_PER_FILTERPAGINA}
    _KENMERK_FACET_CACHE[category.id] = (nu, uit)
    return uit


def _kenmerk_kop(stap, category):
    """'Zeer stille {cat}' + 'Wasmachines' -> 'Zeer stille wasmachines'."""
    kop = stap['kop'].format(cat=category.name.lower())
    return kop[0].upper() + kop[1:]


def _kenmerk_links(category):
    """Linklijst voor de categoriepagina, in de vaste volgorde van
    _FILTERVELDEN zodat de stappen van een veld bij elkaar staan."""
    facet = _kenmerk_facet(category)
    links = []
    for opzet in _FILTERVELDEN.values():
        for stap in opzet['stappen']:
            info = facet.get((opzet['naam'], stap['slug']))
            if info:
                links.append({'veld': opzet['naam'], 'slug': stap['slug'],
                              'kop': _kenmerk_kop(stap, category),
                              'aantal': len(info['ids'])})
    return links


@main_bp.route('/category/<slug>'
               '/<any(breedte,geluid,inhoud,toerental,vulgewicht,waterverbruik):veld>'
               '/<stap_slug>')
def category_kenmerk(slug, veld, stap_slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    info = _kenmerk_facet(category).get((veld, stap_slug))
    if not info:
        abort(404)
    stap, opzet, aantal = info['stap'], info['opzet'], len(info['ids'])
    kop = _kenmerk_kop(stap, category)

    naam_lower = category.name.lower()
    # De bronvermelding is geen beleefdheid maar een licentievoorwaarde van
    # EPREL -- laten staan.
    intro = (f"We volgen {aantal} {naam_lower} met {opzet['naam']} "
             f"{stap['label']}, hieronder gesorteerd op prijs. Deze "
             f"specificaties komen uit het officiële Europese "
             f"energielabelregister (EPREL) van de Europese Commissie; bij "
             f"elk model staat de laagste actuele prijs van onze "
             f"aangesloten winkels.")
    meta_description = (f"{kop} vergelijken: {aantal} modellen op prijs, met "
                        f"specificaties uit het officiële EU-energieregister "
                        f"(EPREL).")[:160]

    return _render_facet_page(
        category, Product.id.in_(info['ids']), stap['label'],
        kop, meta_description, intro,
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


# Zelfde procescache-patroon en TTL als _category_facets: dit verandert alleen
# als de syncs draaien.
_MERKBUUR_CACHE = {}
_MERKBUUR_TTL = 15 * 60


def _merken_per_categorie():
    """{merksleutel: set(category_id)} plus het totaal per merk.

    Een GROUP BY over merk en categorie, geen productrijen: dat zijn een paar
    honderd regels in plaats van 2806 records met beschrijvingsteksten erin.
    Sleutel is merk.lower(), gelijk aan compute_global_brand_index, zodat
    "AEG" en "Aeg" hier ook een merk zijn.
    """
    from sqlalchemy import func

    from models import db

    nu = time.time()
    hit = _MERKBUUR_CACHE.get('data')
    if hit and nu - hit[0] < _MERKBUUR_TTL:
        return hit[1]

    rijen = (db.session.query(Product.brand, Product.category_id,
                              func.count(Product.id))
             .filter(Product.is_available.is_(True), Product.brand.isnot(None))
             .group_by(Product.brand, Product.category_id).all())

    categorieen, totalen = defaultdict(set), Counter()
    for merk, categorie_id, aantal in rijen:
        sleutel = (merk or '').strip().lower()
        if not sleutel or categorie_id is None:
            continue
        categorieen[sleutel].add(categorie_id)
        totalen[sleutel] += aantal

    data = (dict(categorieen), totalen)
    _MERKBUUR_CACHE['data'] = (nu, data)
    return data


def _verwante_merken(merk, index, hoeveel=6):
    """Merken die in dezelfde categorieen zitten als dit merk.

    Waarom dit bestaat: de merkpagina's zijn eindpunten. Je komt er binnen via
    een zoekopdracht op merknaam en dan houdt het op -- er staat geen enkele
    link naar een andere merkpagina, terwijl dat precies de pagina's zijn waar
    dezelfde bezoeker naar kijkt. Wie een Bosch-wasmachine overweegt, kijkt
    ook naar Siemens en AEG.

    Rangschikt op overlap in categorieen, daarna op omvang. Geen willekeur en
    geen "gerelateerd" zonder grond: staat een merk in geen van onze
    categorieen, dan staat het er niet bij.
    """
    categorieen, totalen = _merken_per_categorie()
    eigen = categorieen.get(merk.strip().lower())
    if not eigen:
        return []

    # Alleen merken met een eigen pagina: de index is de enige plek waar
    # weergavenaam en slug samen vastliggen, en een link naar een merk dat
    # daar niet in staat wordt een 404.
    per_sleutel = {m['naam'].strip().lower(): m for m in index}

    scores = []
    for sleutel, hun in categorieen.items():
        if sleutel == merk.strip().lower():
            continue
        gedeeld = len(eigen & hun)
        if not gedeeld:
            continue
        vermelding = per_sleutel.get(sleutel)
        if vermelding:
            scores.append((gedeeld, totalen[sleutel], vermelding))

    scores.sort(key=lambda s: (-s[0], -s[1], s[2]['naam'].lower()))
    return [v for _, _, v in scores[:hoeveel]]


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
                        f"{winkel_opsomming()}.")[:160]

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
                           verwante_merken=_verwante_merken(merk, index),
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
