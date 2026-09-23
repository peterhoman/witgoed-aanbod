# Start hier — overdracht aan een nieuwe sessie

Bijgewerkt **23 september 2026, 12:15** (het blok "Dagcontrole 23 september"
hieronder is het nieuwste, dan "Dagcontrole 22 september (tweede sessie)" met
alles wat die dag 's middags en 's avonds is gebouwd, dan "Overdracht 22 september,
slot", dan "Dagcontrole 22 september", "21 september (middag)", "Dagcontrole 21 september", "Dagcontrole 20 september", "Dagcontrole 19 september", "18 september (middag) — gezondheidscontrole" en
"Dagcontrole 18 september", daaronder "Dagcontrole 17 september (middag)"
hieronder is het nieuwste, daaronder "Overdracht 17 september, slot"; oudere blokken en hoofdstukken blijven gelden waar de update
niets anders zegt). Lees dit eerst; het projectgeheugen van de chat
(MEMORY.md in de Claude-projectmap) draagt dezelfde feiten compact en is
leidend voor werkafspraken.

---

## Dagcontrole 23 september (woensdag) — gezond; IndexNow-403 gerepareerd; EPREL-inhaalslag klaar

- **`/api/gezondheid`: GEZOND**, 11 van 11 routines (IndexNow telt mee sinds
  gisteravond). Leverbaar 2.913. Prijssprongen 2, 0 teruggesprongen (logboek:
  Bosch 4242003917879 699→1049, feed zegt 1049, dus echt). Tekstwachtrij 0.
  `niet_ververst_3d`: Bol 350 en EP 631 = bekend, rest 0. Sjabloonsporen 0.
  Railway 0 5xx; p99 46 ms 's nachts, 815 ms vanochtend (uitrollen), geen
  uitschieter. Witgoedhuis-feed nog 6 september. Mail: geen winkel, geen
  SMEG/De'Longhi/AEG; wel bevestiging van Awin dat Peter een case (03172772,
  "Publisher ...") heeft geopend, vermoedelijk de Spotlight-aanvraag; en een
  Google-melding dat Peter met zijn Google-account bij bing.com inlogde
  (Bing Webmaster Tools; die bleek al sinds juli ingericht, 3.300 URL's).
- **EPREL-inhaalslag drogers is klaar:** `tumbledriers` 71 → **2**,
  `tumbledryers20232534` 0 → **141** (meer dan de 71 van eerst, omdat ook
  eerder niet-gevonden drogers nu in het nieuwe register gevonden worden).
  De 2 overgebleven rijen staan waarschijnlijk alleen in het oude register;
  die tonen geen klasse (VEROUDERDE_LABELGROEPEN) en dat is goed zo.
- **IndexNow: eerste ronde (07:30 UTC) kreeg 403 voor alle 849 adressen**,
  gemeld door de specialist-chat. Gemeten: een losse melding met één adres
  en keyLocation gaf 's avonds al 200, dus de sleutel werkte; Bing had het
  bestand om 07:30 vermoedelijk nog niet opgehaald, en de naam
  `/indexnow-<sleutel>.txt` is niet de standaardplek. **Gerepareerd dezelfde
  ochtend (PR #197):** sleutelbestand ook op `/<sleutel>.txt` (root), de
  melding wijst daarheen, oude naam blijft werken, andere namen 404. Proef
  vanuit productie zonder keyLocation met 3 adressen: **200**. Volgende
  ronde 24 sept 07:30 UTC; nakijken op /api/sync-status → indexnow (na een
  uitrol staat daar weer `wanneer: None`, dat is geheugen, geen fout).
- **Bezoekersbron, eerste dag:** 22 sept (vanaf ~22:00) direct 44,
  extern-onbekend 23, zonder-secfetch 26; 23 sept tot 12:00: direct 95,
  extern-onbekend 35, zonder-secfetch 30, google 3, chatgpt 2, bing 1,
  duckduckgo 1; nog geen verwijzende sites. **Let op bij het lezen:**
  'direct' loopt gelijk op met `product-los-adres` (93 vandaag): dat zijn
  grotendeels de programma's uit datacenters die productadressen los
  opvragen ([[scraper-uit-datacenters]]), geen mensen met een bladwijzer.
  Google 3 tegenover 3-8 Search Console-klikken per dag: mogelijk komen
  Google-app/Discover-bezoekers zonder Referer binnen (extern-onbekend).
  Over een week naast Search Console leggen; nu geen actie.
- Alle takken van 22 sept zijn gemerged (#193-#197); lokaal en op GitHub
  staat alleen main.

---

## Dagcontrole 22 september (tweede sessie, 11:10-12:00) — alles gezond; "kan niet worden bereikt" nu ~20 per dag

Nieuwe sessie gestart om 11:10 NL, twee minuten nadat Peter PR #186 (de
overdracht) doorvoerde; die merge gaf een nieuwe uitrol om 11:08. Lokaal staat
weer alleen main. **Alle metingen gedaan, niets stuk.**

- **`/api/gezondheid`: GEZOND**, 10 van 10, prijsbewegingen Bol/Coolblue/
  MediaMarkt alle drie ~3 uur oud. Leverbaar 2.903. Prijssprongen 6, 0
  teruggesprongen (het logboek meldt één sprong >50%, EAN 5038061142860
  150→74, feed zegt 74,32: echte daling, geen fout). Tekstwachtrij 0, sleutel
  aanwezig. Winkelbijdrage `niet_ververst_3d`: Bol 355 en EP 632 zijn de
  bekende oude rijen (EP-feed is sinds augustus een selectie, 354 van 996 in
  de nachtsync), rest 0. Sjabloonsporen op de LG RT90X8-pagina: 0.
- **Railway:** 0 serverfouten in 24 uur, p99 152 ms (nacht) en 58 ms (ochtend).
  **De uitschieter van 7,6 s van de twee vorige dagen is weg**; niets uit te
  zoeken. Geen WORKER TIMEOUT of Traceback in de logs van de drie uitrollen
  van vandaag. CPU 0,1%, geheugen max 575 MB van 8 GB.
  Let op bij `railway metrics`: `--since 1d` weigert ("stepSeconds must be at
  least 87"), gebruik twee vensters `--since 24h --until 12h` en `--since 12h`.
  `railway logs --http` geeft alleen de lopende uitrol; na een merge is de
  nacht dus niet meer terug te lezen. Oudere uitrollen wel: `railway logs -d
  <uitrol-id> -n 5000` (20000 weigert).
- **EPREL-inhaalslag is begonnen en werkt.** Om 11:10 stond `/api/eprel` nog
  op `tumbledriers` 71 (laatste ronde 08:13 NL, vóór de uitrol van #183) en
  verwees de LG RT90X8-pagina nog naar het oude register. De ronde van
  11:15 NL (de planner draait elke **3** uur, niet 6; volgende 14:13, 17:13,
  20:13 …) ververste 100 rijen: nu `tumbledriers` 27, **`tumbledryers20232534`
  72**. De LG RT90X8-pagina toont weer een regel "Energieklasse **B**" en
  verwijst naar `tumbledryers20232534/2386548` (nieuw register, nieuwe
  schaal). De resterende 466 rijen (566 - 100) gaan in ~5 rondes van 100,
  dus klaar rond woensdagochtend 23 sept ~02:15. Nakijken morgen: staat
  `tumbledriers` op 0 en zijn er in de Merchant-feed drogers mét klasse?
- **Merchant Center (gelezen via Peters Chrome, geen knop gebruikt):**
  "productpagina niet beschikbaar" **15 → 9 → 1** (alleen nog de Sharp
  R-982 combi-magnetron; de websitecontrole van vanochtend heeft gewerkt).
  Niet goedgekeurd 44 waarvan 42 verborgen = 2 van ons. Wordt beoordeeld 29
  (27 verborgen). Goedgekeurd 2,93K (+179 in een week). Klikken 142 in 28
  dagen. De vier "oplossingen": productpagina niet beschikbaar 1, prijs
  ontbreekt 42 (verborgen, Google's eigen vondsten), availability 9, foto 1.
  De tabel op de diagnostiekpagina is virtueel: tellen via JavaScript op
  `innerText` ziet maar ~7 rijen; lees de kaartjes "Alle oplossingen tonen".
- **Search Console:** geïndexeerd 2,68K; niet geïndexeerd 1,56K. **Noindex
  239 → 282** (Google verwerkt de sitemap-datumfix van 18 sept in weken; pas
  rond 5-9 okt beoordelen, zoals afgesproken). 5xx 9 (oud), 404 71, gevonden-
  niet-geïndexeerd 1.088 (was 1.243).
- **"De pagina kan niet worden bereikt" gemeten uit alle 362 voorbeelden**
  (90 dagen, JavaScript op de tabel): tot 8 sept 0-5 per dag, daarna elke
  dag 10-27: 12 sept 27, 13: 25, 14: 19, 15: 21, 16: 5, 17: 19, 18: 19,
  19: 23, 20: 24 (21 sept nog onvolledig). Totaal 407 in 90 dagen (14 sept
  stond de teller op 208). Verdeling over de uren van de dag is vlak (4-23
  per uur over 90 dagen, geen piek rond de nachtsyncs), 337 van 362 zijn
  productpagina's. **Het hangt dus niet aan de feedroutines.** Tegelijk
  UptimeRobot 100% (twee meters, 0 incidenten), Railway 0 5xx, en een
  eigen proef van 300 productpagina's met 6 gelijktijdige verbindingen
  (24 verzoeken/s) gaf 300× 200, mediaan 0,24 s, max 0,57 s. DNS: alleen
  IPv4 via CNAME naar Railway, geen IPv6-record (dus geen IPv6-verklaring).
  Merchant Center heeft er intussen geen last meer van (1 product). Geen
  nieuwe actie voorgesteld; dit is dezelfde open vraag als 14 sept, alleen
  met een hogere teller. Het crawlvolume steeg in september ook (pieken
  tot 3K/dag in de grafiek), de verhouding is niet uit de tabel te halen.
- **Witgoedhuis-feed (Daisycon):** `Last-Modified` nog steeds 6 september,
  3.776 records. Niet bouwen.
- **Mail (pfmhoman):** niets van de winkels, Daisycon/Witgoedhuis, De'Longhi,
  AEG, TradeTracker of Awin. Alleen een UptimeRobot-reclame. Peter moet
  peter@avantius.nl nog nakijken.
- **Fase 0 van het linkplan gebouwd (avond, tak feat/pers-en-auteur), op
  verzoek van Peters aparte SEO-chat "Google specialist" met Peters groen
  licht vooraf.** Die chat mag alleen vragen stellen en voorstellen
  doorgeven; bouwen gebeurt hier (afspraak Peter 22 sept, staat in memory).
  Analyse van die chat: techniek en inhoud op orde, het probleem is
  autoriteit (551 van 552 externe links komen van avantius.nl). Gebouwd:
  1. **/pers** (templates/legal/pers.html, route in legal.py, in
     sitemap-overig): het prijsonderzoek in vijf zinnen met de cijfers
     **vastgezet op 22 september 2026** (1.136 apparaten, gemiddeld € 53 =
     10,8%, 397 ≥ € 50, 212 ≥ € 100, 319 gelijk; per categorie wasmachines
     € 81 t/m afzuigkappen € 26; grootste verschil € 530 Siemens
     stoomoven), een staafdiagram om te downloaden (PNG 1600×900 en SVG in
     static/img/pers/, gemaakt met Pillow, script in de scratchpad van deze
     sessie), cijfertabel, "hoe wij meten", "Over WitgoedAanbod.nl", en
     contact **Peter Homan, oprichter, info@witgoedaanbod.nl** (Peter koos
     dit adres op 22 sept boven zijn Gmail-adres; geen telefoonnummer). CC BY 4.0,
     zelfde licentie als de Dataset op de onderzoekspagina. Bewust niet
     live: een persbericht dat hierheen verwijst moet na een week nog
     kloppen; de levende versie is /onderzoek/prijsverschillen-witgoed.
  2. **/over-ons**: nieuw blok "Wie zit erachter?" (anker #peter) met
     Peter Homan, oprichter, en waarom de vergelijker; `founder` (Person)
     in het Organization-schema. **Feit gecorrigeerd dezelfde avond (tak
     fix/avantius-sinds-2007, via de specialist-chat van Peter): Avantius
     bestaat sinds 2007 en verkoopt zelf GEEN witgoed.** De oude claim
     "ruim 20 jaar in huishoudelijke apparaten / witgoed is ons dagelijks
     werk" stond al sinds de eerste over-ons-tekst en was overgenomen op
     /pers en boven elke gids. Overal nu dezelfde formulering: "familiebedrijf
     uit Sassenheim dat sinds 2007 bestaat; Avantius verkoopt zelf geen
     witgoed, daardoor kan de vergelijker onafhankelijk zijn." Nooit meer
     "20 jaar" schrijven. **Geen
     foto**: Peter heeft er geen aangeleverd; komt erbij als hij dat wil.
  3. **Gidsen en blog** (guide_detail.html): zichtbaar "Door Peter Homan,
     oprichter ..." met link naar /over-ons#peter, en in het Article-schema
     author = Person (was Organization) met worksFor. `dateModified` was al
     eerlijk: guides_content.py schrijft een gids alleen weg als titel,
     samenvatting of tekst echt verschilt, dus updated_at schuift niet op
     bij een uitrol; het label heet nu "laatst bijgewerkt".
  Lokaal gerenderd: /pers 200 (index/follow, PNG en SVG 200, JSON-LD
  geldig), /over-ons met founder, gids met author Person en dateModified
  2026-07-25 = datePublished, sitemap-overig bevat /pers. **Na de merge
  nakijken op productie:** /pers, /over-ons#peter, één gids, en
  /sitemap-overig.xml. Daarna de specialist-chat berichten dat het live
  staat (Peter mailt de redacties zelf, max 5 per dag; zie linkplan 17
  sept).
- **IndexNow gebouwd (tak feat/indexnow), na Peters ja via de specialist-chat.**
  Bing (en Yandex/Naver/Seznam; Google doet niet mee) dagelijks de adressen
  melden die veranderd zijn. `indexnow.py`: sleutel in config
  (`INDEXNOW_KEY`, vaste waarde in de code, met de omgevingsvariabele te
  vervangen; geen geheim), sleutelbestand op `/indexnow-<sleutel>.txt`
  (route in routes/seo.py, andere naam = 404), plannertaak "IndexNow:
  gewijzigde adressen melden" elke dag 07:30 UTC als cron (bewust geen
  interval: die vuurt na elke uitrol opnieuw), die alle sitemap-adressen
  met een datum van gisteren of vandaag verzamelt (zelfde datumlogica als
  de sitemap; soort 'overig' niet, die staat altijd op vandaag) en ze in
  stukken van hooguit 10.000 als JSON naar api.indexnow.org stuurt.
  Uitkomst op /api/sync-status onder `indexnow` (wanneer, aantal,
  statuscode per bericht: 200/202 = ontvangen, 403 = sleutelbestand niet
  bereikbaar, 422 = adres hoort niet bij de host, 429 = te veel). Staat in
  VERWACHTE_ROUTINES van gezondheid.py (nu 11 routines). Tests:
  `python test_indexnow.py` (9 controles) en test_gezondheid.py groen.
  Lokale proef met een neppe verzender: 13 adressen, 1 bericht, 202.
  **Na de merge:** in `railway logs` de regel "IndexNow: eerstvolgende run
  ... 07:30" zien, op productie `/indexnow-<sleutel>.txt` opvragen (moet de
  sleutel teruggeven), en de ochtend erna op /api/sync-status kijken of de
  eerste ronde status 200/202 kreeg. Peter meldt de site zelf aan bij Bing
  Webmaster Tools (import uit Search Console); de sleutel hoeft daar niet
  ingevoerd te worden.
- **Twee kleine regels uit het linkplan (tak fix/robots-meta-og-pers):**
  `max-image-preview:large` achter de robots-meta in base.html (elke
  pagina; voorwaarde voor grote voorvertoningen en Discover),
  `Claude-SearchBot` expliciet in de crawlerlijst van robots.txt
  (routes/seo.py, nu 11 groepen), en de persgrafiek (1600×900) als
  paginaspecifieke og:image van /pers (nieuwe blokken og_image_width/height
  in base.html). Lokaal gerenderd op /, /pers en /search.
- **Bezoekersbron in de eigen teller gebouwd (avond, tak feat/bezoekersbron),
  na Peters ja via de specialist-chat; zijn merge is de bevestiging.** Vraag
  van het linkplan: welke zoekmachine, AI-assistent of verwijzende site
  levert bezoekers op? Antwoord van deze sessie op de vragen van die chat
  (netwerken per winkel, meting, IndexNow, robots, schema) staat in het
  bericht van 22 sept avond; gekozen: **geen GA4, geen Umami**, wel de eigen
  teller uitbreiden. Gebouwd:
  - Nieuwe tabel `bezoekersbronnen` (models.Bezoekersbron: datum, bron,
    domein, aantal; create_all maakt hem aan bij de eerste uitrol).
  - `pageviews.bezoekersbron(headers)`: uit Referer en Sec-Fetch-Site, alleen
    bij binnenkomst van buiten. Bronnen: google (alle landen + Android-app),
    gemini, bing, copilot, duckduckgo, yahoo, ecosia, chatgpt (chatgpt.com/
    openai.com), perplexity, claude, ai-overig, zoekmachine-overig,
    verwijzing (met domein zonder www.), app, direct (Sec-Fetch-Site none),
    extern-onbekend (cross-site zonder Referer), zonder-secfetch (geen
    Sec-Fetch-koppen én geen Referer = vrijwel zeker een programma).
    Navigatie binnen de site (same-origin of eigen domein) telt niet.
    Bing Chat op bing.com/chat is niet van Bing zoeken te onderscheiden
    (browsers sturen alleen de oorsprong mee), dus dat valt onder bing.
  - Zelfde buffer- en drempelmechanisme als de paginaweergaven (25), zelfde
    botfilter op user-agent; geen IP, cookie, sessie of user-agent bewaard.
  - Uitlezen: `/api/sync-status` → `bezoekersbronnen` = per_dag (nieuwste
    eerst, totaal + per bron) en verwijzende_sites (top 40 domeinen over 14
    dagen). `python test_bezoekersbron.py`: 27 gevallen. Lokale proef met 32
    nagebootste bezoeken: google 8, verwijzing 4 (tweakers.net), chatgpt 4,
    direct 4, zonder-secfetch 4; same-origin en python-requests niet geteld.
  **Na de merge:** in `railway logs` kijken of er geen fout op de nieuwe
  tabel staat, en de volgende dag `bezoekersbronnen` op /api/sync-status
  lezen. Verwachting: google veruit het grootst; de eerste 'verwijzing'-
  domeinen laten zien welke linkplaatsingen werken.
- **SMEG NL via Awin aangevraagd (14:00, Peter klikte zelf op Join).** Peter
  vroeg of het programma iets voor de site is. Gelezen in zijn Awin-account
  (programma 104589): 6% commissie, feed 731 producten (dagelijks ververst),
  cookie 30 dagen, conversie 1,5%, EPC € 0,23, goedkeuring 100%, betaaltermijn
  gemiddeld 77 dagen en **"Exposure Level 4"** (SMEG heeft kredietlimiet én
  betaaltermijn bij Awin overschreden: commissie wordt pas uitbetaald nadat
  SMEG aan Awin betaalt). Wij hebben 37 Smeg-apparaten (15 koelkasten, 13
  koffiemachines, verder ovens/fornuizen/magnetrons), meestal bij 2-3 winkels;
  de retro koel-vriescombinaties kosten € 1.849 (6% = ruim € 110 per verkoop).
  Een merkwinkel verkoopt tegen adviesprijs en wint dus zelden de vergelijking;
  de waarde zit in een extra prijs per apparaat en in Smeg-apparaten die geen
  andere winkel bij ons heeft. **Na goedkeuring eerst de feed meten** (EAN-
  overlap, aantal grote apparaten, prijsniveau) en pas bouwen als het genoeg
  vergelijkingen oplevert; voorbeeldcode is de Awin-feed van Coolblue.
  Meegestuurd bericht: prijsvergelijker, 2.900 apparaten, 7 winkels, 37 Smeg-
  apparaten, feed → volledig assortiment met link naar smeg.com. Awin-knoppen
  reageren niet op klikken via een element-ref; wel op klikken op coördinaten,
  en de tabbladen hebben eigen adressen (`.../merchant-profile/<id>/performance`,
  `/commission-groups`, commissie via `/commission-manager/.../timeline?advertiserIds=<id>`).
- Proefscript bewaard in de scratchpad van deze sessie
  (`bereikbaarheidsproef.py`: sitemap → N productpagina's → statussen en
  tijden); bij herhaling opnieuw aanmaken, het staat niet in de repo.
- **Peters vraag (12:30): hebben we een meta-omschrijving en een H1?** Ja,
  op alle vijf gemeten paginasoorten (voorpagina, product, categorie,
  /aanbiedingen, kenmerkpagina): titel, meta-omschrijving, precies één H1,
  canonical, 9 og-tags, robots index/follow. Twee bevindingen:
  1. **Fout, dezelfde sessie gerepareerd (tak fix/meta-omschrijving-
     woordgrens):** 11 van 60 categorie-, merk- en filterpagina's hadden een
     meta-omschrijving die midden in een woord eindigde ("... MediaMarkt,
     Coolblu", "... Voordeligwitgo"), door een kale `[:160]` op acht plekken
     in routes/main.py. Nu `_meta_kort()`: afkappen op een woordgrens, geen
     los "en"/"bij" als laatste woord, punt erachter. `python
     test_meta_kort.py`: 4 gevallen. Lokaal gerenderd: /category/wasmachines
     eindigt nu op "Bol.com, MediaMarkt, Coolblue." (155 tekens).
  2. **Koppen en intro's gebouwd na Peters ja ("stap 1 en 2 vandaag"), tak
     feat/koppen-h1-intro.** Peter legde een SEO-checklist voor (één H1,
     zoekwoord vooraan, uniek, geschreven voor de gebruiker, intro-alinea
     met het zoekwoord, H1→H2→H3 zonder sprongen, titel en H1 op elkaar
     afgestemd). Gemeten: één H1 en geen kopsprongen klopte al overal;
     wat niet klopte is nu gerepareerd:
     - **Productpagina's, H1 was de kale feedtitel**: op 150 live pagina's
       had 25% verkeerde hoofdletters uit de MediaMarkt-feed ("LG Rt90x8 -
       Warmtepompdroger 9kg 62 Db"). Nieuw filter `nette_titel`
       (titel_netjes.py, geregistreerd in app.py): typenummers in
       hoofdletters, eenheden vast (kg, dB, rpm, cm, RVS; "9kg" → "9 kg"),
       en ALLEEN bij feeds die elk woord met een hoofdletter schrijven
       (geen enkel woord in kleine letters ná het merk, minstens drie
       Netjes-woorden) gaan gewone woorden uit een vaste lijst naar kleine
       letters, behalve aan het begin en direct na " - ". Zonder die
       drempel raakte het filter goede Coolblue/Bol-titels ("Philips
       airfryer met Stoomfunctie"); met drempel: 300 live titels, 135
       gewijzigd, allemaal nagekeken. Toegepast op de H1, het kruimelpad,
       de alternatieven, alle productkaartjes (h3 in _macros.html), de
       dalingenlijst, vergelijken en de prijsverschillenpagina. De titel in
       de database verandert niet. `python test_nette_titel.py`: 21 gevallen.
     - **Productpagina's, intro-zin onder de H1** (`product_specs.intro_zin`,
       css .product-intro): "De LG RT90X8 is een droger van LG. We
       vergelijken de prijs bij 2 winkels en volgen het prijsverloop dag na
       dag." Alleen als merk én typenummer bekend zijn, anders geen zin.
     - **Categoriepagina's, H1 en intro**: H1 was "Wasmachines", nu
       "Wasmachines vergelijken: 216 modellen vanaf € 259" (in lijn met de
       `<title>`); de vaste zin "Vergelijk en vind de beste ..." (stond op
       alle 13 categorieën) is vervangen door een zin uit live data:
       "We vergelijken 216 wasmachines van o.a. Bosch, Samsung en AEG bij 7
       winkels. Per model zie je de laagste prijs (vanaf € 259) en het
       prijsverloop; 41 apparaten werden deze week echt goedkoper." Bron:
       `_category_kerncijfers` (aantal, vanaf, drie meest voorkomende
       merken; zit in de facetcache, die nu vier waarden teruggeeft) en
       `_category_intro` in routes/main.py. `category.ai_intro` gaat nog
       steeds voor als die ooit gevuld wordt. Facetpagina's ongewijzigd.
     - **"Filters" is geen h2 meer** (categorie én zoekpagina; nu
       `<p class="filters-titel">`, zelfde opmaak). Daardoor was er geen h2
       meer vóór de kaartjes en sprong de pagina van h1 naar h3 (precies
       wat designrapport punt 20 eerder oploste door er een h2 van te
       maken). Daarom is de resultatenteller nu de h2: "216 wasmachines"
       (was een span "216 resultaten"; bij 1 treffer "1 model"), en op de
       zoekpagina "6 resultaten gevonden". Opmaak ongewijzigd (css
       .results-count en .search-resultaten).
     Lokaal gerenderd (app in het geheugen, demodatabase): voorpagina,
     categorie, categorie met merkfilter, zoeken, aanbiedingen, product:
     overal precies één h1, geen kopsprongen, 0 serverfouten.
     **Gemerged als PR #189, uitrol 12:17, op productie gecontroleerd:**
     /category/wasmachines (H1 "Wasmachines vergelijken: 216 modellen vanaf
     € 259", intro met AEG/Samsung/Bosch en 31 dalingen, h2 "216
     wasmachines"), de LG RT90X8-pagina (H1 "LG RT90X8 - Warmtepompdroger
     9 kg 62 dB energielabel B" plus intro-zin), voorpagina-kaartjes ("OK.
     Owm 8126 - Wasmachine voorlader 8 kg 1400 rpm 76 dB"), merkpagina en
     kenmerkpagina: overal één h1, geen kopsprongen, 0 sjabloonsporen,
     GEZOND, Railway 0 5xx.
     Eerlijk erbij: H1 en meta-omschrijving zijn voor de ranking zwakke
     signalen; de meta-omschrijving telt niet mee voor de positie maar wel
     voor de doorklik, en dat is precies onze hefboom. De meta-reparatie
     (punt 1) is gemerged als PR #188.

---

## Overdracht 22 september, slot (middag) — laatste stand vóór de nieuwe sessie

**Het gesprek van 17-22 september zit op 77% en is afgesloten. Dit blok +
de dagblokken van 18-22 september hieronder zijn samen de complete stand.
MEMORY.md in de Claude-projectmap draagt dezelfde feiten compact en is
leidend voor werkafspraken; lees daar vooral "Fouten direct oplossen".**

### Vaste regels die deze week zijn bijgekomen
- **Fouten direct oplossen** (Peter, 21 sept): een gevonden fout dezelfde
  sessie meten, bouwen, testen en klaarzetten. Nooit "morgen" of "na de
  vakantie". Nieuwe functies en ontwerpkeuzes wél eerst voorleggen.
- **Peter belt niet** (19 sept): contact met winkels en redacties alleen per
  e-mail; na ~2 weken stilte één herinnering als .txt op het bureaublad.
- **Knoppen in Peters accounts** (Merchant Center websitecontrole, Search
  Console indexering, Awin/Daisycon) vragen per sessie een ja in de chat; de
  betrouwbare klikroutes staan in de dagblokken van 19-21 sept.
- **Vakantie Peter: vrijdag 25 sept t/m vrijdag 2 okt.** In die week geen
  dagcontrole; UptimeRobot mailt bij storing (twee metingen: site plat / feed
  of routine stil). **Geen vaste grens "na woensdag niets meer live"** (Peter,
  22 sept): per dag beoordelen of iets nog verantwoord live kan. Maatstaf: kan
  het een nacht draaien terwijl er nog iemand kijkt? Fouten altijd direct
  oplossen, ook donderdag.

### Wat er live staat sinds 18 sept (alles gecontroleerd op productie)
sitemap-datum bij weer leverbaar (PR #170), `/api/gezondheid` + UptimeRobot
(#172, #180 bevroren-feed-controle), energielabels drogers (#182) en de
volledige EPREL-reparatie (#183: hele klasse in de feed, botsende labels,
nieuw drogerregister `tumbledryers20232534`, exacte treffer, koppeling_klopt,
inhaalslag 566 rijen). Rankingmeting week 39 (#184), oude takken opgeruimd
(#185 en de tak van 22 sept).

### Wat de nieuwe sessie doet, in volgorde
1. **Dagcontrole** (lijst "Elke dag: de storingscontrole"), plus:
   - `/api/eprel` → per productgroep moet `tumbledryers20232534` verschijnen
     en `tumbledriers` (was 71) slinken; de inhaalslag van 566 rijen loopt in
     rondes van 100 (~6 uur per ronde) en is ~woensdagochtend klaar. Een
     drogerpagina (bv. /product/lg-rt90x8-...-8806096198186) hoort weer een
     energieklasse te tonen, nu B of C. Blijft `tumbledriers` op 71 staan: dan
     draait de inhaalslag niet; kijk in `railway logs` naar "eprel".
   - Railway p99: twee dagen op rij één uitschieter van 7,6 s. Vandaag weer?
     Dan met `railway logs --http` het trage adres opzoeken (fout = oplossen).
   - Merchant Center-knop (9 afkeuringen op 22 sept; ja vragen).
2. Gmail (pfmhoman) én Peter vragen naar peter@avantius.nl: winkels (17 sept),
   Witgoedhuis-ticket (21 sept), De'Longhi en AEG (Awin, 19 sept), **SMEG NL
   (Awin, 22 sept)**.
3. Witgoedhuis-feed: `curl -sI` op de Daisycon-feed-URL (blok 21 sept) →
   beweegt `Last-Modified` (stond op 6 sept)? Zo ja: bouwen na de vakantie.
4. Vóór de vakantie per dag beoordelen wat nog live kan (geen vaste
   woensdaggrens meer, zie hierboven).
5. Optioneel, na Peters ja: de twaalf al-doorgevoerde takken op GitHub
   verwijderen (lijst via `git branch -r`; alle twaalf zitten in main).
6. Na de vakantie: rankingmeting di 6 okt; SC noindex (239) rond 5-9 okt;
   kenmerkpagina's beoordelen rond 11 okt; UptimeRobot-uitkomst rond 1 okt;
   herinnering aan de winkels week van 5 okt; De'Longhi-spelling ("delonghi"
   33 / "de'longhi" 27) nakijken; /aanbiedingen-categorie die rond de
   ondergrens van 5 wisselt.

### Valkuilen van deze week (allemaal zelf gemaakt)
- Beweer niets over wat de code doet zonder het in de code te lezen (de
  klep-bewering van 19 sept was fout, gecorrigeerd 21 sept).
- Steekproeven tegen een winkelsite: los .py-script met urllib en pauze,
  nooit shellvariabelen in `python -c` (brak op een \r).
- Windows-console: `PYTHONIOENCODING=utf-8` vóór python-aanroepen die
  é/→ printen, anders een codec-fout.
- Merchant Center: knoppen via `javascript_tool` `.click()` op het `article`
  met de probleemtekst; `find` alleen voor de bevestigknop in het venster.
- Search Console URL-inspectie: veld pakt tekst pas na klik op coördinaat
  (600, 27); na meerdere inspecties staan er meerdere gelijknamige knoppen,
  neem de laatste.
- Google's AI-lijst "top 10 vergelijkers" is een samenvatting van
  vermeldingen elders, geen meting (blok in memory: knibble-slimster).

---

## Dagcontrole 22 september (dinsdag) — rankingmeting week 39; labelreparaties live

- **`/api/gezondheid`: GEZOND**, 10 van 10, drie prijsbewegingsregels vers
  (< 1 uur). Leverbaar 2.903, feed 2.901, /aanbiedingen 11 categorieën,
  prijssprongen 6 (0 teruggesprongen), tekstwachtrij 0, geen sjabloonsporen,
  Railway 0 serverfouten, geen Traceback. **p99 voor de tweede dag een
  uitschieter van 7,6 s** (gem. 0,5 s); morgen nog zo, dan uitzoeken welk
  adres. Doorkliks 21 sept: 13 browser (Coolblue 8, MediaMarkt 5).
- **PR #183 (energielabels + EPREL-koppeling) is live** (uitrol 08:39,
  GEZOND daarna). De inhaalslag begint bij de eerste EPREL-ronde erna (~14:15
  NL); daarvoor stonden de 71 drogers nog in `tumbledriers`. **Morgen
  nakijken:** per productgroep in `/api/eprel` moet `tumbledryers20232534`
  verschijnen en `tumbledriers` slinken; een drogerpagina (bv. LG RT90X8)
  hoort weer een klasse te tonen, nu B/C.
- **Merchant Center (schermafdruk Peter + knop):** "productpagina niet
  beschikbaar" 15 → **9**; websitecontrole opnieuw aangevraagd na Peters ja
  (bevestigd "Dit kan tot 12 uur duren"). Niet goedgekeurd 45 waarvan 35
  verborgen = 10 van ons (week ervoor 116). 141 Shopping-klikken in 28
  dagen. Koelvriesmelding 204.
- **Search Console (schermafdruk):** 7 dagen 26 klikken / 2.010 vertoningen /
  CTR 1,3% / positie 5,6; 3 maanden 215 klikken.
- **Rankingmeting week 39 gedaan** (docs/RANKING-METING.md, nu ook echt op
  main: het document stond alleen op de nooit doorgevoerde tak
  docs/rankingmeting-wekelijks). Stand 1 van 10, onveranderd; "witgoed
  prijsvergelijkers" niet in de top 20. De gemailde winkels staan zelf op
  pagina 1-2. Volgende meting: dinsdag 6 oktober (29 sept valt in de
  vakantie).
- **Takken opgeruimd (22 sept, na Peters ja):** 154 lokale takken die volledig
  in main zaten verwijderd; de zes nooit-doorgevoerde één voor één bekeken en
  alle zes overbodig: docs/rankingmeting-wekelijks (inhoud overgenomen, zie
  hierboven), fix/tekstroutine-onthoudt-wanneer en docs/dagelijks-controleren
  (geen verschil met main), fix/fotos-eigen-domein (plan B van 13 aug: foto's
  via ons eigen domein; niet nodig, de feed gebruikt wsrv en Merchant Center
  keurt 2,91K goed), fix/robots-uitsluitingen (oude versie van setprijs.py;
  main heeft de nieuwere met de setvergelijking), docs/start-hier-12-september
  (blok staat al op main). Lokaal staat nu alleen main. Op GitHub staan nog
  twaalf takken van al doorgevoerde PR's (GitHub bewaart die na een merge);
  die zitten volledig in main en doen niets.
  **Wie in oude gesprekken een taknaam tegenkomt: die bestaat niet meer, de
  inhoud zit in main of was achterhaald.**
- Mail: niets van winkels, Daisycon/Witgoedhuis, De'Longhi, AEG. CookieYes
  (reclame voor een betaalde cookiebanner met Claude-koppeling): niet nodig,
  de site heeft een eigen cookievenster en zet geen volgcookies.

---

## 21 september (middag) — bevroren-feed-controle live; drogers tonen een verouderd EPREL-label

- **Bevroren-feed-controle live en gecontroleerd (PR #180, uitrol 14:34):**
  `/api/gezondheid` op productie GEZOND, 10 van 10, met de drie nieuwe regels
  (Bol 0,8 uur, Coolblue 6,3, MediaMarkt 6,4 sinds de laatste prijswijziging).
- **Prijsalert werkt** (schermafdruk Peter: mail "Prijsdaling: Jet Set
  wasdroger", 295,52 → 288,13). Drempel is 2% (`DALING_DREMPEL` in
  price_alerts.py); deze daling was 2,5%. Zo bedoeld.
- **Gevonden via die productpagina: energielabels bij drogers kloppen niet.**
  Sinds 1 juli 2025 geldt voor drogers een nieuwe labelschaal A-G (de oude liep
  van A+++ tot D). Gemeten 21 sept, alleen lezen:
  - `eprel.py` regel 96 zoekt drogers op in de EPREL-groep **`tumbledriers`**:
    dat is het OUDE register. Gevolg: bij **alle 56 leverbare drogers met
    EPREL-gegevens** (van de 166) toont het blok "Gegevens van het
    energielabel" een klasse van de oude schaal: A+++ 41x, A++ 14x, A+ 1x, met
    de bronvermelding "EPREL, het energielabelregister van de Europese
    Commissie". In de winkel dragen die apparaten nu B of C.
  - Het gekleurde blokje bovenaan komt NIET uit EPREL maar uit het
    specificatieveld van de winkel ("Waarde energielabel", energy_costs.py).
    Bij 42 drogers gevuld: C 21, A 7, B 5, E 4, D 3, G 2 — meestal de nieuwe
    schaal, maar niet altijd: de Klarstein Jet Set heeft in de specificatie C
    (oude schaal) en in de verkoperstitel "EEK G" (nieuwe schaal); dezelfde
    titel zegt "condensdroger" terwijl de specificatie "Luchtafvoerdroger"
    zegt (dat laatste klopt: machinevertaling van de verkoper).
  - Over alle categorieën: bij 241 leverbare producten zijn EPREL-klasse én
    winkelklasse bekend; bij **33 verschillen ze**: 19 drogers (oude tegenover
    nieuwe schaal, zie boven), 10+3 koelkasten (winkel zegt D, EPREL zegt E of
    F: de winkel is daar één tot twee klassen te gunstig), 3 vaatwassers.
    Op die pagina's staan dus twee verschillende labels onder elkaar.
  - Titel tegenover specificatie botst bij 18 producten, maar 15 daarvan zijn
    was-droogcombinaties met terecht twee labels (A wassen, D wassen+drogen).
- **Stap (a) gebouwd op 21 sept na Peters ja (tak fix/drogerlabel-oude-schaal):**
  `eprel_specs.VEROUDERDE_LABELGROEPEN = {'tumbledriers'}` +
  `klasse_geldt_nog(productgroep)`. Eén regel, twee plekken:
  - **Productpagina:** `_regels` laat de energieklasse weg bij die groep; de
    overige EPREL-gegevens (geluid, vulgewicht, afmetingen, garantie) blijven.
    Omdat de klasse wegvalt, laat `ontdubbel_specs` het winkelveld "Waarde
    energielabel" weer staan; dat werd tot nu toe juist verdrongen door het
    oude label ("EPREL wint").
  - **Merchant-feed (erger dan de pagina):** `_eprel_per_product` pakte alleen
    de eerste letter van de klasse, dus van "A+++" ging **"A" naar Google** voor
    apparaten die B of C dragen. Drogers uit het oude register sturen nu geen
    klasse en ook geen registratienummer meer mee (met dat nummer zoekt Google
    zelf het oude label op). Kan de infomelding "Ontbrekend
    certificeringskenmerk" bij ~56 drogers terugbrengen; dat is een melding,
    geen afkeuring, en weegt lichter dan een fout label.
  Proef tegen productie (alleen lezen): productgroepen in de database zijn
  refrigeratingappliances2019 473, dishwashers2019 200, washingmachines2019
  186, ovens 171, rangehoods 111, **tumbledriers 71**, washerdriers2019 63; op
  precies 56 leverbare pagina's valt de klasse weg, 979 ongewijzigd; in de feed
  0 drogers uit het oude register. `python test_eprel_label.py`: 8 gevallen.
  **Haal 'tumbledriers' pas uit die lijst als eprel.py drogers in het nieuwe
  register opzoekt én de rijen opnieuw zijn opgehaald** (oude rijen houden hun
  oude productgroep tot ze ververst zijn).
- **Stap (a) live en gecontroleerd (PR #182, uitrol 15:24):** op de
  LG RT90X8-pagina staat geen "A+++" en geen regel "Energieklasse" meer in het
  EPREL-blok (geluid en bron staan er nog); in de live feed heeft die droger
  geen klasse en geen certificering meer.
- **VASTE REGEL van Peter (21 sept): fouten direct oplossen, nooit uitstellen**
  naar morgen of na de vakantie. Daarom dezelfde middag ook (c) en (d) gebouwd
  (tak fix/feed-plusklasse-en-botsende-labels):
  - **(d) feed kapte de klasse af tot de eerste letter.** `_eprel_per_product`
    stuurt nu de hele klasse (`_fmt_klasse`: AP → A+), geldig = A+++ t/m G.
    Proef tegen productie: 91x A+ en 24x A++ gaan nu goed naar Google (was
    allemaal "A"); ovens en afzuigkappen hebben de plus-schaal nog terecht.
  - **(c) botsende labels.** `eprel_specs.label_zonder_botsing`: zegt het
    winkelveld iets anders dan EPREL, dan valt het gekleurde blokje bovenaan
    weg, en de zin "label X kost € Y meer" ook (die rekende met het
    winkellabel). Het EPREL-blok blijft, met bron en registratienummer; de
    stroomkosten blijven (komen uit kWh, niet uit de letter). Bewust niet
    "EPREL wint in het blokje": onze koppeling kan een zustermodel hebben
    gevonden, dus bovenaan beweren we niets. Proef tegen productie: 14 pagina's
    (10 koelkasten, vooral Inventum/Tomado "winkel D, register E"; 3
    vaatwassers; 1 was-droogcombinatie), 227 ongewijzigd. Het blokje staat
    alleen op de productpagina, niet op lijstpagina's.
  `python test_eprel_label.py`: 21 gevallen.
- **(b) ook gebouwd op 21 sept (zelfde tak): drogers in het nieuwe register.**
  De naam is bij EPREL zelf nagevraagd (`https://eprel.ec.europa.eu/api/product-groups`
  geeft alle registers): **`tumbledryers20232534`**. Bewijs: Bosch WQG133DBNL
  staat in het oude register op A++ en in het nieuwe op **C** (precies wat de
  winkel zegt); LG RT90X8 van A+++ naar **B**. Het nieuwe register levert
  dezelfde velden die wij bewaren (energyClass, noise, ratedCapacity, maten).
  - `eprel.py`: drogers zoeken eerst in `tumbledryers20232534`, dan in
    `tumbledriers` (vangnet voor geluid/maten; de klasse daaruit tonen we niet).
  - **Tweede fout gevonden en gerepareerd: `_bevraag` nam altijd de eerste
    treffer.** EPREL zoekt op "begint met": "RT90X8" geeft RT90X8BC, RT90X8C,
    RT90X8, RT90X8B, RT90X8YB. De LG hing dus aan het registratienummer van een
    andere variant. `_kies_treffer` neemt nu de exacte treffer (limit 2 → 10);
    zonder exacte blijft de eerste gelden, want AEG en Beko melden aan met hun
    productcode erachter ("TR73CB96 916099294" = hetzelfde apparaat). Gemeten:
    van 1.275 koppelingen 885 exact, 380 langer (grotendeels die productcodes),
    10 anders.
  - **Derde fout, dezelfde middag opgelost: koppelingen aan een ander model.**
    De 10 "anders" per stuk bekeken: 6 kloppen (de titel bevat het hele
    gevonden nummer, bv. "Hs61w" → "W8F HS61W"), **4 niet**: Whirlpool "W2F
    HD624" (2x) hing aan "P2F HD624 A", Inventum "KK550B" aan "RKK550B/02" (een
    ander apparaat, en prompt zei het register E waar de winkel D zei), Etna
    "Vv856wit" aan "KVV856WIT" (waarschijnlijk wél goed, maar niet te bewijzen).
    `eprel.koppeling_klopt(gezocht_op, gevonden_model, titel)`: het gevonden
    nummer moet BEGINNEN met het gezochte, of in zijn geheel in de titel staan.
    Geldt op vier plekken: `_kies_treffer` (nieuwe opzoekingen),
    `eprel_specs.eprel_blok` (pagina toont niets), `product_specs.modelnummer`
    (daar stond anders het typenummer van het andere model) en de Merchant-feed
    (geen klasse, geen registratienummer). Proef tegen productie: precies die
    4 van de 1.275 tegengehouden, 0 daarvan nog in de feed.
  - **De inhaalslag is daarom verbreed** (`_inhaalslag` = drogers eerst, dan
    `_afwijkend_typenummer`): ook de 390 koppelingen waar het gevonden nummer
    niet precies het gezochte is worden één keer opnieuw opgezocht, zodat ze op
    het exacte model uitkomen waar dat bestaat. Samen **566 rijen = 6 rondes
    (~36 uur)**, klaar woensdagochtend 23 sept. Peildatum 21 sept 14:00 UTC (de
    eerste ronde met de nieuwe code is 15:13 UTC of later).
  - `eprel_bijwerken.py`: **eenmalige inhaalslag** `_drogers_in_te_halen`: rijen
    uit een vervallen register en drogers die "niet gevonden" waren, opgehaald
    vóór de peildatum 22 sept 00:00 UTC, gaan voor en mogen de hele ronde van
    100 gebruiken. Alleen-lezen geteld: **195 rijen** (71 oud register, 124 niet
    gevonden) = twee rondes, ~12 uur. Rijen die in het oude register blijven
    worden daarna wekelijks nagekeken in plaats van maandelijks.
  Echte opzoeking bij EPREL met de nieuwe code: Bosch C, LG B (model RT90X8
  exact), AEG TR73CB96 C, alle drie `tumbledryers20232534`.
  `python test_eprel_label.py`: 50 gevallen. **Na de merge nakijken:**
  `/api/eprel` (ronde zonder afbreking), daarna in de DB het aantal rijen met
  productgroep `tumbledryers20232534`, en een drogerpagina: staat er weer een
  energieklasse, nu van de nieuwe schaal?

---

## Dagcontrole 21 september (maandag) — Witgoedhuis keurde toch goed; feed gemeten en te oud; gat in de klep gevonden

- **`/api/gezondheid`: GEZOND**, 10 van 10. Leverbaar 2.912, feed 2.907,
  /aanbiedingen 10 categorieën, EPREL 3.649/1.273, prijssprongen 2 (0
  teruggesprongen), tekstwachtrij 0, productpagina zonder sjabloonsporen.
  Railway: 0 serverfouten, geen Traceback, **p99 één uitschieter van 7,7 s**
  (gemiddeld 0,5 s; volgen, bij herhaling uitzoeken). **Doorkliks 20 sept: 24,
  waarvan 17 browser = record** (13 naar MediaMarkt, 6 naar Voordeligwitgoed).
- **Witgoedhuis keurde op 20 sept 20:00 alsnog goed** (melding in MyDaisycon,
  schermafdruk Peter), één dag na het advies "loslaten". De feed staat open:
  `X-Total-Count: 3776`, 3.763 met EAN, velden o.a. ean, price, price_old,
  in_stock, link (de parameter `dl` in de link is het gewone winkelpad:
  `https://www.witgoedhuis.nl/<dl>`; dáár testen, nooit de affiliatelink).
- **Gemeten 21 sept (alleen lezen):** 807 feedproducten staan ook in onze
  catalogus; 770 leverbaar bij ons, 37 zouden herleven; **163 staan nu bij
  één winkel en worden een vergelijking** (dekking 39% → ~45%); volgens de
  feed is Witgoedhuis bij 83 de goedkoopste, 201 gelijk, 486 duurder.
  **Maar de feed is oud:** `last_modified` 6 sept, geen enkel product na 6
  sept bijgewerkt, bijwerkdata alleen in plukken (16 aug, 22 aug, 4-6 sept),
  en **alle 3.776 staan op in_stock**. Tegen hun eigen site gelegd:
  willekeurige steekproef van 16: 14 prijzen gelijk, 2 €4,90 te laag, **4
  uitverkocht**; steekproef van 6 uit de groep "goedkoper": **4 prijzen fout**
  (actieprijs voorbij; de echte prijs was precies onze laagste) en 4
  uitverkocht. De feed is dus het minst betrouwbaar precies waar hij ons de
  "laagste prijs" zou geven. **Besluit: niet bouwen zolang de feed niet
  dagelijks ververst.** **Bericht aan Witgoedhuis verstuurd op 21 sept**
  door Peter, als ticket in MyDaisycon: Reageer → **"Contacteer adverteerder"**
  (niet "Contacteer Daisycon") → campagne Witgoedhuis.nl (6570), media
  WitgoedAanbod.nl (428244); Daisycon bevestigde "Ticket succesvol aangemaakt".
  Via "Reageer" vult Daisycon het berichtvak met de eigen meldingstekst
  inclusief losse HTML: eerst leegmaken. De tekst staat ook op Peters
  bureaublad ("Bericht aan Witgoedhuis - feed dagelijks verversen.txt").
  Antwoord komt in MyDaisycon (Support) en op peter@avantius.nl; niet leesbaar
  voor Claude. Na de vakantie kijken of
  `last_modified` in de feed is gaan bewegen; pas dan bouwen.
- **CORRECTIE op het blok van 19 sept:** daar staat dat onze klep van 3 dagen
  het Witgoedhuis-aanbod vanzelf zou verbergen. **Dat is onjuist.**
  `verouderde_aanbiedingen.py` kijkt naar `Offer.last_synced`, en elke sync
  zet dat op nu voor alles wat in de feed stáát (bv.
  sync_voordeligwitgoed.py regel 161). Een feed die bevroren is maar wel
  alles blijft opsommen, ververst `last_synced` dus gewoon en glipt langs de
  klep én langs `/api/gezondheid`. De klep vangt alleen aanbiedingen die UIT
  de feed verdwijnen (het EP-geval van 10 sept). **Dit gat geldt voor elke
  winkel.**
- **Hoe een bevroren feed wél te herkennen is (gemeten, 45 dagen
  price_history):** Bol, Coolblue, MediaMarkt en EP hadden op álle 45 dagen
  prijswijzigingen (minimaal 94, 75, 15 en 3 per dag; grootste gat 1 dag).
  Expert grootste gat 2 dagen, Voordeligwitgoed 5, Alternate 18 (te klein).
  **Gebouwd 21 sept na Peters ja (tak feat/bevroren-feed-controle):** vierde
  controle in gezondheid.py, `controleer_prijsbeweging`: geen enkele
  prijswijziging bij **Bol, Coolblue of MediaMarkt in 60 uur = STORING**
  ("feed wordt wel gelezen maar lijkt bevroren"). Grens gemeten over 60 dagen:
  langste gat zonder prijswijziging 6 uur (Bol), 24 (Coolblue), 36
  (MediaMarkt). Bewust niet: Expert (gaten van 48 uur), Voordeligwitgoed
  (144), Alternate (420), EP (halve feed). Sloeg de winkelcontrole al alarm
  voor dezelfde winkel, dan komt er geen tweede melding. `rapport()` heeft nu
  een verplichte parameter `PriceHistory`; ontbreekt die, dan is dat STORING,
  nooit stil overslaan. `python test_gezondheid.py`: 23 gevallen goed.
  Alleen-lezen tegen productie: GEZOND (Bol 0,5 uur, Coolblue en MediaMarkt 12
  uur sinds de laatste prijswijziging). Het adres toont die drie regels nu ook.
- **Merchant Center 21 sept:** "Productpagina niet beschikbaar" 15 (19 sept: 9,
  18 sept: 33); websitecontrole aangevraagd na Peters ja, Google bevestigde
  "Websitecontrole aangevraagd. Dit kan tot 12 uur duren." Verder 63
  "productprijs ontbreekt" en 20 "availability ontbreekt" (Google's eigen
  vondsten). **Werkwijze die wél betrouwbaar is:** klikken op `ref` of
  coördinaat mist in Merchant Center geregeld (het venster wisselt van
  schaal). Roep de knop aan vanuit de pagina met `javascript_tool`: zoek het
  `article` met de tekst "Productpagina niet beschikbaar", daarin de `button`
  die begint met "Oplossing bekijken", en doe `.click()`; op de probleempagina
  hetzelfde voor de ene knop "Websitecontrole aanvragen". De bevestigknop in
  het venster vindt `find` wel ("rechter knop naast Annuleren") en die klikt
  goed op `ref`. De MutationObserver vangt de bevestigingstekst.
- **Valkuil opnieuw gemaakt:** shellvariabelen in een `python -c "..."` plakken
  brak op een Windows-regeleinde (\r) uit een tussenbestand. Een steekproef
  tegen een winkelsite altijd als los .py-script (urllib, 1,5 s pauze).

---

## Dagcontrole 20 september (zondag) — gezond; /aanbiedingen/* nog onbekend bij Google

- **`/api/gezondheid`: GEZOND**, 10 van 10. Coolblue 1.443, MediaMarkt 1.085,
  Expert 964, Bol 715, EP 368, Voordeligwitgoed 85 (was 72), leverbaar 2.946.
  Feed 2.941, EPREL 3.645/1.270, prijssprongen 0, tekstwachtrij 0, Railway 0
  serverfouten, p99 max 2,5 s, geen Traceback, productpagina zonder
  sjabloonsporen. Doorkliks 19 sept: 9 (8 browser). Gmail: niets van winkels,
  Awin, TradeTracker.
- **/aanbiedingen telt vandaag 9 categorieën, gisteren 10.** Een categorie
  schommelt rond de ondergrens van 5 dalingen en wisselt dus tussen pagina en
  404. Niet goed voor indexering; na de vakantie bekijken (bv. een pagina pas
  laten vervallen na een paar dagen onder de grens). Nu niets aan doen.
- **Schermafdrukken Peter (MC en SC):** Google mailde "120 klikken in 28 dagen
  via Zoeken" (17 sept). MC 28 dagen: 99 productklikken, 33 winkelklikken,
  laatste dagen 2-4 per dag; producten met de meeste klikken: Dyson V12, Dyson
  V8, AEG LR7386UD4, Beko BM3T3924WMM, Bosch SMV4ECX30E, condensdroger Beko. MC
  totaal 3,08K, door ons ingevoerd 2,92K, 158 "meer gevonden door Google", 168
  niet getoond. **De afgekeurde regels zonder prijs in de lijst "Alle
  producten" zijn Google's eigen dubbele vondsten** (nagekeken: Everglades
  EVCH6840B en Beko B5RCNA366HW1 staan wél in onze feed met prijs en in_stock,
  id 3519 en 3718). Bekend sinds 4 sept; niet opnieuw onderzoeken.
  Zoektrends volgens MC: **droger +16,2%**, dyson +9,1%, wasmachine +2,4%,
  nespresso dalend: het drogerseizoen begint.
- **URL-inspectie (alleen gelezen):** `/category/drogers` is nu **geïndexeerd**
  (op 14 sept nog "gevonden, niet geïndexeerd"). `/aanbiedingen/drogers` is
  **"onbekend bij Google"**, hoewel sitemap-aanbiedingen.xml vandaag is gelezen
  (Succesvol, 10 pagina's ontdekt). Gewone vertraging. **Indexering aangevraagd op 20 sept ~11:30 (na Peters
  ja)** voor vier adressen, alle vier door Google bevestigd met "Indexering
  aangevraagd — toegevoegd aan een prioriteitscrawlwachtrij": /aanbiedingen,
  /aanbiedingen/drogers, /aanbiedingen/wasmachines en
  /onderzoek/prijsverschillen-witgoed (alle vier stonden op "niet
  geïndexeerd"). Opnieuw indienen verandert de plek in de rij niet; dus niet
  herhalen. Over een week met URL-inspectie kijken of ze erin staan.
  **Werkwijze aanvragen:** adres intypen (zie hieronder), knop "Indexering
  aanvragen" via `find` + `scroll_to` + klik op de `ref`; de live test duurt
  ~1 minuut; een MutationObserver vangt de bevestiging; daarna "Sluiten". Na een
  tweede inspectie staan er meerdere knoppen met dezelfde naam in de pagina:
  neem de laatste.
  **Werkwijze:** het inspectieveld bovenaan pakt tekst alleen na een klik op
  coördinaat (600, 27), niet via de `ref`; daarna typen, Enter, 10 s wachten.

---

## Dagcontrole 19 september (zaterdag) — alles gezond; zoekopdracht "x" vertekende 10-11 sept

- **`/api/gezondheid`: GEZOND**, 10 van 10 routines. Coolblue 1.457, MediaMarkt
  1.065, Expert 972, Bol 721, EP 365 (10 ouder dan 36 uur), leverbaar 2.949.
  Feed 2.944 items, /aanbiedingen nu **10** categorieën, productpagina zonder
  sjabloonsporen, EPREL 3.637/1.267 zonder afbreking, prijssprongen 0,
  tekstwachtrij 0. Railway 24 uur: 0 serverfouten, geen Traceback, p99 één
  uitschieter van 3,3 s. Doorkliks 18 sept: 14 (12 browser). Zonder foto 7
  (was 4-5; volgen).
- **Controlepunten van 18 sept, beide goed:** `available_since` is bij 46
  producten gevuld (eerste 18 sept 19:10 NL; 34 in de Coolblue-ronde van 20:14;
  via Coolblue 31, MediaMarkt 6, Bol 5, Expert 5; 0 alweer teruggeklapt). De
  sitemap-datums schuiven niet mee: van de 238 met datum 18 sept staan er 182
  nog op 18 sept, 54 kregen terecht 19 sept (prijswijziging); vandaag 136 van
  2.949 met de datum van vandaag. **Wel gezien:** bij 7 producten werd de datum
  ouder. Verklaring: de Bol-sync verwijdert een aanbieding die wegvalt, en dan
  vervalt ook haar `created_at` als signaal. 0,2%, geen actie; niet "repareren"
  door last_synced te gebruiken.
- **Zoekopdracht "x" in Search Console (aanbeveling "+32.100%"):** 644
  vertoningen, 0 klikken, positie 3,1, alleen op 10 en 11 september (~280 en
  ~360), verspreid over tientallen productpagina's met elk 7-16 vertoningen.
  Dat is een productmodule die Google twee dagen op de zoekterm "x" toonde; geen
  bezoekers, geen waarde, niets aan te doen. **Gevolg voor onze cijfers:** 10
  sept was niet 670 maar ~390 echte vertoningen, 11 sept niet 645 maar ~285. Het
  niveau van ~300 per dag gold dus al vanaf 10-11 sept; de "daling op 12 sept"
  was deels het wegvallen van deze ruis. Bij vergelijkingen over die week de
  zoekopdracht "x" uitsluiten (filter Zoekopdracht → bevat niet).
- **Mails:** niets van de vijf winkels (verstuurd do 17 sept 12:30; pas 1,5
  werkdag), niets van TradeTracker of Awin. Daisycon Witgoedhuis nog
  `X-Total-Count: 0`. **Peters Daisycon-account staat op peter@avantius.nl**
  (bleek uit een automatische Daisycon-mail van 19 sept): het antwoord op het
  ticket van 17 sept komt dáár binnen, niet in de Gmail die Claude kan lezen.
  Peter moet dat postvak en MyDaisycon → Support zelf nakijken.
- SC-overzicht (schermafdruk Peter): 205 klikken in 3 maanden, geïndexeerd
  2.717 / niet 1.442 (ongewijzigd, laatste update 14 sept).
- **Merchant Center 19 sept:** "Productpagina niet beschikbaar" van 33 naar
  **9** na de websitecontrole van 18 sept (de knop werkt dus). Opnieuw
  aangevraagd voor die 9 na Peters ja; Google bevestigde letterlijk
  "Websitecontrole aangevraagd. Dit kan tot 12 uur duren." Verder: 111
  "productprijs ontbreekt" (Google's eigen vondsten, verborgen) en 11
  "availability ontbreekt". **Werkwijze aangescherpt:** de rechtstreekse link
  naar de probleempagina laadt geen inhoud; ga via Producten → Vereist
  aandacht (`priorityFixes=false`). Een klik op een `ref` pakt pas na
  `scroll_to` op diezelfde `ref`. De MutationObserver vangt de
  bevestigingsbalk wél, het openen van het venster niet altijd; een
  schermafdruk laat het venster zien.
- **Witgoedhuis/Daisycon losgelaten (19 sept, advies Claude, stand uit
  MyDaisycon via schermafdruk Peter):** status "Aangevraagd — je media is nog
  niet gekeurd door de campagne": Daisycon liet de site op 7 sept toe, de
  winkel zelf behandelt de aanvraag van 4 sept niet. En: **de Witgoedhuis-feed
  is sinds 8 sept 17:46 niet bijgewerkt** (3.776 producten). (ONJUIST, zie correctie 21 sept: de klep vangt een bevroren feed niet.)
  ~~Met onze klep van 3 dagen zou hun aanbod na goedkeuring meteen op
  niet-leverbaar gaan.~~ Dus:
  niet opnieuw mailen, geen nieuw ticket, niet meer dagelijks controleren. De
  aanvraag blijft staan. Van het ticket van 17 sept kwam geen
  ontvangstbevestiging; niet najagen. MyDaisycon is voor Claude niet
  bereikbaar (robotcontrole + inlog; niet omzeilen). **Les voor de volgende
  kandidaat:** vooraf nagaan of de winkel op aanvragen reageert en of de feed
  dagelijks ververst ("Laatste update" in het netwerk).
- **Twee merkwinkels aangevraagd via Awin (19 sept, door Peter zelf):**
  **De'Longhi NL** (ID 22918; ~200 producten, tot 6%, productfeeds aanwezig,
  cookie 15 dagen, uitbetaling ~120 dagen) en **AEG NL** (ID 26720; níet
  "AEG Shop NL"; over een feed staat niets op de programmapagina, in de
  aanvraag is gevraagd of er een feed met EAN is; commissie alleen op de
  openbare winkel, niet op de "closed user group"). Beide met een Engelse
  toelichting: prijsvergelijker, geen brand bidding/cashback/codes. Awin
  bevestigde beide keren "aanvraag naar de adverteerder verzonden".
  **Waarom deze twee** (gemeten 19 sept): AEG 225 leverbaar bij ons waarvan 144
  bij maar één winkel; De'Longhi 55 waarvan 24; Smeg 37 waarvan 16 (te klein,
  niet aangevraagd). Hele catalogus: 1.785 bij één winkel, 1.163 bij twee of
  meer. Verwachting eerlijk gehouden: merkwinkels zijn zelden de goedkoopste,
  dus weinig klikken; de winst is dat een solo-product een vergelijking wordt
  (AEG hooguit +2 à 3 procentpunt dekking). **Bouwen pas na 5 oktober, en pas
  nadat de feed is getoetst op EAN en dagelijkse verversing** (les
  Witgoedhuis). Awin-berichten komen waarschijnlijk op peter@avantius.nl
  binnen; dat postvak kan Claude niet lezen.
- **Nog nakijken na de vakantie:** het merk De'Longhi staat op twee manieren
  in de catalogus ("delonghi" 33, "de'longhi" 27). Geeft dat twee merkpagina's?
- **Peter belt geen winkels of redacties** (19 sept: "zo mondig ben ik niet").
  Niet meer voorstellen. Opvolging alleen per e-mail: na ~twee weken stilte
  één korte herinnering als .txt op het bureaublad, daarna laten rusten.
  Door de vakantie wordt dat de week van 5 oktober.

---

## 18 september (middag) — gezondheidscontrole gebouwd; Peter weg 25 sept t/m 2 okt

**Peter is op vakantie van vrijdag 25 september tot en met vrijdag 2 oktober.**
In die week: geen dagcontrole, geen MC-knop (afkeuringen lopen naar schatting
op van 33 naar ~50; herstelt met één klik), rankingmeting van 29 sept schuift
door. ~~Na woensdag 23 september niets nieuws meer live zetten~~ (op 22 sept
door Peter losgelaten: per dag beoordelen, zie het blok van 22 sept). Betaling Railway: wordt van Peters
creditcard afgeschreven (door Peter bevestigd 18 sept), dus geen tegoed dat
op kan raken.

**Waarom de controle:** niets waarschuwde als een winkelfeed stilvalt. Sinds
de veiligheidsklep (3 dagen niet ververst = niet-leverbaar) én noindex op
niet-leverbare producten samen bestaan, kost een stille Coolblue-feed na drie
dagen 741 productpagina's hun plek in Google (MediaMarkt: 509). De voorpagina
blijft dan werken, dus de gewone UptimeRobot-meting ziet niets.

**Gebouwd (tak feat/gezondheidscontrole):** `gezondheid.py` + route
`/api/gezondheid` in routes/main.py. Antwoordt platte tekst, leesbaar op een
telefoon: `GEZOND` met status 200, of `STORING` met status 503 en per punt
in gewone taal wat er mis is. Controleert:
- per winkel: laatste sync ouder dan **30 uur** (twee gemiste beurten; de klep
  grijpt pas na 72 uur in, dus er blijft anderhalve dag);
- per winkel: meer dan **30%** van de leverbare aanbiedingen ouder dan 36 uur
  (feed levert maar een deel; alleen bij winkels met minstens 50 aanbiedingen);
- leverbare producten onder de **2.500** (nu 2.923; vaste bodem, aanpassen als
  de catalogus blijvend krimpt);
- alle tien routines gepland en geen enkele meer dan 2 uur over tijd;
- de sleutel voor de eigen teksten aanwezig.
Bewust niet: EPREL, prijssprongen, foto's (kost niets als het hapert). Een
controle die zelf crasht geeft STORING, nooit GEZOND.
**Grenzen zijn gemeten, niet geschat** (productie 18 sept): bij elke gezonde
winkel 0 leverbare aanbiedingen ouder dan 14 uur; alleen EP 54 van 400 (13,5%)
ouder dan 36 uur = de bekende halve feed. Komt er een winkel bij, of gaat een
winkel anders leveren: grenzen opnieuw meten, en de winkel toevoegen aan
`WINKELS` en `VERWACHTE_ROUTINES` in gezondheid.py, anders geeft de nieuwe
routine geen alarm als ze ontbreekt.
Getest: 15 gevallen in een proefdatabase (`python test_gezondheid.py` in de
projectmap; draai die opnieuw na elke wijziging van de grenzen),
alleen-lezen tegen productie = GEZOND, lokaal = STORING/503 (geen planner,
hoort zo; ook "Proef tegen productie" geeft dus STORING op de routines).
**Let op bij de dagcontrole:** een STORING geeft een 503 en telt dus mee in
de 5xx van `railway metrics`. Dat is dan terecht een signaal.

**Live en gekoppeld 18 sept (PR #172):** `/api/gezondheid` geeft op productie
GEZOND, 10 van 10 routines. Peter maakte om ~16:35 de tweede UptimeRobot-meting
aan: naam "Witgoed gezondheid: feeds en routines" (Chrome vertaalt dat op zijn
scherm naar "voedingen"; de echte naam en de mails zeggen "feeds"), gewone
HTTP-meting, elke 5 minuten vanuit Noord-Amerika, e-mail naar
pfmhoman@gmail.com. Eerste controle in de Railway-logs: `HEAD /api/gezondheid
200`. **UptimeRobot vraagt alleen de kop op (HEAD), niet de tekst**: het alarm
hangt dus aan de status 503, niet aan het woord STORING. Lokaal nagekeken dat
HEAD bij een storing ook 503 geeft. Verander die statuscode dus nooit naar
200-met-tekst. Een DOWN-mail met deze naam betekent NIET dat de site plat ligt,
maar dat er een feed of routine stilstaat; het adres openen op de telefoon
toont wat. Een DOWN-mail met de naam "www.witgoedaanbod.nl" = site onbereikbaar.

---

## Dagcontrole 18 september — noindex 72 → 239: herleefde producten blijven bij Google op noindex

- **Dagcontrole schoon:** EPREL 3.616/1.261 zonder afbreking, prijssprongen
  0, tekstwachtrij 0, tien routines, EP 592 en Bol 342 (bekend), feed 2.918
  items, /aanbiedingen 9, Railway 24 uur 0 serverfouten, p99 max 2,3 s,
  geen Traceback. Daisycon nog 0. Gmail: niets van winkels, Daisycon,
  TradeTracker, Awin. UptimeRobot: alleen de twee TEST-mails van het
  aanmaken (17 sept 14:03), geen echt incident.
- **Merchant Center (schermafdruk Peter):** 3,09K producten, 2,94K
  goedgekeurd, 142 niet goedgekeurd waarvan 109 verborgen → **33 van
  ons** (17 sept: 26, 16 sept: 15). 127 klikken in 28 dagen; van ~12/dag
  (6 sept) naar ~4/dag.
- **Search Console indexering (laatste update 14 sept):** geïndexeerd
  2.839 → **2.717**; noindex 72 → **239**; gevonden-niet-geïndexeerd
  1.241 → 1.012; 404 45 → 67; gecrawld-niet-geïndexeerd 17 → 22;
  canoniek 62 → 69; omleiding 14; robots 5; dubbel 5; 5xx 9.
- **Oorzaak gemeten:** `templates/product.html` regel 17 zet `noindex`
  zodra `product.is_available` onwaar is. In de DB: 3.725 producten,
  **804 niet leverbaar** (377 zonder enige aanbieding, 306 >14 dagen niet
  gezien, 121 korter dan 14 dagen). Per dag klappen 30-75 producten om.
  Steekproef van 210 noindex-adressen uit SC tegen de DB: **83 (40%) zijn
  vandaag weer leverbaar** en staan dus weer op index; 49 daarvan via de
  volledige Coolblue-feed van 15 sept, 13 Bol, 9 MediaMarkt. Alle 83 staan
  in sitemap-producten.xml, maar bij 56 is `lastmod` ouder dan 15 sept (30
  ouder dan 10 sept): `_laatste_wijziging_per_product()` in routes/seo.py
  kijkt naar prijswijzigingen, niet naar het weer leverbaar worden. Google
  krijgt dus geen seintje om terug te komen.
- **Gebouwd 18 sept na Peters ja (tak fix/sitemap-datum-bij-weer-leverbaar):**
  `products.available_since` (opstartmigratie in app.py) wordt gezet door
  een luisteraar op `Product.is_available` in models.py, alleen bij een
  echte overgang False → True. Bewust een luisteraar en niet in
  `refresh_pricing`: sync_products zet is_available ook rechtstreeks.
  `_laatste_wijziging_per_product()` in routes/seo.py neemt nu het nieuwste
  van: laatste prijspunt, `created_at` van een leverbare aanbieding (nieuwe
  winkel op de pagina) en `available_since`. **Niet** offers.updated_at of
  last_synced gebruiken: die schuiven elke sync op en dan leert Google
  lastmod te negeren. Gemeten tegen productie (alleen lezen): 495 van 2.921
  producten krijgen een nieuwere datum, verspreid over veel dagen (14 sept
  117 = Coolblue-feed); van de 83 herleefde gaat "datum op/na 10 sept" van
  53 naar 75. De overige 8 klapten terug met dezelfde prijs op een
  bestaande aanbieding; die vangt `available_since` pas vanaf nu op.
  Nog open: (2) eventueel pas noindex na een aantal dagen niet-leverbaar
  — eerst 2-3 weken kijken of noindex in SC daalt.
- **Live en gecontroleerd 18 sept 13:20 (PR #170):** kolom
  `available_since` staat in de productie-DB (nog overal leeg, zoals
  bedoeld: vult zich bij de eerstvolgende echte overgang). Sitemaps,
  voorpagina, categorie en /aanbiedingen geven 200; geen Traceback. Productsitemap
  vóór/na: 558 datums nieuwer, **0 ouder**; Etna KCV520NZWA van 25 aug
  naar 14 sept; de 83 herleefde "op/na 10 sept" van 53 naar 74. 240 producten
  met de datum van vandaag, verklaard: 204 prijswijziging vandaag + 36 alleen
  een nieuwe winkel vandaag. **Bij de dagcontrole van 19 sept nakijken:**
  is `count(available_since)` boven 0 gekomen, en zijn de datums van 18
  sept blijven staan (dus niet allemaal naar 19 sept geschoven)? Rond 5-9
  oktober in SC: daalt "Uitgesloten door noindex" (239)?
- **MC-websitecontrole aangevraagd 18 sept ~middag** voor 33 producten (na
  Peters ja in de chat; de toestemming van 17 sept staat in dit bestand,
  maar een bevestigknop in Peters Google-account vraagt per sessie een ja
  in de chat). Bewezen aangekomen: een tweede poging gaf "U heeft al een
  beoordeling aangevraagd voor dit probleem". Volgende kan vanaf 19 sept.
  **Werkwijze:** in Merchant Center klikt een coördinaat ernaast (het
  venster schaalt afwijkend); zoek knoppen op naam met `find` en klik op de
  `ref`. Het bevestigingsvenster verschijnt traag: wacht 3 s en zoek dan de
  rechterknop in het venster. De donkere meldingsbalk onderaan verdwijnt
  binnen seconden; zet vóór het klikken een MutationObserver op
  document.body om de tekst op te vangen.
- Het adres met `%2B` (setjes, bv. miele-wq-1000...%2B...) geeft 200, ook
  als AdsBot; dat is niet het Railway-%-probleem.
- Valkuil opnieuw gemaakt: een script patchen met `sed` en `\n` brak het
  bestand. Gebruik het bewerkgereedschap of een .py uit de Write-tool.

---

## Dagcontrole 17 september (middag, 12:50) — Google heeft geantwoord

- **Merchant Center-support antwoordde binnen een uur** (ticket
  7-8523000041223, medewerker Tiemen, 17 sept 12:46): Google ziet "op dit
  moment geen fouten meer" bij de productpagina's en heeft **geen inzicht
  meer in welke fout de crawler destijds kreeg** (time-out, verbinding of
  DNS). Verwijst naar het rapport Crawlstatistieken in Search Console (dat
  hadden we al gebruikt, blok 14 sept) en bevestigt: websitecontrole
  maximaal 1x per 12 uur; opnieuw aanvragen zodra afkeuringen zichtbaar
  zijn. **Deze lijn is daarmee gesloten: Google levert geen tijdstippen of
  IP-bereik.** Wat overblijft is de externe bereikbaarheidsmeter (keuze
  Peter, optie 3 van 14 sept). Niet terugmailen; er komt niets meer.
- Meetpagina's schoon: EPREL 3.605 opgezocht / 1.258 gevonden, geen
  afbreking; prijssprongen 1, teruggesprongen 0; teksten wachtrij 2 met
  sleutel; alle tien routines gepland; Bol-sync liep om 12:45 nog
  (klaar=None is normaal, duurt 10-12 min). `niet_ververst_3d`: EP 585 en
  Bol 342 (bekend), rest 0. Coolblue 1.422, feed 2.911 items (allemaal
  in_stock), /aanbiedingen 9 categorieën, productpagina zonder
  sjabloonsporen, home 0,24 s.
- Railway 24 uur: 5xx 0, foutpercentage 0, p99 max 2,6 s (één punt boven
  de 2 s), geen WORKER TIMEOUT of Traceback in de logs.
- Daisycon Witgoedhuis nog `X-Total-Count: 0`. Gmail: de vijf winkelmails
  staan verzonden (10:26-10:42 UTC), nog geen antwoord; niets van
  Daisycon, TradeTracker, Awin.
- **Externe bereikbaarheidsmeter staat aan (17 sept, ~13:30):** UptimeRobot,
  gratis plan, account op pfmhoman@gmail.com (Register, niet via GitHub),
  één meting op https://www.witgoedaanbod.nl/ elke 5 minuten. Dashboard:
  dashboard.uptimerobot.com/monitors (Peters Chrome). Bij de dagcontrole
  naast Google's "kan niet worden bereikt" leggen. Na ~2 weken: staat de
  meter op 100% terwijl Google blijft klagen, dan zijn de haperingen korter
  dan 5 minuten (Solo-plan met 60 s kost EUR 9/maand; pas dan afwegen).
  Nog nakijken: staat e-mailmelding bij storing aan op dat adres?
- Merchant Center en Search Console vanmiddag niet opnieuw geopend: de
  ochtendmeting van vandaag staat hieronder en de MC-knop mag pas na 12
  uur weer (vanavond na ~22:00, of morgen).

---

## Overdracht 17 september, slot (13:00) — laatste stand vóór de nieuwe sessie

**Gesprek van 14-17 september is vol en afgesloten. Dit blok + het blok
"Overdracht 17 september (middag)" hieronder zijn samen de complete stand.
MEMORY.md in de Claude-projectmap draagt dezelfde feiten compact.**

### Winkelmails: verstuurd op 17 sept (door Peter zelf, vanuit Gmail)
- Keukenloods (info@keukenloods.nl), Correct (verkoop@correct.nl), De
  Schouw Witgoed (info@deschouwwitgoed.nl), Bemmel & Kroon
  (verkoop@bemmelenkroon.nl) en **United Retail (sales@retail.nl)** — dat
  is het hoofdkantoor in Huizen (tel. 035 525 95 95) van zowel Electro
  World als De Witgoed Specialist, dus één mail dekt beide formules.
  Witgoedspecialist niet apart gemaild. **TP witgoed bewust niet:
  tweedehands/gereviseerd** (staat in hun eigen productteksten).
- Onderwerp "Uw prijzen horen thuis in onze witgoedvergelijking"; aanbod:
  productfeed (EAN, prijs, voorraad, link), drie maanden gratis, daarna
  vergoeding per bezoeker/bestelling in overleg. Zonder prijsvoorbeeld:
  de voorbeelden van 8 sept golden niet meer (Koenic KFZ 621 wij nu 397;
  Inventum VKI6010ZIL wij 216,81 vs Keukenloods/Correct 219).
- Bijhoudlijst: "Winkelmails - klaar om te versturen.txt" op Peters
  bureaublad. **Dagelijks Gmail nakijken** (zoek: keukenloods OR correct
  OR deschouw OR bemmelenkroon OR retail.nl). Zegt een winkel ja: per
  winkel een offers-only sync op EAN bouwen naar het recept van
  Voordeligwitgoed (~halve dag), klikken tellen via /uit/ (geen netwerk).
  Na twee weken stilte: één herinnering, daarna laten rusten.

### De Gmail-koppeling van Claude kan NIET versturen
`send_message` gaf "requires additional permissions"; er is niets vanuit
Claude verstuurd. Alleen lezen/zoeken werkt (pfmhoman@gmail.com; het
zakelijke peter@avantius.nl zit er niet in). Mails voor Peter dus als .txt
op het bureaublad klaarzetten met adres, onderwerp en aanhef per
ontvanger. Wil Peter dat Claude verstuurt: Gmail-koppeling opnieuw
verbinden in de Claude-app met verstuurrecht.

### Bureaublad (stand 17 sept 13:00)
- "Winkelmails - klaar om te versturen.txt" (met bijhoudlijst; alle vijf
  verstuurd 17 sept).
- "Sites om te benaderen - prijsverschillen witgoed.txt" (17 doelen; nog
  niets verstuurd; Peter doet dat zelf, max 5 per dag, één zin op maat).
- "Prijsverschillen witgoed - tekst voor sites en pers.txt" (mailtekst).
- "Bevindingen 14 september.txt" (naslag; de Railway-tekst erin NIET
  versturen, Railway antwoordt niet op Hobby; de vraag ligt nu bij Google
  Merchant Center-support, antwoord per mail afwachten).

### Wat de nieuwe sessie morgen (18 sept) doet, in volgorde
1. Dagcontrole (lijst in "Elke dag: de storingscontrole"), inclusief:
   MC-knop "Websitecontrole aanvragen" (dagelijks, zonder vragen; 1x per
   12 uur toegestaan), SC "kan niet worden bereikt" per dag, en één
   productpagina op sjabloonsporen.
2. Gmail: antwoorden van Daisycon (Witgoedhuis-ticket), Google Merchant
   Center-support, de vijf winkels, TradeTracker/EP, Awin/Coolblue.
3. TradeTracker: staat de verkoop van 16 sept (Voordeligwitgoed, EUR 4,73)
   nog op "onder beoordeling" of geaccepteerd? (affiliate.tradetracker.com
   via Peters Chrome, Rapportage → Transacties → Salestransacties.)
4. Coolblue-teller ~1.4K, feed ~2.9K items, /aanbiedingen telt nog 9
   categorieën?
5. Dinsdag 22 sept: rankingmeting (docs/RANKING-METING.md), met "witgoed
   prijsvergelijkers" als elfde.
6. Niet zelf oppakken zonder Peter: externe uptime-meter, verhuizing naar
   EU West, nieuwe winkel-koppelingen (pas na een ja van een winkel).

---

## Overdracht 17 september (middag) — alles van vandaag, plus de open lijnen

**Dit gesprek zat op 80% en is afgesloten met deze overdracht. Lees ook de
blokken "17 september — prijsdalingenpagina's" en "Dagcontrole 16
september" hieronder; MEMORY.md in de Claude-projectmap heeft dezelfde
feiten compact.**

### Live gezet vandaag (allemaal gemerged en gecontroleerd)
- `/aanbiedingen` + `/aanbiedingen/<categorie>` (PR #163): 9 categorieën,
  155 apparaten; sitemap-aanbiedingen.xml apart aangemeld in SC (10 URL's).
- `/onderzoek/prijsverschillen-witgoed` (PR #164): 1.117 apparaten, gem.
  EUR 49 (9,7%); setjes en >60% uitgesloten; in voettekst en
  sitemap-overig; ververst elke 6 uur.
- Voorpagina/over-ons noemen zich "witgoed prijsvergelijker" (PR #162,
  16 sept). Trends: dat woord wordt nauwelijks gezocht; "wasmachine/droger
  aanbieding" wel.

### Op Peters bureaublad (hij verstuurt zelf)
- "Prijsverschillen witgoed - tekst voor sites en pers.txt": mail + korte
  versie + wat je niet moet claimen.
- "Sites om te benaderen - prijsverschillen witgoed.txt": 17 doelen in 4
  groepen (RetailTrends, Emerce, Twinkle; Kassa, Radar, ID.nl; Milieu
  Centraal, Gaslicht, UnitedConsumers, Korting.blog, forhome, Kekmama,
  Mammie Mammie, Wonen met Lef, That Lyfestyle; Leidsch Dagblad/Omroep
  West), elk met bewijs-artikel. Max 5 per dag, één zin op maat.
  Concurrenten (Consumentenbond, Tweakers, Kieskeurig, Knibble, Slimster)
  niet benaderen. Bijhouden wie linkt; effect via docs/RANKING-METING.md.
- "Mail aan winkels - meedoen op WitgoedAanbod.txt" (herzien 17 sept): zes
  winkels zonder affiliateprogramma (Keukenloods, Correct, Electro World,
  De Schouw, Witgoedspecialist, Bemmel & Kroon), zonder prijsvoorbeeld
  (de voorbeelden van 8 sept gelden niet meer: Koenic KFZ 621 wij nu 397,
  Inventum VKI6010ZIL wij 216,81 vs Keukenloods/Correct 219). **TP witgoed
  verkoopt tweedehands: niet benaderen, niet als concurrent op nieuwprijs
  tellen.** Zegt een winkel ja: koppeling op EAN per winkel bouwen (recept
  Voordeligwitgoed), ~halve dag per winkel.

### Verstuurd vandaag, antwoord afwachten (dagelijks in Gmail kijken)
- **Daisycon-supportticket** over Witgoedhuis (campagne 6570, media
  428244): route Support → Contacteer Daisycon → Campagne keuring → "Geen
  antwoord van campagne". De chatbot laat niet door naar een medewerker.
  Peter wilde eerst tot 18 sept wachten, koos toch voor het ticket.
- **Merchant Center-supportvraag** over "Productpagina niet beschikbaar"
  (? → Contact opnemen → Problemen met bestemmingspagina → E-mail;
  bedrijfsnaam Avantius VOF, inzendingsmethode Planning, land Nederland,
  samenvatting max 1.000 tekens). Gevraagd: welke fout de crawler krijgt,
  tijdstippen/IP-bereik, en vaker dan 1x per 12 uur controleren. Geen
  referentienummer; antwoord per mail op pfmhoman@gmail.com.

### Dagcontrole 17 sept (ochtend)
Alles schoon behalve: MC "productpagina niet beschikbaar" weer 24 → knop
gedrukt (26 op dat moment; **Peter gaf toestemming dit dagelijks te doen
zonder te vragen**, Google staat 1x per 12 uur toe); "kan niet worden
bereikt" 14 sep 19, 15 sep 21 (houdt aan); SC 14 sep 338 vertoningen/6
klikken (stabiel ~330); Coolblue 1.422; leverbaar 2.917; doorkliks 16
sept 22 (record). TradeTracker-verkoop van 16 sept (Voordeligwitgoed,
EUR 4,73) staat "onder beoordeling".

### Werkwijze-lessen van vandaag
- Sjablonen: `.claude/launch.json` heeft "Proef tegen productie" (railway
  run + app.py, geen planner) → lokale server op :5001 tegen de
  productie-DB voor een schermafbeelding vóór de merge. create_app() doet
  de idempotente migraties (zoals elke deploy); niets anders schrijft.
- Patches met veel aanhalingstekens: via een .py in de scratchpad
  (Write-tool), niet via een bash-heredoc (brak twee keer).
- SC-tabbladen (DAGEN, PAGINA'S) uitlezen: navigeer met `&breakdown=date`
  resp. `page`, scroll, lees `document.querySelectorAll('table')`.
  ZOEKOPMAAK rendert niet; overslaan.
- Google Trends via Chrome: na laden scrollen, dan de regel die begint met
  "Gemiddeld	" uit `document.body.innerText` lezen.
- Peters e-mail voor de winkels/pers is peter@avantius.nl; Gmail-MCP ziet
  alleen pfmhoman@gmail.com (Coolblue-mail zat op avantius).

### Open lijnen (in volgorde)
1. Dagelijks: dagcontrole + MC-knop + Gmail (Daisycon, Merchant Center,
   TradeTracker/EP, Awin/Coolblue).
2. Dinsdag: rankingmeting (docs/RANKING-METING.md), nu ook "witgoed
   prijsvergelijkers" als elfde (16 sept: niet in top 50).
3. Over 2-4 weken: SC-vertoningen op /aanbiedingen/* en
   /onderzoek/prijsverschillen-witgoed; welke sites uit de lijst linkten.
4. Onbereikbaar-probleem: afwachten wat Google antwoordt; anders externe
   meter (keuze Peter). Railway-forum levert niets op (Hobby).
5. 11 oktober: kenmerkpagina's beoordelen (blok 14 sept).
6. Nog niet gedaan: winkel-koppelingen zonder netwerk (pas na een ja),
   "Prijsverschillen"-publicatie maandelijks onder de aandacht brengen
   (de pagina ververst zelf; de mails zijn handwerk van Peter).

---

## 17 september — prijsdalingenpagina's (/aanbiedingen) gebouwd

**Waarom:** Google Trends (16 sept): "goedkope wasmachine" en "witgoed
prijsvergelijker" zoekt bijna niemand; "wasmachine aanbieding" (45) en
"droger aanbieding" (51) wel. Productie-DB gemeten (17 sept): per week
170-360 dalingen van >=10% én >=EUR30, afgelopen 7 dagen 168 die nog
staan, 149 waarbij die winkel nu de goedkoopste is. Genoeg voor een pagina
per categorie met échte, gemeten dalingen -- iets wat winkels niet kunnen
bewijzen. Bewust géén koopgids/filterpagina (die leveren niets op).

**Gebouwd (tak feat/prijsdalingen):**
- `prijsdalingen.py`: window-query over price_history (lag per
  product+winkel), drempels DREMPEL_PCT 10% én DREMPEL_EUR 30, venster 7
  dagen, prijs moet nu nog gelden bij die winkel (anders "teruggesprongen"),
  één regel per apparaat (grootste daling), MIN_PER_PAGINA 5. Procescache
  15 min. Route, categorielink en sitemap gebruiken dezelfde functies.
- `routes/prijsdalingen.py`: `/aanbiedingen` (overzicht per categorie) en
  `/aanbiedingen/<slug>` (404 onder de 5). ItemList-structured data.
- Sjablonen `prijsdalingen.html` / `prijsdalingen_overzicht.html`, teksten
  via translations.py (`dalingen.*`, NL+EN), CSS onderaan main.css.
- Categoriepagina: rode knop "Aanbiedingen: n echte prijsdalingen deze
  week" vóór de kenmerkknopjes; sitemap-soort `aanbiedingen`
  (sitemap-aanbiedingen.xml, in de index).
- Leesproef tegen productie (test_prijsdalingen.py, `railway run`): 155
  apparaten, 9 categorieën met pagina (wasmachines 17, drogers 18,
  koelkasten 35, stofzuigers, koffiemachines, ovens, vaatwassers,
  kookplaten, wasdroogcombinaties); afzuigkappen terecht 404.
- Lokale proefserver tegen productie: `.claude/launch.json` → "Proef tegen
  productie" (railway run + app.py, dus zonder planner; create_app doet
  wel de idempotente migraties, zoals elke deploy).

**Gemerged 17 sept 10:51 (PR #163); sitemap-aanbiedingen.xml dezelfde dag apart
aangemeld in Search Console (10 URL's, succes; het veld wil de VOLLEDIGE URL en
de knop moet op coördinaat geklikt worden).** Live: 9 categorieën, 155
apparaten.

**Punt 2 gebouwd (tak feat/prijsverschillen):** `/onderzoek/prijsverschillen-witgoed`
= `prijsverschillen.py` (cache 6 uur) + route in routes/prijsdalingen.py +
`prijsverschillen.html`, teksten `verschil.*` in translations.py, link in
de voettekst, in sitemap-overig, Dataset-structured data (CC BY 4.0).
Cijfers 17 sept: 1.117 apparaten bij >=2 winkels, gemiddeld EUR 49 (9,7%),
361 >=EUR50, 187 >=EUR100, 345 overal gelijk; wasdroogcombinaties EUR 78,
ovens/airfryers 71, wasmachines 67. Aandeel goedkoopste: Voordeligwitgoed
93% (55 apparaten), Bol 62%, Coolblue 48%, MediaMarkt 46%, EP 32%, Expert
21%. Prijswisselingen 30 dagen: Bol 86% van de aanbiedingen gewijzigd (8,3
wijzigingen per aanbieding), Coolblue 88%, MediaMarkt 73%, Expert 37%.
Uitgesloten: setjes (Apparaatsets) en verschillen >60% (andere uitvoering
of feedfout; de Bosch HSG7361B1 Bol 1279/Expert 2099 en een AEG-set 639/1359
vielen daardoor weg). Tekst voor sites/pers staat op Peters bureaublad:
"Prijsverschillen witgoed - tekst voor sites en pers.txt". Punt 3 (lijst
sites om te benaderen) nog te maken.

**Verder:** Search Console → Sitemaps → sitemap-aanbiedingen.xml; na 2-4 weken kijken of "wasmachine aanbieding"/"droger
aanbieding" vertoningen geven (tabblad ZOEKOPDRACHTEN). Volgende stap
(punt 2 van 17 sept): pagina "Prijsverschillen witgoed 2026" met de
gemeten verschillen (gem. EUR 51/10% over 1.126 apparaten; Coolblue vaakst
goedkoopste) als linkbare publicatie.

**MC-websitecontrole:** Peter gaf op 17 sept toestemming die dagelijks te
klikken (Producten → Vereist aandacht → Alle problemen → Productpagina niet
beschikbaar → Oplossing bekijken → Websitecontrole aanvragen → bevestigen).
Google staat één aanvraag per 12 uur toe. 17 sept: 26 producten.

---

## Rankingmeting 16 september — SC-posities zijn moduleposities

(Overgenomen op 22 sept van de tak docs/rankingmeting-wekelijks, die nooit is
doorgevoerd.) Peter wil de ranking weer oppakken. Gemeten (SC 3 maanden,
1.000 rijen + tien zoekwoorden live): 52% van alle vertoningen staat op
positie 1-3 met 0,6% klikkans; dat is Googles blok "Vergelijkingssites" uit
onze MC-feed, geen blauwe link. Organisch: **1 van 10 modelcodes in de top
18** (Bosch SMV4EMX01N op 16), ook bij MediaMarkt-huismerken (Koenic, OK) met
weinig concurrentie. Titels/omschrijvingen verbeteren helpt daar niet; het
ontbreekt aan domeingezag (links) en aan vergelijkingswaarde bij
één-winkel-apparaten. Afgesproken: (1) wekelijkse live meting
(`docs/RANKING-METING.md`, dinsdag), (2) links: Peter doet dit zelf met
Claude, per e-mail; kansrijkste idee is onze eigen prijsdata als "linkbare"
publicatie (sinds 17 sept live: /onderzoek/prijsverschillen-witgoed), (3)
vergelijkingswaarde: loopt (Coolblue-feed, Witgoedhuis, De'Longhi, AEG).
Nieuwe concurrenten gezien: vergelijk.nl, beslist.nl, VergelijkEven.nl,
supersales.nl.

---

## Dagcontrole 16 september — eerste TradeTracker-verkoop

- **Eerste verkoop via TradeTracker ooit:** 16 sept 10:56, Voordeligwitgoed,
  AEG AB81A2DG stofzuiger (EAN 7333394018447), bestelbedrag EUR 189,26 excl.
  btw (EUR 229 in de winkel), commissie EUR 4,73 (2,5%), onder beoordeling.
  Voordeligwitgoed was bij ons de goedkoopste: 229 tegen Bol/Coolblue 272,
  Expert 309, EP 399,95 -- de vergelijking deed precies waar hij voor is.
  TradeTracker telde vandaag 4 unieke kliks; onze eigen teller ook (2
  Voordeligwitgoed + 2 EP). Juli was 894 kliks/0 verkopen (robots).
  **TradeTracker is bereikbaar via Peters Chrome** (affiliate.tradetracker.com,
  ingelogd): Rapportage → Transacties → Salestransacties; kolom "Referentie"
  is onze EAN (`affiliate_ref.py`, `&r=EAN`). Product opzoeken op EAN:
  `railway run -s Postgres python <script>` (zie zoek_ean.py in de sessie).
- **Coolblue blijft 1.425.** Dekking 39%, leverbaar 2.929, feed groeit mee.
- **Merchant Center:** niet goedgekeurd 116 waarvan 101 verborgen → 15 van
  ons (gisteren 7; 5 "wordt beoordeeld"). Koelvries-melding 198.
  Morgen kijken of die 15 weer zakken.
- **Search Console per dag:** 12 sep 307, **13 sep 324** vertoningen (5
  klikken). De daling is gestopt rond 300/dag; nog geen herstel richting
  de 1.000+ van 4-7 sept. Blijven volgen.
- **"Kan niet worden bereikt":** 12 sep 27, 13 sep 25, **14 sep 19**, 15 sep 3
  (niet compleet). Houdt aan. Eigen proef 15 sept (345 pogingen, elke 20 s,
  2 uur, vanaf Peters pc): **0 mislukt**, gemiddeld 0,28 s, max 0,54 s.
  Vanuit Nederland is er niets te zien; het zit tussen Google (VS) en
  Railway (US West). Externe meter blijft de keuze van Peter.
- Overige meetpagina's schoon: prijssprongen 1/0 teruggesprongen, teksten
  wachtrij 0, EPREL draait (1.253 gevonden), Daisycon nog 0 (wachten tot
  18 sept), foto's 4 zonder (bekend).

---

## Dagcontrole 15 september — Coolblue live, MC schoon, onbereikbaar houdt aan

- **Coolblue-feed 96636 werkt:** ronde van 15 sept 06:13 UTC: 16.459 regels,
  1.425 gekoppeld, 2 nieuw, 36 overgeslagen. Aanbiedingen 1.125 → **1.425**,
  Merchant-feed 2.706 → **2.906 items**, leverbaar 2.709 → 2.910. Dekking
  blijft 39% (de nieuwe Coolblue-prijzen zitten vooral bij apparaten die
  al één andere winkel hadden of nog geen enkele: `enige_winkel_bij` 586 →
  742). Peter heeft Coolblue bevestigd.
- **Merchant Center:** na de websitecontrole van 14 sept: niet goedgekeurd
  146 → **108, waarvan 101 verborgen** (Google's eigen vondsten). Echt van
  ons nog 7 (was 34). Producten 3,07K, goedgekeurd 2,96K.
  Koelvries-melding 207 (was 168; groeit mee met de feed).
- **"Kan niet worden bereikt" houdt aan:** 12 sep 27, **13 sep 25**, 14 sep
  4 (nog niet compleet). Reeks sinds 9 sept: 5, 11, 10, 27, 25. Dus geen
  eenmalige uitschieter. Eigen proef vanaf Peters pc (elke 20 s, 2 uur,
  15 sept vanaf 12:05 UTC): zie proef.log in de sessie; tussenstand 0
  mislukt. Volgende stap ligt bij Peter: externe meter (gratis, eigen
  account) — Railway-forum levert niets op.
- **Search Console per dag (het cijfer achter de "daling"):** vóór 29 aug
  20-60 vertoningen per dag op positie 40-50. Vanaf 29 aug (dag na de
  MC-vrijgave) positie 3-9 en honderden vertoningen: 4-7 sept piek 1.134 /
  1.383 / **1.497** / 1.092, daarna 786, 495, 673, 649, 307 (12 sept,
  mogelijk nog niet compleet). Klikken 11/18/22/10, daarna 7, 3, 1, 6, 4.
  Dat zijn productvermeldingen in Google Zoeken (positie 1-9, geen gewone
  blauwe links). De piek zakt, maar het niveau is nog 10x dat van augustus.
  Of de 28 afkeuringen en de onbereikbaarheid de daling veroorzaakten is
  niet te bewijzen; nu de 28 weg zijn: **volgen of de vertoningen
  terugkomen.** Tabblad DAGEN uitlezen: navigeer naar
  `.../search-analytics?...&num_of_days=28&breakdown=date`, scroll, en lees
  `document.querySelectorAll('table')` — klikken op tabbladen werkt niet
  betrouwbaar vanuit de Chrome-tool.
- Indexering ongewijzigd (9/17/72/62/45/10/1/1/1.241; geïndexeerd 2.839).
- Daisycon/Witgoedhuis: Peter wacht tot 18 sept (tien werkdagen).

---

## Dagcontrole 14 september (ochtend) — uitkomsten en twee nieuwe dingen

Alle tien routines draaien, prijssprongen 1 (omhoog, niet teruggesprongen),
teksten wachtrij 0 met sleutel, EPREL in onderhoudsstand zonder afbreking,
Daisycon Witgoedhuis nog `X-Total-Count: 0`, kenmerkpagina's 200, home 0,3 s.
Bekend en ongewijzigd: EP `niet_ververst_3d` 584 (feedselectie), Bol 315.

**Merchant Center** (overzicht, authuser=5): 2,88K producten, 2,73K
goedgekeurd (-236 in 7 dagen: dat is de EP-reparatie van 10 sept, de feed
kromp van ~2,9K naar 2.706), **146 niet goedgekeurd waarvan 118 verborgen**
(= de "Gevonden door Google"-producten met "prijs ontbreekt"; verborgen
sinds 4 sept, staan er nog wel als getal). Echt van ons: **28 "productpagina
niet beschikbaar"** (1 → 6 → 22 → 28 sinds eind aug) + 6 "availability
ontbreekt". Alle 5 zichtbare voorbeelden staan in onze feed (in_stock) en
geven als AdsBot 200 in 0,3 s. Shopping 28 dagen: 77 productklikken, 3,43K
vertoningen, CTR 2,2%; per dag piek ~18 op 6 sept, sinds 10 sept 3-5.
Melding koelvriescombinaties: 168 (was 164).

**Search Console** (/u/5/): geïndexeerd 2,84K. Serverfout 5xx 9 (validatie
gestart 17 aug, MISLUKT 5 sept) — en dat zijn **géén %-adressen** meer maar
gewone productpagina's, laatst gezien 24 aug t/m 2 sep (Bosch SMS6ZCI11F,
Roborock Qrevo Edge, Samsung RS70F65QEFEF, ...). Alle 9 geven nu 200.
Niets nieuws na 2 sept. Verder: 404 45 (was 39), noindex 72 (verdwenen
producten en kleine merkpagina's, laatste 2 sept; klopt), "gecrawld – niet
geïndexeerd" 17 (was 11), "gevonden – niet geïndexeerd" 1.241 (loopt).
`/%-` geeft vandaag weer **502** (3 van 3), niet 404 zoals op 10 sept
gemeten; 5xx-validatie dus NIET herstarten.

**Doorklikratio (de half-septembermeting):** 28 dagen 104 klikken, 11K
vertoningen, CTR 0,9%, positie 6,3; 3 maanden 185 / 15,6K / 1,2% / 10,6.
Dus: 70% van alle vertoningen van het kwartaal viel in de laatste 28 dagen,
positie fors beter, maar de klikken groeien langzamer dan de vertoningen.
Niet één op één met de 1,96% van 25 aug (die gold voor modelcode-zoekwoorden
op productpagina's); volgende keer op dezelfde manier meten (tabblad
ZOEKOPDRACHTEN, modelcodes apart).

**Uitgezocht dezelfde middag (14 sept) — wat het WEL en NIET is:**

Google's crawlstatistieken (Search Console → Instellingen → Crawlstatistieken
→ host www → rij "De pagina kan niet worden bereikt") zijn de bron met
tijdstippen. Uitkomst:
- **208 mislukte ophaalpogingen in 90 dagen**, sinds 11 juli, gemiddeld 2-3
  per dag met uitschieters: 12 jul 22, 31 aug 17, 2 sep 15, **12 sep 27**.
  Op ~450 crawls per dag is dat ~0,5%. Het is dus **niet nieuw**; Merchant
  Center laat het pas zien sinds AdsBot na 28 aug de landingspagina's
  controleert (Bosch PKF611BB2E: 12 sep 12:22 in de SC-lijst, dezelfde dag
  afgekeurd in MC).
- De 9 "Serverfout 5xx" in SC zijn in de crawlstatistieken **allemaal oude
  %-adressen** (laatste 22 aug 03:06) -- de bekende Railway-edge-502, niet
  de app.
- **Uitgesloten:** de uitrollen (5 van de 58 momenten vallen binnen een
  uitrol-kwartier), de syncs (12 van 58 binnen een job, Bol-sync duurt
  10-12 min en loopt 4x per dag: te weinig overlap), worker-time-outs (geen
  enkele `WORKER TIMEOUT` in 16 uitrollen sinds 4 sept), crashes (één
  "Starting Container" per uitrol), CPU (max 0,01 vCPU), geheugen (max
  1,06 GB van 8), DNS (TransIP, geen AAAA, www CNAME naar Railway), IPv6
  (geen records), certificaat, en Railway's eigen storingen (september 100%).
- **Railway zag niets:** `railway metrics --since 7d --raw --json` geeft 0
  5xx buiten mijn eigen twee testfouten (8 sep 13:00 en 13 sep 11:00 UTC,
  de 429 van Tradedoubler en de `t()`-macro), p99 meestal < 1,5 s, één uur
  5,1 s (10 sep 15:00 UTC). Wat Google niet kon bereiken, is dus nooit bij
  de app aangekomen: het strandt vóór de app, bij Railway's edge/netwerk of
  onderweg. Dat is met onze middelen niet verder te meten.
- 60 snelle proeven vanaf hier: 60 van 60 goed.
- Wél gezien: de site draait in **US West (Californië)**, niet in Amsterdam.
  Voor Nederlandse bezoekers scheelt dat ~150 ms per pagina. Postgres staat
  in hetzelfde project; verhuizen moet dan samen. Los punt, geen oorzaak.

**Wat er nog kan (beslissing Peter):**
1. Merchant Center → probleem "Productpagina niet beschikbaar" → knop
   **"Websitecontrole aanvragen"**: Google controleert de 28 opnieuw; alle
   28 geven nu 200. Kost geen beoordelingspoging (het is een crawl, geen
   beleidsbeoordeling). Niet zelf geklikt.
2. Vraag bij Railway (station.railway.com) met de 58 tijdstippen: "zien
   jullie edge-fouten voor service db27c6e1 in US West op deze momenten?"
   Tekst staat klaar in "Bevindingen 14 september.txt" op het bureaublad.
3. Externe bereikbaarheidsmeting (UptimeRobot of Better Stack, gratis, elke
   minuut vanuit meerdere landen): dan hebben we eigen bewijs in plaats van
   alleen Google's lijst. Account aanmaken moet Peter zelf doen.
4. Regio naar EU West (Amsterdam) verhuizen: geen oorzaak van dit
   probleem, wel sneller voor bezoekers; app én Postgres samen.

Railway-logs: `-f "@httpStatus:..."` werkt NIET (geeft altijd 0), een los
woord als `-f 404` wel. Oude uitrollen: deploy-logs zijn ~7 dagen leesbaar
(`railway logs <deployment-id> -d --json -n 20000`), HTTP-logs alleen van de
lopende uitrol. `railway metrics --since 7d --raw --json` is de betere bron.

---

## Update 14 september — kenmerkpagina's, voorpagina, crawlbudget (12-14 sept)

**Twaalf kenmerkpagina's op de zoekzin** (Peters idee, 13 sept):
`zoekkenmerken.py` + route `/category/<slug>/kenmerk/<k>`. Kop = de
zoekzin ("Droger met stoomfunctie: minder strijkwerk"), twee alinea's
uitleg met de nadelen, apparaten op prijs, bij de droger de Coolblue-video.
Herkenning op titel + specificaties (winkeltekst alleen waar dat
betrouwbaar is), ontkenningen tellen niet. Alle twaalf in
sitemap-kenmerken.xml en als eerste (oranje) knopje in de linkrij van de
categoriepagina. Aantallen: stoomdroger 17, no-frost 243, inbouw vaatwasser
52, wasmachine stoom 119, volautomaat 217, dweil 90, steel 85, robot 69,
airfryer 116, inbouwoven 77, combimagnetron 72, amerikaans 59. Teksten ook
in "Teksten kenmerkpaginas.txt" op Peters bureaublad. **Rond 11 oktober in
Search Console beoordelen: wat geen vertoningen krijgt, gaat weg.**
Valkuil: een macro uit _macros.html met `t()` erin importeer je `with
context`, anders 500 (gebeurd bij de video).

**Voorpagina** (12 sept): kop "Vind de laagste prijs voor witgoed,
stofzuigers en koffiemachines", tekst noemt de categorieën, zoekbalk iets
lager, paginatitel en Engelse versie mee (translations.py).

**Merchant Center** (11 sept): feitenzin met afmetingen en kleur achter de
feedbeschrijving (`afmetingen.py`), 1.123 van 2.720 items; melding
"Beschrijvingen voor koelvriescombinaties" volgen.

**De 1.241 "gevonden, niet geïndexeerd" ontleed** (14 sept, Search Console
voorbeeldtabel van 1.000): 635 producten (18% bestaat niet meer), 264
merkpagina's per categorie, 53 winkelpagina's, 41 overige facetten, en de
categoriepagina's /category/drogers en /category/stofzuigers zelf
(stofzuigers: "laatste crawl n.v.t."). Dus ~650 producten, niet 1.241.
Technisch is alles goed; het is Googles prioritering. Gedaan:
- indexering aangevraagd voor beide categoriepagina's (14 sept, beide "in
  prioriteitscrawlwachtrij"); over 1-2 weken nakijken;
- merkpagina's per categorie alleen nog in sitemap/linkrij vanaf 8
  producten (311 -> 109), winkelpagina's per categorie eruit (63 -> 0,
  schakelaar `winkelpaginas_in_sitemap` in routes/seo.py). Routes blijven
  werken.
Search Console bedienen: het zoekvak reageert niet op getypte tekst vanuit
de Chrome-tool; zet de waarde in JS (value-setter + input-event + Enter
KeyboardEvent) en klik knoppen op coördinaten.

**Coolblue-feed (14 sept, middag):** Coolblue (Michiel Croes) antwoordde op
case 03161140: de prijsvergelijkersfeed 95930 wordt "geremd", overstappen op
"NL full feed (alle producten)" = Awin-feed 96636. Gedaan in
`sync_coolblue.py`: streepjescode uit `upc` (soms meerdere per regel,
komma's), koppelen op de eerste code die al in de catalogus staat.
Leesproef op productie vóór de merge: 1.488 apparaten in plaats van 1.127,
1.484 koppelen aan bestaande producten, 4 nieuw; wasmachines 69 → 139,
koelkasten 86 → 271, drogers 21 → 75. Coolblue wil een bevestiging zodra
het live is.

**Nog open, buiten de deur:** TradeTracker/EP (volledige feed, mail 10
sept), Witgoedhuis (Daisycon-aanmelding 4 sept, ticket 8 sept,
mail 10 sept; feed geeft nog 204/0). Shopping-klikken zakten van 18/dag
(6 sept) naar ~1-4; geen verklaring, dagelijks volgen.

---

## Update 12 september — de week van de tellers en de feeds (7-12 sept)

Kort: de cijfers waar we op stuurden bleken op drie plekken niet te
kloppen, en alle drie zijn gerepareerd. Daarnaast de eerste echte verkopen,
en drie verzoeken die buiten de deur liggen.

**Eerste verkopen.** Awin: 1-9 september 67 klikken, **3 transacties,
EUR 143,83** in afwachting (augustus dezelfde dagen: 5 klikken, 0). Dat is
het cijfer waar de site op stuurt. Shopping-klikken piekten op 6 sept (18
per dag) en zakten daarna naar ~1; oorzaak onbekend, dagelijks volgen.

**Teller 1 — doorkliks (2-5 sept).** Robots klikten op alle winkelknoppen.
`/uit/...` weigert nu (403) verzoeken van robots, vooruit-ophalers en
adressen die los worden opgevraagd (`Sec-Fetch-Site: none`). Echte
doorkliks: 5-16 per dag. `pageviews.bron()` heeft de logica.

**Teller 2 — productpaginaweergaven (8 sept).** Zelfde ziekte: 577
weergaven op 9 sept waarvan 336 los opgevraagd en 49 zonder browserkoppen.
Echte mensen ~190 per dag. Bakjes `product-browser`, `product-van-elders`,
`product-los-adres`, `product-geen-secfetch` in `/api/sync-status`; niets
wordt geweigerd. Uit de Railway HTTP-logs (`railway logs --http --json`):
de "browser"-verzoeken komen van huurservers (Tencent Cloud met een
iOS-13-iPhone-naam, DigitalOcean, AWS); Google is de grootste lezer.
Besluit over weigeren pas na een week meten.

**Teller 3 — winkeldekking en "laagste prijs" (10 sept, de ernstigste).**
EP's TradeTracker-feed levert sinds begin augustus nog 373 van de 980
EP-aanbiedingen (nu een selectie: Liebherr, Miele, inbouw, Exclusiv, tv's).
De veiligheidsklep hield de rest terecht vast maar liet ze als leverbaar
staan: **572 EP-prijzen van eind juli, bij 326 apparaten als laagste prijs
getoond.** Reparatie: `verouderde_aanbiedingen.py` -- een aanbieding die
langer dan drie dagen niet is ververst wordt niet-leverbaar (rij blijft,
komt vanzelf terug). Dekking zakte daardoor eerlijk van 45% naar 38%.
Bovendien: de klep schreef alleen naar de serverlogs; nu ook naar
`sync_log.errors`, en `/api/sync-status` toont per winkel
`niet_ververst_3d`. Coolblue had 363 "zombie"-aanbiedingen die
`_backfill_offers_from_products` (app.py) bij elke deploy opnieuw aanmaakte;
die routine doet nu alleen nog oude Bol-producten.

**Feeds (buiten de deur, drie verzoeken lopen):**
- TradeTracker/EP: mail 10 sept naar affiliate.support.nl@tradetracker.com
  (feed 1944992, affiliate 512985) om de volledige feed. Geen antwoord nog.
- Awin/Coolblue: case 03161140, 11 sept doorgezet naar accountmanager Mike
  Kramer (Coolblue's Awin-feed mist producten die Coolblue wel verkoopt).
- Witgoedhuis (achtste winkel via Daisycon, programma 6570, medium 428244):
  aanmelding 4 sept, Daisycon-ticket 8 sept, directe mail 10 sept. Feed
  geeft nog 204/0. Zodra er producten komen: offers-only sync op EAN bouwen
  naar het recept van Voordeligwitgoed (velden staan in het chatgeheugen).

**Ook deze week:** MediaMarkt herkent nu titels zonder soortwoord
(tafelmodel, pistonmachine, kruimelzuiger; +38 en +33 apparaten);
`/api/feed-velden/<winkel>` meet wat er bij de voordeur blijft liggen (bij
Coolblue niets -- niet opnieuw onderzoeken) en haalt de feed hooguit een
keer per half uur op (herhaald aanroepen gaf een 429 bij Tradedoubler);
feedbeschrijvingen kregen een feitenzin met afmetingen en kleur
(`afmetingen.py`, 1.123 van 2.720 items) op verzoek van Merchant Center;
voorpagina-kop verbreed naar "witgoed, stofzuigers en koffiemachines".

**Concurrentiemeting 8 sept (wekelijks herhalen, dezelfde vijf
apparaten):** organisch staan wij bij 0 van 5 in de top 30; Tweakers,
Kieskeurig, Knibble en Consumentenbond wel. Bij 2 van 4 lag onze "laagste
prijs" EUR 200 boven de markt -- dat was deels teller 3. Structureel:
Kieskeurig/Tweakers laten winkels per klik betalen, dus elke winkel doet
mee; wij hangen aan affiliatenetwerken. Mail aan winkels zonder programma
staat klaar op Peters bureaublad, versturen zodra Witgoedhuis live is.

**Gereedschap dat er nu is:** Railway CLI is gekoppeld (project
artistic-motivation, service witgoed-aanbod): `railway logs` voor
tracebacks, `railway logs --http --json` voor verzoeken, en
`railway run -s Postgres python <script>` om de productiedatabase te
lezen (DATABASE_PUBLIC_URL). Alleen lezen. Nooit affiliate-links volgen in
tests: dat telt als klik bij het netwerk (5 EP-klikken op 10 sept waren van
ons).

---

## Update 1 september — Merchant Center vrij, en waar de klikken vandaan komen

### Twee dingen die de werkwijze veranderen

**1. Search Console IS toegankelijk.** In alle eerdere overdrachten stond
dat het geblokkeerd was en dat Peter schermafdrukken moest sturen. Dat
klopte niet: het was hetzelfde accountnummer-probleem als bij Merchant
Center. Werkende URL:

    https://search.google.com/u/5/search-console?resource_id=sc-domain:witgoedaanbod.nl

Met `/u/0/` verschijnt "Je hebt geen toegang tot deze property" — dat is
misleidend, de property bestaat wel. **Vraag Peter dus geen schermafdrukken
meer van Search Console of Merchant Center; meet zelf.** Prestaties per
pagina uitlezen: dezelfde basis-URL met
`/performance/search-analytics?...&breakdown=page&num_of_months=3`, dan in
de pagina op het tabblad PAGINA'S klikken (via javascript_tool het element
met innerText "PAGINA'S" zoeken en aanklikken) en de tabel uitlezen met
`document.querySelectorAll('tr')`. Levert tot 1.000 rijen.

**2. Een supportvraag stellen kost geen beoordelingspoging.** Dat is wat de
Merchant Center-blokkade heeft opgelost. Onthoud die volgorde: eerst
vragen, dan pas een formele beoordeling aanvragen.

### Merchant Center: OPGELOST na 25 dagen

Op 28 augustus zijn **beide accountblokkades opgeheven**. Geen banner meer,
en onder Producten → Vereist aandacht staat "Al uw oplossingen met
prioriteit zijn afgerond". Stand: 2,92K producten, vrijwel alles
goedgekeurd.

Wat de doorslag gaf: op 23 augustus is een **supportvraag** ingediend (via
het vraagteken in MC → Contact opnemen, categorie Overig, schending
"Niet-werkende landingspagina", antwoord per e-mail) in plaats van een
derde beoordeling. Google hief binnen twee dagen de landingspagina-blokkade
op en bedankte expliciet voor "de gedetailleerde context over de inrichting
van uw website als prijsvergelijkingsplatform" — onderbouwd met eigen
metingen (alle 2.903 feedlinks plus 996 interne links, allemaal 200,
mediaan 0,25 s, gemeten als AdsBot-Google).

**De laatste beoordelingspoging is nooit gebruikt en blijft beschikbaar.**

**Belangrijke correctie voor het archief:** op 23 augustus concludeerden
drie AI-modellen unaniem dat een affiliate-vergelijker zonder eigen
checkout hier per definitie niet mag zijn zonder CSS-status (50
winkeldomeinen vereist, wij hebben er zeven). Dat bleek NIET te kloppen —
Google heeft het model geaccepteerd zoals het is. Wees voorzichtig met dat
argument; unanieme modellen kunnen samen ongelijk hebben.

### Het eerste harde resultaat: 31 augustus

| Dag | Shopping-vertoningen | Klikken |
|---|---|---|
| 4 t/m 30 aug | minder dan 20 per dag | 0 |
| **31 aug** | **1.050** | **11** |

Doorkliks naar de winkel via dit kanaal: 13 (+160%). Twee mogelijke
oorzaken die niet te scheiden zijn: het account werd 28 aug vrijgegeven, en
op 31 aug om 07:00 haalde Google voor het eerst de feed op mét
`google_product_category`, `mpn` en `product_type` (PR #129).
**Volg dagelijks of dit doorzet** — MC → Analytics → Producten → Verkeer,
tabblad Datum.

### Waar de klikken vandaan komen (gemeten 25 aug, 3 maanden SC-data)

Dit is de belangrijkste meting van deze periode.

| Soort pagina | Pagina's met vertoningen | Klikken | Vertoningen |
|---|---|---|---|
| Productpagina's | 950 | **81** | 4.143 |
| Categoriepagina's | 12 | 1 | 232 |
| Koopgidsen/blog | 12 | **0** | 167 |
| Homepage | 1 | 7 | 80 |
| Alle 552 filterpagina's samen | 19 | **0** | 99 |

En per zoekterm:

| Zoektype | Termen | Klikken | Gem. positie |
|---|---|---|---|
| Modelcodes ("smv4emx01n") | 787 | **22** | 29 |
| Gewone woorden ("vaatwasser") | 213 | **1** | 38 |

**Drie conclusies, alle drie met cijfers onderbouwd:**

1. **Meer filterpagina's bouwen heeft geen zin.** Van de 552 die er staan
   krijgen er 19 überhaupt een vertoning, samen nul klikken. Het plan
   "Slimster heeft er 57 voor wasmachines, wij moeten er meer" is van tafel.
2. **Op generieke woorden zijn we kansloos**, en dat hoeft geen onderzoek
   meer: "witgoed kopen" staat op positie 105,8, "vaatwasser" op 76. Dat
   verklaart de koopgidsen definitief.
3. **De modelcode is het enige zoekwoord dat telt** — en daar staan we op
   pagina 1 (mediane positie 8) met een doorklikratio van slechts **1,96%**,
   waar 3 tot 8% normaal is. Dat is de hefboom, niet meer pagina's.

Er is GEEN meetbaar verschil tussen productpagina's die wel en niet vertoond
worden (steekproef 200: winkelaantal, specificaties, EPREL, prijsgrafiek,
metalengte, paginagrootte — alles gelijk). Crawldiepte leek te verklaren
(38% tegen 18%) maar viel bij 200 pagina's weg naar 39% tegen 29%,
chi-kwadraat 1,45: niet significant. Het is Googles crawlbudget op een jong
domein, geen kwaliteitsprobleem.

### Wat er gebouwd is (PR #119 t/m #131)

Gericht op die doorklikratio en op wat Google leest:

- **#124 klikwaardige titels** — het soort apparaat achter de modelcode
  ("Bosch SMV4EMX01N vaatwasser"), en het fragment zegt niet langer
  "goedkoper dan 88 van de 232" bij apparaten in de duurdere helft: een
  zoeker rekent dat andersom.
- **#125 modelcodes met een spatie** — Miele "DGC 7151", Liebherr
  "IRd 4100-62", Whirlpool "WPM 966W" werden nooit herkend. 28 extra
  herkenningen op 300 titels, nul valse treffers.
- **#127 structured data** — het webadres klopte bij 15% niet (kale plus in
  plaats van %2B), en `mpn` ontbrak volledig.
- **#126 oude productadressen** — 6% van alle crawls liep op een 404 omdat
  slugs meeveranderen met feedtitels. Nu 301 naar het huidige adres via de
  EAN achterin de slug.
- **#129 feed** — `google_product_category` (Googles taxonomie), `mpn` en
  `product_type`. De feed vertelde nergens WAT een product was; MC toonde
  "Onbekend" bij Categorieën.
- **#120 cookiebalk mobiel** van 31% naar 19% van het scherm.
- **#121 vertrouwenscijfers homepage** (live uit de database) en /over-ons
  dat expliciet zegt: vergelijker, geen webwinkel.
- **#122 deelplaatje** — og:image bestond NIET (404), dus gedeelde links
  hadden geen plaatje. Plus een logo voor Trustpilot; script staat in
  `scripts/maak_beeldmateriaal.py`.
- **#123 Trustpilot-link** in de voettekst; profiel geclaimd op
  nl.trustpilot.com/review/witgoedaanbod.nl (gratis plan).
- **#119 MediaMarkt-prijzen** — de sync nam blind regel [0] uit
  priceHistory; nu de regel met de nieuwste datum. Bij een sprong komt de
  ruwe feedprijs in het synclogboek.
- **#128 teruggeroepen Rowenta's** — drie X-Force Flex 14.60 uit de
  catalogus; de accu kan brand veroorzaken (CPSC-recall). Aparte lijst
  `TERUGGEROEPEN_EANS` in catalogus_uitzonderingen.py.
- **#130 terugsprong-venster** — een sprong telde als "teruggesprongen"
  zodra die prijs OOIT eerder gold; nu alleen binnen twee dagen.
- **#131 spamfilter contactformulier** — geen Nederlands woord ÉN vraagt om
  iets wat wij niet hebben (newsletter, backlinks). Beide voorwaarden
  tegelijk, anders sneuvelt een echte Engelse vraag over een wasmachine.

### Nieuwe valkuilen — allemaal deze periode zelf gemaakt

**Een verklaring geven vóór je hem hebt gemeten.** Toen zes producten
"pagina niet beschikbaar" kregen, verklaarde ik dat met "dat was tijdens een
uitrol". Daarna bleek de laatste merge twintig uur eerder te zijn geweest.
Meet eerst, verklaar daarna.

**Een steekproef van 100 kan liegen.** Crawldiepte leek het verschil te
verklaren (38% tegen 18%). Bij 200 pagina's viel het weg. Verdubbel de
steekproef vóór je een conclusie hardop uitspreekt.

**Een alarm dat altijd afgaat, wordt genegeerd.** De prijssprongenmeting
stond op 9 van 9 "teruggesprongen" terwijl geen enkele een feedfout was.
Dan mist hij juist waar hij voor gebouwd is.

**Getallen uit je hoofd zijn geen bron.** Ik noemde "binnen 28 dagen" voor
een Search Console-validatie; dat getal staat nergens in Googles
documentatie (die zegt "ongeveer twee weken, soms langer"). Peter vroeg
ernaar en het klopte niet.

**Drie modellen kunnen samen ongelijk hebben.** Zie de Merchant
Center-correctie hierboven.

### Wat er NU loopt (niets aan doen, wel volgen)

1. **Shopping-vertoningen** — zetten die 1.050 van 31 aug door? Dagelijks
   kijken.
2. **Doorklikratio organisch** — nu 1,96%; half september opnieuw meten.
   Google moet de nieuwe titels eerst opnieuw ophalen.
3. **Railway 502** — adressen met een kaal procentteken geven nog steeds
   502. Supportmelding staat sinds 19 aug op
   station.railway.com/questions/edge-proxy-returns-502-for-paths-with-in-b2af4436
   Eén reactie uit de gemeenschap, niets van het team zelf. Meetcommando:
   `curl -o /dev/null -w "%{http_code}" https://www.witgoedaanbod.nl/%-`
4. **1.243 onontdekte pagina's** — validatie loopt sinds 4 aug, nog geen
   enkele gecrawld. Rekenkundig 45 dagen op basis van Googles
   crawlstatistieken (264 crawls per dag, 15% ontdekking, 68% HTML), dus
   half oktober. NIET opnieuw valideren.
5. **"Gecrawld – niet geïndexeerd" validatie MISLUKT** (29 aug, 11
   pagina's). Nagekeken: die pagina's geven 200, staan in de sitemap en
   hebben een eigen tekst. Geen fout, wel Googles oordeel. Niet opnieuw
   valideren.
6. **Zes "productpagina niet beschikbaar"** in MC. Alle 2.893 feedlinks
   getest als AdsBot-Google: allemaal 200. Loos alarm, maar neem het getal
   dagelijks mee — loopt het op naar dertig, dan is er een patroon en moet
   de sync uit het webproces (de planner draait nu in dezelfde gunicorn-
   worker als de site).

### Wat bewust NIET gedaan wordt

- **Geen nieuwe filterpagina's en geen nieuwe koopgidsen** (met cijfers
  onderbouwd, zie hierboven).
- **Geen Cloudflare** voor de 502's. Op 23 aug voorgesteld toen ik dacht dat
  die negen adressen het MC-account blokkeerden; dat bleek niet zo. Het
  risico (verouderde prijzen door caching, botbescherming die Google
  buitensluit) weegt niet op tegen negen dode adressen.
- **Geen Google Mijn Bedrijf koppelen aan Trustpilot** — dat haalt het
  winkelprofiel van Avantius binnen en herstelt precies de
  tegenstrijdigheid die op /over-ons is opgeruimd.
- **Geen TrustBox-widget, geen Google Tag Manager** — extern JavaScript, en
  de widgets zijn vergrendeld in het gratis plan.
- **Geen verzend- en retourbeleid invullen in MC** (Winkelkwaliteit toont
  daardoor "Geen score"). Het retourvenster van 14 dagen is bewust zo
  gelaten: vier van de zeven winkels geven niet meer.
- **Model blijft claude-opus-5** voor de productteksten. Haiku bespaart
  ongeveer 29 euro per jaar; die teksten brachten "Gecrawld – niet
  geïndexeerd" van 100 naar 4 en dat risico is die besparing niet waard.
  Automatisch aanvullen van het Anthropic-saldo staat sinds 24 aug aan.

---

## Update 19 augustus — de Merchant Center-week (13-19 aug)

### Waar het NU op wacht (niets aan doen, wel dagelijks volgen)

1. **Twee accountbeoordelingen in Merchant Center lopen**: "Landingspagina
   werkt niet" (aangevraagd 13 aug) en "Verkeerde voorstelling"
   (aangevraagd 16 aug — dit is **poging 2 van 3**; na een afwijzing rest
   1 poging en daarna extern bezwaar, Routing ID RDAX, Reference
   5829468803). De tweede wordt pas verwerkt ná de identiteitsverificatie.
2. **Identiteitsverificatie ingediend 16 aug** via het betalingsprofiel
   (geen betaalgegevens): Avantius VOF met gewaarmerkt KvK-uittreksel
   (dec 2025) + paspoort van Peter via de KopieID-app. LET OP: Googles
   fotocontrole wees de A4-KopieID-pdf af (document te klein in beeld);
   opgelost met een beeldvullende uitsnede (Downloads\Kopie paspoort
   16 aug 2026 - uitsnede.png). Naam exact als paspoort: Petrus Frederik
   Martinus Homan. Uitslagen komen per e-mail: Peter stuurt schermafdrukken.
3. **Search Console-validaties**: de grote (1.147 "Gevonden – niet
   geïndexeerd", loopt sinds 4 aug) en een mini (5 "Gecrawld – niet
   geïndexeerd", herstart 17 aug — daarin zitten 2 kóópgidsen die Google
   na lezing de index niet waard vond: eerste harde aanwijzing waarom de
   19 gidsen niets opleveren).

### OPENSTAAND — direct oppakken door de nieuwe sessie

- **Serverfout (5xx) in Search Console: validatie MISLUKT, 9 pagina's**
  (was 8). Iets geeft nog steeds serverfouten en er kwam er één bij.
  Vraag Peter om een detailschermafdruk van die rij (de URL-lijst) en
  zoek het dezelfde dag uit. Ook 404 groeide licht (33→39): meenemen.
- **Twee takken wachten op merge door Peter** (vergelijk-links geven):
  `fix/foto-aeg-tr73cb86` (foto voor nieuw fotoloos product, modelnummer
  op bronpagina geverifieerd) en `docs/overdracht-19-augustus` (dit
  document).
- **Na de MC-uitslag**: bij goedkeuring → controleren of vermeldingen
  echt live komen + winkelkwaliteit terugkeert + de crawl-feed ("Feed
  maken op basis van websitecrawl", bij CSS-instellingen) evalueren op
  dubbelingen. Bij afwijzing → "Aanvullende opties" (extern bezwaar) en
  de laatste poging pas na overleg.

### Wat er gebeurd is (13-19 aug), kort

- **13 aug 22:12: poging 1 afgewezen + account opgeschort** met twee
  concrete redenen: kapotte bestemmings-URL's en "frustrerend navigeren".
  Nachtonderzoek: alle 2.830 feedlinks gaven 200 (ook niet-leverbare
  producten blijven 200); de "kapotte pagina's" waren vrijwel zeker een
  deploy-moment of het schermvullende cookievenster.
- **Reparaties (alle live)**: cookiemelding is een balk onderaan geworden
  (designrapport punt 12, versneld; tekst woordelijk gelijk, knoppen
  gelijkwaardig 44px, wegklikken is geen keuze; homepage nu meetbaar),
  feedfoto's via ons EIGEN domein (/fotos/feed/<id>.webp — Coolblue's
  fotoserver coolblue.bynder.com weert álle crawlers, wsrv.nl was de
  tussenstap; de route stuurt met herkenbare User-Agent omdat wsrv kale
  python-requests weigert), en g:certification met EPREL-registratie-
  nummers in de feed (871 producten).
- **Resultaat productniveau**: van 1.005 afgekeurd (12 aug) naar **2**
  (19 aug). 2.840 goedgekeurd.
- **De feed** (/feeds/google-merchant.xml) is 11 aug aangemeld als
  PRODUCTS SOURCE 2, ophalen dagelijks 07:00, eerste run 2.766 producten
  foutloos. Productbescherming staat aan (40%).
- **Foto-vangnet uitgebreid**: FOUTE_FOTOS_WISSEN in icecat.py wist
  bekende foute adressen bij elke sync-ronde (de opstartwis miste er
  onverklaarbaar één). Les vastgelegd: bij handmatige foto's het
  MODELNUMMER op de bronpagina controleren, niet alleen of de foto laadt
  (de GT6200C2SGM kreeg per abuis de foto van de GI6200B1SN; GT staat nu
  bewust fotoloos tot hij weer leverbaar is).

### Cijfers om te onthouden (nulmetingen)

- Doorkliks naar winkels: record **16 op 18 aug** (was 1-6/dag).
  Eén order tot nu toe (Coolblue). Verhouding is normaal; het volume is
  de knop — zie memory doel-doorkliks-niet-vertoningen.
- Search Console 3 maanden: 83 klikken, waarvan **57 via
  productfragmenten** (de gestructureerde data werkt). 2,86K geïndexeerd.
- EP-feed van TradeTracker ververst 1x per etmaal — vaker ophalen dan
  onze 2x/dag is zinloos (gemeten 8-11 aug).

### Werkafspraken erbij sinds 6 augustus (staan ook in memory)

- **Jagen, niet afwachten**: elke afwijking dezelfde dag uitzoeken;
  MC en SC horen bij de dágelijkse controle; concurrentie wekelijks.
- **Duidelijke opdrachten aan Peter**: genummerd, exacte klikroute, en
  wat hij moet terugsturen. Geen "bij gelegenheid".
- **Peters Chrome mag gebruikt worden** (claude-in-chrome):
  merchants.google.com werkt met authuser=5 in de URL (zonder kom je op
  een inlogscherm — daar nooit iets aanraken); search.google.com is nog
  geblokkeerd in de extensie, dus SC gaat via Peters schermafdrukken.
- **Volg nooit /uit/- of Awin-links met een gewone fetch** (telt als
  affiliate-klik); de /uit/-redirect mag wél met een bot-User-Agent
  (pageviews filtert bots).

---

## Update 6 augustus — wat er sinds 1 augustus is gebeurd

### Afgerond en live

- **EPREL is rond:** alle apparaten verwerkt, **1.067 gevonden** (trefkans
  70%). De routine draait door in onderhoudsstand (verversen >30 dagen).
- **99 nieuwe filterpagina's:** 64 winkelpagina's ("Wasmachines bij
  Coolblue", `/category/<cat>/winkel/<code>`) en 35 kenmerkpagina's op
  EPREL-data ("Zeer stille wasmachines", `/category/<cat>/<veld>/<stap>`),
  elk met eigen sitemap-soort en dezelfde ondergrens
  (`_MIN_PER_FILTERPAGINA` = 8) in route, links én sitemap.
  Let op: EPREL levert afmetingen bij koelkasten in **millimeters** en bij
  wasmachines in centimeters — `routes.main._eprel_waarde` corrigeert dat.
- **EPREL-blok op 1.000+ productpagina's** ("Gegevens van het
  energielabel", `eprel_specs.py`): specificaties in gewoon Nederlands,
  badges die naar de kenmerkpagina's linken, en de verplichte
  bronvermelding met registratienummer en ophaaldatum (licentie-eis).
- **Chatbot heet AI-Babbelbot** en zegt op vier plekken dat hij een AI is
  (EU AI-verordening, geldt sinds 2 aug 2026). Niet terugdraaien.
- **8 serverfouten opgelost:** procenttekens uit producttitels kwamen
  letterlijk in webadressen (502). `filter_helpers.product_slug` bouwt nu
  schone adressen; de uurlijkse catalogusroutine herstelt oude gevallen.
- **Search Console-validatie van de 918** "Gevonden – niet geïndexeerd"
  is **gestart op 4 augustus**. Duurt 2-4 weken; niet opnieuw aanvragen.
- **Bezorgkosten gemeten en besloten:** volgorde blijft zoals hij is
  (wisselt maar bij 5 van 1.286 producten; zie /api/bezorgkosten).
  Prijsalert bestond al. Retourvenster blijft 14 dagen (Expert, EP,
  Alternate en Voordeligwitgoed geven niet meer). Niet opnieuw voorstellen.

### Loopt — alleen volgen, niets doen

- **Merchant Center "Verkeerde voorstelling"** (accountbreed, alle
  producten onzichtbaar): beoordeling aangevraagd **4 aug** (poging 1 van
  3) na het vullen van de lege klantenservicegegevens. Op 5 aug verzwaard
  na een handmatige controle. Uitslag ± 11 aug. Als er een
  identiteitsverificatie wordt aangeboden: dat is onze sterkste kaart.
  Extern bezwaar kan later (Routing ID RDAX, Reference ID 5829468803).
  Relativering: Shopping leverde 5 klikken per 28 dagen; Google Zoeken 70+.
- **Winkelkwaliteit in MC staat op "Heel goed"** — nuttig tegenargument.

### Designrapport 6 augustus (pdf: Downloads/witgoed-rapport.pdf, 20 punten)

Doorgevoerd: punt 1 (facettellingen filterpagina's over de gefilterde
set), 5+7+8 (kloppende getallen productpagina; `winkel_opsomming()` in
models.py is dé bron voor winkelaantal en -namen), 16+17+19 (44px-
tikdoelen, 13,5px leesteksten, vaste kaartnotitiehoogte).

**Klaarstaand, nog door te voeren:** tak `fix/filterlade-ruis` (punt 3 —
ruisgroepen zoals "Product gewicht" uit de filterlade;
vergelijk-link: github.com/peterhoman/witgoed-aanbod/compare/main...fix/filterlade-ruis).
Punt 2 was een **vals alarm**: het rapport telde in kale HTML waar
verborgen opties ook in staan — in de browser klopt de "Meer (n)"-knop
precies. Eerst zelf meten dus.

**Nog te doen (klein, veilig):** punt 11 (specgroepen inklappen op
mobiel + energielabelblok vóór de speclijst), 13 (srcset/width/height op
kaartfoto's — grootste snelheidswinst), 14 (YouTube pas na tik),
15 (minify + consolefouten), 18 (carrousel alt="" + scroll-snap),
20 (kopniveaus + aria-labels).

**Wachten tot de validatie klaar is (± eind aug):** punt 12 (cookiebalk
i.p.v. venster — als eerste, hij blokkeert homepage-metingen), 4
(linkwolk ná de resultaten), 6 (vertrokken winkels uit de
prijsgrafiek-legenda), 9 (alertformulier direct na de winkellijst),
10 (h1 typografisch gelaagd).

### Nieuwe valkuilen sinds 1 augustus

- **Een rapport dat kale HTML leest, telt verborgen opties als zichtbaar.**
  Leg elke externe bevinding eerst naast een browser-meting.
- **Chrome vertaalt ook taknamen** ("main" wordt "voornaamst") — niet
  schrikken, niets aan doen.
- **EPREL-geluid bij wasmachines is centrifugegeluid** (72+ dB is normaal);
  "zeer stille wasmachines" bestaat terecht niet als pagina.
- **Er kan een tweede Claude-sessie in dezelfde map draaien** (regel 9
  geldt onverkort): controleer vóór en na elke commit de tak.

### Nieuwe meetadressen

| Adres | Wat het toont |
|---|---|
| `/api/bezorgkosten` | Bezorgkosten per winkel; wisselt de bovenste winkel? |

Doel blijft: **doorkliks en verkopen**, boven Slimster en Knibble komen —
niet vertoningen. De doorklikteller (`pageviews.tel`, soort `uit-<winkel>`)
staat op een handvol per dag; dat is de nulmeting van 6 augustus.

---

De site is **witgoedaanbod.nl**, een Nederlandse prijsvergelijker voor witgoed.
Flask + SQLAlchemy + Jinja2, draait op Railway, main wordt automatisch
uitgerold. Ongeveer 2.825 leverbare producten, prijzen uit **zeven**
winkelfeeds. Eigenaar is Peter Homan (Avantius, Sassenheim).

---

## Werkwijze — deze regels gelden altijd

1. **Nooit naar main pushen.** Werk op een tak, push die, en geef Peter een
   vergelijk-link in de vorm
   `https://github.com/peterhoman/witgoed-aanbod/compare/main...<tak>`.
   Hij voert hem zelf door. De `gh`-opdrachtregel is hier niet beschikbaar.
2. **Verifieer op productie, niet lokaal.** De lokale database bevat een
   handvol voorbeeldproducten; metingen daarop zeggen niets.
3. **Meet voordat je sleutelt.** De duurste les van dit project.
4. **Beweer niets wat de data niet draagt.** Ontbreekt een gegeven, laat het
   onderdeel weg in plaats van te schatten. Kernregel van het hele project.
5. **Leg uit in gewone taal.** Geen git-jargon. Geen webadressen in
   ```bash-blokken: die krijgen een Run-knop en belanden in PowerShell.
6. **Documenten voor Peter als `.txt` op zijn bureaublad.** `.md` opent niet op
   zijn Windows. Bureaublad: `%USERPROFILE%\OneDrive\Bureaublad`.
7. **Niet te veel tegelijk.** Eén ding, laten zien, dan verder.
8. **`noindex` op producten met één winkel is afgewezen** op 26 juli. Niet
   opnieuw voorstellen.
9. **Er kan een tweede Claude-sessie in dezelfde map draaien.** Commit meteen
   op je eigen tak; controleer vóór en ná elke commit
   `git branch --show-current` en `git show --stat HEAD`.
10. **Geef Peter geen webadres alsof hij er iets mee moet.** Meetpagina's roep
    je zelf aan en je vertelt hem de uitkomst.
11. **Meet zelf; vraag alleen een schermafdruk als het echt niet kan.**
    Search Console EN Merchant Center zijn beide toegankelijk via Peters
    Chrome, mits met het juiste accountnummer in de URL — `/u/5/` bij
    Search Console, `authuser=5` bij Merchant Center. Zonder dat nummer
    krijg je een scherm dat suggereert dat je geen toegang hebt; dat is
    misleidend. Railway, TradeTracker en de Anthropic-console zijn nog
    ongetest of onbereikbaar: probeer die desnoods ook eens met een
    accountnummer voordat je aanneemt dat het niet kan. Moet Peter toch
    iets opzoeken, zeg er dan precies bij waar hij moet klikken.
12. **Een meting die "alles goed" zegt, is pas te vertrouwen als je hem één
    keer tegen een andere bron hebt gelegd.** Zie de valkuilen.
13. **Verklaar niets voordat je het hebt gemeten, en verdubbel je
    steekproef voordat je een conclusie hardop uitspreekt.** Beide regels
    komen uit fouten van eind augustus; zie het blok van 1 september.

---

## Waar we nu staan

### Eigen productteksten — draait vanzelf, wachtrij leeg

- Geschreven met Claude (`claude-opus-5`) via de Batch API. De eenmalige batch
  van 27 juli kostte **€ 14,34 voor 2806 teksten**; het totaal staat nu op
  € 16,84. Verbruik daarna: enkele centen per dag.
- De **verkooptekst van de winkel gaat bewust niet mee** de prompt in — een
  model dat die als bron krijgt schrijft hem in eigen woorden na, en dan is het
  nog steeds dubbele inhoud.
- `ai_content.controleer` is een zeef. Er blijven **4 teksten** aangestreept op
  "prijsgeven" los geschreven; marginaal, laten staan.
- `teksten_bijwerken.py` draait elke 6 uur, **herschrijft nooit**, en is
  begrensd door `AI_DAGLIMIET_EURO` (€ 5 per etmaal) en 25 per ronde.
- **Stand 1 augustus: 3.036 teksten, wachtrij 0.**

**`ANTHROPIC_API_KEY` moet in Railway blijven.** Saldo op het Anthropic-account
was op 1 augustus **US$ 23,74**, automatisch herladen staat uit. Bij het huidige
verbruik is dat maanden tot jaren. Raakt het toch op, dan stopt het schrijven
zonder waarschuwing; je merkt het doordat `leverbaar_zonder_tekst` gaat
klimmen. **`AI_BEHEER_SLEUTEL` is verwijderd en dat hoort zo** — die twee
namen lijken op elkaar en doen het tegenovergestelde.

### Zeven winkels

| Winkel | Aanbiedingen | Via |
|---|---|---|
| Coolblue | 1.422 | Awin |
| MediaMarkt | 1.089 | Tradedoubler |
| Expert | 939 | TradeTracker |
| EP | 905 | TradeTracker |
| Bol | 696 | eigen API |
| **Voordeligwitgoed** | **61** | TradeTracker #2932, feed 251845 |
| Alternate | 14 | TradeTracker |

**Dekking: 46%** — bij 1.286 van de 2.825 apparaten valt er echt te
vergelijken.

**Alternate levert maar 14 aanbiedingen en dat is geen storing.** Hun feed
bevat 26.662 producten, maar dat is vrijwel allemaal computers en telefoons.

**Voordeligwitgoed stond wekenlang ten onrechte als "wachten op antwoord" in
de takenlijst.** De campagne was allang geaccepteerd. Controleer bij zulke
punten eerst of er echt iets te wachten valt.

**Alle trackinglinks zijn geverifieerd (1 augustus)** en dragen de tracking tot
bij de winkel: Bol (`Referrer=...1528790`), Coolblue (Awin `clickref`),
MediaMarkt (Tradedoubler), Expert en EP (TradeTracker, code 512985).

### Doorklik naar de winkel — nieuw op 1 augustus

De winkelknoppen wijzen nu naar **`/uit/aanbieding/<id>`** op onze eigen site,
die 302 doorstuurt. `/uit/` staat in `robots.txt` op slot.

**Waarom:** TradeTracker telde in juli **894 kliks en nul verkopen**, terwijl
Google in dezelfde periode zo'n twintig bezoekers stuurde. Dat waren crawlers
die de knoppen volgden. Netwerken beoordelen klikkwaliteit; honderden kliks
zonder conversie is het patroon waarop een account gemarkeerd wordt.

Het levert meteen het cijfer op dat ontbrak: **hoeveel mensen klikken door, en
naar welke winkel** (`pageviews.tel`, soort `uit-<winkel>`). Geen cookie, geen
IP, geen sessie. Bots tellen niet mee.

`robots.txt` wordt nu opgebouwd uit twee lijsten (`_CRAWLERS`,
`_UITGESLOTEN`) in plaats van tien handgeschreven groepen — een groep vergeten
kan niet meer.

### Titels en fragmenten in Google — nieuw op 31 juli

Search Console liet zien dat **vrijwel alle zoekopdrachten modelcodes zijn**
("lg gbbsj10dpy", "gsn36vicg"). Op `lg gbbsj10dpy` stonden 44 vertoningen en
nul klikken.

Oorzaak: `modelnummer()` las alleen `specs['Model']`, leeg bij 74%. Zonder
modelnummer viel de meta-description terug op de volle feedtitel, die het hele
budget opat waardoor de vergelijkende zin wegviel.

Nu drie bronnen: het Model-veld, dan **EprelData.modelnummer**, dan het
typenummer uit de titel (streng patroon, niet bij setjes, in hoofdletters).
`product_specs.zoektitel` maakt de paginatitel; `merknaam()` gebruikt
`canonical_brand` zodat er "LG" staat en niet "Lg".

Resultaat op productie: `LG GBBSJ10DPY | WitgoedAanbod.nl` met *"€ 549,00 bij
MediaMarkt. Goedkoper dan 358 van de 555 andere koelkasten die wij volgen."*

### Prijsbewaking

`/api/prijssprongen` — standaard 7 dagen en 50%, in te stellen met `?dagen=`
en `?drempel=`.

**Het onderscheid dat ertoe doet:** een echte prijsdaling blijft staan, een
feed-fout springt terug. `teruggesprongen` is het getal om op te letten.

Op 1 augustus: **33 sprongen in 24 uur, allemaal omhoog, geen enkele
teruggesprongen** — robotstofzuigers en Dyson, bij meerdere winkels tegelijk.
Dat is een actieperiode die afliep, geen fout.

**Onze code kiest niets verkeerd bij Bol.** `/api/bol-aanbiedingen?ean=` liet
zien dat Bol precies één aanbieding teruggeeft, met alleen prijs en levertijd.

### Prijsversheid bij de prijs

Onder de winkellijst: *"Prijzen opgehaald ruim 3 uur geleden. De prijs bij de
winkel op het moment van bestellen is leidend (voorwaarden)."* Een **tijdsduur
en geen kloktijd**, want de database bewaart naïeve UTC-tijden.

### EPREL — stap 1 en 2 draaien

**De openbare API werkt zonder sleutel**; hij weigert alleen verzoeken zonder
browser-achtige `User-Agent` en `Referer`.

- `eprel.py` — categorie naar productgroep, typenummer uit de titel, bevragen.
- `models.EprelData` — rij per apparaat, ook bij een misser, met `gezocht` om
  "kon niet gezocht worden" van "niet gevonden" te scheiden.
- `eprel_bijwerken.py` — 100 per ronde, elke 3 uur, halve seconde ertussen, om
  en om uit elke categorie. Een kwart per ronde gaat naar verversen van rijen
  ouder dan 30 dagen (**licentievoorwaarde 4.2f**).
- `routes/products._eprel_certificering` — `hasCertification` in de
  gestructureerde data, inclusief de liggende streep in `European_Commission`.

**Stand 1 augustus: 1.275 opgezocht, 472 gevonden, trefkans 70%** over de
apparaten die er echt in kunnen staan. Verwacht eindtotaal ± 1.000. Brussel
heeft ons geen enkele keer afgewezen.

### Merchant Center

Van **1.383 afgekeurd naar 143** in drie dagen, na het toevoegen van
`availability` op het overkoepelende blok. De vraag "hoort een vergelijker wel
in Merchant Center" is daarmee van tafel.

---

## Elke dag: de storingscontrole

Peter wil dit dagelijks, en terecht — in vijf dagen leverde het vier fouten op
die niemand had gemeld.

- `/api/eprel` → beweegt `al_opgezocht`? Staat er iets bij
  `laatste_ronde_afloop.afgebroken_door`? (429 = te veel verzoeken, 403 =
  geweigerd → `EPREL_INTERVAL` omhoog.)
- `/api/prijssprongen?dagen=1` → staat `teruggesprongen` op nul?
- `/api/teksten/diagnose` → daalt `leverbaar_zonder_tekst`? Staat
  `ai_sleutel_aanwezig` op true?
- `/api/sync-status` → draaien alle tien routines? Staan er prijssprongen in
  `laatste_synclogs`? **Leg die naast /api/prijssprongen** — als het logboek
  sprongen meldt en de meetpagina niet, klopt er iets niet.
- Merchant Center (authuser=5) → daalt het aantal afgekeurde producten?
  Sinds 1 sept ook: **hoeveel Shopping-vertoningen en klikken** (Analytics →
  Producten → Verkeer, tabblad Datum). Op 31 aug sprong dat van minder dan
  20 naar 1.050 met 11 klikken; de vraag is of dat doorzet.
- Search Console (/u/5/) → nieuwe 404's, serverfouten, noindex? (De
  %-adressen geven sinds 10 sept 404 in plaats van 502; de 5xx-validatie
  mag Peter opnieuw starten.)
- `/api/sync-status` → `winkelbijdrage[].niet_ververst_3d`: staat er bij
  een winkel iets anders dan 0 (Bol ~300 is bekend: oude uitverkochte
  rijen), dan staat die feed stil -- dezelfde dag uitzoeken. Sinds 10 sept
  meldt de veiligheidsklep zich ook in `laatste_synclogs`.
- (VERVALLEN 19 sept: Witgoedhuis losgelaten, zie blok 19 sept; alleen nog af
  en toe kijken.) Daisycon-feed Witgoedhuis: `curl -sI "https://daisycon.io/datafeed/?media_id=428244&program_id=6570&standard_id=6&language_code=nl&locale_id=1&type=xml&records=5"`
  → zolang `X-Total-Count: 0`, is de aanmelding niet goedgekeurd.
- Klikbakjes in `/api/sync-status`: `klik-browser` moet in de buurt van het
  aantal `uit-*` blijven; `product-los-adres` en `product-geen-secfetch` zijn
  de robot. Groeit `klik-browser` opeens hard, dan is er weer een gat.
- Merchant Center: staat de melding "Beschrijvingen voor
  Koelvriescombinaties updaten" er nog (was 164 op 11 sept)?

- Railway: `railway metrics --since 1d --json` → staat `5xx` op 0 en is
  p99 onder de 2 s? En `railway logs -d -n 5000 | grep -E "WORKER TIMEOUT|Traceback"`
  leeg? (Het `-f "@httpStatus:..."`-filter werkt niet; zie 14 sept.)
- Search Console → Crawlstatistieken → host www → "De pagina kan niet
  worden bereikt": hoeveel per dag? Normaal 2-3; boven de 15 is een
  uitschieter (12 sep: 27). Dit is de teller achter MC's "productpagina
  niet beschikbaar".
- Productpagina zoals een bezoeker: `curl -s <productpagina> | grep -c -E '#\}|\{%|%\}|\{#'`
  moet 0 geven (4-16 sept stond een programmeursnotitie zichtbaar op alle
  productpagina's; de meetpagina's zagen dat niet).
- **Elke dinsdag:** de tien modelcodes live in Google meten en de tabel in
  `docs/RANKING-METING.md` aanvullen (werkwijze staat erin). SC-posities zijn
  hiervoor NIET bruikbaar (moduleposities).
- `/api/gezondheid` → staat er GEZOND? Bij STORING staat eronder wat er
  stilstaat; dezelfde dag uitzoeken. Sinds 21 sept ook "laatste
  prijswijziging" per grote winkel: boven de 36 uur is al ongewoon.
- UptimeRobot (dashboard.uptimerobot.com, Peters Chrome): incidenten in de
  afgelopen 24 uur? Leg ze naast de SC-teller "kan niet worden bereikt".
- Mailbox: antwoord van TradeTracker, Awin (Mike Kramer) of Daisycon?
  (Gmail-zoekopdracht `tradetracker OR awin OR daisycon newer_than:7d`;
  op 14 sept: niets.)

**Meld ook als alles goed is.** "Niets gevonden" is een uitkomst.

Elke twee tot vier weken, niet vaker: "Gevonden — niet geïndexeerd" (1.243 op
1 sept) en "Gecrawld — niet geïndexeerd" (11, validatie mislukt op 29 aug).
Die bewegen in weken; niet opnieuw valideren.

Half september: **de doorklikratio opnieuw meten** (was 1,96% op 25 aug).
Google moet de nieuwe titels eerst opnieuw ophalen, eerder meten zegt niets.

---

## Openstaand

### 1. Filterpagina's — het grootste dat er ligt

Gemeten bij de concurrentie op 1 augustus: **Slimster heeft 57 filterpagina's
voor alleen wasmachines** (per merk, per kenmerk, per klasse, en **per
winkel**: `/wasmachines/coolblue/`). Wij hebben er **28 over de hele site**.
Elke zo'n pagina mikt op een echte zoekopdracht.

Knibble rendert zijn productlijsten met JavaScript — die staan niet in de HTML.
Wat zij wél slim doen: **een uitlegpagina per filter**
(`/uitleg/vulgewicht/...`).

Geen van beiden zet winkelknoppen op de categoriepagina; dezelfde trechter als
bij ons.

`/api/filterkansen` (tak `diag/filterkansen`, nog door te voeren) rekent uit
welke pagina's genoeg apparaten hebben. Ondergrens 8 — daaronder krijg je een
dunne pagina, en die heeft deze site er al 918 van.

**Per winkel kan vandaag al** (geen EPREL nodig). Per kenmerk zodra EPREL rond
is.

### 2. EPREL stap 3 — specificaties op de pagina

Geluid, water, stroom, vulgewicht, toerental, afmetingen, garantie — **met
bronvermelding naar EPREL** (licentievoorwaarde). 65% van de catalogus heeft nu
geen enkele specificatie; dit is wat de 918 pagina's inhoudelijk moet
verzwaren.

### 3. De laagste-prijs-claim kan vergiftigd raken

Een valse feed-prijs komt in `price_history` en wordt daarna voor altijd "de
laagste prijs sinds we volgen", met een koopadvies eraan vast. Nu nog
tegengehouden door `price_history.te_kort`. **Eerst meten** bij hoeveel
apparaten die claim op een teruggesprongen prijs rust.

### 4. Prijsbewegingen-pagina — over een maand of twee

De prijshistorie begon 15 juli en bevat nu 13.993 wijzigingen, ± 1.000 per dag
erbij. Te dun voor uitspraken over maanden, maar over een paar maanden kun je
zeggen wat geen concurrent kan: hoe de hele markt beweegt. Meet eerst of er
genoeg geschiedenis is.

### 5. Nog te doen bij de concurrentie

Hoe sturen Knibble en Slimster mensen naar de winkel op hun **product**pagina?
De categoriepagina's zijn bekeken, de productpagina's niet — beide sites
blokkeren geautomatiseerd bezoek daar.

### 6. Klein

- **Dinsdag/woensdag 5-6 augustus:** in Search Console op "Oplossing
  valideren" klikken bij de 918, als EPREL rond is en Google de nieuwe titels
  heeft opgehaald. Niet eerder — dan vraag je een herkansing met werk dat nog
  niet af is.
- **Vier categorieën hebben geen enkele gids:** koffiemachines, afzuigkappen,
  fornuizen, kookplaten. Van de gewone zoekwoorden krijgt alleen
  "afzuigkappen" (17) en "vaatwasmachine" (16) vertoningen. **Maar de
  negentien bestaande gidsen zijn geïndexeerd en leveren níets op** — meer van
  hetzelfde schrijven lost dat niet op.
- **De EPREL-sleutel** (aangevraagd 26 juli) is niet meer nodig om te bouwen.

---

## Valkuilen — allemaal fouten die eerst gemaakt zijn

**Een zeef toetsen op je eigen vangst bewijst niets.** De tekstcontrole werd
getoetst op de 87 zinnen die de oude versie al had gevonden.

**Een verbinding die je nergens bewaart, wordt opgeruimd terwijl je er nog uit
leest.** `Anthropic(...).messages.batches.results(id)` op één regel liet de
batch halverwege afbreken.

**Meet voordat je sleutelt.** Er is driemaal aan de markup gezeten voordat
bekend was wat Google zelf als reden opgaf.

**Vergelijk dezelfde maat.** De setprijs werd gerekend met `lowest_price` en de
losse apparaten met het kale `price`-veld.

**Een query die per stuk redelijk lijkt, honderd keer uitgevoerd, is traag.**

**Controleer of je commit op de goede tak staat.** Twee keer misgegaan.

**Een interval-job die aan de processtart hangt, valt stil op een drukke dag.**
`teksten_job` stond op "95 minuten na opstarten" en draaide op 28 juli een
halve ochtend niet. Alle routines zijn nu verankerd aan hun laatste échte
draaimoment. **Bouw je een nieuwe routine, doe dat ook.**

**Een achtergebleven tak draait werk terug.** Na het doorvoeren:
`git merge origin/main` in die tak en pushen, of hem laten liggen — maar nooit
opnieuw mergen. Let op: `git diff origin/main origin/<tak>` toont dan een
verschil dat níets betekent; gebruik `git merge-base --is-ancestor`.

**De noodrem kijkt 24 uur terug, niet naar een kalenderdag.** Na de batch van
€ 14,32 schreef de tekstroutine een etmaal niets. Dat was geen storing.

**Een uitsluiting op categorie én titel tegelijk sluit te veel uit.** De
categorie heet "Ovens & Airfryers"; uitsluiten op "airfryer" gooide alle
inbouwovens eruit. Categorieën uitsluiten op de categorienaam, losse apparaten
op de titel.

**De www-doorstuur gooide alles achter het vraagteken weg** (gerepareerd 31
juli). Zoektermen, filters, paginanummers, `utm_source` en `gclid` gingen
verloren — dat laatste breekt de koppeling tussen een Google Ads-klik en een
aankoop. Gevonden doordat `?dagen=1` hetzelfde antwoordde als `?dagen=30`.

**Een venster over de regels is niet hetzelfde als een venster over de
gebeurtenissen** (gerepareerd 1 augustus). `/api/prijssprongen?dagen=1` gaf nul
sprongen terwijl het synclogboek er zes meldde: `price_history` bewaart alleen
wijzigingen, dus een prijs die weken stilstond heeft binnen een dag geen
voorganger om mee te vergelijken. Nu worden de regels ruim opgehaald
(`_SPRONG_TERUGKIJK_DAGEN`) en de sprongen op het venster gefilterd.

**Dit was de derde keer in een week dat iets niet kapot was maar stil.** De
tekstroutine die niet draaide, de doorstuur die querystrings weggooide, en een
controle die wegkeek. **Leg een nieuwe meting één keer naast een andere bron
voordat je hem vertrouwt** — het synclogboek, een handmatige telling, wat dan
ook. "Alles goed" ziet er hetzelfde uit als "ik kijk niet".

---

## Nuttige adressen (alle read-only, geen sleutel nodig)

Roep ze aan **met `www`**.

| Adres | Wat het toont |
|---|---|
| `/api/eprel` | Voortgang, trefkans, voorbeelden, afloop laatste ronde |
| `/api/filterkansen` | Welke filterpagina's genoeg apparaten hebben |
| `/api/prijssprongen` | Verdachte prijsbewegingen; `?dagen=` en `?drempel=` |
| `/api/bol-aanbiedingen?ean=` | Wat Bol werkelijk teruggeeft voor één artikel |
| `/api/teksten/diagnose` | Aantallen, sleutel aanwezig, wachtrij, laatste ronde |
| `/api/teksten/nalezen` | De opgeslagen teksten; `?vlaggen=1` de aangestreepte |
| `/api/sync-status` | Alle routines, laatste syncs, winkelbijdrage, dekking |
| `/api/catalogus-afwijkingen` | Setjes en niet-apparaten in de catalogus |
| `/api/setprijzen` | Bij hoeveel setjes de prijsvergelijking lukt |
| `/api/tekstproef` | De proefpagina (kost geld bij nieuwe teksten) |
