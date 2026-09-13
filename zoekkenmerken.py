"""Kenmerkpagina's op de zoekzin: "droger met stoomfunctie", "no frost koelkast".

Waarom dit bestaat
------------------
We hadden al 34 kenmerkpagina's, maar allemaal op getallen uit het
energielabel ("wasmachines 60-70 cm breed", "zeer stille koelkasten"). Zo
zoekt niemand. Mensen zoeken zoals Peter het op 13 september 2026 zelf deed:
"droogtrommel met strijk functie" -- en Google stuurt die zoekers naar
"droger met stoomfunctie". Coolblue en Slimster staan met precies zulke
pagina's op pagina 1; wij hadden ze niet.

Wat deze pagina's anders maakt dan de 552 filterpagina's die op 25 augustus
nul klikken opleverden: de kop IS de zoekzin, er staat een korte uitleg in
gewone taal, en er zijn er maar een handvol. Of dat genoeg is, weten we pas
na vier weken Search Console; daarom eerst drie proefpagina's.

Herkenning
----------
Per kenmerk een patroon over de titel, de specificaties en (alleen als dat
is aangezet) de winkeltekst. "geen stoomfunctie" of "zonder no frost" telt
niet mee. Alleen leverbare producten; de lijst wordt een kwartier
onthouden, net als de andere facetten.
"""
import re
import time

# Tekst mag niet vooraf worden gegaan door een ontkenning.
_ONTKENNING = r'(?<!geen )(?<!zonder )(?<!niet )'

KENMERKEN = {
    'drogers': {
        'stoomfunctie': {
            'kop': 'Droger met stoomfunctie: minder strijkwerk',
            'label': 'met stoomfunctie',
            'patroon': _ONTKENNING + r'(stoomfunctie|stoomprogramma|steam|stoom)',
            'in_tekst': True,
            'uitleg': [
                'Een droger met stoomfunctie blaast aan het eind van het '
                'programma stoom door de trommel. Dat haalt de meeste kreukels '
                'uit je was, zodat je minder of niet hoeft te strijken; overhemden '
                'en blouses kun je vaak zo op een hanger hangen. Ook geurtjes gaan '
                'er met stoom uit, handig voor kleding die niet gewassen hoeft te '
                'worden.',
                'Reken er niet op dat het strijkwerk helemaal verdwijnt: het wordt '
                'minder. Een droger met stoom is duurder dan hetzelfde model zonder, '
                'en een stoomprogramma kost wat water en tijd extra. Let bij het '
                'kiezen ook op het vulgewicht en het energielabel -- die staan bij '
                'elk model hieronder.',
            ],
            'video': 'khtqhn4gTso',  # Coolblue Productadvies: stoomfunctie op een wasdroger
            'meta': 'Droger met stoomfunctie vergelijken: minder strijken, '
                    'kreukels en geurtjes eruit. Alle modellen met stoom op prijs '
                    'bij onze winkels.',
        },
    },
    'koelkasten': {
        'no-frost': {
            'kop': 'No frost koelkast: nooit meer ontdooien',
            'label': 'no frost',
            'patroon': _ONTKENNING + r'(no[- ]?frost|nofrost)',
            'in_tekst': True,
            'uitleg': [
                'Een no-frost koelkast heeft een ventilator die koude, droge lucht '
                'door de vriesruimte blaast, zodat er geen ijslaag aangroeit. '
                'Ontdooien hoeft dus niet meer, en de vriezer houdt zijn inhoud '
                'gelijkmatiger op temperatuur.',
                'Nadelen zijn er ook: iets meer stroomverbruik dan een gewone '
                'koelkast, een ventilator die je zachtjes kunt horen, en onverpakt '
                'eten droogt in de vriezer sneller uit. Let daarom op het '
                'geluidsniveau en het jaarverbruik; die staan bij elk model hieronder '
                'als we ze uit het energielabel kennen.',
            ],
            'video': None,
            'meta': 'No frost koelkast vergelijken: nooit meer ontdooien. Alle '
                    'no-frost koelkasten en koel-vriescombinaties op prijs bij '
                    'onze winkels.',
        },
    },
    'vaatwassers': {
        'inbouw': {
            'kop': 'Inbouw vaatwasser: past in je keuken',
            'label': 'inbouw',
            'patroon': _ONTKENNING + r'(\binbouw|volledig ge[ïi]ntegreerd|half ge[ïi]ntegreerd|onderbouw)',
            'in_tekst': False,  # "inbouw" in een winkeltekst zegt te vaak iets anders
            'uitleg': [
                'Een inbouw vaatwasser verdwijnt achter een keukenfrontje en past in '
                'een standaardnis van 60 cm breed; voor kleine keukens zijn er smalle '
                'modellen van 45 cm. Volledig geïntegreerd betekent dat de bediening '
                'in de bovenrand van de deur zit en van buiten niets te zien is; bij '
                'een half-geïntegreerd model blijft het bedieningspaneel zichtbaar.',
                'Meet de nis (hoogte, breedte en diepte) voordat je kiest, en let op '
                'het geluidsniveau: onder de 44 dB hoor je een vaatwasser in een open '
                'keuken nauwelijks. Het keukenfrontje zelf is nooit inbegrepen.',
            ],
            'video': None,
            'meta': 'Inbouw vaatwasser vergelijken: volledig of half geïntegreerd, '
                    '60 en 45 cm breed. Alle inbouwmodellen op prijs bij onze winkels.',
        },
    },
}

_CACHE = {}
_TTL = 15 * 60


def kenmerken_voor(category_slug):
    """{kenmerk_slug: definitie} voor een categorie, of {}."""
    return KENMERKEN.get(category_slug, {})


def _tekst_van(product, in_tekst):
    specs = product.specs or {}
    delen = [product.title or '',
             ' '.join(f'{k} {v}' for k, v in specs.items())]
    if in_tekst:
        delen.append(product.description or '')
    return ' '.join(delen)


def producten_met_kenmerk(category, kenmerk_slug):
    """Product-id's in deze categorie die het kenmerk hebben (leverbaar), of [].

    Een kwartier onthouden per (categorie, kenmerk), zoals de andere
    facetten: de uitkomst verandert alleen als de syncs draaien.
    """
    from models import Product

    definitie = kenmerken_voor(category.slug).get(kenmerk_slug)
    if not definitie:
        return []
    sleutel = (category.id, kenmerk_slug)
    nu = time.time()
    hit = _CACHE.get(sleutel)
    if hit and nu - hit[0] < _TTL:
        return hit[1]

    patroon = re.compile(definitie['patroon'], re.I)
    ids = []
    for product in (Product.query
                    .filter_by(category_id=category.id, is_available=True)
                    .with_entities(Product.id, Product.title, Product.description, Product.specs)
                    .all()):
        if patroon.search(_tekst_van(product, definitie['in_tekst'])):
            ids.append(product.id)
    _CACHE[sleutel] = (nu, ids)
    return ids
