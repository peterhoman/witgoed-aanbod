"""EPREL-stap 3: de opgehaalde energielabelgegevens leesbaar op de productpagina.

65% van de catalogus had geen enkele specificatie uit de winkelfeeds; voor
1.031 apparaten staat er sinds augustus wél een EPREL-rij met de opgave van
de fabrikant zelf. Dit bestand vertaalt die rij naar Nederlandse regels
("Geluidsniveau: 44 dB") en naar badges die doorlinken naar de
kenmerk-filterpagina's die op dezelfde indeling gebouwd zijn.

Twee regels uit de EPREL-licentie zijn hier zichtbaar:
- de bronvermelding onder het blok is verplicht, dus die hoort bij het blok
  en niet bij de opmaak;
- het "opgehaald op"-moment staat erbij omdat de gegevens actueel gehouden
  moeten worden (de routine ververst rijen ouder dan 30 dagen).

Eenheden verschillen per productgroep: ratedCapacity is kilo's bij
wasmachines en drogers maar couverts bij vaatwassers, en afmetingen staan
bij koelkasten in millimeters (zie routes.main._eprel_waarde).
"""


def _fmt_klasse(klasse):
    """EPREL schrijft A+++ als APPP; op het label staat A+++."""
    return {'APPP': 'A+++', 'APP': 'A++', 'AP': 'A+'}.get(klasse, klasse)


def _getal(waarde):
    """1400 -> '1400', 9.5 -> '9,5', 55.0 -> '55'."""
    afgerond = round(float(waarde), 1)
    if afgerond == int(afgerond):
        return str(int(afgerond))
    return str(afgerond).replace('.', ',')


def _regels(gegevens, productgroep):
    """[(label, waarde), ...] in vaste volgorde, alleen wat er echt is."""
    uit = []

    def voeg(label, tekst):
        uit.append((label, tekst))

    if gegevens.get('energyClass'):
        voeg('Energieklasse', _fmt_klasse(gegevens['energyClass']))
    if gegevens.get('noise') is not None:
        tekst = f"{_getal(gegevens['noise'])} dB"
        if gegevens.get('noiseClass'):
            tekst += f" (geluidsklasse {gegevens['noiseClass']})"
        voeg('Geluidsniveau', tekst)
    if gegevens.get('waterCons') is not None:
        voeg('Waterverbruik per beurt', f"{_getal(gegevens['waterCons'])} liter")
    if gegevens.get('energyConsPer100Cycle') is not None:
        voeg('Stroomverbruik per 100 beurten',
             f"{_getal(gegevens['energyConsPer100Cycle'])} kWh")
    elif gegevens.get('energyConsPerCycle') is not None:
        voeg('Stroomverbruik per beurt',
             f"{_getal(gegevens['energyConsPerCycle'])} kWh")
    if gegevens.get('annualEnergyConsumption') is not None:
        voeg('Stroomverbruik per jaar',
             f"{_getal(gegevens['annualEnergyConsumption'])} kWh")

    if gegevens.get('ratedCapacity') is not None:
        if (productgroep or '').startswith('dishwashers'):
            voeg('Aantal couverts', _getal(gegevens['ratedCapacity']))
        else:
            voeg('Vulgewicht', f"{_getal(gegevens['ratedCapacity'])} kg")
    if gegevens.get('spinSpeedRated') is not None:
        tekst = f"{_getal(gegevens['spinSpeedRated'])} toeren per minuut"
        if gegevens.get('spinClass'):
            tekst += f" (centrifugeklasse {gegevens['spinClass']})"
        voeg('Centrifugetoerental', tekst)

    if gegevens.get('totalVolume') is not None:
        voeg('Inhoud', f"{_getal(gegevens['totalVolume'])} liter")
    if gegevens.get('fridgeVolume') is not None:
        voeg('Koelgedeelte', f"{_getal(gegevens['fridgeVolume'])} liter")
    if gegevens.get('freezerVolume') is not None:
        voeg('Vriesgedeelte', f"{_getal(gegevens['freezerVolume'])} liter")
    if gegevens.get('cavityVolume') is not None:
        voeg('Inhoud ovenruimte', f"{_getal(gegevens['cavityVolume'])} liter")
    if gegevens.get('airflow') is not None:
        voeg('Luchtafvoer', f"{_getal(gegevens['airflow'])} m³ per uur")
    if gegevens.get('climateClass'):
        voeg('Klimaatklasse', str(gegevens['climateClass']))

    # Afmetingen pas na de maatcorrectie (koelkasten staan in millimeters).
    from routes.main import _eprel_waarde
    maten = [_eprel_waarde(gegevens, veld) for veld in
             ('dimensionWidth', 'dimensionHeight', 'dimensionDepth')]
    if all(m is not None for m in maten):
        voeg('Afmetingen (b × h × d)',
             ' × '.join(_getal(m) for m in maten) + ' cm')

    if gegevens.get('guaranteeDuration') is not None:
        maanden = int(gegevens['guaranteeDuration'])
        if maanden > 0:
            tekst = (f"{maanden // 12} jaar" if maanden % 12 == 0
                     else f"{maanden} maanden")
            voeg('Fabrieksgarantie', tekst)
    return uit


def _badges(product, gegevens):
    """Badges die doorlinken naar kenmerkpagina's die écht bestaan.

    Zelfde indeling en dezelfde ondergrens als de kenmerkpagina's zelf
    (routes.main._kenmerk_facet): een badge kan dus nooit naar een 404
    wijzen, en verdwijnt vanzelf als de pagina erachter verdwijnt.
    """
    from routes.main import (_FILTERVELDEN, _eprel_waarde, _kenmerk_facet,
                             _stap_voor)
    categorie = product.category
    if categorie is None:
        return []
    facet = _kenmerk_facet(categorie)
    uit = []
    for veld, opzet in _FILTERVELDEN.items():
        waarde = _eprel_waarde(gegevens, veld)
        if waarde is None:
            continue
        stap = _stap_voor(waarde, opzet)
        if stap and (opzet['naam'], stap['slug']) in facet:
            uit.append({
                'naam': opzet['naam'],
                'label': stap['label'],
                'url': f"/category/{categorie.slug}/{opzet['naam']}/{stap['slug']}",
            })
    return uit


# Waar het EPREL-blok een gegeven toont, verdwijnt het gelijknamige feedveld
# uit de specificatielijst: twee keer "afmetingen" met verschillende getallen
# op één pagina ondergraaft precies het vertrouwen dat het EPREL-blok moet
# geven (designrapport 6 aug, punt 5). EPREL wint, want dat is de opgave van
# de fabrikant zelf, mét eenheid. Sleutel = EPREL-regelnaam, waarde =
# zoektermen in de feed-labelnaam (kleine letters, bewust smal gekozen:
# "Inhoud" staat er niet in, want "Inhoud trommel" is iets anders dan de
# koelkastinhoud).
_FEEDVELD_DUBBEL = {
    'Afmetingen (b × h × d)': ('afmeting',),
    'Geluidsniveau': ('geluidsniveau',),
    'Energieklasse': ('energielabel', 'energieklasse'),
    'Waterverbruik per beurt': ('waterverbruik',),
    'Centrifugetoerental': ('toerental',),
    'Vulgewicht': ('vulgewicht',),
}


def ontdubbel_specs(eprel, kern, groepen):
    """(kernspecs, spec_groepen) zonder de velden die EPREL al toont."""
    if not eprel:
        return kern, groepen
    eprel_labels = {label for label, _ in eprel['regels']}
    termen = [term for label, zoek in _FEEDVELD_DUBBEL.items()
              if label in eprel_labels for term in zoek]
    if not termen:
        return kern, groepen

    def blijft(label):
        laag = (label or '').lower()
        return not any(term in laag for term in termen)

    kern = [(label, waarde) for label, waarde in kern if blijft(label)]
    uit = []
    for groep, rijen in groepen:
        rijen = [(label, waarde) for label, waarde in rijen if blijft(label)]
        if rijen:
            uit.append((groep, rijen))
    return kern, uit


def eprel_blok(product):
    """Alles wat de sjabloon nodig heeft, of None (dan valt het blok weg)."""
    from models import EprelData

    rij = EprelData.query.filter_by(product_id=product.id,
                                    gevonden=True).first()
    if rij is None:
        return None
    gegevens = rij.gegevens or {}
    regels = _regels(gegevens, rij.productgroep)
    if not regels:
        return None

    nummer = (rij.registratienummer or '').strip()
    url = None
    if nummer and rij.productgroep:
        url = f"https://eprel.ec.europa.eu/screen/product/{rij.productgroep}/{nummer}"
    return {
        'regels': regels,
        'badges': _badges(product, gegevens),
        'registratienummer': nummer or None,
        'url': url,
        'opgehaald': rij.opgehaald_at.strftime('%d-%m-%Y') if rij.opgehaald_at else None,
    }
