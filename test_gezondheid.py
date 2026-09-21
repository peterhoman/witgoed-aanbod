# Proef in een geheugen-database: slaat de gezondheidscontrole aan waar het moet, en alleen daar?
# Draaien vanuit de projectmap:  python test_gezondheid.py
import sys, os
sys.path.insert(0, os.getcwd())
from datetime import datetime, timedelta, timezone
from flask import Flask
from models import db, Product, Offer, Category, PriceHistory, utcnow
import gezondheid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db.init_app(app)
ok = True
def check(naam, voorwaarde, extra=''):
    global ok
    print(('GOED ' if voorwaarde else 'FOUT ') + naam + (' -> ' + extra if extra and not voorwaarde else ''))
    ok = ok and voorwaarde

def goede_jobs():
    straks = datetime.now(timezone.utc) + timedelta(hours=3)
    return [(n, straks) for n in gezondheid.VERWACHTE_ROUTINES]

def rapport(jobs=None, sleutel=True, offer=Offer):
    return gezondheid.rapport(db, offer, Product, goede_jobs() if jobs is None else jobs,
                              sleutel, PriceHistory)

def zet_prijsbeweging(winkel, uren_geleden):
    """Laatste prijswijziging van een winkel op precies `uren_geleden` zetten."""
    PriceHistory.query.filter_by(retailer=winkel).delete()
    if uren_geleden is not None:
        db.session.add(PriceHistory(product_id=1, retailer=winkel, price=1,
                                    recorded_at=utcnow() - timedelta(hours=uren_geleden)))
    db.session.commit()

gezondheid.MIN_LEVERBARE_PRODUCTEN = 5      # proefdatabase is klein
with app.app_context():
    db.create_all()
    c = Category(name='T', slug='t'); db.session.add(c); db.session.commit()
    nu = utcnow()
    n = 0
    for winkel in gezondheid.WINKELS:
        for i in range(60):
            n += 1
            p = Product(ean=str(n), title='t', price=1, bol_url='x', slug=str(n), category_id=c.id, is_available=True)
            db.session.add(p); db.session.flush()
            db.session.add(Offer(product_id=p.id, retailer=winkel, price=1, is_available=True,
                                 last_synced=nu - timedelta(hours=5)))
    db.session.commit()
    for winkel in gezondheid.BEWEGENDE_WINKELS:
        zet_prijsbeweging(winkel, 4)

    g, m, cij = rapport()
    check('alles vers: GEZOND', g, str(m))
    check('tekst begint met GEZOND', gezondheid.als_tekst(g, m, cij).startswith('GEZOND'))
    check('tekst toont de laatste prijswijziging per grote winkel',
          all((w + ': laatste prijswijziging') in gezondheid.als_tekst(g, m, cij) for w in gezondheid.BEWEGENDE_WINKELS))

    # EP-situatie van 18 sept: 13% oud mag GEEN alarm geven
    for o in Offer.query.filter_by(retailer='ep').limit(8).all(): o.last_synced = nu - timedelta(hours=60)
    db.session.commit()
    g, m, _ = rapport()
    check('EP met 13% oude aanbiedingen (bekend): nog steeds GEZOND', g, str(m))

    # halve feed: 40% oud, laatste sync wel vers
    for o in Offer.query.filter_by(retailer='mediamarkt').limit(24).all(): o.last_synced = nu - timedelta(hours=50)
    db.session.commit()
    g, m, _ = rapport()
    check('MediaMarkt levert maar een deel: STORING met uitleg', (not g) and any('mediamarkt' in x and 'deel' in x for x in m), str(m))
    for o in Offer.query.filter_by(retailer='mediamarkt').all(): o.last_synced = nu - timedelta(hours=5)
    db.session.commit()

    # hele feed stil
    for o in Offer.query.filter_by(retailer='coolblue').all(): o.last_synced = nu - timedelta(hours=31)
    db.session.commit()
    g, m, cij = rapport()
    check('Coolblue 31 uur stil: STORING', (not g) and any(x.startswith('coolblue') and 'niet ververst' in x for x in m), str(m))
    check('precies één melding (geen dubbele over dezelfde winkel)', len(m) == 1, str(m))
    check('tekst begint met STORING en bevat GEEN woord GEZOND', gezondheid.als_tekst(g, m, cij).startswith('STORING') and 'GEZOND' not in gezondheid.als_tekst(g, m, cij))
    # sync stil EN prijzen stil: nog steeds één melding over Coolblue
    zet_prijsbeweging('coolblue', 70)
    g, m, _ = rapport()
    check('Coolblue sync stil én prijzen stil: toch maar één melding', (not g) and len(m) == 1, str(m))
    for o in Offer.query.filter_by(retailer='coolblue').all(): o.last_synced = nu - timedelta(hours=29)
    db.session.commit()
    zet_prijsbeweging('coolblue', 4)
    g, m, _ = rapport()
    check('Coolblue 29 uur (één gemiste beurt): nog GEZOND', g, str(m))

    # BEVROREN FEED: de sync loopt gewoon, maar er beweegt geen prijs meer
    for o in Offer.query.filter_by(retailer='coolblue').all(): o.last_synced = nu - timedelta(hours=2)
    db.session.commit()
    zet_prijsbeweging('coolblue', 61)
    g, m, _ = rapport()
    check('Coolblue vers gelezen maar 61 uur geen prijswijziging: STORING "bevroren"',
          (not g) and len(m) == 1 and m[0].startswith('coolblue') and 'bevroren' in m[0], str(m))
    zet_prijsbeweging('coolblue', 59)
    g, m, _ = rapport()
    check('Coolblue 59 uur geen prijswijziging: nog GEZOND', g, str(m))
    zet_prijsbeweging('mediamarkt', 37)
    g, m, _ = rapport()
    check('MediaMarkt 37 uur stil (het langste gat dat ooit gemeten is was 36): GEZOND', g, str(m))
    zet_prijsbeweging('mediamarkt', None)
    g, m, _ = rapport()
    check('MediaMarkt zonder enige prijshistorie: STORING', (not g) and 'nog nooit' in m[0], str(m))
    zet_prijsbeweging('mediamarkt', 4)
    zet_prijsbeweging('expert', 200)
    zet_prijsbeweging('alternate', None)
    g, m, _ = rapport()
    check('Expert 200 uur stil en Alternate zonder historie: GEZOND (kleine winkels tellen niet mee)', g, str(m))
    zet_prijsbeweging('coolblue', 4)

    # routines
    g, m, _ = rapport(jobs=goede_jobs()[:-1])
    check('routine ontbreekt: STORING', (not g) and 'ontbreekt' in m[0], str(m))
    j = goede_jobs(); j[0] = (j[0][0], datetime.now(timezone.utc) - timedelta(hours=5))
    g, m, _ = rapport(jobs=j)
    check('routine 5 uur over tijd: STORING', (not g) and 'over tijd' in m[0], str(m))
    j = goede_jobs(); j[0] = (j[0][0], datetime.now(timezone.utc) - timedelta(minutes=30))
    g, m, _ = rapport(jobs=j)
    check('routine half uur over tijd (loopt gewoon): GEZOND', g, str(m))
    g, m, _ = rapport(jobs=[])
    check('geen planner: STORING', not g)

    # sleutel en catalogus
    g, m, _ = rapport(sleutel=False)
    check('sleutel weg: STORING', (not g) and 'sleutel' in m[0], str(m))
    gezondheid.MIN_LEVERBARE_PRODUCTEN = 10000
    g, m, _ = rapport()
    check('te weinig leverbare producten: STORING', (not g) and 'leverbare producten' in m[0], str(m))

    # een kapotte controle mag nooit GEZOND opleveren
    gezondheid.MIN_LEVERBARE_PRODUCTEN = 5
    g, m, _ = rapport(offer=None)
    check('controle die zelf crasht: STORING, geen serverfout', (not g) and 'kon niet draaien' in m[0], str(m))
    g, m, _ = gezondheid.rapport(db, Offer, Product, goede_jobs(), True, None)
    check('prijsbeweging zonder prijshistorie-model: STORING, nooit stil overgeslagen',
          (not g) and any('prijsbeweging' in x for x in m), str(m))

print('ALLES GOED' if ok else 'ER GAAT IETS FOUT')
sys.exit(0 if ok else 1)
