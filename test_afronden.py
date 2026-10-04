"""Afronden vóór het indelen en eigen geluidsstappen voor koelkasten
(routes.main._AFRONDEN, _STAPPEN_PER_CATEGORIE, _stap_van).
Draaien: python test_afronden.py
"""
import os
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'afronden_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import create_app  # noqa: E402
from routes.main import _FILTERVELDEN, _stap_van  # noqa: E402

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    if not ok:
        fouten += 1

def stap(veld, waarde, cat='wasmachines'):
    s = _stap_van({veld: waarde}, veld, _FILTERVELDEN[veld], cat)
    return s['slug'] if s else None

# Breedte: koelkasten in mm, op hele cm afgerond.
check('595 mm (59,5 cm) telt als 60', stap('dimensionWidth', 595, 'koelkasten') == '60-70-cm')
check('598 mm telt als 60', stap('dimensionWidth', 598, 'koelkasten') == '60-70-cm')
check('594 mm (59,4) blijft 50-60', stap('dimensionWidth', 594, 'koelkasten') == '50-60-cm')
check('wasmachine 60 cm blijft 60-70', stap('dimensionWidth', 60) == '60-70-cm')
check('495 mm (49,5) telt als 50', stap('dimensionWidth', 495, 'koelkasten') == '50-60-cm')
# Toerental: op honderdtallen.
check('1351 telt als 1400', stap('spinSpeedRated', 1351) == '1400-1600-toeren')
check('1350 telt als 1400', stap('spinSpeedRated', 1350) == '1400-1600-toeren')
check('1349 blijft 1200-1400', stap('spinSpeedRated', 1349) == '1200-1400-toeren')
check('1551 telt als 1600', stap('spinSpeedRated', 1551) == 'vanaf-1600-toeren')
check('1400 blijft 1400-1600', stap('spinSpeedRated', 1400) == '1400-1600-toeren')
# Geluid: koelkasten eigen grens 36 dB, andere categorieën ongewijzigd.
check('koelkast 35 dB zeer stil', stap('noise', 35, 'koelkasten') == 'zeer-stil')
check('koelkast 36 dB stil', stap('noise', 36, 'koelkasten') == 'stil')
check('koelkast 44 dB stil', stap('noise', 44, 'koelkasten') == 'stil')
check('vaatwasser 44 dB nog zeer stil (tot 45)', stap('noise', 44, 'vaatwassers') == 'zeer-stil')
check('hoogte niet afgerond (85,4 blijft tot 90)', stap('dimensionHeight', 854, 'koelkasten') == 'tot-90-cm')

# Weergave: de productpagina toont de echte maat, niet de afgeronde.
from eprel_specs import _regels  # noqa: E402
regels = dict(_regels({'dimensionWidth': 595, 'dimensionHeight': 1850, 'dimensionDepth': 650},
                      'refrigeratingappliances2019'))
check('productpagina toont 59,5', regels.get('Afmetingen (b × h × d)', '').startswith('59,5'),
      regels.get('Afmetingen (b × h × d)'))

# Pagina's en links op een tijdelijke database.
app = create_app('development')
with app.app_context():
    from models import Category, EprelData, Offer, Product, db, utcnow
    koel = Category.query.filter_by(slug='koelkasten').first()
    if koel is None:
        koel = Category(name='Koelkasten', slug='koelkasten')
        db.session.add(koel)
        db.session.flush()
    for i, (db_, b) in enumerate([(34, 595)] * 9 + [(40, 595)] * 9):
        p = Product(ean=f'{i:013d}', title=f'Koelkast {i}', price=300 + i, bol_url='x',
                    category_id=koel.id, slug=f'koelkast-{i}', is_available=True, brand='Merk')
        db.session.add(p)
        db.session.flush()
        db.session.add(Offer(product_id=p.id, retailer='coolblue', price=300 + i,
                             is_available=True, last_synced=utcnow()))
        db.session.add(EprelData(product_id=p.id, gevonden=True,
                                 gegevens={'noise': db_, 'dimensionWidth': b}))
    db.session.commit()
c = app.test_client()
h = c.get('/category/koelkasten').get_data(as_text=True)
check('link "Zeer stille koelkasten (onder 36 dB) (9)"', 'Zeer stille koelkasten (onder 36 dB) (9)' in h)
check('link "Stille koelkasten (36-60 dB) (9)"', 'Stille koelkasten (36-60 dB) (9)' in h)
check('link breedte 60-70 met 18 (59,5 telt als 60)', 'van 60-70 cm breed (18)' in h)
check('geen 50-60-link meer', '/category/koelkasten/breedte/50-60-cm' not in h)
r = c.get('/category/koelkasten/geluid/zeer-stil')
check('zeer-stil pagina 200 met 9 modellen', r.status_code == 200 and ': 9 modellen' in r.get_data(as_text=True)
      or 'We volgen 9 ' in r.get_data(as_text=True))
s = c.get('/sitemap-kenmerken.xml').get_data(as_text=True)
check('sitemap: zeer-stil, stil en 60-70', all(x in s for x in ('/koelkasten/geluid/zeer-stil<',
                                                              '/koelkasten/geluid/stil<',
                                                              '/koelkasten/breedte/60-70-cm<')))

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
