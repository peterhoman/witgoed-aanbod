import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

    # PostgreSQL for production, SQLite for development
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///witgoed.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bol.com API
    BOL_CLIENT_ID = os.getenv('BOL_CLIENT_ID')
    BOL_CLIENT_SECRET = os.getenv('BOL_CLIENT_SECRET')
    BOL_PARTNER_ID = os.getenv('BOL_PARTNER_ID')

    # MediaMarkt productfeed via Tradedoubler (source ID 3490179, programma 262336)
    TRADEDOUBLER_TOKEN = os.getenv('TRADEDOUBLER_TOKEN')

    # Coolblue productfeed via Awin (publisher 2969655, advertiser 85161)
    AWIN_FEED_APIKEY = os.getenv('AWIN_FEED_APIKEY')

    # Claude API
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Bit.ly API for URL shortening
    BITLY_TOKEN = os.getenv('BITLY_TOKEN')

    # Site config
    SITE_NAME = os.getenv('SITE_NAME', 'WitgoedAanbod.nl')
    # Met www: de site redirect non-www naar www, dus sitemap-/og-URLs
    # zonder www kosten zoekmachines een extra redirect per pagina.
    # Sanitizer: knip alles vóór "http" weg — de Railway-variabele bevatte
    # na een copy-paste een keer ",=https://..." waardoor og:url en sitemap
    # kapotte URLs kregen.
    _site_url = os.getenv('SITE_URL', 'https://www.witgoedaanbod.nl').strip()
    _http_idx = _site_url.find('http')
    SITE_URL = _site_url[_http_idx:].rstrip('/') if _http_idx >= 0 else 'https://www.witgoedaanbod.nl'

    # Google Search Console: de content-waarde van de meta-verificatietag
    # (uit "HTML-tag"-verificatie). Leeg = geen tag. De property is een
    # domein-property, geverifieerd via DNS onder pfmhoman@gmail.com; de
    # eerdere HTML-tag (avantiusshop, 2026-07-11) is bewust verwijderd
    # zodat dat account zijn eigenaarschap verliest.
    GOOGLE_SITE_VERIFICATION = os.getenv('GOOGLE_SITE_VERIFICATION', '')

    # TradeTracker site-verificatie (affiliatesite #512985): bewijst het
    # eigendom van de site richting adverteerders. Geen geheim — staat
    # bewust publiek in de <head>. TradeTracker hercontroleert periodiek,
    # dus de tag moet blijven staan.
    TRADETRACKER_SITE_VERIFICATION = os.getenv(
        'TRADETRACKER_SITE_VERIFICATION',
        '9aa380426ef441ac55aad81838ffa685fa5dcb2c')

    # Prijsalert-e-mail via Brevo (transactionele API). Zonder API-key is de
    # hele feature onzichtbaar op de site (formulier verschijnt niet) —
    # zo kan de code live staan terwijl de domeinverificatie nog loopt.
    # Reply-to wijst naar een bestaand, gelezen adres: het afzenderadres
    # zelf (prijsalert@) heeft bewust geen postbus.
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    ALERT_FROM_EMAIL = os.getenv('ALERT_FROM_EMAIL', 'prijsalert@witgoedaanbod.nl')
    ALERT_FROM_NAME = os.getenv('ALERT_FROM_NAME', 'WitgoedAanbod.nl')
    ALERT_REPLY_TO = os.getenv('ALERT_REPLY_TO', 'info@witgoedaanbod.nl')
    # Waar contactformulier-berichten heen gemaild worden (komt via de
    # TransIP-doorstuurservice binnen op Peters eigen mailbox).
    CONTACT_TO_EMAIL = os.getenv('CONTACT_TO_EMAIL', 'info@witgoedaanbod.nl')

    # Sync
    SYNC_INTERVAL = 6  # hours


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
