# Start hier — overdracht aan een nieuwe sessie

Bijgewerkt **1 augustus 2026, eind van de middag**. Lees dit eerst, daarna
`STAND_VAN_ZAKEN.md` (de volledige verantwoording) en `MORGEN.md` (de
takenlijst).

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
