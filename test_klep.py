"""Veiligheidsklep van de syncs telt alleen recent geleverde aanbiedingen
(verouderde_aanbiedingen.recent_bekend). Tijdelijke sqlite-database.
Draaien: python test_klep.py
"""
import os
import sys
import tempfile
from datetime import timedelta
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'klep_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import create_app  # noqa: E402

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)

app = create_app('development')
with app.app_context():
    from models import Category, Offer, Product, db, utcnow
    from sync_ep import MIN_FEED_RATIO
    from verouderde_aanbiedingen import recent_bekend
    cat = Category.query.first()
    nu = utcnow()
    for i in range(30):
        p = Product(ean=f'{i:013d}', title=f'P{i}', price=100, bol_url='x', category_id=cat.id, slug=f'p{i}')
        db.session.add(p)
        db.session.flush()
        oud = i >= 10  # 10 vers, 20 al weken niet in de feed
        db.session.add(Offer(product_id=p.id, retailer='ep', price=100, is_available=not oud,
                             last_synced=nu - timedelta(days=20 if oud else 0, hours=0 if oud else 6)))
    db.session.add(Offer(product_id=1, retailer='coolblue', price=90, last_synced=nu))
    db.session.commit()

    check('telt alleen verse aanbiedingen van deze winkel', recent_bekend('ep') == 10, recent_bekend('ep'))
    check('andere winkel apart', recent_bekend('coolblue') == 1)
    # Gewone dag: 9 van de 10 verse terug -> opruimen mag (oud: 9 < 30*0,5 -> klep).
    check('gewone dag: klep slaat niet aan', not (9 < recent_bekend('ep') * MIN_FEED_RATIO))
    check('vroeger sloeg hij hier wel aan', 9 < Offer.query.filter_by(retailer='ep').count() * MIN_FEED_RATIO)
    # Echte storing: maar 3 van de 10 terug -> klep moet aanslaan.
    check('halflege feed: klep slaat aan', 3 < recent_bekend('ep') * MIN_FEED_RATIO)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
