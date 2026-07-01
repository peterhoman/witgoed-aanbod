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

    # Claude API
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Bit.ly API for URL shortening
    BITLY_TOKEN = os.getenv('BITLY_TOKEN')

    # Site config
    SITE_NAME = os.getenv('SITE_NAME', 'WitgoedAanbod.nl')
    SITE_URL = os.getenv('SITE_URL', 'https://witgoedaanbod.nl')

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
