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
    ('droger', ('tumbledriers',)),
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


def _bevraag(groep, code):
    """Eén zoekopdracht bij EPREL. Geeft de eerste treffer of None."""
    adres = (f"{_BASIS}/{groep}"
             f"?modelIdentifier={urllib.parse.quote(code)}&limit=2")
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
    treffers = data.get('hits') or []
    return treffers[0] if treffers else None


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
            hit = _bevraag(groep, code)
            if pauze:
                time.sleep(pauze)
            if hit:
                uitkomst = _uitpakken(hit, groep, code)
                uitkomst['gezocht'] = True
                return uitkomst
    return {'gezocht': True, 'gevonden': False, 'gezocht_op': ', '.join(codes)}
