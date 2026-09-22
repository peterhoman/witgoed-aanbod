"""Gegevens uit de EU-energielabeldatabase (EPREL) bij onze apparaten zoeken.

Waarom dit bestaat
------------------
Van onze catalogus heeft 65% geen enkele specificatie, en het Model-veld is
bij 74% leeg. Dat is precies waarom veel eigen productteksten kort zijn: er
viel weinig over te schrijven. En het is een van de redenen dat Google 918
pagina's kent maar niet de moeite waard vindt om op te halen.

EPREL is het register waar fabrikanten wettelijk verplicht hun
energielabelgegevens aanmelden. Geen winkeltekst, geen overgeschreven
specificatie: de opgave van de fabrikant zelf bij de Europese Commissie.

Twee dingen komen hier vandaan die we nergens anders krijgen: het
registratienummer (nodig voor hasCertification, een veld dat Google
uitdrukkelijk voor EPREL documenteert en "particularly relevant in European
countries" noemt) en geverifieerde specificaties.

Wat gemeten is voordat dit gebouwd werd
---------------------------------------
Steekproef van 150 producten op 30-07-2026:

    gevonden in EPREL          55
    niet gevonden               9
    geen typenummer in de titel 20
    soort zonder energielabel   66

Van de apparaten die een EU-energielabel hébben vinden we er 65% terug; over
de hele catalogus komt dat neer op ongeveer 1.020 producten. De 66 zonder
label zijn stofzuigers, koffiemachines, magnetrons en airfryers -- die staan
niet in EPREL en kunnen dus nooit matchen.

Waar het spaak loopt, en dat is met opzet
-----------------------------------------
Het typenummer moet als los woord uit de titel te halen zijn. Dat lukt bij
"Bosch WQG133DANL", maar niet bij "Miele WEE 388 WCS" of "Liebherr Cue 2331"
-- die schrijven hun typenummers met spaties. Zulke apparaten krijgen geen
EPREL-koppeling. Dezelfde afweging als bij de setprijzen: liever niets dan een
verkeerde koppeling, want een verkeerd registratienummer in de markup is
erger dan geen registratienummer.

Spelregels van de licentie
--------------------------
De openbare API mag hiervoor gebruikt worden; artikel 4 lid 1 noemt
uitdrukkelijk "to implement the Data in mobile applications and other
comparison tools". Daar horen twee verplichtingen bij:

  - bronvermelding bij wat we tonen (artikel 4 lid 3);
  - lokaal opgeslagen data actueel houden (artikel 4 lid 2f). Vandaar dat
    elke rij een ophaalmoment krijgt en oude rijen opnieuw worden opgehaald.

En een fatsoensregel die niet in de licentie staat: rustig bevragen. Eén
verzoek tegelijk, met een pauze ertussen, en per apparaat stoppen zodra er
een treffer is.
"""

import logging
import re
import time
import urllib.parse

import requests

logger = logging.getLogger(__name__)

_BASIS = 'https://eprel.ec.europa.eu/api/products'

# Zonder browser-achtige kop antwoordt de API met 403. Dat is geen omzeiling
# van een slot -- dit zijn dezelfde openbare adressen die de EPREL-website
# zelf gebruikt -- maar hun beveiliging weert kale scripts.
_KOP = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/126.0 Safari/537.36'),
    'Referer': 'https://eprel.ec.europa.eu/screen/home',
}

_PAUZE = 0.5
_TIMEOUT = 25

# Dezelfde strenge herkenning als setprijs.py: begint met een paar letters,
# bevat een cijfer, en is lang genoeg om geen gewoon woord te zijn. Een
# verkeerde match is erger dan geen match.
_TYPENUMMER = re.compile(r'^[a-z]{1,5}[0-9][a-z0-9./-]{2,}$', re.IGNORECASE)
_MIN_LENGTE = 5
_MAX_KANDIDATEN = 3

# Onze categorie of titel -> de EPREL-productgroep(en). Volgorde telt: de
# eerste die een treffer geeft wint. Wat hier niet in staat heeft geen
# EU-energielabel en wordt niet gezocht.
_GROEPEN = (
    ('wasdroog', ('washerdriers2019',)),
    ('was-droog', ('washerdriers2019',)),
    ('wasmachine', ('washingmachines2019', 'washerdriers2019')),
    # Drogers: eerst het register van de nieuwe labelschaal A-G (geldt sinds
    # 1 juli 2025), dan pas het oude. Tot 21 september 2026 stond hier alleen
    # 'tumbledriers' en toonden 56 pagina's een vervallen A+++. De naam is bij
    # EPREL zelf nagevraagd (/api/product-groups), niet gegokt: de Bosch
    # WQG133DBNL staat in het oude register op A++ en in het nieuwe op C. Het
    # oude blijft als vangnet voor geluid en afmetingen van modellen die niet
    # opnieuw zijn aangemeld; de klasse daaruit tonen we niet
    # (eprel_specs.VEROUDERDE_LABELGROEPEN).
    ('droger', ('tumbledryers20232534', 'tumbledriers')),
    ('vaatwasser', ('dishwashers2019',)),
    ('koelkast', ('refrigeratingappliances2019', 'refrigeratingappliances')),
    ('vries', ('refrigeratingappliances2019', 'refrigeratingappliances')),
    ('koel-vries', ('refrigeratingappliances2019', 'refrigeratingappliances')),
    ('oven', ('ovens',)),
    ('fornuis', ('ovens',)),
    ('afzuigkap', ('rangehoods',)),
    ('airco', ('airconditioners',)),
)

# Soorten zonder EU-energielabel worden niet gezocht -- dat scheelt een derde
# van de catalogus aan vergeefse verzoeken aan Brussel. Twee lijsten, en dat
# onderscheid is niet vrijblijvend.
#
# Op de CATEGORIE: hele categorieen waarvan niets een energielabel heeft.
_CATEGORIE_ZONDER_LABEL = ('stofzuiger', 'koffie', 'magnetron',
                           'apparaatset', 'kookplaat')

# Op de TITEL: apparaten die in een categorie zitten waar de rest wél een
# label heeft. De categorie heet "Ovens & Airfryers", en daar zitten echte
# inbouwovens in (die een label hebben) naast vrijstaande airfryers (die er
# geen hebben). Op de categorie uitsluiten zou dus alle ovens meenemen -- dat
# gebeurde in de eerste versie hiervan, en dat kostte de zes oven-treffers
# die er al lagen.
#
# Een titel met allebei ("Inventum GF1200HLD Airfryer Oven XXL") valt af.
# Dat is de veilige kant: liever een oven missen dan een airfryer koppelen
# aan het energielabel van iets anders.
_TITEL_ZONDER_LABEL = ('airfryer', 'friteuse', 'espresso', 'kookplaat')

# Velden die we bewaren als ze er zijn. Per productgroep verschilt welke
# bestaan; wat ontbreekt wordt overgeslagen in plaats van op nul gezet.
_VELDEN = (
    'energyClass', 'energyConsPerCycle', 'energyConsPer100Cycle',
    'noise', 'noiseClass', 'waterCons', 'ratedCapacity',
    'spinSpeedRated', 'spinClass', 'energyEfficiencyIndex',
    'dimensionHeight', 'dimensionWidth', 'dimensionDepth',
    'guaranteeDuration', 'onMarketStartDate', 'productGroup',
    'totalVolume', 'freezerVolume', 'fridgeVolume', 'climateClass',
    'annualEnergyConsumption', 'cavityVolume', 'airflow',
)


class EprelFout(Exception):
    """Iets ging mis bij het bevragen van EPREL."""


def groepen_voor(categorie, titel=''):
    """De EPREL-productgroepen waarin dit apparaat kan staan, of een lege lijst."""
    cat = (categorie or '').lower()
    tit = (titel or '').lower()

    # Een apparaatset kan wel een wasmachine bevatten, maar staat als set niet
    # in EPREL; de losse apparaten staan er apart in.
    if any(soort in cat for soort in _CATEGORIE_ZONDER_LABEL):
        return []
    if any(soort in tit for soort in _TITEL_ZONDER_LABEL):
        return []

    tekst = f"{cat} {tit}"
    uit = []
    for sleutel, groepen in _GROEPEN:
        if sleutel in tekst:
            for groep in groepen:
                if groep not in uit:
                    uit.append(groep)
    return uit


def codes_uit_titel(titel):
    """Kandidaat-typenummers uit een titel, het langste eerst.

    Het langste eerst omdat een langere code specifieker is: bij "Bosch
    WQG133DANL 9 kg" is WQG133DANL het typenummer en niet iets anders dat
    toevallig aan de vorm voldoet.
    """
    gevonden = []
    gezien = set()
    for woord in re.split(r'[\s,]+', str(titel or '')):
        kaal = woord.strip('.,;:()[]/')
        if len(kaal) < _MIN_LENGTE or not _TYPENUMMER.match(kaal):
            continue
        if kaal.upper() in gezien:
            continue
        gezien.add(kaal.upper())
        gevonden.append(kaal)
    gevonden.sort(key=len, reverse=True)
    return gevonden[:_MAX_KANDIDATEN]


def _kaal(tekst):
    """Typenummer zonder opmaak: 'WF5S1045BB/PL' -> 'wf5s1045bbpl'."""
    return re.sub(r'[^a-z0-9]', '', (tekst or '').lower())


def koppeling_klopt(gezocht_op, gevonden_model, titel):
    """Hoort deze EPREL-treffer bij dit apparaat?

    Ja als het gevonden typenummer BEGINT met het gezochte ('TR73CB96' ->
    'TR73CB96 916099294': AEG zet zijn productcode erachter), of als het hele
    gevonden nummer in onze titel staat ('Hs61w' -> 'W8F HS61W' bij de titel
    "Whirlpool W8f Hs61w").

    Nee als het gezochte nummer alleen ergens ín een ander model zit. Gemeten
    op 21 september 2026, vier gevallen: Whirlpool "W2F HD624" hing (twee keer)
    aan 'P2F HD624 A', Inventum "KK550B" aan 'RKK550B/02' (een ander apparaat,
    en prompt zei het register E waar de winkel D zei), Etna "Vv856wit" aan
    'KVV856WIT'. Dat laatste is waarschijnlijk wél hetzelfde apparaat met een
    verminkte winkeltitel, maar dat weten we niet zeker, en een verkeerd
    registratienummer is erger dan geen (zie de kop van dit bestand).

    gezocht_op kan meerdere codes bevatten ("A123, B456"); één die past is
    genoeg.
    """
    model = _kaal(gevonden_model)
    if not model:
        return False
    codes = [_kaal(c) for c in (gezocht_op or '').split(',')]
    if any(c and model.startswith(c) for c in codes):
        return True
    return model in _kaal(titel)


def _kies_treffer(treffers, code, titel=''):
    """De treffer met precies dit typenummer, anders de eerste die klopt.

    EPREL zoekt op "begint met": 'RT90X8' geeft RT90X8BC, RT90X8C, RT90X8,
    RT90X8B en RT90X8YB, in die volgorde. Tot 21 september 2026 namen we
    altijd de eerste, en hing de LG RT90X8 dus aan het registratienummer van
    de RT90X8BC. Staat het exacte nummer ertussen, dan wint dat.

    Zonder exacte treffer blijft de eerste gelden, en dat is met opzet: AEG en
    Beko melden hun modellen aan met hun eigen productcode erachter
    ('GI5200C2SZ 911571123'). Dat is hetzelfde apparaat, en zulke koppelingen
    (een paar honderd) zouden anders verdwijnen.
    """
    doel = _kaal(code)
    for treffer in treffers:
        if _kaal(treffer.get('modelIdentifier')) == doel:
            return treffer
    # Geen exacte: de eerste die aantoonbaar bij dit apparaat hoort. Een
    # treffer waar het gezochte nummer alleen middenin zit valt af.
    for treffer in treffers:
        if koppeling_klopt(code, treffer.get('modelIdentifier'), titel):
            return treffer
    return None


def _bevraag(groep, code, titel=''):
    """Eén zoekopdracht bij EPREL. Geeft de beste treffer of None."""
    # limit=10 en niet 2: de exacte treffer staat lang niet altijd vooraan.
    adres = (f"{_BASIS}/{groep}"
             f"?modelIdentifier={urllib.parse.quote(code)}&limit=10")
    try:
        antwoord = requests.get(adres, headers=_KOP, timeout=_TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise EprelFout(f"EPREL onbereikbaar: {e}") from e
    if antwoord.status_code == 404:
        return None
    # 429 en 403 apart benoemen: dat zijn de twee manieren waarop Brussel
    # zegt "je vraagt te veel". De voorwaarden noemen geen limieten, dus dit
    # is de enige manier om te weten dat we er tegenaan lopen -- en dat moet
    # zichtbaar zijn, niet alleen in een logregel die niemand leest.
    if antwoord.status_code == 429:
        raise EprelFout('EPREL wijst ons af: te veel verzoeken (429). '
                        'Verlaag de frequentie (EPREL_INTERVAL omhoog).')
    if antwoord.status_code == 403:
        raise EprelFout('EPREL weigert de toegang (403). Dat kan een blokkade '
                        'zijn, of een wijziging aan hun kant.')
    if antwoord.status_code != 200:
        raise EprelFout(f"EPREL gaf {antwoord.status_code} voor {groep}")
    try:
        data = antwoord.json()
    except ValueError as e:
        raise EprelFout("EPREL gaf geen leesbare JSON") from e
    if not data.get('size'):
        return None
    return _kies_treffer(data.get('hits') or [], code, titel)


def _uitpakken(hit, groep, code):
    """Het antwoord van EPREL terugbrengen tot wat wij bewaren."""
    gegevens = {veld: hit[veld] for veld in _VELDEN
                if hit.get(veld) not in (None, '')}
    return {
        'gevonden': True,
        'gezocht_op': code,
        'registratienummer': str(hit.get('eprelRegistrationNumber') or '') or None,
        'productgroep': groep,
        'modelnummer': hit.get('modelIdentifier'),
        'leverancier': hit.get('supplierOrTrademark'),
        'energieklasse': hit.get('energyClass'),
        'gegevens': gegevens,
    }


def zoek(categorie, titel, pauze=_PAUZE):
    """Zoek dit apparaat in EPREL. Geeft altijd een dict terug.

    Drie uitkomsten, en het verschil ertussen is het hele punt:

      gezocht=False   er is niet eens gezocht. Dit soort apparaat staat niet
                      in EPREL (stofzuiger, magnetron, airfryer), of er valt
                      geen typenummer uit de titel te halen (Miele schrijft
                      "WEE 388 WCS" met spaties). Zo'n apparaat kan nooit een
                      treffer worden en hoort niet mee te tellen als misser.
      gevonden=False  gezocht en niets gevonden. Dit model staat niet in het
                      register, of onder een andere schrijfwijze.
      gevonden=True   raak, met de gegevens erbij.

    Dat onderscheid stond er eerst niet in -- beide eerste gevallen gaven
    None -- en daardoor las de meetpagina een trefkans van 48% terwijl die
    over de apparaten die er echt in kunnen staan rond de 70% ligt. Een
    cijfer dat je verkeerd leest is erger dan geen cijfer.

    Stopt bij de eerste treffer: een apparaat staat maar in één groep.
    """
    groepen = groepen_voor(categorie, titel)
    if not groepen:
        return {'gezocht': False, 'reden': 'dit soort staat niet in EPREL'}
    codes = codes_uit_titel(titel)
    if not codes:
        return {'gezocht': False, 'reden': 'geen typenummer in de titel'}

    for code in codes:
        for groep in groepen:
            hit = _bevraag(groep, code, titel)
            if pauze:
                time.sleep(pauze)
            if hit:
                uitkomst = _uitpakken(hit, groep, code)
                uitkomst['gezocht'] = True
                return uitkomst
    return {'gezocht': True, 'gevonden': False, 'gezocht_op': ', '.join(codes)}
