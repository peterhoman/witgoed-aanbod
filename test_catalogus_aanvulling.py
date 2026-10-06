"""Catalogusaanvulling (catalogus_aanvulling.py): kandidaten, dubbelcheck,
verdeling en het proefmaximum. Feeds en EPREL worden nagebootst; tijdelijke
sqlite-database. Draaien: python test_catalogus_aanvulling.py
"""
import os
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'aanvulling_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

import catalogus_aanvulling as ca  # noqa: E402
from app import create_app  # noqa: E402

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)

def rij(ean, titel, prijs, winkel, merk='Miele'):
    return (ean, titel, merk, prijs, 'https://x/foto.jpg', 'Beschrijving', winkel)

# 1. Kandidaten: alleen witgoed bij 2+ winkels, met de opschoonregels.
rijen = [
    rij('4002516000001', 'Miele KFN 4397 CD el Koel-vriescombinatie', 1299, 'expert'),
    rij('4002516000001', 'Miele KFN 4397 CD el Koel-vriescombinatie', 1279, 'ep'),
    rij('4002516000002', 'Miele WWD 320 WPS Wasmachine', 1099, 'expert'),          # 1 winkel
    rij('4002516000003', 'Miele stofzuigerzakken GN', 19, 'expert'),               # accessoire
    rij('4002516000003', 'Miele stofzuigerzakken GN', 19, 'ep'),
    rij('4002516000004', 'Liebherr IRBc 4120-22 Inbouw koelkast', 899, 'expert', 'Liebherr'),
    rij('4002516000004', 'Liebherr IRBc 4120-22', 899, 'witgoedhuis', 'Liebherr'),
    rij('4002516000005', 'Miele Koel-vriescombinatie goedkoop', 50, 'expert'),     # te goedkoop
    rij('4002516000005', 'Miele Koel-vriescombinatie goedkoop', 50, 'ep'),
]
k = ca.kandidaten(rijen)
check('alleen de twee echte kandidaten', sorted(v['ean'] for v in k.values()) == ['4002516000001', '4002516000004'],
      sorted(v['ean'] for v in k.values()))
miele = next(v for v in k.values() if v['ean'] == '4002516000001')
check('laagste prijs als beginprijs', miele['prijs'] == 1279)
check('categorie koelkasten', miele['cat'] == 'koelkasten')
lieb = next(v for v in k.values() if v['ean'] == '4002516000004')
check('beschrijvende titel wint van de Witgoedhuis-titel', 'Inbouw koelkast' in lieb['titel'], lieb['titel'])

# 2. Dubbelcheck op merk + typenummer.
bestaande = {'miele': [ca._typecodes('Miele KFN 4397 CD Koel-vriescombinatie wit')]}
check('zelfde merk en typenummer = dubbel', ca.is_dubbel('Miele', 'Miele KFN 4397 CD el 125 Edition', bestaande))
check('ander merk = geen dubbel', not ca.is_dubbel('Liebherr', 'Liebherr KFN 4397 CD', bestaande))
check('ander typenummer = geen dubbel', not ca.is_dubbel('Miele', 'Miele KFN 4398 CD', bestaande))

check('WCS en WPS zijn verschillende machines',
      not ca.is_dubbel('Miele', 'Miele WEA 135 WPS Excellence', {'miele': [ca._typecodes('Miele WEA 135 WCS Excellence')]}))
check('AEG-serie is geen typenummer',
      not ca.is_dubbel('AEG', 'AEG 6000 ProSense wasmachine LR6KOLN',
                       {'aeg': [ca._typecodes('AEG 6000 SatelliteClean vaatwasser FFB64627ZM')]}))
check('kleurvariant (edt/cs) is dubbel',
      ca.is_dubbel('Miele', 'Miele KFN 4795 AD edt/cs Koel-vriescombinatie',
                   {'miele': [ca._typecodes('Miele KFN 4795 AD Koel-vriescombinatie')]}))

# 3. De hele ronde op een tijdelijke database, met nagebootste feeds en EPREL.
app = create_app('development')
nep_rijen = []
for i in range(40):
    ean = f'40025161{i:05d}'
    nep_rijen += [rij(ean, f'Miele KFN {4000 + i} CD Koel-vriescombinatie', 999, 'expert'),
                  rij(ean, f'Miele KFN {4000 + i} CD Koel-vriescombinatie', 989, 'ep')]
for i in range(30):
    ean = f'40025162{i:05d}'
    nep_rijen += [rij(ean, f'Miele WWD {300 + i} WPS Wasmachine', 899, 'expert'),
                  rij(ean, f'Miele WWD {300 + i} WPS Wasmachine', 899, 'ep')]
# Twee kleurvarianten van één nieuw model in dezelfde ronde: één mag erin.
for ean in ('4002516999001', '4002516999002'):
    nep_rijen += [rij(ean, 'Miele FNS 4382 D Vrijstaande diepvries', 1399, 'expert'),
                  rij(ean, 'Miele FNS 4382 D Vrijstaande diepvries', 1399, 'ep')]
ca._feeds = lambda: list(nep_rijen)
import eprel  # noqa: E402
eprel.zoek = lambda cat, titel, pauze=0: ({'gezocht': True, 'gevonden': True, 'gezocht_op': 'x',
                                          'productgroep': 'g', 'modelnummer': 'KFN', 'gegevens': {}}
                                         if '40' in titel[-20:] or 'KFN 40' in titel else
                                         {'gezocht': True, 'gevonden': False, 'gezocht_op': 'x'})
import sync_expert, sync_ep, sync_voordeligwitgoed, sync_alternate, sync_witgoedhuis  # noqa: E402,E401
for m in (sync_expert, sync_ep, sync_voordeligwitgoed, sync_alternate, sync_witgoedhuis):
    setattr(m, m.__name__, lambda: None)  # winkelsyncs niet echt draaien

with app.app_context():
    from models import Category, Product, db
    for slug in ca.VERDELING:
        if not Category.query.filter_by(slug=slug).first():
            db.session.add(Category(name=slug.capitalize(), slug=slug))
    db.session.commit()
    cat = Category.query.filter_by(slug='koelkasten').first()
    db.session.add(Product(ean='99', title='Miele KFN 4005 CD bestaand', brand='Miele', price=1,
                           bol_url='x', category_id=cat.id, slug='bestaand'))
    db.session.commit()

uit = ca.vul_catalogus_aan(app)
with app.app_context():
    from models import CatalogusAanvulling
    per_cat = {}
    for r in CatalogusAanvulling.query.all():
        per_cat[r.categorie] = per_cat.get(r.categorie, 0) + 1
check('koelkasten: 39 KFN + 1 FNS (quotum 45 niet vol)', per_cat.get('koelkasten') == 40, per_cat)
check('wasmachines tot hun quotum (18)', per_cat.get('wasmachines') == 18, per_cat)
check('dubbelen tegengehouden: bestaande KFN 4005 CD en de tweede FNS 4382 D', uit['dubbel'] == 2, uit)
with app.app_context():
    from models import Product as P
    check('FNS 4382 D maar één keer aangemaakt', P.query.filter(P.title.like('%FNS 4382 D%')).count() == 1)
check('adressen terug', len(uit['adressen']) == 58 and all(a.endswith(tuple('0123456789')) for a in uit['adressen']))
with app.app_context():
    from models import EprelData
    check('EPREL-uitkomst bewaard bij de nieuwe producten', EprelData.query.count() >= 45, EprelData.query.count())

uit2 = ca.vul_catalogus_aan(app)
check('tweede ronde: niets meer bij deze categorieën', uit2['aangemaakt'] == 0, uit2)
# Weggehaalde dubbelen: product met tekst en EPREL-rij wordt verwijderd en
# komt niet terug.
with app.app_context():
    from models import AIContent, Product as P2, db as db2
    cat = Category.query.filter_by(slug='koelkasten').first()
    p = P2(ean='4002516741725', title='Miele FNS 4382 D dubbel', brand='Miele', price=1,
           bol_url='', category_id=cat.id, slug='dubbel-weg')
    db2.session.add(p)
    db2.session.flush()
    db2.session.add(AIContent(product_id=p.id, content_type='beschrijving', content='x'))
    db2.session.add(CatalogusAanvulling(product_id=p.id, ean=p.ean, categorie='koelkasten'))
    db2.session.commit()
ca.vul_catalogus_aan(app)
with app.app_context():
    check('dubbele kleurvariant weggehaald, met tekst en al',
          P2.query.filter_by(ean='4002516741725').count() == 0
          and AIContent.query.count() == 0)
    cat = Category.query.filter_by(slug='koelkasten').first()
    zus = P2(ean='4002516741596', title='Miele FNS 4382 D zuster', brand='Miele', price=1,
             bol_url='', category_id=cat.id, slug='miele-fns-4382-d-zuster-4002516741596')
    db2.session.add(zus)
    db2.session.commit()
r = app.test_client().get('/product/miele-fns-4382-d-vrijstaande-diepvries-4002516741725')
check('oud adres stuurt met 301 door naar het zustermodel',
      r.status_code == 301 and r.headers.get('Location', '').endswith('/product/miele-fns-4382-d-zuster-4002516741596'),
      (r.status_code, r.headers.get('Location')))

ca.PROEF_MAXIMUM = 58
uit3 = ca.vul_catalogus_aan(app)
check('proefmaximum bereikt: doet niets', uit3.get('reden') == 'proefmaximum bereikt', uit3)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
