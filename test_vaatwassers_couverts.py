"""Vaatwassers krijgen geen kilopagina (routes.main._VELD_NIET_IN): EPREL zet
daar het aantal couverts in ratedCapacity. Draait op een tijdelijke
sqlite-database. Draaien: python test_vaatwassers_couverts.py
"""
import os
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'couverts_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import create_app  # noqa: E402

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra else ''))
    if not ok:
        fouten += 1

app = create_app('development')
with app.app_context():
    from models import Category, EprelData, Offer, Product, db, utcnow
    for slug, waarde in (('vaatwassers', 13), ('wasmachines', 8)):
        cat = Category.query.filter_by(slug=slug).first()
        if cat is None:
            cat = Category(name=slug.capitalize(), slug=slug)
            db.session.add(cat)
            db.session.flush()
        for i in range(10):
            p = Product(ean=f'{waarde:02d}{i:011d}', title=f'{slug} {i}', price=400 + i,
                        bol_url='x', category_id=cat.id, slug=f'{slug}-{i}', is_available=True,
                        brand='Merk')
            db.session.add(p)
            db.session.flush()
            db.session.add(Offer(product_id=p.id, retailer='coolblue', price=400 + i,
                                 is_available=True, last_synced=utcnow()))
            db.session.add(EprelData(product_id=p.id, gevonden=True,
                                     gegevens={'ratedCapacity': waarde}))
    db.session.commit()

c = app.test_client()
r = c.get('/category/vaatwassers/vulgewicht/vanaf-11-kg')
check('oud vaatwasseradres stuurt door (301)', r.status_code == 301, r.status_code)
check('naar de categorie', r.headers.get('Location', '').endswith('/category/vaatwassers'),
      r.headers.get('Location'))
r = c.get('/category/wasmachines/vulgewicht/8-9-kg')
check('wasmachines 8 kg bestaat nog (200)', r.status_code == 200, r.status_code)
h = c.get('/category/vaatwassers').get_data(as_text=True)
check('linkblok staat er (anders zegt de volgende niets)', 'category-facet-links' in h)
check('geen kilolink op de vaatwasserpagina', '/category/vaatwassers/vulgewicht/' not in h)
h = c.get('/category/wasmachines').get_data(as_text=True)
check('kilolink op de wasmachinepagina blijft', '/category/wasmachines/vulgewicht/8-9-kg' in h)
s = c.get('/sitemap-kenmerken.xml').get_data(as_text=True)
check('sitemap zonder vaatwasser-kilo', '/vaatwassers/vulgewicht/' not in s)
check('sitemap met wasmachine-kilo', '/wasmachines/vulgewicht/8-9-kg' in s, s[:300])

print()
print('ALLES GOED' if not fouten else f'{fouten} FOUT(EN)')
sys.exit(1 if fouten else 0)
