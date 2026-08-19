# Start hier — overdracht aan een nieuwe sessie

Bijgewerkt **19 augustus 2026** (het blok "Update 19 augustus" hieronder is
het nieuwste; oudere blokken en hoofdstukken blijven gelden waar de update
niets anders zegt). Lees dit eerst; het projectgeheugen van de chat
(MEMORY.md in de Claude-projectmap) draagt dezelfde feiten compact en is
leidend voor werkafspraken.

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
11. **Wat Peter niet kan, kan hij wel laten zien.** Search Console, Railway,
    TradeTracker en Anthropic zijn voor de browser hier geblokkeerd; Merchant
    Center wel toegankelijk. Vraag om een schermafdruk en zeg er precies bij
    waar hij moet klikken — hij leert er graag van.
12. **Een meting die "alles goed" zegt, is pas te vertrouwen als je hem één
    keer tegen een andere bron hebt gelegd.** Zie de valkuilen.

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
- Merchant Center → daalt het aantal afgekeurde producten?
- Search Console → nieuwe 404's, serverfouten, noindex?

**Meld ook als alles goed is.** "Niets gevonden" is een uitkomst.

Elke twee tot vier weken, niet vaker: "Gevonden — niet geïndexeerd" (918) en
"Gecrawld — niet geïndexeerd" (4, was 100). Die bewegen in weken.

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
