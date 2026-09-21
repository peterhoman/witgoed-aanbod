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


# EPREL-registers waarvan de energieklasse niet meer geldt.
#
# 'tumbledriers' is het oude drogerregister (schaal A+++ tot D). Sinds 1 juli
# 2025 dragen drogers het nieuwe label A tot G, en de nieuwe registraties
# staan in een ander register. eprel.py zoekt drogers nog in het oude op.
# Gemeten op 21 september 2026: bij alle 56 leverbare drogers met
# EPREL-gegevens toonde de pagina daardoor A+++ (41x), A++ (14x) of A+ (1x),
# met de Europese Commissie als bron, terwijl dezelfde apparaten in de winkel
# B of C dragen. In de Merchant-feed werd het nog erger: daar bleef van "A+++"
# alleen de eerste letter over en ging er "A" naar Google.
#
# De klasse uit zo'n register tonen we niet en sturen we niet mee. De overige
# gegevens (geluid, vulgewicht, afmetingen, garantie) zijn metingen en blijven
# kloppen. Valt de klasse weg, dan laat ontdubbel_specs het labelveld van de
# winkel weer staan, en dat is meestal wél de nieuwe schaal.
#
# Haal 'tumbledriers' hier pas weg als eprel.py drogers in het nieuwe register
# opzoekt EN de bestaande rijen opnieuw zijn opgehaald: de oude rijen houden
# hun oude productgroep tot ze ververst zijn, en dat is precies wat deze regel
# nodig heeft om te blijven werken.
VEROUDERDE_LABELGROEPEN = frozenset({'tumbledriers'})


def klasse_geldt_nog(productgroep):
    """Mag de energieklasse uit deze EPREL-productgroep nog getoond worden?"""
    return (productgroep or '').strip().lower() not in VEROUDERDE_LABELGROEPEN


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

    if gegevens.get('energyClass') and klasse_geldt_nog(productgroep):
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


def label_zonder_botsing(energiekosten, eprel):
    """Het gekleurde labelblokje weglaten als winkel en EPREL elkaar tegenspreken.

    Het blokje bovenaan de pagina komt uit het winkelveld "Waarde energielabel"
    (energy_costs), het blok onderaan uit EPREL. Gemeten op 21 september 2026:
    bij 241 leverbare producten zijn beide bekend en bij 33 verschillen ze. Na
    het weglaten van de vervallen drogerklasse blijven er 17 over: 13 koelkasten
    waar de winkel D zegt en het register E of F, 3 vaatwassers en 1
    was-droogcombinatie. Op die pagina's stonden twee verschillende labels.

    Wij weten niet zeker wie gelijk heeft: het register is de wettelijke opgave
    van de fabrikant, maar onze koppeling kan ook een zustermodel hebben
    gevonden. Dus beweren we bovenaan niets: het blokje valt weg, en daarmee
    ook de zin "label X kost € Y meer", die op het winkellabel was gebaseerd.
    Het EPREL-blok blijft staan, mét bron en registratienummer, zodat de
    bezoeker kan nakijken waar het label vandaan komt. De stroomkosten zelf
    blijven: die komen uit het opgegeven verbruik in kWh, niet uit de letter.
    """
    if not energiekosten or not eprel:
        return energiekosten
    officieel = next((w for l, w in eprel.get('regels', []) if l == 'Energieklasse'), None)
    winkel = (energiekosten.get('label') or '').strip().upper()
    if officieel and winkel and officieel.strip().upper() != winkel:
        uit = dict(energiekosten)
        uit['label'] = None
        uit['meerkosten_slechter_label'] = None
        return uit
    return energiekosten


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
