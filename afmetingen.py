"""Afmetingen (breedte, hoogte, diepte) uit titel en winkeltekst halen.

Waarom dit bestaat
------------------
Merchant Center vroeg op 11 september 2026 om bij 164 koelvriescombinaties
de breedte, diepte en afwerking in de beschrijving op te nemen: "zodat
klanten precies kunnen vinden wat ze nodig hebben". Terecht -- wie een
koelkast zoekt, zoekt op "60 cm breed" -- en onze specificaties bevatten
geen enkele afmeting. Wel staat de breedte bij 210 van de 482 koelkasten
gewoon in de titel of de winkeltekst ("Breedte 59.7 Cm Hoogte 203 Cm",
"Afmetingen (hxbxd): 185 x 60 x 65 cm"). Gemeten op de productiedatabase op
11 september 2026.

Wat het doet
------------
Alleen wat er letterlijk staat, met het woord erbij. Een kale reeks
"185 x 60 x 65 cm" zonder label wordt NIET geraden: bij een koelkast is de
eerste maat de hoogte, bij een oven de breedte, en een verkeerde maat is
erger dan geen maat. Een label als "(hxbxd)" of "(bxhxd)" zegt wel wat de
volgorde is en wordt gevolgd.

Geeft centimeters als float terug, alleen voor maten tussen 10 en 250 cm.
"""
import re

_GETAL = r'(\d{2,3}(?:[.,]\d)?)'
_LOS = {
    'breedte': re.compile(r'\bbreedte\s*[:=]?\s*' + _GETAL + r'\s*(?:cm|centimeter)\b', re.I),
    'hoogte': re.compile(r'\bhoogte\s*[:=]?\s*' + _GETAL + r'\s*(?:cm|centimeter)\b', re.I),
    'diepte': re.compile(r'\bdiepte\s*[:=]?\s*' + _GETAL + r'\s*(?:cm|centimeter)\b', re.I),
}
# "Afmetingen (hxbxd): 185 x 60 x 65 cm" -- het label tussen haakjes geeft de
# volgorde; letters h, b, d in elke volgorde, gescheiden door x of ×.
_GELABELD = re.compile(
    r'afmeting(?:en)?\s*\(\s*([hbd])\s*[x×]\s*([hbd])\s*[x×]\s*([hbd])\s*\)\s*[:=]?\s*'
    + _GETAL + r'\s*[x×]\s*' + _GETAL + r'\s*[x×]\s*' + _GETAL + r'\s*(?:cm|centimeter)?',
    re.I)
_NAAM = {'h': 'hoogte', 'b': 'breedte', 'd': 'diepte'}


def _cm(waarde):
    try:
        cm = float(str(waarde).replace(',', '.'))
    except (TypeError, ValueError):
        return None
    return cm if 10 <= cm <= 250 else None


def parse_afmetingen(titel, tekst=''):
    """{'breedte': 59.7, 'hoogte': 203.0, ...} -- alleen wat er letterlijk staat.

    De titel gaat voor de tekst: die is korter en komt van de winkel zelf.
    """
    uit = {}
    for bron in (titel or '', tekst or ''):
        if not bron:
            continue
        for naam, rx in _LOS.items():
            if naam not in uit:
                m = rx.search(bron)
                if m and _cm(m.group(1)) is not None:
                    uit[naam] = _cm(m.group(1))
        m = _GELABELD.search(bron)
        if m:
            letters = [m.group(i).lower() for i in (1, 2, 3)]
            if len(set(letters)) == 3:
                for letter, waarde in zip(letters, (m.group(4), m.group(5), m.group(6))):
                    naam = _NAAM[letter]
                    if naam not in uit and _cm(waarde) is not None:
                        uit[naam] = _cm(waarde)
    return uit


def _nl(cm):
    """59.7 -> '59,7', 60.0 -> '60'."""
    return (f'{cm:.1f}'.rstrip('0').rstrip('.')).replace('.', ',')


def afmetingen_zin(afmetingen):
    """'Breedte 59,7 cm, hoogte 203 cm, diepte 65 cm.' of '' als er niets is."""
    delen = [f'{naam} {_nl(afmetingen[naam])} cm'
             for naam in ('breedte', 'hoogte', 'diepte') if naam in afmetingen]
    if not delen:
        return ''
    zin = ', '.join(delen)
    return zin[0].upper() + zin[1:] + '.'


# Specificatievelden zoals de feeds ze leveren (872 producten hebben 'Product
# breedte', 826 'Product hoogte'; 'Product lengte' is bij een apparaat de
# diepte). Waarden zijn tekst: "59.5 cm", "595 mm", "60".
_SPEC_SLEUTELS = {
    'breedte': ('product breedte', 'breedte'),
    'hoogte': ('product hoogte', 'hoogte'),
    'diepte': ('product lengte', 'product diepte', 'diepte'),
}
_SPEC_WAARDE = re.compile(r'^\s*(\d{2,4}(?:[.,]\d+)?)\s*(cm|mm|centimeter|millimeter)?\s*$', re.I)


def _spec_cm(waarde):
    m = _SPEC_WAARDE.match(str(waarde or ''))
    if not m:
        return None
    getal = float(m.group(1).replace(',', '.'))
    eenheid = (m.group(2) or 'cm').lower()
    if eenheid in ('mm', 'millimeter'):
        getal = getal / 10
    return getal if 10 <= getal <= 250 else None


def afmetingen_van_product(product):
    """Afmetingen uit de specificaties, aangevuld uit titel en winkeltekst.

    Specificaties gaan voor: die zijn per veld geleverd en hoeven niet
    geraden te worden. Wat daar ontbreekt komt uit de tekst, alleen als het
    er letterlijk met het woord erbij staat (zie parse_afmetingen).
    """
    specs = {str(k).strip().lower(): v for k, v in (getattr(product, 'specs', None) or {}).items()}
    uit = {}
    for naam, sleutels in _SPEC_SLEUTELS.items():
        for sleutel in sleutels:
            cm = _spec_cm(specs.get(sleutel))
            if cm is not None:
                uit[naam] = cm
                break
    if len(uit) < 3:
        geparsed = parse_afmetingen(getattr(product, 'title', ''),
                                    getattr(product, 'description', ''))
        for naam, cm in geparsed.items():
            uit.setdefault(naam, cm)
    return uit


def kenmerken_zin(product):
    """Korte feitenzin voor de feedbeschrijving: afmetingen en kleur.

    Merchant Center vroeg op 11 september 2026 om breedte, diepte en
    afwerking in de beschrijving van koelvriescombinaties. Dit is het
    antwoord: alleen feiten die we hebben, in een vaste, korte vorm, achter
    de gewone tekst. Leeg als er niets bekend is.
    """
    delen = []
    zin = afmetingen_zin(afmetingen_van_product(product))
    if zin:
        delen.append(zin)
    specs = {str(k).strip().lower(): v for k, v in (getattr(product, 'specs', None) or {}).items()}
    kleur = str(specs.get('kleur') or '').strip()
    if kleur and len(kleur) <= 40:
        delen.append(f'Kleur: {kleur}.')
    materiaal = str(specs.get('materiaal behuizing') or '').strip()
    if materiaal and len(materiaal) <= 40:
        delen.append(f'Afwerking: {materiaal}.')
    return ' '.join(delen)
