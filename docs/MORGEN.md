# Waar we staan — verder op 28 juli

Kort overdrachtsbriefje, geschreven aan het eind van 27 juli. Dit is een
takenlijst, geen toestandsbeschrijving: de echte stand staat in
`STAND_VAN_ZAKEN.md`. Weggooien zodra het afgewerkt is.

---

## 0. Eerst dit: één tak wacht nog

`feat/teksten-routine` staat gepusht maar is nog niet doorgevoerd. Daar zit de
catalogusopschoning in (Apparaatsets + de vijf niet-apparaten). Zonder die merge
gebeurt er van punt 1 niets.

Doorvoeren, wachten op Railway, en dan kijken bij:

    https://www.witgoedaanbod.nl/api/catalogus-afwijkingen

---

## 1. Controleren of de opschoning is aangeslagen

De uitzonderingen worden elk uur toegepast, en drie minuten na een herstart.
Meteen na de deploy is het dus nog niet gedaan; even wachten.

Wat er hoort te kloppen:

- `/category/apparaatsets` bestaat en bevat rond de 51 producten.
- De vijf geblokkeerde EAN's zitten niet meer in de catalogus. Ze staan met naam
  en toenaam in `catalogus_uitzonderingen.GEBLOKKEERDE_EANS`.
- In de uitkomst van `pas_toe` is `ten_onrechte_in_setjes` leeg. Staat daar wél
  iets in, dan is er een product in Apparaatsets beland dat volgens zijn titel
  geen setje is. Dat is een signaal dat de titelregel bijgesteld moet worden —
  niet dat het product met de hand verplaatst moet worden.

Let op: de categoriemeting (`category_context._profiel`) heeft een cache van 15
minuten. De prijszinnen op de wasmachinepagina's veranderen dus pas een kwartier
nadat de setjes eruit zijn.

---

## 2. De enige echte bouwklus die nog openstaat: setprijs vs. los

Afgesproken, nog niet gebouwd.

Bij een setje staat nu niets bijzonders. Het idee: de twee apparaten uit de titel
opzoeken in de eigen catalogus, hun laagste prijzen optellen, en het verschil
tonen.

    Deze set kost € 1.149. Dezelfde twee apparaten los kosten samen € 1.207 —
    een verschil van € 58.

En net zo goed de andere kant op:

    Deze set kost € 1.149. Dezelfde twee apparaten los kosten samen € 1.098 —
    los is hier € 51 goedkoper.

Waarom dit de moeite waard is: het is een uitspraak die geen enkele andere site
over die set doet, hij komt volledig uit de eigen catalogus, en hij is elke dag
opnieuw waar omdat hij wordt meegerekend. Hetzelfde principe als het
categoriecontext-blok.

Waar het aan vastzit: de twee typenummers uit de titel halen (die staan er, dat
is juist hoe een setje herkend wordt — zie `catalogus_uitzonderingen.is_setje`)
en die matchen tegen `Product.title` of het Model-veld. Lukt één van de twee
niet, dan vervalt de hele zin. Niets schatten, zoals overal.

Dit is ook waarom "Voordeelsets" als categorienaam is afgewezen: dat is een
prijsbelofte die wij niet kunnen waarmaken. Uitrekenen mag wel, beweren niet.

---

## 2b. Waar we op wachten (niets aan te doen, wel in de gaten houden)

Twee dingen liggen bij anderen. Ze staan hier zodat ze niet stilletjes
verdwijnen; er is geen actie behalve af en toe kijken.

- **EPREL-API (Brussel).** Aanvraag verstuurd op 26 juli 's avonds, nog geen
  antwoord. Dit is de EU-database met energielabels; hij matcht op de
  modelaanduiding. Waarom het ertoe doet: 74% van de producten heeft nu een leeg
  `Model`-veld, en Coolblue levert er 616 aan (van de 1237 die wij van hen
  volgen). Met de EPREL-sleutel kunnen die codes geverifieerd worden en kunnen
  we labelgegevens ophalen voor producten waar de winkel ze niet levert.
  Komt er niets, dan is dat op zichzelf een antwoord: dan blijft het bij wat de
  feeds leveren.
- **De laatste winkel (TradeTracker / Voordeligwitgoed.nl).** Feed nog niet
  binnen. Daarmee zou de vergelijker op zeven winkels komen in plaats van zes.

---

## 3. Losse einden, geen haast

- **Nieuwe producten zonder tekst.** De routine (`teksten_bijwerken`) draait elke
  6 uur en pakt er hoogstens 25 per keer. Stond vanavond op 16 à 25 stuks. Even
  kijken of dat getal daalt; blijft het staan, dan draait de job niet.
- **19 aangestreepte teksten** staan opgeslagen maar niet op de site. Vijftien
  daarvan zijn setjes — die verhuizen nu naar Apparaatsets, en dan is de vraag of
  hun tekst daar wél klopt. Te lezen via `/api/teksten/nalezen?vlaggen=1`.
- **`AI_BEHEER_SLEUTEL` is verwijderd** uit Railway. De eindpunten `start`,
  `ophalen` en `publiceren` staan daarmee op slot (503). Is er ooit weer een
  grote batch nodig, dan een nieuwe waarde neerzetten en daarna weer weghalen.
- **De proefteksten** (`proef-v1`, 17 rijen; `proef-v2`, 28 rijen) staan nog in
  `ai_content` en worden nergens gebruikt. Mogen weg.

---

## Wat er 27 juli is gebeurd, in het kort

Alle 2806 leverbare producten hebben een eigen beschrijving gekregen; 2787 staan
live. De verkooptekst van de winkel — woordelijk gelijk aan die bij Bol en bij de
fabrikant — is daarmee van de productpagina's verdwenen. Dat was het laatste stuk
van de pagina dat nog uit de feed kwam.

Totale kosten: **€ 14,34** voor 2806 teksten, een halve cent per stuk. Ruim onder
de eerste raming van € 34, doordat de vaste instructie in een grote batch vrijwel
altijd hergebruikt wordt in plaats van opnieuw berekend.

Verder die dag: drie zinsvarianten in het categoriecontext-blok (dat stond op
2800 pagina's met dezelfde zinsbouw), merk-naar-merk-links onderaan de
merkpagina's, een verantwoordingspagina op `/productteksten`, een noodrem van
€ 5 per etmaal op de tekstgeneratie, en een automatische controle die elke tekst
toetst op prijzen, winkelnamen en aansporingen.

Twee dingen die het waard zijn om te onthouden, omdat ze allebei fout gingen
voordat ze goed gingen:

- **Een zeef toetsen op je eigen vangst bewijst niets.** De controle werd
  aangescherpt en getoetst op de 87 zinnen die de oude versie al had gevonden.
  Die toets kon per definitie geen nieuwe valse treffers laten zien; de nieuwe
  versie leverde er 46 op en was dus strikt slechter.
- **Een verbinding die je nergens bewaart, wordt opgeruimd terwijl je er nog uit
  leest.** `Anthropic(...).messages.batches.results(id)` op één regel liet de
  batch halverwege afbreken met "Bad file descriptor". Lokaal onvindbaar, want
  daar was geen echte verbinding.

De volledige verantwoording staat in `STAND_VAN_ZAKEN.md`.
