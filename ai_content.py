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
4. Schrijf niets wat na verloop van tijd onwaar wordt. Deze tekst wordt een \
keer geschreven en blijft dan staan, terwijl prijzen dagelijks wijzigen en \
winkels apparaten uit hun aanbod halen. Dus: geen prijs, en ook geen \
omschrijving van de prijs -- niet "goedkoop", niet "in het hogere \
prijssegment", niet "een van de duurdere modellen in zijn soort". Geen \
winkelnaam, en niets over leverbaarheid, aanbiedingen of levertijd. Schrijf \
alleen over eigenschappen van het apparaat zelf; die veranderen niet.
5. Geen aansporing om te kopen, geen "bekijk nu", geen uitroeptekens.
6. De meting die je meekrijgt gaat over maat en energielabel binnen de \
categorie. Gebruik die om te bepalen of iets ruim of krap, zuinig of \
onzuinig is voor zijn soort. Schrijf hem niet over: hij staat als apart blok \
op dezelfde pagina.
7. Spreken de gegevens elkaar aantoonbaar tegen, benoem dat dan -- dat is voor \
de lezer het nuttigste wat je kunt doen. Voorbeeld: staat er in de titel van \
de winkel "Energieklasse A" terwijl het energielabel van de gecombineerde \
was-droogcyclus D is, zeg dan dat die A alleen voor het wassen geldt. Doe dit \
alleen bij een echte tegenspraak in de gegevens die je hebt, nooit op \
vermoeden.
8. Geen kop, geen opsomming, geen markdown. Alleen alinea's gewone tekst, \
gescheiden door een lege regel. Begin niet met de productnaam als \
aankondiging ("De Bosch WGG244FONL is een wasmachine die...") maar schrijf \
alsof de lezer al ziet welk apparaat hij voor zich heeft.
9. Schrijf zakelijk en droog. Spreek de lezer niet aan met "u" of "je"."""


# Woorden die er niet in horen, met de reden erbij. Tien teksten kan een mens
# nalezen, 2806 niet -- dus toetst de machine mee. Aanleiding: proef-v1 leverde
# drie teksten met een prijsoordeel ("hoort tot de goedkopere modellen"),
# terwijl regel 4 alleen bedragen verbood. Zulke zinnen zijn vandaag waar en
# over een maand onwaar, want de tekst wordt eenmalig geschreven.
#
# Waar de grens ligt is met de hand nagelopen. Te ruim (kale deelstring) keurt
# "duurzaam" en "wasduur" af, die niets met prijs te maken hebben. Te strak
# (alleen hele woorden) laat verbuigingen door: \bgoedkoper\b vond in ronde 1
# de zin "hoort tot de goedkopere modellen" niet, want na "goedkoper" volgt
# een letter en dan is er geen woordgrens. Vandaar stammen met \w* waar de
# verbuiging vrij is, en hele woorden waar een langer woord iets anders
# betekent.
#
# Na 2806 teksten opnieuw geijkt. De zeef streepte er 87 aan en bij nalezen was
# er geen enkele die een regel overtrad -- allemaal woorden die op prijs lijken
# maar het niet zijn. Een zeef die 87 goede teksten tegenhoudt is net zo
# schadelijk als een die een foute doorlaat: dan ga je hem negeren.
#
# Wat er in de praktijk misging, met de aantallen erbij:
# - "prijsgeeft" (28x): het werkwoord prijsgeven. "wat de winkeltitel prijsgeeft"
# - "prijsvergelijking" (32x) en "prijsoverzicht" (1x): verwijzingen naar het
#   vergelijkblok op de pagina zelf, geen bedrag.
# - "duur" (4x): tijdsduur. "bij dit type bepaalt die duur hoeveel..."
# - "koop" (2x): het model legde uit dat "Beste Koop Maart 2026" in de
#   winkeltitel een reclamekreet is en geen eigenschap -- precies wat regel 7
#   vraagt.
# - "actie" (1x): "turbo-actie", een functie van het apparaat.
_VERBODEN = [
    # "duur" kaal is eruit: dat is vaker tijdsduur dan geld. De trap van
    # vergelijking blijft, want daar gaat een prijsoordeel altijd overheen.
    (r'\bgoedko\w*|\bduurder\w*|\bduurst\w*|\bprijzig\w*|\bbetaalb\w*',
     'prijsoordeel'),
    (r'\binstap\w*|\btopmodel\w*|\bbudget\w*', 'prijsoordeel'),
    # Alles met "prijs" behalve het werkwoord prijsgeven en de verwijzingen
    # naar ons eigen vergelijkblok.
    (r'\bprijs(?!geef|geeft|gegeven|geven|vergelijking|overzicht)\w*', 'noemt de prijs'),
    (r'€|\beuro\b', 'noemt een bedrag'),
    (r'\b(bol\.com|coolblue|mediamarkt|expert|alternate|wehkamp)\b', 'winkelnaam'),
    # "actie" kaal is eruit (turbo-actie, ontdooiactie); alleen de
    # aanbiedingsbetekenis blijft.
    (r'\b(leverbaar|voorradig|op voorraad|levertijd|aanbieding|korting|actieprijs)\b',
     'aanbod verandert'),
    # "koop" kaal is eruit: dat zit in aankoop, koopadvies en in een geciteerde
    # winkeltitel. Alleen de gebiedende wijs telt als aansporing.
    (r'\b(bekijk|bestel|profiteer)\b|\bkoop\s+(nu|hier|deze|dit|hem)\b',
     'aansporing'),
    (r'!', 'uitroepteken'),
    (r'^#|\*\*|^- |^\* ', 'opmaakteken'),
]


def controleer(tekst):
    """Zinnen die tegen een harde regel ingaan, met de reden.

    Geeft een lijst [{'zin', 'reden'}] terug; leeg is goed. Dit is een zeef,
    geen bewijs: hij vindt wat we eerder fout zagen gaan, niet alles wat fout
    kan gaan. Een mens leest de steekproef, de zeef bewaakt de rest.
    """
    import re
    gevonden = []
    for zin in re.split(r'(?<=[.!?])\s+', tekst):
        for patroon, reden in _VERBODEN:
            if re.search(patroon, zin, re.IGNORECASE | re.MULTILINE):
                gevonden.append({'zin': zin.strip(), 'reden': reden})
                break
    return gevonden


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

    # Bewust niet bepaal_categoriecontext(): die begint met de prijszinnen, en
    # daar kwamen in proef-v1 de drie prijsoordelen vandaan die er niet in
    # horen. Een model dat een feit voorgeschoteld krijgt, gebruikt het -- dus
    # de betrouwbare oplossing is het feit niet aanleveren, niet het verbieden.
    # Maat en label blijven wel: die zijn eigenschappen van het apparaat en
    # veranderen niet, en juist die maken "ruim" of "zuinig" hard.
    from category_context import _MIN_CATEGORIE, _formaatzin, _labelzin, _profiel

    if product.category is not None:
        profiel = _profiel(product.category.id, product.category.slug)
        if len(profiel['prijzen']) >= _MIN_CATEGORIE:
            naam = product.category.name.lower()
            meting = [z for z in (_formaatzin(product, profiel, naam),
                                  _labelzin(product, profiel, naam)) if z]
            if meting:
                delen.append("\nOnze meting over deze categorie (ter "
                             "orientatie, niet overschrijven):\n"
                             + "\n".join(meting))

    return "\n".join(delen)


def verzoek_velden(product, model):
    """De velden van een aanvraag, gedeeld door de losse en de batch-route.

    Bewust een functie en niet twee keer dezelfde regels: gaan die uit elkaar
    lopen, dan voorspelt de proef niet meer wat de batch doet, en dat is
    precies het soort verschil dat je pas na 2806 teksten ontdekt.
    """
    return {
        'model': model,
        'max_tokens': _MAX_TOKENS,
        'system': [{
            'type': 'text',
            'text': SYSTEEMINSTRUCTIE,
            'cache_control': {'type': 'ephemeral'},
        }],
        # Lage inspanning: dit is schrijfwerk op een vaste opdracht, geen
        # redeneerprobleem. Scheelt tokens zonder dat de tekst eronder lijdt.
        'output_config': {'effort': 'low'},
        'messages': [{'role': 'user', 'content': bouw_prompt(product)}],
    }


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


class Budgetstop(Exception):
    """De dagelijkse geldgrens is bereikt. Geen fout maar een noodrem."""


def besteed_vandaag():
    """Wat er dit etmaal aan teksten is uitgegeven, in euro's.

    Telt over de hele ai_content-tabel, niet per soort tekst: een noodrem die
    per categorie apart telt is geen noodrem. Bij een lege of ontbrekende
    kolom komt er 0 uit -- dat mag, want dan is er ook niets uitgegeven.
    """
    from datetime import timedelta

    from sqlalchemy import func

    from models import AIContent, db, utcnow

    grens = utcnow() - timedelta(hours=24)
    som = (db.session.query(func.coalesce(func.sum(AIContent.cost), 0.0))
           .filter(AIContent.generated_at >= grens).scalar())
    return float(som or 0.0)


def bewaak_budget(limiet):
    """Werpt Budgetstop als de geldgrens bereikt is.

    Aanroepen voor elke generatie, niet een keer per verzoek: een lus die
    duizend teksten maakt moet bij tekst 400 stoppen, niet pas de volgende
    keer dat er iemand langskomt.
    """
    besteed = besteed_vandaag()
    if besteed >= limiet:
        raise Budgetstop(
            f"daggrens bereikt: EUR {besteed:.2f} van EUR {limiet:.2f} in de "
            f"afgelopen 24 uur. Verhoog AI_DAGLIMIET_EURO bewust, of wacht.")
    return besteed


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
    antwoord = client.messages.create(**verzoek_velden(product, naam))

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
            'model': antwoord.model, 'bron_specs': len(_specregels(product))}


# Hoeveel bruikbare specificaties erbij moeten komen voordat een bestaande
# tekst opnieuw geschreven wordt.
#
# De vergelijking gaat over het aantal specs dat de prompt haalt, en dat is
# afgetopt op _MAX_SPECS. Groei daarboven is voor de tekst onzichtbaar: van 76
# naar 78 specs verandert er niets, want in beide gevallen gaan er veertien
# mee. Vier is waar de tekst aantoonbaar anders wordt -- bij minder verschuift
# er hooguit een bijzin, en dat is geen cent per product waard.
_HERSCHRIJF_DREMPEL = 4


def telbare_specs(product):
    """Hoeveel specificaties er van dit product in een tekst terechtkomen.

    Publieke naam voor len(_specregels(...)): de batchroute moet dit getal
    opslaan zonder een functie met een underscore aan te roepen, en het is
    dezelfde meting die moet_herschrijven gebruikt.
    """
    return len(_specregels(product))


def moet_herschrijven(product, rij):
    """Is de data inmiddels zoveel rijker dat deze tekst niet meer klopt?

    Een tekst wordt eenmalig geschreven en blijft staan; dat is de afspraak.
    De uitzondering is een product dat er specificaties bij krijgt. 65% van de
    catalogus heeft er nu geen enkele en krijgt daarom een tekst van 65
    woorden. Levert de feed er later veertig, dan is die korte tekst niet fout
    maar wel achterhaald, en dan is het een cent waard om hem te vervangen.

    Andersom niet: raakt een product specificaties kwijt, dan blijft de
    bestaande tekst staan. Die is geschreven toen we meer wisten, en wat toen
    waar was over het apparaat is dat nu nog.
    """
    if rij is None:
        return True
    # Onbekend (kolom net toegevoegd, tekst van ervoor): niet herschrijven op
    # een aanname. Bij de eerstvolgende echte herschrijving vult het zichzelf.
    if rij.bron_specs is None:
        return False
    return len(_specregels(product)) - rij.bron_specs >= _HERSCHRIJF_DREMPEL


# ---------------------------------------------------------------------------
# Batch: de hele catalogus in een keer, voor de halve prijs
# ---------------------------------------------------------------------------
#
# Waarom niet gewoon 2806 losse aanroepen achter elkaar: dat duurt uren, houdt
# een webverzoek open dat allang is afgekapt, en kost het dubbele. De Batch API
# neemt alles in een keer aan, werkt het binnen 24 uur af en rekent de helft.
#
# Het custom_id is de enige draad terug naar het product: de resultaten komen
# in willekeurige volgorde binnen, dus op positie afgaan gaat mis.

_BATCH_PREFIX = 'prod-'


def dien_batch_in(producten, model=None, api_key=None):
    """Levert de teksten voor deze producten in een keer in. Geeft het batch-id.

    Schrijft zelf niets weg: de aanroeper bewaart het id en haalt de uitkomst
    later op met haal_batch_op. Dat moet ook wel, want tussen inleveren en
    klaar zit tot 24 uur.
    """
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    sleutel = api_key or os.getenv('ANTHROPIC_API_KEY')
    if not sleutel:
        raise TekstFout("ANTHROPIC_API_KEY ontbreekt")
    naam = model or os.getenv('ANTHROPIC_MODEL') or 'claude-opus-5'
    if not producten:
        raise TekstFout("geen producten om in te leveren")

    verzoeken = [
        Request(custom_id=f"{_BATCH_PREFIX}{p.id}",
                params=MessageCreateParamsNonStreaming(**verzoek_velden(p, naam)))
        for p in producten
    ]
    # Verbinding in een variabele, net als in batch_resultaten: hier is het
    # antwoord in een keer binnen en dus ongevaarlijk, maar de schrijfwijze
    # met de verbinding weggemoffeld in de aanroep is precies de val.
    verbinding = Anthropic(api_key=sleutel)
    batch = verbinding.messages.batches.create(requests=verzoeken)
    logger.info("batch %s ingeleverd met %d teksten", batch.id, len(verzoeken))
    return batch.id


def batch_toestand(batch_id, api_key=None):
    """Hoe ver de batch is: {'status', 'gelukt', 'mislukt', 'bezig'}."""
    sleutel = api_key or os.getenv('ANTHROPIC_API_KEY')
    verbinding = Anthropic(api_key=sleutel)
    batch = verbinding.messages.batches.retrieve(batch_id)
    tellingen = batch.request_counts
    return {
        'status': batch.processing_status,
        'klaar': batch.processing_status == 'ended',
        'gelukt': getattr(tellingen, 'succeeded', 0),
        'mislukt': getattr(tellingen, 'errored', 0) + getattr(tellingen, 'expired', 0),
        'bezig': getattr(tellingen, 'processing', 0),
    }


def batch_resultaten(batch_id, api_key=None):
    """Loopt de uitkomsten langs als {'product_id', 'tekst', 'kosten', 'fout'}.

    Halveert de gerapporteerde kosten: de Batch API rekent 50% van het normale
    tarief, en _kosten rekent met de normale prijslijst. Zonder die correctie
    zou de teller op de site het dubbele laten zien van wat er werkelijk
    afgeschreven wordt.
    """
    sleutel = api_key or os.getenv('ANTHROPIC_API_KEY')
    # De verbinding in een eigen variabele, en die moet blijven bestaan zolang
    # er uit de stroom gelezen wordt. Stond hier eerst als
    # Anthropic(...).messages.batches.results(...) op een regel; dan houdt
    # niemand de verbinding meer vast, ruimt Python hem halverwege op en breekt
    # het lezen af met "[Errno 9] Bad file descriptor". Op productie kwam
    # daardoor een van de vijftig teksten binnen en de rest niet -- lokaal viel
    # het niet op, want daar was geen echte verbinding.
    verbinding = Anthropic(api_key=sleutel)
    stroom = verbinding.messages.batches.results(batch_id)
    for uitkomst in stroom:
        cid = uitkomst.custom_id or ''
        if not cid.startswith(_BATCH_PREFIX):
            continue
        try:
            product_id = int(cid[len(_BATCH_PREFIX):])
        except ValueError:
            continue

        soort = uitkomst.result.type
        if soort != 'succeeded':
            fout = getattr(getattr(uitkomst.result, 'error', None), 'type', soort)
            yield {'product_id': product_id, 'tekst': None, 'kosten': None,
                   'fout': f"batch gaf '{soort}' terug ({fout})"}
            continue

        bericht = uitkomst.result.message
        if bericht.stop_reason == 'refusal':
            yield {'product_id': product_id, 'tekst': None, 'kosten': None,
                   'fout': "het model weigerde deze opdracht"}
            continue
        tekst = next((b.text for b in bericht.content
                      if b.type == 'text' and b.text.strip()), '')
        if not tekst:
            yield {'product_id': product_id, 'tekst': None, 'kosten': None,
                   'fout': f"leeg antwoord (stop_reason={bericht.stop_reason})"}
            continue
        if bericht.stop_reason == 'max_tokens':
            yield {'product_id': product_id, 'tekst': None, 'kosten': None,
                   'fout': "tekst liep tegen het tokenplafond en is afgekapt"}
            continue

        kosten = _kosten(bericht.usage)
        kosten['euro'] = round(kosten['euro'] / 2, 5)
        yield {'product_id': product_id, 'tekst': tekst.strip(),
               'kosten': kosten, 'fout': None}
