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


def _zoek_apparaat(code, uitgezonderd_id):
    """Het losse apparaat met dit typenummer, of None.

    Precies een treffer is de eis. Twee treffers betekent dat de code ook bij
    een ander apparaat past (een variant, of een te korte code), en dan weten
    we niet welk bedrag we optellen.
    """
    from catalogus_uitzonderingen import is_setje
    from models import Product

    kandidaten = [
        p for p in Product.query.filter(
            Product.is_available.is_(True),
            Product.id != uitgezonderd_id,
            Product.title.ilike(f'%{code}%')).limit(10).all()
        # Een ander setje telt niet mee: dan zou de som twee apparaten
        # bevatten waar er een gevraagd wordt.
        if not is_setje(p.title)
    ]
    return kandidaten[0] if len(kandidaten) == 1 else None


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
        prijs = float(gevonden.lowest_price or 0)
        if prijs <= 0:
            return None
        apparaten.append({'product': gevonden, 'code': code, 'prijs': prijs})

    # Zelfde apparaat twee keer gevonden: dan is er iets mis met de codes en
    # klopt de som niet.
    if len({a['product'].id for a in apparaten}) != len(apparaten):
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
