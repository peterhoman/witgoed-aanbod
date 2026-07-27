import time
from collections import Counter, defaultdict

from flask import Blueprint, render_template, request, redirect, current_app, abort
from models import Category, Product, Guide
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
        'antwoord': ("We verversen de prijzen van Bol, Coolblue, MediaMarkt, Expert, "
                     "Alternate en EP meerdere keren per dag, volledig automatisch via "
                     "hun officiële productfeeds. De goedkoopste leverbare aanbieding "
                     "staat altijd bovenaan; winkels kunnen hun positie niet kopen."),
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
        for r in ('bol', 'mediamarkt', 'coolblue', 'expert', 'alternate', 'ep')
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
                                  maxnieuw=_MAX_NIEUW_PER_AANROEP)


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
  <p>Model: <code>{{ model }}</code> &middot; opgeslagen als <code>{{ versie }}</code>.
     Deze teksten staan <b>nergens op de site</b>; ze zitten alleen in de tabel
     <code>ai_content</code>.</p>
  <p>Nu nieuw geschreven: {{ nieuw_aantal }} stuks, kosten
     &euro;&nbsp;{{ '%.4f'|format(nieuw_euro) }}. De rest kwam uit de opslag en
     kostte niets &mdash; herladen van deze pagina kost dus ook niets.</p>
  {% if toon_raming|default(true) %}
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
  <p><b>Noodrem:</b> &euro;&nbsp;{{ '%.2f'|format(besteed) }} van de
     &euro;&nbsp;{{ '%.2f'|format(daglimiet) }} die er per etmaal uitgegeven
     mag worden, en hoogstens {{ maxnieuw }} nieuwe teksten per verzoek.
     Daarboven stopt het uit zichzelf.</p>
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

    opgeslagen, mislukt, gevlagd, euro = 0, [], 0, 0.0
    try:
        for uitkomst in batch_resultaten(batch_id, sleutel):
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
                    'opgeslagen': opgeslagen, 'gevlagd_door_controle': gevlagd,
                    'mislukt': mislukt[:25], 'aantal_mislukt': len(mislukt),
                    'kosten_euro': round(euro, 4),
                    'nog_zonder_tekst': len(_zonder_tekst(3000)),
                    'nalezen': '/api/teksten/nalezen'})


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
        maxnieuw=_MAX_NIEUW_PER_AANROEP, toon_raming=False)


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
                        f"{'model' if aantal == 1 else 'modellen'} op prijs, bij Bol, "
                        f"Coolblue, MediaMarkt, Expert, Alternate en EP.")[:160]

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
