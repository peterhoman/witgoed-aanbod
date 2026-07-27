"""Eigen productbeschrijvingen laten schrijven, op basis van eigen gegevens.

Waarom dit bestaat
------------------
Google beoordeelde 449 productpagina's en sloeg er 100 over met "gecrawld,
momenteel niet geindexeerd" -- een oordeel over de inhoud. De bodytekst op zo'n
pagina is de beschrijving van de leverancier, en die staat woordelijk ook bij
Bol en bij de fabrikant. Drie van de vier bouwstenen van de pagina (titel,
meta-description, bodytekst) kwamen daarmee uit dezelfde feed.

De meta-description en het categoriecontext-blok zijn inmiddels eigen tekst
(zie category_context.py). De bodytekst is het laatste stuk dat nog van de
leverancier komt. Dit bestand vult dat gat.

Wat er is weggehaald
--------------------
De oude versie van dit bestand (nooit aangeroepen -- generate_for_product stond
in geen enkel ander bestand) had drie problemen die het onbruikbaar maakten:

- model="claude-3-5-sonnet-20241022", met anthropic==0.7.1 in requirements.txt.
  Dat model is met pensioen; die SDK-versie is van 2023.
- De prompt sloot af met de opdracht 'Sluit af met call-to-action: "Bekijk nu
  op Bol.com"'. Deze site vergelijkt zes winkels; bij 43% van de producten is
  Bol niet eens de goedkoopste, en bij een deel staat Bol er helemaal niet bij.
- De prompt kreeg alleen titel, type en merk mee. Daarmee schrijft elk
  taalmodel dezelfde tekst als elk ander taalmodel -- opnieuw dubbele inhoud,
  alleen met een andere bron. Onze eigen catalogusmeting ging er niet in.

De buying-guide- en vergelijkingsfuncties zijn eruit: ze werden nergens
aangeroepen en wezen naar hetzelfde verlopen model.

De regel die boven alles gaat
-----------------------------
Dezelfde als in category_context.py: er wordt niets geschat. Het model krijgt
uitsluitend feiten uit onze database en de opdracht om niets toe te voegen over
dit apparaat wat daar niet in staat. Waar de data dun is, hoort de tekst kort
te zijn -- een lange tekst over een product waarvan wij alleen merk en prijs
kennen is precies de opvulling die een pagina dun maakt.

Wat het model wel mag: uitleggen wat een specificatie in de praktijk betekent
("9 kg trommel" -> voor wat voor huishouden dat bedoeld is). Dat is algemene
vakkennis, geen bewering over dit exemplaar. Wat het niet mag: iets zeggen over
kwaliteit, betrouwbaarheid of prestaties van dit apparaat, want dat weten wij
niet en het zou nergens op gebaseerd zijn.
"""

import logging
import os

from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Prijs per miljoen tokens, Claude Opus 5 (stand 27-07). Alleen voor de
# kostenweergave in de proef; de echte afrekening staat in de Console.
# Bewust hier en niet in config: dit is een tarief van de leverancier, geen
# instelling van deze site.
_PRIJS_INVOER = 5.00
_PRIJS_UITVOER = 25.00
_PRIJS_CACHE_SCHRIJVEN = 6.25   # 1,25x invoer
_PRIJS_CACHE_LEZEN = 0.50       # 0,10x invoer

# Ruim boven de verwachte lengte: max_tokens is op Opus 5 een plafond over
# denkwerk en tekst samen, en denkwerk staat daar standaard aan. Te krap
# afgetopt levert een tekst die midden in een zin ophoudt.
_MAX_TOKENS = 2000

# Zoveel specificaties gaan er hoogstens mee. Koelkasten hebben er in de feed
# tot 40, waarvan de meeste ("CE-markering", "Product hoogte") niets toevoegen
# aan een lopende tekst en alleen invoertokens kosten.
_MAX_SPECS = 14

# De instructie staat apart van de productgegevens zodat hij voor elk product
# byte voor byte gelijk is. Dat is de voorwaarde voor prompt-caching: bij de
# tweede en volgende aanroep wordt dit blok voor een tiende van de prijs
# gelezen in plaats van opnieuw berekend. Over 2816 producten scheelt dat het
# grootste deel van de invoerkosten.
SYSTEEMINSTRUCTIE = """Je schrijft productteksten voor WitgoedAanbod.nl, een \
Nederlandse vergelijkingssite voor witgoed. De site vergelijkt de prijs van \
hetzelfde apparaat bij zes winkels.

Je krijgt per product uitsluitend gegevens uit onze eigen database. Schrijf \
daar een lopende tekst bij in het Nederlands.

Harde regels:

1. Verzin niets over dit apparaat. Noem geen eigenschap, functie, maat of \
programma die niet in de gegevens staat. Zeg niets over kwaliteit, \
betrouwbaarheid, zuinigheid in de praktijk, geluid of prestaties -- dat weten \
wij niet.
2. Je mag wel uitleggen wat een genoemde specificatie in de praktijk betekent. \
Bij "Laadvermogen 9 kg" mag je uitleggen voor wat voor huishouden die maat \
gangbaar is. Dat is algemene kennis over apparaten, geen bewering over dit \
exemplaar.
3. De lengte volgt de gegevens. Veel specificaties: 150 tot 250 woorden. \
Weinig of geen specificaties: 40 tot 80 woorden. Vul nooit aan met algemene \
zinnen over het merk, over waar je op moet letten bij het kopen, of over de \
categorie in het algemeen. Een korte tekst is beter dan een opgerekte.
4. Noem geen enkele winkelnaam en geen prijzen. Die staan elders op de pagina \
en wisselen per dag; in de tekst zouden ze verouderen.
5. Geen aansporing om te kopen, geen "bekijk nu", geen uitroeptekens.
6. Herhaal de catalogusmeting niet letterlijk. Die staat als apart blok op \
dezelfde pagina. De meting is er zodat jij weet waar dit apparaat staat -- \
duur of goedkoop, groot of klein voor zijn soort -- niet om over te schrijven.
7. Geen kop, geen opsomming, geen markdown. Alleen alinea's gewone tekst, \
gescheiden door een lege regel. Begin niet met de productnaam als \
aankondiging ("De Bosch WGG244FONL is een wasmachine die...") maar schrijf \
alsof de lezer al ziet welk apparaat hij voor zich heeft.
8. Schrijf zakelijk en droog. Spreek de lezer niet aan met "u" of "je"."""


def _specregels(product):
    """De specificaties die iets toevoegen, als 'Naam: waarde'-regels.

    Filtert op dezelfde manier als de specificatietabel op de pagina zelf:
    lege waarden eruit, en de administratieve velden waar een lezer niets aan
    heeft. Zie filter_helpers._EXCLUDED_SPEC_KEYWORDS voor de reden dat
    "CE-markering" en "Product hoogte" daar ook al buiten vielen.
    """
    from filter_helpers import _EXCLUDED_SPEC_KEYWORDS, weergavenaam
    from product_specs import _is_lege_waarde

    regels = []
    for sleutel, waarde in (product.specs or {}).items():
        if _is_lege_waarde(waarde):
            continue
        if any(woord in sleutel.lower() for woord in _EXCLUDED_SPEC_KEYWORDS):
            continue
        tekst = str(waarde).strip()
        # Een spec van een halve alinea is geen spec maar een stuk
        # leveranciersbeschrijving in een verkeerd veld. Die willen we juist
        # niet als bron, want dat is de tekst die we aan het vervangen zijn.
        if len(tekst) > 120:
            continue
        regels.append(f"- {weergavenaam(sleutel)}: {tekst}")
        if len(regels) >= _MAX_SPECS:
            break
    return regels


def bouw_prompt(product):
    """De gegevens van een product, als platte tekst voor het model.

    Alles komt uit onze database. De leveranciersbeschrijving gaat er bewust
    niet in: die is de tekst die we vervangen, en een model dat hem als bron
    krijgt schrijft hem in eigen woorden na. Dan hebben we geen nieuwe tekst
    maar een parafrase van dubbele inhoud.
    """
    from category_context import bepaal_categoriecontext

    delen = [f"Titel zoals de winkel hem levert: {product.title}"]
    if product.brand:
        delen.append(f"Merk: {product.brand}")
    if product.category is not None:
        delen.append(f"Categorie: {product.category.name}")
    if product.subcategory:
        delen.append(f"Soort: {product.subcategory}")

    specs = _specregels(product)
    if specs:
        delen.append("\nSpecificaties uit de winkelfeed:\n" + "\n".join(specs))
    else:
        # Expliciet benoemen, anders vult het model het gat zelf op. Dit
        # geldt voor 65% van de catalogus.
        delen.append("\nSpecificaties: geen enkele bekend. Er is over dit "
                     "apparaat niets meer bekend dan hierboven staat. Houd de "
                     "tekst navenant kort.")

    context = bepaal_categoriecontext(product)
    if context:
        delen.append("\nOnze meting over de hele categorie (niet overschrijven, "
                     "alleen ter orientatie):\n" + context['tekst'])

    return "\n".join(delen)


def _kosten(usage):
    """Wat deze ene aanroep kostte, in euro's.

    Wisselkoers bewust vast op 0,92: dit is een indicatie voor de proef, geen
    boekhouding. De echte bedragen staan in de Anthropic Console.
    """
    invoer = getattr(usage, 'input_tokens', 0) or 0
    uitvoer = getattr(usage, 'output_tokens', 0) or 0
    cache_schrijf = getattr(usage, 'cache_creation_input_tokens', 0) or 0
    cache_lees = getattr(usage, 'cache_read_input_tokens', 0) or 0
    dollar = (invoer * _PRIJS_INVOER
              + uitvoer * _PRIJS_UITVOER
              + cache_schrijf * _PRIJS_CACHE_SCHRIJVEN
              + cache_lees * _PRIJS_CACHE_LEZEN) / 1_000_000
    return {
        'invoer': invoer,
        'uitvoer': uitvoer,
        'cache_geschreven': cache_schrijf,
        'cache_gelezen': cache_lees,
        'euro': round(dollar * 0.92, 5),
    }


class TekstFout(Exception):
    """Het model leverde geen bruikbare tekst. De aanroeper toont de reden."""


def schrijf_beschrijving(product, model=None, api_key=None):
    """Een beschrijving voor dit product, plus wat de aanroep kostte.

    Geeft {'tekst', 'kosten', 'model'} terug, of werpt TekstFout.

    Er wordt niets opgeslagen: dat is de verantwoordelijkheid van de
    aanroeper. Zo kan dezelfde functie een proef draaien zonder de site te
    raken.
    """
    sleutel = api_key or os.getenv('ANTHROPIC_API_KEY')
    if not sleutel:
        raise TekstFout("ANTHROPIC_API_KEY ontbreekt")
    naam = model or os.getenv('ANTHROPIC_MODEL') or 'claude-opus-5'

    client = Anthropic(api_key=sleutel)
    antwoord = client.messages.create(
        model=naam,
        max_tokens=_MAX_TOKENS,
        system=[{
            'type': 'text',
            'text': SYSTEEMINSTRUCTIE,
            'cache_control': {'type': 'ephemeral'},
        }],
        # Lage inspanning: dit is schrijfwerk op een vaste opdracht, geen
        # redeneerprobleem. Scheelt tokens zonder dat de tekst eronder lijdt.
        output_config={'effort': 'low'},
        messages=[{'role': 'user', 'content': bouw_prompt(product)}],
    )

    # Volgorde is niet vrijblijvend: bij een weigering is content leeg, en
    # antwoord.content[0] zou dan een IndexError geven in plaats van een
    # leesbare melding.
    if antwoord.stop_reason == 'refusal':
        raise TekstFout("het model weigerde deze opdracht")
    tekst = next((blok.text for blok in antwoord.content
                  if blok.type == 'text' and blok.text.strip()), '')
    if not tekst:
        raise TekstFout(f"leeg antwoord (stop_reason={antwoord.stop_reason})")
    if antwoord.stop_reason == 'max_tokens':
        raise TekstFout("tekst liep tegen het tokenplafond en is afgekapt")

    return {'tekst': tekst.strip(), 'kosten': _kosten(antwoord.usage),
            'model': antwoord.model}
