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
            'zin': '{n} drogers met stoomfunctie',
            'paginatitel': 'Droger met stoomfunctie vergelijken - minder strijkwerk | WitgoedAanbod.nl',
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
                'kiezen ook op het vulgewicht en het energielabel; die staan bij '
                'elk model hieronder.',
            ],
            'video': 'khtqhn4gTso',  # Coolblue Productadvies: stoomfunctie op een wasdroger
            'meta': 'Droger met stoomfunctie vergelijken: minder strijken, '
                    'kreukels en geurtjes eruit. Alle modellen met stoom op prijs '
                    'bij onze winkels.',
        },
    },
    'koelkasten': {
        'amerikaans': {
            'kop': 'Amerikaanse koelkast: side-by-side met veel ruimte',
            'label': 'amerikaans',
            'zin': '{n} amerikaanse koelkasten',
            'patroon': _ONTKENNING + r'(amerikaans|side[- ]?by[- ]?side)',
            'in_tekst': True,
            'uitleg': [
                'Een amerikaanse koelkast heeft twee deuren naast elkaar: links de vriezer, rechts de koelkast, of een koelkast boven twee vriesladen. Ze zijn 80 tot 95 cm breed en bieden 500 tot 700 liter, vaak met een water- en ijsdispenser in de deur.',
                "Zo'n kast vraagt ruimte, ook aan de zijkanten en de achterkant voor ventilatie, en een dispenser met wateraansluiting vraagt een waterleiding in de buurt. Het stroomverbruik ligt door de grootte hoger dan bij een gewone koel-vriescombinatie; het energielabel hieronder laat het verschil zien.",
            ],
            'video': None,
            'meta': 'Amerikaanse koelkast vergelijken: side-by-side, 500 tot 700 liter, met of zonder dispenser. Alle modellen op prijs bij onze winkels.',
            'paginatitel': 'Amerikaanse koelkast vergelijken - side-by-side | WitgoedAanbod.nl',
        },
        'no-frost': {
            'kop': 'No frost koelkast: nooit meer ontdooien',
            'label': 'no frost',
            'zin': '{n} no-frost koelkasten en koel-vriescombinaties',
            'paginatitel': 'No frost koelkast vergelijken - nooit meer ontdooien | WitgoedAanbod.nl',
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
            'zin': '{n} inbouw vaatwassers',
            'paginatitel': 'Inbouw vaatwasser vergelijken - volledig en half geïntegreerd | WitgoedAanbod.nl',
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
    'wasmachines': {
        'stoomfunctie': {
            'kop': 'Wasmachine met stoomfunctie: frisser en minder kreukels',
            'label': 'met stoomfunctie',
            'zin': '{n} wasmachines met stoomfunctie',
            'patroon': _ONTKENNING + r'(stoomfunctie|stoomprogramma|steam|stoom)',
            'in_tekst': True,
            'uitleg': [
                "Een wasmachine met stoomfunctie voegt aan het eind van de wasbeurt stoom toe, of heeft aparte stoomprogramma's. Stoom maakt de vezels soepel, zodat de was met minder kreukels uit de trommel komt en het strijken lichter wordt. Een kort stoomprogramma frist kleding op die niet echt vuil is, zonder een volledige wasbeurt.",
                'Stoom is een extra, geen vervanging van wassen: vlekken gaan er niet mee uit. Het kost een beetje water en tijd per programma, en een model met stoom is meestal wat duurder dan hetzelfde model zonder. Vergelijk hieronder ook het vulgewicht, het toerental en het energielabel.',
            ],
            'video': None,
            'meta': 'Wasmachine met stoomfunctie vergelijken: minder kreukels, opfrissen zonder wassen. Alle modellen met stoom op prijs bij onze winkels.',
            'paginatitel': 'Wasmachine met stoomfunctie vergelijken - minder kreukels | WitgoedAanbod.nl',
        },
    },
    'koffiemachines': {
        'volautomaat': {
            'kop': 'Volautomatische koffiemachine: verse bonen, één knop',
            'label': 'volautomaat',
            'zin': '{n} volautomatische koffiemachines',
            'patroon': _ONTKENNING + r'(volautomat|bonen)',
            'in_tekst': True,
            'uitleg': [
                'Een volautomaat maalt per kopje verse bonen, zet de koffie en reinigt zichzelf tussendoor. Je drukt op een knop en krijgt espresso, lungo of cappuccino; de meeste modellen hebben een melkopschuimer of een melksysteem dat het schuim zelf maakt.',
                'Bonen zijn per kopje goedkoper dan cups of pads, maar de machine zelf kost meer en vraagt onderhoud: ontkalken, de zetgroep spoelen en bij een melksysteem dagelijks reinigen. Let bij het kiezen op de grootte van het waterreservoir en het bonenreservoir, en of het melksysteem los in de vaatwasser kan.',
            ],
            'video': None,
            'meta': 'Volautomatische koffiemachine vergelijken: verse bonen per kopje, melkschuim met één knop. Alle volautomaten op prijs bij onze winkels.',
            'paginatitel': 'Volautomatische koffiemachine vergelijken - bonen, één knop | WitgoedAanbod.nl',
        },
    },
    'stofzuigers': {
        'dweilfunctie': {
            'kop': 'Stofzuiger met dweilfunctie: zuigen en dweilen in één',
            'label': 'met dweilfunctie',
            'zin': '{n} stofzuigers met dweilfunctie',
            'patroon': _ONTKENNING + r'(dweil)',
            'in_tekst': False,
            'uitleg': [
                'Een stofzuiger met dweilfunctie zuigt en dweilt in dezelfde beurt. Bij een robotstofzuiger zit er een waterreservoir en een dweildoek onder; bij een steelstofzuiger een roterende dweilrol of een nat-en-droogkop. Handig voor harde vloeren: tegels, laminaat, pvc.',
                'Een dweilfunctie vervangt geen goede schrobbeurt bij hardnekkig vuil; het is onderhoud, geen grote schoonmaak. Let op of de dweil automatisch omhoog gaat op tapijt (anders wordt je kleed nat), hoe groot het waterreservoir is en of het dweilstation zichzelf reinigt. Bij elk model hieronder staat de laagste prijs van onze winkels.',
            ],
            'video': None,
            'meta': 'Stofzuiger met dweilfunctie vergelijken: robot- en steelstofzuigers die zuigen en dweilen. Alle modellen op prijs bij onze winkels.',
            'paginatitel': 'Stofzuiger met dweilfunctie vergelijken - zuigen en dweilen | WitgoedAanbod.nl',
        },
        'steelstofzuiger': {
            'kop': 'Steelstofzuiger: snoerloos en licht',
            'label': 'steelstofzuiger',
            'zin': '{n} steelstofzuigers',
            'patroon': _ONTKENNING + r'(steelstofzuiger|steelzuiger|snoerloos|draadloos)',
            'in_tekst': False,
            'uitleg': [
                'Een steelstofzuiger werkt op een accu en hangt aan een haak of oplaadstation, klaar voor een snelle ronde. Geen snoer, geen zak, en licht genoeg om mee de trap op te gaan. De meeste modellen zijn ook los te gebruiken als kruimeldief voor de bank of de auto.',
                'De accuduur is de belangrijkste beperking: reken op 20 tot 60 minuten, en op de hoogste stand vaak veel minder. Het stofreservoir is klein en moet vaker geleegd worden dan een zak. Let bij het kiezen op de accuduur op de gewone stand, het gewicht en of de accu los te vervangen is.',
            ],
            'video': None,
            'meta': 'Steelstofzuiger vergelijken: snoerloos, licht, met accuduur en gewicht. Alle steelstofzuigers op prijs bij onze winkels.',
            'paginatitel': 'Steelstofzuiger vergelijken - snoerloos en licht | WitgoedAanbod.nl',
        },
        'robotstofzuiger': {
            'kop': 'Robotstofzuiger: zuigt terwijl jij iets anders doet',
            'label': 'robot',
            'zin': '{n} robotstofzuigers',
            'patroon': _ONTKENNING + r'(robot)',
            'in_tekst': False,
            'uitleg': [
                'Een robotstofzuiger rijdt zelf door het huis, brengt de plattegrond in kaart en gaat terug naar zijn station om op te laden. Je start hem met een app of op een vast tijdstip. Ideaal voor dagelijks bijhouden van harde vloeren en laagpolig tapijt.',
                'Een robot komt niet overal: randen, drempels en losse kabels blijven lastig, en de trap doet hij niet. Modellen met een leegstation hoef je weken niet aan te raken; zonder station leeg je het bakje na elke beurt. Let op de zuigkracht op tapijt, de hoogte (past hij onder de bank) en of hij ook kan dweilen.',
            ],
            'video': None,
            'meta': 'Robotstofzuiger vergelijken: met of zonder leegstation, met of zonder dweil. Alle robotstofzuigers op prijs bij onze winkels.',
            'paginatitel': 'Robotstofzuiger vergelijken - zuigt zelf | WitgoedAanbod.nl',
        },
    },
    'ovens': {
        'airfryer': {
            'kop': 'Airfryer: krokant met weinig of geen olie',
            'label': 'airfryer',
            'zin': '{n} airfryers',
            'patroon': _ONTKENNING + r'(airfryer|hetelucht ?friteuse|heteluchtfriteuse)',
            'in_tekst': False,
            'uitleg': [
                'Een airfryer is een kleine heteluchtoven met een krachtige ventilator. Frites, kipnuggets en groenten worden krokant met een lepel olie of helemaal zonder, en hij is in een paar minuten op temperatuur. Voor kleine porties is hij sneller en zuiniger dan de grote oven.',
                'De inhoud is de belangrijkste keuze: rond de 4 liter is genoeg voor één of twee personen, een gezin wil een model van 6 liter of meer of een dubbele lade. Let ook op of de mand en de bodem in de vaatwasser mogen, en op het geluid van de ventilator. Bij elk model hieronder staat de laagste prijs van onze winkels.',
            ],
            'video': None,
            'meta': 'Airfryer vergelijken: inhoud, dubbele lade, vaatwasserbestendig. Alle airfryers op prijs bij onze winkels.',
            'paginatitel': 'Airfryer vergelijken - krokant zonder olie | WitgoedAanbod.nl',
        },
        'inbouw': {
            'kop': 'Inbouwoven: in de kastenwand op ooghoogte',
            'label': 'inbouw',
            'zin': '{n} inbouwovens',
            'patroon': _ONTKENNING + r'(\binbouw)',
            'in_tekst': False,
            'uitleg': [
                'Een inbouwoven zit in een keukenkast, meestal op ooghoogte, en past in een standaardnis van 60 cm breed en 60 cm hoog. Compacte modellen van 45 cm hoog combineren oven en magnetron in één nis. Hetelucht is de standaard; duurdere modellen voegen stoom, een braadthermometer of een pyrolyse-reiniging toe.',
                'Meet de nis (breedte, hoogte en diepte) voordat je kiest, en kijk naar de aansluiting: een gewone oven werkt op een normaal stopcontact, een oven met veel vermogen vraagt soms een aparte groep. Let daarnaast op de inhoud in liters en het energielabel.',
            ],
            'video': None,
            'meta': 'Inbouwoven vergelijken: 60 en 45 cm hoog, hetelucht, stoom, pyrolyse. Alle inbouwovens op prijs bij onze winkels.',
            'paginatitel': 'Inbouwoven vergelijken - 60 en 45 cm | WitgoedAanbod.nl',
        },
    },
    'magnetrons': {
        'combimagnetron': {
            'kop': 'Combimagnetron: magnetron, oven en grill in één',
            'label': 'combi',
            'zin': '{n} combimagnetrons',
            'patroon': _ONTKENNING + r'(combi)',
            'in_tekst': False,
            'uitleg': [
                'Een combimagnetron verwarmt met microgolven, maar heeft ook hetelucht en een grill. Daarmee bak je een pizza of een kleine cake en gratineer je een ovenschotel, terwijl opwarmen en ontdooien gewoon met de magnetron gaat. Voor een kleine keuken of een studentenkamer vervangt hij de oven.',
                'De inhoud is kleiner dan een echte oven, dus een groot gerecht past er niet in, en de combinatie van microgolven en hetelucht vraagt even wennen. Let bij het kiezen op het vermogen, de inhoud in liters en of het een vrijstaand of inbouwmodel is. Bij elk model hieronder staat de laagste prijs van onze winkels.',
            ],
            'video': None,
            'meta': 'Combimagnetron vergelijken: magnetron, hetelucht en grill in één. Alle combimagnetrons op prijs bij onze winkels.',
            'paginatitel': 'Combimagnetron vergelijken - oven en grill in één | WitgoedAanbod.nl',
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
