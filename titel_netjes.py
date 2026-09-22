"""Feedtitels opknappen voor koppen: modelcodes in hoofdletters, eenheden
zoals ze horen, soortwoorden zonder hoofdletter.

Waarom (22 september 2026): de H1 van de productpagina en de H3 van elk
productkaartje waren de kale feedtitel. MediaMarkt (Tradedoubler) levert die
met een hoofdletter per woord: "LG Rt90x8 - Warmtepompdroger 9kg 62 Db
Energielabel B", "Haier Hw90-b14939 I-pro 3 - Wasmachine Voorlader 9 Kg 1400
Rpm 67 Db". Gemeten op 150 live productpagina's: 25% van de H1's had zo'n
verkeerd geschreven modelcode of eenheid. De <title> was al schoon
(product_specs.zoektitel); de kop op de pagina zelf niet.

Bewust een lichte hand: alleen wat zeker fout is wordt aangeraakt.
- Een woord dat op een typenummer lijkt (letters, cijfer, lang genoeg) gaat
  naar hoofdletters: Rt90x8 -> RT90X8. Zelfde patroon als zoektitel.
- Eenheden en afkortingen krijgen hun vaste schrijfwijze: Kg -> kg, Db -> dB,
  Rpm -> rpm, Rvs -> RVS. "9kg" wordt "9 kg".
- Een vaste lijst gewone woorden (warmtepompdroger, voorlader, breedte, ...)
  verliest zijn hoofdletter, behalve aan het begin van de titel of direct na
  een " - " (daar begint een nieuw zinsdeel). Alleen als het woord Netjes
  Met Één Hoofdletter geschreven is; "SuperSpeed" of "NoFrost" blijft staan.
- Al het andere (merknamen, productnamen, kleuren die niet in de lijst
  staan) blijft precies zoals de winkel het schreef.
De titel in de database verandert niet; dit is een weergavefilter.
"""
import re

# Zelfde patroon als product_specs._TITEL_TYPENUMMER; hier gekopieerd om geen
# import-kring te maken (product_specs importeert modellen).
_TYPENUMMER = re.compile(r'^[a-z]{1,5}[0-9][a-z0-9./-]{2,}$', re.IGNORECASE)
_TYPENUMMER_MIN = 5

# Vaste schrijfwijze van eenheden en afkortingen (sleutel in kleine letters).
_EENHEDEN = {
    'kg': 'kg', 'db': 'dB', 'rpm': 'rpm', 'cm': 'cm', 'mm': 'mm', 'ml': 'ml',
    'kw': 'kW', 'kwh': 'kWh', 'l': 'l', 'w': 'W', 'v': 'V', 'hz': 'Hz',
    'rvs': 'RVS', 'led': 'LED', 'lcd': 'LCD', 'tft': 'TFT', 'oled': 'OLED',
    'xl': 'XL', 'xxl': 'XXL', 'xs': 'XS', 'usb': 'USB', 'hd': 'HD',
    'wifi': 'wifi', 'wi-fi': 'wifi', 'nofrost': 'NoFrost', 'bpa': 'BPA',
    'pfas': 'PFAS', 'ai': 'AI', 'tv': 'TV', 'ac': 'AC', 'dc': 'DC',
    'min': 'min', 'sec': 'sec', 'std': 'std',
}
# Getal direct gevolgd door een eenheid: "9kg", "62db", "1400rpm", "9.5l".
_GETAL_EENHEID = re.compile(
    r'^(\d+(?:[.,]\d+)?)(kg|db|rpm|cm|mm|ml|kw|kwh|l|w|v|hz)$', re.IGNORECASE)

# Gewone woorden die in een titel geen hoofdletter horen te hebben.
_GEWONE_WOORDEN = {
    # soorten apparaten
    'wasmachine', 'wasmachines', 'voorlader', 'bovenlader', 'droger', 'drogers',
    'wasdroger', 'warmtepompdroger', 'warmtepomdroger', 'condensdroger',
    'luchtafvoerdroger', 'was-droogcombinatie', 'wasdroogcombinatie',
    'koelkast', 'koelkasten', 'koel-vriescombinatie', 'koelvriescombinatie',
    'vriezer', 'vrieskast', 'vrieskist', 'diepvrieskast', 'vaatwasser',
    'afwasmachine', 'magnetron', 'combi-magnetron', 'combimagnetron', 'oven',
    'inbouwoven', 'heteluchtoven', 'stofzuiger', 'steelstofzuiger',
    'robotstofzuiger', 'kruimeldief', 'koffiemachine', 'espressomachine',
    'koffiezetapparaat', 'fornuis', 'kookplaat', 'inductiekookplaat',
    'afzuigkap', 'heteluchtfriteuse', 'airfryer', 'friteuse', 'wijnkoelkast',
    'kap', 'apparaat', 'vriesvak', 'dubbele', 'tafelkoelkast', 'bundel',
    'stoomoven', 'combi-oven',
    # eigenschappen en maten
    'breedte', 'hoogte', 'diepte', 'inhoud', 'capaciteit', 'vermogen',
    'energielabel', 'energieklasse', 'laadvermogen', 'vulgewicht', 'toeren',
    'centrifuge', 'accuduur', 'geluidsniveau', 'programma', "programma's",
    'aantal', 'liter', 'minuten', 'serie', 'model', 'type', 'kleur',
    'automatisch', 'doseren', 'nishoogte', 'personen', 'meter', 'standen',
    'jaar', 'garantie', 'zak', 'frituurmanden', 'kopjes', 'maximaal',
    'volautomatische', 'volautomatisch', 'mat', 'glans',
    # plaatsing en uitvoering
    'vrijstaand', 'vrijstaande', 'inbouw', 'onderbouw', 'tafelmodel',
    'muur', 'plafond', 'eiland', 'bevestigde', 'wand', 'hoek',
    'inductie', 'keramisch', 'keramische', 'gas', 'elektrisch', 'elektrische',
    'rechtsdraaiende', 'linksdraaiende', 'deur', 'deuren', 'lade', 'laden',
    'zones', 'branders', 'pitten', 'fasen', '2-fasen', '3-fasen', 'phases',
    # kleuren
    'zwart', 'zwarte', 'wit', 'witte', 'zilver', 'grijs', 'grijze', 'rood',
    'blauw', 'groen', 'beige', 'antraciet', 'roestvrijstaal',
    # verbindingswoorden
    'met', 'en', 'voor', 'van', 'op', 'in', 'zonder', 'incl', 'incl.', 'of',
    'per', 'tot', 'bij', 'inclusief',
}

# Een woord dat "Netjes" geschreven is: hoofdletter, dan alleen kleine
# letters, koppeltekens of apostrofs. "SuperSpeed" en "NoFrost" vallen erbuiten.
_NETJES = re.compile(r"^[A-ZÀ-Ý][a-zà-ÿ'\-]+\.?$")

_SCHEIDING = re.compile(r'(\s+)')
_RAND = ".,;:()[]/|"


def _woord(kaal, aan_zinsbegin):
    """Eén woord (zonder omringende leestekens) opknappen."""
    laag = kaal.lower()

    # Eenheid of afkorting met vaste schrijfwijze.
    if laag in _EENHEDEN:
        return _EENHEDEN[laag]

    # "9kg" -> "9 kg", "62db" -> "62 dB".
    m = _GETAL_EENHEID.match(kaal)
    if m:
        return f"{m.group(1)} {_EENHEDEN[m.group(2).lower()]}"

    # Typenummer: hoofdletters. Niet als het woord al een eenheid was, en
    # niet als het een gewoon woord is.
    if (len(kaal) >= _TYPENUMMER_MIN and _TYPENUMMER.match(kaal)
            and laag not in _GEWONE_WOORDEN):
        return kaal.upper()

    # Gewoon woord met een onnodige hoofdletter.
    if not aan_zinsbegin and laag in _GEWONE_WOORDEN and _NETJES.match(kaal):
        return laag

    return kaal


_ALFABETISCH = re.compile(r"^[A-Za-zÀ-ÿ'\-]+$")


def _hoofdletter_per_woord(titel):
    """Schrijft deze feed elk woord met een hoofdletter (MediaMarkt-stijl)?

    Alleen dan worden gewone woorden uit de lijst kleingemaakt. Proef op 300
    live titels (22 sept): zonder deze drempel raakte het filter ook titels
    van Coolblue en Bol die al goed waren, en maakte er halfslachtige dingen
    van ("Philips airfryer met Stoomfunctie"). Criterium: na het eerste
    woord geen enkel woord in kleine letters, en minstens drie woorden Netjes
    Met Hoofdletter.
    """
    woorden = [w.strip(_RAND) for w in titel.split()][1:]
    netjes = 0
    for w in woorden:
        if not w or not _ALFABETISCH.match(w) or w.isupper():
            continue
        if w.islower():
            return False
        if _NETJES.match(w):
            netjes += 1
    return netjes >= 3


def nette_titel(titel):
    """De feedtitel zoals hij in een kop hoort te staan. Leeg blijft leeg."""
    titel = (titel or '').strip()
    if not titel:
        return titel
    kleinmaken = _hoofdletter_per_woord(titel)
    delen = _SCHEIDING.split(titel)
    uit = []
    zinsbegin = True
    for deel in delen:
        if not deel or deel.isspace():
            uit.append(deel)
            continue
        # Losse streep of pijp tussen zinsdelen: daarna begint een nieuw deel.
        if deel in ('-', '–', '—', '|', '+', '/'):
            uit.append(deel)
            zinsbegin = True
            continue
        voor = ''
        achter = ''
        kaal = deel
        while kaal and kaal[0] in _RAND:
            voor += kaal[0]
            kaal = kaal[1:]
        while kaal and kaal[-1] in _RAND and kaal.lower() not in _EENHEDEN:
            achter = kaal[-1] + achter
            kaal = kaal[:-1]
        if not kaal:
            uit.append(deel)
            continue
        uit.append(voor + _woord(kaal, zinsbegin or not kleinmaken) + achter)
        zinsbegin = False
    return ''.join(uit)
