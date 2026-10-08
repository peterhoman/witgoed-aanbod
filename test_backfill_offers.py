"""Boot-migratie _backfill_offers_from_products (app.py): maakt geen Bol-rij
meer aan voor een niet-leverbaar product dat Bol niet meer levert (8 okt).
Tijdelijke sqlite-database. Draaien: python test_backfill_offers.py
"""
import os
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'backfill_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import _backfill_offers_from_products, create_app  # noqa: E402

fouten = 0


def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)


app = create_app('development')
with app.app_context():
    from models import Category, Offer, Product, db
    cat = Category.query.first() or Category(name='Wasmachines', slug='wasmachines')
    db.session.add(cat)
    db.session.flush()
    weg = Product(ean='1', title='Weg bij Bol', brand='X', price=300, bol_url='https://bol/x',
                  category_id=cat.id, slug='weg-1', retailer='bol', is_available=False)
    oud = Product(ean='2', title='Oud Bol-product zonder rij', brand='X', price=300, bol_url='https://bol/y',
                  category_id=cat.id, slug='oud-2', retailer='bol', is_available=True)
    db.session.add_all([weg, oud])
    db.session.commit()

    _backfill_offers_from_products(db)
    check('niet-leverbaar product krijgt geen Bol-rij terug',
          Offer.query.filter_by(product_id=weg.id).count() == 0)
    check('leverbaar oud Bol-product wordt nog wel omgezet',
          Offer.query.filter_by(product_id=oud.id, retailer='bol').count() == 1)
    _backfill_offers_from_products(db)
    check('tweede keer: niets dubbel', Offer.query.filter_by(product_id=oud.id).count() == 1)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
