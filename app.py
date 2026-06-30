from flask import Flask, render_template, request, redirect
from config import config
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from models import db, Category, Product, SyncLog, AIContent
    db.init_app(app)

    with app.app_context():
        db.create_all()

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
