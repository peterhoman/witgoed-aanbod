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
_EXCLUDED_SPEC_KEYS = {'fabrikant naam', 'taal handleiding'}
_EXCLUDED_SPEC_KEYWORDS = ('verpakking', 'mpn')


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

    top_keys = [key for key, _ in key_frequency.most_common(max_filters)]

    facets = []
    for key in top_keys:
        options = [
            {'value': value, 'count': count}
            for value, count in value_counts[key].most_common(max_options)
        ]
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
