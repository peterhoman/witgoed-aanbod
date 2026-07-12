"""
Helpers to derive filterable facets (brand, specs) from a list of products.

These are pure functions (no Flask/DB dependencies) so they can be tested
in isolation with plain lists of objects that have `.brand` and `.specs`.
"""

from collections import Counter, defaultdict

# Specs die bol.com wel meelevert maar die niemand gebruikt om op te
# filteren: verpakkingsmaten/-gewicht (niet hetzelfde als het gewicht van
# het product zelf), interne artikelcodes, handleidingtaal, en de ruwe
# fabrikant-registratienaam (soms letterlijk een e-mailadres als waarde).
# 'merk' staat er ook in: de zijbalk heeft al een eigen merkfilter (op
# products.brand); de spec-variant verscheen als tweede "Merk"-blok.
_EXCLUDED_SPEC_KEYS = {'fabrikant naam', 'taal handleiding', 'merk'}
# 'model' (en varianten als modelnaam/modelnummer) is per product uniek en
# dus zinloos om op te filteren; maakte de zijbalk alleen maar langer.
_EXCLUDED_SPEC_KEYWORDS = ('verpakking', 'mpn', 'model')

# Filters waar bezoekers echt op zoeken krijgen voorrang: die komen direct
# na het merkblok, ook als andere specs vaker voorkomen. De waarden van deze
# filters sorteren we alfabetisch (energielabel A t/m G) i.p.v. op aantal.
_PRIORITY_SPEC_KEYWORDS = ('energielabel',)


def _is_priority_spec(key):
    key_lower = key.lower()
    return any(kw in key_lower for kw in _PRIORITY_SPEC_KEYWORDS)


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
    priority = [key for key in ordered if _is_priority_spec(key)]
    rest = [key for key in ordered if key not in priority]
    top_keys = (priority + rest)[:max_filters]

    facets = []
    for key in top_keys:
        counted = value_counts[key].most_common(max_options)
        if _is_priority_spec(key):
            # energielabel: A boven G is logischer dan "meeste eerst"
            counted = sorted(counted, key=lambda vc: vc[0])
        options = [{'value': value, 'count': count} for value, count in counted]
        facets.append({'key': key, 'options': options})

    return facets


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
