"""Waar dit apparaat staat tussen de andere apparaten in zijn categorie.

Waarom dit bestaat
------------------
Google beoordeelde 449 van onze pagina's en sloeg er 100 over met de reden
"gecrawld, momenteel niet geïndexeerd". Dat is een oordeel over de inhoud, niet
over de links: zo'n pagina bevat een titel, een prijs, een knop en de
beschrijving van de leverancier — en die beschrijving staat woordelijk ook bij
Bol en bij de fabrikant.

Wat wél alleen hier staat, is onze eigen meting over de hele categorie. "Van de
255 wasmachines die wij volgen loopt de prijs van € 239 tot € 4.849" komt uit
onze catalogus en nergens anders vandaan. Het werkt bovendien op élke
productpagina — ook op de 65% zonder specificaties en de 57% met één winkel,
precies de pagina's die Google te dun vindt.

De regel die boven alles gaat
-----------------------------
Elk onderdeel verdwijnt zodra de data ontbreekt. Er wordt niets geschat en er
staat nergens "onbekend". De prijszinnen kunnen altijd (elk product heeft een
prijs), de label- en formaatzin alleen waar dat veld écht gevuld is — bij
wasmachines is dat 46 van de 255.

Twee valkuilen uit de productiedata, allebei gemeten via
/api/category-specs/<slug> voordat hier iets op gebouwd is:

- Ovens hebben als energielabel de waarde "Energielabel niet van toepassing".
  Wie daar de eerste letter van pakt, telt dat als label E en verzint een
  vergelijking. Daarom accepteert energielabel_letter (filter_helpers) alleen een kale
  letter A t/m G; die regel wordt ook door de sitemap en de facetpagina's
  gebruikt.
- Zestien magnetrons hebben "0 W" als ovenvermogen. Dat is een leeg veld, geen
  meting, en het zou de laagste waarde van de categorie worden.
"""
import math
import re
import time
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict

from filter_helpers import ENERGIELADDER, energielabel_letter
from product_specs import FORMAAT_VELD

# Zelfde patroon en TTL als _category_facets in routes/main.py: dit verandert
# alleen als de syncs draaien, en gunicorn draait met één worker dus een
# procescache volstaat.
_CACHE = {}
_TTL = 15 * 60  # seconden

# Onder dit aantal producten zegt een positie niets: "duurder dan 4 van de 6"
# is ruis, geen bevinding.
_MIN_CATEGORIE = 12

# Per spec-veld: onder dit aantal metingen is de noemer te dun om een uitspraak
# op te baseren.
_MIN_GEMETEN = 20

# Merkzin: onder vijf modellen van hetzelfde merk is de vergelijking te klein.
_MIN_MERK = 5

# Heeft vrijwel de hele categorie dezelfde waarde, dan onderscheidt die niets.
# Bij wasmachines heeft 45 van de 46 gemeten modellen label A; "hoort bij de 45
# zuinigste van de 46" is waar maar zegt niets, en zulke zinnen zijn precies wat
# een pagina dun maakt.
_MAX_AANDEEL = 0.9

_LADDER = ENERGIELADDER
_GETAL = re.compile(r'\s*(\d+(?:[.,]\d+)?)')

# Hoe het formaatveld van de categorie (FORMAAT_VELD, zie product_specs) in een
# lopende zin heet: als kop van de zin en als verwijzing halverwege. De ruwe
# feednaam ("Laadvermogen wasmachine") leest niet als Nederlands, en het lidwoord
# hoort erbij omdat het per veld verschilt -- "de inhoud" naast "het vulgewicht".
_FORMAAT_WOORD = {
    'Laadvermogen wasmachine': ('Vulgewicht', 'het vulgewicht'),
    'Laadvermogen wasdroger': ('Vulgewicht', 'het vulgewicht'),
    'Volume in liters': ('Inhoud', 'de inhoud'),
    'Aantal couverts': ('Aantal couverts', 'het aantal couverts'),
    'Ovenvermogen': ('Ovenvermogen', 'het ovenvermogen'),
}


def _euro(bedrag, afronding=round):
    """549.4 -> '549', 4849.0 -> '4.849'. Zonder centen: dit zijn grenzen en
    ordegroottes, en '4.849,00' leest in een lopende zin als ruis.

    `afronding` is math.floor voor de onderkant van een prijsbereik en
    math.ceil voor de bovenkant. Anders zou "loopt van € 240 tot € 4.849" een
    apparaat van € 239,50 buitensluiten -- een kleine onwaarheid, maar wel een
    over onze eigen meting.
    """
    try:
        return f"{int(afronding(float(bedrag))):,}".replace(',', '.')
    except (TypeError, ValueError):
        return str(bedrag)


def _euro_exact(bedrag):
    """1299.5 -> '1.299,50'. Voor de prijs van dit apparaat zelf: die staat
    even verderop op de pagina en moet daar op de cent mee overeenkomen."""
    try:
        return f"{float(bedrag):,.2f}".replace(',', ' ').replace('.', ',').replace(' ', '.')
    except (TypeError, ValueError):
        return str(bedrag)


def _getal(waarde):
    """'9 kg' -> 9.0, '10.5 kg' -> 10.5, '0 W' -> None.

    Nul telt niet als meting: zestien magnetrons hebben "0 W" als ovenvermogen
    en dat is een leeg veld. Zonder deze grens wordt dat de laagste waarde van
    de categorie en klopt elke vergelijking eronder niet meer.
    """
    if waarde is None:
        return None
    m = _GETAL.match(str(waarde))
    if not m:
        return None
    getal = float(m.group(1).replace(',', '.'))
    return getal if getal > 0 else None


def _bouw_profiel(category_id, slug):
    """De meting over één categorie: prijzen, labels en formaten, gesorteerd.

    Alleen de drie kolommen die we nodig hebben, geen volledige productrijen:
    koelkasten zijn 566 records inclusief beschrijvingsteksten en daar hebben we
    hier niets aan (zelfde afweging als _gemiddeld_kwh_per_label).
    """
    from models import db, Product

    veld = FORMAAT_VELD.get(slug)
    rijen = (db.session.query(Product.price, Product.brand, Product.specs)
             .filter(Product.category_id == category_id,
                     Product.is_available.is_(True))
             .all())

    prijzen, labels, formaten = [], Counter(), []
    per_merk = defaultdict(list)
    for prijs, merk, specs in rijen:
        try:
            prijs = float(prijs)
        except (TypeError, ValueError):
            prijs = 0.0
        if prijs > 0:
            prijzen.append(prijs)
            sleutel = (merk or '').strip().lower()
            if sleutel:
                per_merk[sleutel].append(prijs)

        specs = specs or {}
        letter = energielabel_letter(specs.get('Waarde energielabel'))
        if letter:
            labels[letter] += 1
        if veld:
            getal = _getal(specs.get(veld))
            if getal is not None:
                formaten.append(getal)

    prijzen.sort()
    formaten.sort()
    for lijst in per_merk.values():
        lijst.sort()

    return {
        'prijzen': prijzen,
        'labels': labels,
        'labels_gemeten': sum(labels.values()),
        'formaat_veld': veld,
        'formaten': formaten,
        'per_merk': dict(per_merk),
    }


def _profiel(category_id, slug):
    nu = time.time()
    hit = _CACHE.get(category_id)
    if hit and nu - hit[0] < _TTL:
        return hit[1]
    data = _bouw_profiel(category_id, slug)
    _CACHE[category_id] = (nu, data)
    return data


def _prijszinnen(product, profiel, categorie_naam, meegeteld):
    """De prijspositie en de spreiding van de categorie."""
    prijzen = profiel['prijzen']
    totaal = len(prijzen)
    zinnen = []

    # De positiezin vervalt bij een niet-leverbaar apparaat: de pagina toont
    # daar geen prijs (het aanbiedingenblok staat achter is_available), en dan
    # hoort er ook geen prijs in de tekst te staan.
    if meegeteld:
        prijs = float(product.lowest_price or 0)
        andere = totaal - 1
        duurder = totaal - bisect_right(prijzen, prijs)
        goedkoper = bisect_left(prijzen, prijs)
        if duurder == 0:
            zinnen.append(f"Dit model kost € {_euro_exact(prijs)}; geen ander apparaat "
                          f"in deze categorie is duurder.")
        elif goedkoper == 0:
            zinnen.append(f"Dit model kost € {_euro_exact(prijs)}; geen ander apparaat "
                          f"in deze categorie is goedkoper.")
        else:
            zinnen.append(f"Dit model kost € {_euro_exact(prijs)}: van de {andere} andere "
                          f"{categorie_naam} die wij volgen zijn er {duurder} duurder "
                          f"en {goedkoper} goedkoper.")

    # De spreiding staat er altijd, ook bij een niet-leverbaar apparaat: dat is
    # een uitspraak over de categorie, niet over dit product.
    p25 = prijzen[int(totaal * 0.25)]
    p75 = prijzen[int(totaal * 0.75)]
    spreiding = (f"De prijs in deze categorie loopt van "
                 f"€ {_euro(prijzen[0], math.floor)} tot "
                 f"€ {_euro(prijzen[-1], math.ceil)}")
    # Vallen de kwartielen samen, dan is "de middelste helft zit tussen € 549 en
    # € 549" geen informatie maar een rare zin.
    if p75 > p25:
        spreiding += f"; de middelste helft zit tussen € {_euro(p25)} en € {_euro(p75)}"
    zinnen.append(spreiding + '.')
    return zinnen


def _formaatzin(product, profiel, categorie_naam):
    """'Vulgewicht 9 kg: daarmee zit dit model boven 18 van de 46 ...' of None."""
    veld = profiel['formaat_veld']
    formaten = profiel['formaten']
    if not veld or len(formaten) < _MIN_GEMETEN:
        return None
    # Staat de hele categorie op dezelfde maat, dan valt er niets te plaatsen.
    if formaten[0] == formaten[-1]:
        return None

    ruw = (product.specs or {}).get(veld)
    waarde = _getal(ruw)
    if waarde is None:
        return None

    kop, verwijzing = _FORMAAT_WOORD.get(veld, (veld, 'dit veld'))
    lager = bisect_left(formaten, waarde)
    # De ruwe waarde ("9 kg") gaat mee zoals de feed hem levert: die bevat de
    # eenheid, en die zelf samenstellen is precies het gokken dat we niet doen.
    tekst = str(ruw).strip()
    # "boven 0 van de 28" is dezelfde lege mededeling als de "+ € 0,00" die
    # eerder bij gelijke winkelprijzen is opgeruimd: nul is geen positie.
    if lager == 0:
        return (f"{kop} {tekst}: dat is de laagste waarde die wij bij de "
                f"{len(formaten)} gemeten {categorie_naam} tegenkomen.")
    return (f"{kop} {tekst}: daarmee zit dit model boven {lager} van de "
            f"{len(formaten)} {categorie_naam} waarvan wij {verwijzing} kennen.")


def _labelzin(product, profiel, categorie_naam):
    """'Energielabel C: daarmee hoort dit model bij de 46 zuinigste ...' of None."""
    labels = profiel['labels']
    gemeten = profiel['labels_gemeten']
    if gemeten < _MIN_GEMETEN:
        return None

    letter = energielabel_letter((product.specs or {}).get('Waarde energielabel'))
    if not letter:
        return None

    eigen = labels.get(letter, 0)
    beter = sum(aantal for lab, aantal in labels.items()
                if _LADDER.index(lab) < _LADDER.index(letter))
    zuiniger_of_gelijk = beter + eigen

    # Onderdrukken alleen als dít label vrijwel de hele categorie is: dan
    # onderscheidt het niets. Bij wasmachines heeft 45 van de 46 gemeten
    # modellen label A -- "bij de 45 zuinigste van de 46" is waar en zinloos.
    #
    # Bewust op het eigen label en niet op de groep "gelijk of zuiniger". Die
    # groep is bij het slechtste label van een categorie per definitie 100%,
    # waardoor ook koelkasten met label E hun zin kwijtraakten -- terwijl daar
    # juist iets te zeggen valt, alleen andersom (zie hieronder).
    if eigen / gemeten > _MAX_AANDEEL:
        return None

    staart = f"van de {gemeten} {categorie_naam} waarvan wij het label kennen"

    if beter == 0:
        return (f"Energielabel {letter}: dat is het beste label in deze "
                f"categorie; {eigen} {staart} halen het.")
    # Zit meer dan de helft van de categorie op of boven dit label, dan is
    # "hoort bij de 106 zuinigste van de 106" geen mededeling. Omgekeerd
    # geformuleerd staat er wel iets: hoeveel modellen zuiniger zijn. Dat is
    # precies wat een koper van een zuinig apparaat wil weten.
    if zuiniger_of_gelijk / gemeten > 0.5:
        return f"Energielabel {letter}: {beter} {staart} zijn zuiniger."
    return (f"Energielabel {letter}: daarmee hoort dit model bij de "
            f"{zuiniger_of_gelijk} zuinigste {staart}.")


def _merkzin(product, profiel, categorie_naam):
    """'Wij volgen 63 wasmachines van Bosch; 41 daarvan zijn duurder.' of None."""
    merk = (product.brand or '').strip()
    prijzen = profiel['per_merk'].get(merk.lower()) if merk else None
    if not prijzen or len(prijzen) < _MIN_MERK:
        return None

    prijs = float(product.lowest_price or 0)
    duurder = len(prijzen) - bisect_right(prijzen, prijs)
    if duurder == 0:
        return (f"Wij volgen {len(prijzen)} {categorie_naam} van {merk}; dit is "
                f"de duurste daarvan.")
    return (f"Wij volgen {len(prijzen)} {categorie_naam} van {merk}; {duurder} "
            f"daarvan zijn duurder dan dit model.")


def bepaal_categoriecontext(product):
    """Zinnen over de plaats van dit apparaat in zijn categorie, of None.

    Geeft {'kop', 'tekst', 'voet'} terug. `tekst` is één alinea: het gaat om
    inhoud die gelezen wordt, niet om een dashboard met losse cijfers.

    None bij een te kleine categorie — dan is elke positie ruis.
    """
    categorie = product.category
    if categorie is None:
        return None

    profiel = _profiel(categorie.id, categorie.slug)
    totaal = len(profiel['prijzen'])
    if totaal < _MIN_CATEGORIE:
        return None

    naam = categorie.name.lower()
    # Een niet-leverbaar apparaat zit niet in de meting; dan is elk ander
    # product een "ander product" en klopt totaal - 1 niet.
    meegeteld = bool(product.is_available)

    zinnen = _prijszinnen(product, profiel, naam, meegeteld)
    for zin in (_formaatzin(product, profiel, naam),
                _labelzin(product, profiel, naam)):
        if zin:
            zinnen.append(zin)
    if meegeteld:
        merkzin = _merkzin(product, profiel, naam)
        if merkzin:
            zinnen.append(merkzin)

    return {
        'kop': f"Waar dit model staat tussen {totaal} {naam}",
        'tekst': ' '.join(zinnen),
        'voet': (f"Berekend over alle {totaal} leverbare {naam} op deze site, "
                 f"bijgewerkt bij elke sync."),
    }
