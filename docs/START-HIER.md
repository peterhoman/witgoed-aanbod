# Start hier — overdracht aan een nieuwe sessie

Geschreven 28 juli 2026, eind van de middag, omdat het gesprek vol raakte.
Lees dit eerst, daarna `STAND_VAN_ZAKEN.md` (de volledige verantwoording) en
`MORGEN.md` (de takenlijst).

De site is **witgoedaanbod.nl**, een Nederlandse prijsvergelijker voor witgoed.
Flask + SQLAlchemy + Jinja2, draait op Railway, main wordt automatisch
uitgerold. Ongeveer 2.800 leverbare producten, prijzen uit zes winkelfeeds.
Eigenaar is Peter Homan (Avantius, Sassenheim).

---

## Werkwijze — deze regels gelden altijd

Ze staan ook in `STAND_VAN_ZAKEN.md`, maar ze zijn te belangrijk om te missen.

1. **Nooit naar main pushen.** Werk op een tak, push die, en geef Peter een
   vergelijk-link in de vorm
   `https://github.com/peterhoman/witgoed-aanbod/compare/main...<tak>`.
   Hij voert hem zelf door. De `gh`-opdrachtregel is hier niet beschikbaar.
2. **Verifieer op productie, niet lokaal.** De lokale database bevat een
   handvol voorbeeldproducten; metingen daarop zeggen niets.
3. **Meet voordat je sleutelt.** Dit is de duurste les van vandaag — zie
   "Valkuilen" onderaan.
4. **Beweer niets wat de data niet draagt.** Ontbreekt een gegeven, laat het
   onderdeel weg in plaats van te schatten. Dat is de kernregel van het hele
   project.
5. **Leg uit in gewone taal.** Geen git-jargon ("takken erdoor halen" zei niets
   tegen hem). Geen webadressen in ```bash-blokken: die krijgen een Run-knop en
   belanden dan in PowerShell in plaats van in de browser.
6. **Documenten voor Peter als `.txt` op zijn bureaublad.** `.md` opent niet op
   zijn Windows. Bureaublad staat op
   `%USERPROFILE%\OneDrive\Bureaublad`.
7. **Niet te veel tegelijk.** Hij heeft eerder aangegeven dat het tempo te hoog
   lag. Eén ding, laten zien, dan verder.
8. **`noindex` op de circa 1600 producten met één winkel is afgewezen** op
   26 juli. Niet opnieuw voorstellen.

---

## Waar we nu staan

### Eigen productteksten — af

Alle leverbare producten hebben een eigen beschrijving; die van de winkel is
van de productpagina's verdwenen. Dat was het laatste stuk dat woordelijk ook
bij Bol en bij de fabrikant stond, en de reden dat Google 100 pagina's oversloeg
met "gecrawld, momenteel niet geïndexeerd".

- Geschreven met Claude (`claude-opus-5`) via de Batch API. **Kosten: € 14,34
  voor 2806 teksten**, een halve cent per stuk.
- `ai_content.py` bouwt de prompt uit eigen gegevens: specificaties uit de
  feeds plus de eigen catalogusmeting. De **verkooptekst van de winkel gaat
  bewust niet mee** — een model dat die als bron krijgt, schrijft hem in eigen
  woorden na, en dan is het nog steeds dubbele inhoud.
- `ai_content.controleer` is een zeef over elke tekst: prijzen, prijsoordelen,
  winkelnamen, aansporingen. Wat wordt aangestreept gaat niet live.
- `teksten_bijwerken.py` draait elke 6 uur mee met de scheduler en geeft nieuwe
  producten vanzelf een tekst. **Herschrijft nooit** — alleen producten zonder
  tekst. Begrensd door `AI_DAGLIMIET_EURO` (€ 5 per etmaal, getoetst vóór elke
  tekst) en 25 teksten per ronde.
- Verantwoording staat op `/productteksten`, gelinkt onder elke tekst. Google
  vraagt daarom waar AI de inhoud grotendeels maakt.

**Let op:** `AI_BEHEER_SLEUTEL` is uit Railway verwijderd. Daarmee staan
`/api/teksten/start`, `ophalen` en `publiceren` op slot (503). Voor een nieuwe
grote batch: variabele opnieuw zetten, gebruiken, weer weghalen.

### Catalogus opgeschoond — af

Gevonden door de 2806 eigen teksten te doorzoeken; het model had de rommel zelf
al benoemd.

- **5 artikelen die geen apparaat zijn** van de site gehaald (stellingkast en
  serviesset onder Magnetrons, waterfilters onder Koffiemachines, geurfilter
  onder Afzuigkappen, borstel onder Stofzuigers). Op EAN, in
  `catalogus_uitzonderingen.GEBLOKKEERDE_EANS`.
- **59 setjes** (twee apparaten als één artikel) naar de nieuwe categorie
  **Apparaatsets**. Herkend aan de titel, niet aan een lijst: na de plus staat
  opnieuw een merknaam of een typenummer. Zie `catalogus_uitzonderingen.is_setje`.
- `catalogus_uitzonderingen.pas_toe` draait elk uur en trekt dit telkens recht,
  want de syncs zetten geblokkeerde artikelen anders zo weer terug.

### Setprijs versus los — af, vandaag gebouwd

Op elke setpagina waar het lukt (45 van de 59) staat wat dezelfde twee
apparaten los kosten, met links erheen. **Bij 10 van de 28 met een verschil
boven € 25 is los kopen goedkoper** — soms € 131. Dat zegt geen enkele andere
site.

Werkt niet bij Miele (typenummers met spaties, "WQ 1000 WPS Nova") en bij vijf
sets waar één apparaat niet los in de catalogus staat. Dan vervalt het blok.
Zie `setprijs.py` en de meetpagina `/api/setprijzen`.

### Overig van 27-28 juli

- Drie zinsvarianten in het categoriecontext-blok (stond op 2800 pagina's met
  dezelfde zinsbouw). Vast gekoppeld aan `product.id`, niet willekeurig — anders
  verandert de tekst tussen twee crawls van Google.
- Merk-naar-merk-links onderaan de merkpagina's.
- `priceValidUntil` helemaal weg uit de gestructureerde data.
- `availability` toegevoegd aan het overkoepelende `AggregateOffer`-blok.
- `robots.txt`: `Disallow: /api/` en `/admin/` stonden alleen onder `*`, terwijl
  Googlebot een eigen groep had met alleen `Allow: /`. Een crawler volgt maar
  één groep — die uitsluitingen werkten dus niet. Nu bij alle tien de groepen.

---

## Dit moet als eerste gebeuren

### 1. Controleren of `fix/restpunten` heeft gedaan wat het moest

Die tak is 28 juli aan het eind doorgevoerd, maar het resultaat is niet meer
nagekeken. De routine die het werk doet draait elke 6 uur, dus het kan zijn dat
het pas later zichtbaar is.

Wat er moet kloppen:

- `/api/teksten/nalezen?vlaggen=1` toont nog **4** aangestreepte teksten in
  plaats van 19. De 15 setjesteksten met "Deze aanbieding betreft een
  combinatie van..." horen er nu doorheen te komen.
- `/api/teksten/diagnose` toont **geen `proef-v1` en `proef-v2` meer** (waren
  17 en 28 rijen).
- De kop van `/api/teksten/nalezen` toont een percentage onder de 100 (stond op
  101,4%).

Klopt er iets niet, kijk dan of de scheduler-job `teksten_job` wel draait —
zonder die job gebeurt geen van de drie.

### 2. Merchant Center — elke dag kijken tot het opgelost is

Google keurde **alle 1383** automatisch gevonden producten af met één reden:
**"Ontbrekende waarde voor [availability]"**. Dat veld stond wel in de markup,
maar in de geneste aanbiedingen — en Google leest van een `AggregateOffer`
alleen het overkoepelende blok. Dat is vandaag toegevoegd.

Elke dag kijken in Merchant Center → Producten → **Vereist aandacht**, tot dat
aantal nul is. Zolang het niet daalt is er iets mis met de reparatie, en dat
wil je binnen een dag weten.

- **Naar nul** → opgelost. Dan pas zien we of dit kanaal iets oplevert; er waren
  nul klikken, maar dat kwam doordat alles was afgekeurd.
- **Blijft staan** → dan speelt punt 5 hieronder.

### 3. Search Console — elke dag kijken, maar weet waarnaar

Peter controleert dagelijks, en dat is goed: een storing zie je dan binnen een
dag in plaats van na een week. Hou wel twee dingen uit elkaar, anders trek je
conclusies uit ruis.

**Elke dag, om fouten te vangen:** nieuwe 404's, serverfouten, pagina's die
ineens op noindex staan, een sitemap die niet meer wordt gelezen. Dat zijn
storingen en die horen dezelfde dag opgelost. Nagaan met de controles onderaan
dit document — alle sitemap-adressen en interne links moeten 200 geven.

**Elke twee tot vier weken, om vooruitgang te lezen:** de aantallen "gevonden —
niet geïndexeerd" en "gecrawld — niet geïndexeerd". Die bewegen langzaam omdat
Google 2800 pagina's opnieuw moet beoordelen. Dagelijkse schommelingen daarin
zeggen niets; alleen de lijn over weken telt.

Het doel is hoger komen in Google. Daarvoor is de dagelijkse controle het
vangnet en de wekenlange lijn de uitkomst.

### Waar het nu staat

918 pagina's staan als "Gevonden — momenteel niet geïndexeerd". Dat is een
derde van de site, en het is een kwaliteitsoordeel: Google kent die adressen
maar vindt ze de moeite van het ophalen niet waard. Daar waren de eigen teksten
voor bedoeld; het oordeel duurt weken.

Goed nieuws in datzelfde rapport: **"Gecrawld — niet geïndexeerd" staat op 4,
was 100.** Dat is het cijfer waar het hele project op gericht was.

De 22 404's, 20 noindex en 41 canonical-meldingen zijn nagelopen en onschuldig:
alle 3269 sitemap-adressen geven 200, 316 interne links geven 200, geen enkele
echte pagina heeft noindex.

---

## Wat verder openstaat

### 4. Wachten op anderen

- **EPREL-API (Brussel)** — aangevraagd 26 juli 's avonds, nog geen antwoord.
  Levert twee dingen op: het `Model`-veld vullen (74% is leeg) én het veld
  `hasCertification`, dat Google **speciaal voor EPREL** documenteert en
  *"particularly relevant in European countries"* noemt. Vrijwel geen
  concurrent vult dat in. Bouwen zodra de sleutel er is.
- **De zevende winkel** (TradeTracker / Voordeligwitgoed.nl) — feed nog niet
  binnen.

### 5. Geparkeerd: hoort een vergelijker in Merchant Center?

Google's beleid: affiliate-links in Shopping mogen alleen via een Comparison
Shopping Service. Zelf CSS worden kan niet — dat vereist **minstens 50
winkeldomeinen**, en er zijn er zes.

Maar Google klaagt hier niet over; de enige afkeuringsreden is dat ontbrekende
veld. Deze vraag dus pas oppakken als punt 2 níet oplost. Conclusie zou dan
waarschijnlijk zijn: die automatische bron uitzetten en Merchant Center
loslaten.

### 6. Kleine dingen

- **Geneste aanbiedingen weghalen** uit de markup. Drie modellen adviseerden dat
  (Google leest ze niet). **Niet doen voordat punt 2 beantwoord is** — anders is
  straks niet te zeggen welke wijziging het deed.
- **4 teksten blijven aangestreept** op zinnen als "de gegevens geven over het
  geluid niets prijs" (het werkwoord prijsgeven, los geschreven). Marginaal;
  laten staan tenzij er een schone oplossing is.

---

## Valkuilen — allemaal fouten die eerst gemaakt zijn

**Een zeef toetsen op je eigen vangst bewijst niets.** De tekstcontrole werd
aangescherpt en getoetst op de 87 zinnen die de oude versie al had gevonden.
Zo'n toets kan per definitie geen nieuwe valse treffers laten zien; de nieuwe
versie leverde er 46 op en was strikt slechter.

**Een verbinding die je nergens bewaart, wordt opgeruimd terwijl je er nog uit
leest.** `Anthropic(...).messages.batches.results(id)` op één regel liet de
batch halverwege afbreken met "Bad file descriptor". Lokaal onvindbaar.

**Meet voordat je sleutelt, ook als de diagnose voor de hand ligt.** Er is
tweemaal aan de markup gezeten voordat bekend was wat Google zelf als reden
opgaf — en die reden bleek iets heel anders. Eén klik in Merchant Center had
dat vooraf verteld.

**Vergelijk dezelfde maat.** De setprijs werd eerst gerekend met `lowest_price`
en de losse apparaten met het kale `price`-veld. Het bedrag zag er geloofwaardig
uit en klopte principieel niet.

**Een query die per stuk redelijk lijkt, honderd keer uitgevoerd, is traag.**
`Product.title.ilike('%code%')` per typenummer liet de meetpagina na tien
minuten nog niet afronden. Nu één keer ophalen en in het geheugen vergelijken.

**Controleer of je commit echt op de goede tak staat.** Er is een keer werk op
de verkeerde tak gecommit en naar een derde tak gepusht; het stond nergens.

---

## Nuttige adressen (alle read-only, geen sleutel nodig)

| Adres | Wat het toont |
|---|---|
| `/api/teksten/diagnose` | Aantallen per soort tekst, batchstatus, zichtbare teksten |
| `/api/teksten/nalezen` | De opgeslagen teksten; `?vlaggen=1` alleen de aangestreepte |
| `/api/catalogus-afwijkingen` | Setjes en niet-apparaten in de catalogus |
| `/api/setprijzen` | Bij hoeveel setjes de prijsvergelijking lukt |
| `/api/tekstproef` | De proefpagina (kost geld bij nieuwe teksten) |
