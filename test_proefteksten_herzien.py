"""EPREL in de tekstprompt en de eenmalige herziening van de proefteksten
(13 okt 2026, teksten_bijwerken._PROEF_HERZIEN_VOOR). Het model wordt
nagebootst; tijdelijke sqlite-database. Draaien: python test_proefteksten_herzien.py
"""
import os
import sys
import tempfile
from datetime import datetime
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'herzien_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

import ai_content  # noqa: E402
import teksten_bijwerken as tb  # noqa: E402
from app import create_app  # noqa: E402

fouten = 0


def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)


app = create_app('development')
app.config['ANTHROPIC_API_KEY'] = 'nep'
aanroepen = []


def nep_schrijf(product, model=None, api_key=None):
    prompt = ai_content.bouw_prompt(product)
    aanroepen.append(prompt)
    return {'tekst': f'Nieuwe tekst voor {product.title}, energieklasse uit het register.',
            'kosten': {'invoer': 1, 'uitvoer': 1, 'cache_geschreven': 0, 'cache_gelezen': 0, 'euro': 0.001},
            'bron_specs': 0}


ai_content.schrijf_beschrijving = nep_schrijf
ai_content.bewaak_budget = lambda limiet: None

with app.app_context():
    from models import AIContent, CatalogusAanvulling, Category, EprelData, Product, db
    cat = Category.query.filter_by(slug='koelkasten').first() or Category(name='Koelkasten', slug='koelkasten')
    db.session.add(cat)
    db.session.flush()

    def maak(ean, titel, proef, eprel, oud=True):
        p = Product(ean=ean, title=titel, brand='Miele', price=999, bol_url='', category_id=cat.id,
                    slug=f'p-{ean}', is_available=True, ai_description='Oude tekst: energielabel niet bekend.')
        db.session.add(p)
        db.session.flush()
        db.session.add(AIContent(product_id=p.id, content_type='beschrijving',
                                 content='Oude tekst: energielabel niet bekend.',
                                 generated_at=datetime(2026, 10, 6, 13, 0) if oud else datetime(2026, 10, 14)))
        if proef:
            db.session.add(CatalogusAanvulling(product_id=p.id, ean=ean, categorie='koelkasten'))
        if eprel:
            db.session.add(EprelData(product_id=p.id, gevonden=True, gezocht=True, gezocht_op='KFN 4397 CD',
                                     modelnummer='KFN 4397 CD', productgroep='refrigeratingappliances2019',
                                     registratienummer='2491384',
                                     gegevens={'energyClass': 'C', 'noise': 35, 'totalVolume': 360}))
        return p

    a = maak('1', 'Miele KFN 4397 CD koel-vriescombinatie', proef=True, eprel=True)
    b = maak('2', 'Miele KFN 4397 CD andere proef zonder EPREL', proef=True, eprel=False)
    c = maak('3', 'Miele KFN 4397 CD geen proefproduct', proef=False, eprel=True)
    d = maak('4', 'Miele KFN 4397 CD proef met nieuwe tekst', proef=True, eprel=True, oud=False)
    db.session.commit()

    prompt = ai_content.bouw_prompt(a)
    check('prompt bevat EPREL-energieklasse', 'Energieklasse: C' in prompt and 'EPREL' in prompt, prompt)
    check('prompt zegt niet meer "geen enkele bekend" als EPREL er is',
          'geen enkele bekend' not in prompt, prompt)

    tb._draai_ronde(app)
    check('alleen de proeftekst met EPREL en oude datum herschreven', len(aanroepen) == 1, len(aanroepen))
    a2 = Product.query.get(a.id)
    check('nieuwe tekst zichtbaar', a2.ai_description.startswith('Nieuwe tekst'), a2.ai_description)
    check('precies één tekstrij per product',
          AIContent.query.filter_by(product_id=a.id, content_type='beschrijving').count() == 1)
    check('proef zonder EPREL ongemoeid', Product.query.get(b.id).ai_description.startswith('Oude'))
    check('geen proefproduct ongemoeid', Product.query.get(c.id).ai_description.startswith('Oude'))
    check('proef met tekst van na de reparatie ongemoeid', Product.query.get(d.id).ai_description.startswith('Oude'))

    tb._draai_ronde(app)
    check('tweede ronde: niets meer te herzien', len(aanroepen) == 1, len(aanroepen))

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
