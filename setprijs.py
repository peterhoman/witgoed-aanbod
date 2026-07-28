"""Wat een setje kost tegenover dezelfde twee apparaten los.

Waarom dit bestaat
------------------
De categorie Apparaatsets bevat artikelen die twee losse apparaten samen
verkopen, meestal een wasmachine met een bijpassende droger. Winkels noemen dat
graag een "voordeelset", maar of het werkelijk voordeliger is zegt niemand.

Wij kunnen het uitrekenen, want in de meeste gevallen staan die twee apparaten
ook los in onze eigen catalogus. Dan wordt het:

    Deze set kost EUR 1.149. Dezelfde twee apparaten los kosten samen
    EUR 1.207 -- een verschil van EUR 58.

En net zo goed de andere kant op, want dat komt voor:

    ... los is hier EUR 51 goedkoper.

Dat is een uitspraak die geen andere site over die set doet, hij komt volledig
uit eigen gegevens, en hij is elke dag opnieuw waar omdat hij wordt meegerekend.
Precies waarom "Voordeelsets" als categorienaam is afgewezen: uitrekenen mag,
beweren niet.

De regel die boven alles gaat
-----------------------------
Dezelfde als overal in dit project: niets schatten. Kunnen we niet allebei de
apparaten met zekerheid terugvinden, dan vervalt de hele zin. Liever geen
mededeling dan een som die op een gok rust.

Waar het spaak loopt, en dat is met opzet
-----------------------------------------
Het typenummer moet uit de titel te halen zijn. Dat lukt bij "AEG LR86CB86
PowerCare + AEG TR86CBC86 AbsoluteCare", maar niet bij "Miele WQ 1000 WPS Nova
+ Miele TQ 1000 WP Nova" -- Miele schrijft zijn typenummers met spaties, en dan
is er geen los woord meer aan te wijzen. Zulke sets krijgen geen zin.
"""

import re

# Een typenummer in een titel: begint met een paar letters, bevat een cijfer,
# en is lang genoeg om geen gewoon woord te zijn. Bewust strenger dan nodig --
# een verkeerde match levert een verkeerd bedrag op, en dat is erger dan geen
# bedrag.
_TYPENUMMER = re.compile(r'^[a-z]{1,5}[0-9][a-z0-9./-]{2,}$', re.IGNORECASE)
_MIN_LENGTE = 5


def modelcodes_uit_titel(titel):
    """De typenummers van de losse apparaten in een settitel.

    "AEG LR86CB86 PowerCare + AEG TR86CBC86 AbsoluteCare"
        -> ['LR86CB86', 'TR86CBC86']

    Geeft een lege lijst zodra een van de delen geen herkenbaar typenummer
    heeft: een halve set is geen set, en met een enkel apparaat valt niets te
    vergelijken.
    """
    tekst = str(titel or '')
    if ' + ' not in tekst:
        return []
    codes = []
    for deel in tekst.split(' + '):
        gevonden = None
        for woord in deel.replace(',', ' ').split():
            kaal = woord.strip('.,;:()[]')
            if len(kaal) >= _MIN_LENGTE and _TYPENUMMER.match(kaal):
                gevonden = kaal
                break
        if not gevonden:
            return []
        codes.append(gevonden)
    return codes if len(codes) >= 2 else []


_CACHE = {}
_TTL = 15 * 60


def _losse_apparaten():
    """Alle leverbare niet-setjes met hun laagste winkelprijs. 15 min gecached.

    De prijs komt uit de goedkoopste leverbare aanbieding, met terugval op
    products.price -- precies wat Product.lowest_price doet en wat de pagina
    toont. Dat is niet vrijblijvend: de eerste versie las hier het kale
    price-veld terwijl de set met lowest_price werd gerekend. Dan tel je twee
    verschillende maten bij elkaar op en klopt het verschil principieel niet,
    ook al ziet het bedrag er geloofwaardig uit.

    Een keer ophalen en in het geheugen vergelijken, niet per typenummer een
    query: Product.title.ilike('%code%') kan geen index gebruiken, en met 59
    setjes van elk twee of drie codes gebeurde dat ruim honderd keer. Op
    productie liep de meetpagina daardoor na tien minuten nog niet af.
    """
    import time

    from sqlalchemy import func

    from catalogus_uitzonderingen import is_setje
    from models import Offer, Product, db

    nu = time.time()
    hit = _CACHE.get('data')
    if hit and nu - hit[0] < _TTL:
        return hit[1]

    # Laagste leverbare winkelprijs per product, in een enkele query.
    laagste = dict(
        db.session.query(Offer.product_id, func.min(Offer.price))
        .filter(Offer.is_available.is_(True), Offer.price.isnot(None),
                Offer.price > 0)
        .group_by(Offer.product_id).all())

    rijen = (Product.query
             .filter(Product.is_available.is_(True))
             .with_entities(Product.id, Product.slug, Product.title,
                            Product.price)
             .all())
    data = [(r.id, r.slug, (r.title or '').upper(), r.title,
             laagste.get(r.id, r.price))
            for r in rijen if not is_setje(r.title)]
    _CACHE['data'] = (nu, data)
    return data


def _zoek_apparaat(code, uitgezonderd_id):
    """Het losse apparaat met dit typenummer, of None.

    Precies een treffer is de eis. Twee treffers betekent dat de code ook bij
    een ander apparaat past (een variant, of een te korte code), en dan weten
    we niet welk bedrag we optellen.
    """
    naald = code.upper()
    treffers = [r for r in _losse_apparaten()
                if r[0] != uitgezonderd_id and naald in r[2]]
    if len(treffers) != 1:
        return None
    pid, slug, _, titel, prijs = treffers[0]
    return {'id': pid, 'slug': slug, 'title': titel, 'prijs': prijs}


def vergelijk_met_los(product):
    """Wat dit setje kost tegenover de losse apparaten, of None.

    Geeft {'set', 'los_totaal', 'verschil', 'set_goedkoper', 'apparaten'}.
    None zodra er iets niet met zekerheid vast te stellen is.
    """
    if not product.is_available:
        return None
    setprijs = float(product.lowest_price or 0)
    if setprijs <= 0:
        return None

    codes = modelcodes_uit_titel(product.title)
    if not codes:
        return None

    apparaten = []
    for code in codes:
        gevonden = _zoek_apparaat(code, product.id)
        if gevonden is None:
            return None
        prijs = float(gevonden['prijs'] or 0)
        if prijs <= 0:
            return None
        apparaten.append({'product': gevonden, 'code': code, 'prijs': prijs})

    # Zelfde apparaat twee keer gevonden: dan is er iets mis met de codes en
    # klopt de som niet.
    if len({a['product']['id'] for a in apparaten}) != len(apparaten):
        return None

    los_totaal = sum(a['prijs'] for a in apparaten)
    verschil = abs(los_totaal - setprijs)
    return {
        'set': setprijs,
        'los_totaal': los_totaal,
        'verschil': verschil,
        'set_goedkoper': setprijs < los_totaal,
        # Een verschil van een paar tientjes op ruim duizend euro is ruis:
        # prijzen bij verschillende winkels bewegen dagelijks meer dan dat.
        'noemenswaardig': verschil >= 25,
        'apparaten': apparaten,
    }


def _euro(bedrag):
    """1249.0 -> '1.249,00'. Zelfde schrijfwijze als elders op de pagina."""
    return f"{float(bedrag):,.2f}".replace(',', ' ').replace('.', ',').replace(' ', '.')


def setzin(product):
    """De vergelijking als leesbaar blok, of None.

    Geeft {'kop', 'tekst', 'apparaten'} terug. De apparaten gaan mee zodat de
    pagina ernaartoe kan linken: dan kan de lezer het zelf nakijken, en het
    verbindt meteen twee pagina's die anders los van elkaar staan.

    Drie uitkomsten, want alle drie zijn ze informatie:
    - de set is goedkoper
    - los kopen is goedkoper (bij 10 van de 28 gemeten sets het geval)
    - het scheelt vrijwel niets

    Bewust geen woord als "voordeel" of "korting": wij rekenen het uit, de
    winkel doet de belofte.
    """
    uitkomst = vergelijk_met_los(product)
    if uitkomst is None:
        return None

    set_bedrag = _euro(uitkomst['set'])
    los_bedrag = _euro(uitkomst['los_totaal'])
    verschil = _euro(uitkomst['verschil'])
    aantal = len(uitkomst['apparaten'])
    woord = 'twee' if aantal == 2 else 'drie' if aantal == 3 else str(aantal)

    basis = (f"Deze set kost € {set_bedrag}. Dezelfde {woord} apparaten los "
             f"kosten samen € {los_bedrag}")
    if not uitkomst['noemenswaardig']:
        # Een paar tientjes op ruim duizend euro is ruis: prijzen bij
        # verschillende winkels bewegen dagelijks meer dan dat.
        staart = " — vrijwel hetzelfde."
    elif uitkomst['set_goedkoper']:
        staart = f" — als set bent u € {verschil} goedkoper uit."
    else:
        staart = f" — los kopen is hier € {verschil} goedkoper."

    return {
        'kop': 'Wat kost dit los?',
        'tekst': basis + staart,
        'apparaten': [{'slug': a['product']['slug'],
                       'titel': a['product']['title'],
                       'prijs': _euro(a['prijs'])} for a in uitkomst['apparaten']],
        'voet': 'Berekend over de laagste prijs van elk apparaat in onze eigen '
                'vergelijking, op het moment dat u deze pagina opvraagt.',
    }
