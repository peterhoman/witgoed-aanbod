#!/usr/bin/env python
"""
One-off migration: drop and recreate the (currently empty) products table
so it picks up the new is_example column.

Safe to run because no successful Bol.com sync has ever populated this
table in production. Run this once, manually, after deploying the updated
models.py (e.g. via Railway's Console/Shell tab), then run
seed_example_products.py.
"""

from app import create_app
from models import db, Product


def migrate():
    app = create_app()

    with app.app_context():
        Product.__table__.drop(db.engine, checkfirst=True)
        print("[+] Dropped products table (if it existed)")

        db.create_all()
        print("[+] Recreated products table with current schema (incl. is_example)")


if __name__ == '__main__':
    migrate()
