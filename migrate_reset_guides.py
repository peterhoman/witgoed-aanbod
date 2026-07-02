#!/usr/bin/env python
"""
One-off migration: drop and recreate the guides table so it picks up
the new post_type column.

Safe to run: all guide content is fully reproducible via seed_guides.py
(no user-generated data in this table). Run this once after deploying
the updated models.py, then run seed_guides.py again.
"""

from sqlalchemy import text
from app import create_app
from models import db


def migrate():
    app = create_app()

    with app.app_context():
        is_postgres = db.engine.dialect.name == 'postgresql'
        drop_sql = "DROP TABLE IF EXISTS guides CASCADE" if is_postgres else "DROP TABLE IF EXISTS guides"

        with db.engine.connect() as conn:
            conn.execute(text(drop_sql))
            conn.commit()
        print("[+] Dropped guides table (if it existed)")

        db.create_all()
        print("[+] Recreated guides table with current schema (incl. post_type)")


if __name__ == '__main__':
    migrate()
