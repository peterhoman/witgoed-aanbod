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

    # Google site-verificatie: de content-waarde van de meta-verificatietag.
    # De Search Console-property zelf is een domein-property (DNS-geverifieerd
    # onder pfmhoman@gmail.com); deze HTML-tag is 23-07 toegevoegd voor de
    # Merchant Center-verificatie (gratis Shopping-vermeldingen, zelfde
    # account). Geen geheim — staat bewust publiek in de <head> en moet
    # blijven staan (Google hercontroleert periodiek). De eerdere tag van
    # het avantiusshop-account (2026-07-11) is bewust verwijderd.
    GOOGLE_SITE_VERIFICATION = os.getenv(
        'GOOGLE_SITE_VERIFICATION',
        'FSTWs3GDdEhblm5n4TdA8e6AmXFhMEg8b2KLHom8qZ0')

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
    # Waar contactformulier-berichten heen gemaild worden. Bewust direct
    # naar de Gmail-inbox en niet naar info@witgoedaanbod.nl: die extra
    # sprong (Brevo -> TransIP-doorstuur -> Gmail) bleek onbetrouwbaar
    # voor Brevo-mail van het eigen domein (19-07 permanent "deferred"),
    # terwijl Brevo -> Gmail direct aantoonbaar goed werkt. info@ blijft
    # het publieke adres voor mail van échte mensen (die route werkt wel).
    CONTACT_TO_EMAIL = os.getenv('CONTACT_TO_EMAIL', 'pfmhoman@gmail.com')

    # De Babbelbot, de advies-chatbot (routes/chat.py + chatbot.py). Zonder
    # OPENROUTER_API_KEY is de widget onzichtbaar en weigert het endpoint —
    # zelfde patroon als BREVO_API_KEY hierboven. Model instelbaar zodat er
    # zonder deploy gewisseld kan worden.
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    # gemini-flash-1.5 (uit de oorspronkelijke opdracht) bestaat niet meer
    # bij OpenRouter (geverifieerd 21-07 via hun /models-endpoint);
    # 2.5-flash-lite is de huidige goedkoopste opvolger.
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-flash-lite')

    # Eigen productbeschrijvingen (ai_content.py). Zonder ANTHROPIC_API_KEY
    # weigert het eindpunt -- zelfde patroon als BREVO_API_KEY en
    # OPENROUTER_API_KEY hierboven. Let op: tot 27-07 stond hier in productie
    # de letterlijke tekst "your-claude-api-key", dus "sleutel is gevuld" is
    # geen bewijs dat hij werkt; alleen een echte aanroep bewijst dat.
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    # Model instelbaar zodat er zonder deploy gewisseld kan worden (bv. naar
    # claude-sonnet-5 als de kosten per tekst tegenvallen).
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-opus-5')
    # Harde geldgrens per etmaal, in euro's. Aanleiding: op een eerdere site
    # van de eigenaar bleef een generator herschrijven en kostte dat bijna
    # 800 euro voordat iemand het zag. De redenering dat dat hier niet kan
    # (ai_content.moet_herschrijven schrijft nooit terug bij krimp, dus elk
    # product kan hooguit een keer omhoog) is geen plafond -- dit wel.
    #
    # Vijf euro is ruim boven een normale dag (nieuwe producten kosten samen
    # centen) en ruim onder een ongeluk. De hele catalogus in een keer kost
    # 34 euro en loopt hier dus tegenaan; dat is de bedoeling. Een bewuste
    # uitrol verhoogt de grens tijdelijk via de omgevingsvariabele.
    AI_DAGLIMIET_EURO = float(os.getenv('AI_DAGLIMIET_EURO', '5'))

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
