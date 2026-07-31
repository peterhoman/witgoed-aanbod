# Start hier — overdracht aan een nieuwe sessie

Bijgewerkt **31 juli 2026, ochtend**. Vorige versie was van 28 juli; alles wat
daarna gebeurd is staat hieronder verwerkt. Lees dit eerst, daarna
`STAND_VAN_ZAKEN.md` (de volledige verantwoording) en `MORGEN.md` (de
takenlijst).

De site is **witgoedaanbod.nl**, een Nederlandse prijsvergelijker voor witgoed.
Flask + SQLAlchemy + Jinja2, draait op Railway, main wordt automatisch
uitgerold. Ongeveer 2.800 leverbare producten, prijzen uit zes winkelfeeds.
Eigenaar is Peter Homan (Avantius, Sassenheim).

---

## Werkwijze — deze regels gelden altijd

1. **Nooit naar main pushen.** Werk op een tak, push die, en geef Peter een
   vergelijk-link in de vorm
   `https://github.com/peterhoman/witgoed-aanbod/compare/main...<tak>`.
   Hij voert hem zelf door. De `gh`-opdrachtregel is hier niet beschikbaar.
2. **Verifieer op productie, niet lokaal.** De lokale database bevat een
   handvol voorbeeldproducten; metingen daarop zeggen niets.
3. **Meet voordat je sleutelt.** De duurste les van dit project — zie
   "Valkuilen" onderaan.
4. **Beweer niets wat de data niet draagt.** Ontbreekt een gegeven, laat het
   onderdeel weg in plaats van te schatten. Dat is de kernregel van het hele
   project.
5. **Leg uit in gewone taal.** Geen git-jargon ("takken erdoor halen" zei niets
   tegen hem). Geen webadressen in ```bash-blokken: die krijgen een Run-knop en
   belanden dan in PowerShell in plaats van in de browser.
6. **Documenten voor Peter als `.txt` op zijn bureaublad.** `.md` opent niet op
   zijn Windows. Bureaublad staat op `%USERPROFILE%\OneDrive\Bureaublad`.
7. **Niet te veel tegelijk.** Eén ding, laten zien, dan verder.
8. **`noindex` op de circa 1600 producten met één winkel is afgewezen** op
   26 juli. Niet opnieuw voorstellen.
9. **Er kan een tweede Claude-sessie in dezelfde map draaien.** Op 30 juli
   wisselde die van tak terwijl er werk klaarstond met alleen `git add`; dat
   werk liftte mee in háár commit en ging als andermans PR naar main. Commit
   dus meteen op je eigen tak, en controleer vóór en ná elke commit
   `git branch --show-current` en `git show --stat HEAD`.
10. **Geef Peter geen webadres alsof hij er iets mee moet.** Meetpagina's roep
    je zelf aan en je vertelt hem de uitkomst. Hij vroeg terecht "wat moet ik
    hiermee?".

---

## Waar we nu staan

### Eigen productteksten — draait vanzelf

Alle leverbare producten hebben een eigen beschrijving; die van de winkel is
van de productpagina's verdwenen. Dat was het laatste stuk dat woordelijk ook
bij Bol en bij de fabrikant stond.

- Geschreven met Claude (`claude-opus-5`) via de Batch API. **Kosten: € 14,34
  voor 2806 teksten**, een halve cent per stuk.
- `ai_content.py` bouwt de prompt uit eigen gegevens. De **verkooptekst van de
  winkel gaat bewust niet mee** — een model dat die als bron krijgt, schrijft
  hem in eigen woorden na, en dan is het nog steeds dubbele inhoud.
- `ai_content.controleer` is een zeef over elke tekst. Wat wordt aangestreept
  gaat niet live. Er blijven **4 teksten** aangestreept op het woord
  "prijsgeven" los geschreven; marginaal, laten staan.
- `teksten_bijwerken.py` draait elke 6 uur en geeft nieuwe producten vanzelf
  een tekst. **Herschrijft nooit.** Begrensd door `AI_DAGLIMIET_EURO` (€ 5 per
  etmaal) en 25 teksten per ronde.
- Stand 31 juli: **2.975 teksten opgeslagen, nog 6 producten wachtend.**

**`ANTHROPIC_API_KEY` staat in Railway en moet daar blijven** — zonder die
sleutel krijgt geen enkel nieuw product ooit een tekst.
**`AI_BEHEER_SLEUTEL` is verwijderd** en dat is goed; daarmee staan
`/api/teksten/start`, `ophalen` en `publiceren` op slot (503). Die twee namen
lijken op elkaar en doen het tegenovergestelde.

### Catalogus opgeschoond — af

- **5 artikelen die geen apparaat zijn** van de site gehaald, op EAN, in
  `catalogus_uitzonderingen.GEBLOKKEERDE_EANS`.
- **59 setjes** naar de categorie **Apparaatsets**, herkend aan de titel
  (`catalogus_uitzonderingen.is_setje`).
- `catalogus_uitzonderingen.pas_toe` draait elk uur en trekt dit telkens recht.

### Setprijs versus los — af

Op 45 van de 59 setpagina's staat wat dezelfde twee apparaten los kosten. Bij
10 van de 28 met een verschil boven € 25 is los kopen goedkoper. Werkt niet bij
Miele (typenummers met spaties). Zie `setprijs.py` en `/api/setprijzen`.

### Gestructureerde data — opgeschoond

- `priceValidUntil` helemaal weg.
- `availability` op het overkoepelende `AggregateOffer`-blok. **Dit was de
  reparatie die Merchant Center vlottrok** (zie hieronder).
- **Geneste aanbiedingen weg** (30 juli). Per winkel stond er een `Offer` met
  prijs en `seller`; Google leest die niet, en ze presenteerden ons als de
  verkoper in plaats van als vergelijker. Aantal winkels, laagste en hoogste
  prijs blijven in het overkoepelende blok.
- **`hasCertification` met het EPREL-registratienummer** (30 juli, zie EPREL).

### Prijsbewaking — nieuw op 30 juli

`/api/prijssprongen` toont verdachte prijsbewegingen uit `price_history`.
Standaard 7 dagen en 50%; met `?dagen=` en `?drempel=` in te stellen.

Het onderscheid dat ertoe doet: **een echte prijsdaling blijft staan, een
feed-fout springt terug.** Het veld `teruggesprongen` is het getal om op te
letten. Staat dat op nul, dan waren alle sprongen echte prijzen.

Gemeten over 30 dagen: 12.927 prijswijzigingen, 29 sprongen boven 50%, waarvan
**10 teruggesprongen** — dus vals. Vrijwel allemaal bij Bol, vooral bij
inbouwovens. De SMEG SO4301M1N sprong drie keer heen en weer tussen € 599 en
€ 1.399.

**Onze code doet daar niets fout.** `/api/bol-aanbiedingen?ean=...` liet zien
dat Bol precies één aanbieding teruggeeft, met alleen een prijs en een
levertijd — geen verkoper, geen conditie. Er valt niets te kiezen, dus ook
niets verkeerd te kiezen. Die € 599 wás op dat moment de prijs die Bol opgaf.

### Prijsversheid bij de prijs — nieuw op 30 juli

Onder de winkellijst staat nu: *"Prijzen opgehaald ruim 3 uur geleden. De prijs
bij de winkel op het moment van bestellen is leidend (voorwaarden)."*

Een **tijdsduur en geen kloktijd**: de database bewaart naïeve UTC-tijden, en
die als Nederlandse tijd tonen zit er in de zomer twee uur naast. Ontbreekt het
tijdstempel, dan valt dat halve zinnetje weg.

De juridische dekking stond al in de Algemene Voorwaarden, artikel 6 ("de prijs
op de website van de aanbieder op het moment van bestellen is leidend"), plus
artikel 3 en 7. Alleen niet zichtbaar bij de prijs zelf.

### EPREL — stap 1 en 2 draaien

**Het stond vier dagen ten onrechte op "wachten op Brussel".** De openbare
EPREL-API werkt zonder sleutel; hij weigert alleen verzoeken die er niet als
een browser uitzien (403 zonder `User-Agent` en `Referer`). Dat zijn dezelfde
adressen die de EPREL-website zelf gebruikt.

- `eprel.py` — categorie naar productgroep, typenummer uit de titel, en het
  bevragen van de API.
- `models.EprelData` — een rij per apparaat, ook bij een misser.
- `eprel_bijwerken.py` — 100 apparaten per ronde, halve seconde ertussen, om
  en om uit elke categorie. Een kwart van elke ronde gaat naar het opnieuw
  ophalen van rijen ouder dan 30 dagen; dat is **licentievoorwaarde 4.2f**.
- `routes/products._eprel_certificering` — zet `hasCertification` in de
  gestructureerde data, precies zoals Google het documenteert, inclusief de
  liggende streep in `European_Commission`.

**Licentie:** artikel 4 lid 1 staat dit gebruik uitdrukkelijk toe — *"to
implement the Data in mobile applications and other comparison tools"*. Twee
verplichtingen: bronvermelding (lid 3) en actueel houden (lid 2f).

Stand 31 juli: 175 apparaten opgezocht, 84 gevonden. Verwacht over de hele
catalogus: **ongeveer 1.020 apparaten**.

### Merchant Center — bijna opgelost

Google keurde alle 1383 automatisch gevonden producten af op één reden:
"Ontbrekende waarde voor [availability]". Sinds die reparatie:

| Datum | Goedgekeurd | Afgekeurd |
|---|---|---|
| 29 juli | 134 | 1.250 |
| 30 juli | 942 | 437 |
| 31 juli | 1.240 | **143** |

Loopt vanzelf leeg. **Punt "hoort een vergelijker wel in Merchant Center" is
daarmee van tafel** — Google klaagde nooit over de affiliate-links.

---

## Dit moet als eerste gebeuren

### 1. Eén tak wacht op doorvoeren

`fix/eprel-eerlijk-tellen` — zie "Openstaand" hieronder waarom.

### 2. Elke dag: de storingscontrole

- `/api/eprel` → beweegt `al_opgezocht`? Staat er iets bij
  `laatste_ronde_afloop.afgebroken_door`? Dat laatste betekent dat Brussel ons
  afwijst (429 = te veel verzoeken, 403 = geweigerd). Dan `EPREL_INTERVAL`
  omhoog.
- `/api/prijssprongen?dagen=1` → staat `teruggesprongen` op nul?
- `/api/teksten/diagnose` → daalt `leverbaar_zonder_tekst`? Staat
  `ai_sleutel_aanwezig` op true?
- `/api/sync-status` → draaien alle negen routines nog?
- Merchant Center → daalt het aantal afgekeurde producten?
- Search Console → nieuwe 404's, serverfouten, noindex?

### 3. Elke twee tot vier weken: de vooruitgang lezen

"Gevonden — niet geïndexeerd" (918) en "Gecrawld — niet geïndexeerd" (4, was
100). Die bewegen langzaam omdat Google 2800 pagina's opnieuw moet
beoordelen. Dagelijkse schommelingen zijn ruis.

---

## Openstaand

### EPREL stap 3 — de specificaties op de pagina

Geluid, waterverbruik, stroomverbruik, vulgewicht, toerental, afmetingen en
garantieduur, **met bronvermelding naar EPREL** (licentievoorwaarde). Dit is
het stuk dat de 918 niet-geïndexeerde pagina's inhoudelijk moet verzwaren:
65% van de catalogus heeft nu géén enkele specificatie.

### De laagste-prijs-claim kan vergiftigd raken

Een valse prijs uit een feed komt in `price_history` en wordt daarna voor
altijd "de laagste prijs sinds we dit apparaat volgen" — met een koopadvies
eraan vast. Bij de SMEG wordt dat straks € 599 terwijl het apparaat € 1.399
kost. Nu nog tegengehouden doordat de meetperiode te kort is
(`price_history.te_kort`).

**Eerst meten:** bij hoeveel apparaten rust die claim op een prijs die is
teruggesprongen? Daarna pas repareren. De gegevens om een uitschieter te
herkennen liggen er sinds 30 juli.

### Wachten op anderen

- **De zevende winkel** (TradeTracker / Voordeligwitgoed.nl) — feed nog niet
  binnen.
- **EPREL-sleutel** — aangevraagd 26 juli. Niet meer nodig om te bouwen, maar
  wel netjes om te hebben.

---

## Valkuilen — allemaal fouten die eerst gemaakt zijn

**Een zeef toetsen op je eigen vangst bewijst niets.** De tekstcontrole werd
getoetst op de 87 zinnen die de oude versie al had gevonden. Zo'n toets kan per
definitie geen nieuwe valse treffers laten zien.

**Een verbinding die je nergens bewaart, wordt opgeruimd terwijl je er nog uit
leest.** `Anthropic(...).messages.batches.results(id)` op één regel liet de
batch halverwege afbreken. Lokaal onvindbaar.

**Meet voordat je sleutelt, ook als de diagnose voor de hand ligt.** Er is
driemaal aan de markup gezeten voordat bekend was wat Google zelf als reden
opgaf — en die reden bleek iets heel anders.

**Vergelijk dezelfde maat.** De setprijs werd eerst gerekend met `lowest_price`
en de losse apparaten met het kale `price`-veld.

**Een query die per stuk redelijk lijkt, honderd keer uitgevoerd, is traag.**
`Product.title.ilike('%code%')` per typenummer liet een meetpagina na tien
minuten nog niet afronden.

**Controleer of je commit echt op de goede tak staat.** Twee keer misgegaan:
een keer naar een derde tak gepusht, een keer meegelift in de commit van een
tweede sessie in dezelfde map.

**Een interval-job die aan de processtart hangt, valt stil op een drukke dag.**
`teksten_job` stond op "95 minuten na opstarten". Op 28 juli werd er zes keer
uitgerold en heeft hij de hele ochtend niet gedraaid. Alle routines zijn nu
verankerd aan hun laatste échte draaimoment. **Bouw je een nieuwe routine, doe
dat ook.**

**Een achtergebleven tak draait werk terug.** Een tak die al is doorgevoerd
maar niet is bijgewerkt, laat bij een tweede merge het nieuwere werk
verdwijnen. Na het doorvoeren: `git merge origin/main` in die tak en pushen,
of hem laten liggen — maar nooit opnieuw mergen.

**De noodrem kijkt 24 uur terug, niet naar een kalenderdag.** Na de batch van
€ 14,32 op 27 juli schreef de tekstroutine een etmaal lang niets. Dat was geen
storing. Kijk dus eerst naar `ai_sleutel_aanwezig` en naar wat er in de
afgelopen 24 uur is uitgegeven voordat je iets repareert.

**Een uitsluiting op categorie én titel tegelijk sluit te veel uit.** De
categorie heet "Ovens & Airfryers"; uitsluiten op het woord "airfryer" gooide
alle inbouwovens eruit. Sluit hele categorieën uit op de categorienaam en
losse apparaten op de titel.

**De www-doorstuur gooide alles achter het vraagteken weg** (gerepareerd 31
juli). `request.path` bevat de querystring niet, dus wie zonder `www` binnenkwam
verloor zoektermen, filters, paginanummers én `utm_source` en `gclid`. Dat
laatste breekt de koppeling tussen een Google Ads-klik en een aankoop.
Gevonden doordat `/api/prijssprongen?dagen=1` hetzelfde antwoordde als
`?dagen=30` — de meetpagina deugde, de doorstuur niet.

---

## Nuttige adressen (alle read-only, geen sleutel nodig)

Roep ze aan **met `www`**; zonder www werkte de querystring vóór 31 juli niet.

| Adres | Wat het toont |
|---|---|
| `/api/eprel` | Voortgang EPREL, trefkans, voorbeelden, afloop laatste ronde |
| `/api/prijssprongen` | Verdachte prijsbewegingen; `?dagen=` en `?drempel=` |
| `/api/bol-aanbiedingen?ean=` | Wat Bol werkelijk teruggeeft voor één artikel |
| `/api/teksten/diagnose` | Aantallen, sleutel aanwezig, wachtrij, laatste ronde |
| `/api/teksten/nalezen` | De opgeslagen teksten; `?vlaggen=1` de aangestreepte |
| `/api/sync-status` | Alle routines met hun eerstvolgende run, laatste syncs |
| `/api/catalogus-afwijkingen` | Setjes en niet-apparaten in de catalogus |
| `/api/setprijzen` | Bij hoeveel setjes de prijsvergelijking lukt |
| `/api/tekstproef` | De proefpagina (kost geld bij nieuwe teksten) |
