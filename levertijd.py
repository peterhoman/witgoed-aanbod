"""Levertijd uit een winkelfeed omrekenen naar een aantal dagen.

De feeds leveren vrije tekst, geen getal. Verzameld van de echte site:

    "Voor 23:59 besteld, morgen in huis"
    "Vandaag voor 18:00 besteld, volgende werkdag in huis"
    "Op voorraad. Voor 23:59 uur besteld, dinsdag in huis"
    "Levertijd 1-3 werkdagen"
    "1-2 werkdagen"
    "3 dagen"

Nodig om winkels met dezelfde prijs op snelheid te kunnen ordenen: als drie
winkels hetzelfde vragen, is de snelste bezorger objectief het betere aanbod
en heeft de bovenste plek een reden.

Bewust conservatief: herkennen we een tekst niet, dan komt die achteraan in
plaats van dat we een snelheid gokken.
"""
import re
from datetime import date

ONBEKEND = 99

_WEEKDAGEN = ('maandag', 'dinsdag', 'woensdag', 'donderdag',
              'vrijdag', 'zaterdag', 'zondag')


def dagen_tot_levering(tekst, vandaag=None):
    """Aantal dagen tot levering, of ONBEKEND.

    De volgorde van de regels telt. "Vandaag besteld, dinsdag in huis" bevat
    zowel "vandaag" als een weekdag; het woord "vandaag" slaat daar op het
    moment van bestellen, niet op de bezorging. Daarom kijken we eerst naar
    een weekdag en pas daarna naar losse tijdsaanduidingen.
    """
    if not tekst:
        return ONBEKEND
    laag = str(tekst).lower()
    vandaag = vandaag or date.today()

    for i, dag in enumerate(_WEEKDAGEN):
        if dag in laag:
            verschil = (i - vandaag.weekday()) % 7
            return verschil or 7          # "maandag" op maandag = volgende week

    if 'overmorgen' in laag:
        return 2
    if 'morgen' in laag:
        return 1
    if 'volgende werkdag' in laag:
        return 1
    if 'vandaag' in laag and 'in huis' in laag:
        return 0

    # "1-3 werkdagen", "2 tot 4 werkdagen", "3 dagen": de bóvengrens telt.
    # Dat is wat de winkel garandeert, en het maakt een reeks eerlijk
    # vergelijkbaar met een harde belofte: "1-3 werkdagen" hoort ná "morgen
    # in huis" te staan, niet ernaast.
    m = re.search(r'(\d+)\s*(?:-|tot|t/m|en)?\s*(\d+)?\s*(?:werk)?dag', laag)
    if m:
        return int(m.group(2) or m.group(1))

    return ONBEKEND


def snelste(offers):
    """De aanbieding met de kortste levertijd, of None bij gelijke stand."""
    if not offers:
        return None
    gesorteerd = sorted(offers, key=lambda o: dagen_tot_levering(o.delivery_time))
    beste = dagen_tot_levering(gesorteerd[0].delivery_time)
    if beste == ONBEKEND:
        return None
    zelfde = [o for o in gesorteerd if dagen_tot_levering(o.delivery_time) == beste]
    return gesorteerd[0] if len(zelfde) == 1 else None
