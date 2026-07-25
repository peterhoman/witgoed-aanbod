"""Tellen hoeveel pagina's per soort per dag worden opgevraagd.

Waarom dit bestaat: de site heeft geen analytics, en die aanzetten vraagt om
een cookiebanner met toestemming. Voor één vraag is dat te zwaar -- namelijk:
komen bezoekers dieper de site in? Die vraag is te beantwoorden met een kale
teller per paginasoort, zonder iets over de bezoeker vast te leggen.

Geen IP, geen sessie, geen cookie, geen user-agent. Alleen: op datum X zijn
er N productpagina's opgevraagd. Daarmee zie je of de verhouding tussen
categorie- en productpagina's verschuift nadat de kaartknoppen naar de
productpagina zijn gaan wijzen.

De tellingen worden gebufferd in het geheugen en periodiek weggeschreven, zodat
een paginaweergave geen extra databaseschrijfactie kost.
"""
import threading
from datetime import date

# Buffer: {(datum, soort): aantal}. Wordt leeggeschreven zodra hij groot
# genoeg is; een slot omdat gunicorn met meerdere threads draait.
_buffer = {}
_slot = threading.Lock()
_DREMPEL = 25

# Bots tellen niet mee: die bezoeken alles en zeggen niets over of een mens
# dieper de site in komt.
_BOTS = ('bot', 'crawl', 'spider', 'slurp', 'bingpreview', 'headless',
         'lighthouse', 'pingdom', 'uptime')


def _soort(pad):
    """URL-pad -> paginasoort, of None als we het niet tellen."""
    if pad.startswith('/product/'):
        return 'product'
    if pad.startswith('/category/'):
        # Facetpagina's (merk, energielabel, type) tellen als categorie:
        # het zijn varianten van dezelfde stap in de reis.
        return 'categorie'
    if pad.startswith('/search'):
        return 'zoeken'
    if pad.startswith('/vergelijk'):
        return 'vergelijken'
    if pad.startswith('/gidsen') or pad.startswith('/blog'):
        return 'gidsen'
    if pad == '/':
        return 'home'
    return None


def registreer(app):
    """Hangt de teller achter elke succesvolle paginaweergave."""

    @app.after_request
    def _tel(response):
        try:
            from flask import request
            if request.method != 'GET' or response.status_code != 200:
                return response
            if not (response.content_type or '').startswith('text/html'):
                return response
            ua = (request.headers.get('User-Agent') or '').lower()
            if any(b in ua for b in _BOTS):
                return response
            soort = _soort(request.path)
            if not soort:
                return response

            sleutel = (date.today(), soort)
            tellingen = None
            with _slot:
                _buffer[sleutel] = _buffer.get(sleutel, 0) + 1
                if sum(_buffer.values()) >= _DREMPEL:
                    tellingen = dict(_buffer)
                    _buffer.clear()
            # Buiten het slot wegschrijven: de database mag geen andere
            # verzoeken laten wachten.
            if tellingen:
                _wegschrijven(tellingen)
        except Exception:
            # Een teller mag nooit een pagina stukmaken.
            pass
        return response


def _wegschrijven(tellingen):
    from models import db, PageView
    try:
        for (datum, soort), aantal in tellingen.items():
            rij = PageView.query.filter_by(datum=datum, soort=soort).first()
            if rij:
                rij.aantal += aantal
            else:
                db.session.add(PageView(datum=datum, soort=soort, aantal=aantal))
        db.session.commit()
    except Exception:
        db.session.rollback()


def overzicht(dagen=14):
    """Tellingen per dag en per soort, nieuwste eerst. Voor /api/sync-status."""
    from datetime import timedelta
    from models import PageView

    vanaf = date.today() - timedelta(days=dagen)
    rijen = (PageView.query.filter(PageView.datum >= vanaf)
             .order_by(PageView.datum.desc()).all())

    per_dag = {}
    for r in rijen:
        per_dag.setdefault(str(r.datum), {})[r.soort] = r.aantal

    uit = []
    for datum in sorted(per_dag, reverse=True):
        soorten = per_dag[datum]
        product = soorten.get('product', 0)
        categorie = soorten.get('categorie', 0)
        uit.append({
            'datum': datum,
            **soorten,
            # De kernvraag in één getal: hoeveel productpagina's per
            # categoriepagina. Stijgt dit, dan komen bezoekers dieper.
            'product_per_categorie': round(product / categorie, 2) if categorie else None,
        })
    return uit
