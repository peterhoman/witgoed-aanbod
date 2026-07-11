from datetime import datetime, timezone
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    """Huidige UTC-tijd zonder tijdzone-informatie.

    Vervangt datetime.utcnow(), dat sinds Python 3.12 een DeprecationWarning
    geeft. Het resultaat is bewust 'naief' (zonder tijdzone): alle bestaande
    kolommen zijn DateTime zonder tijdzone en alle opgeslagen waarden zijn
    UTC. Een tijdzone-bewuste waarde zou Postgres laten omrekenen naar de
    serverzone en de tijden in de database stilletjes verschuiven.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Weergavenaam per winkel (retailer-code -> label op de site). Nieuwe winkels
# (bijv. 'coolblue') hier toevoegen zodra ze meedoen.
RETAILER_LABELS = {
    'bol': 'Bol.com',
    'mediamarkt': 'MediaMarkt',
    'coolblue': 'Coolblue',
}


def retailer_label(code):
    """Nette weergavenaam voor een winkel-code; valt terug op de code zelf."""
    return RETAILER_LABELS.get((code or '').lower(), code)

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

    last_synced = db.Column(db.DateTime, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    # Aanbiedingen per winkel voor dit apparaat (Bol, MediaMarkt, ...). Verwijder
    # je een product, dan gaan zijn aanbiedingen mee (cascade). Zie Offer.
    offers = db.relationship('Offer', backref='product', lazy='select',
                             cascade='all, delete-orphan')

    @property
    def available_offers(self):
        """Leverbare aanbiedingen, goedkoopste eerst; bij gelijke prijs op
        winkelnaam zodat geen enkele winkel structureel wordt voorgetrokken."""
        return sorted((o for o in self.offers if o.is_available),
                      key=lambda o: (o.price, o.retailer or ''))

    @property
    def best_offer(self):
        """De goedkoopste leverbare aanbieding, of None."""
        offers = self.available_offers
        return offers[0] if offers else None

    @property
    def lowest_price(self):
        """Laagste leverbare prijs; valt terug op de oude products.price zodat
        pagina's blijven werken zolang er nog geen aanbiedingen zijn ingevuld."""
        best = self.best_offer
        return best.price if best else self.price

    @property
    def retailer_count(self):
        """Aantal winkels met een leverbare aanbieding voor dit apparaat."""
        return len(self.available_offers)

    def refresh_pricing(self):
        """Zet price/strikethrough_price/is_available gelijk aan de beste
        aanbieding. De categorie- en zoekpagina's filteren en sorteren op de
        SQL-kolom products.price, niet op de aanbiedingen; zonder deze stap
        zou een goedkopere MediaMarkt-prijs wel op de productpagina staan maar
        niet meetellen in het prijsfilter."""
        best = self.best_offer
        if best:
            self.price = best.price
            self.strikethrough_price = best.strikethrough_price
            self.is_available = True
        else:
            self.is_available = False

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

    def __repr__(self):
        return f'<Product {self.title}>'


class Offer(db.Model):
    """Eén aanbieding van één winkel voor één apparaat (Product).

    Fase 1 van de multi-winkel-uitbreiding: prijs, links en voorraad hoorden
    voorheen rechtstreeks op de products-rij (alleen Bol). Die informatie
    verhuist naar deze tabel, zodat hetzelfde apparaat meerdere aanbieders kan
    hebben (Bol, MediaMarkt, later Coolblue) op één productpagina.
    """
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    retailer = db.Column(db.String(50), nullable=False, default='bol')

    price = db.Column(db.Float, nullable=False)
    # winkel-adviesprijs ("van-prijs"); alleen gevuld bij een echte korting
    strikethrough_price = db.Column(db.Float, nullable=True)

    url = db.Column(db.String(500))            # productpagina bij de winkel
    affiliate_url = db.Column(db.String(500))  # tracking-/deeplink naar de winkel

    is_available = db.Column(db.Boolean, default=True)
    last_synced = db.Column(db.DateTime, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    # Per winkel hooguit één aanbieding per apparaat.
    __table_args__ = (
        db.UniqueConstraint('product_id', 'retailer', name='uq_offer_product_retailer'),
    )

    @property
    def retailer_name(self):
        """Nette weergavenaam, bijv. 'bol' -> 'Bol.com'."""
        return retailer_label(self.retailer)

    @property
    def link(self):
        """De klik-URL: bij voorkeur de affiliate-/trackinglink, anders de
        gewone winkel-URL."""
        return self.affiliate_url or self.url

    def __repr__(self):
        return f'<Offer {self.retailer} €{self.price}>'


class PriceHistory(db.Model):
    """Prijsverloop per apparaat per winkel.

    Er komt alleen een rij bij wanneer de prijs daadwerkelijk verandert
    (of bij de allereerste waarneming), niet bij elke sync. Zo blijft de
    tabel compact en is het verloop als traptreden-grafiek te tekenen:
    elke rij geldt vanaf recorded_at tot de volgende rij.

    Dit is de basis voor 'laagste prijs ooit', prijsgrafieken en later
    prijsalerts — de eigen data die deze site onderscheidt van de winkels.
    """
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('products.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    retailer = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    __table_args__ = (
        db.Index('ix_price_history_product_retailer', 'product_id', 'retailer'),
    )

    def __repr__(self):
        return f'<PriceHistory {self.retailer} €{self.price} @ {self.recorded_at:%Y-%m-%d}>'


def log_price(product_id, retailer, price):
    """Schrijf een prijspunt weg als de prijs afwijkt van de laatst bekende.

    Aanroepen vanuit de winkel-syncs nadat de aanbieding is bijgewerkt; de
    aanroeper commit zelf (dit voegt alleen toe aan de sessie).
    """
    if price is None:
        return
    last = (PriceHistory.query
            .filter_by(product_id=product_id, retailer=retailer)
            .order_by(PriceHistory.recorded_at.desc())
            .first())
    if last is None or last.price != price:
        db.session.add(PriceHistory(product_id=product_id,
                                    retailer=retailer, price=price))


class SyncLog(db.Model):
    __tablename__ = 'sync_logs'

    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(db.DateTime, default=utcnow)
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
    generated_at = db.Column(db.DateTime, default=utcnow)

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
    created_at = db.Column(db.DateTime, default=utcnow)

    category = db.relationship('Category', backref='guides')

    def __repr__(self):
        return f'<Guide {self.title}>'
