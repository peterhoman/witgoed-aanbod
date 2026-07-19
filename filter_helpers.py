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


def compute_brand_facet(products):
    """Return a list of {'value': brand, 'count': n} sorted by count desc, then name."""
    counts = Counter(p.brand for p in products if p.brand)
    return [
        {'value': brand, 'count': count}
        for brand, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]


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
    for data in per_merk.values():
        weergavenaam = data['casing'].most_common(1)[0][0]
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
