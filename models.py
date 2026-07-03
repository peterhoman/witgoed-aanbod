from datetime import datetime
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    ai_intro = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    ean = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255))
    brand = db.Column(db.String(100))

    description = db.Column(db.Text)
    ai_description = db.Column(db.Text)
    ai_meta_description = db.Column(db.String(160))

    price = db.Column(db.Float, nullable=False)
    # bol's adviesprijs ("van-prijs"); alleen gevuld als die hoger is dan
    # de actuele prijs, zodat er een echte korting te tonen valt
    strikethrough_price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(500))
    bol_url = db.Column(db.String(500), nullable=False)
    affiliate_url = db.Column(db.String(500))
    retailer = db.Column(db.String(50), default='bol')

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    subcategory = db.Column(db.String(100))
    format = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    label = db.Column(db.String(100))
    year = db.Column(db.Integer)

    specs = db.Column(db.JSON)

    is_available = db.Column(db.Boolean, default=True)
    is_example = db.Column(db.Boolean, default=False)
    slug = db.Column(db.String(255), nullable=False)

    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def generate_affiliate_url(self, site_id='1528790'):
        """Generate Bol.com affiliate tracking URL.

        Format bevestigd via affiliate.bol.com/nl/handleiding/tracking-url/
        en identiek aan het bewezen bol-affiliate-page/affiliate_link.py:
        de product-URL moet volledig percent-encoded als url-parameter mee,
        en f= (promotietype) is verplicht.
        """
        return (
            "https://partner.bol.com/click/click"
            f"?t=url&s={site_id}&url={quote(self.bol_url or '', safe='')}"
            f"&f=api&subid={quote(f'product-{self.ean}')}"
        )

    def generate_short_affiliate_url(self, bitly_client, site_id='1528790'):
        """Generate and shorten affiliate tracking URL using Bit.ly"""
        long_url = self.generate_affiliate_url(site_id)
        if bitly_client:
            short_url = bitly_client.shorten_url(long_url, title=self.title[:50])
            return short_url or long_url
        return long_url

    def get_button_text(self):
        """Get dynamic button text based on retailer"""
        if self.retailer == 'bol':
            return 'Bekijk op bol'
        elif self.retailer == 'coolblue':
            return 'Bekijk bij Coolblue'
        elif self.retailer == 'mediamarkt':
            return 'Bekijk bij MediaMarkt'
        else:
            return f'Bekijk bij {self.retailer.capitalize()}'

    def __repr__(self):
        return f'<Product {self.title}>'


class SyncLog(db.Model):
    __tablename__ = 'sync_logs'

    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)
    products_synced = db.Column(db.Integer, default=0)
    products_updated = db.Column(db.Integer, default=0)
    products_hidden = db.Column(db.Integer, default=0)
    errors = db.Column(db.Text)

    def __repr__(self):
        return f'<SyncLog {self.started_at}>'


class AIContent(db.Model):
    __tablename__ = 'ai_content'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    content_type = db.Column(db.String(50), nullable=False)  # description, meta, guide, etc
    content = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer)
    cost = db.Column(db.Float)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AIContent {self.content_type}>'


class Guide(db.Model):
    __tablename__ = 'guides'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    excerpt = db.Column(db.String(300))
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    post_type = db.Column(db.String(20), default='guide')  # 'guide' (koopgids) or 'blog' (nieuwsbericht)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref='guides')

    def __repr__(self):
        return f'<Guide {self.title}>'
