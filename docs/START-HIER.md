# Start hier — overdracht aan een nieuwe sessie

Bijgewerkt **1 september 2026** (het blok "Update 1 september" hieronder is
het nieuwste; oudere blokken en hoofdstukken blijven gelden waar de update
niets anders zegt). Lees dit eerst; het projectgeheugen van de chat
(MEMORY.md in de Claude-projectmap) draagt dezelfde feiten compact en is
leidend voor werkafspraken.

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
- Search Console (/u/5/) → nieuwe 404's, serverfouten, noindex?
- Railway-proef: `curl -o /dev/null -w "%{http_code}" https://www.witgoedaanbod.nl/%-`
  → nog steeds 502? Zodra dat iets anders wordt, heeft Railway het gerepareerd
  en mag de 5xx-validatie in Search Console opnieuw.

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
