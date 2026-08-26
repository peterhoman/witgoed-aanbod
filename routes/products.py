from datetime import timedelta

from flask import (Blueprint, abort, render_template, request, jsonify,
                   current_app)
from models import Product, Category, Guide, RETAILER_LABELS
from product_specs import FORMAAT_VELD
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)


@products_bp.route('/uit/aanbieding/<int:offer_id>')
def naar_winkel(offer_id):
    """Stuur de bezoeker door naar de winkel, via ons eigen adres.

    Waarom deze omweg
    -----------------
    De knoppen wezen rechtstreeks naar het affiliate-netwerk. Elke crawler
    die de pagina las volgde die link, en het netwerk telde dat als een klik.
    Gemeten op 01-08 in TradeTracker: 894 kliks in juli, nul verkopen, nul
    leads -- terwijl Search Console over drie maanden ongeveer twintig
    bezoekers naar de site stuurde. Die kliks waren dus vrijwel zeker geen
    mensen.

    Dat is niet onschuldig. Netwerken beoordelen klikkwaliteit, en
    honderden kliks zonder één conversie is precies het patroon waarop een
    account gemarkeerd wordt (TradeTracker heeft er een menu-item voor:
    "Ongeldige links"). Dat risico loopt de eigenaar zonder er iets aan te
    hebben.

    Nu wijst de knop hierheen, en /uit/ staat in robots.txt op slot. Een
    crawler die zich aan de regels houdt komt niet verder; het netwerk ziet
    alleen echte bezoekers.

    En het levert het cijfer op dat tot nu toe ontbrak: hoeveel mensen gaan
    er daadwerkelijk naar een winkel, en naar welke. Dat is de vraag waar
    deze site voor bestaat -- vertoningen in Google zijn leuk, doorklikken
    betaalt.

    Wat hier bewust NIET gebeurt: geen cookie, geen IP, geen sessie. Alleen
    een teller per winkel per dag, dezelfde afspraak als bij de
    paginaweergaven.
    """
    from flask import redirect
    from models import Offer

    from pageviews import is_bot, tel

    offer = Offer.query.get(offer_id)
    if offer is None or not offer.link:
        abort(404)

    # Een bot die zich niet aan robots.txt houdt telt niet mee; anders meten
    # we straks weer wat we juist wilden uitfilteren.
    if not is_bot(request.headers.get('User-Agent')):
        tel(f"uit-{offer.retailer}")

    # 302 en niet 301: dit is geen verhuizing van een pagina maar een
    # doorverwijzing per klik, en de bestemming verandert zodra de winkel
    # zijn link aanpast.
    return redirect(offer.link, code=302)


@products_bp.route('/uit/product/<int:product_id>')
def naar_winkel_product(product_id):
    """Zelfde als hierboven, voor de terugvalknop zonder aanbieding.

    Die knop staat op productpagina's waar geen enkele winkel meer levert;
    hij wijst naar de oorspronkelijke Bol-link. Zeldzaam, maar er zijn 2.800
    productpagina's en zonder deze route zou een crawler daar alsnog het
    netwerk aantikken.
    """
    from flask import redirect

    from pageviews import is_bot, tel

    product = Product.query.get(product_id)
    if product is None:
        abort(404)
    doel = product.affiliate_url or product.bol_url
    if not doel:
        abort(404)

    if not is_bot(request.headers.get('User-Agent')):
        tel('uit-terugval')
    return redirect(doel, code=302)


def _eprel_certificering(product):
    """Het EPREL-registratienummer als Certification-blok, of None.

    Google documenteert dit veld uitdrukkelijk voor EPREL en schrijft dat het
    de code gebruikt om het juiste energielabel op te zoeken en te tonen bij
    vermeldingen. Voor Europees witgoed is dat een van de weinige velden waar
    een vergelijker zich mee kan onderscheiden -- vrijwel geen concurrent
    vult het in.

    De schrijfwijze volgt letterlijk Google's eigen voorbeeld, inclusief de
    liggende streep in "European_Commission". Dat ziet er verkeerd uit maar
    staat zo in de documentatie; een spatie is iets anders dan wat zij
    verwachten.

    Geen nummer, geen blok. Zoals overal hier: een onderdeel weglaten is
    beter dan iets beweren wat de data niet draagt -- en bij een
    certificeringsnummer geldt dat dubbel, want een verkeerd nummer wijst
    naar het energielabel van een ander apparaat.
    """
    from models import EprelData

    rij = EprelData.query.filter_by(product_id=product.id,
                                    gevonden=True).first()
    if rij is None or not (rij.registratienummer or '').strip():
        return None
    return {
        '@type': 'Certification',
        'issuedBy': {'@type': 'Organization', 'name': 'European_Commission'},
        'name': 'EPREL',
        'certificationIdentification': rij.registratienummer.strip(),
    }


def _product_structured_data(product, merk_facet=None):
    """Schema.org Product + AggregateOffer voor rich results in Google.

    De EAN gaat mee als gtin13: daarmee kan Google het apparaat koppelen aan
    zijn productkennisgraaf en prijzen/winkels in de zoekresultaten tonen —
    voor een prijsvergelijker de belangrijkste SEO-bouwsteen.
    """
    from urllib.parse import quote

    site_url = current_app.config['SITE_URL']
    offers = product.available_offers

    # Zelfde codering als de canonical in app.py. Zonder quote() gaat het mis
    # bij slugs met een +, haakjes of een letter met puntjes: gemeten 25 aug
    # week bij 6 van de 40 productpagina's de url hier af van het echte adres
    # ("...cm724g1b1-+-siemens..." in plaats van "...-%2B-..."), en een kale
    # plus betekent in een webadres een spatie. Google las hier dus een
    # pagina die niet bestaat.
    data = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': product.title,
        'url': f"{site_url}/product/{quote(product.slug, safe='-._~')}",
    }
    if product.image_url:
        data['image'] = product.image_url
    if product.brand:
        data['brand'] = {'@type': 'Brand', 'name': product.brand}
    ean = (product.ean or '').strip()
    if len(ean) == 13 and ean.isdigit():
        data['gtin13'] = ean

    # Het modelnummer als mpn. Google gebruikt gtin/mpn om een apparaat aan
    # zijn productkennisgraaf te koppelen, en gemeten op 25 aug is de
    # modelcode het enige zoekwoord dat deze site klikken oplevert: 787 van
    # de 1.000 zoektermen waren een modelcode en die leverden 22 van de 23
    # klikken op. Dan hoort die code ook in de gestructureerde gegevens te
    # staan; hij ontbrak op alle 40 onderzochte pagina's.
    from product_specs import modelnummer
    model = modelnummer(product)
    if model:
        data['mpn'] = model
    description = product.ai_description or product.description
    if description:
        data['description'] = description[:500]
    if product.category:
        data['category'] = product.category.name

    certificering = _eprel_certificering(product)
    if certificering:
        data['hasCertification'] = certificering

    if offers:
        prices = [o.price for o in offers]
        data['offers'] = {
            '@type': 'AggregateOffer',
            'priceCurrency': 'EUR',
            'lowPrice': min(prices),
            'highPrice': max(prices),
            'offerCount': len(offers),
            # Beschikbaarheid hoort hier, op het overkoepelende blok, en niet
            # alleen bij de losse aanbiedingen hieronder. Gemeten op 28-07:
            # Merchant Center keurde alle 1383 automatisch gevonden producten
            # af met "Ontbrekende waarde voor [availability]", terwijl het veld
            # bij elke geneste Offer wel degelijk stond. Google leest dus het
            # bovenste blok en niet de nesting -- dat verklaart ook waarom de
            # prijs wel overkwam (die staat hier) en de beschikbaarheid niet.
            #
            # We komen hier alleen als product.available_offers gevuld is, dus
            # er is minstens een winkel die het apparaat levert. InStock is
            # daarmee geen aanname maar een weergave van wat de pagina toont.
            'availability': 'https://schema.org/InStock',
            # Hieronder stond per winkel een geneste Offer met prijs, link en
            # seller. Die zijn er op 29-07 uit gehaald, om twee redenen.
            #
            # 1. Google leest ze niet. Dat is geen aanname meer maar gemeten:
            #    tot 28-07 stond availability alleen bij de geneste Offers, en
            #    Merchant Center keurde alle 1383 producten af op precies dat
            #    ontbrekende veld. Zodra het op het overkoepelende blok stond,
            #    liep de goedkeuring op (134 -> 339 binnen een dag). Het bovenste
            #    blok is dus wat telt; de nesting werd genegeerd.
            #
            # 2. Ze zeggen iets wat niet klopt over wie wij zijn. Door per winkel
            #    een prijs met een seller-naam te publiceren presenteert deze
            #    site zich als de partij die het apparaat aanbiedt, terwijl wij
            #    prijzen vergelijken en de bezoeker doorsturen. Dat is
            #    waarschijnlijk ook waarom Google uit zichzelf 1383 producten in
            #    Merchant Center heeft aangemaakt.
            #
            # Er gaat geen informatie verloren die Google gebruikte: het aantal
            # winkels staat in offerCount, de prijsspreiding in lowPrice en
            # highPrice, en de winkels zelf staan zichtbaar op de pagina waar de
            # bezoeker ze nodig heeft.
            #
            # priceValidUntil stond er al bewust niet in en komt ook niet terug.
            # Het veld is optioneel, en Google schrijft: "your listing may not
            # display if the priceValidUntil property indicates a past date".
            # Bij prijzen die doorlopend wijzigen is elke datum die wij
            # verzinnen een tikkende bom -- hij verloopt zodra Google een paar
            # dagen niet langskomt, en dan verdwijnt de vermelding.
        }

    # Zelfde stappen als het zichtbare kruimelpad in product.html. Google toont
    # dit pad in de zoekresultaten ("witgoedaanbod.nl > Wasmachines > Bosch"),
    # dus een merkstap maakt het fragment concreter. Hij staat er alleen als de
    # merk-facetpagina echt bestaat; anders blijft het bij twee niveaus.
    stappen = [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home',
         'item': f"{site_url}/"},
        {'@type': 'ListItem', 'position': 2, 'name': product.category.name,
         'item': f"{site_url}/category/{product.category.slug}"},
    ]
    if merk_facet:
        stappen.append({'@type': 'ListItem', 'position': 3,
                        'name': merk_facet['naam'],
                        'item': f"{site_url}{merk_facet['url']}"})
    stappen.append({'@type': 'ListItem', 'position': len(stappen) + 1,
                    'name': product.title})
    breadcrumbs = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': stappen,
    }
    return [data, breadcrumbs]


def prijzen_opgehaald(product):
    """Hoe lang geleden de getoonde prijzen bij de winkels zijn opgehaald.

    Geeft 'ruim 3 uur geleden' terug, of None als er geen leverbare
    aanbieding met een tijdstempel is -- dan vervalt de mededeling, zoals
    overal op deze site: liever niets dan een slag in de lucht.

    Bewust een tijdsduur en geen kloktijd. De database bewaart naieve
    UTC-tijden; die als Nederlandse kloktijd tonen zou er in de zomer twee
    uur naast zitten, en een tijdstip dat er naast zit is erger dan geen
    tijdstip. Een duur klopt in elke tijdzone.

    Waarom dit er staat: bij een prijsvergelijker is de versheid van de
    prijs de kern van wat je belooft. Op 29-07 stond er een dag lang EUR 599
    bij een oven waar de winkel EUR 1399 voor rekende, door een fout in de
    feed van die winkel. Dat valt niet volledig te voorkomen -- de winkel is
    de bron -- maar wel eerlijk te begrenzen: zeggen wanneer je gekeken hebt,
    en zeggen dat de winkel leidend is.
    """
    from flask import g

    from models import utcnow
    from translations import translate

    tijden = [o.last_synced for o in product.available_offers if o.last_synced]
    if not tijden:
        return None
    uren = (utcnow() - max(tijden)).total_seconds() / 3600
    if uren < 0:
        # Een tijdstempel in de toekomst betekent dat er iets niet klopt met
        # de klok; dan liever niets zeggen dan iets onmogelijks.
        return None

    taal = g.get('lang', 'nl')
    if uren < 1:
        return translate('product.fetched_lasthour', taal)
    if uren < 24:
        return translate('product.fetched_hours', taal, n=int(uren))
    dagen = int(uren // 24)
    if dagen == 1:
        return translate('product.fetched_yesterday', taal)
    return translate('product.fetched_days', taal, n=dagen)


def _is_set(product):
    """True als dit een combinatie van twee apparaten is, geen los apparaat.

    De feeds zetten zo'n set als "Wisberg WBWM5A5W9ML + Wisberg WBDR5AW9ML" in
    de titel. Van de 120 wasmachines op de site zijn er 29 zo'n set. Het
    onderscheid is hard: een was/droogcombinatie van € 1.649 hoort niet
    vergeleken te worden met een losse wasmachine van € 349, hoe goed het
    energielabel ook matcht.
    """
    return ' + ' in (product.title or '')


def _vergelijkbare_alternatieven(product, aantal=4):
    """Apparaten die lijken op dit product én bij meerdere winkels liggen.

    Voor de één-winkel-pagina: bij één aanbieding valt er niets te
    vergelijken, en dan is een doodlopende pagina het slechtste antwoord.
    Deze lijst wijst door naar precies de producten waar de vergelijker wél
    werkt, gesorteerd op het aantal winkels.

    Geeft een lege lijst als er niets vergelijkbaars is; de sectie verdwijnt
    dan, in plaats van zich te vullen met willekeurige producten.
    """
    from models import db, Offer
    specs = product.specs or {}
    slug = product.category.slug if product.category else ''

    winkels = (
        db.session.query(Offer.product_id.label('pid'),
                         db.func.count(Offer.id).label('n'))
        .filter(Offer.is_available.is_(True))
        .group_by(Offer.product_id)
        .subquery()
    )
    # Twee harde grenzen, ongeacht hoe ruim we verderop zoeken.
    #
    # Prijsband 0,6 tot 1,6 keer: op een was/droogcombinatie van € 1.649
    # stonden losse machines van € 349 en een Miele van € 2.374 als
    # "wel te vergelijken". Dat is geen alternatief maar een andere aankoop,
    # en het kost meer vertrouwen dan het oplevert -- juist op de pagina die
    # het van eerlijkheid moet hebben.
    #
    # Set versus los apparaat: een combinatie van wasmachine plus droger
    # hoort alleen naast andere combinaties te staan.
    prijs = product.lowest_price or product.price or 0
    grenzen = [Product.price >= prijs * 0.6, Product.price <= prijs * 1.6] if prijs else []
    if _is_set(product):
        grenzen.append(Product.title.like('% + %'))
    else:
        grenzen.append(~Product.title.like('% + %'))

    basis = (
        db.session.query(Product, winkels.c.n)
        .join(winkels, winkels.c.pid == Product.id)
        .filter(Product.category_id == product.category_id,
                Product.id != product.id,
                Product.is_available.is_(True),
                winkels.c.n > 1,
                *grenzen)
        .order_by(winkels.c.n.desc(), Product.price.asc())
    )

    label = str(specs.get('Waarde energielabel') or '').strip()
    formaat_veld = FORMAAT_VELD.get(slug)
    formaat = str(specs.get(formaat_veld) or '').strip() if formaat_veld else ''

    # Van specifiek naar ruim: eerst zelfde formaat én label, dan alleen
    # label, dan alles uit de categorie met meerdere winkels.
    pogingen = []
    if formaat and label:
        pogingen.append([Product.specs[formaat_veld].as_string() == formaat,
                         Product.specs['Waarde energielabel'].as_string() == label])
    if label:
        pogingen.append([Product.specs['Waarde energielabel'].as_string() == label])
    pogingen.append([])

    gezien, resultaat = set(), []
    for filters in pogingen:
        for kandidaat, n in basis.filter(*filters).limit(aantal * 2).all():
            if kandidaat.id in gezien:
                continue
            gezien.add(kandidaat.id)
            resultaat.append(kandidaat)
            if len(resultaat) >= aantal:
                return resultaat
    return resultaat


def _alternatieven_kenmerk(product):
    """Korte omschrijving van waarop de alternatieven lijken: "9 kg, label A"."""
    specs = product.specs or {}
    slug = product.category.slug if product.category else ''
    delen = []
    veld = FORMAAT_VELD.get(slug)
    if veld and specs.get(veld):
        delen.append(str(specs[veld]).strip())
    if specs.get('Waarde energielabel'):
        delen.append('label ' + str(specs['Waarde energielabel']).strip())
    return ', '.join(delen)


@products_bp.route('/product/<slug>')
def product_detail(slug):
    # Ook niet-leverbare producten tonen (met "tijdelijk niet leverbaar"):
    # gidsen en YouTube-video's linken hierheen, en een 404 breekt die links
    # terwijl het apparaat vaak gewoon terugkomt in de winkel-feeds.
    product = Product.query.filter_by(slug=slug).first_or_404()

    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_available == True
    ).limit(6).all()

    # Koopgidsen en blogartikelen uit dezelfde categorie: elke productpagina
    # linkt zo naar de adviescontent (interne links voor SEO + hulp bij kiezen).
    category_guides = (Guide.query
                       .filter_by(category_id=product.category_id)
                       .order_by(Guide.post_type.desc(), Guide.created_at.desc())
                       .limit(5).all())

    from price_chart import build_price_history
    from energy_costs import bereken_energiekosten
    from eprel_specs import eprel_blok, ontdubbel_specs
    from product_specs import (kernspecs, groepeer_specs, modelnummer,
                               zoektitel)
    from category_context import bepaal_categoriecontext, meta_beschrijving
    from setprijs import setzin
    from facet_links import merk_facetpagina, verfijningslinks

    # De één-winkel-variant (design 5c) geldt voor ruim de helft van de
    # producten; alleen dáár halen we alternatieven op, zodat de gewone
    # pagina geen extra query kost.
    een_winkel = product.is_available and product.retailer_count <= 1
    # EPREL wint bij dubbele specs: het gelijknamige feedveld verdwijnt uit
    # de speclijst (designrapport 6 aug, punt 5 — twee verschillende
    # afmetingen op één pagina). Zie eprel_specs._FEEDVELD_DUBBEL.
    eprel_data = eprel_blok(product)
    kern, spec_groepen = ontdubbel_specs(eprel_data, kernspecs(product),
                                         groepeer_specs(product))
    # Eén keer opgehaald: het kruimelpad en de structured data moeten dezelfde
    # stappen tonen. Komt uit dezelfde gecachete index als de verfijningslinks.
    merk_facet = merk_facetpagina(product)
    return render_template('product.html', product=product,
                           related_products=related_products,
                           category_guides=category_guides,
                           merk_facet=merk_facet,
                           structured_data=_product_structured_data(product, merk_facet),
                           price_history=build_price_history(product),
                           prijzen_opgehaald=prijzen_opgehaald(product),
                           energiekosten=bereken_energiekosten(product),
                           kernspecs=kern,
                           spec_groepen=spec_groepen,
                           # Voor de "Alle N specificaties"-knop: het aantal
                           # dat na het ontdubbelen echt getoond wordt.
                           spec_totaal=len(kern) + sum(
                               len(rijen) for _, rijen in spec_groepen),
                           # EPREL-stap 3: geverifieerde specificaties met
                           # verplichte bronvermelding; None = geen blok.
                           eprel=eprel_data,
                           modelnummer=modelnummer(product),
                           zoektitel=zoektitel(product),
                           # Eigen meting over de hele categorie: de enige
                           # inhoud op een dunne productpagina die nergens
                           # anders staat. Gecachet per categorie, dus dit
                           # kost niet elke paginaweergave een query.
                           categoriecontext=bepaal_categoriecontext(product),
                           # Alleen gevuld bij een setje waarvan we allebei
                           # de apparaten los in de catalogus terugvinden;
                           # bij al het andere None en dan valt het blok weg.
                           setvergelijking=setzin(product),
                           # Uit dezelfde gecachete meting: een
                           # meta-description die per pagina uniek is
                           # en niet uit de feed komt.
                           meta_beschrijving=meta_beschrijving(product),
                           # Links naar facetpagina's die al bestaan en al in
                           # de sitemap staan. Ook gecachet per categorie.
                           verfijningslinks=verfijningslinks(product),
                           een_winkel=een_winkel,
                           # Niet hardgecodeerd in de tekst: sluit er een
                           # zevende winkel aan, dan klopt "de andere vijf"
                           # niet meer.
                           aantal_winkels=len(RETAILER_LABELS),
                           alternatieven=_vergelijkbare_alternatieven(product) if een_winkel else [],
                           alternatieven_kenmerk=_alternatieven_kenmerk(product) if een_winkel else '')


@products_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 10000, type=float)
    brand_filter = request.args.getlist('brand')
    page = request.args.get('page', 1, type=int)

    q = Product.query.filter(Product.is_available == True)

    if query:
        q = q.filter(
            or_(
                Product.title.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%'),
                Product.brand.ilike(f'%{query}%'),
                Product.ean.ilike(f'%{query}%')
            )
        )

    if category_filter:
        q = q.filter(Product.category_id == category_filter)

    q = q.filter(Product.price.between(min_price, max_price))

    if brand_filter:
        q = q.filter(or_(*[Product.brand.ilike(b) for b in brand_filter]))

    results = q.paginate(page=page, per_page=24)
    categories = Category.query.filter_by(parent_id=None).all()

    available_brands = sorted(set(p.brand for p in Product.query.filter(Product.is_available == True).all() if p.brand))

    from routes.main import _pros_cons_by_ean
    return render_template('search.html', results=results.items, pagination=results,
                         query=query, categories=categories, selected_category=category_filter,
                         available_brands=available_brands, selected_brands=brand_filter,
                         min_price=min_price, max_price=max_price,
                         pros_cons_by_ean=_pros_cons_by_ean())


@products_bp.route('/vergelijk')
def compare():
    ids_param = request.args.get('ids', '')
    ids = []
    for raw_id in ids_param.split(','):
        raw_id = raw_id.strip()
        if raw_id.isdigit():
            product_id = int(raw_id)
            if product_id not in ids:
                ids.append(product_id)
    ids = ids[:3]

    products = []
    if ids:
        found = Product.query.filter(Product.id.in_(ids)).all()
        by_id = {p.id: p for p in found}
        products = [by_id[i] for i in ids if i in by_id]

    spec_keys = []
    for product in products:
        for key in (product.specs or {}).keys():
            if key not in spec_keys:
                spec_keys.append(key)

    return render_template('compare.html', products=products, spec_keys=spec_keys)


@products_bp.route('/verlanglijst')
def wishlist():
    # Zelfde opzet als /vergelijk: de lijst zelf staat alleen lokaal bij de
    # bezoeker (localStorage, geen account); deze pagina zoekt op basis van
    # de ID's in de URL de actuele productgegevens op, zodat prijs en foto
    # altijd live zijn i.p.v. de (mogelijk verouderde) waarde uit de browser.
    ids_param = request.args.get('ids', '')
    ids = []
    for raw_id in ids_param.split(','):
        raw_id = raw_id.strip()
        if raw_id.isdigit():
            product_id = int(raw_id)
            if product_id not in ids:
                ids.append(product_id)

    products = []
    if ids:
        found = Product.query.filter(Product.id.in_(ids)).all()
        by_id = {p.id: p for p in found}
        products = [by_id[i] for i in ids if i in by_id]

    return render_template('wishlist.html', products=products)


@products_bp.route('/api/categories')
def api_categories():
    categories = Category.query.filter_by(parent_id=None).all()
    return jsonify([{'id': c.id, 'name': c.name, 'slug': c.slug} for c in categories])
