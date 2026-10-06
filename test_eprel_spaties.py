"""Typenummers met spaties (eprel.codes_uit_titel), 6 okt 2026.
Draaien: python test_eprel_spaties.py
"""
import sys
sys.path.insert(0, '.')

from eprel import codes_uit_titel, koppeling_klopt

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)

c = codes_uit_titel('Miele KFN 4397 CD el 125 Edition Koel-vriescombinatie Zilver')
check('Miele: heel nummer eerst', c[:2] == ['KFN 4397 CD', 'KFN 4397'], c)
c = codes_uit_titel('Liebherr IRBc 4120-22 Inbouw koelkast zonder vriesvak')
check('Liebherr: met en zonder achtervoegsel', c[:2] == ['IRBc 4120-22', 'IRBc 4120'], c)
c = codes_uit_titel('Miele G 7110 SCi AutoDos')
check('één letter is geen typenummer (te weinig hoofdletters)', 'G 7110' not in c, c)
c = codes_uit_titel('Koelkast inhoud 330 liter')
check('"inhoud 330" is geen typenummer', not any('330' in x for x in c), c)
c = codes_uit_titel('Bosch WQG133DANL Serie 6 warmtepompdroger 9 kg')
check('gewoon typenummer blijft werken', c[0] == 'WQG133DANL', c)
c = codes_uit_titel('Samsung WW11DG5B25AB SuperSpeed')
check('gewoon typenummer zonder spaties ongewijzigd', c == ['WW11DG5B25AB'], c)
check('koppeling: IRBc 4120 past bij IRBc 4120_994878551',
      koppeling_klopt('IRBc 4120-22, IRBc 4120', 'IRBc 4120_994878551', 'Liebherr IRBc 4120-22'))
check('koppeling: KFN 4397 CD past bij KFN 4397 CD 125 Edition',
      koppeling_klopt('KFN 4397 CD', 'KFN 4397 CD 125 Edition', 'Miele KFN 4397 CD el 125 Edition'))

# Inhaalslag: oude niet-gevonden rijen met een gespatieerd typenummer.
import os
import tempfile
from datetime import datetime
os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.join(tempfile.mkdtemp(), 'sp.db').replace('\\', '/')
from app import create_app  # noqa: E402
app = create_app('development')
with app.app_context():
    from models import Category, EprelData, Product, db
    from eprel_bijwerken import _met_spaties_opnieuw
    cat = Category.query.first()
    oud = datetime(2026, 9, 1)
    for i, (titel, gevonden, wanneer) in enumerate([
            ('Miele KFN 4397 CD el 125 Edition', False, oud),      # opnieuw
            ('Liebherr IRBc 4120-22 Inbouw koelkast', False, oud),  # opnieuw
            ('Bosch KGN39VLCT No Frost', False, oud),               # geen spaties
            ('Miele KFN 4397 CD', True, oud),                       # al gevonden
            ('Miele KFN 4398 CD', False, datetime(2026, 10, 7))]):  # na de peildatum
        p = Product(ean=f'{i:013d}', title=titel, price=1, bol_url='x', category_id=cat.id, slug=f's{i}')
        db.session.add(p)
        db.session.flush()
        db.session.add(EprelData(product_id=p.id, gevonden=gevonden, gezocht=gevonden, opgehaald_at=wanneer))
    db.session.commit()
    rijen = _met_spaties_opnieuw(10)
    titels = sorted(Product.query.get(r.product_id).title[:12] for r in rijen)
    check('inhaalslag pakt alleen de twee juiste', titels == ['Liebherr IRB', 'Miele KFN 43'], titels)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
