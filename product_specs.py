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


# Kenmerken die kort genoeg zijn voor een productkaart, met de eenheid die
# erbij hoort. Alleen deze velden komen op een kaart: de rest van de
# specificaties is te lang of te technisch voor een vak van ruim 160 pixels.
# De sleutels zijn dezelfde letterlijke feedvelden als in KERNVELDEN.
KAART_VELDEN = {
    'Laadvermogen wasmachine': 'kg',
    'Laadvermogen wasdroger': 'kg',
    'Toerental centrifuge': 'tpm',
    'Volume in liters': 'liter',
    'Volume koelruimte': 'liter',
    'Aantal couverts': 'couverts',
    'Waarde energielabel': '',
    'Ovenvermogen': 'W',
}

# Een waarde die langer is dan dit past niet op een kaart naast twee andere.
_KAART_MAX_TEKENS = 12


def kaart_tags(product, aantal=3):
    """Twee of drie korte kenmerken voor op een productkaart, of niets.

    Waarom dit bestaat: op een kaart stond alleen de titel uit de feed, en
    die is vaak tachtig tekens lang ("OK. Owm 8136 A-10 Wasmachine
    Voorlader (8 Kg 1400 Rpm A)"). Wie op een telefoon door een categorie
    scrolt leest dat niet. Drie blokjes -- 8 kg, 1400 tpm, A -- zijn in een
    oogopslag te vergelijken, en de gegevens hebben we al staan.

    Twee grenzen die bewust streng zijn:

    - Alleen velden uit KAART_VELDEN. De feed levert ook "Vermogen per
      kookzone: zone linksvoor en rechtsachter"; zulke waarden horen niet
      als blokje op een kaart.
    - Minder dan twee bruikbare kenmerken levert niets op. Eén los blokje
      ziet eruit als een fout, en de helft van de catalogus heeft helemaal
      geen specificaties (gemeten 2 september 2026: 48% van de
      productpagina's heeft een specificatieblok).

    Leest alleen product.specs en product.category, allebei al geladen --
    geen extra databasevraag per kaart. Dat is hier eerder misgegaan.
    """
    specs = product.specs or {}
    if not specs:
        return []

    slug = product.category.slug if product.category else ''
    tags = []
    for veld in KERNVELDEN.get(slug, []):
        if len(tags) >= aantal:
            break
        if veld not in KAART_VELDEN:
            continue
        waarde = specs.get(veld)
        if not waarde or _is_lege_waarde(waarde):
            continue
        tekst = str(waarde).strip()
        if len(tekst) > _KAART_MAX_TEKENS:
            continue
        eenheid = KAART_VELDEN[veld]
        # Staat de eenheid al in de waarde ("9 liter"), dan niet nog eens.
        if eenheid and not any(c.isalpha() for c in tekst):
            tekst = '%s %s' % (tekst, eenheid)
        tags.append(tekst)

    return tags if len(tags) >= 2 else []


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

# Sommige merken schrijven hun code mét spatie: "Miele DGC 7151", "Liebherr
# IRd 4100-62", "Whirlpool WPM 966W". Die viel buiten het patroon hierboven,
# want dat kijkt per woord. Gemeten 25 aug op 300 echte titels: dit levert
# 28 extra herkenningen op (9% van de catalogus) zonder één valse treffer.
#
# Streng gehouden, want een verkeerd modelnummer in de titel is erger dan
# geen: minstens drie cijfers (anders vangt hij "Inhoud 20" en "Ena 5"),
# hooguit vijf letters (anders "Magnetron 20L"), en nooit het eerste woord
# van de titel -- dat is het merk.
_TITEL_TYPENUMMER_GESPLITST = re.compile(
    r'^([a-z]{1,5})\s([0-9]{3,}[a-z0-9-]*)$', re.IGNORECASE)

_LEEG = ('niet van toepassing', 'nvt', 'n.v.t.', '-')

# Ruimte voor het productdeel van de paginatitel. Google toont ongeveer 60
# tekens; " | WitgoedAanbod.nl" kost er 19.
_TITEL_MAX = 45

# Eigen "nog niet uitgezocht"-waarde, want None is hier een geldige uitkomst
# (dit apparaat heeft geen herkenbaar modelnummer) en zou anders elke keer
# opnieuw worden opgezocht.
_NIET_BEPAALD = object()


def merknaam(product):
    """De merknaam zoals het merk hem zelf schrijft, of leeg.

    De feeds spellen merken wisselend: "Lg" naast "LG", "Aeg" naast "AEG".
    Op de categoriepagina werd dat al rechtgetrokken (filter_helpers.
    canonical_brand, met een vaste lijst voor merken die per se hoofdletters
    zijn), maar de productpagina las het kale veld.

    Dat viel niet op zolang de paginatitel de lange feedtitel was. Nu die
    kort is, staat er "Lg GBBSJ10DPY" in het zoekresultaat terwijl iemand op
    "lg gbbsj10dpy" zocht -- en een merknaam die anders geschreven is dan het
    merk zelf doet, oogt als een pagina die het niet zo nauw neemt.
    """
    from filter_helpers import canonical_brand

    return canonical_brand((product.brand or '').strip())


# Enkelvoud per categorie voor in de paginatitel. Handmatig, want
# Nederlandse meervouden zijn niet met een regel te vangen ("drogers" ->
# "droger", maar "apparaatsets" -> "apparaatset" en "kookplaten" ->
# "kookplaat"). Ontbreekt een slug, dan valt de titel terug op alleen merk
# en model -- precies zoals hij daarvoor was.
_CATEGORIE_ENKELVOUD = {
    'wasmachines': 'wasmachine',
    'drogers': 'droger',
    'wasdroogcombinaties': 'was-droogcombinatie',
    'koelkasten': 'koelkast',
    'vaatwassers': 'vaatwasser',
    'magnetrons': 'magnetron',
    'stofzuigers': 'stofzuiger',
    'ovens': 'oven',
    'koffiemachines': 'koffiemachine',
    'fornuizen': 'fornuis',
    'kookplaten': 'kookplaat',
    'afzuigkappen': 'afzuigkap',
    'apparaatsets': 'apparaatset',
}


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
    merk = merknaam(product)
    model = modelnummer(product)
    if merk and model:
        # Merk niet twee keer: "LG LG GBBSJ10DPY" bij feeds die het merk in
        # het Model-veld herhalen.
        if model.upper().startswith(merk.upper()):
            kop = model
        else:
            kop = f"{merk} {model}"

        # Wat voor apparaat het is, erachter. Gemeten 25 aug in Search
        # Console: 950 productpagina's kregen 4.143 vertoningen en 81
        # klikken -- 1,96%, terwijl de mediane positie 8 is en daar 3 tot
        # 8% normaal is. De titel was een kale modelcode ("Bosch
        # SMV4EMX01N"), dus wie niet toevallig dat exacte type zocht, zag
        # niet eens waar de pagina over ging. De code blijft vooraan staan,
        # want dát is wat mensen intikken.
        #
        # Bewust GEEN prijs in de titel: Google bewaart titels dagen tot
        # weken, en een prijs die daar veroudert is precies de belofte die
        # deze site nergens doet.
        soort = _CATEGORIE_ENKELVOUD.get(
            product.category.slug if product.category else '')
        if soort and soort.lower() not in kop.lower():
            return f"{kop} {soort}"
        return kop

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

    # Pas als er in één woord niets zat: de code met een spatie erin. Alleen
    # in de kop van de titel (tot de eerste streep of komma), want daarna
    # begint de omschrijving met maten en vermogens.
    kop = re.split(r'\s[-–—(]|,', titel)[0]
    woorden = [w.strip('.,;:()[]/') for w in kop.split()]
    for i in range(1, len(woorden) - 1):
        paar = f"{woorden[i]} {woorden[i + 1]}"
        if _TITEL_TYPENUMMER_GESPLITST.match(paar):
            return paar.upper()
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
