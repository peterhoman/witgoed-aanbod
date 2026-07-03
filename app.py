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

    from models import db, Category, Product, SyncLog, AIContent
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _ensure_guides_post_type_column(db)

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
