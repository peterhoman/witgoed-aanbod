"""
Helpers to derive filterable facets (brand, specs) from a list of products.

These are pure functions (no Flask/DB dependencies) so they can be tested
in isolation with plain lists of objects that have `.brand` and `.specs`.
"""

import re
from collections import Counter, defaultdict

# Specs die bol.com wel meelevert maar die niemand gebruikt om op te
# filteren: verpakkingsmaten/-gewicht (niet hetzelfde als het gewicht van
# het product zelf), interne artikelcodes, handleidingtaal, en de ruwe
# fabrikant-registratienaam (soms letterlijk een e-mailadres als waarde).
# 'merk' staat er ook in: de zijbalk heeft al een eigen merkfilter (op
# products.brand); de spec-variant verscheen als tweede "Merk"-blok.
_EXCLUDED_SPEC_KEYS = {'fabrikant naam', 'taal handleiding', 'merk', 'taal bedieningspaneel'}
# 'model' (en varianten als modelnaam/modelnummer) is per product uniek en
# dus zinloos om op te filteren; maakte de zijbalk alleen maar langer.
# 'toerental aanpasbaar' is een Ja/Nee-veld dat een filterplek zou opeten
# nu 'toerental' een voorrangs-keyword is (zie hieronder).
#
# De laatste vier zijn velden die de feeds wel leveren maar waar niemand een
# apparaat op kiest. Ze aten plekken op in een lijst van zes: op wasmachines
# stonden "Stand display" en "Positie deur scharnier" in de zijbalk terwijl
# vulgewicht ontbrak. Alle vier gecontroleerd tegen de 289 veldnamen uit
# /api/category-specs: samen raken ze precies vijf velden, geen enkel nuttig.
#
# De losse buitenmaten en 'CE markering' gaan om dezelfde reden weg. Niemand
# kiest een koelkast op "Product lengte", maar de drie maten samen bezetten wel
# drie van de zes plekken -- bij drogers, koelkasten, ovens en koffiemachines
# deden ze dat ook echt. Op de detailpagina staan ze gewoon, daar voegt
# _afmetingen() ze al tot één regel samen.
#
# Voluit 'product lengte' en niet 'lengte': dat laatste raakt ook 'Snoerlengte'.
# En niet 'hoogte', want dan verdwijnen 'Nis hoogte' en 'Hoogte instelbaar' --
# juist de inbouwmaten waar iemand wél op filtert.
_EXCLUDED_SPEC_KEYWORDS = ('verpakking', 'mpn', 'model', 'toerental aanpasbaar',
                           'stand display', 'scharnier', 'steenkool',
                           'professioneel gebruik', 'product hoogte',
                           'product breedte', 'product lengte', 'ce markering')

# Filters waar bezoekers echt op zoeken krijgen voorrang: die komen direct
# na het merkblok, ook als andere specs vaker voorkomen — in déze volgorde.
# De waarden van deze filters sorteren we oplopend (energielabel A t/m G,
# vulgewicht 6 kg vóór 12 kg, toerental 1200 vóór 1600) i.p.v. op aantal.
#
# Formaat (laadvermogen/inhoud/couverts) staat hier sinds duidelijk werd dat
# de top-6 op frequentie niets te kiezen heeft: op wasmachines zit vrijwel elk
# spec-veld op exact 46 van de 255 producten -- dezelfde 46 machines die
# überhaupt specs hebben. Bij zo'n gelijkspel besliste de volgorde waarin de
# feed zijn velden aanlevert, en zo verloor vulgewicht van "Positie deur
# scharnier". Dat is toeval, geen keuze.
#
# 'volume in liters' staat er voluit: 'volume' alleen raakt ook "Volume
# koelruimte", "Volume vriesvak" en "Verstelbaar water volume", en dan zou één
# categorie vier voorrangsfilters krijgen. Om dezelfde reden geen 'vermogen'
# (negen velden, van "Zuigvermogen" tot "Aantal vermogensstanden").
_PRIORITY_SPEC_KEYWORDS = ('energielabel', 'laadvermogen', 'volume in liters',
                           'couverts', 'toerental')


def _is_priority_spec(key):
    key_lower = key.lower()
    return any(kw in key_lower for kw in _PRIORITY_SPEC_KEYWORDS)


def _priority_rank(key):
    """Positie van het eerste matchende voorrangs-keyword: bepaalt de vaste
    volgorde van de voorrangsfilters in de zijbalk (energielabel, toerental)."""
    key_lower = key.lower()
    for i, kw in enumerate(_PRIORITY_SPEC_KEYWORDS):
        if kw in key_lower:
            return i
    return len(_PRIORITY_SPEC_KEYWORDS)


def _waarde_sorteersleutel(waarde):
    """'1200 r/min' -> (0, 1200.0), 'A' -> (1, 'a'): numerieke waarden
    oplopend op getal, tekstwaarden alfabetisch — '900 r/min' belandt zo
    vóór '1600 r/min' i.p.v. erna (tekstsortering op eerste teken)."""
    m = re.match(r'\s*(\d+(?:[.,]\d+)?)', str(waarde))
    if m:
        return (0, float(m.group(1).replace(',', '.')), str(waarde).lower())
    return (1, 0.0, str(waarde).lower())


# Weergavenaam voor de filterkop. De sleutel waarop gefilterd wordt blijft de
# letterlijke feednaam -- alleen het label verandert.
#
# Dit staat er omdat een filter dat je niet herkent voor de bezoeker niet
# bestaat: bij een beoordeling van tien vergelijkers kreeg de site als minpunt
# "geen filter op energieklasse", terwijl dat filter er gewoon stond. Het heette
# alleen "Waarde energielabel" en was dichtgeklapt, dus je leest eroverheen.
#
# Alleen velden waarvan de feednaam echt in de weg zit; de rest is prima
# leesbaar en hoort hier niet bij te staan.
_WEERGAVENAAM = {
    'waarde energielabel': 'Energielabel',
    'laadvermogen wasmachine': 'Vulgewicht',
    'laadvermogen wasdroger': 'Vulgewicht',
    'volume in liters': 'Inhoud',
    'toerental centrifuge': 'Toerental',
    'top load of voorlader': 'Type lader',
    'energieverbruik per 100 cycli': 'Energieverbruik',
    'geluidsniveau centrifuge': 'Geluidsniveau',
    'stofzuigerzak of zonder stofzak': 'Stofzak',
}


def weergavenaam(key):
    """De filterkop zoals de bezoeker hem leest; valt terug op de feednaam."""
    return _WEERGAVENAAM.get((key or '').strip().lower(), key)


# EU-energielabels, van zuinig naar onzuinig.
ENERGIELADDER = 'ABCDEFG'


def energielabel_letter(waarde):
    """'A' -> 'A'. Alles wat geen kale letter A t/m G is -> None.

    Bewust niet de eerste letter van de waarde. Ovens leveren als energielabel
    de tekst "Energielabel niet van toepassing", en die begint met een E. Op
    die ene waarde was een facetpagina /category/ovens/energielabel/e ontstaan
    die in de sitemap stond en beweerde het zuinigste model te tonen -- een
    pizzaoven zonder energielabel.

    De lengtecheck hoort erbij: `'AB' in 'ABCDEFG'` is ook waar, dus een kale
    substring-test accepteert lege en samengestelde waarden.
    """
    tekst = str(waarde or '').strip().upper()
    return tekst if len(tekst) == 1 and tekst in ENERGIELADDER else None


def _is_excluded_spec(key):
    key_lower = key.lower()
    if key_lower in _EXCLUDED_SPEC_KEYS:
        return True
    return any(kw in key_lower for kw in _EXCLUDED_SPEC_KEYWORDS)


# Merken waarvan de juiste schrijfwijze geen Titelvorm is. De feeds leveren
# ze door elkaar ("LG" naast "Lg", "chiq" naast "ChiQ") en dan wint de
# vaakst-voorkomende variant het, ook als die fout is: bij 8x "Lg" tegen
# 3x "LG" zou de zijbalk "Lg" tonen. Voor deze merken ligt de naam dus vast.
_MERK_SCHRIJFWIJZE = {
    'aeg': 'AEG',
    'lg': 'LG',
    'chiq': 'ChiQ',
    'ok': 'OK',
    'bsh': 'BSH',
    'smeg': 'Smeg',
}


def canonical_brand(naam, casing_counts=None):
    """Weergavenaam voor een merk, ongeacht hoe de feed het spelde.

    Staat het merk in _MERK_SCHRIJFWIJZE, dan wint die vaste schrijfwijze.
    Anders wint de vaakst voorkomende variant uit `casing_counts` (een
    Counter van schrijfwijze -> aantal), en zonder die telling de naam zelf.
    """
    naam = (naam or '').strip()
    if not naam:
        return ''
    vast = _MERK_SCHRIJFWIJZE.get(naam.lower())
    if vast:
        return vast
    if casing_counts:
        return casing_counts.most_common(1)[0][0]
    return naam


def compute_brand_facet(products):
    """Return a list of {'value': brand, 'count': n} sorted by count desc, then name.

    Schrijfwijze-varianten van hetzelfde merk worden samengevoegd: de feeds
    leveren "AEG" naast "Aeg" en "Samsung" naast "SAMSUNG", wat de zijbalk
    twee vinkjes voor één merk gaf met allebei een te laag aantal. Het
    filteren zelf was al hoofdletter-ongevoelig (Product.brand.ilike), dus
    "AEG (33)" leverde in werkelijkheid alle 40 AEG-producten op — de
    getoonde aantallen logen, de resultaten niet.
    """
    per_merk = defaultdict(lambda: {'casing': Counter(), 'aantal': 0})
    for product in products:
        naam = (product.brand or '').strip()
        if not naam:
            continue
        sleutel = naam.lower()
        per_merk[sleutel]['casing'][naam] += 1
        per_merk[sleutel]['aantal'] += 1

    facet = [
        {'value': canonical_brand(sleutel, data['casing']), 'count': data['aantal']}
        for sleutel, data in per_merk.items()
    ]
    facet.sort(key=lambda b: (-b['count'], b['value'].lower()))
    return facet


# Kleur is het enige spec-veld waar de feeds structureel rommel in leveren:
# naast "Wit" en "wit" staan er varianten waarin de capaciteit ("Wit/Zwart
# 9kg Autodose") of zelfs een korting ("Zwart - -30%") in het kleurveld is
# beland. Tien "kleuren" voor 46 wasmachines, terwijl witgoed in de praktijk
# wit, zwart of rvs is. We bucketen op trefwoord i.p.v. op exacte waarde.
# De feeds spellen kleuren ook in het Engels en Duits ("Stainless steel",
# "Manhattan Gray", "Schwarz"). Metaallook-woorden (chrome, metallic, stone)
# vallen onder rvs: dat is wat een koper bedoelt als hij "rvs" zoekt.
_KLEUR_TREFWOORDEN = (
    ('RVS / Inox', ('rvs', 'inox', 'roestvrij', 'stainless', 'chrome', 'chroom',
                    'metallic', 'metaal', 'stone')),
    ('Zwart', ('zwart', 'black', 'antraciet', 'schwarz')),
    ('Wit', ('wit', 'white', 'weiss', 'weiß')),
    ('Grijs', ('grijs', 'zilver', 'silver', 'gray', 'grey')),
)

# Kleuren die te weinig voorkomen voor een eigen filterregel, maar wél een
# kleur zijn: die horen in Overig. Staat er geen enkel kleurwoord in de
# waarde, dan is het geen kleur maar feedrommel ("nvt", "12 liter inhoud")
# en krijgt het product helemaal geen kleur -- wie op Overig klikt hoort
# apparaten met een afwijkende kleur te zien, niet met een kapot veld.
_KLEUR_OVERIGE_WOORDEN = (
    'groen', 'green', 'beige', 'blauw', 'blue', 'turquoise', 'oranje', 'orange',
    'bronze', 'brons', 'rood', 'red', 'geel', 'yellow', 'roze', 'pink', 'paars',
    'purple', 'goud', 'gold', 'koper', 'copper', 'bruin', 'brown', 'creme',
    'crème', 'ivoor', 'ivory',
)
_KLEUR_OVERIG = 'Overig'


def _is_kleur_spec(key):
    return 'kleur' in key.lower()


def normaliseer_kleur(waarde):
    """Kleurwaarde -> verzameling buckets. Meerwaardig, want tweekleurig.

    'Zwart - -30%'      -> {'Zwart'}          (ruis eromheen verdwijnt)
    'Wit/Zwart 9kg'     -> {'Wit', 'Zwart'}   (in beide filters te vinden)
    'Zilver en zwart'   -> {'Grijs', 'Zwart'}
    'Groen'             -> {'Overig'}         (kleur, te zeldzaam voor eigen regel)
    '12 liter inhoud'   -> set()              (geen kleur: product krijgt er geen)

    Bewust geen split op scheidingstekens: de feeds gebruiken /, komma,
    puntkomma, "en" én een kale spatie ("Wit Zwart"). Alle kleurwoorden in de
    hele waarde opzoeken vangt die varianten allemaal in één keer.
    """
    tekst = str(waarde or '').lower()
    gevonden = {naam for naam, trefwoorden in _KLEUR_TREFWOORDEN
                if any(tw in tekst for tw in trefwoorden)}
    if gevonden:
        return gevonden
    if any(woord in tekst for woord in _KLEUR_OVERIGE_WOORDEN):
        return {_KLEUR_OVERIG}
    return set()


def expand_spec_values(spec_facets, key, gekozen):
    """Vertaal getoonde filterwaarden terug naar wat er in de database staat.

    Voor de meeste facetten is dat één-op-één, maar bij Kleur staat er achter
    "Wit" een reeks ruwe waarden ("Wit", "wit"). Zonder deze vertaling zou
    een klik op "Wit" alleen de exacte "Wit"-rijen vinden en zou het filter
    opnieuw liegen, nu over zijn resultaten in plaats van zijn aantallen.
    """
    facet = next((f for f in spec_facets if f['key'] == key), None)
    if not facet:
        return gekozen
    ruw = []
    for waarde in gekozen:
        optie = next((o for o in facet['options'] if o['value'] == waarde), None)
        ruw.extend(optie['raw'] if optie else [waarde])
    return ruw


def compute_spec_facets(products, max_filters=6, max_options=None):
    """Derive the most common spec fields across the given products.

    Returns a list of {'key': str, 'options': [{'value', 'count', 'raw'}]},
    ordered by how many products have that spec key (most common first).
    Only the top `max_filters` keys are returned.

    `max_options` stond op 10 en kapte de waardenlijst stil af: de zijbalk
    toonde tien "kleuren" zonder te melden dat er meer waren, en een filter
    dat een deel van zijn eigen assortiment verzwijgt geeft verkeerde
    antwoorden. Standaard nu ongelimiteerd; de sjabloon toont de eerste zes
    met een "Meer (n)"-knop, zodat de zijbalk kort blijft zonder te liegen.

    `raw` bevat de oorspronkelijke databasewaarden achter een optie. Voor de
    meeste facetten is dat de waarde zelf; bij Kleur zitten er meerdere ruwe
    schrijfwijzen achter één knop (zie normaliseer_kleur).
    """
    key_frequency = Counter()
    value_counts = defaultdict(Counter)

    for product in products:
        specs = product.specs or {}
        for key, value in specs.items():
            if not value or _is_excluded_spec(key):
                continue
            key_frequency[key] += 1
            value_counts[key][value] += 1

    ordered = [key for key, _ in key_frequency.most_common()]
    # Ruisgroepen weren (designrapport 6 aug, punt 3): een veld als
    # "Product gewicht" levert 29 opties waarvan 24 met telling 1 --
    # niemand kiest een wasmachine op 71,50 kg, en elke optie is
    # scrollafstand tussen de bezoeker en het filter dat hij wél zoekt.
    # De regel: heeft een veld vijf of meer opties en staat meer dan de
    # helft daarvan op telling 1, dan is het geen filter maar een
    # eigenschappenlijst. Prioriteitsvelden (vulgewicht, energielabel...)
    # blijven altijd staan; die stappen zijn met de hand ingedeeld.
    def is_ruis(key):
        # Kleur is de uitzondering: de rúwe waarden zijn bijna allemaal
        # uniek ("Wit/Zwart 9kg Autodose"), maar na normaliseer_kleur
        # blijven er een paar echte knoppen over (Wit, Zwart, RVS).
        if _is_priority_spec(key) or _is_kleur_spec(key):
            return False
        tellingen = list(value_counts[key].values())
        if len(tellingen) < 5:
            return False
        return sum(1 for n in tellingen if n == 1) > len(tellingen) / 2

    ordered = [key for key in ordered if not is_ruis(key)]
    priority = sorted([key for key in ordered if _is_priority_spec(key)], key=_priority_rank)
    rest = [key for key in ordered if key not in priority]
    top_keys = (priority + rest)[:max_filters]

    facets = []
    for key in top_keys:
        if _is_kleur_spec(key):
            gebucket = defaultdict(lambda: {'aantal': 0, 'raw': []})
            for waarde, aantal in value_counts[key].items():
                # Meerwaardig: een tweekleurig apparaat telt in beide filters,
                # zodat het opduikt of je nu op Wit of op Zwart zoekt. Een
                # lege verzameling betekent "geen kleur" en valt dus weg.
                for naam in normaliseer_kleur(waarde):
                    gebucket[naam]['aantal'] += aantal
                    gebucket[naam]['raw'].append(waarde)
            options = [{'value': naam, 'count': data['aantal'], 'raw': data['raw']}
                       for naam, data in gebucket.items()]
            # Overig hoort onderaan, ook als het toevallig veel producten telt.
            options.sort(key=lambda o: (o['value'] == _KLEUR_OVERIG, -o['count'], o['value']))
        else:
            counted = value_counts[key].most_common(max_options)
            if _is_priority_spec(key):
                # Oplopend i.p.v. "meeste eerst": energielabel A boven G,
                # toerental 1200 vóór 1600.
                counted = sorted(counted, key=lambda vc: _waarde_sorteersleutel(vc[0]))
            options = [{'value': value, 'count': count, 'raw': [value]} for value, count in counted]
        if max_options:
            options = options[:max_options]
        # 'key' blijft de feednaam: daarop wordt gefilterd en die staat in de
        # URL. 'label' is puur wat de bezoeker leest.
        facets.append({'key': key, 'label': weergavenaam(key), 'options': options})

    # Twee velden met dezelfde weergavenaam is erger dan een lelijke feednaam:
    # wasdroogcombinaties hebben zowel 'Laadvermogen wasmachine' als
    # 'Laadvermogen wasdroger', en die stonden allebei als "Vulgewicht" in de
    # zijbalk -- twee identieke koppen met verschillende opties, precies het
    # soort filter dat niet meer uit te leggen is. Botsen ze, dan vallen ze
    # allebei terug op hun feednaam; die is lelijk maar ondubbelzinnig.
    dubbel = {f['label'] for f in facets
              if sum(1 for g in facets if g['label'] == f['label']) > 1}
    for facet in facets:
        if facet['label'] in dubbel:
            facet['label'] = facet['key']

    return facets


def compute_global_brand_index(brand_counts):
    """brand_counts: iterable van (merknaam, aantal) — bv. uit een SQL
    GROUP BY over alle categorieën heen. Voegt schrijfwijze-varianten
    samen (AEG/Aeg/aeg) tot één merk met de vaakst voorkomende
    schrijfwijze als weergavenaam. Sorteert alfabetisch."""
    per_merk = defaultdict(lambda: {'casing': Counter(), 'aantal': 0})
    for naam, aantal in brand_counts:
        naam = (naam or '').strip()
        if not naam:
            continue
        key = naam.lower()
        per_merk[key]['casing'][naam] += aantal
        per_merk[key]['aantal'] += aantal

    resultaat = []
    for sleutel, data in per_merk.items():
        weergavenaam = canonical_brand(sleutel, data['casing'])
        resultaat.append({'naam': weergavenaam, 'slug': slugify(weergavenaam), 'aantal': data['aantal']})
    resultaat.sort(key=lambda m: m['naam'].lower())
    return resultaat


def slugify(value):
    """'AEG' -> 'aeg', 'Miele & Co' -> 'miele-co'. Voor merk-/spec-facet-URL's
    (/category/wasmachines/merk/aeg) — geen externe dependency nodig voor
    de eenvoudige, grotendeels ASCII merknamen die de feeds leveren."""
    slug = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    return slug


def foto_url(url, breedte=400):
    """Winkelfoto via de verkleinservice wsrv.nl, als exact vierkant canvas.

    Eén bron voor de |foto-sjabloonfilter (app.py) én de Merchant
    Center-feed. Hier en niet in app.py, zodat de feed hem zonder
    Flask-import kan gebruiken en beide plekken gegarandeerd hetzelfde
    adres bouwen.

    Waarom de feed óók via wsrv moet (gemeten 12 aug): de fotoserver van
    Coolblue (coolblue.bynder.com) verbiedt in robots.txt álle crawlers.
    Googlebot-Image mocht daardoor 1.049 feedfoto's niet ophalen en
    Merchant Center keurde die producten af met "kan geen kwaliteits- en
    beleidscontroles uitvoeren". wsrv.nl staat Googlebot wél toe (alleen
    AI-trainingsbots geweerd) en is precies wat onze eigen pagina's al
    aan bezoekers serveren.
    """
    from urllib.parse import quote
    if not url or not str(url).startswith(('http://', 'https://')):
        return url
    origineel = quote(str(url), safe='')
    return (f"https://wsrv.nl/?url={origineel}&w={breedte}&h={breedte}"
            f"&fit=contain&cbg=white&output=webp&q=80&default={origineel}")


# Tekens die een webadres structureel breken: % begint een ontsnappingscode
# ("%--" is ongeldig en gaf een serverfout op 8 productpagina's, gevonden via
# Search Console op 4 augustus), en # ? & knippen het pad af. Meer niet:
# bestaande adressen met haakjes of apostrofs werken en zijn geïndexeerd,
# agressiever schoonmaken zou duizenden werkende adressen wijzigen.
URL_BREKERS = '%#?&'


def product_slug(title, ean):
    """Webadres voor een productpagina, zoals de syncs hem altijd bouwden
    (eerste 50 tekens van de titel, kleine letters, spatie en / worden een
    streepje) — maar zonder de tekens die een URL breken."""
    kaal = (title or '')[:50].lower().replace(' ', '-').replace('/', '-')
    kaal = re.sub(f'[{re.escape(URL_BREKERS)}]', '-', kaal)
    return f"{kaal}-{ean}"


def parse_spec_filters(raw_values):
    """Parse ['Merk::Bosch', 'Vulgewicht::9 kg'] into {'Merk': ['Bosch'], 'Vulgewicht': ['9 kg']}."""
    parsed = defaultdict(list)
    for raw in raw_values:
        if '::' not in raw:
            continue
        key, value = raw.split('::', 1)
        if key and value:
            parsed[key].append(value)
    return dict(parsed)
