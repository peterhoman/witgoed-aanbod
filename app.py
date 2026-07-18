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
        _ensure_categories(db)
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

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(legal_bp)
    app.register_blueprint(seo_bp)

    @app.before_request
    def redirect_to_www():
        if request.host == 'witgoedaanbod.nl':
            return redirect(f'https://www.{request.host}{request.path}', code=301)

    @app.before_request
    def set_language():
        lang = request.cookies.get('lang', 'nl')
        g.lang = lang if lang in ('nl', 'en') else 'nl'

    @app.context_processor
    def inject_translations():
        def t(key, **kwargs):
            return translate(key, g.get('lang', 'nl'), **kwargs)
        return {'t': t, 'current_lang': g.get('lang', 'nl')}

    @app.template_filter('euro')
    def euro_filter(value):
        """Nederlandse prijsnotatie: 1299.5 -> '1.299,50' (komma, puntjes voor duizendtallen)."""
        try:
            formatted = f"{float(value):,.2f}"
        except (TypeError, ValueError):
            return value
        return formatted.replace(",", " ").replace(".", ",").replace(" ", ".")

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
