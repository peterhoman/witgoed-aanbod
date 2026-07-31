"""Ordening van de productspecificaties op de detailpagina.

De feeds leveren tot 77 velden per apparaat, in de volgorde waarin de winkel
ze aanlevert. De eerste acht daarvan zijn willekeurig: bij magnetrons begint
de lijst met "Kleur" en "Fabrieksgarantie termijn", terwijl iemand die kiest
het vermogen wil zien.

Dit bestand doet twee dingen:

1. `kernspecs` kiest per categorie welke acht velden bovenaan staan.
2. `groepeer_specs` verdeelt de rest over benoemde blokken, zodat uitklappen
   iets bruikbaars oplevert in plaats van een muur van 77 regels.

Beide zijn configuratie, geen logica: staat een veld er niet in de data, dan
wordt het overgeslagen. Er wordt niets geschat of ingevuld.
"""
import re


# Per categorie de acht velden die bovenaan staan, in deze volgorde. Namen
# zijn de letterlijke spec-keys uit de feeds (geverifieerd via
# /api/category-specs/<slug>). 'AFMETINGEN' is geen feedveld maar de
# samengestelde regel h x b x d, zie _afmetingen().
AFMETINGEN = 'AFMETINGEN'

KERNVELDEN = {
    'wasmachines': [
        'Laadvermogen wasmachine',
        'Waarde energielabel',
        'Toerental centrifuge',
        'Energieverbruik per 100 cycli',
        'Geluidsniveau centrifuge',
        'Waterverbruik per cyclus',
        AFMETINGEN,
        "Aantal wasprogramma's",
    ],
    'drogers': [
        'Laadvermogen wasdroger',
        'Waarde energielabel',
        'Type droger',
        'Energieverbruik per 100 cycli',
        'Geluidsniveau drogen',
        'Type condensafvoer',
        'Vochtigheid sensor',
        AFMETINGEN,
    ],
    'wasdroogcombinaties': [
        'Laadvermogen wasmachine',
        'Waarde energielabel',
        'Toerental centrifuge',
        'Energieverbruik per 100 cycli',
        'Geluidsniveau centrifuge',
        'Waterverbruik per cyclus',
        AFMETINGEN,
        "Aantal wasprogramma's",
    ],
    'koelkasten': [
        'Volume in liters',
        'Waarde energielabel',
        'Volume koelruimte',
        'Jaarlijks energieverbruik in kWh',
        'Geluidsniveau',
        AFMETINGEN,
        'Product gewicht',
        'Fabrieksgarantie termijn',
    ],
    'vaatwassers': [
        'Aantal couverts',
        'Waarde energielabel',
        'Geluidsniveau',
        'Duur wascyclus op standaard programma',
        'Type waterbeveiliging',
        'Overstromingsbeveiliging',
        AFMETINGEN,
        'Fabrieksgarantie termijn',
    ],
    'ovens': [
        'Volume in liters',
        'Waarde energielabel',
        'Maximale temperatuur',
        'Bediening',
        AFMETINGEN,
        'Materiaal behuizing',
        'Product gewicht',
        'Fabrieksgarantie termijn',
    ],
    'magnetrons': [
        'Magnetronvermogen',
        'Ovenvermogen',
        'Grill functie',
        'Hete lucht functionaliteit',
        'Ontdooi functionaliteit',
        AFMETINGEN,
        'Bediening',
        'Fabrieksgarantie termijn',
    ],
    'koffiemachines': [
        'Soort koffie',
        'Type melkopschuimer',
        'Vermogen',
        'Aantal kopjes per keer',
        'Afneembare waterreservoir',
        'Waterfilter',
        AFMETINGEN,
        'Fabrieksgarantie termijn',
    ],
    'stofzuigers': [
        'Vermogen',
        'Airwatts',
        'Geluidsniveau',
        'Stofzuigerzak of zonder stofzak',
        'Capaciteit verzamel reservoir',
        'Hepa luchtfilter',
        'Gewicht stofzuiger',
        'Fabrieksgarantie termijn',
    ],
    'fornuizen': [
        'Aantal kookzones',
        'Aantal ovens',
        'Inhoud',
        'Maximale temperatuur',
        'Aansluiting op aantal fasen',
        'Aansluitwaarde',
        AFMETINGEN,
        'Bediening',
    ],
    'kookplaten': [
        'Aantal kookzones',
        'Vermogen per kookzone',
        'Aansluiting op aantal fasen',
        'Type bedieningsknoppen',
        AFMETINGEN,
        'Snoerlengte',
        'Materiaal behuizing',
        'Fabrieksgarantie termijn',
    ],
    'afzuigkappen': [
        'Type afzuigkap',
        'Zuigvermogen',
        'Aantal motoren',
        'Geschikt voor luchtafvoer',
        'Geschikt voor recirculatie',
        AFMETINGEN,
        'Materiaal behuizing',
        'Fabrieksgarantie termijn',
    ],
}

# Het veld dat per categorie "formaat" betekent: vulgewicht, inhoud, couverts.
# Stond eerst als _FORMAAT_VELD in routes/products.py, maar wordt inmiddels op
# twee plaatsen gebruikt (vergelijkbare alternatieven en de categoriecontext) en
# is net als de lijsten hierboven configuratie, geen logica. Staat een categorie
# er niet in, dan vervalt het onderdeel dat het veld nodig heeft.
FORMAAT_VELD = {
    'wasmachines': 'Laadvermogen wasmachine',
    'wasdroogcombinaties': 'Laadvermogen wasmachine',
    'drogers': 'Laadvermogen wasdroger',
    'koelkasten': 'Volume in liters',
    'vaatwassers': 'Aantal couverts',
    'ovens': 'Volume in liters',
    'magnetrons': 'Ovenvermogen',
}

# Blokken voor de uitgeklapte lijst, in weergavevolgorde. Een veld valt in
# het eerste blok waarvan een trefwoord in de veldnaam voorkomt; wat nergens
# past belandt in Overig.
SPEC_GROEPEN = (
    # Volgorde telt: een veld valt in het eerste blok dat matcht. Identificatie
    # en garantie staan vooraan omdat hun woorden ook elders voorkomen.
    # Geen 'ean' als trefwoord: dat zit ook in "cleansing", waardoor "Maximum
    # cleansing temperatuur" hier belandde in plaats van bij Prestaties.
    ('Merk en model', ('merk', 'model', 'mpn', 'fabrikant', 'markering')),
    ('Garantie en service', ('garantie', 'reparatie', 'reserveonderdelen',
                             'ondersteuning', 'updates')),
    ('Slim en verbonden', ('app', 'internet', 'wifi', 'bluetooth', 'smart', 'slim',
                           'gebruikersgegevens', 'data', 'compatibel', 'mobiele',
                           'diensten', 'besturingssyteem', 'besturingssysteem')),
    ('Verbruik en kosten', ('energie', 'kwh', 'verbruik', 'water', 'label', 'stroom')),
    ('Prestaties', ('toerental', 'vermogen', 'capaciteit', 'laadvermogen', 'couverts',
                    'volume', 'geluid', 'temperatuur', 'sensor', 'droogklasse',
                    'resultaat', 'centrifuge', 'balans', 'motor', 'professioneel',
                    'load', 'cleansing',
                    # koffie, stofzuigen, koken: zonder deze woorden viel het
                    # halve assortiment buiten wasmachines in Overig
                    'koffie', 'bonen', 'maal', 'melk', 'kopje', 'espresso',
                    'zuig', 'stofzak', 'airwatts', 'kookzone', 'druk', 'bar',
                    'reservoir', 'inhoud', 'watt')),
    ('Afmetingen en installatie', ('hoogte', 'breedte', 'lengte', 'diepte', 'gewicht',
                                   'afmeting', 'verpakking', 'inbouw', 'snoer', 'deur',
                                   'scharnier', 'installatie', 'materiaal', 'kleur',
                                   'tuimelaar')),
    ("Programma's en functies", ('programma', 'functie', 'display', 'kinderslot',
                                 'indicat', 'timer', 'uitstel', 'automat', 'stoom',
                                 'grill', 'ontdooi', 'bediening', 'alarm', 'signaal',
                                 'verlichting', 'lade', 'kreuk', 'toevoegen',
                                 'meegeleverd', 'taal', 'beurt')),
)
OVERIG = 'Overig'


# Een nul met een eenheid is bij deze grootheden geen meting maar een leeg
# veld: een koffiemachine van 0 dB bestaat niet. Bewust beperkt tot de
# eenheden waar dat zeker is -- bij bijvoorbeeld "0 programma's" of
# "0 bonenreservoirs" kan nul wél kloppen.
_NULWAARDE = re.compile(r'^0(?:[.,]0+)?\s*(?:db|kwh|kw|l|liter|lt)?$', re.I)


def _is_lege_waarde(waarde):
    """True als deze spec-waarde niets zegt (leeg, streepje, of nul met eenheid)."""
    tekst = str(waarde or '').strip()
    if not tekst or tekst in ('-', '--', 'n.v.t.', 'nvt'):
        return True
    return bool(_NULWAARDE.match(tekst))


def _afmetingen(specs):
    """'Product hoogte' + breedte + lengte -> één regel 'h x b x d'.

    De feeds leveren de drie maten los; op de pagina is één regel bruikbaarder
    dan drie. Ontbreekt er een, dan tonen we de maten die er wel zijn.
    """
    delen = [specs.get(k) for k in ('Product hoogte', 'Product breedte', 'Product lengte')]
    delen = [str(d).strip() for d in delen if d]
    return ' × '.join(delen) if delen else None


def _kies_kernspecs(product, aantal=8):
    """(zichtbare rijen, gebruikte spec-sleutels).

    De tweede waarde heeft groepeer_specs nodig: die velden staan al bovenaan
    en horen niet nog eens in de uitgeklapte lijst te verschijnen.
    """
    specs = product.specs or {}
    if not specs:
        return [], set()

    slug = product.category.slug if product.category else ''
    gekozen, gebruikt = [], set()

    for veld in KERNVELDEN.get(slug, []):
        if veld == AFMETINGEN:
            waarde = _afmetingen(specs)
            if waarde:
                gekozen.append(('Afmetingen (h × b × d)', waarde))
                gebruikt.update(('Product hoogte', 'Product breedte', 'Product lengte'))
        elif specs.get(veld) and not _is_lege_waarde(specs[veld]):
            gekozen.append((veld, specs[veld]))
            gebruikt.add(veld)
        if len(gekozen) >= aantal:
            break

    for sleutel, waarde in specs.items():
        if len(gekozen) >= aantal:
            break
        if sleutel not in gebruikt and not _is_lege_waarde(waarde):
            gekozen.append((sleutel, waarde))
            gebruikt.add(sleutel)

    return gekozen[:aantal], gebruikt


def kernspecs(product, aantal=8):
    """De belangrijkste specs van dit apparaat, als lijst van (label, waarde).

    Staat de categorie niet in KERNVELDEN, of levert de lijst te weinig op,
    dan vullen we aan met de eerste velden uit de feed — beter iets in de
    volgorde van de winkel dan een half blok.
    """
    return _kies_kernspecs(product, aantal)[0]


def groepeer_specs(product):
    """De overige specs, verdeeld over benoemde blokken.

    "Overige": de velden die bovenaan al als kernspec staan, worden hier
    overgeslagen. Anders staat elk van die acht twee keer op de pagina --
    één keer bovenaan en nog eens in zijn groep. Bij een koffiemachine met
    een lijst van 27 koffiesoorten leest dat als een fout.

    Geeft een lijst van (groepsnaam, [(label, waarde), ...]); lege groepen
    vallen weg en Overig staat altijd onderaan.
    """
    specs = product.specs or {}
    if not specs:
        return []

    _, al_getoond = _kies_kernspecs(product)

    per_groep = {naam: [] for naam, _ in SPEC_GROEPEN}
    per_groep[OVERIG] = []

    for sleutel, waarde in specs.items():
        if sleutel in al_getoond or _is_lege_waarde(waarde):
            continue
        laag = sleutel.lower()
        doel = next((naam for naam, trefwoorden in SPEC_GROEPEN
                     if any(tw in laag for tw in trefwoorden)), OVERIG)
        per_groep[doel].append((sleutel, waarde))

    volgorde = [naam for naam, _ in SPEC_GROEPEN] + [OVERIG]
    return [(naam, per_groep[naam]) for naam in volgorde if per_groep[naam]]


# Een typenummer in een titel: een paar letters, een cijfer, en lang genoeg om
# geen gewoon woord te zijn. Zelfde patroon als setprijs.py en eprel.py --
# bewust strenger dan nodig, want een verkeerd modelnummer in de paginatitel
# is erger dan geen modelnummer.
_TITEL_TYPENUMMER = re.compile(r'^[a-z]{1,5}[0-9][a-z0-9./-]{2,}$', re.IGNORECASE)
_TITEL_MIN_LENGTE = 5

_LEEG = ('niet van toepassing', 'nvt', 'n.v.t.', '-')

# Ruimte voor het productdeel van de paginatitel. Google toont ongeveer 60
# tekens; " | WitgoedAanbod.nl" kost er 19.
_TITEL_MAX = 45

# Eigen "nog niet uitgezocht"-waarde, want None is hier een geldige uitkomst
# (dit apparaat heeft geen herkenbaar modelnummer) en zou anders elke keer
# opnieuw worden opgezocht.
_NIET_BEPAALD = object()


def zoektitel(product):
    """De titel voor het browsertabblad en het zoekresultaat.

    Hier stond `product.title`, de kale feedtitel. Die is bij deze winkels
    lang -- "LG Gbbsj10dpy - Koel-vriescombinatie Breedte 59.7 Cm Hoogte 186
    Inhoud 375 L Nofrost Prime Silver", 96 tekens -- en Google toont er
    ongeveer 60. De rest wordt afgekapt, vaak midden in een maat.

    Wat mensen intikken is het typenummer: van de zoekopdrachten die deze
    site in drie maanden bereikten was vrijwel alles een modelcode
    ("gsn36vicg", "lg gbbsj10dpy", "smv4emx01n"). Die hoort dus vooraan te
    staan, in de schrijfwijze waarin hij gezocht wordt.

    Zonder herkenbaar typenummer valt hij terug op de feedtitel, afgekapt op
    een woordgrens -- korter en heel, in plaats van lang en halverwege
    afgesneden.
    """
    merk = (product.brand or '').strip()
    model = modelnummer(product)
    if merk and model:
        # Merk niet twee keer: "LG LG GBBSJ10DPY" bij feeds die het merk in
        # het Model-veld herhalen.
        if model.upper().startswith(merk.upper()):
            return model
        return f"{merk} {model}"

    titel = (product.title or '').strip()
    if len(titel) <= _TITEL_MAX:
        return titel
    return titel[:_TITEL_MAX].rsplit(' ', 1)[0].rstrip(' -–—,;:/|') + '…'


def _model_uit_titel(product):
    """Het typenummer uit de producttitel, of None.

    Feedtitels van deze winkels beginnen met merk en type: "LG Gbbsj10dpy -
    Koel-vriescombinatie Breedte 59.7 Cm ...". Het eerste woord dat aan het
    patroon voldoet is dat typenummer.

    Niet bij setjes: "AEG LR86CB86 + AEG TR86CBC86" bevat er twee, en dan is
    er geen goede keuze. Die houden hun volledige titel.
    """
    from catalogus_uitzonderingen import is_setje

    titel = (product.title or '').strip()
    if not titel or is_setje(titel):
        return None
    for woord in re.split(r'[\s,]+', titel):
        kaal = woord.strip('.,;:()[]/')
        if len(kaal) >= _TITEL_MIN_LENGTE and _TITEL_TYPENUMMER.match(kaal):
            # Feeds schrijven typenummers in wisselende schrijfwijze
            # ("Gbbsj10dpy"). Fabrikanten en zoekers gebruiken hoofdletters;
            # zo ziet iemand die op "lg gbbsj10dpy" zoekt zijn eigen
            # zoekterm terug in het resultaat.
            return kaal.upper()
    return None


def modelnummer(product):
    """Het modelnummer van dit apparaat, of None.

    Drie bronnen, in volgorde van betrouwbaarheid:

    1. het Model-veld uit de feed;
    2. wat EPREL teruggaf -- de opgave van de fabrikant zelf bij de Europese
       Commissie, dus betrouwbaarder dan wat een winkel ervan maakt;
    3. het typenummer uit de titel.

    MPN blijft er bewust buiten: dat levert bij sommige merken interne codes
    op ("914 913 271") die geen koper herkent.

    Waarom bron 2 en 3 erbij zijn gekomen: het Model-veld is bij 74% van de
    catalogus leeg, en zonder modelnummer valt de meta-description terug op de
    volledige feedtitel. Gemeten op 31-07: de LG GBBSJ10DPY kreeg 44
    vertoningen in Google en nul klikken, met een titel van 116 tekens die
    halverwege werd afgekapt en een omschrijving die alleen die titel
    herhaalde. Dezelfde pagina van een Siemens mét Model-veld toonde
    "Goedkoper dan 53 van de 227 andere vaatwassers die wij volgen" -- een
    reden om te klikken.
    """
    # Onthouden op het object zelf: de productpagina vraagt dit drie keer
    # (paginatitel, meta-description, en het zichtbare veld), en bron 2 is
    # een databasevraag. Eén keer per verzoek volstaat.
    onthouden = getattr(product, '_modelnummer_cache', _NIET_BEPAALD)
    if onthouden is not _NIET_BEPAALD:
        return onthouden

    specs = product.specs or {}
    waarde = (specs.get('Model') or '').strip()
    if waarde and waarde.lower() not in _LEEG:
        uitkomst = waarde
    else:
        uitkomst = None
        try:
            from models import EprelData
            rij = EprelData.query.filter_by(product_id=product.id,
                                            gevonden=True).first()
            if rij and (rij.modelnummer or '').strip():
                uitkomst = rij.modelnummer.strip()
        except Exception:
            # Geen app-context of geen tabel: dan gewoon door naar de titel.
            pass
        if uitkomst is None:
            uitkomst = _model_uit_titel(product)

    product._modelnummer_cache = uitkomst
    return uitkomst
