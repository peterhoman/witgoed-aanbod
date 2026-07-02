#!/usr/bin/env python
"""
Seed the database with original buying guides and product comparisons.

Written to give visitors genuine, independent advice (not copied from
manufacturer or retailer marketing text), addressing Bol.com's affiliate
review feedback that the site needs more "added value" content beyond
plain product listings ("niet alleen doorlinken, maar mensen helpen
kiezen").

Safe to re-run: existing guides (matched by slug) are replaced.
"""

from app import create_app
from models import db, Category, Guide

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
<p>Met 10,5 kg vulgewicht en 1400 rpm centrifugeren is dit de machine met de grootste capaciteit van de drie, voor circa €499. Geschikt voor grotere gezinnen of huishoudens die liever minder vaak, maar dan in grote ladingen wassen. Energielabel A maakt hem ook op verbruik een solide keuze, ondanks de grotere trommel.</p>

<h2>AEG LR8686UC4 8000 PowerCare UniversalDose — de zuinigste keuze</h2>
<p>Deze AEG heeft een kleiner vulgewicht (8 kg) dan de Hisense, voor circa €749. Het opvallendste kenmerk: dit model is tot 40% zuiniger dan wettelijk vereist voor energielabel A, wat hem tot de zuinigste van de drie maakt. De hogere aanschafprijs wordt deels gecompenseerd door een lager energieverbruik per wasbeurt — voor wie veel wast en op de lange termijn wil besparen, is dit de moeite waard om te overwegen.</p>

<h2>Samsung WW90CGC04AAHEN Ecobubble 5000 — de gebalanceerde middenmoot</h2>
<p>Met 9 kg vulgewicht zit deze Samsung qua capaciteit tussen de andere twee in, voor circa €499. De Ecobubble-technologie zorgt ervoor dat wasmiddel sneller en gelijkmatiger inwerkt via een bellenmengsel, wat effectief wassen op lagere temperaturen mogelijk maakt — praktisch voor wie vaker op 30 graden wast. Energielabel A, 10% zuiniger dan het wettelijk vereiste minimum.</p>

<h2>Welke past bij jou?</h2>
<ul>
    <li><strong>Groot gezin, minder vaak wassen:</strong> de Hisense, vanwege het hoogste vulgewicht.</li>
    <li><strong>Vaak wassen, energiekosten op lange termijn belangrijk:</strong> de AEG, vanwege het laagste energieverbruik ten opzichte van het wettelijk minimum.</li>
    <li><strong>Gemiddeld huishouden, vaak op lage temperatuur wassen:</strong> de Samsung, vanwege de Ecobubble-technologie en gebalanceerde specificaties.</li>
</ul>
<p>Alle drie zijn voorladers met een energielabel A of beter — het verschil zit hem vooral in vulgewicht en de mate waarin ze het wettelijke minimum overtreffen.</p>

<h2>Prijs-kwaliteitverhouding: waarom de goedkoopste niet altijd de beste keuze is</h2>
<p>Opvallend genoeg zijn de Hisense en de Samsung in deze vergelijking even duur (circa €499), terwijl de AEG €250 meer kost. Dat prijsverschil zit hem grotendeels in het energielabel: de AEG verbruikt tot 40% minder dan wettelijk vereist, tegenover 10% bij de Samsung en het wettelijk minimum bij de Hisense. Was je bijvoorbeeld 4 keer per week, dan kan dat verbruiksverschil de hogere aanschafprijs van de AEG binnen enkele jaren compenseren — reken dit na met de vuistregel uit onze <a href="/gidsen/energielabel-witgoed-uitgelegd">gids over energielabels</a>. Voor wie minder vaak wast of een kleiner budget heeft, is het verschil in de praktijk vaak te klein om de hogere aanschafprijs te rechtvaardigen, en is de Hisense of Samsung de verstandigere keuze.</p>

<p>Bekijk de actuele prijzen en beschikbaarheid van deze en andere modellen in onze <a href="/category/wasmachines">categorie wasmachines</a>.</p>
""",
}


def seed():
    app = create_app()

    with app.app_context():
        all_guides = [WASMACHINE_GUIDE, KOELKAST_GUIDE, ENERGY_LABEL_GUIDE, WASMACHINE_COMPARISON_GUIDE]

        for guide_data in all_guides:
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
            )
            db.session.add(guide)
            print(f"[+] Added guide: {guide_data['title']}")

        db.session.commit()
        print(f"\n[+] {len(all_guides)} guides seeded successfully")


if __name__ == '__main__':
    seed()
