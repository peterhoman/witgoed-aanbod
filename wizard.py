"""
Keuzehulp-wizard: een paar simpele vragen i.p.v. specs-jargon.

Niet iedereen weet of ze "9 kg vulgewicht" of "1400 toeren" nodig hebben —
de wizard vertaalt mensentaal ("met hoeveel personen woon je?") naar
dezelfde spec-filters die de categoriepagina al ondersteunt (?spec=...).

Twee vraagtypes:
- 'bucket': het antwoord is een drempelwaarde (bv. "tot 7 kg"). De bijbehorende
  spec-waarden worden bij elke wizard-weergave LIVE berekend uit de echte
  productdata (zie resolve_bucket_options) — nooit een hardgecodeerde lijst
  van vermoede waarden, want spec-waarden verschillen qua notatie per winkel-
  feed ("9 kg" vs "9,0 kg") en veranderen mee met nieuwe producten.
- 'exact': het antwoord wijst direct naar een vaste spec-waarde (bv.
  energielabel A) of naar None ("maakt niet uit" — dit filter dan niet
  meeneemt, in plaats van te filteren op een lege waardenlijst).

De vraag-drempels zelf (vulgewicht-categorieën, wat "stil" betekent) komen
uit dezelfde vuistregels als de bestaande koopgidsen (guides_content.py /
seed_guides.py) — geen nieuwe aannames, alleen hergebruik van wat daar al
stond.
"""
import re

_NUMMER = re.compile(r'\d+(?:[.,]\d+)?')


def _parse_nummer(waarde):
    """'9 kg' -> 9.0, '1400 r/min' -> 1400.0, '10.5 kg' -> 10.5."""
    m = _NUMMER.search(str(waarde))
    if not m:
        return None
    return float(m.group().replace(',', '.'))


def resolve_bucket_options(spec_facet_values, opties):
    """Voor elke {'label', 'max'}-optie: welke échte spec-waarden vallen
    eronder. Zonder expliciete 'min' sluiten de buckets op elkaar aan
    (ondergrens = vorige bovengrens); mét 'min' mogen ze overlappen — een
    8kg-machine past immers bij "1-2 personen" én bij een gezin, en juist
    de kleine maten zijn zeldzaam in het echte aanbod. 'geen_filter': True
    betekent "maakt niet uit": geen spec-filter, zodat ook producten
    zonder deze spec in beeld blijven. Opties zonder enige matchende
    productwaarde worden overgeslagen (geen doodlopende keuze aanbieden)."""
    resultaat = []
    vorige_grens = 0
    for optie in opties:
        if optie.get('geen_filter'):
            resultaat.append({'label': optie['label'], 'waarden': None})
            continue
        bovengrens = optie['max']
        ondergrens = optie.get('min', vorige_grens)
        match = []
        for w in spec_facet_values:
            n = _parse_nummer(w)
            if n is None:
                continue
            if n >= ondergrens and (bovengrens is None or n < bovengrens):
                match.append(w)
        if match:
            resultaat.append({'label': optie['label'], 'waarden': match})
        vorige_grens = bovengrens if bovengrens is not None else vorige_grens
    return resultaat


# Drempels uit wasmachine-kopen-waar-op-letten, met bewuste overlap: de gids
# zegt "7 kg volstaat; 8 kg geeft ruimte" voor 1-2 personen en "8-9 kg is de
# sweet spot" voor een gezin. Een harde grens op 7 kg liet in de praktijk
# maar een handvol machines over (kleine trommels zijn zeldzaam geworden).
WASMACHINE_VULGEWICHT = [
    {'label': '1-2 personen', 'max': 8.5},
    {'label': '3-4 personen', 'min': 7.5, 'max': 9.5},
    {'label': '5 of meer personen', 'min': 8.5, 'max': None},
]
# Drempel uit droger-kopen-waar-op-letten: vergelijkbare capaciteit als de
# wasmachine, met dezelfde overlap rond 8 kg.
DROGER_LAADVERMOGEN = [
    {'label': 'Klein huishouden (1-2 personen)', 'max': 8.5},
    {'label': 'Gezin (3 personen of meer)', 'min': 7.5, 'max': None},
]
# Drempels uit koelkast-kopen-complete-gids: 150-250l=1-2p, 250-350l=gezin,
# 350l+=groot gezin — met overlap op de grenzen (een 260l-koelkast is voor
# beide situaties prima).
KOELKAST_VOLUME = [
    {'label': '1-2 personen', 'max': 275},
    {'label': '3-4 personen', 'min': 225, 'max': 375},
    {'label': '5 of meer personen', 'min': 325, 'max': None},
]
# Drempels uit vaatwasser-kopen-complete-gids: 10-12=1-2p, 12-14=gezin,
# 14+=groot gezin — zelfde overlap-principe.
VAATWASSER_COUVERTS = [
    {'label': '1-2 personen', 'max': 12.5},
    {'label': '3-4 personen', 'min': 11.5, 'max': 14.5},
    {'label': '5 of meer personen', 'min': 13.5, 'max': None},
]
# Uit vaatwasser-gids: stille modellen zitten rond 40-44 dB. "Maakt niet
# uit" is bewust géén filter: de oude bucket (alles boven 44,5 dB) sloot
# juist de stille én de spec-loze modellen uit.
GELUID_STIL = [
    {'label': 'Ja, het liefst zo stil mogelijk', 'max': 44.5},
    {'label': 'Maakt niet uit', 'geen_filter': True},
]
# Toerental als ondergrens-bucket i.p.v. de exacte tekst '1600 r/min':
# notaties verschillen per winkel-feed, en zo doet 1700 toeren ook mee.
WASMACHINE_TOERENTAL = [
    {'label': 'Ja, minstens 1600 toeren', 'min': 1550, 'max': None},
    {'label': 'Maakt niet uit', 'geen_filter': True},
]

WIZARD_QUESTIONS = {
    'wasmachines': {
        'titel': 'Welke wasmachine past bij jou?',
        'vragen': [
            {'vraag': 'Met hoeveel personen woon je?', 'key': 'Laadvermogen wasmachine',
             'type': 'bucket', 'opties': WASMACHINE_VULGEWICHT},
            {'vraag': 'Hoe belangrijk is energieverbruik voor jou?', 'key': 'Waarde energielabel',
             'type': 'exact', 'opties': [
                 {'label': 'Heel belangrijk — het zuinigste', 'waarden': ['A']},
                 {'label': 'Maakt niet zoveel uit', 'waarden': None},
             ]},
            {'vraag': 'Wil je dat de was extra droog uit de trommel komt (handig i.c.m. een droger)?',
             'key': 'Toerental centrifuge', 'type': 'bucket', 'opties': WASMACHINE_TOERENTAL},
        ],
    },
    'koelkasten': {
        'titel': 'Welke koelkast past bij jou?',
        'vragen': [
            {'vraag': 'Met hoeveel personen woon je?', 'key': 'Volume in liters',
             'type': 'bucket', 'opties': KOELKAST_VOLUME},
            {'vraag': 'Hoe belangrijk is energieverbruik voor jou?', 'key': 'Waarde energielabel',
             'type': 'exact', 'opties': [
                 {'label': 'Heel belangrijk — het zuinigste', 'waarden': ['A']},
                 {'label': 'Maakt niet zoveel uit', 'waarden': None},
             ]},
            {'vraag': 'Vind je een stille koelkast belangrijk (staat vaak in of naast de keuken)?',
             'key': 'Geluidsniveau', 'type': 'bucket', 'opties': GELUID_STIL},
        ],
    },
    'drogers': {
        'titel': 'Welke droger past bij jou?',
        'vragen': [
            {'vraag': 'Hoeveel was droog je meestal per keer?', 'key': 'Laadvermogen wasdroger',
             'type': 'bucket', 'opties': DROGER_LAADVERMOGEN},
            {'vraag': 'Warmtepompdroger of maakt het niet uit?', 'key': 'Type droger',
             'type': 'exact', 'opties': [
                 {'label': 'Warmtepompdroger (zuiniger)', 'waarden': ['Warmtepompdroger']},
                 {'label': 'Maakt niet uit', 'waarden': None},
             ]},
            {'vraag': 'Hoe belangrijk is energieverbruik voor jou?', 'key': 'Waarde energielabel',
             'type': 'exact', 'opties': [
                 {'label': 'Heel belangrijk — het zuinigste', 'waarden': ['A']},
                 {'label': 'Maakt niet zoveel uit', 'waarden': None},
             ]},
        ],
    },
    'vaatwassers': {
        'titel': 'Welke vaatwasser past bij jou?',
        'vragen': [
            {'vraag': 'Met hoeveel personen woon je?', 'key': 'Aantal couverts',
             'type': 'bucket', 'opties': VAATWASSER_COUVERTS},
            {'vraag': 'Hoe belangrijk is energieverbruik voor jou?', 'key': 'Waarde energielabel',
             'type': 'exact', 'opties': [
                 {'label': 'Heel belangrijk — het zuinigste', 'waarden': ['A']},
                 {'label': 'Maakt niet zoveel uit', 'waarden': None},
             ]},
            {'vraag': 'Draait je vaatwasser vaak \'s avonds of in een open keuken?',
             'key': 'Geluidsniveau', 'type': 'bucket', 'opties': GELUID_STIL},
        ],
    },
}


def build_wizard_context(category_slug, products):
    """Zet WIZARD_QUESTIONS[slug] om naar kant-en-klare vragen met live
    opgeloste antwoordopties, voor de wizard-pagina van deze categorie.
    Geeft None terug als deze categorie geen wizard heeft.

    Rekent de spec-facetten hier zelf ONGELIMITEERD uit i.p.v. de (top-6,
    voor de filter-zijbalk bedoelde) cache van _category_facets te
    hergebruiken: de wizard-vragen wijzen juist vaak naar specs die qua
    aanwezigheid niet in die top 6 zitten (Laadvermogen, Aantal couverts, ...).
    """
    config = WIZARD_QUESTIONS.get(category_slug)
    if not config:
        return None

    from filter_helpers import compute_spec_facets
    spec_facets = compute_spec_facets(products, max_filters=999, max_options=999)
    facet_by_key = {f['key']: [o['value'] for o in f['options']] for f in spec_facets}

    vragen = []
    for vraag in config['vragen']:
        if vraag['type'] == 'bucket':
            waarden = facet_by_key.get(vraag['key'], [])
            opties = resolve_bucket_options(waarden, vraag['opties'])
            # Alleen "maakt niet uit" over (spec ontbreekt in deze data):
            # dan is er niets te kiezen en vervalt de vraag.
            if not any(o['waarden'] for o in opties):
                opties = []
        else:
            opties = [{'label': o['label'], 'waarden': o['waarden']} for o in vraag['opties']]
        if opties:
            vragen.append({'vraag': vraag['vraag'], 'key': vraag['key'], 'opties': opties})

    if not vragen:
        return None
    return {'titel': config['titel'], 'vragen': vragen}
