"""Herziening van oude teksten via de Batch API (teksten_bijwerken,
_herzien_via_batch; Peters ja 16 okt 2026). Anthropic wordt nagebootst;
tijdelijke sqlite-database. Draaien: python test_herzien_batch.py
"""
import os
import sys
import tempfile
from datetime import datetime
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'batch_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

import ai_content  # noqa: E402
import teksten_bijwerken as tb  # noqa: E402
from app import create_app  # noqa: E402

fouten = 0


def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)


ingeleverd, klaar = [], {'klaar': False}
ai_content.dien_batch_in = lambda producten, model=None, api_key=None: (ingeleverd.append([p.id for p in producten]) or 'batch-1')
ai_content.batch_toestand = lambda batch_id, api_key=None: {'klaar': klaar['klaar'], 'status': 'x'}


def nep_resultaten(batch_id, api_key=None):
    for pid in ingeleverd[0]:
        yield {'product_id': pid, 'tekst': f'Batchtekst {pid} met energieklasse C.', 'fout': None,
               'kosten': {'invoer': 1, 'uitvoer': 1, 'cache_geschreven': 0, 'cache_gelezen': 0, 'euro': 0.007}}


ai_content.batch_resultaten = nep_resultaten
ai_content.schrijf_beschrijving = lambda *a, **k: (_ for _ in ()).throw(AssertionError('vol tarief gebruikt'))
ai_content.bewaak_budget = lambda limiet: None

app = create_app('development')
app.config['ANTHROPIC_API_KEY'] = 'nep'
with app.app_context():
    from models import AIContent, Category, EprelData, Product, db
    cat = Category(name='Koelkasten', slug='koelkasten')
    db.session.add(cat)
    db.session.flush()

    def maak(ean, eprel, oud=True, leverbaar=True):
        p = Product(ean=ean, title='Miele KFN 4397 CD koelkast', brand='Miele', price=999, bol_url='',
                    category_id=cat.id, slug=f'p-{ean}', is_available=leverbaar, ai_description='Oude tekst.')
        db.session.add(p)
        db.session.flush()
        db.session.add(AIContent(product_id=p.id, content_type='beschrijving', content='Oude tekst.',
                                 generated_at=datetime(2026, 7, 27) if oud else datetime(2026, 10, 14)))
        if eprel:
            db.session.add(EprelData(product_id=p.id, gevonden=True, gezocht=True, gezocht_op='KFN 4397 CD',
                                     modelnummer='KFN 4397 CD', productgroep='refrigeratingappliances2019',
                                     gegevens={'energyClass': 'C', 'noise': 35}))
        return p.id

    a = maak('1', eprel=True)
    b = maak('2', eprel=False)
    c = maak('3', eprel=True, oud=False)
    d = maak('4', eprel=True, leverbaar=False)
    db.session.commit()

    tb._draai_ronde(app)
    check('één batch ingeleverd met alleen het oude EPREL-product', ingeleverd == [[a]], ingeleverd)
    check('administratierij bestaat', AIContent.query.filter_by(content_type='herzien-batch').count() == 1)
    check('volle-tariefherziening staat stil zolang de batch loopt', tb._proefteksten_om_te_herzien(50) == [])

    tb._draai_ronde(app)
    check('batch nog bezig: niets opnieuw ingeleverd', len(ingeleverd) == 1, ingeleverd)

    klaar['klaar'] = True
    tb._draai_ronde(app)
    check('tekst verwerkt en zichtbaar', Product.query.get(a).ai_description.startswith('Batchtekst'))
    check('precies één tekstrij', AIContent.query.filter_by(product_id=a, content_type='beschrijving').count() == 1)
    check('kosten op halftarief geboekt',
          abs(AIContent.query.filter_by(product_id=a, content_type='beschrijving').first().cost - 0.007) < 1e-9)
    check('administratierij weg', AIContent.query.filter_by(content_type='herzien-batch').count() == 0)
    check('andere producten ongemoeid', all(Product.query.get(i).ai_description == 'Oude tekst.' for i in (b, c, d)))

    tb._draai_ronde(app)
    check('daarna geen nieuwe batch meer', len(ingeleverd) == 1, ingeleverd)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
