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
- Sinds ronde 2 (4 okt 2026) mag een blok ook alleen 'titel', 'vragen' en
  een eigen 'bekijk_ook' hebben: de zoekzin-pagina's uit zoekkenmerken.py
  houden dan hun eigen kop, intro en uitleg. 'bekijk_ook' in een blok gaat
  voor de lijst per categorie in BEKIJK_OOK.

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
        # Tot 4 okt 2026 "Drogers van 8 en 9 kg", maar de stap is 8 <= x < 9
        # (routes.main._FILTERVELDEN): 9 kg staat op /9-11-kg. Het adres blijft.
        'titel': 'Droger 8 kg: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Drogers van 8 kg',
        'naam': 'drogers van 8 kg',  # voor de vragenkop
        'intro': ('Een droger van 8 kg is de maat voor de meeste gezinnen: er past een volle '
                  'trommel uit een wasmachine van 8 kg in, inclusief handdoeken of een '
                  'dekbedovertrek. Wij volgen {n} drogers van 8 kg en tonen per model de '
                  'laagste prijs van {winkels} winkels.'),
        'uitleg': [
            ('8 kg of toch 9 kg?', [
                'Kies een droger die minstens evenveel aankan als je wasmachine, anders moet '
                'je een was in tweeën drogen. Bij een wasmachine van 8 kg past een droger van '
                '8 kg; was je met 9 of 10 kg, kijk dan bij de drogers van 9 en 10 kg. Een '
                'grotere trommel droogt ook gelijkmatiger en kreukt minder, omdat de was meer '
                'ruimte heeft.']),
            ('Verbruikt een grotere droger meer?', [
                'Per beurt iets, maar per kilo was juist minder als je de trommel goed vult. '
                'Het energielabel rekent met een standaardprogramma; de stroomkosten per jaar '
                'staan op de productpagina, waar het energielabel bekend is.']),
        ],
        'vragen': [
            ('Hoeveel kg droger heb ik nodig voor 4 personen?',
             '8 kg is voor de meeste gezinnen van vier genoeg; 9 kg als je vaak beddengoed en '
             'handdoeken droogt.'),
            ('Past een droger van 8 kg op een wasmachine?',
             'Ja, drogers en wasmachines zijn vrijwel altijd 60 cm breed. Gebruik een '
             'tussenstuk van hetzelfde merk.'),
            ('Is 9 kg veel duurder dan 8 kg?',
             'Meestal een paar tientjes. Vergelijk de prijzen met de pagina voor drogers van 9 '
             'en 10 kg.'),
        ],
    },
    # Stap 9 <= x < 11: 9 en 10 kg.
    ('drogers', 'vulgewicht', '9-11-kg'): {
        'titel': 'Droger 9 kg en 10 kg: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Drogers van 9 en 10 kg',
        'naam': 'drogers van 9 en 10 kg',
        'intro': ('Een droger van 9 of 10 kg past bij een wasmachine van dezelfde maat en bij '
                  'gezinnen die veel beddengoed, handdoeken of grote wassen drogen. De was heeft '
                  'meer ruimte, droogt gelijkmatiger en kreukt minder. Wij volgen {n} drogers van '
                  '9 en 10 kg, met per model de laagste prijs van {winkels} winkels.'),
        'vragen': [
            ('Past een droger van 9 kg op een wasmachine?',
             'Ja, de breedte is gelijk aan die van kleinere modellen (60 cm). Gebruik een '
             'tussenstuk van hetzelfde merk en let op de diepte.'),
            ('Is een droger van 10 kg zuinig als ik hem niet vol doe?',
             'Per kilo was is een volle trommel het zuinigst. Droog je meestal kleine wassen, '
             'dan is 8 kg een betere maat.'),
        ],
        'bekijk_ook': [
            ('Drogers van 8 kg', '/category/drogers/vulgewicht/8-9-kg'),
            ('Warmtepompdrogers', '/category/drogers/type/warmtepompdroger'),
            ('Drogers zonder afvoer', '/category/drogers/kenmerk/zonder-afvoer'),
            ('Alle drogers', '/category/drogers'),
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

    # ------------------------------------------------------------------
    # Ronde 2 (specialist-chat, 4 okt 2026; Peter zei 3 okt ja op
    # kenmerkpagina's in fases). Deel A: maatpagina's met volledige tekst.
    # "zeven winkels" uit de aanlevering is {winkels} geworden.
    # ------------------------------------------------------------------
    # Vulgewicht-stappen zijn van <= x < tot: /8-9-kg is 8 kg, /9-11-kg is 9 en 10 kg.
    ('wasmachines', 'vulgewicht', '8-9-kg'): {
        'titel': 'Wasmachine 8 kg: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Wasmachines van 8 kg',
        'naam': 'wasmachines van 8 kg',
        'intro': ('Een wasmachine van 8 kg is de meest gekozen maat voor een gezin. Er past een '
                  'dekbedovertrek met lakens in, of de was van drie tot vier personen in een paar '
                  'beurten per week. Wij volgen {n} wasmachines van 8 kg; het vulgewicht komt uit '
                  'het officiële Europese energielabelregister en bij elk model staat de laagste '
                  'prijs van {winkels} winkels.'),
        'uitleg': [
            ('8 kg of toch 9 kg?', [
                'Voor twee tot vier personen is 8 kg ruim genoeg. Was je vaak beddengoed, '
                'handdoeken of sportkleding van een groter gezin, dan scheelt 9 kg je al snel een '
                'wasbeurt per week; die staan op de pagina voor wasmachines van 9 en 10 kg. De '
                'buitenmaten zijn gelijk: vrijwel elke wasmachine is 60 cm breed en 85 cm hoog. '
                'Een grotere trommel is wel vaak een paar centimeter dieper.']),
            ('Verbruikt een grotere wasmachine meer?', [
                'Per wasbeurt iets meer stroom en water, maar per kilo was minder, mits je de '
                'trommel vult. Moderne machines wegen de was en passen het waterverbruik aan. Het '
                'energielabel rekent per honderd wasbeurten; op elke productpagina staan de '
                'stroomkosten per jaar.']),
        ],
        'vragen': [
            ('Hoeveel kg wasmachine heb ik nodig voor 4 personen?',
             '8 kg is voor de meeste gezinnen van vier genoeg. Kies 9 kg als je vaak grote stukken '
             'wast of minder vaak wilt draaien.'),
            ('Past een dekbed in een wasmachine van 8 kg?',
             'Een eenpersoons synthetisch dekbed meestal wel. Voor een tweepersoons dekbed is 9 kg '
             'of meer veiliger; kijk ook naar het wasvoorschrift van het dekbed.'),
            ('Is een wasmachine van 9 kg groter dan een van 8 kg?',
             'In breedte en hoogte niet. De diepte kan enkele centimeters verschillen; die staat '
             'bij de specificaties van elk model.'),
        ],
        'bekijk_ook': [
            ('Wasmachines van 9 en 10 kg', '/category/wasmachines/vulgewicht/9-11-kg'),
            ('Wasmachines van 7 kg', '/category/wasmachines/vulgewicht/7-8-kg'),
            ('Wasmachines 1400-1600 toeren', '/category/wasmachines/toerental/1400-1600-toeren'),
            ('Wasmachine met stoomfunctie', '/category/wasmachines/kenmerk/stoomfunctie'),
            ('Gids: wasmachine 8 of 9 kg', '/gidsen/wasmachine-8-of-9-kg'),
            ('Alle wasmachines', '/category/wasmachines'),
        ],
    },
    ('wasmachines', 'vulgewicht', '9-11-kg'): {
        'titel': 'Wasmachine 9 kg en 10 kg: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Wasmachines van 9 en 10 kg',
        'naam': 'wasmachines van 9 en 10 kg',
        'intro': ('Een wasmachine van 9 of 10 kg is bedoeld voor grotere gezinnen en voor wie zelf '
                  'dekbedden, gordijnen of werkkleding wast. Je draait minder beurten per week, en '
                  'dat scheelt tijd. Wij volgen {n} wasmachines van 9 en 10 kg, met per model de '
                  'laagste prijs van {winkels} winkels en de gegevens van het energielabel.'),
        'uitleg': [
            ('Voor wie is 9 of 10 kg zinvol?', [
                'Voor huishoudens van vier of meer personen, of als je grote stukken in één keer '
                'wilt wassen. Voor een of twee personen is zo\'n trommel meestal te groot: '
                'halfvolle beurten zijn per kilo was minder zuinig, ook al past de machine het '
                'water aan.']),
            ('Waar let je op bij een grote wasmachine?', [
                'Op de diepte: grote trommels maken de machine dieper, soms meer dan 60 cm. Meet '
                'de plek op, inclusief ruimte voor de slangen. Kijk ook naar het toerental en het '
                'geluid bij centrifugeren, want een volle trommel van 10 kg is zwaar.']),
        ],
        'vragen': [
            ('Kan een tweepersoons dekbed in een wasmachine van 10 kg?',
             'Een synthetisch tweepersoons dekbed past doorgaans in 10 kg. Voor dons en extra '
             'dikke dekbedden blijft een wasserette met een grotere trommel de veiligste keuze.'),
            ('Is een wasmachine van 10 kg duurder in gebruik?',
             'Alleen als je hem halfleeg laat draaien. Goed gevuld is het verbruik per kilo was '
             'lager dan bij een kleinere machine.'),
            ('Past een wasmachine van 10 kg onder een aanrecht?',
             'De hoogte is meestal 85 cm, net als bij kleinere modellen, maar de diepte kan het '
             'probleem zijn. Controleer de maten bij het model.'),
        ],
        'bekijk_ook': [
            ('Wasmachines van 8 kg', '/category/wasmachines/vulgewicht/8-9-kg'),
            ('Wasmachines vanaf 11 kg', '/category/wasmachines/vulgewicht/vanaf-11-kg'),
            ('Drogers van 9 en 10 kg', '/category/drogers/vulgewicht/9-11-kg'),
            ('Alle wasmachines', '/category/wasmachines'),
        ],
    },
    # Stap 45 <= x < 60 dB; "stil" hoort bij /zeer-stil (onder 45 dB), dus
    # hier een neutrale naam.
    ('vaatwassers', 'geluid', 'stil'): {
        'titel': 'Vaatwassers 45-60 dB: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Vaatwassers van 45 tot 60 dB',
        'naam': 'vaatwassers van 45 tot 60 dB',
        'intro': ('De meeste vaatwassers maken 45 tot 50 decibel: goed hoorbaar in een open '
                  'keuken, maar geen probleem achter een dichte deur. Wij volgen {n} vaatwassers in '
                  'deze klasse. Zoek je een model dat je nauwelijks hoort, kijk dan bij de stille '
                  'vaatwassers onder 45 dB.'),
        'bekijk_ook': [
            ('Stille vaatwassers onder 45 dB', '/category/vaatwassers/geluid/zeer-stil'),
            ('Inbouw vaatwassers', '/category/vaatwassers/kenmerk/inbouw'),
            ('Alle vaatwassers', '/category/vaatwassers'),
        ],
    },
    ('wasmachines', 'toerental', '1400-1600-toeren'): {
        'titel': 'Wasmachine 1400 toeren: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Wasmachines met 1400 tot 1600 toeren',
        'naam': 'wasmachines met 1400 toeren',
        'intro': ('Het toerental bepaalt hoe droog je was uit de machine komt. Met 1400 toeren '
                  'per minuut is de was droog genoeg om snel aan de lijn of in de droger te '
                  'drogen, zonder dat stoffen onnodig kreuken. Het is de meest verkochte klasse. '
                  'Wij volgen {n} wasmachines met 1400 tot 1600 toeren.'),
        'uitleg': [
            ('1400 of 1600 toeren?', [
                'Bij 1600 toeren blijft er nog iets minder vocht in de was dan bij 1400. Dat '
                'merk je vooral als je daarna de droger gebruikt: die is sneller klaar en '
                'verbruikt minder. Hang je de was altijd op, dan is het verschil klein en is '
                '1400 toeren ruim voldoende.']),
            ('Nadelen van een hoog toerental', [
                'Harder centrifugeren geeft meer kreuken en meer geluid. Vrijwel elke machine '
                'laat je het toerental per programma lager zetten, dus je kunt voor fijne was '
                'altijd terug naar 800 of 1000 toeren.']),
        ],
        'vragen': [
            ('Is 1400 toeren genoeg?',
             'Ja, voor de meeste huishoudens. De was komt er goed uitgewrongen uit en droogt vlot.'),
            ('Is 1600 toeren slechter voor mijn kleding?',
             'Voor katoen en handdoeken niet. Voor fijne stoffen en wol kies je een programma met '
             'een lager toerental.'),
            ('Scheelt een hoger toerental stroom?',
             'In de wasmachine zelf nauwelijks. De winst zit in de droger, die minder lang hoeft '
             'te draaien.'),
        ],
        'bekijk_ook': [
            ('Wasmachines vanaf 1600 toeren', '/category/wasmachines/toerental/vanaf-1600-toeren'),
            ('Wasmachines 1200-1400 toeren', '/category/wasmachines/toerental/1200-1400-toeren'),
            ('Wasmachines van 8 kg', '/category/wasmachines/vulgewicht/8-9-kg'),
            ('Warmtepompdrogers', '/category/drogers/type/warmtepompdroger'),
            ('Alle wasmachines', '/category/wasmachines'),
        ],
    },
    ('koelkasten', 'breedte', 'smal'): {
        'titel': 'Smalle koelkast: {n} modellen tot 50 cm breed vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Smalle koelkasten (tot 50 cm breed)',
        'naam': 'smalle koelkasten',
        'intro': ('Een smalle koelkast is hooguit 50 cm breed en past op plekken waar een gewone '
                  'kast van 60 cm niet kan staan: een kleine keuken, een studentenkamer, kantoor '
                  'of bijkeuken. Wij volgen {n} smalle koelkasten. De breedte komt uit het '
                  'officiële Europese energielabelregister.'),
        'uitleg': [
            ('Welke maten zijn er?', [
                'De meeste smalle koelkasten zijn 45 tot 50 cm breed. Daaronder vallen '
                'tafelmodellen van ongeveer 85 cm hoog, die onder een werkblad passen, en hoge '
                'smalle koel-vriescombinaties. Let naast de breedte op de diepte en op de '
                'draairichting van de deur; bij veel modellen kun je de deur omzetten.']),
            ('Hoeveel inhoud houd je over?', [
                'Een tafelmodel heeft 80 tot 130 liter, genoeg voor een of twee personen of als '
                'tweede koelkast. Een hoge smalle kast komt tot ruim 200 liter. Reken per persoon '
                'op ongeveer 50 tot 70 liter koelruimte.']),
        ],
        'vragen': [
            # Aangeleverd: "sorteer of filter de lijst op breedte"; de lijst
            # sorteert alleen op prijs.
            ('Wat is de smalste koelkast?',
             'Er zijn modellen vanaf ongeveer 45 cm breed. De breedte staat bij elk model op de '
             'productpagina, bij de gegevens van het energielabel.'),
            ('Is een smalle koelkast minder zuinig?',
             'Niet per se. Kleine kasten verbruiken in totaal weinig, maar hebben niet altijd het '
             'beste label. Het jaarverbruik staat bij elk model.'),
            ('Mag een koelkast strak tussen twee kasten staan?',
             'Een vrijstaande koelkast heeft rondom wat ruimte nodig om warmte af te voeren. De '
             'minimale afstand staat in de handleiding.'),
        ],
        'bekijk_ook': [
            ('Koelkasten 50-60 cm breed', '/category/koelkasten/breedte/50-60-cm'),
            ('Kleine koelkasten tot 100 liter', '/category/koelkasten/inhoud/tot-100-liter'),
            ('Koelkasten 100-250 liter', '/category/koelkasten/inhoud/100-250-liter'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('koelkasten', 'inhoud', 'tot-100-liter'): {
        'titel': 'Kleine koelkast: {n} modellen tot 100 liter vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Kleine koelkasten (tot 100 liter)',
        'naam': 'kleine koelkasten',
        'intro': ('Een kleine koelkast tot 100 liter is een tafelmodel of minikoelkast: voor een '
                  'studentenkamer, kantoor, schuur, caravan of als tweede koelkast voor drankjes. '
                  'Wij volgen {n} kleine koelkasten, met per model de laagste prijs en het '
                  'jaarverbruik van het energielabel.'),
        'uitleg': [
            ('Met of zonder vriesvak?', [
                'Een vriesvakje is handig voor ijsblokjes en een paar diepvriesproducten, maar '
                'het kost koelruimte en het vak moet af en toe ontdooid worden. Gebruik je de '
                'kast alleen voor drinken en beleg, dan heb je meer aan een model zonder '
                'vriesvak.']),
            ('Waar zet je hem neer?', [
                'Een tafelmodel van ongeveer 85 cm hoog past onder een werkblad. Zet een '
                'koelkast niet in een onverwarmde schuur als de fabrikant een minimale '
                'omgevingstemperatuur opgeeft; onder die temperatuur koelt hij slecht. De '
                'klimaatklasse staat bij de specificaties.']),
        ],
        'vragen': [
            ('Hoeveel stroom verbruikt een kleine koelkast?',
             'Dat verschilt per model en label; het jaarverbruik in kilowattuur en de '
             'stroomkosten per jaar staan op elke productpagina.'),
            ('Is een minikoelkast stil genoeg voor een slaapkamer?',
             'Kijk naar het geluid in decibel bij het model. Onder de 36 decibel is een koelkast '
             'erg stil.'),
            ('Kan een tafelmodel koelkast worden ingebouwd?',
             'Alleen als het een onderbouw- of inbouwmodel is. Een vrijstaand tafelmodel heeft '
             'ventilatieruimte nodig.'),
        ],
        'bekijk_ook': [
            ('Smalle koelkasten', '/category/koelkasten/breedte/smal'),
            ('Koelkasten 100-250 liter', '/category/koelkasten/inhoud/100-250-liter'),
            ('Stille koelkasten', '/category/koelkasten/geluid/zeer-stil'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    # /geluid/zeer-stil is onder 45 dB (routes.main._FILTERVELDEN, van <= x < tot).
    ('vaatwassers', 'geluid', 'zeer-stil'): {
        'titel': 'Stille vaatwasser: {n} modellen onder 45 dB vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Stille vaatwassers (onder 45 dB)',
        'naam': 'stille vaatwassers',
        'intro': ('In een open keuken hoor je de vaatwasser de hele avond. Een stille vaatwasser '
                  'blijft onder de 45 decibel en is tijdens het draaien nauwelijks te horen. Wij '
                  'volgen {n} stille vaatwassers. Het geluidsniveau komt uit het officiële '
                  'Europese energielabelregister, opgegeven door de fabrikant.'),
        'uitleg': [
            ('Hoeveel decibel is stil voor een vaatwasser?', [
                'De meeste vaatwassers maken 44 tot 48 decibel. Onder de 45 decibel noemen wij '
                'een vaatwasser stil; de stilste modellen zitten rond de 40 decibel. Het '
                'energielabel geeft daarnaast een geluidsklasse van A tot D.']),
            ('Inbouw is stiller dan vrijstaand', [
                'Een inbouwvaatwasser zit achter een keukenfront en tussen kasten, en dat dempt '
                'het geluid. Zoek je de stilste oplossing voor een open keuken, kijk dan eerst '
                'naar volledig geïntegreerde inbouwmodellen.']),
        ],
        'vragen': [
            # Aangeleverd: "sorteer de lijst op geluid"; de lijst sorteert alleen op prijs.
            ('Wat is de stilste vaatwasser?',
             'Dat wisselt met het aanbod. Het geluidsniveau in decibel staat bij elk model op de '
             'productpagina, bij de gegevens van het energielabel.'),
            ('Is een stille vaatwasser duurder?',
             'Meestal iets, omdat betere isolatie en een stillere motor geld kosten. Het '
             'prijsverloop per model laat zien wanneer hij het goedkoopst was.'),
            ('Is het nachtprogramma stiller?',
             'Ja, veel vaatwassers hebben een stil programma dat langer duurt en met minder druk '
             'spoelt. Het geluid op het label geldt voor het standaardprogramma.'),
        ],
        'bekijk_ook': [
            ('Inbouw vaatwassers', '/category/vaatwassers/kenmerk/inbouw'),
            ('Vaatwassers 60 cm breed', '/category/vaatwassers/breedte/60-70-cm'),
            ('Vaatwassers met laag waterverbruik', '/category/vaatwassers/waterverbruik/tot-10-liter'),
            ('Alle vaatwassers', '/category/vaatwassers'),
        ],
    },

    # ------------------------------------------------------------------
    # Ronde 2, deel B: bestaande zoekzin-pagina's (zoekkenmerken.py). Kop,
    # intro en uitleg blijven van zoekkenmerken.py; hier alleen titel,
    # vragen en "bekijk ook". Velden die ontbreken laat tekst_voor op None.
    # ------------------------------------------------------------------
    ('ovens', 'kenmerk', 'airfryer'): {
        'titel': 'Airfryer vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'naam': 'airfryers',
        'vragen': [
            ('Welke maat airfryer heb ik nodig?',
             'Reken op ongeveer 1 liter per persoon voor een bijgerecht en 1,5 liter per persoon '
             'voor een hele maaltijd. Voor een gezin van vier is 5 tot 6 liter een gangbare maat.'),
            ('Airfryer met één of twee lades?',
             'Met twee lades bereid je twee gerechten tegelijk op verschillende temperaturen. Eén '
             'grote lade is handiger voor grote stukken, zoals een hele kip.'),
            ('Verbruikt een airfryer minder dan een oven?',
             'Voor kleine porties meestal wel: de ruimte is kleiner en voorverwarmen is '
             'nauwelijks nodig. Voor grote hoeveelheden is een oven efficiënter.'),
            ('Waarom verschilt de prijs van dezelfde airfryer per winkel?',
             'Winkels bepalen hun eigen prijs en passen die vaak aan. Het prijsverloop per model '
             'laat zien of een aanbieding echt een aanbieding is.'),
        ],
        'bekijk_ook': [
            ('Ovens en airfryers', '/category/ovens'),
            ('Inbouw ovens', '/category/ovens/kenmerk/inbouw'),
            ('Combimagnetrons', '/category/magnetrons/kenmerk/combimagnetron'),
        ],
    },
    ('koelkasten', 'kenmerk', 'amerikaans'): {
        'titel': 'Amerikaanse koelkast vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'naam': 'Amerikaanse koelkasten',
        'vragen': [
            ('Hoe breed is een Amerikaanse koelkast?',
             'Meestal 83 tot 92 cm. Meet ook de deuropeningen en de trap op: de kast moet naar '
             'binnen kunnen.'),
            ('Heeft een Amerikaanse koelkast een wateraansluiting nodig?',
             'Alleen voor een dispenser met vaste wateraansluiting. Er zijn ook modellen met een '
             'watertank die je zelf bijvult.'),
            ('Verbruikt een Amerikaanse koelkast veel stroom?',
             'Meer dan een gewone koel-vriescombinatie, door de grootte. Het jaarverbruik en de '
             'stroomkosten staan bij elk model.'),
        ],
        'bekijk_ook': [
            ('Koelkasten vanaf 450 liter', '/category/koelkasten/inhoud/vanaf-450-liter'),
            ('Brede koelkasten', '/category/koelkasten/breedte/breed'),
            ('No frost koelkasten', '/category/koelkasten/kenmerk/no-frost'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('koelkasten', 'kenmerk', 'no-frost'): {
        'titel': 'No frost koelkast vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'naam': 'no frost koelkasten',
        'vragen': [
            ('Wat is het verschil tussen no frost en low frost?',
             'No frost voorkomt ijsvorming met een ventilator; ontdooien is niet nodig. Low frost '
             'vertraagt ijsvorming, maar je moet af en toe nog ontdooien.'),
            ('Droogt eten uit in een no frost koelkast?',
             'De circulerende lucht is droog, dus onverpakt eten droogt sneller uit. Bewaar het '
             'afgedekt of in de groentelade.'),
            ('Is no frost zuiniger?',
             'Een vriezer zonder ijslaag werkt efficiënter dan een aangevroren vriezer. De '
             'ventilator verbruikt zelf een beetje; het jaarverbruik per model staat op de '
             'productpagina.'),
        ],
        'bekijk_ook': [
            ('Amerikaanse koelkasten', '/category/koelkasten/kenmerk/amerikaans'),
            ('Koelkasten 250-350 liter', '/category/koelkasten/inhoud/250-350-liter'),
            ('Koelkasten 60-70 cm breed', '/category/koelkasten/breedte/60-70-cm'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('vaatwassers', 'kenmerk', 'inbouw'): {
        'titel': 'Inbouw vaatwasser vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'naam': 'inbouw vaatwassers',
        'vragen': [
            ('Wat is het verschil tussen volledig en half geïntegreerd?',
             'Bij volledig geïntegreerd zit het hele front achter een keukendeur en zit de '
             'bediening op de bovenrand. Bij half geïntegreerd blijft het bedieningspaneel '
             'zichtbaar.'),
            ('Welke nismaat heeft een inbouw vaatwasser?',
             'De standaard is 60 cm breed; smalle modellen zijn 45 cm. De hoogte is verstelbaar '
             'binnen een bereik dat bij het model staat. Meet de nis voordat je bestelt.'),
            ('Kan ik mijn oude keukenfront hergebruiken?',
             'Meestal wel, als de maat en het scharniersysteem passen. Bij een hoog front is een '
             'schuifscharnier nodig.'),
        ],
        'bekijk_ook': [
            ('Stille vaatwassers', '/category/vaatwassers/geluid/zeer-stil'),
            ('Vaatwassers 60 cm breed', '/category/vaatwassers/breedte/60-70-cm'),
            ('Vaatwassers energielabel A', '/category/vaatwassers/energielabel/a'),
            ('Alle vaatwassers', '/category/vaatwassers'),
        ],
    },
    ('stofzuigers', 'kenmerk', 'robotstofzuiger'): {
        'titel': 'Robotstofzuiger vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'naam': 'robotstofzuigers',
        'vragen': [
            ('Kan een robotstofzuiger een gewone stofzuiger vervangen?',
             'Voor dagelijks onderhoud op harde vloeren en laag tapijt grotendeels. Voor trappen, '
             'hoeken en hoogpolig tapijt blijft een gewone of steelstofzuiger nodig.'),
            ('Wat is een leegstation?',
             'Een basisstation dat de stofbak van de robot zelf leegzuigt in een zak. Je hoeft '
             'dan maar eens in de paar weken iets te doen.'),
            ('Werkt een robotstofzuiger op tapijt en drempels?',
             'De meeste nemen drempels tot ongeveer 2 cm en rijden over laag tapijt. De maximale '
             'drempelhoogte staat bij de specificaties.'),
        ],
        'bekijk_ook': [
            ('Stofzuigers met dweilfunctie', '/category/stofzuigers/kenmerk/dweilfunctie'),
            ('Steelstofzuigers', '/category/stofzuigers/kenmerk/steelstofzuiger'),
            ('Alle stofzuigers', '/category/stofzuigers'),
        ],
    },
    ('stofzuigers', 'kenmerk', 'steelstofzuiger'): {
        'titel': 'Steelstofzuiger vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'naam': 'steelstofzuigers',
        'vragen': [
            ('Hoe lang gaat de accu van een steelstofzuiger mee?',
             'Op de normale stand 30 tot 60 minuten, op de hoogste stand vaak 10 tot 15 minuten. '
             'De opgegeven gebruiksduur staat bij het model.'),
            ('Is een steelstofzuiger sterk genoeg als enige stofzuiger?',
             'Voor een appartement of een huis met vooral harde vloeren meestal wel. Voor veel '
             'tapijt of een groot huis is een model met een grote stofbak en wisselbare accu '
             'handiger.'),
            ('Is de accu te vervangen?',
             'Bij steeds meer modellen wel, soms met een klik. Dat verlengt de levensduur van het '
             'apparaat.'),
        ],
        'bekijk_ook': [
            ('Robotstofzuigers', '/category/stofzuigers/kenmerk/robotstofzuiger'),
            ('Stofzuigers met dweilfunctie', '/category/stofzuigers/kenmerk/dweilfunctie'),
            ('Alle stofzuigers', '/category/stofzuigers'),
        ],
    },
    ('koffiemachines', 'kenmerk', 'volautomaat'): {
        'titel': ('Volautomatische koffiemachine vergelijken: {n} modellen vanaf € {vanaf} '
                  '| WitgoedAanbod.nl'),
        'naam': 'volautomatische koffiemachines',
        'vragen': [
            ('Wat is het verschil tussen een volautomaat en een halfautomaat?',
             'Een volautomaat maalt, doseert en zet de koffie met één druk op de knop. Bij een '
             'halfautomaat doe je het malen en aandrukken zelf.'),
            ('Automatisch melksysteem of losse opschuimer?',
             'Een automatisch systeem maakt cappuccino met één knop, maar vraagt dagelijks '
             'spoelen. Een stoompijpje is goedkoper en eenvoudiger schoon te houden.'),
            ('Hoe vaak moet je ontkalken?',
             'Dat hangt af van de waterhardheid en het gebruik; de machine geeft het aan. Met een '
             'waterfilter is het minder vaak nodig.'),
        ],
        'bekijk_ook': [
            ('Alle koffiemachines', '/category/koffiemachines'),
        ],
    },
    ('magnetrons', 'kenmerk', 'combimagnetron'): {
        'titel': 'Combimagnetron vergelijken: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'naam': 'combimagnetrons',
        'vragen': [
            ('Kan een combimagnetron een oven vervangen?',
             'Voor een klein huishouden vaak wel: hij heeft hetelucht en een grill. De ovenruimte '
             'is kleiner dan die van een gewone oven, dus een grote bakplaat past niet.'),
            ('Wat betekent de inhoud in liters?',
             'De binnenruimte. 25 tot 32 liter is gangbaar voor een vrijstaand model; '
             'inbouwmodellen gaan tot ongeveer 45 liter.'),
            ('Inbouw of vrijstaand?',
             'Een inbouwmodel past in een nis in de keukenkast en heeft ventilatie aan de '
             'voorkant. Een vrijstaand model heeft ruimte rondom nodig en mag niet zomaar worden '
             'ingebouwd.'),
        ],
        'bekijk_ook': [
            ('Alle magnetrons', '/category/magnetrons'),
            ('Inbouw ovens', '/category/ovens/kenmerk/inbouw'),
            ('Airfryers', '/category/ovens/kenmerk/airfryer'),
        ],
    },

    # ------------------------------------------------------------------
    # Ronde 3a (specialist-chat, 4 okt 2026): koelkasten per hoogte, het
    # nieuwe filterveld 'hoogte' (routes.main._FILTERVELDEN, alleen
    # koelkasten). Apparaathoogte uit EPREL; inbouwmodellen tellen mee.
    # ------------------------------------------------------------------
    ('koelkasten', 'hoogte', 'tot-90-cm'): {
        'titel': 'Lage koelkast tot 90 cm: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Lage koelkasten (tot 90 cm hoog)',
        'naam': 'lage koelkasten tot 90 cm',
        'intro': ('Een koelkast tot 90 cm hoog is een tafelmodel of onderbouwmodel. Hij past onder '
                  'een werkblad van 85 tot 90 cm, of staat los in een bijkeuken, studentenkamer of '
                  'kantoor. Wij volgen {n} koelkasten in deze hoogte. De maten komen uit het '
                  'officiële Europese energielabelregister en bij elk model staat de laagste prijs '
                  'van {winkels} winkels.'),
        'uitleg': [
            ('Tafelmodel of onderbouw?', [
                'Een tafelmodel is een vrijstaande koelkast met een eigen bovenblad. Een '
                'onderbouwmodel schuif je onder het aanrecht; die heeft meestal geen bovenblad en '
                'een rooster aan de voorkant voor de luchtafvoer. Zet een tafelmodel niet zomaar '
                'onder een werkblad: zonder ruimte voor ventilatie wordt hij warm en verbruikt hij '
                'meer.']),
            ('Met of zonder vriesvak?', [
                'Veel lage koelkasten hebben een klein vriesvak voor ijsblokjes en een paar '
                'diepvriesproducten. Wil je meer vriesruimte, kijk dan naar een hogere '
                'koel-vriescombinatie of een losse vriezer.']),
        ],
        'vragen': [
            ('Past een tafelmodel koelkast onder het aanrecht?',
             'Alleen als er boven en achter genoeg ruimte overblijft voor de luchtafvoer. Een '
             'onderbouwmodel is daarvoor gemaakt; de benodigde ruimte staat in de handleiding.'),
            ('Hoeveel liter heeft een lage koelkast?',
             'Meestal 80 tot 140 liter. Genoeg voor een of twee personen of als tweede koelkast.'),
            ('Hoe hoog is een standaard aanrecht?',
             'In Nederland meestal 85 tot 92 cm, inclusief werkblad. Meet je eigen keuken op '
             'voordat je kiest.'),
        ],
        'bekijk_ook': [
            ('Kleine koelkasten tot 100 liter', '/category/koelkasten/inhoud/tot-100-liter'),
            ('Smalle koelkasten', '/category/koelkasten/breedte/smal'),
            ('Koelkasten van 90 tot 130 cm', '/category/koelkasten/hoogte/90-130-cm'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('koelkasten', 'hoogte', '90-130-cm'): {
        'titel': 'Koelkast 90 tot 130 cm hoog: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Koelkasten van 90 tot 130 cm hoog',
        'naam': 'koelkasten van 90 tot 130 cm',
        'intro': ('Een koelkast van 90 tot 130 cm hoog zit tussen een tafelmodel en een hoge kast in. '
                  'Hij past onder een hangkast of schuin dak, en heeft meer ruimte dan een '
                  'tafelmodel. Wij volgen {n} koelkasten in deze hoogte, met per model de laagste '
                  'prijs van {winkels} winkels. De maten komen uit het officiële Europese '
                  'energielabelregister.'),
        'uitleg': [
            ('Voor wie is deze maat?', [
                'Voor een of twee personen die meer willen dan een tafelmodel, voor een kleine '
                'keuken met hangkasten, of voor een zolder of bijkeuken met een lage wand. Veel '
                'modellen in deze hoogte zijn koel-vriescombinaties met een kleine vriezer onderin '
                'of bovenin.']),
            ('Meten', [
                'Meet de hoogte tot de onderkant van de hangkast of het laagste punt van het dak. '
                'Houd boven de koelkast een paar centimeter vrij voor de luchtafvoer, tenzij de '
                'handleiding iets anders zegt.']),
        ],
        'vragen': [
            ('Is een koelkast van 120 cm groot genoeg voor twee personen?',
             'Meestal wel. Met 150 tot 200 liter inhoud heb je voor twee personen genoeg '
             'koelruimte.'),
            ('Bestaan er inbouwkoelkasten in deze hoogte?',
             'Ja, voor nissen van ongeveer 102 en 122 cm. Bij inbouw telt de nismaat; die staat in '
             'de specificaties of de handleiding van het model.'),
            ('Heeft een koelkast van deze hoogte een vriezer?',
             'Dat verschilt. Er zijn kasten met alleen een vriesvak en combinaties met een aparte '
             'vriezer. Kijk bij het model naar de inhoud van het vriesdeel.'),
        ],
        'bekijk_ook': [
            ('Lage koelkasten tot 90 cm', '/category/koelkasten/hoogte/tot-90-cm'),
            ('Koelkasten van 130 tot 170 cm', '/category/koelkasten/hoogte/130-170-cm'),
            ('Koelkasten 100-250 liter', '/category/koelkasten/inhoud/100-250-liter'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('koelkasten', 'hoogte', '130-170-cm'): {
        'titel': 'Koelkast 130 tot 170 cm hoog: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Koelkasten van 130 tot 170 cm hoog',
        'naam': 'koelkasten van 130 tot 170 cm',
        'intro': ('Een koelkast van 130 tot 170 cm hoog is ruim genoeg voor een klein huishouden en '
                  'past onder veel hangkasten en schuine daken waar een kast van 1,80 m te hoog is. '
                  'Wij volgen {n} koelkasten in deze hoogte, met per model de laagste prijs van '
                  '{winkels} winkels. De maten komen uit het officiële Europese '
                  'energielabelregister.'),
        'uitleg': [
            ('Koelkast of koel-vriescombinatie?', [
                'In deze hoogte vind je zowel koelkasten zonder vriezer, met veel koelruimte, als '
                'koel-vriescombinaties met een kleinere vriezer. Vries je weinig in, dan geeft een '
                'kast zonder vriezer meer ruimte voor verse producten.']),
            ('Inbouw', [
                'Inbouwkoelkasten in deze maat passen in nissen van ongeveer 140 of 158 cm. Bij '
                'inbouw is de nismaat bepalend, niet de buitenmaat. Die staat in de specificaties '
                'of de handleiding.']),
        ],
        'vragen': [
            ('Welke koelkast past onder een hangkast?',
             'Meet de vrije hoogte tot de hangkast en trek er een paar centimeter af voor de '
             'luchtafvoer. Kies een model dat daaronder blijft.'),
            ('Hoeveel liter heeft een koelkast van 150 cm?',
             'Meestal 200 tot 270 liter, afhankelijk van de breedte en of er een vriezer in zit.'),
            ('Is een koelkast van 140 cm genoeg voor een gezin?',
             'Voor twee tot drie personen vaak wel. Voor een groter gezin is een kast van 1,75 m '
             'of hoger handiger.'),
        ],
        'bekijk_ook': [
            ('Koelkasten van 90 tot 130 cm', '/category/koelkasten/hoogte/90-130-cm'),
            ('Koelkasten van 170 tot 180 cm', '/category/koelkasten/hoogte/170-180-cm'),
            ('Koelkasten 250-350 liter', '/category/koelkasten/inhoud/250-350-liter'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('koelkasten', 'hoogte', '170-180-cm'): {
        'titel': 'Koelkast 170 tot 180 cm hoog: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Koelkasten van 170 tot 180 cm hoog',
        'naam': 'koelkasten van 170 tot 180 cm',
        'intro': ('Koelkasten van 170 tot 180 cm hoog zijn de meest voorkomende maat voor een gezin. '
                  'Hieronder vallen de meeste koel-vriescombinaties en veel inbouwkoelkasten voor '
                  'de standaardnis van 178 cm. Wij volgen {n} koelkasten in deze hoogte, met per '
                  'model de laagste prijs van {winkels} winkels. De maten komen uit het officiële '
                  'Europese energielabelregister.'),
        'uitleg': [
            ('Inbouw: de nis van 178 cm', [
                'De meeste inbouwkoelkasten zijn gemaakt voor een nis van 178 cm hoog. Het '
                'apparaat zelf is dan iets lager, zodat het erin past. Vervang je een '
                'inbouwkoelkast, meet dan de nis, niet het oude apparaat, en kijk ook hoe de deur '
                'vastzit: met sleepdeur of met vaste deur.']),
            ('Vrijstaand', [
                'Een vrijstaande kast van deze hoogte heeft meestal 250 tot 350 liter inhoud. Let '
                'bij het kiezen ook op het geluid, de no frost-vriezer en het energielabel; de '
                'stroomkosten per jaar staan bij elk model.']),
        ],
        'vragen': [
            ('Wat is een standaard inbouwmaat voor een koelkast?',
             'De meest gebruikte nis is 178 cm hoog en 56 tot 57 cm breed. Daarnaast bestaan '
             'nissen van onder meer 88, 102, 122, 140 en 158 cm.'),
            ('Wat is het verschil tussen een sleepdeur en een vaste deur?',
             'Bij een sleepdeur glijdt de keukendeur mee langs een rail. Bij een vaste deur zit het '
             'keukenfront vast aan de deur van de koelkast. Een vervangend model moet hetzelfde '
             'systeem hebben, of je moet het front aanpassen.'),
            ('Hoeveel liter heeft een koelkast van 1,75 m?',
             'Meestal 250 tot 320 liter, verdeeld over koel- en vriesdeel.'),
        ],
        'bekijk_ook': [
            ('Koelkasten van 180 tot 190 cm', '/category/koelkasten/hoogte/180-190-cm'),
            ('Koelkasten van 130 tot 170 cm', '/category/koelkasten/hoogte/130-170-cm'),
            ('No frost koelkasten', '/category/koelkasten/kenmerk/no-frost'),
            ('Koelkasten 250-350 liter', '/category/koelkasten/inhoud/250-350-liter'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('koelkasten', 'hoogte', '180-190-cm'): {
        'titel': 'Koelkast 180 tot 190 cm hoog: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Koelkasten van 180 tot 190 cm hoog',
        'naam': 'koelkasten van 180 tot 190 cm',
        'intro': ('Een koelkast van 180 tot 190 cm hoog geeft een gezin veel ruimte op een gewone '
                  'breedte van ongeveer 60 cm. Het zijn vooral vrijstaande koel-vriescombinaties en '
                  'hoge koelkasten zonder vriezer. Wij volgen {n} koelkasten in deze hoogte, met '
                  'per model de laagste prijs van {winkels} winkels. De maten komen uit het '
                  'officiële Europese energielabelregister.'),
        'uitleg': [
            ('Past hij?', [
                'Meet de hoogte van de plek en houd boven de kast ruimte vrij voor de luchtafvoer, '
                'tenzij de handleiding iets anders zegt. Let ook op de diepte met de deur open, en '
                'of er naast de kast genoeg ruimte is om de deur ver genoeg te openen voor de '
                'lades.']),
            ('Twee kasten naast elkaar', [
                'Veel merken hebben een hoge koelkast en een hoge vriezer van dezelfde maat. Naast '
                'elkaar gezet heb je de ruimte van een Amerikaanse koelkast, maar dan met twee '
                'losse apparaten.']),
        ],
        'vragen': [
            ('Hoeveel liter heeft een koelkast van 1,85 m?',
             'Meestal 300 tot 370 liter op een breedte van 60 cm.'),
            ('Kan een hoge koelkast in een keuken met hangkasten?',
             'Alleen als de hangkasten hoger hangen dan de kast plus de vrije ruimte voor de '
             'luchtafvoer. Meet dat vooraf.'),
            ('Is een hogere koelkast duurder in gebruik?',
             'Een grotere kast verbruikt iets meer, maar het energielabel zegt meer dan de maat. '
             'Vergelijk de stroomkosten per jaar bij elk model.'),
        ],
        'bekijk_ook': [
            ('Koelkasten van 170 tot 180 cm', '/category/koelkasten/hoogte/170-180-cm'),
            ('Hoge koelkasten vanaf 190 cm', '/category/koelkasten/hoogte/vanaf-190-cm'),
            ('Amerikaanse koelkasten', '/category/koelkasten/kenmerk/amerikaans'),
            ('Alle koelkasten', '/category/koelkasten'),
        ],
    },
    ('koelkasten', 'hoogte', 'vanaf-190-cm'): {
        'titel': 'Hoge koelkast vanaf 190 cm: {n} modellen vanaf € {vanaf} | WitgoedAanbod.nl',
        'h1': 'Hoge koelkasten (vanaf 190 cm)',
        'naam': 'hoge koelkasten vanaf 190 cm',
        'intro': ('Een koelkast vanaf 190 cm hoog haalt de meeste ruimte uit een gewone breedte. '
                  'Hieronder vallen hoge koel-vriescombinaties tot ruim 2 meter en veel kasten '
                  'zonder vriezer. Wij volgen {n} koelkasten in deze hoogte, met per model de '
                  'laagste prijs van {winkels} winkels. De maten komen uit het officiële Europese '
                  'energielabelregister.'),
        'uitleg': [
            ('Waar let je op?', [
                'Op de plafondhoogte en op deuren of balken onderweg: een kast van 2 meter moet ook '
                'door de gang en de keukendeur. Kijk verder naar de hoogte van de bovenste plank; '
                'in een hoge kast is die voor niet iedereen goed bereikbaar.']),
            ('Hoog of breed?', [
                'Wil je nog meer ruimte, dan is een Amerikaanse koelkast van ongeveer 90 cm breed '
                'het alternatief. Die is meestal lager, rond 1,78 m, maar veel breder en '
                'dieper.']),
        ],
        'vragen': [
            # Aangeleverd: "filter de lijst op hoogte"; de lijst sorteert alleen op prijs.
            ('Hoe hoog is de hoogste koelkast?',
             'Er zijn vrijstaande modellen van ruim 2 meter. De hoogte staat bij elk model op de '
             'productpagina, bij de gegevens van het energielabel.'),
            ('Past een koelkast van 2 meter in een gewone keuken?',
             'In de meeste nieuwbouwwoningen is het plafond 2,60 m of hoger, dus in hoogte wel. '
             'Meet wel de doorgang onderweg en de plek met de deur open.'),
            ('Is een hoge koelkast handiger dan een Amerikaanse?',
             'Een hoge kast neemt minder vloer in en past in een gewone opstelling van 60 cm. Een '
             'Amerikaanse koelkast heeft meer inhoud en vaak een ijs- of waterdispenser.'),
        ],
        'bekijk_ook': [
            ('Koelkasten van 180 tot 190 cm', '/category/koelkasten/hoogte/180-190-cm'),
            ('Amerikaanse koelkasten', '/category/koelkasten/kenmerk/amerikaans'),
            ('Koelkasten vanaf 450 liter', '/category/koelkasten/inhoud/vanaf-450-liter'),
            ('Alle koelkasten', '/category/koelkasten'),
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
        ('Drogers van 8 kg', '/category/drogers/vulgewicht/8-9-kg'),
        ('Drogers van 9 en 10 kg', '/category/drogers/vulgewicht/9-11-kg'),
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
    h1 = ruw.get('h1')
    links = ruw.get('bekijk_ook') or BEKIJK_OOK.get(pad[0], [])
    return {
        'titel': titel.format(**waarden),
        # None = de pagina houdt haar eigen kop en intro (ronde 2, deel B).
        'h1': h1,
        # Korte naam voor 'Veelgestelde vragen over ...'; de hele h1 las daar
        # stroef ('... over warmtepompdrogers vergelijken'). Zonder naam: de h1
        # met een kleine eerste letter.
        'naam': ruw.get('naam') or (h1[:1].lower() + h1[1:] if h1 else ''),
        'intro': ruw['intro'].format(**waarden) if ruw.get('intro') else None,
        'uitleg': ruw.get('uitleg') or [],
        'vragen': ruw.get('vragen') or [],
        'bekijk_ook': [(t, p) for t, p in links if p != eigen],
    }
