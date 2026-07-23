#!/usr/bin/env python
"""
Seed the database with original buying guides and product comparisons.

Written to give visitors genuine, independent advice (not copied from
manufacturer or retailer marketing text), addressing Bol.com's affiliate
review feedback that the site needs more "added value" content beyond
plain product listings ("niet alleen doorlinken, maar mensen helpen
kiezen").

Safe to re-run: existing guides (matched by slug) are replaced.

De inhoud hieronder wordt ook automatisch gesynchroniseerd bij elke deploy
(ensure_new_guides in guides_content.py leest ALL_GUIDES en BLOG_POSTS):
een tekstwijziging hier komt dus vanzelf live, dit script handmatig draaien
is alleen nog nodig om een gids volledig opnieuw op te bouwen.
"""

BLOG_POSTS = [
    {
        'slug': 'recht-op-reparatie-31-juli-2026',
        'title': 'Vanaf 31 juli: recht op reparatie voor wasmachines en ander witgoed',
        'excerpt': 'De Europese reparatierichtlijn wordt eind deze maand concreet: fabrikanten moeten witgoed ook ná de garantie repareren, en wie binnen de garantie voor reparatie kiest krijgt er 12 maanden garantie bij.',
        'category_slug': None,
        'content': """
<p>We schreven er eerder dit jaar al over in ons <a href="/blog/witgoedmarkt-nieuws-2026-reparatierecht-smart-inbouw">marktoverzicht</a>, en nu is het bijna zover: uiterlijk <strong>31 juli 2026</strong> moet de Europese richtlijn "recht op reparatie" in nationale wetgeving zijn omgezet. Voor iedereen met een wasmachine, droger, vaatwasser, koelkast of vriezer verandert er daarmee het nodige.</p>

<h2>Wat verandert er concreet?</h2>
<ul>
    <li><strong>Reparatie ook ná de garantie:</strong> fabrikanten van grote huishoudelijke apparaten worden verplicht om reparaties uit te voeren als dat technisch mogelijk is — ook buiten de wettelijke garantieperiode, tegen een redelijke prijs.</li>
    <li><strong>12 maanden extra garantie na reparatie:</strong> laat je een apparaat bínnen de garantie repareren in plaats van vervangen, dan wordt de wettelijke garantie eenmalig met een jaar verlengd. Repareren wordt daarmee aantrekkelijker dan omruilen.</li>
    <li><strong>Onderdelen en informatie beschikbaar:</strong> reserveonderdelen, gereedschap en technische reparatie-informatie moeten beschikbaar komen, zonder kunstmatige drempels zoals het alleen verkopen van dure complete modules.</li>
</ul>

<h2>Let op: reparatie is niet gratis</h2>
<p>De regels maken reparatie mogelijk en toegankelijk, maar buiten de garantieperiode betaal je er gewoon voor. De wettelijke garantie zelf blijft ongewijzigd. De afweging "repareren of vervangen" blijft dus een rekensom — zeker bij oudere, onzuinige apparaten kan een nieuw, zuinig model per saldo goedkoper zijn. Hoe je die som maakt, lees je in onze gids over het <a href="/blog/stroomverbruik-koelkast-per-jaar">stroomverbruik van een koelkast</a> (dezelfde rekenmethode werkt voor elk groot apparaat).</p>

<p>Staat vervangen toch op de planning? Vergelijk dan eerst de actuele prijzen in onze categorieën <a href="/category/wasmachines">wasmachines</a>, <a href="/category/drogers">drogers</a>, <a href="/category/vaatwassers">vaatwassers</a> en <a href="/category/koelkasten">koelkasten</a> — de goedkoopste leverbare aanbieding staat bij ons altijd bovenaan.</p>
""",
    },
    {
        'slug': 'witgoedaanbod-vergelijkt-nu-6-winkels',
        'title': 'WitgoedAanbod vergelijkt nu 6 winkels: EP en Alternate zijn live',
        'excerpt': 'Onze vergelijker is deze maand uitgebreid met twee winkels: EP (met een groot witgoedassortiment) en elektronica-specialist Alternate. Meer prijzen per apparaat, dus een completer beeld.',
        'category_slug': None,
        'content': """
<p>Goed nieuws voor iedereen die via WitgoedAanbod.nl prijzen vergelijkt: er doen sinds deze maand twee winkels extra mee. Daarmee vergelijken we de prijzen van <strong>zes grote Nederlandse webshops</strong>: Bol, Coolblue, MediaMarkt, Expert, Alternate en EP.</p>

<h2>Wat merk je daarvan?</h2>
<p><strong>EP</strong> is een echte witgoedwinkel — van wasmachines en koelkasten tot afzuigkappen — en voegt in vrijwel elke categorie honderden actuele prijzen toe. <strong>Alternate</strong> is vooral sterk in elektronica en vult de vergelijking aan bij onder meer stofzuigers en koffiemachines. Per apparaat zie je dus vaker meerdere winkels naast elkaar, en dat vergroot de kans dat je de laagste prijs te pakken hebt.</p>

<p>De spelregels blijven zoals je van ons gewend bent: de <strong>goedkoopste leverbare aanbieding staat altijd bovenaan</strong>, winkels kunnen hun positie niet kopen, en de prijzen worden meerdere keren per dag automatisch ververst — inclusief het prijsverloop per apparaat, zodat je ziet of een "aanbieding" echt een aanbieding is. Meer over hoe we werken lees je op onze <a href="/over-ons">over-ons-pagina</a>.</p>

<p>Benieuwd? Bekijk de vernieuwde vergelijking in de categorieën <a href="/category/wasmachines">wasmachines</a>, <a href="/category/koelkasten">koelkasten</a> of <a href="/category/stofzuigers">stofzuigers</a>.</p>
""",
    },
    {
        'slug': 'witgoedmarkt-nieuws-2026-reparatierecht-smart-inbouw',
        'title': 'Witgoedmarkt 2026: reparatierecht, slimme apparaten en meer luxe inbouw',
        'excerpt': 'Drie actuele ontwikkelingen in de witgoedmarkt: het nieuwe Europese reparatierecht, de opmars van slimme apparaten en een duidelijke verschuiving naar luxe inbouwapparatuur.',
        'category_slug': None,
        'content': """
<p>De witgoedmarkt verandert dit jaar op een paar duidelijke punten. We zetten de belangrijkste ontwikkelingen op een rij.</p>

<h2>Recht op Reparatie vanaf juli 2026</h2>
<p>Vanaf juli 2026 treedt nieuwe Europese wetgeving in werking die consumenten een wettelijk recht geeft om grote huishoudelijke apparaten, zoals wasmachines en vaatwassers, te laten repareren in plaats van ze meteen te vervangen. Doel is de levensduur van apparaten te verlengen en de hoeveelheid elektronisch afval te verminderen. Een neveneffect: de markt voor refurbished en outlet-witgoed groeit mee, doordat meer consumenten bewust kiezen voor een gerepareerd, goedkoper tweedehands model in plaats van meteen nieuw te kopen.</p>

<h2>Slimme apparaten: op weg naar 30% van de huishoudens</h2>
<p>Uit consumentenonderzoek van Multiscope blijkt dat inmiddels ongeveer 30% van de Nederlandse huishoudens minstens één slim huishoudelijk apparaat bezit. De robotstofzuiger is met 12% het populairst, gevolgd door de slimme wasmachine of droger (9%) en de slimme vaatwasser (6%). De belangrijkste reden die kopers noemen is gemak: op afstand bedienen, plannen en monitoren via een app.</p>

<h2>Meer luxe inbouw, minder vrijstaand</h2>
<p>Cijfers van branchevereniging APPLiA Nederland laten zien dat het totale verkoopvolume van witgoed licht daalt, maar dat kopers wel vaker voor luxere, ingebouwde apparatuur kiezen. Er werd voor circa €1,7 miljard aan inbouwapparatuur verkocht, een stijging van 3%, mede gedreven door een actievere huizenmarkt. Vrijstaande apparaten daalden juist met 2%. Ook opvallend: kopers kiezen vaker voor grotere capaciteit, zoals wasmachines vanaf 9 kg en Amerikaanse koelkasten. Wil je weten waar je op moet letten bij een grotere wasmachine? Bekijk onze <a href="/gidsen/wasmachine-kopen-waar-op-letten">koopgids voor wasmachines</a>.</p>
""",
    },
    {
        'slug': 'uitgelicht-aeg-powercare-universaldose',
        'title': 'Uitgelicht: AEG PowerCare UniversalDose, de wasmachine die zelf doseert',
        'excerpt': 'Deze maand lichten we een product uit dat opvalt door zijn automatische wasmiddeldosering: de AEG LR8686UC4 8000 PowerCare UniversalDose.',
        'category_slug': 'wasmachines',
        'content': """
<p>Elke maand lichten we een product uit dat opvalt binnen zijn categorie. Deze keer: de <strong><a href="/product/aeg-lr8686uc4-8000-powercare-universaldose---wasma-7333394144375">AEG LR8686UC4 8000 PowerCare UniversalDose</a></strong>.</p>

<p>Wat deze wasmachine onderscheidt, is de automatische wasmiddeldosering: je vult een voorraadhouder met wasmiddel, en de machine bepaalt zelf de juiste hoeveelheid per wasbeurt op basis van vulgewicht en programma. Dat scheelt niet alleen gedoe met doseerbakjes, maar voorkomt ook over- of onderdosering — vaak de oorzaak van slecht wasresultaat of onnodig wasmiddelverbruik.</p>

<p>Daarnaast scoort dit model met energielabel A (tot 40% zuiniger dan wettelijk vereist) opvallend goed op verbruik. We hebben het model uitgebreider besproken in onze <a href="/gidsen/beste-wasmachines-vergeleken">vergelijking van drie populaire wasmachines</a>. De actuele prijs en het prijsverloop vind je op de <a href="/product/aeg-lr8686uc4-8000-powercare-universaldose---wasma-7333394144375">productpagina van de AEG LR8686UC4</a>.</p>

<p>De UniversalDose-doseertechniek bleek trouwens geen eendagsvlieg: de grotere 10 kg-uitvoering, de <a href="/product/aeg-lr86power-powercare-universaldose-7333394121017">AEG LR86 PowerCare UniversalDose</a>, staat inmiddels op nummer 2 in onze <a href="/gidsen/beste-wasmachine-2026">top 5 beste wasmachines van 2026</a> (met video).</p>
""",
    },
    {
        'slug': 'koelkast-instellen-voor-de-zomer',
        'title': 'Zomertip: zo stel je je koelkast optimaal in tijdens warme dagen',
        'excerpt': 'Bij hogere kamertemperaturen moet je koelkast harder werken. Een paar simpele aanpassingen houden je energieverbruik binnen de perken.',
        'category_slug': 'koelkasten',
        'content': """
<p>Bij warm weer moet je koelkast harder werken om dezelfde binnentemperatuur te behouden, wat het energieverbruik tijdelijk kan verhogen. Een paar simpele gewoontes helpen om dat binnen de perken te houden.</p>

<p>Zet de koelkast niet naast een warmtebron zoals de oven of in direct zonlicht — dat dwingt de compressor onnodig hard te werken. Laat ook voldoende ruimte vrij achter en rond het apparaat voor luchtcirculatie; ingebouwde modellen hebben hier vaak een minimale ventilatieruimte voor die je niet moet dichtzetten.</p>

<p>Vermijd daarnaast het te lang openhouden van de deur, en laat warm eten eerst even afkoelen op het aanrecht voordat je het in de koelkast zet. Meer weten over waar je op moet letten bij de aanschaf van een nieuwe koelkast? Bekijk onze <a href="/gidsen/koelkast-kopen-complete-gids">complete koopgids</a>.</p>
""",
    },
]

WASMACHINE_GUIDE = {
    'slug': 'wasmachine-kopen-waar-op-letten',
    'title': 'Wasmachine kopen: waar moet je op letten?',
    'excerpt': 'Vulgewicht, toerental, energielabel en geluidsniveau uitgelegd, zodat je een wasmachine kiest die echt bij je huishouden past.',
    'category_slug': 'wasmachines',
    'content': """
<p>Een wasmachine gaat al snel 10 tot 15 jaar mee, dus een verkeerde keuze merk je lang. De prijsverschillen tussen modellen lijken op het eerste gezicht vooral te zitten in merk en design, maar de échte verschillen zitten in vulgewicht, toerental, energielabel en geluidsniveau. Hieronder leggen we uit waar elk van die specificaties voor staat, zodat je zelf kunt bepalen welke wasmachine bij jouw huishouden past — in plaats van te varen op een willekeurig sterrenaantal.</p>

<h2>Bepaal eerst je vulgewicht</h2>
<p>Het vulgewicht (uitgedrukt in kg) bepaalt hoeveel droge was je in één keer kunt draaien. Als vuistregel geldt: reken ongeveer 1 kg was per gezinslid per wasbeurt, plus wat extra ruimte voor beddengoed, handdoeken en dikkere kleding zoals spijkerbroeken.</p>
<ul>
    <li><strong>7 kg:</strong> geschikt voor 1-2 personen</li>
    <li><strong>8-9 kg:</strong> geschikt voor een gezin van 3-4 personen</li>
    <li><strong>10 kg en meer:</strong> voor grotere gezinnen, of voor wie liever minder vaak maar dan grondig wast</li>
</ul>
<p>Een te kleine machine betekent dat je vaker moet wassen, wat op termijn meer water en stroom kost dan één keer extra investeren in een groter model. Een te grote machine is juist inefficiënt bij kleine ladingen: veel wasmachines gebruiken namelijk altijd een minimale hoeveelheid water, ongeacht hoe vol de trommel is — tenzij het model een beladingssensor heeft (zie verderop).</p>

<h2>Toerental centrifugeren</h2>
<p>Het toerental (uitgedrukt in rpm, rotaties per minuut) bepaalt hoe droog je was uit de machine komt na het wasprogramma. Hoe hoger het toerental, hoe droger het resultaat — maar ook hoe meer mechanische belasting op de kleding en hoe meer geluid tijdens het centrifugeren.</p>
<ul>
    <li><strong>1200 rpm en lager:</strong> zachter voor kwetsbare stoffen, maar de was blijft merkbaar vochtiger</li>
    <li><strong>1400 rpm:</strong> de meest gangbare middenweg, geschikt voor de meeste huishoudens</li>
    <li><strong>1600 rpm en hoger:</strong> droogste resultaat, vooral handig als je aansluitend een droger gebruikt of weinig droogruimte hebt</li>
</ul>
<p>Twijfel je? Kies dan 1400 rpm: dat is voor vrijwel alle textielsoorten een veilige, praktische keuze.</p>

<h2>Energielabel en waterverbruik</h2>
<p>Sinds de herziening van de Europese energielabels lopen de klassen van A (zuinigst) tot G (minst zuinig). Een wasmachine met een zuiniger label kost in de winkel vaak iets meer, maar dat verschil verdien je terug via een lagere energierekening — zeker als je, zoals de meeste huishoudens, wekelijks meerdere keren wast. Let bij het vergelijken ook op het waterverbruik per wasbeurt (in liters), dat staat meestal apart vermeld in de specificaties naast het energielabel zelf. Waarom dit precies zo belangrijk is, leggen we uitgebreider uit in onze <a href="/gidsen/energielabel-witgoed-uitgelegd">gids over energielabels bij witgoed</a>.</p>

<h2>Type belading: voorlader of bovenlader</h2>
<p>Verreweg de meeste wasmachines in Nederland zijn voorladers. Bovenladers zijn vaak iets smaller en daardoor handig in krappe ruimtes, maar het aanbod is beperkter en de prijs per liter trommelinhoud ligt gemiddeld hoger.</p>

<h2>Geluidsniveau</h2>
<p>Staat je wasmachine in of naast een leefruimte, bijvoorbeeld in een open keuken? Dan is het geluidsniveau tijdens centrifugeren relevant. Dit wordt uitgedrukt in decibel (dB): modellen rond de 70 dB of lager tijdens centrifugeren zijn merkbaar rustiger dan modellen die richting de 80 dB gaan.</p>

<h2>Handige extra's</h2>
<p>Sommige machines hebben functies zoals een beladingssensor (past het water- en energieverbruik automatisch aan de daadwerkelijke hoeveelheid was aan, in plaats van uit te gaan van een volle trommel), een quick-wash-programma voor kleine, snelle ladingen, of een stoomfunctie om kreuken te verminderen zonder strijken. Dit zijn waardevolle toevoegingen, maar wij raden aan om eerst je basisbehoefte vast te stellen — vulgewicht, toerental en energielabel — voordat je op extra's gaat letten. Een machine die qua basisspecificaties niet past, wordt niet beter door een handige extra functie.</p>

<h2>Kort samengevat</h2>
<p>Ga voor het juiste vulgewicht bij je huishoudgrootte, kies 1400 rpm als veilige middenweg tenzij je specifieke wensen hebt, let op een goed energielabel omdat dat zich op termijn terugbetaalt, en houd rekening met geluidsniveau als de machine in een leefruimte staat. Wil je zien hoe dit er in de praktijk uitziet? Bekijk onze <a href="/gidsen/beste-wasmachines-vergeleken">vergelijking van drie populaire wasmachines</a>, waarin we deze afwegingen concreet naast elkaar leggen.</p>
""",
}

KOELKAST_GUIDE = {
    'slug': 'koelkast-kopen-complete-gids',
    'title': 'Koelkast kopen: de complete gids',
    'excerpt': 'Inhoud, type, energielabel en No Frost uitgelegd, zodat je een koelkast kiest die past bij je keuken en je huishouden.',
    'category_slug': 'koelkasten',
    'content': """
<p>Een koelkast is, samen met de vriezer, het enige grote huishoudapparaat dat vrijwel 24 uur per dag aanstaat. Dat maakt de keuze net iets anders dan bij bijvoorbeeld een wasmachine: naast inhoud en type weegt het energieverbruik zwaarder mee, simpelweg omdat het apparaat nooit uit staat. Hieronder lopen we de belangrijkste keuzefactoren langs.</p>

<h2>Hoeveel inhoud heb je nodig?</h2>
<p>De inhoud van een koelkast wordt uitgedrukt in liters. Als richtlijn:</p>
<ul>
    <li><strong>Tot 100 liter (tafelmodel):</strong> handig als bijzet-koelkast, op een studentenkamer, of in een kleine keuken</li>
    <li><strong>150-250 liter:</strong> geschikt voor 1-2 personen</li>
    <li><strong>250-350 liter:</strong> geschikt voor een gezin van 3-4 personen</li>
    <li><strong>350 liter en meer:</strong> voor grotere huishoudens, of voor wie graag voorraad inslaat en niet vaak boodschappen wil doen</li>
</ul>
<p>Reken niet alleen met het aantal personen, maar ook met je boodschappenritme: doe je wekelijks één grote boodschap, dan heb je meer buffer nodig dan wanneer je vaker kleine hoeveelheden haalt.</p>

<h2>Type: koelkast, koel-vriescombinatie of Amerikaanse koelkast</h2>
<p>Een losse koelkast heeft alleen koelruimte, zonder vriesvak (of met een heel klein vriesvakje). Een koel-vriescombinatie combineert koelen en vriezen in één toestel — de meest gekozen optie in Nederlandse huishoudens, omdat je geen aparte vriezer nodig hebt. Amerikaanse koelkasten (side-by-side) bieden veel inhoud en vaak extra's zoals een waterdispenser of ijsblokjesmachine, maar zijn ook aanzienlijk breder en dus niet in elke keuken te plaatsen.</p>

<h2>No Frost versus handmatig ontdooien</h2>
<p>Bij een koelkast of vriesvak zonder No Frost-techniek vormt zich na verloop van tijd ijsaanslag, waardoor je regelmatig (meestal een paar keer per jaar) handmatig moet ontdooien. No Frost-modellen voorkomen ijsvorming automatisch door lucht te laten circuleren, wat onderhoud bespaart. Dit zie je meestal terug in een iets hogere aanschafprijs, maar het bespaart je structureel tijd en gedoe.</p>

<h2>Energielabel: waarom dit hier extra belangrijk is</h2>
<p>Een koelkast staat, in tegenstelling tot een wasmachine, vrijwel de hele dag aan. Het energielabel heeft daardoor relatief veel invloed op je jaarlijkse energiekosten — meer dan bij apparaten die je maar een paar keer per week gebruikt. Een zuiniger toestel (hogere klasse op het label) is vaak iets duurder in aanschaf, maar verdient zich over de levensduur van het apparaat terug via een lagere energierekening. Lees ook onze algemene <a href="/gidsen/energielabel-witgoed-uitgelegd">uitleg over energielabels bij witgoed</a> voor de achtergrond hierachter.</p>

<h2>Geluidsniveau</h2>
<p>Omdat een koelkast continu draait, kan geluid sneller opvallen dan bij apparaten die je af en toe gebruikt — zeker in een open keuken naast de woonkamer. Let op het aantal decibel (dB) in de specificaties: onder de 40 dB is voor de meeste mensen nauwelijks hoorbaar in een woonruimte.</p>

<h2>Afmetingen en inbouw versus vrijstaand</h2>
<p>Meet altijd de beschikbare ruimte (hoogte, breedte, diepte, én de ruimte om deuren volledig te kunnen openen) voordat je een koelkast bestelt. Inbouwkoelkasten zijn ontworpen om naadloos in keukenkasten te passen, maar zijn vaak duurder en minder flexibel qua formaatkeuze dan vrijstaande modellen. Vrijstaande koelkasten geven meer keuzevrijheid in merk en formaat, maar vallen optisch meer op in de keuken.</p>

<h2>Klimaatklasse: let op als je koelkast in een garage of schuur komt</h2>
<p>Elke koelkast heeft een klimaatklasse die aangeeft binnen welk omgevingstemperatuurbereik het apparaat optimaal functioneert — meestal SN, N, ST of T, met elk een eigen temperatuurbereik. Voor een koelkast in een verwarmde woonruimte is dit zelden een probleem, maar plaats je een koelkast in een ongeïsoleerde garage, schuur of kelder, dan kan de omgevingstemperatuur 's winters of 's zomers buiten het ondersteunde bereik vallen. Het apparaat werkt dan minder efficiënt of, in extreme gevallen, helemaal niet zoals bedoeld. Check dus altijd de klimaatklasse als je koelkast niet in een verwarmde ruimte komt te staan.</p>

<h2>Kort samengevat</h2>
<p>Bepaal eerst hoeveel inhoud je nodig hebt op basis van huishoudgrootte én boodschappenritme, kies het type dat past bij je keuken (los, combi, of Amerikaans), en besteed extra aandacht aan het energielabel omdat dit apparaat nooit uitstaat. No Frost is een prettige, tijdsbesparende extra, geen must-have — en vergeet de klimaatklasse niet als de koelkast niet in een verwarmde ruimte komt te staan.</p>
""",
}

ENERGY_LABEL_GUIDE = {
    'slug': 'energielabel-witgoed-uitgelegd',
    'title': 'Waarom is het energielabel zo belangrijk bij witgoed?',
    'excerpt': 'Wat het energielabel precies betekent, hoe de ECO-stand werkt, en waarom een zuiniger toestel zich vaak binnen een paar jaar terugverdient.',
    'category_slug': None,
    'content': """
<p>Bij vrijwel elk witgoedproduct — wasmachine, droger, koelkast, vaatwasser — zie je een gekleurde balk met een letter erop: het energielabel. Veel mensen kijken er vluchtig naar, maar begrijpen niet helemaal waarom dat label zoveel invloed heeft op de uiteindelijke kosten van een apparaat. In deze gids leggen we uit hoe het energielabel werkt, wat de ECO-stand precies doet, en waarom het de moeite waard is om hier bewust op te letten.</p>

<h2>Hoe werkt het energielabel?</h2>
<p>Sinds de herziening van de Europese energielabels (2021) lopen de klassen van A (zuinigst) tot G (minst zuinig). Dit is een strengere schaal dan de oude labels, waarbij vrijwel alles A+++ was — de nieuwe schaal maakt onderlinge verschillen tussen apparaten weer echt zichtbaar. Het label geeft aan hoeveel energie een apparaat verbruikt tijdens een standaardprogramma, gemeten onder gecontroleerde testomstandigheden, zodat je modellen eerlijk met elkaar kunt vergelijken.</p>

<h2>Waarom een paar euro's extra aanschafprijs zich terugverdient</h2>
<p>Een zuiniger apparaat (bijvoorbeeld klasse A in plaats van C) kost bij aanschaf vaak wat meer. Het verschil in energieverbruik lijkt op papier klein — een paar cent per wasbeurt of per dag bij een koelkast — maar telt op:</p>
<ul>
    <li>Een <strong>wasmachine</strong> draait bij een gemiddeld huishouden 3 tot 5 keer per week. Over een levensduur van 10-15 jaar kan het verschil tussen een zuinig en een minder zuinig model oplopen tot honderden euro's aan stroomkosten.</li>
    <li>Een <strong>koelkast</strong> staat 24 uur per dag, 365 dagen per jaar aan. Hier is het effect van het energielabel het grootst van alle witgoedcategorieën, omdat er geen "uit"-moment is zoals bij een wasmachine of droger.</li>
    <li>Een <strong>droger</strong> is van alle witgoed doorgaans het minst zuinige apparaat qua verbruik per gebruiksmoment — hier loont een goed energielabel extra.</li>
</ul>
<p>Reken bij twijfel simpelweg uit: het prijsverschil tussen twee modellen, gedeeld door het geschatte jaarlijkse verschil in energiekosten, geeft je de terugverdientijd. Bij de meeste witgoedproducten ligt die tussen de 2 en 5 jaar — ruim binnen de gemiddelde levensduur van het apparaat.</p>

<h2>Wat is de ECO-stand, en waarom duurt die langer?</h2>
<p>Veel wasmachines en vaatwassers hebben een ECO-programma. Dit programma wast of wast af op een lagere temperatuur en met minder water, maar compenseert dat met een langere looptijd — vaak 3 tot 4 uur in plaats van 1 tot 2 uur. Dat klinkt tegenstrijdig (langer draaien voor minder verbruik), maar het werkt: door langer op een lagere temperatuur te werken, hoeft het apparaat minder energie te gebruiken om water op te warmen, wat verreweg het grootste deel van het energieverbruik van een wasbeurt of afwasbeurt uitmaakt. Voor niet-dringende was of vaat is de ECO-stand daarom vaak de goedkoopste keuze, ook al voelt "langer duren" in eerste instantie minder efficiënt.</p>

<h2>Let ook op waterverbruik</h2>
<p>Naast het energielabel vermelden fabrikanten meestal ook het waterverbruik per programma, in liters. Dit staat los van het energielabel maar telt wel mee in de totale gebruikskosten, vooral bij wasmachines en vaatwassers die je dagelijks of bijna dagelijks gebruikt.</p>

<h2>De QR-code op het label: meer details dan je zou denken</h2>
<p>Sinds de herziening van 2021 staat er op elk energielabel een QR-code. Scan je die met je telefoon, dan kom je terecht in de Europese productendatabank EPREL, waar de volledige, officiële testgegevens van dat specifieke model staan: exact energieverbruik per jaar, waterverbruik per programma, geluidsniveau, en programmaduur. Dit is handig als je twee modellen met hetzelfde label (bijvoorbeeld beide klasse A) toch precies met elkaar wilt vergelijken — binnen één klasse kunnen modellen namelijk nog steeds behoorlijk verschillen in daadwerkelijk verbruik.</p>

<h2>Kort samengevat</h2>
<p>Het energielabel is geen marketingdetail, maar een directe indicator van wat een apparaat je de komende jaren aan stroom gaat kosten. Vooral bij apparaten die veel of continu draaien — koelkasten voorop, gevolgd door wasmachines en drogers — is een paar euro's meer investeren in een zuiniger label vaak binnen enkele jaren terugverdiend. Bekijk onze specifieke koopgidsen voor <a href="/gidsen/wasmachine-kopen-waar-op-letten">wasmachines</a> en <a href="/gidsen/koelkast-kopen-complete-gids">koelkasten</a> voor meer categoriegebonden advies.</p>
""",
}

WASMACHINE_COMPARISON_GUIDE = {
    'slug': 'beste-wasmachines-vergeleken',
    'title': 'De beste wasmachines vergeleken: welke past bij jou?',
    'excerpt': 'We zetten drie populaire wasmachines naast elkaar op vulgewicht, energielabel en prijs, en leggen uit voor wie elk model het meest geschikt is.',
    'category_slug': 'wasmachines',
    'content': """
<p>Om de theorie uit onze <a href="/gidsen/wasmachine-kopen-waar-op-letten">koopgids voor wasmachines</a> concreet te maken, zetten we hieronder drie verschillende modellen naast elkaar: de <strong>Hisense WF5I1045BBQ</strong>, de <strong>AEG LR8686UC4 8000 PowerCare UniversalDose</strong> en de <strong>Samsung WW90CGC04AAHEN Ecobubble 5000</strong>. Dit zijn drie machines met een duidelijk verschillend profiel, waardoor de afweging tussen vulgewicht, energielabel en prijs goed zichtbaar wordt. We bespreken elk model apart en zetten de specificaties daarna nog eens overzichtelijk naast elkaar.</p>

<h2>Specificaties naast elkaar</h2>
<table class="comparison-table">
    <thead>
        <tr><th>Model</th><th>Vulgewicht</th><th>Toerental</th><th>Energielabel</th><th>Richtprijs</th></tr>
    </thead>
    <tbody>
        <tr><td>Hisense WF5I1045BBQ</td><td>10,5 kg</td><td>1400 rpm</td><td>A</td><td>€499</td></tr>
        <tr><td>AEG LR8686UC4 8000</td><td>8 kg</td><td>n.v.t.</td><td>A (-40%)</td><td>€749</td></tr>
        <tr><td>Samsung WW90CGC04AAHEN</td><td>9 kg</td><td>n.v.t.</td><td>A (-10%)</td><td>€499</td></tr>
    </tbody>
</table>

<h2>Hisense WF5I1045BBQ — de ruimste optie</h2>
<p>Met 10,5 kg vulgewicht en 1400 rpm centrifugeren is de <a href="/product/hisense-wf5i1045bbq-wasmachine---voorbelading---10-6901101834089">Hisense WF5I1045BBQ</a> de machine met de grootste capaciteit van de drie, voor circa €499. Geschikt voor grotere gezinnen of huishoudens die liever minder vaak, maar dan in grote ladingen wassen. Energielabel A maakt hem ook op verbruik een solide keuze, ondanks de grotere trommel.</p>

<h2>AEG LR8686UC4 8000 PowerCare UniversalDose — de zuinigste keuze</h2>
<p>De <a href="/product/aeg-lr8686uc4-8000-powercare-universaldose---wasma-7333394144375">AEG LR8686UC4 8000 PowerCare UniversalDose</a> heeft een kleiner vulgewicht (8 kg) dan de Hisense, voor circa €749. Het opvallendste kenmerk: dit model is tot 40% zuiniger dan wettelijk vereist voor energielabel A, wat hem tot de zuinigste van de drie maakt. De hogere aanschafprijs wordt deels gecompenseerd door een lager energieverbruik per wasbeurt — voor wie veel wast en op de lange termijn wil besparen, is dit de moeite waard om te overwegen. De automatische UniversalDose-wasmiddeldosering bespraken we eerder uitgebreid in ons <a href="/blog/uitgelicht-aeg-powercare-universaldose">uitgelicht-artikel over de AEG PowerCare UniversalDose</a>.</p>

<h2>Samsung WW90CGC04AAHEN Ecobubble 5000 — de gebalanceerde middenmoot</h2>
<p>Met 9 kg vulgewicht zit de <a href="/product/samsung-ww90cgc04aahen---ecobubble---5000-serie----8806095210582">Samsung WW90CGC04AAHEN Ecobubble 5000</a> qua capaciteit tussen de andere twee in, voor circa €499. De Ecobubble-technologie zorgt ervoor dat wasmiddel sneller en gelijkmatiger inwerkt via een bellenmengsel, wat effectief wassen op lagere temperaturen mogelijk maakt — praktisch voor wie vaker op 30 graden wast. Energielabel A, 10% zuiniger dan het wettelijk vereiste minimum.</p>

<h2>Welke past bij jou?</h2>
<ul>
    <li><strong>Groot gezin, minder vaak wassen:</strong> de Hisense, vanwege het hoogste vulgewicht.</li>
    <li><strong>Vaak wassen, energiekosten op lange termijn belangrijk:</strong> de AEG, vanwege het laagste energieverbruik ten opzichte van het wettelijk minimum.</li>
    <li><strong>Gemiddeld huishouden, vaak op lage temperatuur wassen:</strong> de Samsung, vanwege de Ecobubble-technologie en gebalanceerde specificaties.</li>
</ul>
<p>Alle drie zijn voorladers met een energielabel A of beter — het verschil zit hem vooral in vulgewicht en de mate waarin ze het wettelijke minimum overtreffen.</p>

<h2>Prijs-kwaliteitverhouding: waarom de goedkoopste niet altijd de beste keuze is</h2>
<p>Opvallend genoeg zijn de Hisense en de Samsung in deze vergelijking even duur (circa €499), terwijl de AEG €250 meer kost. Dat prijsverschil zit hem grotendeels in het energielabel: de AEG verbruikt tot 40% minder dan wettelijk vereist, tegenover 10% bij de Samsung en het wettelijk minimum bij de Hisense. Was je bijvoorbeeld 4 keer per week, dan kan dat verbruiksverschil de hogere aanschafprijs van de AEG binnen enkele jaren compenseren — reken dit na met de vuistregel uit onze <a href="/gidsen/energielabel-witgoed-uitgelegd">gids over energielabels</a>. Voor wie minder vaak wast of een kleiner budget heeft, is het verschil in de praktijk vaak te klein om de hogere aanschafprijs te rechtvaardigen, en is de Hisense of Samsung de verstandigere keuze.</p>

<p>Bekijk de actuele prijzen en beschikbaarheid van deze en andere modellen in onze <a href="/category/wasmachines">categorie wasmachines</a>. Wil je een bredere shortlist met één winnaar per budget? Bekijk dan onze <a href="/gidsen/beste-wasmachine-2026">top 5 beste wasmachines van 2026</a> (met video).</p>
""",
}

DROGER_GUIDE = {
    'slug': 'droger-kopen-waar-op-letten',
    'title': 'Droger kopen: waarschijnlijk het minst zuinige apparaat in huis',
    'excerpt': 'Warmtepomp versus condensdroger, capaciteit en energielabel uitgelegd — en waarom dit precies het apparaat is waar een goed label het meeste verschil maakt.',
    'category_slug': 'drogers',
    'content': """
<p>Een droger is van alle grote huishoudapparaten doorgaans het minst zuinige toestel qua energieverbruik per gebruiksmoment. Dat maakt de keuze voor het juiste type en energielabel hier extra belangrijk — meer nog dan bij een wasmachine of koelkast.</p>

<h2>Warmtepompdroger versus condensdroger</h2>
<p>Er zijn twee hoofdtypen. Een <strong>condensdroger</strong> verwarmt lucht met een verwarmingselement, vergelijkbaar met een föhn, en is relatief eenvoudig maar verbruikt veel stroom. Een <strong>warmtepompdroger</strong> hergebruikt warmte via een gesloten circuit, vergelijkbaar met hoe een koelkast werkt, en verbruikt daardoor aanzienlijk minder energie — vaak 40 tot 50% minder dan een condensdroger. Warmtepompdrogers zijn duurder in aanschaf, maar verdienen dat verschil bij regelmatig gebruik binnen enkele jaren terug via de energierekening.</p>

<h2>Capaciteit</h2>
<p>Net als bij een wasmachine wordt de capaciteit van een droger uitgedrukt in kg. Kies bij voorkeur een droger met een vergelijkbare of net iets grotere capaciteit dan je wasmachine, zodat je een volle trommel wasgoed in één keer kunt drogen.</p>

<h2>Energielabel: hier telt het het meest</h2>
<p>Omdat drogen relatief veel energie kost per gebruiksmoment, is het energielabel bij een droger nog belangrijker dan bij andere witgoed. De meeste moderne warmtepompdrogers zitten in de zuinigste klassen; condensdrogers scoren doorgaans merkbaar lager. Lees ook onze algemene <a href="/gidsen/energielabel-witgoed-uitgelegd">uitleg over energielabels</a> voor de achtergrond.</p>

<h2>Afvoer- of condensdroger: waar moet het water heen?</h2>
<p>Een condensdroger vangt het vocht uit de was op in een reservoir dat je regelmatig moet legen, of sluit je aan op een afvoer. Sommige modellen hebben een automatische afvoerslang naar de riolering, wat het legen overbodig maakt. Warmtepompdrogers werken vrijwel altijd met een reservoir, omdat ze geen actieve afvoer van warme lucht naar buiten nodig hebben — handig als je geen buitenmuur in de buurt hebt, in tegenstelling tot oudere afvoerdrogers die een slang naar buiten nodig hadden.</p>

<h2>Onderhoud: pluizenfilter en condensor</h2>
<p>Welk type droger je ook kiest, regelmatig onderhoud is belangrijk voor zowel de droogprestatie als de levensduur. Maak het pluizenfilter na iedere droogbeurt leeg, en reinig bij een warmtepompdroger periodiek (ongeveer elke paar maanden) ook de condensor, waar zich anders pluis kan ophopen dat de efficiëntie vermindert. Dit wordt vaak vergeten, maar heeft direct invloed op zowel de droogtijd als het energieverbruik.</p>

<h2>Kort samengevat</h2>
<p>Kies, tenzij het budget echt niet toelaat, voor een warmtepompdroger — het energieverschil met een condensdroger is bij regelmatig gebruik simpelweg te groot om te negeren. Stem de capaciteit af op je wasmachine, en onderhoud filter en condensor regelmatig om de efficiëntie op peil te houden.</p>
""",
}

WASDROOGCOMBI_GUIDE = {
    'slug': 'wasdroogcombinatie-kopen-voor-en-nadelen',
    'title': 'Wasdroogcombinatie kopen: voor- en nadelen op een rij',
    'excerpt': 'Eén apparaat dat wast én droogt — handig bij weinig ruimte, maar met een aantal praktische afwegingen die je vooraf moet kennen.',
    'category_slug': 'wasdroogcombinaties',
    'content': """
<p>Een wasdroogcombinatie combineert een wasmachine en droger in één toestel. Dit is aantrekkelijk als je weinig ruimte hebt of niet twee aparte apparaten wilt plaatsen, maar er zijn een paar praktische afwegingen om vooraf te kennen.</p>

<h2>Het belangrijkste nadeel: droogcapaciteit is vaak lager dan wascapaciteit</h2>
<p>Bij de meeste wasdroogcombinaties kun je bijvoorbeeld 9 kg was in één keer wassen, maar slechts 6 kg in één keer drogen. Dit betekent dat je bij een volle wasbeurt vaak een deel van de was er tussenuit moet halen voordat je kunt drogen, of in twee keer moet drogen. Let dus goed op de aparte was- én droogcapaciteit in de specificaties, niet alleen op het vulgewicht dat vaak prominent wordt vermeld.</p>

<h2>Eén apparaat, één storing</h2>
<p>Een praktisch nadeel: als het apparaat kapot gaat, ben je in één keer zowel je wasmachine als je droger kwijt, in plaats van dat je nog met één van de twee verder kunt.</p>

<h2>Energielabel en verbruik</h2>
<p>Wasdroogcombinaties hebben een eigen energielabel-systematiek die rekening houdt met zowel de was- als de droogfunctie. Omdat drogen relatief veel energie kost (zie onze <a href="/gidsen/droger-kopen-waar-op-letten">gids over drogers</a>), is het energielabel hier extra de moeite waard om te vergelijken tussen modellen.</p>

<h2>Voor wie is dit de juiste keuze?</h2>
<p>Een wasdroogcombinatie is vooral geschikt voor kleinere huishoudens met beperkte ruimte, bijvoorbeeld een appartement zonder aparte opstelplek voor twee apparaten. Voor grotere gezinnen die regelmatig volle wasladingen draaien, is een aparte wasmachine en droger vaak praktischer, juist vanwege het verschil in was- en droogcapaciteit.</p>

<h2>Langere programmaduur</h2>
<p>Omdat wassen en drogen na elkaar in hetzelfde toestel gebeuren, duurt een volledig was-en-droogprogramma bij een combinatie vaak aanzienlijk langer dan wanneer je een aparte wasmachine en droger gebruikt — soms wel 4 tot 5 uur voor een combinatieprogramma. Dat is geen probleem als je 's ochtends een programma start en 's avonds droge was uit de machine haalt, maar wel iets om rekening mee te houden als je snel schone kleding nodig hebt.</p>

<h2>Alternatief: stapelen in plaats van combineren</h2>
<p>Wie wél twee aparte apparaten wil maar weinig vloerruimte heeft, kan overwegen een wasmachine en droger op elkaar te stapelen met een speciaal stapelframe. Dit vraagt wel om voldoende stahoogte en is niet bij elk model mogelijk — check vooraf of de gewenste wasmachine en droger geschikt zijn om te stapelen, en of de afmetingen op elkaar aansluiten.</p>

<h2>Kort samengevat</h2>
<p>Let bij een wasdroogcombinatie extra goed op de aparte droogcapaciteit (vaak lager dan de wascapaciteit) en weeg de ruimtebesparing af tegen het risico dat je bij een defect in één keer beide functies kwijt bent. Heb je iets meer stahoogte beschikbaar, overweeg dan ook een gestapelde losse wasmachine en droger als alternatief.</p>
""",
}

VAATWASSER_GUIDE = {
    'slug': 'vaatwasser-kopen-complete-gids',
    'title': 'Vaatwasser kopen: waar moet je op letten?',
    'excerpt': 'Formaat, aantal couverts, energie- en waterverbruik en geluidsniveau uitgelegd, voor een vaatwasser die past bij je huishouden.',
    'category_slug': 'vaatwassers',
    'content': """
<p>Een vaatwasser gebruik je waarschijnlijk dagelijks, wat de keuze voor het juiste formaat en energielabel direct voelbaar maakt in je energie- en waterrekening.</p>

<h2>Formaat: volledig, smal of tafelmodel</h2>
<p>De standaardbreedte is 60 cm, geschikt voor de meeste huishoudens. Smalle vaatwassers (45 cm) zijn een goede optie voor kleinere keukens of 1-2 personen, maar bieden minder capaciteit per beurt. Tafelmodellen zijn er ook, vooral geschikt als er geen ruimte is voor een inbouw- of vrijstaand model.</p>

<h2>Aantal couverts</h2>
<p>De capaciteit van een vaatwasser wordt uitgedrukt in "couverts" (het aantal complete gedekte tafels dat erin past). Als richtlijn: 10-12 couverts voor 1-2 personen, 12-14 voor een gezin van 3-4 personen, en 14 of meer voor grotere huishoudens.</p>

<h2>Energie- en waterverbruik</h2>
<p>Net als bij een wasmachine loopt het energielabel van A tot G. Omdat een vaatwasser bij de meeste huishoudens dagelijks of bijna dagelijks draait, telt het verschil tussen een zuinig en minder zuinig model op termijn stevig op — zie onze algemene <a href="/gidsen/energielabel-witgoed-uitgelegd">uitleg over energielabels</a>. Let ook op het waterverbruik per programma, in liters: moderne vaatwassers gebruiken vaak minder water dan handmatig afwassen.</p>

<h2>Geluidsniveau</h2>
<p>Draait je vaatwasser vaak 's avonds of in een open keuken? Let dan op het geluidsniveau in dB. Stille modellen zitten rond de 40-44 dB; wie extra gevoelig is voor geluid kan kiezen voor modellen onder de 40 dB.</p>

<h2>Programma's: meer dan alleen "standaard"</h2>
<p>De meeste vaatwassers hebben naast een standaardprogramma ook een ECO-stand (lagere temperatuur, langere duur, minder verbruik — zie onze <a href="/gidsen/energielabel-witgoed-uitgelegd">uitleg over ECO-programma's</a>), een kort/snelprogramma voor licht vervuild serviesgoed, en vaak een intensief programma voor pannen en ovenschalen. Let bij het vergelijken niet alleen op het aantal programma's, maar vooral of de programma's aansluiten bij hoe je daadwerkelijk afwast — veel extra programma's die je nooit gebruikt voegen weinig waarde toe.</p>

<h2>Besteklade: een klein detail met groot gemak</h2>
<p>Veel nieuwere vaatwassers hebben een derde lade specifiek voor bestek, bovenin het apparaat, in plaats van een bestekmandje in de onderste lade. Dit geeft meer ruimte in de onderste lade voor pannen en schalen, en zorgt vaak voor een beter wasresultaat van het bestek zelf. Niet essentieel, maar wel een prettig detail om op te letten bij het vergelijken van modellen.</p>

<h2>Kort samengevat</h2>
<p>Kies het formaat en aantal couverts op basis van huishoudgrootte, let op het energielabel omdat dit apparaat vaak dagelijks draait, en houd rekening met geluidsniveau als de vaatwasser in of naast een leefruimte staat. Check ook of de beschikbare programma's aansluiten bij je daadwerkelijke gebruik.</p>
""",
}

MAGNETRON_GUIDE = {
    'slug': 'magnetron-kopen-waar-op-letten',
    'title': 'Magnetron kopen: vermogen, inhoud en functies uitgelegd',
    'excerpt': 'Van simpel opwarmen tot combimagnetrons met grill en hetelucht — wat de specificaties van een magnetron echt betekenen.',
    'category_slug': 'magnetrons',
    'content': """
<p>Magnetrons variëren sterk in prijs en functionaliteit — van eenvoudige opwarmmodellen tot combimagnetrons die ook grillen en bakken. De juiste keuze hangt vooral af van waarvoor je het apparaat wilt gebruiken.</p>

<h2>Vermogen: hoe sneller, hoe hoger</h2>
<p>Het vermogen van een magnetron wordt uitgedrukt in watt, meestal tussen de 700 en 1000+ watt. Hoe hoger het vermogen, hoe sneller eten wordt opgewarmd of bereid. Voor dagelijks opwarmen van etensresten volstaat 700-800 watt ruimschoots; voor snel en gelijkmatig koken kies je beter voor 900 watt of meer.</p>

<h2>Inhoud</h2>
<p>De inhoud wordt uitgedrukt in liters, meestal tussen de 17 en 30+ liter. Een kleine magnetron (17-20 liter) is voldoende voor opwarmen van borden en kommen; wil je ook grotere schalen of een hele kip kunnen bereiden, kies dan voor 25 liter of meer.</p>

<h2>Type: solo, grill of combi</h2>
<ul>
    <li><strong>Solo-magnetron:</strong> alleen de basisfunctie, opwarmen en ontdooien</li>
    <li><strong>Grillmagnetron:</strong> heeft ook een grillelement voor bijvoorbeeld gegratineerde gerechten of krokante toppings</li>
    <li><strong>Combimagnetron:</strong> combineert magnetron, grill én hetelucht (convectie), waardoor je het apparaat ook als volwaardige oven kunt gebruiken</li>
</ul>
<p>Een combimagnetron is aanzienlijk duurder maar veel veelzijdiger — handig als je weinig aanrechtruimte hebt en geen aparte oven wilt.</p>

<h2>Inbouw versus vrijstaand</h2>
<p>Net als bij ovens en koelkasten zijn er inbouw- en vrijstaande magnetrons. Inbouwmodellen zien er strakker uit en besparen aanrechtruimte, maar zijn minder flexibel qua formaat en duurder dan vrijstaande modellen.</p>

<h2>Bediening: draaiknop of digitaal display</h2>
<p>Eenvoudigere magnetrons hebben een mechanische draaiknop voor tijd en vermogen, wat intuïtief en snel is voor dagelijks gebruik. Uitgebreidere modellen hebben een digitaal display met voorgeprogrammeerde functies (bijvoorbeeld automatisch ontdooien op basis van gewicht). Dit is vooral comfort — het zegt niets over de daadwerkelijke bereidingskwaliteit, dus laat dit niet je enige afwegingspunt zijn.</p>

<h2>Draaiplateau: glas of keramiek</h2>
<p>Vrijwel alle magnetrons hebben een draaiplateau dat zorgt voor gelijkmatige verwarming. Let bij vervanging of aankoop op de diameter, zeker als je vaak grotere schalen gebruikt — een groter plateau biedt meer flexibiliteit maar vraagt ook om een ruimere binnenkant.</p>

<h2>Kort samengevat</h2>
<p>Bepaal eerst of je alleen wilt opwarmen (solo volstaat) of ook echt wilt koken en bakken (kies dan voor een combimagnetron), en stem het vermogen en de inhoud af op je huishoudgrootte en gebruiksdoel.</p>
""",
}

OVEN_GUIDE = {
    'slug': 'oven-kopen-complete-gids',
    'title': 'Oven kopen: de complete gids',
    'excerpt': 'Hetelucht versus boven-onderwarmte, inhoud, energielabel en pyrolyse-reiniging uitgelegd.',
    'category_slug': 'ovens',
    'content': """
<p>Een oven gaat vaak lang mee, dus is het de moeite waard om even stil te staan bij de belangrijkste verschillen voordat je een keuze maakt.</p>

<h2>Hetelucht (convectie) versus boven-onderwarmte</h2>
<p>Bij <strong>boven-onderwarmte</strong> komt de warmte van boven en onder de gerechten, zonder actieve luchtcirculatie — traditioneel en geschikt voor bijvoorbeeld gebak dat gelijkmatig moet rijzen. Bij <strong>hetelucht</strong> circuleert een ventilator de warme lucht door de hele ovenruimte, wat zorgt voor een gelijkmatigere temperatuur en vaak kortere bereidingstijden, en waardoor je op meerdere niveaus tegelijk kunt bakken zonder dat smaken zich vermengen. De meeste moderne ovens bieden beide standen.</p>

<h2>Inhoud</h2>
<p>De inhoud wordt uitgedrukt in liters, meestal tussen de 50 en 75 liter voor standaard inbouwovens. Grotere gezinnen of wie vaak grote gerechten (zoals een hele kalkoen) bereidt, heeft baat bij een ruimere oven.</p>

<h2>Energielabel</h2>
<p>Ook ovens hebben een energielabel, van A tot G. Het verschil in verbruik tussen klassen is bij een oven relatief kleiner dan bij bijvoorbeeld een koelkast, maar telt bij regelmatig gebruik alsnog op — zie onze <a href="/gidsen/energielabel-witgoed-uitgelegd">algemene uitleg over energielabels</a>.</p>

<h2>Pyrolyse- of katalytische reiniging</h2>
<p>Sommige ovens hebben een zelfreinigingsfunctie. Bij <strong>pyrolyse</strong> verhit de oven zichzelf tot een zeer hoge temperatuur, waardoor vuil verast tot as die je simpelweg uitveegt — effectief, maar verbruikt tijdens de reinigingscyclus relatief veel stroom. <strong>Katalytische</strong> reiniging gebruikt een speciale binnenwand die vet tijdens normaal gebruik geleidelijk afbreekt, minder krachtig maar ook minder energie-intensief.</p>

<h2>Inbouw versus vrijstaand</h2>
<p>Inbouwovens zijn ontworpen om in een keukenkast te passen en ogen strakker, maar zijn minder flexibel in formaat en duurder dan vrijstaande fornuizen met geïntegreerde oven.</p>

<h2>Stoomondersteuning: vochtiger en gezonder bereiden</h2>
<p>Sommige (vaak duurdere) ovens hebben een stoomfunctie, waarbij tijdens het bakken of braden vocht wordt toegevoegd. Dit voorkomt uitdroging van vlees en groenten, en zorgt bijvoorbeeld voor knapperiger brood met een luchtiger binnenkant. Voor wie regelmatig bakt of vlees bereidt, is dit een waardevolle toevoeging; voor incidenteel gebruik weegt de meerprijs vaak niet op tegen het voordeel.</p>

<h2>Aantal bakniveaus en toebehoren</h2>
<p>Let bij het vergelijken ook op het aantal bakniveaus en het meegeleverde toebehoren (bakplaten, grillrooster, braadslede). Een oven met meer niveaus geeft flexibiliteit om op meerdere hoogtes tegelijk te bakken, vooral relevant in combinatie met hetelucht.</p>

<h2>Kort samengevat</h2>
<p>Kies hetelucht als je op meerdere niveaus tegelijk wilt bakken, stem de inhoud af op je huishoudgrootte, en overweeg pyrolysereiniging als gemak zwaarder weegt dan het iets hogere energieverbruik tijdens het reinigen. Bak je regelmatig brood of vlees, dan is stoomondersteuning het overwegen waard.</p>
""",
}

STOFZUIGER_GUIDE = {
    'slug': 'stofzuiger-kopen-waar-op-letten',
    'title': 'Stofzuiger kopen: zak, zakloos of robot?',
    'excerpt': 'De belangrijkste verschillen tussen stofzuigertypen, en waar je op moet letten qua vermogen, filters en actieradius.',
    'category_slug': 'stofzuigers',
    'content': """
<p>Het aanbod aan stofzuigers is inmiddels groot: van traditionele modellen met stofzak tot draadloze steelstofzuigers en volautomatische robotstofzuigers. Welk type het beste past, hangt vooral af van je woning en persoonlijke voorkeur.</p>

<h2>Met stofzak of zakloos</h2>
<p>Stofzuigers met een <strong>stofzak</strong> zijn vaak hygiënischer bij het legen (je gooit de hele zak weg zonder stofcontact) en hebben doorgaans een goede filtering, maar je hebt terugkerende kosten voor nieuwe zakken. <strong>Zakloze</strong> stofzuigers besparen die kosten en tonen direct hoeveel vuil is opgezogen, maar het legen van het stofreservoir kan stof verspreiden en vereist regelmatig schoonmaken van filters.</p>

<h2>Steelstofzuiger versus traditionele stofzuiger</h2>
<p>Draadloze steelstofzuigers zijn licht, wendbaar en handig voor snel gebruik, maar de accuduur (meestal 20-60 minuten) kan beperkend zijn bij grotere woningen. Traditionele stofzuigers met snoer hebben onbeperkte gebruiksduur en vaak meer zuigkracht, maar zijn minder wendbaar en zwaarder om te dragen.</p>

<h2>Robotstofzuiger: gemak, met wat kanttekeningen</h2>
<p>Een robotstofzuiger stofzuigt automatisch volgens een schema, wat vooral prettig is voor onderhoudsstofzuigen tussen grondige beurten door. Let op: robotstofzuigers zijn minder geschikt als enige stofzuiger in huis — ze hebben moeite met hoge drempels, veel obstakels, of hoeken, en zijn typisch een aanvulling op (niet vervanging van) een reguliere stofzuiger.</p>

<h2>Vermogen en zuigkracht</h2>
<p>Let niet alleen op het opgenomen vermogen in watt (dat zegt vooral iets over energieverbruik), maar vooral op de daadwerkelijke zuigkracht, vaak uitgedrukt in Air Watt (AW) of kPa in de specificaties. Een hoger AW-getal duidt op effectievere reiniging, vooral merkbaar op tapijt.</p>

<h2>Filters voor huisstofallergie</h2>
<p>Heb je huisstofallergie, let dan op een HEPA-filter. Deze vangt fijnstof en allergenen effectiever af dan standaardfilters, wat een merkbaar verschil kan maken in luchtkwaliteit.</p>

<h2>Geschikt voor huisdieren?</h2>
<p>Heb je huisdieren, kijk dan specifiek naar modellen die geadverteerd worden met een dierenhaar-borstel of speciaal mondstuk voor haren op tapijt en meubels. Standaard borstels raken sneller verstopt met haren, wat de zuigkracht op termijn vermindert. Sommige fabrikanten bieden speciale "pet"-varianten van hun stofzuigers met een aangepaste borstelrol hiervoor.</p>

<h2>Actieradius en accessoires</h2>
<p>Bij een stofzuiger met snoer bepaalt de snoerlengte plus de lengte van de slang je actieradius zonder te hoeven verplaatsen naar een ander stopcontact — praktisch bij grotere woningen. Kijk ook naar meegeleverde hulpstukken zoals een kierenzuiger, meubelborstel of mondstuk voor harde vloeren, die het gebruiksgemak sterk kunnen beïnvloeden.</p>

<h2>Kort samengevat</h2>
<p>Kies stofzak voor gemak bij legen en goede filtering, zakloos om terugkerende kosten te besparen, een steelstofzuiger voor wendbaarheid bij kleinere woningen, en overweeg een robotstofzuiger als aanvulling — niet als vervanging — voor onderhoudsstofzuigen tussendoor. Heb je huisdieren of huisstofallergie, let dan specifiek op de borstel respectievelijk het filtersysteem.</p>
""",
}


ALL_GUIDES = [
    WASMACHINE_GUIDE, KOELKAST_GUIDE, ENERGY_LABEL_GUIDE, WASMACHINE_COMPARISON_GUIDE,
    DROGER_GUIDE, WASDROOGCOMBI_GUIDE, VAATWASSER_GUIDE, MAGNETRON_GUIDE, OVEN_GUIDE, STOFZUIGER_GUIDE,
]


def seed():
    from app import create_app
    from models import db, Category, Guide

    app = create_app()

    with app.app_context():
        for guide_data in ALL_GUIDES:
            Guide.query.filter_by(slug=guide_data['slug']).delete()

            category = None
            if guide_data['category_slug']:
                category = Category.query.filter_by(slug=guide_data['category_slug']).first()

            guide = Guide(
                title=guide_data['title'],
                slug=guide_data['slug'],
                excerpt=guide_data['excerpt'],
                content=guide_data['content'].strip(),
                category_id=category.id if category else None,
                post_type='guide',
            )
            db.session.add(guide)
            print(f"[+] Added guide: {guide_data['title']}")

        for post_data in BLOG_POSTS:
            Guide.query.filter_by(slug=post_data['slug']).delete()

            category = None
            if post_data['category_slug']:
                category = Category.query.filter_by(slug=post_data['category_slug']).first()

            post = Guide(
                title=post_data['title'],
                slug=post_data['slug'],
                excerpt=post_data['excerpt'],
                content=post_data['content'].strip(),
                category_id=category.id if category else None,
                post_type='blog',
            )
            db.session.add(post)
            print(f"[+] Added blog post: {post_data['title']}")

        db.session.commit()
        print(f"\n[+] {len(ALL_GUIDES)} guides + {len(BLOG_POSTS)} blog posts seeded successfully")


if __name__ == '__main__':
    seed()
