"""Geschreven tekst per subpagina: titel, kop, intro, uitleg, vragen, links.

Waarom dit bestaat (3 oktober 2026)
-----------------------------------
De subpagina's van een categorie (type, geluid, vulgewicht, kenmerk) hadden
22 tot 41 woorden tekst en kromme titels ("Warmtepompdroger Drogers"). Voor
het drogerseizoen leverde Peters SEO-chat per pagina een eigen tekst aan:
kop, intro, een uitlegblok onder de productlijst, zichtbare veelgestelde
vragen en links naar de verwante pagina's. Peter gaf er op 3 oktober ja op.

Hoe het werkt
- Sleutel is het pad: (categorie-slug, soort, waarde-slug), bijvoorbeeld
  ('drogers', 'type', 'warmtepompdroger'). routes.main._render_facet_page
  zoekt de tekst op en geeft hem aan templates/category.html.
- In 'titel' en 'intro' mogen {n} (aantal modellen), {vanaf} (laagste prijs
  in hele euro's) en {winkels} (aantal aangesloten winkels) staan. Die
  worden bij elke weergave uit de live data ingevuld. Geen vaste bedragen
  of aantallen in de tekst zelf: die verouderen.
- 'uitleg' is een lijst (tussenkop, [alinea's]); 'vragen' een lijst
  (vraag, antwoord). De vragen staan zichtbaar op de pagina; er is bewust
  geen FAQ-schema bij (Google toont dat sinds mei 2026 niet meer).
- Een nieuwe ronde (smalle vaatwassers, koelkasten op hoogte, ...) is een
  nieuw blok in TEKSTEN plus een regel in BEKIJK_OOK; de code hoeft er niet
  voor te veranderen.

Kernregel van de site geldt ook hier: beweer niets wat de pagina niet
waarmaakt. Voorbeeld: de aangeleverde tekst zei "sorteer de lijst op
geluid", maar de lijst sorteert alleen op prijs; dat antwoord is aangepast.
"""

# Gewone naam voor type-pagina's (kop en titel). De waarde uit de winkelfeed
# is enkelvoud ("Warmtepompdroger"); met de categorienaam erachter werd dat
# "Warmtepompdroger Drogers".
TYPE_NAMEN = {
    'warmtepompdroger': 'Warmtepompdrogers',
    'condensdroger': 'Condensdrogers',
    'luchtafvoerdroger': 'Luchtafvoerdrogers',
    'voorlader': 'Voorladers',
    'bovenlader': 'Bovenladers',
}

TEKSTEN = {
    ('drogers', 'type', 'warmtepompdroger'): {
        'titel': 'Warmtepompdrogers vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Warmtepompdrogers vergelijken',
        'naam': 'warmtepompdrogers',  # voor de vragenkop
        'intro': ('Een warmtepompdroger is de zuinigste soort wasdroger. Hij hergebruikt de '
                  'warme lucht in plaats van die weg te blazen en verbruikt daardoor ruwweg de '
                  'helft van de stroom van een gewone condensdroger. Wij volgen {n} '
                  'warmtepompdrogers en zetten per model de laagste prijs van {winkels} winkels '
                  'naast elkaar, met het prijsverloop en de officiële gegevens van het '
                  'energielabel.'),
        'uitleg': [
            ('Hoe werkt een warmtepompdroger?', [
                'Een warmtepompdroger droogt met lucht van ongeveer 50 graden, veel lager dan '
                'een condensdroger. Het vocht uit de was wordt opgevangen in een reservoir of '
                'via een slangetje afgevoerd. De warmte blijft in de machine en wordt opnieuw '
                'gebruikt. Dat is zuinig en beter voor je kleding, maar een droogbeurt duurt '
                'wat langer.']),
            ('Waar let je op?', [
                'Vulgewicht: 7 tot 8 kg is genoeg voor een of twee personen, 8 tot 9 kg voor '
                'een gezin. Neem een droger die minstens zoveel aankan als je wasmachine.',
                'Energielabel: sinds 1 juli 2025 hebben drogers een nieuw label van A tot G. '
                'De oude A+++ bestaat niet meer; een goede warmtepompdroger heeft nu label A, '
                'B of C.',
                'Geluid: de meeste warmtepompdrogers maken 62 tot 66 decibel. Staat de droger '
                'in of naast een leefruimte, kijk dan naar de stille modellen.',
                'Condensor: bij sommige modellen maak je de condensor zelf schoon, bij andere '
                'gaat dat automatisch. Een vervuilde condensor kost stroom.']),
            ('Wat kost een warmtepompdroger in gebruik?', [
                'Dat hangt af van het model en hoe vaak je droogt. Op de productpagina staat, '
                'waar het energielabel bekend is, wat het apparaat per jaar aan stroom kost en '
                'wat aanschaf plus stroom over tien jaar samen kosten. Zo zie je of een '
                'duurder, zuiniger model zich terugverdient.']),
        ],
        'vragen': [
            ('Heeft een warmtepompdroger een afvoer nodig?',
             'Nee. Het water komt in een reservoir dat je na het drogen leegt. Je kunt de '
             'meeste modellen ook op de afvoer aansluiten, dan hoef je niets te legen.'),
            ('Is een warmtepompdroger de meerprijs waard?',
             'Wie een paar keer per week droogt, verdient de meerprijs ten opzichte van een '
             'condensdroger meestal binnen enkele jaren terug via de stroomrekening.'),
            ('Hoe lang duurt een droogbeurt?',
             'Langer dan bij een condensdroger: reken op twee tot drie uur voor een volle '
             'trommel katoen.'),
            ('Mag een warmtepompdroger in een koude schuur staan?',
             'Liever niet. Onder de 5 tot 10 graden werkt de warmtepomp slecht. Zet hem in '
             'een ruimte die boven die temperatuur blijft.'),
            ('Waarom verschilt de prijs per winkel?',
             'Winkels bepalen hun eigen prijs en passen die vaak aan. Voor hetzelfde apparaat '
             'zien wij regelmatig tientallen euro\'s verschil. Daarom tonen we alle winkels '
             'naast elkaar.'),
        ],
    },
    ('drogers', 'geluid', 'stil'): {
        'titel': 'Stille drogers: {n} modellen onder 60 dB vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Stille drogers (onder 60 dB)',
        'naam': 'stille drogers',  # voor de vragenkop
        'intro': ('Een stille droger maakt minder dan 60 decibel, ongeveer het geluid van een '
                  'gesprek. Dat scheelt als de droger in de badkamer, de keuken of naast een '
                  'slaapkamer staat. Wij volgen {n} stille drogers. Het geluidsniveau komt uit '
                  'het officiële Europese energielabelregister (EPREL), dus het is door de '
                  'fabrikant opgegeven en niet door de winkel.'),
        'uitleg': [
            ('Hoeveel decibel is stil?', [
                'Het energielabel van een droger vermeldt het geluid in decibel en een '
                'geluidsklasse van A tot D. De meeste drogers zitten tussen 62 en 66 decibel. '
                'Onder de 60 decibel noemen wij een droger stil. Elke 3 decibel minder '
                'halveert de geluidsenergie, dus het verschil tussen 59 en 65 decibel is goed '
                'te horen.']),
            ('Waardoor is de ene droger stiller dan de andere?', [
                'Vooral door de motor en de isolatie van de kast. Warmtepompdrogers met een '
                'inverter-motor zijn doorgaans het stilst. Ook de plek telt: een droger op een '
                'harde, holle vloer klinkt luider dan op een stevige ondergrond.']),
        ],
        'vragen': [
            # Aangeleverd antwoord was "sorteer de lijst op geluid"; de lijst
            # sorteert alleen op prijs, dus dat klopte niet.
            ('Wat is de stilste droger?',
             'Dat wisselt met het aanbod. Het geluidsniveau in decibel staat bij elk model op '
             'de productpagina, bij de gegevens van het energielabel.'),
            ('Is een stille droger duurder?',
             'Vaak wel iets, omdat stille modellen meestal ook de zuinigere warmtepompdrogers '
             'zijn. Het prijsverloop per model laat zien wanneer hij het goedkoopst was.'),
            ('Helpt een antivibratiemat?',
             'Tegen trillingen op een houten vloer wel. Aan het geluid van de trommel en de '
             'motor verandert het weinig.'),
        ],
    },
    ('drogers', 'vulgewicht', '8-9-kg'): {
        'titel': 'Droger 8 kg en 9 kg: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Drogers van 8 en 9 kg',
        'naam': 'drogers van 8 en 9 kg',  # voor de vragenkop
        'intro': ('Een droger van 8 of 9 kg is de maat voor een gezin: er past een volle '
                  'wasmachinetrommel in, inclusief dekbedovertrek of handdoeken. Wij volgen '
                  '{n} drogers met dit vulgewicht en tonen per model de laagste prijs van '
                  '{winkels} winkels. Het vulgewicht komt uit het officiële Europese '
                  'energielabelregister (EPREL).'),
        'uitleg': [
            ('8 kg of 9 kg?', [
                'Kies een droger die minstens evenveel aankan als je wasmachine, anders moet '
                'je een was in tweeën drogen. Bij een wasmachine van 8 kg past een droger van '
                '8 kg; was je met 9 of 10 kg, neem dan 9 kg. Een grotere trommel droogt ook '
                'gelijkmatiger en kreukt minder, omdat de was meer ruimte heeft.']),
            ('Verbruikt een grotere droger meer?', [
                'Per beurt iets, maar per kilo was juist minder als je de trommel goed vult. '
                'Het energielabel rekent met een standaardprogramma; de stroomkosten per jaar '
                'staan op de productpagina, waar het energielabel bekend is.']),
        ],
        'vragen': [
            ('Hoeveel kg droger heb ik nodig voor 4 personen?',
             '8 kg is voor de meeste gezinnen van vier genoeg; 9 kg als je vaak beddengoed en '
             'handdoeken droogt.'),
            ('Past een droger van 9 kg op een wasmachine?',
             'Ja, de buitenmaten zijn vrijwel gelijk aan die van kleinere modellen (60 cm '
             'breed). Gebruik een tussenstuk van hetzelfde merk.'),
            ('Is 9 kg veel duurder dan 8 kg?',
             'Meestal een paar tientjes. In de lijst zie je beide maten naast elkaar op prijs.'),
        ],
    },
    ('drogers', 'kenmerk', 'zonder-afvoer'): {
        'titel': 'Droger zonder afvoer: {n} modellen met waterreservoir | WitgoedAanbod.nl',
        'h1': 'Drogers zonder afvoer',
        'naam': 'drogers zonder afvoer',  # voor de vragenkop
        'intro': ('Geen afvoer of raam in de buurt? Dan heb je een condensdroger of '
                  'warmtepompdroger nodig. Die vangen het vocht op in een reservoir dat je na '
                  'het drogen leegt, en hoeven dus niet op een afvoer of naar buiten te worden '
                  'aangesloten. Wij volgen {n} drogers zonder afvoer.'),
        'uitleg': [
            ('Welke drogers hebben geen afvoer nodig?', [
                'Er zijn drie soorten drogers. Een luchtafvoerdroger blaast de vochtige lucht '
                'via een slang naar buiten en heeft dus wel een afvoer nodig. Een condensdroger '
                'en een warmtepompdroger zetten het vocht om in water en bewaren dat in een '
                'opvangbak. Die twee kun je overal neerzetten waar een stopcontact is.']),
            ('Condensdroger of warmtepompdroger?', [
                'Beide werken zonder afvoer. De warmtepompdroger is duurder in aanschaf maar '
                'verbruikt ongeveer de helft van de stroom. De condensdroger is goedkoper en '
                'droogt iets sneller, maar wordt steeds minder verkocht. Meer hierover in onze '
                'gids "Warmtepompdroger of condensdroger".']),
            ('Waar zet je een droger zonder afvoer neer?', [
                'In een ruimte die niet te koud wordt en waar de lucht weg kan: een bijkeuken, '
                'badkamer of zolder met een rooster of raam dat af en toe open kan. De droger '
                'geeft wat warmte en vocht af aan de ruimte.']),
        ],
        'vragen': [
            ('Moet ik het waterreservoir elke keer legen?',
             'Ja, na elke droogbeurt. Vergeet je het, dan stopt de droger vanzelf als de bak '
             'vol is.'),
            ('Kan een droger zonder afvoer toch op de afvoer?',
             'Bij de meeste modellen wel: er zit een slangetje bij waarmee je het water '
             'rechtstreeks kunt lozen.'),
            ('Kan een droger zonder afvoer in een kast?',
             'Alleen met voldoende ventilatie rondom. Kijk in de handleiding naar de minimale '
             'vrije ruimte.'),
            ('Wordt mijn kamer vochtig van een condensdroger?',
             'Een beetje. Zorg voor ventilatie; een warmtepompdroger geeft minder warmte en '
             'vocht af dan een condensdroger.'),
        ],
    },
}

# "Bekijk ook" per categorie: (linktekst, pad). De pagina zelf valt bij het
# tonen vanzelf weg; een link naar een pagina die (nog) niet bestaat ook
# (routes.main controleert dat bij de kenmerk- en typepagina's niet, dus
# zet hier alleen pagina's die er zijn).
BEKIJK_OOK = {
    'drogers': [
        ('Warmtepompdrogers', '/category/drogers/type/warmtepompdroger'),
        ('Stille drogers', '/category/drogers/geluid/stil'),
        ('Drogers van 8 en 9 kg', '/category/drogers/vulgewicht/8-9-kg'),
        ('Drogers zonder afvoer', '/category/drogers/kenmerk/zonder-afvoer'),
        ('Gids: warmtepompdroger of condensdroger', '/gidsen/warmtepompdroger-of-condensdroger'),
        ('Alle drogers', '/category/drogers'),
    ],
}


def tekst_voor(pad, n, vanaf, winkels):
    """De ingevulde tekst voor dit pad, of None als er geen geschreven tekst is.

    `vanaf` mag None zijn (geen prijs bekend): dan vervalt het stuk
    " vanaf € ..." uit de titel in plaats van "vanaf € None" te tonen.
    """
    ruw = TEKSTEN.get(tuple(pad) if pad else None)
    if not ruw:
        return None
    titel = ruw['titel']
    if vanaf is None:
        titel = titel.replace(' vanaf € {vanaf}', '')
    waarden = {'n': n, 'vanaf': vanaf, 'winkels': winkels}
    eigen = '/category/' + '/'.join(pad)
    return {
        'titel': titel.format(**waarden),
        'h1': ruw['h1'],
        # Korte naam voor 'Veelgestelde vragen over ...'; de hele h1 las daar
        # stroef ('... over warmtepompdrogers vergelijken'). Zonder naam: de h1
        # met een kleine eerste letter.
        'naam': ruw.get('naam') or ruw['h1'][:1].lower() + ruw['h1'][1:],
        'intro': ruw['intro'].format(**waarden),
        'uitleg': ruw['uitleg'],
        'vragen': ruw['vragen'],
        'bekijk_ook': [(t, p) for t, p in BEKIJK_OOK.get(pad[0], []) if p != eigen],
    }
