from flask import Flask, render_template, request, redirect, g
from config import config
from translations import translate
from sqlalchemy import inspect, text
import os


def _ensure_guides_post_type_column(db):
    """
    db.create_all() only creates missing tables, it never alters existing
    ones. The 'guides' table predates the post_type column, so on a
    database that already has it, add the column here at startup instead
    of relying on a manual migration step run after deploy (which raced
    with Railway's health check and failed the deploy).
    """
    inspector = inspect(db.engine)
    if 'guides' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('guides')]
    if 'post_type' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE guides ADD COLUMN post_type VARCHAR(20) DEFAULT 'guide'"))
            conn.commit()


def _ensure_products_strikethrough_column(db):
    """Zelfde boot-migratiepatroon: voeg de van-prijs-kolom toe aan een
    bestaande products-tabel (db.create_all() wijzigt geen bestaande tabellen)."""
    inspector = inspect(db.engine)
    if 'products' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('products')]
    if 'strikethrough_price' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE products ADD COLUMN strikethrough_price FLOAT"))
            conn.commit()


def _ensure_guides_updated_at_column(db):
    """Zelfde boot-migratiepatroon: voeg updated_at toe aan een bestaande
    guides-tabel, zodat 'bijgewerkt op'-datums (E-E-A-T) ook op gidsen
    werken die al vóór deze kolom bestonden."""
    inspector = inspect(db.engine)
    if 'guides' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('guides')]
    if 'updated_at' not in columns:
        with db.engine.connect() as conn:
            # Bestaande rijen: updated_at = created_at, geen valse "zojuist bijgewerkt".
            conn.execute(text("ALTER TABLE guides ADD COLUMN updated_at TIMESTAMP"))
            conn.execute(text("UPDATE guides SET updated_at = created_at WHERE updated_at IS NULL"))
            conn.commit()


def _ensure_offers_delivery_columns(db):
    """Boot-migratie: verzendinfo-kolommen op de bestaande offers-tabel
    (db.create_all() wijzigt geen bestaande tabellen)."""
    inspector = inspect(db.engine)
    if 'offers' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('offers')]
    with db.engine.connect() as conn:
        if 'delivery_time' not in columns:
            conn.execute(text("ALTER TABLE offers ADD COLUMN delivery_time VARCHAR(120)"))
        if 'delivery_cost' not in columns:
            conn.execute(text("ALTER TABLE offers ADD COLUMN delivery_cost FLOAT"))
        conn.commit()


def _ensure_eprel_gezocht_column(db):
    """Boot-migratie: onderscheid tussen 'niet gezocht' en 'niets gevonden'.

    De eprel_data-tabel is gisteren aangemaakt zonder deze kolom, en
    db.create_all() wijzigt geen bestaande tabellen. Zonder deze stap zou de
    kolom alleen op een verse database bestaan.

    Bestaande rijen krijgen True: die zijn geschreven toen elke misser als
    'gezocht' gold. Dat is voor de al opgehaalde apparaten niet helemaal
    waar, maar het is de veilige kant -- ze worden bij de maandelijkse
    verversing vanzelf rechtgezet, en tot die tijd is de trefkans hooguit te
    laag en niet te hoog.
    """
    inspector = inspect(db.engine)
    if 'eprel_data' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('eprel_data')]
    if 'gezocht' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text(
                'ALTER TABLE eprel_data ADD COLUMN gezocht BOOLEAN '
                'DEFAULT TRUE NOT NULL'))
            conn.commit()


def _ensure_ai_content_bron_column(db):
    """Boot-migratie: onthoud waarop een gegenereerde tekst gebaseerd was.

    Een producttekst wordt eenmalig geschreven en blijft staan. Dat is goed
    zolang de gegevens niet veranderen -- maar 65% van de catalogus heeft nu
    geen enkele specificatie, en feeds worden rijker (toen Coolblue om extra
    kolommen werd gevraagd, kwam er meer binnen). Zonder deze kolom houdt zo'n
    product voor altijd de korte tekst van 65 woorden, ook als er later veertig
    specificaties bij komen.

    Met het aantal bronspecificaties erbij kan ai_content.moet_herschrijven
    zien wanneer een tekst verouderd is ten opzichte van de data.
    """
    inspector = inspect(db.engine)
    if 'ai_content' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('ai_content')]
    if 'bron_specs' not in columns:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE ai_content ADD COLUMN bron_specs INTEGER"))
            conn.commit()


def _backfill_offers_from_products(db):
    """Fase 1 (multi-winkel): tot nu toe stond prijs/link/voorraad rechtstreeks
    op elke products-rij (alleen Bol). Zet die één-op-één om naar een rij in de
    nieuwe offers-tabel (winkel = product.retailer, standaard 'bol'), zodat de
    site straks meerdere winkels per apparaat aankan.

    Veilig en herhaalbaar: dit VERWIJDERT of WIJZIGT geen enkel bestaand
    product; het maakt alleen een ontbrekende aanbieding aan. Draait die winkel
    voor dit product al in de offers-tabel, dan slaat het over.
    """
    from models import Product, Offer, utcnow
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'offers' not in tables or 'products' not in tables:
        return

    # Alleen backfillen zolang er producten zijn zonder enige aanbieding; scheelt
    # werk bij elke herstart zodra alles is omgezet.
    existing_product_ids = {row[0] for row in db.session.query(Offer.product_id).distinct()}
    created = 0
    for product in Product.query.all():
        if product.id in existing_product_ids:
            continue
        db.session.add(Offer(
            product_id=product.id,
            retailer=product.retailer or 'bol',
            price=product.price,
            strikethrough_price=product.strikethrough_price,
            url=product.bol_url,
            affiliate_url=product.affiliate_url,
            is_available=product.is_available,
            last_synced=product.last_synced or utcnow(),
        ))
        created += 1
    if created:
        db.session.commit()


def _ensure_categories(db):
    """Voeg ontbrekende categorieën toe.

    init_db.py draait alleen met de hand; op Railway is er niemand die dat doet.
    Nieuwe categorieën horen daarom hier, in hetzelfde boot-migratiepatroon als
    de kolommen hierboven. Bestaande categorieën worden niet aangeraakt: de
    Bol-sync werkt hun naam bij (bijv. 'Ovens & Airfryers').
    """
    from models import Category
    inspector = inspect(db.engine)
    if 'categories' not in inspector.get_table_names():
        return

    nieuw = [
        ('koffiemachines', 'Koffiemachines',
         'Vergelijk volautomaten, espressomachines en koffiezetapparaten'),
        ('fornuizen', 'Fornuizen', 'Vergelijk gasfornuizen en inductiefornuizen'),
        ('kookplaten', 'Kookplaten', 'Vergelijk inductie-, keramische en gaskookplaten'),
        ('afzuigkappen', 'Afzuigkappen', 'Vergelijk afzuigkappen voor elke keuken'),
    ]
    toegevoegd = 0
    for slug, naam, omschrijving in nieuw:
        if not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(slug=slug, name=naam, description=omschrijving))
            toegevoegd += 1
    if toegevoegd:
        db.session.commit()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Achter Railway's proxy ziet Flask intern http-verkeer, waardoor
    # request.url (en dus de canonical-tags op elke pagina) http:// werd.
    # ProxyFix laat Flask de X-Forwarded-Proto/-Host headers respecteren.
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    from models import db, Category, Product, SyncLog, AIContent, Guide
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _ensure_guides_post_type_column(db)
        _ensure_guides_updated_at_column(db)
        _ensure_products_strikethrough_column(db)
        _ensure_offers_delivery_columns(db)
        _ensure_ai_content_bron_column(db)
        _ensure_eprel_gezocht_column(db)
        _ensure_categories(db)
        # De categorie Apparaatsets moet bestaan voordat er producten in gezet
        # kunnen worden; het opruimen zelf gebeurt in de uurlijkse job.
        from catalogus_uitzonderingen import zorg_voor_setjescategorie
        zorg_voor_setjescategorie(db)
        _backfill_offers_from_products(db)
        # Gidsen en blogposts publiceren zichzelf bij de eerstvolgende deploy;
        # wijkt de tekst in de code af van de database, dan wint de code
        # (zie guides_content.py, dekt ook het materiaal uit seed_guides.py).
        from guides_content import ensure_new_guides
        ensure_new_guides(db, Category, Guide)
        # Handmatige foto-overrides (producten zonder feed-/Icecat-foto)
        # meteen toepassen i.p.v. te wachten op de eerstvolgende sync.
        from icecat import apply_manual_image_overrides
        apply_manual_image_overrides(db, Product)

    # Register blueprints
    from routes.main import main_bp
    from routes.products import products_bp
    from routes.legal import legal_bp
    from routes.seo import seo_bp
    from routes.alerts import alerts_bp
    from routes.chat import chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(seo_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(chat_bp)

    # Telt paginaweergaven per soort per dag. Geen cookies, geen IP, geen
    # sessie -- alleen aantallen, zodat zichtbaar is of bezoekers dieper de
    # site in komen zonder dat er toestemming voor nodig is.
    from pageviews import registreer as registreer_paginateller
    registreer_paginateller(app)

    @app.context_processor
    def inject_chat_enabled():
        # Babbelbot-widget alleen tonen als er echt geadviseerd kan worden
        # (OPENROUTER_API_KEY gezet, of lokale dev) — zelfde patroon als
        # alerts_enabled hieronder.
        from chatbot import chat_enabled
        return {'chat_enabled': chat_enabled()}

    @app.context_processor
    def inject_winkels():
        # Eén bron voor het winkelaantal en de namenopsomming in álle
        # sjablonen (designrapport 6 aug, punt 7): sluit er een winkel aan
        # of af, dan kloppen alle teksten meteen weer.
        from models import RETAILER_LABELS, winkel_opsomming
        return {'aantal_winkels': len(RETAILER_LABELS),
                'winkel_opsomming': winkel_opsomming()}

    @app.context_processor
    def inject_alerts_enabled():
        # Bepaalt of productpagina's het prijsalert-formulier tonen; op
        # productie blijft de feature onzichtbaar zolang Brevo niet
        # gekoppeld is (BREVO_API_KEY ontbreekt) — zie mailer.alerts_enabled.
        from mailer import alerts_enabled
        return {'alerts_enabled': alerts_enabled()}

    @app.before_request
    def redirect_to_www():
        """Alles zonder www doorsturen naar www, mét de vraagtekens erachter.

        Hier stond alleen request.path, en dat is het adres ZONDER alles wat
        na het vraagteken komt. Elke bezoeker die zonder www binnenkwam
        raakte dus stilzwijgend kwijt:

          - de zoekterm      /search?q=wasmachine
          - alle filters     /category/wasmachines?merk=bosch&label=A
          - de pagina        ?page=2
          - advertentie- en herkomstlabels (utm_source, gclid)

        Dat laatste is het duurst: zonder gclid kan Google Ads een aankoop
        niet aan een klik koppelen, en dan lijkt een campagne niets op te
        leveren terwijl hij dat wel doet.

        Gemeten op 31-07: /api/prijssprongen?dagen=1 gaf exact hetzelfde
        antwoord als ?dagen=30, omdat de instelling nooit aankwam. Dat was
        het spoor -- de meetpagina zelf deugde.

        query_string is bytes en kan alles bevatten wat een bezoeker
        meestuurt; latin-1 laat elke byte ongewijzigd door, zodat er niets
        stukgaat op een teken dat geen UTF-8 is.
        """
        if request.host == 'witgoedaanbod.nl':
            doel = f'https://www.{request.host}{request.path}'
            if request.query_string:
                doel += '?' + request.query_string.decode('latin-1')
            return redirect(doel, code=301)

    @app.before_request
    def set_language():
        lang = request.cookies.get('lang', 'nl')
        g.lang = lang if lang in ('nl', 'en') else 'nl'

    @app.context_processor
    def inject_translations():
        def t(key, **kwargs):
            return translate(key, g.get('lang', 'nl'), **kwargs)
        return {'t': t, 'current_lang': g.get('lang', 'nl')}

    @app.template_filter('slugify')
    def slugify_filter(value):
        """Merk-/spec-facet-links in templates (/category/<slug>/merk/<slug>)."""
        from filter_helpers import slugify
        return slugify(value)

    @app.template_filter('kort')
    def kort_filter(value, lengte=50):
        """Kap een titel af op een woordgrens, zonder streepje te laten hangen.

        Het kruimelpad deed dit met title[:50] en sneed dan midden in een
        woord. Jinja's truncate lost dat half op: feedtitels zitten vol
        streepjes ("... - Ecobubble - AI Wash - 11 kg"), en dan blijft er
        "- Ecobubble -…" staan. Die scheidingstekens gaan er hier af.
        """
        tekst = str(value or '').strip()
        if len(tekst) <= lengte:
            return tekst
        afgekapt = tekst[:lengte].rsplit(' ', 1)[0]
        return afgekapt.rstrip(' -–—,;:/|') + '…'

    @app.template_filter('energieletter')
    def energieletter_filter(value):
        """De kale energielabelletter (A t/m G), of leeg als het er geen is.

        Zodat het sjabloon dezelfde regel gebruikt als de sitemap, de
        facetroute en de FAQ. Deed het sjabloon het zelf met value[:1], dan
        werd "Energielabel niet van toepassing" een link naar
        /category/ovens/energielabel/e — een pagina die er niet meer is.
        """
        from filter_helpers import energielabel_letter
        return energielabel_letter(value) or ''

    @app.template_filter('foto')
    def foto_filter(url, breedte=400):
        """Winkelfoto's via de gratis verkleinservice wsrv.nl (Cloudflare-CDN).

        De feeds leveren originelen tot ~5 MB (MediaMarkt) voor kaartjes
        van ~300px; wsrv.nl verkleint naar WebP van enkele tientallen KB's
        en cachet wereldwijd. Mislukt het ophalen bij wsrv, dan stuurt de
        &default= door naar de originele foto (geen kapotte afbeelding).
        Niet-http-waarden (None, static paden) gaan ongemoeid terug.
        """
        from urllib.parse import quote
        if not url or not str(url).startswith(('http://', 'https://')):
            return url
        origineel = quote(str(url), safe='')
        return (f"https://wsrv.nl/?url={origineel}&w={breedte}"
                f"&output=webp&q=80&default={origineel}")

    @app.template_filter('euro')
    def euro_filter(value):
        """Nederlandse prijsnotatie: 1299.5 -> '1.299,50' (komma, puntjes voor duizendtallen)."""
        try:
            formatted = f"{float(value):,.2f}"
        except (TypeError, ValueError):
            return value
        return formatted.replace(",", " ").replace(".", ",").replace(" ", ".")

    @app.context_processor
    def _canonical_url():
        """Canonical met dezelfde percent-codering als de sitemap.

        De sitemap codeert product-URL's netjes (%2B, %27, %28); de canonical
        gebruikte request.base_url, en dat is het pad zoals Werkzeug het al
        gedecodeerd heeft. Daardoor stond er in de sitemap
        ".../dyson-clean-%2B-wash-..." en in de canonical
        ".../dyson-clean-+-wash-...". Dat raakt 453 van de 2813
        productpagina's (16%), waarvan 106 met een plus -- en juist een plus
        in een pad wordt door veel systemen als spatie gelezen.

        Host uit SITE_URL en niet uit het verzoek, zodat een bezoek zonder
        www nooit een andere canonical oplevert dan de sitemap.
        """
        from flask import request
        from urllib.parse import quote
        basis = app.config['SITE_URL'].rstrip('/')
        return {'canonical_url': basis + quote(request.path, safe='/-._~')}

    @app.template_filter('euro_kort')
    def euro_kort_filter(value):
        """Als euro, maar zonder centen: 10000 -> '10.000'. Voor de hint op een
        dichtgeklapte filterkop, waar '10.000,00' onnodig lang leest."""
        try:
            return f"{int(float(value)):,}".replace(",", ".")
        except (TypeError, ValueError):
            return value

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
