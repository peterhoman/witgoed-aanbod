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

    # ------------------------------------------------------------------
    # Ronde 2 (specialist-chat, 4 okt 2026; Peter zei 3 okt ja op
    # kenmerkpagina's in fases). Deel A: maatpagina's met volledige tekst.
    # "zeven winkels" uit de aanlevering is {winkels} geworden.
    # ------------------------------------------------------------------
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
