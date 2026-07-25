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
    # Kosten over tien jaar: aanschafprijs plus stroom. Dit is het cijfer dat
    # een webshop niet geeft — een apparaat van honderd euro meer kan over de
    # levensduur goedkoper zijn. Zonder prijs alleen de stroomkosten.
    aanschaf = product.lowest_price
    tien_jaar_stroom = jaar_kosten * 10
    tien_jaar_totaal = (aanschaf + tien_jaar_stroom) if aanschaf else None

    return {
        'label': label,
        'label_kleur': kleur,
        'label_tekstkleur': tekstkleur,
        'jaar_kwh': round(jaar_kwh),
        'jaar_kosten': _euro(jaar_kosten),
        'vijf_jaar_kosten': _euro(jaar_kosten * 5),
        'tien_jaar_kosten': _euro(tien_jaar_totaal) if tien_jaar_totaal else None,
        'tien_jaar_bevat_aanschaf': bool(aanschaf),
        'meerkosten_slechter_label': _meerkosten_slechter_label(slug, label, jaar_kwh),
        'basis': basis,
        'stroomprijs': f"{STROOMPRIJS:.2f}".replace('.', ','),
    }


# Gemiddeld kWh-verbruik per energielabel, per categorie: het cijfer dat de
# vergelijking "label D kost € 380 meer over tien jaar" mogelijk maakt.
# Gevuld vanuit de eigen catalogus en gecachet, want dit verandert alleen als
# de syncs draaien.
_LABEL_CACHE = {}
_LABEL_TTL = 3600


def _gemiddeld_kwh_per_label(slug):
    """{'A': 48.0, 'D': 121.0, ...} voor deze categorie, uit de eigen data."""
    import time
    nu = time.time()
    hit = _LABEL_CACHE.get(slug)
    if hit and nu - hit[0] < _LABEL_TTL:
        return hit[1]

    from models import Category, Product
    per_label = {}
    categorie = Category.query.filter_by(slug=slug).first()
    if categorie:
        for p in Product.query.filter_by(category_id=categorie.id, is_available=True).all():
            specs = p.specs or {}
            letter = str(specs.get('Waarde energielabel') or '').strip().upper()[:1]
            if not letter:
                continue
            kwh = _kwh(specs.get('Jaarlijks energieverbruik in kWh'))
            if kwh is None:
                beurten = BEURTEN_PER_JAAR.get(slug)
                per_100 = _kwh(specs.get('Energieverbruik per 100 cycli'))
                kwh = (per_100 / 100.0 * beurten) if (per_100 and beurten) else None
            if kwh and kwh > 0:
                per_label.setdefault(letter, []).append(kwh)

    gemiddeld = {letter: sum(v) / len(v) for letter, v in per_label.items()}
    _LABEL_CACHE[slug] = (nu, gemiddeld)
    return gemiddeld


def _meerkosten_slechter_label(slug, label, jaar_kwh):
    """Wat een slechter gelabeld apparaat over tien jaar extra kost.

    Geeft {'label': 'D', 'bedrag': '380'} of None. Zonder eigen meetpunten
    voor dat label geven we niets terug — liever geen vergelijking dan een
    verzonnen vergelijking.
    """
    letter = (label or '').strip().upper()[:1]
    if not letter or letter not in 'ABCDEFG':
        return None
    gemiddeld = _gemiddeld_kwh_per_label(slug)
    # Het eerstvolgende slechtere label waarvoor we genoeg data hebben.
    for slechter in 'ABCDEFG'[('ABCDEFG'.index(letter) + 1):]:
        ander_kwh = gemiddeld.get(slechter)
        if not ander_kwh or ander_kwh <= jaar_kwh:
            continue
        verschil = (ander_kwh - jaar_kwh) * STROOMPRIJS * 10
        if verschil >= 25:  # onder de 25 euro is het geen argument
            return {'label': slechter, 'bedrag': _euro(verschil)}
    return None
