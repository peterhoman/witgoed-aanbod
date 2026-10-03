"""Adresopschoning (filter_helpers.schoon_adres) en de doorverwijzing van
oude adressen. Adressen zijn letterlijk van de live site (3 oktober 2026).

Draaien: python test_adresopschoning.py
"""
import sys
sys.path.insert(0, '.')

from filter_helpers import product_slug, schoon_adres, schone_productlinks

fouten = 0
def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)

GEVALLEN = [
    # groep A: wordt opgeschoond
    ("de'longhi-dinamica-ecam350.15.b-8004399331143", "delonghi-dinamica-ecam350.15.b-8004399331143"),
    ("aeg-lr7386ud4---wasmachine-8-kg-1600-rpm-76-db-(8--7333394151854", "aeg-lr7386ud4---wasmachine-8-kg-1600-rpm-76-db-8--7333394151854"),
    ("aeg-lr9604c6-absolutecare-+-aeg-tr969bc6-absolutec-6151127583571", "aeg-lr9604c6-absolutecare-plus-aeg-tr969bc6-absolutec-6151127583571"),
    ("jura-z10-obsidian-black-(ec)-7610917158362", "jura-z10-obsidian-black-ec-7610917158362"),
    ("aeg-tr968v4c-9000x-absolutecare®-pro---warmtepomp--7333394100777", "aeg-tr968v4c-9000x-absolutecare-pro---warmtepomp--7333394100777"),
    ("bosch-sms2htw02e-speedperfect+-vaatwasser---vrijst-4242005437351", "bosch-sms2htw02e-speedperfectplus-vaatwasser---vrijst-4242005437351"),
    ("tristar-dubbele-airfryer-fr-9429---2x-4,5-liter----8711387998430", "tristar-dubbele-airfryer-fr-9429---2x-45-liter----8711387998430"),
    ("3-x-nivea-men-–-gezichtscrème-–-sensitive,-gevoeli-4006000161426", "3-x-nivea-men--gezichtscreme--sensitive-gevoeli-4006000161426"),
    ("whirlpool-|-w7ihp40lc-|-inbouw-vaatwasser-|-bestek-8003437639371", "whirlpool--w7ihp40lc--inbouw-vaatwasser--bestek-8003437639371"),
    # groep B en C: blijven precies zo
    ("lg-rt90x8---warmtepompdroger-9kg-62-db-energielabe-8806096198186", "lg-rt90x8---warmtepompdroger-9kg-62-db-energielabe-8806096198186"),
    ("ok.-owm-8126---wasmachine-voorlader-8-kg-1400-rpm--4049011197251", "ok.-owm-8126---wasmachine-voorlader-8-kg-1400-rpm--4049011197251"),
    ("smeg-egf03creu-creme-8017709329839", "smeg-egf03creu-creme-8017709329839"),
]
for oud, verwacht in GEVALLEN:
    uit = schoon_adres(oud)
    check(f'{oud[:48]}', uit == verwacht, uit)
    check('   twee keer = één keer', schoon_adres(uit) == uit)
    check('   EAN achteraan blijft', uit.rsplit('-', 1)[1] == oud.rsplit('-', 1)[1])

# De titel wordt eerst op 50 tekens afgekapt, daarna opgeschoond.
check('product_slug bouwt een schoon adres',
      product_slug("De'Longhi Magnifica S (ECAM 22.110.B) + melkopschuimer", '8004399325067')
      == 'delonghi-magnifica-s-ecam-22.110.b-plus-melkopschu-8004399325067',
      product_slug("De'Longhi Magnifica S (ECAM 22.110.B) + melkopschuimer", '8004399325067'))
check('product_slug laat een schone titel met rust',
      product_slug('LG RT90X8 - Warmtepompdroger 9kg', '8806096198186') == 'lg-rt90x8---warmtepompdroger-9kg-8806096198186')
check('procentteken blijft een streepje (oude reparatie)', '%' not in product_slug('A -20% PFAS-vrij', '1'))

html = ('<a href="/product/ok.-owm-6146-d-wasmachine-(6-kg-1000-rpm-d)-4049011190580">x</a> '
        '<a href="/product/de%27longhi-ecam-1">y</a> <a href="/gidsen/iets-(anders)">z</a>')
uit = schone_productlinks(html)
check('gidslinks naar het schone adres',
      'href="/product/ok.-owm-6146-d-wasmachine-6-kg-1000-rpm-d-4049011190580"' in uit
      and 'href="/product/delonghi-ecam-1"' in uit and 'href="/gidsen/iets-(anders)"' in uit, uit)

# De uurroutine en de doorverwijzing, tegen de lokale demodatabase.
# Let op: pas_toe() zet ook aanbiedingen die drie dagen niet ververst zijn op
# niet-leverbaar, en lokale voorbeelddata is altijd oud. Daarom eerst alle
# aanbiedingen vers maken; anders is de proefdatabase na deze test leeg
# (gebeurd op 3 oktober 2026).
from app import create_app
from models import db, Offer, Product, utcnow
from catalogus_uitzonderingen import pas_toe
import indexnow
gemeld = []
indexnow._post = lambda body: (gemeld.append(body) or 200)
app = create_app()
c = app.test_client()
with app.app_context():
    for o in Offer.query.all():
        o.last_synced = utcnow()
    p = Product.query.filter(Product.is_available == True).first()
    pid, oud_slug, oud_ean = p.id, p.slug, p.ean
    # De doorverwijzing werkt op een EAN van cijfers; de voorbeelddata heeft
    # "EXAMPLE..."-codes. Tijdelijk een echte vorm geven.
    p.ean = '9990000000017'
    vies = "test's-(proef)-+-ding-" + p.ean
    schoon = 'tests-proef-plus-ding-9990000000017'
    p.slug = vies
    db.session.commit()
    try:
        uitkomst = pas_toe(app)
        p = db.session.get(Product, pid)
        db.session.refresh(p)
        check('uurroutine schoont het adres op',
              p.slug == schoon and uitkomst['webadres_opgeschoond'] >= 1, p.slug)
        adressen = gemeld[0]['urlList'] if gemeld else []
        check('Bing krijgt oud en nieuw adres',
              any(u.endswith('/product/' + schoon) for u in adressen)
              and any('proef' in u and not u.endswith('/product/' + schoon) for u in adressen))
        r = c.get('/product/' + vies)
        check('oud adres: 301 in één stap naar het nieuwe',
              r.status_code == 301 and r.headers['Location'].endswith('/product/' + schoon),
              r.headers.get('Location', ''))
        r = c.get('/product/' + schoon)
        pagina = r.get_data(as_text=True)
        check('nieuw adres: 200', r.status_code == 200)
        check('canonical = nieuwe adres',
              ('/product/' + schoon + '"') in pagina.split('rel="canonical" href="')[1][:200])
        check('tweede ronde verandert niets meer', pas_toe(app)['webadres_opgeschoond'] == 0)
        check('proefdatabase nog leverbaar na de routine',
              Product.query.filter_by(is_available=True).count() > 0)
    finally:
        p = db.session.get(Product, pid)
        p.slug, p.ean = oud_slug, oud_ean
        db.session.commit()

print(f"\n{fouten} fout")
sys.exit(1 if fouten else 0)
