#!/usr/bin/env python
"""Initialize database with sample categories."""

from app import create_app
from models import db, Category
import os

def init_database():
    app = create_app()

    with app.app_context():
        # Create tables
        db.create_all()
        print("[+] Database tables created")

        # Add sample categories
        categories = [
            {'name': 'Wasmachines', 'slug': 'wasmachines', 'description': 'Vergelijk alle wasmachines op Bol.com'},
            {'name': 'Drogers', 'slug': 'drogers', 'description': 'Vind de beste drogers'},
            {'name': 'Wasdroogcombinaties', 'slug': 'wasdroogcombinaties', 'description': 'Combinatie was- en drogers'},
            {'name': 'Koelkasten', 'slug': 'koelkasten', 'description': 'Alle koelkasten op een rij'},
            {'name': 'Vaatwassers', 'slug': 'vaatwassers', 'description': 'Vergelijk vaatwassers'},
            {'name': 'Magnetrons', 'slug': 'magnetrons', 'description': 'De beste magnetrons'},
            {'name': 'Ovens', 'slug': 'ovens', 'description': 'Alle ovens op Bol.com'},
        ]

        for cat_data in categories:
            if not Category.query.filter_by(slug=cat_data['slug']).first():
                category = Category(**cat_data)
                db.session.add(category)
                print(f"[+] Added category: {cat_data['name']}")

        db.session.commit()
        print("[+] Database initialized successfully!")

if __name__ == '__main__':
    init_database()
