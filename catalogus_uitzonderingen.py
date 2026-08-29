"""Wat er niet in de catalogus hoort, en wat in een eigen categorie hoort.

Waarom dit bestaat
------------------
De 2806 eigen productteksten bleken een inspectierapport: het model keek per
product naar de werkelijke gegevens en schreef op waar het geen los apparaat
was. Dat leverde twee soorten vervuiling op.

**Vijf artikelen die geen apparaat zijn.** Een inklapbare stellingkast en een
serviesset van 48 delen onder Magnetrons, een doosje waterfilters onder
Koffiemachines, een koolstoffilter onder Afzuigkappen, een vervangborstel onder
Stofzuigers.

**Eenenvijftig artikelen die twee apparaten zijn**, meestal een wasmachine met
een droger, als een artikel verkocht.

Waarom het meer is dan netheid: beide vervuilen de catalogusmeting waar het
categoriecontext-blok en de meta-descriptions op gebouwd zijn. Op elke
wasmachinepagina staat "van de 256 andere wasmachines die wij volgen zijn er 87
duurder". Zit daar een set met een droger bij, dan is die fors duurder en
verschuift de positie van elk ander apparaat. Een serviesset doet hetzelfde met
de onderkant. Die meting is precies de eigen inhoud waarmee we die pagina's uit
"gecrawld, niet geindexeerd" proberen te krijgen -- dan moet hij kloppen.

Hoe een setje herkend wordt
---------------------------
Niet met een lijst die onderhouden moet worden, maar aan de titel. De weg
daarheen, want de eerste twee pogingen waren fout:

- Alleen " + " in de titel: 97 producten, terwijl de teksten er 37 aanwezen.
  Die plus betekent drie dingen. Een echt setje ("Bosch WGJ23400NL + Bosch
  WQJ23200NL"), een functiecombinatie van EEN apparaat ("Inbouw Oven 71 L
  Pyrolytisch + Hydrolytisch"), of een cadeautje ("Philips Airfryer NA332/00 +
  Bakmeesterset"). En bij een was-droogcombinatie is het een specificatie:
  "8 Kg + 5 1500 Rpm" -- 8 kg wassen, 5 kg drogen, een machine.
- Wat de drie wel scheidt: NA de plus staat bij een echt setje opnieuw een
  merknaam, of een typenummer. Bij een functie of een cadeautje staat daar een
  gewoon woord.

Getoetst op 40 titels uit productie: 23 setjes, 17 terecht afgewezen, geen
enkele fout in beide richtingen.
"""

import re

# De categorie waar setjes heen gaan. Bewust niet "Combinatiesets": de site
# heeft al "Wasdroogcombinaties", en dat is juist EEN machine die wast en
# droogt in een trommel. Twee bijna gelijke woorden in hetzelfde menu haalt
# niemand uit elkaar, een zoekmachine ook niet.
SETJE_SLUG = 'apparaatsets'
SETJE_NAAM = 'Apparaatsets'
SETJE_OMSCHRIJVING = ('Twee losse apparaten die als een artikel worden verkocht, '
                      'meestal een wasmachine met een bijpassende droger')

# Artikelen die geen apparaat zijn en dus niet op een witgoedvergelijker horen.
# Op EAN, want dat is de identiteit waar de syncs op matchen; een slug verandert
# zodra de winkel zijn titel aanpast.
GEBLOKKEERDE_EANS = {
    '7610917717941',   # Koffiemachines: JURA CLARIS Smart+ filter (3 stuks)
    '8721008682846',   # Magnetrons: FOXSPORT inklapbare stellingkast
    '8720364105358',   # Magnetrons: Pure Living serviesset, 48-delig
    '4251731229222',   # Afzuigkappen: Bora eSwap geurfilter GFESP
    '6976233674919',   # Stofzuigers: Dreame Tricut vervangborstel
}

# Apparaten die door de fabrikant of een autoriteit zijn TERUGGEROEPEN wegens
# een veiligheidsrisico. Apart van de lijst hierboven, want dat gaat om
# artikelen die geen apparaat zijn; dit gaat om apparaten die je niet moet
# willen kopen.
#
# Wij verkopen niets, maar we sturen mensen wél naar een winkel. Iemand die
# via ons een apparaat koopt dat in brand kan vliegen, is niet geholpen met
# "de winkel bood het aan". Dus: uit de catalogus. Google hanteert dezelfde
# regel ("Producten met een veiligheidsrisico worden wereldwijd niet getoond
# op Google") en markeerde op 29 aug 2026 de RH9958.
TERUGGEROEPEN_EANS = {
    # Rowenta X-Force Flex 14.60 -- de lithium-ionaccu kan oververhitten en
    # brand veroorzaken. Rowenta roept de accu's van het hele type 14.60
    # (en 15.60) terug; de Amerikaanse CPSC spreekt van "risk of serious
    # injury from fire and burn hazards" en adviseert het apparaat niet meer
    # te gebruiken. Alle drie de 14.60-varianten in onze catalogus geblokkeerd,
    # want het gaat om de accu die zij delen -- bij twijfel over veiligheid de
    # veilige kant kiezen.
    '3221616004573',   # Rowenta X-Force Flex 14.60 RH9958
    '3221616060449',   # Rowenta X-Force Flex 14.60 RH99A9
    '3221616104952',   # Rowenta X-Force Flex 14.60 RH99C3
}

# Merken uit de feeds. Staat een van deze namen direct na de plus, dan gaat het
# om een tweede apparaat.
_MERKEN = (
    'aeg', 'atag', 'bauknecht', 'beko', 'bella', 'bosch', 'candy', 'chiq',
    'cosori', 'delonghi', "de'longhi", 'dreame', 'dyson', 'electrolux', 'etna',
    'everglades', 'heinner', 'hisense', 'hoover', 'indesit', 'inventum', 'jura',
    'koenic', 'krups', 'lg', 'liebherr', 'miele', 'philips', 'roborock',
    'rowenta', 'sage', 'samsung', 'sharp', 'siemens', 'smeg', 'veripart',
    'whirlpool', 'wisberg', 'zanussi',
)
_MERK_PATROON = re.compile(r'(' + '|'.join(re.escape(m) for m in _MERKEN) + r')\b',
                           re.IGNORECASE)

# Een typenummer: begint met letters, bevat een cijfer, en is lang genoeg om
# geen gewoon woord te zijn. Vangt "Dh5i104bbab" in "Hisense Wf5i1045bbq
# Wasmachine + Dh5i104bbab Warmtepompdroger", en laat "Bakmeesterset",
# "uitklopbak" en "Hydrolytisch" met rust omdat daar geen cijfer in zit.
_TYPENUMMER = re.compile(r'^[a-z]{2,}[0-9][a-z0-9./-]{3,}$', re.IGNORECASE)


def is_setje(titel):
    """Verkoopt dit artikel twee losse apparaten tegelijk?"""
    tekst = str(titel or '')
    if ' + ' not in tekst:
        return False
    na_de_plus = tekst.split(' + ', 1)[1].strip()
    if not na_de_plus:
        return False
    if _MERK_PATROON.match(na_de_plus):
        return True
    eerste_woord = na_de_plus.split()[0]
    return bool(_TYPENUMMER.match(eerste_woord))


def hoort_niet_op_de_site(ean):
    """Staat dit artikel op een van de blokkeerlijsten?

    Twee redenen om iets te weren: het is geen apparaat, of het is
    teruggeroepen wegens een veiligheidsrisico. De uitkomst is dezelfde --
    het hoort niet in de catalogus.
    """
    kaal = str(ean or '').strip().lstrip('0')
    geblokkeerd = {e.lstrip('0') for e in GEBLOKKEERDE_EANS | TERUGGEROEPEN_EANS}
    return kaal in geblokkeerd


def zorg_voor_setjescategorie(db):
    """Maak de categorie Apparaatsets aan als hij nog niet bestaat."""
    from models import Category

    categorie = Category.query.filter_by(slug=SETJE_SLUG).first()
    if categorie is None:
        categorie = Category(slug=SETJE_SLUG, name=SETJE_NAAM,
                             description=SETJE_OMSCHRIJVING)
        db.session.add(categorie)
        db.session.commit()
    return categorie


def pas_toe(app):
    """Ruim geblokkeerde artikelen op en zet setjes in hun eigen categorie.

    Draait bij het opstarten en daarna elk uur. Waarom herhaald en niet een
    keer: de syncs lezen de feeds opnieuw en zetten een geblokkeerd artikel er
    zo weer in, met dezelfde verkeerde categorie. Dit trekt dat telkens recht.

    Bewust hier en niet in de zes sync-modules zelf: dat zou zes plekken zijn
    waar dezelfde regel moet blijven staan. De prijs is een venster van
    hooguit een uur waarin een net binnengekomen artikel nog verkeerd staat.
    """
    from models import Product, db

    with app.app_context():
        categorie = zorg_voor_setjescategorie(db)

        verwijderd = 0
        for product in Product.query.all():
            if hoort_niet_op_de_site(product.ean):
                db.session.delete(product)
                verwijderd += 1

        verplaatst = 0
        for product in Product.query.filter(Product.category_id != categorie.id):
            if is_setje(product.title):
                product.category_id = categorie.id
                verplaatst += 1

        # Andersom ook: staat er iets in Apparaatsets dat volgens de titel geen
        # setje (meer) is, dan hoort het daar niet te blijven staan. Zonder deze
        # kant zou een verkeerde indeling er nooit meer uit komen.
        terug = [p for p in Product.query.filter_by(category_id=categorie.id)
                 if not is_setje(p.title)]

        # Webadressen met een procentteken gaven een serverfout (8 stuks,
        # gevonden via Search Console op 4 augustus: "A -20%", "100%
        # PFAS-vrij" in de titel). De syncs bouwen zulke adressen sindsdien
        # niet meer (filter_helpers.product_slug); dit herstelt wat er al
        # stond, en vangt op wat er ooit nog eens doorheen glipt.
        from filter_helpers import URL_BREKERS, product_slug
        hersteld = 0
        for product in Product.query.all():
            if any(teken in (product.slug or '') for teken in URL_BREKERS):
                product.slug = product_slug(product.title, product.ean)
                hersteld += 1

        if verwijderd or verplaatst or hersteld:
            db.session.commit()
        return {'verwijderd': verwijderd, 'verplaatst': verplaatst,
                'webadres_hersteld': hersteld,
                'ten_onrechte_in_setjes': [p.slug for p in terug]}
