# Openstaande punten — bijgewerkt 28 juli, ochtend

Volledige lijst van wat er nog moet gebeuren. Dit is een takenlijst, geen
toestandsbeschrijving: de verantwoording staat in `STAND_VAN_ZAKEN.md`. Punten
doorstrepen zodra ze af zijn; het bestand mag weg als alles leeg is.

---

## 0. Eerst doorvoeren — twee takken wachten

Ze bijten elkaar niet en mogen allebei tegelijk.

- `fix/geen-prijsvervaldatum` — `priceValidUntil` helemaal weg
- `fix/beschikbaarheid-aggregateoffer` — `availability` op het overkoepelende blok

De tweede is de belangrijkste van vandaag: die repareert vermoedelijk alle 1383
afgekeurde producten in Merchant Center.

---

## 1. Merchant Center in de gaten houden (vanaf maandag)

Google keurde alle 1383 automatisch gevonden producten af met één reden:
**"Ontbrekende waarde voor [availability]"**. Die waarde stond wel in onze
markup, maar in de geneste aanbiedingen — en Google leest van een
`AggregateOffer` alleen het overkoepelende blok.

Na de merge dus kijken of dat aantal daalt. Google zegt de bron elke 24 uur te
verversen, maar bij "laatste update" stond 24 juli, dus reken op een paar dagen.

- **Daalt het naar nul** → opgelost, en dan zien we voor het eerst of dit kanaal
  iets oplevert (tot nu toe nul klikken bij alle producten, maar dat kwam omdat
  alles was afgekeurd).
- **Blijft het staan** → dan komt de andere vraag terug, zie punt 6.

Waar te kijken: Merchant Center → Producten → tabblad **Vereist aandacht**.

---

## 2. De 918 niet-geïndexeerde pagina's — het echte werk, en er is niets te doen

Search Console meldt 918 pagina's als "Gevonden — momenteel niet geïndexeerd".
Dat is een derde van de site. Het betekent: Google kent die adressen wel, maar
vindt ze de moeite van het ophalen niet waard.

Drie onafhankelijke bronnen (GPT, Gemini, Claude, alle drie met verwijzing naar
Google's documentatie) zeggen hetzelfde: dat is een kwaliteitsoordeel, en het
staat **los** van de prijsvervaldatum en van Merchant Center.

Precies daarvoor zijn op 27 juli 2787 eigen productteksten live gegaan. Dat is
de ingreep. Er is nu niets meer te doen behalve wachten tot Google die pagina's
opnieuw langsloopt, en dat duurt weken.

**Goed nieuws in datzelfde overzicht:** "Gecrawld — niet geïndexeerd" staat op
**4**, was **100**. Dat is het cijfer waar het hele project op gericht was.

Niet elke week kijken. Over twee tot vier weken.

---

## 3. Bouwklussen die nog openstaan

### 3a. Setprijs versus de twee apparaten los

Afgesproken op 27 juli, nog niet gebouwd. Bij een setje (categorie
Apparaatsets) de twee apparaten uit de titel opzoeken in de eigen catalogus,
hun laagste prijzen optellen, en het verschil tonen:

    Deze set kost € 1.149. Dezelfde twee apparaten los kosten samen € 1.207 —
    een verschil van € 58.

En net zo goed de andere kant op ("los is hier € 51 goedkoper"). Dit is een
uitspraak die geen andere site over die set doet en die volledig uit de eigen
catalogus komt. Hetzelfde principe als het categoriecontext-blok.

Waar het aan vastzit: de twee typenummers uit de titel halen (die staan er —
zie `catalogus_uitzonderingen.is_setje`) en matchen tegen `Product.title` of het
Model-veld. Lukt één van de twee niet, dan vervalt de hele zin.

Dit is ook waarom "Voordeelsets" als categorienaam is afgewezen: dat is een
prijsbelofte die wij niet kunnen waarmaken. Uitrekenen mag, beweren niet.

### 3b. EPREL-certificering in de gestructureerde data

Nieuw gevonden op 28 juli, en het is de moeite waard. Google documenteert een
veld `hasCertification` **speciaal voor EPREL** — de Europese
energielabeldatabase — en noemt het *"particularly relevant in European
countries"*. Voor wasmachines, koelkasten en vaatwassers.

Dat betekent dat de EPREL-sleutel waar we op wachten (punt 5) niet alleen het
Model-veld vult, maar ook een veld in de markup mogelijk maakt dat Google
uitdrukkelijk voor Europees witgoed heeft gemaakt en dat vrijwel geen
concurrent invult.

Bouwen zodra de sleutel er is.

### 3c. Geneste aanbiedingen: houden of weghalen?

Alle drie de modellen adviseren ze weg te halen. Redenering: Google leest ze
niet (dat is nu gemeten, zie punt 1), en door per winkel een `Offer` met prijs
en `seller` te publiceren kan Google ons als de verkoper zijn gaan modelleren —
mogelijk de reden dat die 1383 producten überhaupt zijn aangemaakt.

**Niet doen voordat punt 1 is beantwoord.** Als het toevoegen van
`availability` de afkeuringen oplost, weten we dat Google het bovenste blok
leest en de nesting negeert; dan is weghalen een schoonmaakklus zonder haast.
Halen we ze nu weg, dan weten we straks niet welke van de twee wijzigingen
werkte.

### 3d. Teller op de nalees-pagina klopt niet

`/api/teksten/nalezen` deelt het aantal producten mét tekst door het aantal
leverbare producten en komt op 101,4%. Hij telt alle producten met tekst
(inclusief niet-leverbare) tegen alleen de leverbare. Kleine rekenfout,
verwarrende meter.

---

## 4. Losse einden

- **Nieuwe producten zonder tekst.** De routine (`teksten_bijwerken`) draait elke
  6 uur en pakt er hoogstens 25 per keer. Stond op 16 à 25 stuks. Kijken of dat
  getal daalt; blijft het staan, dan draait de job niet.
- **19 aangestreepte teksten** staan opgeslagen maar niet op de site. Vijftien
  daarvan waren setjes, die zijn inmiddels naar Apparaatsets verhuisd — de vraag
  is of hun tekst daar wél klopt. Te lezen via
  `/api/teksten/nalezen?vlaggen=1`.
- **Apparaatsets controleren.** De categorie bestaat en bevat producten, maar het
  exacte aantal is nog niet nageteld tegen de verwachte 51. De vijf
  niet-apparaten zijn wel bevestigd verdwenen (audit geeft 0).
- **Proefteksten opruimen.** `proef-v1` (17 rijen) en `proef-v2` (28 rijen) staan
  nog in `ai_content` en worden nergens gebruikt. Mogen weg.
- **`AI_BEHEER_SLEUTEL` is verwijderd** uit Railway, dus `/api/teksten/start`,
  `ophalen` en `publiceren` staan op slot (503). Nodig voor een nieuwe grote
  batch? Nieuwe waarde neerzetten, gebruiken, daarna weer weghalen.

---

## 5. Waar we op wachten (niets aan te doen)

- **EPREL-API (Brussel).** Aanvraag verstuurd 26 juli 's avonds, nog geen
  antwoord. Nodig voor punt 3b en voor het vullen van het Model-veld (74% is nu
  leeg; Coolblue levert er 616 aan van de 1237 die wij van hen volgen).
- **De zevende winkel** (TradeTracker / Voordeligwitgoed.nl). Feed nog niet
  binnen.

---

## 6. Geparkeerd: hoort een vergelijker wel in Merchant Center?

Google's beleid: *"You're not allowed to use Shopping to promote affiliate or
pay-per-click links to products, except when participating as a Comparison
Shopping Service (CSS) in a CSS program country."* Nederland is zo'n land.

Zelf een CSS worden kan niet: dat vereist producten van **minstens 50
verschillende winkeldomeinen** per land, en wij hebben er zes.

**Maar Google klaagt hier niet over.** De enige afkeuringsreden is het
ontbrekende `availability`-veld. Deze vraag dus geparkeerd tot punt 1 een
antwoord geeft. Blijven de afkeuringen na de reparatie staan, dan is dit het
volgende spoor — en dan is de conclusie waarschijnlijk: die automatische bron
uitzetten en Merchant Center loslaten.

---

## Wat er 27 en 28 juli is gebeurd

**27 juli.** Alle 2806 leverbare producten kregen een eigen beschrijving; 2787
staan live. De verkooptekst van de winkel — woordelijk gelijk aan die bij Bol en
de fabrikant — is van de productpagina's verdwenen. Kosten: **€ 14,34** voor 2806
teksten, een halve cent per stuk. Verder: drie zinsvarianten in het
categoriecontext-blok, merk-naar-merk-links op de merkpagina's, een
verantwoordingspagina op `/productteksten`, een noodrem van € 5 per etmaal, een
automatische controle op elke tekst, en een routine die nieuwe producten vanzelf
van tekst voorziet.

Ook: 5 artikelen die geen apparaat zijn van de site gehaald (een stellingkast en
een serviesset onder Magnetrons, waterfilters onder Koffiemachines, een
geurfilter onder Afzuigkappen, een borstel onder Stofzuigers) en 51 setjes naar
de nieuwe categorie Apparaatsets. Gevonden door de eigen productteksten te
doorzoeken — het model had ze zelf al benoemd.

**28 juli.** Twee Google-meldingen uitgezocht. Merchant Center bleek alle
producten af te keuren op één ontbrekend veld; Search Console liet zien dat het
grote tekstproject op één cijfer al aanslaat (100 → 4) en op het andere nog niet
(340 → 918).

---

## Drie lessen die het waard zijn te onthouden

Alle drie kwamen ze uit een fout die eerst gemaakt is.

**Een zeef toetsen op je eigen vangst bewijst niets.** De tekstcontrole werd
aangescherpt en getoetst op de 87 zinnen die de oude versie al had gevonden. Zo'n
toets kan per definitie geen nieuwe valse treffers laten zien; de nieuwe versie
leverde er 46 op en was strikt slechter.

**Een verbinding die je nergens bewaart, wordt opgeruimd terwijl je er nog uit
leest.** `Anthropic(...).messages.batches.results(id)` op één regel liet de batch
halverwege afbreken. Lokaal onvindbaar, want daar was geen echte verbinding.

**Meet voordat je sleutelt, ook als de diagnose voor de hand ligt.** Op 28 juli
is er drie keer aan hetzelfde markup-blok gezeten voordat bekend was wat Google
zelf als reden opgaf. Die reden bleek iets anders dan de eerste twee ingrepen
aanpakten. Eén klik in Merchant Center had dat vooraf verteld.
