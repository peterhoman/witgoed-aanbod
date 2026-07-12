"""Geschatte stroomkosten per jaar, berekend uit de energielabel-specs.

De winkel-feeds leveren de officiële energielabel-gegevens mee in de
product-specs. Daar rekenen we een jaarbedrag uit — informatie die de
winkels zelf niet tonen en die bij witgoed vaak belangrijker is dan het
prijsverschil tussen twee modellen:

- Koelkasten/vriezers: "Jaarlijks energieverbruik in kWh" (staat 24/7 aan,
  fabrieksopgave per jaar) -> direct te gebruiken.
- Wasmachines, vaatwassers, drogers, wasdroogcombinaties:
  "Energieverbruik per 100 cycli" (EU-label 2021) -> omrekenen met een
  aanname voor het aantal beurten per jaar (ordegrootte Milieu Centraal).

De aannames staan bewust op de pagina vermeld: het is een schatting om
modellen onderling te vergelijken, geen energierekening-voorspelling.
"""
import re

# Gemiddeld Nederlands stroomtarief; bewust conservatief afgerond.
STROOMPRIJS = 0.30  # euro per kWh

# Aantal beurten per jaar per categorie (alleen categorieën met het
# "per 100 cycli"-label; ordegroottes zoals Milieu Centraal hanteert).
BEURTEN_PER_JAAR = {
    'wasmachines': 200,
    'vaatwassers': 220,
    'drogers': 150,
    'wasdroogcombinaties': 150,  # volledige was+droog-cycli
}

_GETAL = re.compile(r'(\d+(?:[.,]\d+)?)')

# Officiële EU-energielabelkleuren (A groen -> G rood); donkere tekst op
# de gele/lichte middenklassen voor leesbaarheid.
LABEL_KLEUREN = {
    'A': ('#00a651', '#ffffff'),
    'B': ('#50b848', '#ffffff'),
    'C': ('#bfd730', '#212529'),
    'D': ('#fff200', '#212529'),
    'E': ('#fdb913', '#212529'),
    'F': ('#f37021', '#ffffff'),
    'G': ('#ed1c24', '#ffffff'),
}


def _kwh(waarde):
    """'40 kWh' / '6.5' / '0,75 kWh' -> float, anders None."""
    if waarde is None:
        return None
    m = _GETAL.search(str(waarde))
    return float(m.group(1).replace(',', '.')) if m else None


def _euro(bedrag):
    s = f"{bedrag:,.0f}".replace(',', '.')
    return s


def bereken_energiekosten(product):
    """Geeft een dict voor de stroomkosten-weergave, of None zonder data."""
    specs = product.specs or {}
    slug = product.category.slug if product.category else ''

    label = None
    for sleutel in ('Waarde energielabel', 'Energie-efficiëntieklasse',
                    'Energieklasse'):
        if specs.get(sleutel):
            label = str(specs[sleutel]).strip()
            break

    jaar_kwh = None
    basis = None

    # 1. Directe jaaropgave (koelkasten, vriezers)
    for sleutel in ('Jaarlijks energieverbruik in kWh',
                    'Jaarlijks energieverbruik', 'Energieverbruik per jaar'):
        v = _kwh(specs.get(sleutel))
        if v:
            jaar_kwh = v
            basis = 'fabrieksopgave per jaar'
            break

    # 2. EU-label "per 100 cycli" (was/vaat/droog)
    if jaar_kwh is None:
        beurten = BEURTEN_PER_JAAR.get(slug)
        v = _kwh(specs.get('Energieverbruik per 100 cycli'))
        if v and beurten:
            jaar_kwh = v / 100.0 * beurten
            basis = f'{beurten} beurten per jaar'

    if jaar_kwh is None or jaar_kwh <= 0:
        return None

    jaar_kosten = jaar_kwh * STROOMPRIJS
    # Labelkleur op de eerste letter (waardes als "A+++" of "a" vangen we af)
    letter = (label or '').strip().upper()[:1]
    kleur, tekstkleur = LABEL_KLEUREN.get(letter, ('#6c757d', '#ffffff'))
    return {
        'label': label,
        'label_kleur': kleur,
        'label_tekstkleur': tekstkleur,
        'jaar_kwh': round(jaar_kwh),
        'jaar_kosten': _euro(jaar_kosten),
        'vijf_jaar_kosten': _euro(jaar_kosten * 5),
        'basis': basis,
        'stroomprijs': f"{STROOMPRIJS:.2f}".replace('.', ','),
    }
