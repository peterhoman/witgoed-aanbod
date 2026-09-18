# Proef in een geheugen-database: slaat de gezondheidscontrole aan waar het moet, en alleen daar?
import sys, os
sys.path.insert(0, os.getcwd())
from datetime import datetime, timedelta, timezone
from flask import Flask
from models import db, Product, Offer, Category, utcnow
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

    g, m, cij = gezondheid.rapport(db, Offer, Product, goede_jobs(), True)
    check('alles vers: GEZOND', g, str(m))
    check('tekst begint met GEZOND', gezondheid.als_tekst(g, m, cij).startswith('GEZOND'))

    # EP-situatie van vandaag: 14% oud mag GEEN alarm geven
    ep = Offer.query.filter_by(retailer='ep').limit(8).all()      # 8 van 60 = 13%
    for o in ep: o.last_synced = nu - timedelta(hours=60)
    db.session.commit()
    g, m, _ = gezondheid.rapport(db, Offer, Product, goede_jobs(), True)
    check('EP met 13% oude aanbiedingen (bekend): nog steeds GEZOND', g, str(m))

    # halve feed: 40% oud, laatste sync wel vers
    for o in Offer.query.filter_by(retailer='mediamarkt').limit(24).all(): o.last_synced = nu - timedelta(hours=50)
    db.session.commit()
    g, m, _ = gezondheid.rapport(db, Offer, Product, goede_jobs(), True)
    check('MediaMarkt levert maar een deel: STORING met uitleg', (not g) and any('mediamarkt' in x and 'deel' in x for x in m), str(m))
    for o in Offer.query.filter_by(retailer='mediamarkt').all(): o.last_synced = nu - timedelta(hours=5)
    db.session.commit()

    # hele feed stil
    for o in Offer.query.filter_by(retailer='coolblue').all(): o.last_synced = nu - timedelta(hours=31)
    db.session.commit()
    g, m, cij = gezondheid.rapport(db, Offer, Product, goede_jobs(), True)
    check('Coolblue 31 uur stil: STORING', (not g) and any(x.startswith('coolblue') and 'niet ververst' in x for x in m), str(m))
    check('precies één melding (geen dubbele over dezelfde winkel)', len(m) == 1, str(m))
    check('tekst begint met STORING en bevat GEEN woord GEZOND', gezondheid.als_tekst(g, m, cij).startswith('STORING') and 'GEZOND' not in gezondheid.als_tekst(g, m, cij))
    for o in Offer.query.filter_by(retailer='coolblue').all(): o.last_synced = nu - timedelta(hours=29)
    db.session.commit()
    g, m, _ = gezondheid.rapport(db, Offer, Product, goede_jobs(), True)
    check('Coolblue 29 uur (één gemiste beurt): nog GEZOND', g, str(m))

    # routines
    g, m, _ = gezondheid.rapport(db, Offer, Product, goede_jobs()[:-1], True)
    check('routine ontbreekt: STORING', (not g) and 'ontbreekt' in m[0], str(m))
    j = goede_jobs(); j[0] = (j[0][0], datetime.now(timezone.utc) - timedelta(hours=5))
    g, m, _ = gezondheid.rapport(db, Offer, Product, j, True)
    check('routine 5 uur over tijd: STORING', (not g) and 'over tijd' in m[0], str(m))
    j = goede_jobs(); j[0] = (j[0][0], datetime.now(timezone.utc) - timedelta(minutes=30))
    g, m, _ = gezondheid.rapport(db, Offer, Product, j, True)
    check('routine half uur over tijd (loopt gewoon): GEZOND', g, str(m))
    g, m, _ = gezondheid.rapport(db, Offer, Product, [], True)
    check('geen planner: STORING', not g)

    # sleutel en catalogus
    g, m, _ = gezondheid.rapport(db, Offer, Product, goede_jobs(), False)
    check('sleutel weg: STORING', (not g) and 'sleutel' in m[0], str(m))
    gezondheid.MIN_LEVERBARE_PRODUCTEN = 10000
    g, m, _ = gezondheid.rapport(db, Offer, Product, goede_jobs(), True)
    check('te weinig leverbare producten: STORING', (not g) and 'leverbare producten' in m[0], str(m))

    # een kapotte controle mag nooit GEZOND opleveren
    gezondheid.MIN_LEVERBARE_PRODUCTEN = 5
    g, m, _ = gezondheid.rapport(db, None, Product, goede_jobs(), True)
    check('controle die zelf crasht: STORING, geen serverfout', (not g) and 'kon niet draaien' in m[0], str(m))

print('ALLES GOED' if ok else 'ER GAAT IETS FOUT')
sys.exit(0 if ok else 1)
