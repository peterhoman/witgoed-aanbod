"""Koelkasten per hoogte (routes.main._FILTERVELDEN 'dimensionHeight', alleen
koelkasten). Draait op een tijdelijke sqlite-database.
Draaien: python test_koelkast_hoogte.py
"""
import os
import re
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'hoogte_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import create_app  # noqa: E402

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    if not ok:
        fouten += 1

# Hoogtes zoals EPREL ze geeft: koelkasten in mm, soms in cm. 8 per stap,
# plus randgevallen precies op een grens.
KOELKASTEN = ([850] * 8 + [1220] * 8 + [1440] * 8 + [1772] * 8 + [1855] * 8 + [2010] * 7
              + [190])  # 190 = cm, hoort bij vanaf-190
GRENS = {900: '90-130-cm', 1800: '180-190-cm'}

app = create_app('development')
with app.app_context():
    from models import Category, EprelData, Offer, Product, db, utcnow
    def categorie(slug, naam):
        c = Category.query.filter_by(slug=slug).first()
        if c is None:
            c = Category(name=naam, slug=slug)
            db.session.add(c)
            db.session.flush()
        return c
    koel, was = categorie('koelkasten', 'Koelkasten'), categorie('wasmachines', 'Wasmachines')
    nr = 0
    def product(cat, gegevens):
        global nr
        nr += 1
        p = Product(ean=f'{nr:013d}', title=f'Apparaat {nr}', price=300 + nr, bol_url='x',
                    category_id=cat.id, slug=f'apparaat-{nr}', is_available=True, brand='Merk')
        db.session.add(p)
        db.session.flush()
        db.session.add(Offer(product_id=p.id, retailer='coolblue', price=300 + nr,
                             is_available=True, last_synced=utcnow()))
        db.session.add(EprelData(product_id=p.id, gevonden=True, gegevens=gegevens))
    for h in KOELKASTEN + list(GRENS):
        product(koel, {'dimensionHeight': h})
    for _ in range(10):
        product(was, {'dimensionHeight': 85})
    db.session.commit()

    from routes.main import _eprel_waarde, _FILTERVELDEN, _stap_voor
    opzet = _FILTERVELDEN['dimensionHeight']
    for mm, slug in GRENS.items():
        stap = _stap_voor(_eprel_waarde({'dimensionHeight': mm}, 'dimensionHeight'), opzet)
        check(f'{mm} mm valt in {slug} (ondergrens telt mee)', stap and stap['slug'] == slug)

c = app.test_client()
verwacht = {'tot-90-cm': 8, '90-130-cm': 9, '130-170-cm': 8, '170-180-cm': 8,
            '180-190-cm': 9, 'vanaf-190-cm': 8}
for slug, n in verwacht.items():
    r = c.get(f'/category/koelkasten/hoogte/{slug}')
    h = r.get_data(as_text=True)
    check(f'{slug}: pagina bestaat (200)', r.status_code == 200, r.status_code)
    check(f'{slug}: {n} modellen in de titel',
          f': {n} modellen' in (re.search(r'<title>([^<]*)', h) or [None, ''])[1],
          re.search(r'<title>([^<]*)', h).group(1) if r.status_code == 200 else '')
    check(f'{slug}: bijgewerkt-regel en vragen', 'Bijgewerkt op ' in h and 'Veelgestelde vragen over' in h)

h = c.get('/category/koelkasten').get_data(as_text=True)
check('categoriepagina linkt naar alle zes', all(f'/category/koelkasten/hoogte/{s}' in h for s in verwacht))
check('linktekst "Lage koelkasten (tot 90 cm hoog)"', 'Lage koelkasten (tot 90 cm hoog)' in h)
s = c.get('/sitemap-kenmerken.xml').get_data(as_text=True)
check('sitemap bevat de zes', all(f'/koelkasten/hoogte/{x}<' in s for x in verwacht))
check('wasmachines geen hoogtepagina in de sitemap', '/wasmachines/hoogte/' not in s)
h = c.get('/category/wasmachines').get_data(as_text=True)
check('wasmachines geen hoogtelink', '/category/wasmachines/hoogte/' not in h)
r = c.get('/category/wasmachines/hoogte/tot-90-cm')
check('wasmachines/hoogte stuurt door naar de categorie', r.status_code == 301
      and r.headers.get('Location', '').endswith('/category/wasmachines'), r.status_code)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
