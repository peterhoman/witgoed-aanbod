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
_EXCLUDED_SPEC_KEYWORDS = ('verpakking', 'mpn', 'model', 'toerental aanpasbaar')

# Filters waar bezoekers echt op zoeken krijgen voorrang: die komen direct
# na het merkblok, ook als andere specs vaker voorkomen — in déze volgorde
# (energielabel eerst, dan toerental). De waarden van deze filters sorteren
# we oplopend (energielabel A t/m G, toerental 1200 vóór 1600) i.p.v. op aantal.
_PRIORITY_SPEC_KEYWORDS = ('energielabel', 'toerental')


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


def compute_spec_facets(products, max_filters=6, max_options=10):
    """Derive the most common spec fields across the given products.

    Returns a list of {'key': str, 'options': [{'value': str, 'count': int}]},
    ordered by how many products have that spec key (most common first).
    Only the top `max_filters` keys are returned, each capped at `max_options`
    distinct values (also sorted by count desc).
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
    priority = sorted([key for key in ordered if _is_priority_spec(key)], key=_priority_rank)
    rest = [key for key in ordered if key not in priority]
    top_keys = (priority + rest)[:max_filters]

    facets = []
    for key in top_keys:
        counted = value_counts[key].most_common(max_options)
        if _is_priority_spec(key):
            # Oplopend i.p.v. "meeste eerst": energielabel A boven G,
            # toerental 1200 vóór 1600.
            counted = sorted(counted, key=lambda vc: _waarde_sorteersleutel(vc[0]))
        options = [{'value': value, 'count': count} for value, count in counted]
        facets.append({'key': key, 'options': options})

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
