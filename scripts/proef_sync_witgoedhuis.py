"""Proef: de echte Witgoedhuis-feed tegen een tijdelijke database met een paar
apparaten die ook in die feed staan. Raakt productie niet.
Draaien: python scripts/proef_sync_witgoedhuis.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(tempfile.mkdtemp(), 'wh.db').replace('\\', '/')

from sync_witgoedhuis import FEED_URL_DEFAULT, _feed_records, sync_witgoedhuis  # noqa: E402

records = _feed_records(FEED_URL_DEFAULT)
print('bruikbare feedproducten (nieuw, op voorraad, met EAN en prijs):', len(records))
eans = list(records)[:5]

from app import create_app  # noqa: E402
app = create_app('development')
with app.app_context():
    from models import Category, Offer, Product, db
    cat = Category.query.first()
    for i, ean in enumerate(eans):
        db.session.add(Product(ean=ean, title=f'Proef {i}', price=999, bol_url='x',
                               category_id=cat.id, slug=f'proef-{i}', is_available=True))
    db.session.commit()

sync_witgoedhuis()
sync_witgoedhuis()  # tweede keer: bijwerken, niet dubbel aanmaken

with app.app_context():
    from models import Offer, Product, SyncLog
    aanbiedingen = Offer.query.filter_by(retailer='witgoedhuis').all()
    print('aanbiedingen na twee rondes:', len(aanbiedingen), '(verwacht', len(eans), ')')
    for o in aanbiedingen[:3]:
        print(f'  {o.product.ean} € {o.price}  {o.url[:60]}')
        print(f'     klik: {o.link[:110]}')
    print('laagste prijs op product bijgewerkt:', all(p.price < 999 for p in Product.query.all()))
    print('synclog:', [(l.products_synced, l.products_updated, l.errors) for l in SyncLog.query.all()])
