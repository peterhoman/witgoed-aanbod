"""Een filterstap onder de ondergrens stuurt door (routes.main._dichtstbijzijnde_stap).
Draait op een tijdelijke sqlite-database. Draaien: python test_kleine_filterpagina.py
"""
import os
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'klein_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import create_app  # noqa: E402

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    if not ok:
        fouten += 1

app = create_app('development')
with app.app_context():
    from models import Category, EprelData, Offer, Product, db, utcnow
    cat = Category.query.filter_by(slug='wasdroogcombinaties').first()
    if cat is None:
        cat = Category(name='Wasdroogcombinaties', slug='wasdroogcombinaties')
        db.session.add(cat)
        db.session.flush()
    # 10 x 1400 toeren (pagina 1400-1600 bestaat), 3 x 1250 (1200-1400 te klein),
    # 9 x 1600 (vanaf-1600 bestaat, maar kleiner dan 1400-1600).
    for i, toeren in enumerate([1400] * 10 + [1250] * 3 + [1600] * 9):
        p = Product(ean=f'{i:013d}', title=f'Wasdroog {i}', price=500 + i, bol_url='x',
                    category_id=cat.id, slug=f'wasdroog-{i}', is_available=True, brand='Merk')
        db.session.add(p)
        db.session.flush()
        db.session.add(Offer(product_id=p.id, retailer='coolblue', price=500 + i,
                             is_available=True, last_synced=utcnow()))
        db.session.add(EprelData(product_id=p.id, gevonden=True,
                                 gegevens={'spinSpeedRated': toeren}))
    db.session.commit()

c = app.test_client()
r = c.get('/category/wasdroogcombinaties/toerental/1200-1400-toeren')
check('te kleine stap: 301', r.status_code == 301, r.status_code)
check('naar de dichtstbijzijnde stap die bestaat (1400-1600)',
      r.headers.get('Location', '').endswith('/category/wasdroogcombinaties/toerental/1400-1600-toeren'),
      r.headers.get('Location'))
r = c.get('/category/wasdroogcombinaties/toerental/tot-1200-toeren')
check('tot-1200 (leeg): naar 1400-1600 via de dichtstbijzijnde',
      r.status_code == 301 and r.headers.get('Location', '').endswith('/toerental/1400-1600-toeren'),
      (r.status_code, r.headers.get('Location')))
r = c.get('/category/wasdroogcombinaties/geluid/zeer-stil')
check('veld zonder enige pagina: naar de categorie',
      r.status_code == 301 and r.headers.get('Location', '').endswith('/category/wasdroogcombinaties'),
      (r.status_code, r.headers.get('Location')))
r = c.get('/category/wasdroogcombinaties/toerental/onzin')
check('geen bestaande stap: 404', r.status_code == 404, r.status_code)
r = c.get('/category/wasdroogcombinaties/toerental/1400-1600-toeren')
check('bestaande stap blijft 200', r.status_code == 200, r.status_code)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
