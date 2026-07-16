"""Nieuwe koopgidsen die automatisch bij een deploy worden gepubliceerd.

Pure data + één idempotente ensure-functie, bewust zonder imports uit app
of models (geen circulaire imports): app.py roept ensure_new_guides() aan
bij het opstarten en geeft db/Category/Guide mee. Voor de slugs in
NEW_GUIDES is dít bestand de bron van de waarheid: ontbrekende gidsen
worden toegevoegd én bestaande worden bijgewerkt zodra de tekst hier
wijzigt (zo bereiken correcties, zoals een verkeerd modelnummer, ook
productie). Gidsen die hier niet in staan blijven onaangeroerd; de
volledige her-seed van al het oudere materiaal blijft in seed_guides.py.

Deze gidsen mikken op longtail-zoekvragen ("warmtepompdroger of
condensdroger") in plaats van de bredere categorie-koopgidsen die er al
staan, en rekenen waar mogelijk met concrete kosten — content die de
aangesloten winkels zelf niet bieden.
"""

NEW_GUIDES = [
    {
        'slug': 'beste-koelkast-2026',
        'title': 'De 5 beste koelkasten van 2026',
        'excerpt': 'Vijf winnaars voor elk huishouden — van compact tafelmodel tot Amerikaanse blikvanger — mét wat elke koelkast per jaar aan stroom kost. Met video.',
        'category_slug': 'koelkasten',
        'content': """
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": "De 5 beste koelkasten van 2026 — koopgids",
    "description": "De vijf beste koelkasten van dit moment voor elk huishouden, van tafelmodel tot Amerikaanse koelkast — met per model het jaarlijkse stroomverbruik. Alle prijzen komen van WitgoedAanbod.nl.",
    "thumbnailUrl": "https://i.ytimg.com/vi/-wLFTVQpy3A/hqdefault.jpg",
    "uploadDate": "2026-07-16",
    "embedUrl": "https://www.youtube-nocookie.com/embed/-wLFTVQpy3A",
    "contentUrl": "https://www.youtube.com/watch?v=-wLFTVQpy3A",
    "publisher": {"@type": "Organization", "name": "WitgoedAanbod.nl"}
}
</script>
<p>Een koelkast staat 24 uur per dag aan, zo'n vijftien jaar lang. Daarmee is het sluipende stroomverbruik n&eacute;t zo belangrijk als de aanschafprijs — en precies daar kijken we in deze koopgids naar. Dit zijn de vijf beste koelkasten van dit moment, voor elk huishouden &eacute;&eacute;n: van tafelmodel tot Amerikaanse blikvanger. We letten op de <strong>inhoud</strong> (liters), het <strong>geluid</strong> (een koelkast hoor je dag en nacht) en vooral het <strong>jaarlijkse stroomverbruik</strong> — reken gemiddeld zo'n &euro; 0,30 per kilowattuur, of lees onze <a href="/gidsen/stroomverbruik-koelkast-per-jaar">uitleg over het stroomverbruik van koelkasten</a>.</p>

<p>Liever kijken dan lezen? Hier is de video-versie:</p>
<div style="position:relative;width:100%;max-width:800px;margin:0 auto 24px;aspect-ratio:16/9;">
    <iframe
        src="https://www.youtube-nocookie.com/embed/-wLFTVQpy3A"
        title="De 5 beste koelkasten van 2026 — koopgids"
        style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;border-radius:12px;"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen>
    </iframe>
</div>

<h2>De top 5 met actuele prijzen</h2>
<!--productkaart ean=8592344700514 rank=1 label="De blikvanger: Amerikaans, 559 liter"-->
<!--productkaart ean=4242005517169 rank=2 label="Inbouw: bespaart tot &euro;640 over de levensduur"-->
<!--productkaart ean=4242005254330 rank=3 label="D&eacute; gezins-allrounder: 337 l, VitaFresh"-->
<!--productkaart ean=8592344703225 rank=4 label="Beste compacte combi: 231 l, No Frost"-->
<!--productkaart ean=8712876501681 rank=5 label="Tafelmodel: &plusmn; &euro;33 stroom per jaar"-->

<h2>1. CHiQ Amerikaanse koelkast (559 l) — de blikvanger</h2>
<p>Maar liefst 559 liter, No Frost en plek voor de boodschappen van een heel gezin — voor ruim &euro; 600, waar Amerikaanse koelkasten normaal ver boven de duizend zitten. Wel eerlijk: 362 kWh per jaar is ruim &euro; 100 aan stroom. Grote koelkast, groter verbruik — dat is de afweging. Bekijk de actuele prijs van de <a href="/product/chiq-fss559nei42d---amerikaanse-koelkast---559-lit-8592344700514">CHiQ FSS559NEI42D</a>.</p>

<h2>2. Bosch KIN86 — inbouw die zichzelf deels terugverdient</h2>
<p>Voor wie de koelkast liever niet z&iacute;et: hij verdwijnt naadloos in het keukenblok en is z&oacute; zuinig dat je volgens Bosch tot &euro; 640 aan energiekosten bespaart over de levensduur. De duurste van deze lijst, maar wel eentje die zichzelf deels terugverdient. Bekijk de actuele prijs van de <a href="/product/bosch-kin86adb0-4242005517169">Bosch KIN86ADB0</a>.</p>

<h2>3. Bosch KGE398 Serie 6 — d&eacute; allrounder voor gezinnen</h2>
<p>337 liter, 60 cm breed — hij past in elke keuken — en het VitaFresh-systeem regelt automatisch de luchtvochtigheid zodat groente en fruit langer vers blijven. Degelijkheid waar je vijftien jaar plezier van hebt. Bekijk de actuele prijs van de <a href="/product/bosch-kge398ibp---koel-vriescombinatie-breedte-60--4242005254330">Bosch KGE398IBP</a>.</p>

<h2>4. CHiQ koel-vriescombinatie (231 l) — beste compacte combi</h2>
<p>Volwaardig koelen &eacute;n vriezen m&eacute;t No Frost (dus nooit meer ontdooien) voor nog geen &euro; 400 — ideaal voor een- en tweepersoonshuishoudens. Let w&eacute;l op het energielabel E: zo'n &euro; 80 aan stroom per jaar. Goedkoop in aanschaf, gemiddeld in verbruik. Bekijk de actuele prijs van de <a href="/product/chiq-fbm228ne4de---koel-vriescombinatie---231-lite-8592344703225">CHiQ FBM228NE4DE</a>.</p>

<h2>5. Tomado TRT4702 — de redder van de kleine ruimte</h2>
<p>Tachtig liter m&eacute;t vriesvak, en hij verbruikt maar 110 kWh per jaar — omgerekend zo'n &euro; 33 aan stroom. Perfect voor de studentenkamer, het kantoor of als bijzetkoelkast, en met ruim &euro; 160 ook nog eens de goedkoopste van de lijst. Bekijk de actuele prijs van de <a href="/product/tomado-trt4702w---tafelmodel-koelkast---80-liter---8712876501681">Tomado TRT4702W</a>.</p>

<h2>Zo kies je uit deze vijf</h2>
<p>Voor elk huishouden &eacute;&eacute;n: van de compacte Tomado tot de Amerikaanse CHiQ. Twijfel je nog over inhoud, No Frost of inbouw versus vrijstaand? Lees dan onze <a href="/gidsen/koelkast-kopen-complete-gids">complete koelkast-koopgids</a>. En omdat een koelkast nooit uitstaat: reken v&oacute;&oacute;r de aankoop even het stroomverbruik na met onze <a href="/gidsen/stroomverbruik-koelkast-per-jaar">verbruiksgids</a> — het verschil tussen twee modellen loopt over vijftien jaar flink op.</p>

<p><strong>Let op: prijzen veranderen dagelijks.</strong> In onze <a href="/category/koelkasten">categorie koelkasten</a> zie je van al deze modellen de actuele prijs bij de grote webshops, m&eacute;t prijsverloop per apparaat — zo koop je op het juiste moment.</p>
""",
    },
    {
        'slug': 'beste-vaatwasser-2026',
        'title': 'De 5 beste vaatwassers van 2026',
        'excerpt': 'Van de smalle budgetkoop (45 cm) tot de zelfdoserende topper: de vijf beste vaatwassers van dit moment — inbouw én vrijstaand, gekozen op couverts, geluidsniveau en energielabel. Met video.',
        'category_slug': 'vaatwassers',
        'content': """
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": "De 5 beste vaatwassers van 2026 — koopgids",
    "description": "De vijf beste vaatwassers van dit moment voor elke keuken, inbouw en vrijstaand, gekozen op couverts, geluidsniveau en energielabel. Alle prijzen komen van WitgoedAanbod.nl.",
    "thumbnailUrl": "https://i.ytimg.com/vi/GJi9W8Xpqas/hqdefault.jpg",
    "uploadDate": "2026-07-16",
    "embedUrl": "https://www.youtube-nocookie.com/embed/GJi9W8Xpqas",
    "contentUrl": "https://www.youtube.com/watch?v=GJi9W8Xpqas",
    "publisher": {"@type": "Organization", "name": "WitgoedAanbod.nl"}
}
</script>
<p>Een vaatwasser uitzoeken is lastiger dan het lijkt: inbouw of vrijstaand, tien of vijftien couverts, en stil genoeg voor een open keuken? Wij zochten het uit. Dit zijn de vijf beste vaatwassers van dit moment, van zo'n &euro; 370 tot ruim &euro; 1.200. We letten op het <strong>aantal couverts</strong> (hoeveel vaat er in &eacute;&eacute;n keer in kan), het <strong>geluidsniveau</strong> (in een open keuken wil je onder de 45 dB blijven), het <strong>energielabel</strong> en natuurlijk of hij past: <strong>vrijstaand of inbouw</strong>.</p>

<p>Liever kijken dan lezen? Hier is de video-versie:</p>
<div style="position:relative;width:100%;max-width:800px;margin:0 auto 24px;aspect-ratio:16/9;">
    <iframe
        src="https://www.youtube-nocookie.com/embed/GJi9W8Xpqas"
        title="De 5 beste vaatwassers van 2026 — koopgids"
        style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;border-radius:12px;"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen>
    </iframe>
</div>

<h2>De top 5 met actuele prijzen</h2>
<!--productkaart ean=4002516915669 rank=1 label="De beste: energielabel A, doseert zelf"-->
<!--productkaart ean=4242005417421 rank=2 label="De stilste: 40 dB, volledig integreerbaar"-->
<!--productkaart ean=8003437611865 rank=3 label="De gezinsvriend: 14 couverts, vrijstaand"-->
<!--productkaart ean=8690842609008 rank=4 label="Beste betaalbare inbouw: 15 couverts"-->
<!--productkaart ean=8712876150315 rank=5 label="Kleine keuken: 45 cm breed, 10 couverts"-->

<h2>1. Miele G 7040 AutoDos — de beste</h2>
<p>Energielabel A — de zuinigste van deze lijst — en hij doseert zijn wasmiddel automatisch met een PowerDisk die je maar af en toe hoeft te vervangen. Leuk detail: wij vonden deze machine bij twee webshops met &euro; 16 prijsverschil — vergelijken loont dus zeker in deze prijsklasse. Bekijk de actuele prijzen van de <a href="/product/miele-g-7040-sc-autodos---vrijstaande-vaatwasser-s-4002516915669">Miele G 7040 SC AutoDos</a>.</p>

<h2>2. Bosch SMV6ZCX13 — de stilste</h2>
<p>40 dB: je hoort hem nauwelijks, zelfs tijdens het thuiswerken niet. Een volledig ge&iuml;ntegreerde inbouwmachine met 14 couverts en energielabel B, en dankzij PerfectDry komt je vaat &eacute;cht droog uit de machine. Bekijk de actuele prijs van de <a href="/product/bosch-smv6zcx13e-4242005417421">Bosch SMV6ZCX13E</a>.</p>

<h2>3. Whirlpool WFC 3C34 — de gezinsvriend</h2>
<p>14 couverts en dankzij FlexiSpace flexibel in te delen, dus ook je pannen kunnen er gewoon bij. Een vrijstaande machine die veel aankan, voor een verrassend nette prijs. Bekijk de actuele prijs van de <a href="/product/whirlpool-wfc-3c34-ap-x-vaatwasser---vrijstaand-14-8003437611865">Whirlpool WFC 3C34</a>.</p>

<h2>4. Beko BDIN38560 — de beste betaalbare inbouw</h2>
<p>15 couverts — de grootste capaciteit van deze top 5 — en met 42 dB netjes stil. De CornerIntense-sproeiarm komt ook in de hoeken van de machine, waar gewone sproeiarmen weleens wat laten staan. Bekijk de actuele prijs van de <a href="/product/beko-bdin38560c---inbouwvaatwasser---cornerintense-8690842609008">Beko BDIN38560C</a>.</p>

<h2>5. Inventum VVW4530 — de redder van de kleine keuken</h2>
<p>Slechts 45 cm breed en toch passen er 10 couverts in. Voor een- of tweepersoonshuishoudens (of als tweede vaatwasser) heb je vaak niet meer nodig — en het is ook nog eens de goedkoopste van deze lijst. Bekijk de actuele prijs van de <a href="/product/inventum-vvw4530aw-smalle-vaatwasser---10-couverts-8712876150315">Inventum VVW4530AW</a>.</p>

<h2>Zo kies je uit deze vijf</h2>
<p>Voor elke keuken zit er &eacute;&eacute;n tussen: van de compacte Inventum tot de zelfdoserende Miele. Wil je weten waar alle specificaties voor staan — couverts, programma's, bestekla — lees dan onze <a href="/gidsen/vaatwasser-kopen-complete-gids">complete vaatwasser-koopgids</a>, en waarom het energielabel bij een dagelijks draaiend apparaat extra telt lees je in de <a href="/gidsen/energielabel-witgoed-uitgelegd">energielabel-uitleg</a>.</p>

<p><strong>Let op: prijzen veranderen dagelijks.</strong> In onze <a href="/category/vaatwassers">categorie vaatwassers</a> zie je van al deze machines de actuele prijs bij de grote webshops, m&eacute;t prijsverloop per apparaat — zo koop je op het juiste moment.</p>
""",
    },
    {
        'slug': 'beste-droger-2026',
        'title': 'De 5 beste drogers van 2026',
        'excerpt': 'Van de beste budgetkoop (±€499) tot de zuinigste topper met energielabel B: de vijf beste warmtepompdrogers van dit moment, gekozen op vulgewicht, geluidsniveau en energielabel — met video.',
        'category_slug': 'drogers',
        'content': """
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": "De 5 beste drogers van 2026 — koopgids",
    "description": "De vijf beste warmtepompdrogers van dit moment voor elk budget, gekozen op vulgewicht, geluidsniveau en energielabel. Alle prijzen komen van WitgoedAanbod.nl.",
    "thumbnailUrl": "https://i.ytimg.com/vi/VTuSkXh8FkI/hqdefault.jpg",
    "uploadDate": "2026-07-16",
    "embedUrl": "https://www.youtube-nocookie.com/embed/VTuSkXh8FkI",
    "contentUrl": "https://www.youtube.com/watch?v=VTuSkXh8FkI",
    "publisher": {"@type": "Organization", "name": "WitgoedAanbod.nl"}
}
</script>
<p>Een droger kopen? Dan wil je er &eacute;&eacute;n die zuinig is, want een droger is van nature een stroomvreter. Wij zochten uit welke hun geld echt waard zijn: dit zijn de vijf beste drogers van dit moment, van zo'n &euro; 500 tot ruim &euro; 1.000. E&eacute;n ding vooraf: bijna elke goede droger is tegenwoordig een <strong>warmtepompdroger</strong> — die hergebruikt zijn eigen warmte en verbruikt daardoor veel minder stroom dan een oude condensdroger (waarom precies lees je in onze gids <a href="/gidsen/warmtepompdroger-of-condensdroger">warmtepompdroger of condensdroger</a>). Verder letten we op het <strong>vulgewicht</strong>, het <strong>geluidsniveau</strong> (een droger draait vaak 's avonds) en het <strong>energielabel</strong>.</p>

<p>Liever kijken dan lezen? Hier is de video-versie:</p>
<div style="position:relative;width:100%;max-width:800px;margin:0 auto 24px;aspect-ratio:16/9;">
    <iframe
        src="https://www.youtube-nocookie.com/embed/VTuSkXh8FkI"
        title="De 5 beste drogers van 2026 — koopgids"
        style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;border-radius:12px;"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen>
    </iframe>
</div>

<h2>De top 5 met actuele prijzen</h2>
<!--productkaart ean=4242005522118 rank=1 label="De beste: energielabel B en de stilste (59 dB)"-->
<!--productkaart ean=8806096717677 rank=2 label="De grootste: 10 kg, relatief stil (62 dB)"-->
<!--productkaart ean=8806099109806 rank=3 label="Degelijke middenklasser, 8 kg"-->
<!--productkaart ean=8690842722806 rank=4 label="Beste prijs-kwaliteit, 8 kg"-->
<!--productkaart ean=6901101829627 rank=5 label="Beste koop rond de 500 euro, 8 kg"-->

<h2>1. Bosch WQH246 — de beste: energielabel B en de stilste</h2>
<p>De enige van deze lijst met <strong>energielabel B</strong> — zuiniger vind je ze nauwelijks — en met 59 dB ook nog eens de stilste. Auto Dry zorgt dat hij nooit langer droogt dan nodig, dus je kleding gaat langer mee. Duurder in aanschaf, maar elke droogbeurt goedkoper: wie veel droogt, verdient het verschil terug (reken het na met onze <a href="/gidsen/energielabel-witgoed-uitgelegd">energielabel-uitleg</a>). Bekijk de actuele prijs van de <a href="/product/bosch-wqh246clnl---warmtepomdroger-9-kg-59-db-ener-4242005522118">Bosch WQH246CLNL</a>.</p>

<h2>2. LG RHX5010 — de grootste</h2>
<p>10 kg vulgewicht, de grootste van deze top 5: een tweepersoons dekbedovertrek of de weekwas van een groot gezin gaat er in &eacute;&eacute;n keer in. En met 62 dB is hij ook nog eens relatief stil. Voor wie nooit meer in twee rondes wil drogen. Bekijk de actuele prijs van de <a href="/product/lg-rhx5010thb---warmtepompdroger-10-62-energielabe-8806096717677">LG RHX5010THB</a>.</p>

<h2>3. Samsung DV80DG52 (5000-serie) — de degelijke middenklasser</h2>
<p>8 kg vulgewicht en OptimalDry-sensoren die het droogproces bijsturen zodat je was niet langer draait dan nodig: een degelijke middenklasser van een vertrouwd merk, voor een nette prijs. Bekijk de actuele prijs van de <a href="/product/samsung-dv80dg52b0aeen-8806099109806">Samsung DV80DG52B0 (5000-serie)</a>, of het volledige <a href="/category/drogers?brand=Samsung">Samsung-drogeraanbod</a> voor andere formaten.</p>

<h2>4. Beko RecycledDry — beste prijs-kwaliteit</h2>
<p>De RecycledDry-lijn combineert een scherpe prijs met de EcoGentle-technologie, die je was extra voorzichtig droogt zodat ook fijne kleding veilig de droger in kan. Wij vergelijken de 8 kg-uitvoering: bekijk de actuele prijs van de <a href="/product/beko-bm3t3823wmm-recycleddry---warmtepompdroger-8--8690842722806">Beko BM3T3823WMM RecycledDry</a>, of het volledige <a href="/category/drogers?brand=Beko">Beko-drogeraanbod</a>.</p>

<h2>5. Hisense DH3S802 — de beste koop rond &euro; 500</h2>
<p>8 kg vulgewicht en Auto Dry: sensoren meten hoe vochtig je was is en stoppen precies op tijd — dat spaart stroom &eacute;n je kleding. Ook handig: het Allergy Care-programma voor wie gevoelig is voor huisstofmijt. Een complete droger voor een instapprijs. Bekijk de actuele prijs van de <a href="/product/hisense-dh3s802bw3---warmtepompdroger-8-kg-64-db-e-6901101829627">Hisense DH3S802BW3</a>.</p>

<h2>Zo kies je uit deze vijf</h2>
<p>Voor elk huishouden zit er &eacute;&eacute;n tussen: van de voordelige Hisense tot de zuinige Bosch. Twijfel je nog over het type of wil je weten waar de specificaties voor staan? Lees dan onze <a href="/gidsen/droger-kopen-waar-op-letten">complete droger-koopgids</a> en de vergelijking <a href="/gidsen/warmtepompdroger-of-condensdroger">warmtepompdroger of condensdroger</a>.</p>

<p><strong>Let op: prijzen veranderen dagelijks.</strong> In onze <a href="/category/drogers">categorie drogers</a> zie je van al deze drogers de actuele prijs bij de grote webshops, m&eacute;t prijsverloop per apparaat — zo koop je op het juiste moment.</p>
""",
    },
    {
        'slug': 'beste-wasmachine-2026',
        'title': 'De 5 beste wasmachines van 2026',
        'excerpt': 'Van een degelijke budgetkoop tot de onverwoestbare nummer 1: de vijf beste wasmachines van dit moment, gekozen op vulgewicht, toerental, energielabel en prijs — met video.',
        'category_slug': 'wasmachines',
        'content': """
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": "De 5 beste wasmachines van 2026 — koopgids",
    "description": "De vijf beste wasmachines van dit moment voor elk budget, gekozen op vulgewicht, toerental, energielabel en prijs. Alle prijzen komen van WitgoedAanbod.nl.",
    "thumbnailUrl": "https://i.ytimg.com/vi/3eyfGDGUzVk/hqdefault.jpg",
    "uploadDate": "2026-07-16",
    "embedUrl": "https://www.youtube-nocookie.com/embed/3eyfGDGUzVk",
    "contentUrl": "https://www.youtube.com/watch?v=3eyfGDGUzVk",
    "publisher": {"@type": "Organization", "name": "WitgoedAanbod.nl"}
}
</script>
<p>Een nieuwe wasmachine kopen is niet makkelijk: honderden modellen, prijzen die dagelijks veranderen en elke winkel roept dat hij de goedkoopste is. Daarom hebben we het uitgezocht. Dit zijn de vijf beste wasmachines van dit moment, voor elk budget van zo'n &euro; 400 tot ruim &euro; 1.000. We hebben op vier dingen gelet: het <strong>vulgewicht</strong> (hoeveel was er in &eacute;&eacute;n keer in kan), het <strong>toerental</strong> (hoe droog je was uit de machine komt), het <strong>energielabel</strong> (wat hij je per jaar aan stroom kost) en natuurlijk de <strong>prijs</strong>.</p>

<p>Liever kijken dan lezen? Hier is de video-versie:</p>
<div style="position:relative;width:100%;max-width:800px;margin:0 auto 24px;aspect-ratio:16/9;">
    <iframe
        src="https://www.youtube-nocookie.com/embed/3eyfGDGUzVk"
        title="De 5 beste wasmachines van 2026 — koopgids"
        style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;border-radius:12px;"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen>
    </iframe>
</div>

<h2>De top 5 met actuele prijzen</h2>
<!--productkaart ean=4002516896067 rank=1 label="De beste: wasresultaat en levensduur"-->
<!--productkaart ean=7333394121017 rank=2 label="De slimste: automatische dosering, 10 kg"-->
<!--productkaart ean=4242003979389 rank=3 label="De krachtpatser: 1600 toeren, 9 kg"-->
<!--productkaart ean=4242005445912 rank=4 label="Beste prijs-kwaliteit voor gezinnen, 9 kg"-->
<!--productkaart ean=8690842820250 rank=5 label="Beste koop onder de 400 euro, 7 kg"-->

<h2>1. Miele W1 WEB 368 WCS PowerWash — de beste</h2>
<p>Niet de grootste van de lijst (8 kg), wel de beste. PowerWash mengt water en wasmiddel vooraf en sproeit het diep in de vezels: schoner wasgoed, ook op korte programma's. En Miele bouwt zijn machines om twintig jaar mee te gaan — duurder in aanschaf, maar per jaar gerekend waarschijnlijk de goedkoopste machine die je kunt kopen. Bekijk de actuele prijs van de <a href="/product/miele-web-368-wcs-powerwash-4002516896067">Miele WEB 368 WCS PowerWash</a>.</p>

<h2>2. AEG LR86 PowerCare UniversalDose — de slimste</h2>
<p>Met 10 kg vulgewicht de grootste van deze top 5, en hij doseert zijn wasmiddel automatisch: jij vult het reservoir, de machine bepaalt per wasbeurt precies hoeveel er nodig is. Dat bespaart wasmiddel en is beter voor je kleding. Bekijk de actuele prijs van de <a href="/product/aeg-lr86power-powercare-universaldose-7333394121017">AEG LR86 PowerCare UniversalDose</a>, of lees waarom we deze UniversalDose-techniek eerder al uitlichtten in onze <a href="/gidsen/beste-wasmachines-vergeleken">wasmachine-vergelijking</a>.</p>

<h2>3. Siemens WG46 iQ500 — de krachtpatser</h2>
<p>9 kg vulgewicht en 1600 toeren: dat hoge toerental slingert veel meer water uit je was, waardoor de droger daarna korter hoeft te draaien — dat scheelt tijd &eacute;n stroom. Met 73 dB is hij bij het centrifugeren bovendien netjes stil. Voor grote gezinnen die veel en snel wassen. Bekijk de actuele prijs van de <a href="/product/siemens-wg46g2zwnl---wasmachine-9-kg-1600-rpm-73-d-4242003979389">Siemens WG46G2ZWNL</a>.</p>

<h2>4. Bosch Serie 6 WGG244 — beste prijs-kwaliteit voor gezinnen</h2>
<p>9 kg vulgewicht voor onder de &euro; 600. Stil, zuinig (energielabel A) en dankzij Iron Assist komen overhemden met minder kreukels uit de trommel. Een machine waar je jaren op kunt bouwen. Bekijk de actuele prijs van de <a href="/product/bosch-wgg244zonl-iron-assist-4242005445912">Bosch WGG244 Iron Assist</a>.</p>

<h2>5. Beko B1W764 SteamCure — de beste koop onder &euro; 400</h2>
<p>7 kg vulgewicht, 1400 toeren en energielabel A — dat zie je in deze prijsklasse bijna nooit. Met SteamCure fris je kleding tussendoor op met stoom, zodat je minder vaak hoeft te wassen. Perfect voor een- of tweepersoonshuishoudens die een degelijke, zuinige machine willen. Bekijk de actuele prijs van de <a href="/product/beko-b1w764w-be---steamcure-wasmachine-7-kg-1400-r-8690842820250">Beko B1W764 SteamCure</a> (ook <a href="/product/beko-b1w764bbbe-steamcure-8690842820267">in het zwart</a> leverbaar).</p>

<h2>Zo kies je uit deze vijf</h2>
<p>Voor elk huishouden zit er &eacute;&eacute;n tussen: van de voordelige Beko tot de onverwoestbare Miele. Twijfel je over het juiste vulgewicht? Lees dan onze gids <a href="/gidsen/wasmachine-8-of-9-kg">wasmachine van 8 of 9 kg</a>. Wil je weten wat de specificaties precies betekenen, dan helpt de <a href="/gidsen/wasmachine-kopen-waar-op-letten">complete wasmachine-koopgids</a>, en waarom het energielabel zich terugverdient lees je in onze <a href="/gidsen/energielabel-witgoed-uitgelegd">uitleg over energielabels</a>.</p>

<p><strong>Let op: prijzen veranderen dagelijks.</strong> In onze <a href="/category/wasmachines">categorie wasmachines</a> zie je van al deze machines de actuele prijs bij de grote webshops, m&eacute;t prijsverloop per apparaat — zo koop je op het juiste moment.</p>
""",
    },
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
    """Synchroniseer de gidsen uit NEW_GUIDES met de database.

    Idempotent: ontbrekende slugs worden toegevoegd; bestaat een slug al
    maar wijkt titel, samenvatting of tekst af van deze broncode, dan
    wordt de databaseversie bijgewerkt (de code is voor déze gidsen de
    bron van de waarheid). Geeft het aantal gewijzigde gidsen terug.
    """
    changed = 0
    for data in NEW_GUIDES:
        category = None
        if data['category_slug']:
            category = Category.query.filter_by(slug=data['category_slug']).first()

        guide = Guide.query.filter_by(slug=data['slug']).first()
        if guide is None:
            db.session.add(Guide(
                title=data['title'],
                slug=data['slug'],
                excerpt=data['excerpt'],
                content=data['content'].strip(),
                category_id=category.id if category else None,
                post_type='guide',
            ))
            changed += 1
        elif (guide.content != data['content'].strip()
              or guide.title != data['title']
              or guide.excerpt != data['excerpt']):
            guide.title = data['title']
            guide.excerpt = data['excerpt']
            guide.content = data['content'].strip()
            changed += 1
    if changed:
        db.session.commit()
    return changed
