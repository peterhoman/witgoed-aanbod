"""Nieuwe koopgidsen die automatisch bij een deploy worden gepubliceerd.

Pure data + één idempotente ensure-functie, bewust zonder imports uit app
of models (geen circulaire imports): app.py roept ensure_new_guides() aan
bij het opstarten en geeft db/Category/Guide mee. Bestaande gidsen worden
nooit overschreven — alleen ontbrekende slugs worden toegevoegd. De
volledige her-seed van al het oudere materiaal blijft in seed_guides.py.

Deze gidsen mikken op longtail-zoekvragen ("warmtepompdroger of
condensdroger") in plaats van de bredere categorie-koopgidsen die er al
staan, en rekenen waar mogelijk met concrete kosten — content die de
aangesloten winkels zelf niet bieden.
"""

NEW_GUIDES = [
    {
        'slug': 'warmtepompdroger-of-condensdroger',
        'title': 'Warmtepompdroger of condensdroger: welke moet je kiezen?',
        'excerpt': 'Het prijsverschil lijkt groot, maar wie de stroomkosten meerekent komt bijna altijd bij de warmtepompdroger uit. We rekenen het voor.',
        'category_slug': 'drogers',
        'content': """
<p>Wie een droger zoekt, komt direct voor deze keuze te staan: een condensdroger voor een lagere aanschafprijs, of een warmtepompdroger die zuiniger is maar meer kost. Het korte antwoord: <strong>voor vrijwel iedereen die minstens twee keer per week droogt, is de warmtepompdroger de verstandigste keuze</strong>. Hieronder rekenen we voor waarom — en benoemen we de gevallen waarin een condensdroger tóch logischer is.</p>

<h2>Het verschil in één alinea</h2>
<p>Een <strong>condensdroger</strong> verwarmt lucht met een verwarmingselement, zoals een föhn: simpel, snel, maar energie-intensief. Een <strong>warmtepompdroger</strong> hergebruikt de warmte in een gesloten circuit, vergelijkbaar met de techniek in een koelkast (maar dan omgekeerd). Daardoor verbruikt hij per droogbeurt grofweg de helft tot een derde van de stroom.</p>

<h2>De rekensom</h2>
<p>Het werkelijke verbruik verschilt per model en per lading, maar als vuistregel per droogbeurt (8 kg was):</p>
<table class="comparison-table">
    <thead>
        <tr><th></th><th>Condensdroger</th><th>Warmtepompdroger</th></tr>
    </thead>
    <tbody>
        <tr><td>Stroomverbruik per beurt</td><td>± 4 kWh</td><td>± 1,5 kWh</td></tr>
        <tr><td>Kosten per beurt (bij € 0,30/kWh)</td><td>± € 1,20</td><td>± € 0,45</td></tr>
        <tr><td>Jaarkosten bij 3 beurten/week</td><td>± € 190</td><td>± € 70</td></tr>
    </tbody>
</table>
<p>Het verschil is dus al snel zo'n <strong>€ 120 per jaar</strong> bij drie droogbeurten per week. Is een warmtepompdroger € 200 tot € 300 duurder in aanschaf, dan is dat verschil binnen twee tot drie jaar terugverdiend — terwijl een droger gemiddeld tien jaar of langer meegaat. Over de hele levensduur bespaart een gemiddeld huishouden al gauw duizend euro of meer. Droog je vaker (gezin met kinderen, sportkleding), dan gaat de rekensom nog sneller in het voordeel van de warmtepomp.</p>

<h2>De nadelen van de warmtepompdroger (eerlijk is eerlijk)</h2>
<ul>
    <li><strong>Langere droogtijd:</strong> omdat hij op lagere temperatuur droogt, duurt een beurt vaak 2 tot 3 uur, tegenover 1 tot 2 uur bij een condensdroger. Wie 's ochtends start en 's avonds droge was pakt, merkt hier niets van.</li>
    <li><strong>Hogere aanschafprijs:</strong> het instapniveau ligt hoger, al is dat verschil de afgelopen jaren flink gekrompen.</li>
    <li><strong>Iets meer onderhoud:</strong> naast het pluizenfilter moet ook de condensor af en toe worden schoongemaakt.</li>
</ul>
<p>Dat lagere-temperatuur-drogen heeft trouwens ook een voordeel: het is zachter voor kleding, waardoor die minder slijt en krimpt.</p>

<h2>Wanneer is een condensdroger wél logisch?</h2>
<ul>
    <li>Je droogt maar zelden — bijvoorbeeld alleen in de wintermaanden of bij noodgevallen. Dan verdient de meerprijs zich niet terug.</li>
    <li>Het aanschafbudget is nu simpelweg de beperkende factor.</li>
    <li>Je hebt de droger tijdelijk nodig (studentenkamer, tussenwoning, overbrugging).</li>
</ul>

<h2>Waar je verder op moet letten</h2>
<p>Kies je eenmaal het type, kijk dan naar capaciteit (afstemmen op je wasmachine), energielabel binnen het type — de verschillen tussen warmtepompdrogers onderling zijn nog steeds fors — en het geluidsniveau als de droger in een leefruimte staat. Onze algemene <a href="/gidsen/droger-kopen-waar-op-letten">koopgids voor drogers</a> loopt al deze punten langs, en in onze <a href="/gidsen/energielabel-witgoed-uitgelegd">uitleg over energielabels</a> lees je hoe je de terugverdientijd zelf narekent voor twee concrete modellen.</p>

<h2>Kort samengevat</h2>
<p>Droog je twee keer per week of vaker: warmtepompdroger, zonder twijfel — de meerprijs is binnen een paar jaar terugverdiend en daarna bespaar je elk jaar ruim € 100. Droog je zelden of is het budget krap: dan is een condensdroger een prima pragmatische keuze. Bekijk de actuele prijzen van beide typen in onze <a href="/category/drogers">categorie drogers</a>.</p>
""",
    },
    {
        'slug': 'wasmachine-8-of-9-kg',
        'title': 'Wasmachine van 8 of 9 kg: welk vulgewicht heb je echt nodig?',
        'excerpt': 'Het verschil van één kilo klinkt klein, maar bepaalt of je dekbedovertrek in één beurt mee kan. Zo kies je het juiste vulgewicht.',
        'category_slug': 'wasmachines',
        'content': """
<p>Tussen een wasmachine van 8 kg en één van 9 kg zit vaak maar een klein prijsverschil, en dat maakt de keuze verraderlijk: "doe dan maar de grote" is snel gezegd. Toch loont het om even echt na te denken over wat je wast — want zowel te klein als te groot kopen kost geld.</p>

<h2>Wat past er eigenlijk in een kilo?</h2>
<p>Het vulgewicht gaat over <em>droge</em> was. Ter indicatie: een spijkerbroek weegt ± 700 gram, een handdoek ± 500 gram, een overhemd ± 250 gram en een tweepersoons dekbedovertrek ± 1,5 kg. Een gemiddelde volle wasmand van een gezin komt op 6 à 8 kg uit.</p>

<h2>De vuistregel per huishouden</h2>
<ul>
    <li><strong>1-2 personen:</strong> 7 kg volstaat; 8 kg geeft ruimte voor beddengoed</li>
    <li><strong>3-4 personen:</strong> 8-9 kg is de sweet spot</li>
    <li><strong>5 of meer personen:</strong> 9-10,5 kg voorkomt dat je dagelijks moet draaien</li>
</ul>

<h2>Het echte verschil: beddengoed en winterjassen</h2>
<p>Voor dagelijkse was maakt die ene kilo weinig uit. Het verschil merk je bij groot textiel: een tweepersoons dekbedovertrek plus hoeslaken en kussenslopen wil in een 9 kg-trommel nog comfortabel in één beurt, terwijl het in een 8 kg-machine al krap wordt — en een te volle trommel wast aantoonbaar slechter, omdat de was niet vrij kan bewegen. Was je regelmatig dekbedden, dekens of winterjassen, dan is 9 kg (of meer) het overwegen waard. Vuistregel: de trommel is goed gevuld als er bovenin nog een handbreedte ruimte vrij is.</p>

<h2>Te groot kopen kost óók geld</h2>
<p>Een grotere trommel die structureel halfvol draait, verspilt water en stroom: veel machines gebruiken een minimale hoeveelheid water per beurt, ongeacht de vulling. Moderne modellen met een <strong>beladingssensor</strong> passen het verbruik automatisch aan, maar niet elk model heeft die — check dat in de specificaties voordat je "voor de zekerheid" een maat groter koopt. Draai je vrijwel altijd kleine wasjes, dan is groter dus niet beter.</p>

<h2>Kort samengevat</h2>
<p>Kies 8 kg als je met 2-3 personen bent en beddengoed geen hoofdrol speelt; kies 9 kg bij een gezin of als je dekbedovertrekken en groot textiel in één beurt wilt wassen. Twijfel je tussen twee modellen, kijk dan ook naar toerental en energielabel — die maken in de praktijk meer verschil dan die ene kilo. Onze <a href="/gidsen/wasmachine-kopen-waar-op-letten">complete wasmachine-koopgids</a> legt alle specificaties uit, en in de <a href="/category/wasmachines">categorie wasmachines</a> kun je op vulgewicht filteren en direct prijzen vergelijken.</p>
""",
    },
    {
        'slug': 'stroomverbruik-koelkast-per-jaar',
        'title': 'Hoeveel stroom verbruikt een koelkast? (en wanneer loont vervangen)',
        'excerpt': 'Een koelkast staat altijd aan. We rekenen uit wat dat per jaar kost, en vanaf welk punt een oude koelkast vervangen goedkoper is dan hem laten staan.',
        'category_slug': 'koelkasten',
        'content': """
<p>Een koelkast is het enige grote apparaat in huis dat nooit uitstaat. Het stroomverbruik lijkt per dag verwaarloosbaar, maar juist door die 8.760 draaiuren per jaar telt elk wattje op. In deze gids: wat een koelkast werkelijk kost per jaar, hoe je dat zelf opzoekt, en de rekensom die bepaalt of je oude koelkast vervangen het waard is.</p>

<h2>Wat verbruikt een koelkast per jaar?</h2>
<p>Het jaarverbruik staat gewoon op het energielabel, in kWh per jaar. Ter indicatie, voor een koel-vriescombinatie van gemiddeld formaat (± 300 liter):</p>
<table class="comparison-table">
    <thead>
        <tr><th>Type / leeftijd</th><th>Verbruik per jaar</th><th>Kosten per jaar (€ 0,30/kWh)</th></tr>
    </thead>
    <tbody>
        <tr><td>Nieuw, energielabel A-C</td><td>100-160 kWh</td><td>€ 30-50</td></tr>
        <tr><td>Nieuw, energielabel D-F</td><td>160-250 kWh</td><td>€ 50-75</td></tr>
        <tr><td>10-15 jaar oud</td><td>250-400 kWh</td><td>€ 75-120</td></tr>
        <tr><td>Ouder dan 15 jaar</td><td>400-600 kWh</td><td>€ 120-180</td></tr>
    </tbody>
</table>
<p>De cijfers voor oudere koelkasten zijn indicatief: verbruik loopt op naarmate isolatie en rubbers verouderen, en oude apparaten waren sowieso minder zuinig ontworpen. Wil je het precies weten, dan kun je het werkelijke verbruik meten met een energiemeter tussen stekker en stopcontact (± € 15), of het jaarverbruik van je huidige model opzoeken via de QR-code op het label of in de Europese productendatabank EPREL.</p>

<h2>De vervangingsrekensom</h2>
<p>Stel: je koelkast van 14 jaar oud verbruikt 350 kWh per jaar (€ 105). Een vergelijkbare nieuwe met label B verbruikt 130 kWh (€ 39). Besparing: <strong>€ 66 per jaar</strong>. Kost de nieuwe € 500, dan is de terugverdientijd 7 à 8 jaar — op het randje, want zo lang gaat een koelkast gemiddeld nog wel mee. Maar verbruikt je oude apparaat 500 kWh (€ 150/jaar) en vind je een nieuwe voor € 400, dan zit je op 3 à 4 jaar en is vervangen financieel een no-brainer. De vuistregel: <strong>vervang een werkende koelkast puur om het verbruik pas als hij ouder is dan ± 12 jaar én de terugverdientijd onder de 5 jaar uitkomt</strong> — en check de actuele prijzen, want die bepalen de helft van de som.</p>

<h2>Zo houd je het verbruik laag (nieuw én oud)</h2>
<ul>
    <li>Stel de koelkast in op <strong>4 °C</strong> en het vriesvak op −18 °C; elke graad kouder kost ± 5% extra stroom.</li>
    <li>Houd de ventilatieruimte achter en boven het apparaat vrij, en zet hem niet naast de oven of in de zon.</li>
    <li>Ontdooi een vriesvak zonder No Frost bij meer dan een halve centimeter ijs: ijsaanslag werkt als isolatie op de verkeerde plek.</li>
    <li>Controleer de deurrubbers: klemt een tussengeschoven papiertje niet meer, dan lekt er koude lucht weg.</li>
    <li>Laat warme gerechten eerst afkoelen voordat ze de koelkast in gaan.</li>
</ul>

<h2>Kort samengevat</h2>
<p>Een moderne, zuinige koelkast kost € 30-50 per jaar aan stroom; een oude al snel het drievoudige. Zoek het werkelijke verbruik van je huidige apparaat op, reken de terugverdientijd uit, en laat die som — niet de leeftijd alleen — bepalen of vervangen loont. Meer weten over waar je bij een nieuwe koelkast op let, zoals inhoud, No Frost en klimaatklasse? Lees onze <a href="/gidsen/koelkast-kopen-complete-gids">complete koelkast-koopgids</a>, bekijk de <a href="/gidsen/energielabel-witgoed-uitgelegd">uitleg over energielabels</a>, of vergelijk direct prijzen in de <a href="/category/koelkasten">categorie koelkasten</a>.</p>
""",
    },
]


def ensure_new_guides(db, Category, Guide):
    """Voeg gidsen uit NEW_GUIDES toe die nog niet in de database staan.

    Idempotent en niet-destructief: bestaande slugs blijven onaangeroerd,
    zodat handmatige aanpassingen in productie nooit worden overschreven.
    Geeft het aantal toegevoegde gidsen terug.
    """
    added = 0
    for data in NEW_GUIDES:
        if Guide.query.filter_by(slug=data['slug']).first():
            continue
        category = None
        if data['category_slug']:
            category = Category.query.filter_by(slug=data['category_slug']).first()
        db.session.add(Guide(
            title=data['title'],
            slug=data['slug'],
            excerpt=data['excerpt'],
            content=data['content'].strip(),
            category_id=category.id if category else None,
            post_type='guide',
        ))
        added += 1
    if added:
        db.session.commit()
    return added
