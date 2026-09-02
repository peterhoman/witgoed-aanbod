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
#
# De tweede regel is er op 2 september bij gekomen. De eerste ving alleen
# robots die zichzelf zo noemen; programma's die met een kale HTTP-bibliotheek
# langskomen (curl, python-requests, Go, Java) noemen zich niet zo en werden
# geteld als bezoeker. Dat is geen theorie: Search Console gaf over 28 dagen
# 18 klikken vanuit Google, terwijl deze teller in zes dagen ruim 1.500
# doorkliks naar winkels meldde.
_BOTS = ('bot', 'crawl', 'spider', 'slurp', 'bingpreview', 'headless',
         'lighthouse', 'pingdom', 'uptime',
         'curl', 'wget', 'python-requests', 'python-urllib', 'httpx',
         'aiohttp', 'go-http-client', 'okhttp', 'java/', 'apache-httpclient',
         'axios', 'node-fetch', 'scrapy', 'libwww-perl', 'guzzle',
         'facebookexternalhit', 'googleother', 'google-read-aloud',
         'google-safety', 'feedfetcher', 'phantomjs', 'puppeteer',
         'playwright', 'selenium', 'dataprovider', 'semrush', 'ahrefs')


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


def tel(soort):
    """Eén telling erbij voor deze soort, buiten een paginaweergave om.

    Gebruikt door de doorklik naar een winkel: dat is een omleiding en geen
    HTML-pagina, dus de teller hieronder ziet hem niet. En juist die telling
    is het cijfer waar het om draait -- hoeveel mensen gaan er daadwerkelijk
    naar een winkel. Vertoningen in Google zijn leuk, doorklikken betaalt.
    """
    try:
        sleutel = (date.today(), soort[:30])
        tellingen = None
        with _slot:
            _buffer[sleutel] = _buffer.get(sleutel, 0) + 1
            if sum(_buffer.values()) >= _DREMPEL:
                tellingen = dict(_buffer)
                _buffer.clear()
        if tellingen:
            _wegschrijven(tellingen)
    except Exception:
        # Een teller mag nooit een doorklik tegenhouden.
        pass


def is_bot(user_agent):
    """Ziet dit verzoek eruit als een robot?"""
    ua = (user_agent or '').lower()
    return any(b in ua for b in _BOTS)


# Bakjes voor de doorklik naar een winkel. De namen blijven onder de dertig
# tekens; dat is de lengte van de kolom.
BRON_ROBOT = 'klik-robot-ua'
BRON_GEEN_SECFETCH = 'klik-geen-secfetch'
BRON_BROWSER = 'klik-browser'
BRON_ANDERS = 'klik-anders'


def bron(headers):
    """Waar komt deze doorklik vandaan: een mens in een browser of een programma?

    Waarom dit bestaat
    ------------------
    De doorklikteller was het cijfer waar deze site op stuurt, en hij bleek
    niet te vertrouwen. Op 2 september stonden er meer doorkliks (134) dan
    productpaginaweergaven (108) op dezelfde dag, terwijl elke winkelknop
    alleen op een productpagina staat. Dat kan bij mensen niet en past
    precies bij een crawler die de pagina leest en daarna alle knoppen erop
    volgt: een weergave, zeven doorkliks.

    Wat er gemeten wordt
    --------------------
    Alleen wat er in de kop van het verzoek zelf staat. Geen IP, geen cookie,
    geen sessie, en de user-agent wordt niet bewaard -- er gaat alleen een
    teller per bakje per dag omhoog, dezelfde afspraak als bij de
    paginaweergaven.

    De Sec-Fetch-koppen zijn hiervoor het sterkste signaal dat er is. Elke
    browser die iemand vandaag gebruikt stuurt ze mee over https; een
    HTTP-bibliotheek stuurt ze niet. Bij een echte klik op een knop staat er
    `Sec-Fetch-Mode: navigate`.
    """
    if is_bot(headers.get('User-Agent')):
        return BRON_ROBOT
    modus = (headers.get('Sec-Fetch-Mode') or '').lower()
    doel = (headers.get('Sec-Fetch-Dest') or '').lower()
    if not modus and not doel:
        # Geen enkele Sec-Fetch-kop. Vrijwel zeker een programma, maar niet
        # met zekerheid: een enkele oude browser stuurt ze niet. Daarom wel
        # tellen, nog niet weigeren -- eerst een week meten hoe groot dit is.
        return BRON_GEEN_SECFETCH
    if modus == 'navigate' and doel in ('', 'document'):
        return BRON_BROWSER
    # Wel Sec-Fetch-koppen, maar geen gewone navigatie: vooruit ophalen
    # (prefetch), of een script op een andere pagina dat het adres opvraagt.
    # Dat is geen mens die op een knop drukt.
    return BRON_ANDERS


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
            if is_bot(request.headers.get('User-Agent')):
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
