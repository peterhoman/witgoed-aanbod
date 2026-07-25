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
                    'load', 'cleansing')),
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


def _afmetingen(specs):
    """'Product hoogte' + breedte + lengte -> één regel 'h x b x d'.

    De feeds leveren de drie maten los; op de pagina is één regel bruikbaarder
    dan drie. Ontbreekt er een, dan tonen we de maten die er wel zijn.
    """
    delen = [specs.get(k) for k in ('Product hoogte', 'Product breedte', 'Product lengte')]
    delen = [str(d).strip() for d in delen if d]
    return ' × '.join(delen) if delen else None


def kernspecs(product, aantal=8):
    """De belangrijkste specs van dit apparaat, als lijst van (label, waarde).

    Staat de categorie niet in KERNVELDEN, of levert de lijst te weinig op,
    dan vullen we aan met de eerste velden uit de feed — beter iets in de
    volgorde van de winkel dan een half blok.
    """
    specs = product.specs or {}
    if not specs:
        return []

    slug = product.category.slug if product.category else ''
    gekozen, gebruikt = [], set()

    for veld in KERNVELDEN.get(slug, []):
        if veld == AFMETINGEN:
            waarde = _afmetingen(specs)
            if waarde:
                gekozen.append(('Afmetingen (h × b × d)', waarde))
                gebruikt.update(('Product hoogte', 'Product breedte', 'Product lengte'))
        elif specs.get(veld):
            gekozen.append((veld, specs[veld]))
            gebruikt.add(veld)
        if len(gekozen) >= aantal:
            break

    for sleutel, waarde in specs.items():
        if len(gekozen) >= aantal:
            break
        if sleutel not in gebruikt and waarde:
            gekozen.append((sleutel, waarde))
            gebruikt.add(sleutel)

    return gekozen[:aantal]


def groepeer_specs(product):
    """Alle specs verdeeld over benoemde blokken, voor de uitgeklapte lijst.

    Geeft een lijst van (groepsnaam, [(label, waarde), ...]); lege groepen
    vallen weg en Overig staat altijd onderaan.
    """
    specs = product.specs or {}
    if not specs:
        return []

    per_groep = {naam: [] for naam, _ in SPEC_GROEPEN}
    per_groep[OVERIG] = []

    for sleutel, waarde in specs.items():
        if not waarde:
            continue
        laag = sleutel.lower()
        doel = next((naam for naam, trefwoorden in SPEC_GROEPEN
                     if any(tw in laag for tw in trefwoorden)), OVERIG)
        per_groep[doel].append((sleutel, waarde))

    volgorde = [naam for naam, _ in SPEC_GROEPEN] + [OVERIG]
    return [(naam, per_groep[naam]) for naam in volgorde if per_groep[naam]]


def modelnummer(product):
    """Het modelnummer uit het Model-spec-veld, of None.

    Alleen dit veld: MPN levert bij sommige merken interne codes op
    ("914 913 271") die geen koper herkent, en het uit de titel vissen breekt
    op was/droog-sets met twee modelnummers in de naam. Is het veld leeg, dan
    toont de pagina alleen het merk.
    """
    specs = product.specs or {}
    waarde = (specs.get('Model') or '').strip()
    if not waarde or waarde.lower() in ('niet van toepassing', 'nvt', 'n.v.t.', '-'):
        return None
    return waarde
