# Terugkoppeling aan de designchat — 26 juli 2026

Van: de bouwer. Voor: de designchat.

Dit document doet drie dingen. Het meldt wat er sinds jullie laatste spec is
gebouwd, waar er bewust van jullie ontwerp is afgeweken en waarom, en het legt
één vraag terug.

Alle cijfers hieronder zijn gemeten op productie op 26 juli, niet lokaal. De
ontwikkeldatabase heeft 10 producten met 4 spec-velden en geeft een verkeerd
beeld van hoe iets eruitziet.

---

## 1. Wat er live staat

### Categoriecontext op de productpagina — nieuw, niet uit jullie spec

Een alinea met onze eigen meting over de hele categorie, onder het
aanbiedingenblok:

> **Waar dit model staat tussen 423 stofzuigers**
>
> Dit model kost € 157,00: van de 422 andere stofzuigers die wij volgen zijn er
> 333 duurder en 88 goedkoper. De prijs in deze categorie loopt van € 56 tot
> € 1.599; de middelste helft zit tussen € 169 en € 479. Wij volgen 44
> stofzuigers van Bosch; 34 daarvan zijn duurder dan dit model.

Dit is er gekomen omdat Google 449 van onze pagina's beoordeelde en er 100
oversloeg met de reden "gecrawld, momenteel niet geïndexeerd" — een oordeel over
de inhoud. Zo'n pagina bevatte titel, prijs, een knop en de
leveranciersbeschrijving, en die beschrijving staat woordelijk ook bij Bol en
bij de fabrikant.

De twee prijszinnen werken op élke productpagina: elk apparaat heeft een prijs
en elke categorie is groot genoeg. Dat raakt precies de dunne pagina's — de 65%
zonder specificaties en de 57% met één winkel.

Bewust lopende tekst en geen cijferraster: het probleem is dat er te wéinig
inhoud staat, en een dashboard met losse getallen leest als schermmeubilair.

Elk onderdeel verdwijnt als de data ontbreekt. Geen schatting, nergens
"onbekend".

### Verfijningslinks op de productpagina — nieuw

Onder dat blok, in dezelfde pilvorm als op de categoriepagina:

> **Meer wasmachines bekijken**
> `AEG wasmachines (19)` `Wasmachines met energielabel A (25)` `Voorlader (21)`

Uitsluitend naar facetpagina's die al bestaan en al in de sitemap staan. Geen
nieuwe filtercombinaties genereren — dat zou honderden extra dunne pagina's
opleveren, en dat is dunne inhoud bestrijden met meer dunne inhoud.

### Kruimelpad met merkstap

`Home / Wasmachines / AEG / <model>`, en dezelfde stappen in de
BreadcrumbList-structured-data. Google toont dat pad in de zoekresultaten, en
"witgoedaanbod.nl › Wasmachines › AEG" is daar concreter dan "› Wasmachines".

De merkstap verschijnt alleen als die facetpagina echt bestaat. Dat bleek geen
formaliteit: een niet-leverbaar apparaat van een merk dat verder niets leverbaar
heeft, zou naar een 404 hebben gewezen.

### Filterzijbalk gerepareerd

Wasmachines gingen van

`Waarde energielabel | Toerental centrifuge | Kleur | Top load of voorlader | Stand display | Positie deur scharnier`

naar

`Energielabel | Vulgewicht | Toerental | Kleur | Type lader | Product gewicht`

Drie dingen: de velden waar kopers op kiezen krijgen voorrang, de koppen staan
niet meer in feed-taal, en acht ruisvelden zijn uitgesloten (deurscharnier,
steenkoolborstel, CE-markering, de drie losse buitenmaten).

Waarom vulgewicht ontbrak is leerzaam: de zijbalk koos de zes vaakst
voorkomende spec-velden, maar op wasmachines zit vrijwel élk veld op exact 46
van de 255 producten — dezelfde 46 machines die überhaupt specs hebben. Bij dat
gelijkspel besliste de volgorde waarin de feed zijn velden aanlevert. Puur
toeval, geen keuze.

### Twee verzonnen uitspraken over energielabels weggehaald

Ovens leveren als energielabel de tekst "Energielabel niet van toepassing". Op
vijf plaatsen werd daarvan de eerste letter gepakt, en die is een E. Twee daarvan
stonden live:

- `/category/ovens/energielabel/e` stond in de sitemap en meldde "Dit zijn de 1
  zuinigste modellen (energielabel E)". Erop stond een pizzaoven zonder
  energielabel.
- De categoriepagina van ovens beantwoordde "Wat is het zuinigste energielabel
  dat nu te koop is?" met "Energielabel E" — in FAQPage-structured-data, dus dat
  kon als rich result bij Google verschijnen.

Ook de teksten op die facetpagina's klopten niet: op `/energielabel/g` stond "de
1 zuinigste modellen", terwijl een G-label juist het mínst zuinige apparaat is.

---

## 2. Waar er van jullie spec is afgeweken, en waarom

Dit is het deel dat voor jullie het nuttigst is.

### Prijsverloop: drie onderdelen niet gebouwd

Jullie vragen om periodeknoppen "90 dagen / 1 jaar", maandlabels onder de
grafiek, en de subregel "Laagste prijs in 90 dagen. Nu € 40 onder het
gemiddelde."

**Wij meten sinds 14 juli.** Dat is twaalf dagen. Een steekproef van 45
productpagina's op productie:

| Uitkomst | Aantal |
|---|---|
| Met grafiek | **0** |
| "te weinig dagen" (drempel staat op 14) | 23 |
| "prijs is niet veranderd" | 22 |

Twee knoppen die allebei dezelfde twaalf dagen tonen zijn geen keuze, maandlabels
over 90 dagen worden twaalf keer "juli", en "onder het gemiddelde van 90 dagen"
is een uitspraak over een venster waarvan we 13% hebben. Die drie kunnen zodra er
drie maanden historie ligt; de rest van de grafiek is er klaar voor.

De grafiek is wel compacter geworden (van 640×220 naar 640×150), het raster is
vervangen door twee assen, en er staat een punt op de huidige prijs met het
bedrag ernaast.

### De groene punt is niet altijd groen

Jullie schrijven "een groene punt op de huidige waarde". Dat gaat uit van goed
nieuws — jullie voorbeeldtekst is "nu € 40 onder het gemiddelde". Bij een
stijgende prijs staat die punt op het duurste moment dat wij ooit maten, en groen
betekent op deze site besparing. Daar is het nu een positiemarkering in gewone
inkt.

### Eén lijn per winkel, niet één blauwe lijn

Jullie vragen "één polyline in merkblauw". Meerdere winkels naast elkaar is
precies wat deze site te bieden heeft; die samenvoegen tot één lijn gooit de
vergelijking weg. De kleuren volgen de winkel, nooit de positie.

### De grafiekhoogte kan niet allebei

5a vraagt 150px, 5b vraagt 84px. De desktopkolom is ongeveer 2,4× zo breed als
de mobiele, maar de gevraagde hoogtes verhouden zich als 1,8. Eén beeldverhouding
haalt die twee niet allebei. Wij hebben mobiel op maat gehouden (79px) en desktop
komt daardoor op 190px in plaats van 150.

Als jullie desktop echt op 150 willen, moet de SVG uitgerekt worden en dan worden
de punten ovalen. Zeg het als jullie dat liever hebben.

### Weergavenamen voor filters — toevoeging, niet in jullie spec

De filterkoppen stonden in feed-taal ("Waarde energielabel", "Laadvermogen
wasmachine"). Er is nu een vertaallaag naar kopers-taal ("Energielabel",
"Vulgewicht"). De sleutel waarop gefilterd wordt blijft de feednaam, dus URL's en
bestaande facetpagina's veranderen niet.

---

## 3. Wat Search Console laat zien

Property: domein-property `sc-domain:witgoedaanbod.nl`, DNS-geverifieerd.

| Reden | Stand 26 juli | Betekenis |
|---|---|---|
| Geïndexeerd | 137 | het getal dat omhoog moet |
| Gevonden – niet geïndexeerd | 340 | wachtrij, geen actie |
| **Gecrawld – niet geïndexeerd** | **100** | Google vond ze te dun |
| Pagina met omleiding | 7 | correcte 301's |
| Serverfout (5xx) | 1 | opgelost 26-07 |
| Niet gevonden (404) | 1 | opgeruimde pannenset |

**137 geïndexeerd van 3281 URL's in de sitemap.** Dat is 4%.

De 100 "gecrawld – niet geïndexeerd" zijn de aanleiding voor bijna al het werk
hierboven: dat is een oordeel over inhoud, niet over links.

Twee bevindingen die de moeite van het melden waard zijn:

**De ene serverfout was geen serverfout.** Acht productpagina's waren via interne
links onbereikbaar door een kale `%` in de slug. Eén 5xx bleek dus acht kapotte
pagina's.

**De sitemap bevatte een pagina die op een leesfout was gebouwd** — de
ovens-energielabelpagina hierboven. Google crawlde die dus, vond één pizzaoven,
en zag een pagina die beweerde het zuinigste model te tonen.

### Wat er nu in de sitemap staat

| Soort | Aantal |
|---|---|
| Productpagina | 2814 |
| Merk binnen categorie | 281 |
| Merkpagina globaal | 114 |
| Gids of blog | 24 |
| Energielabelpagina | 22 |
| Categoriepagina | 12 |
| Subtypepagina | 5 |
| Overig | 9 |
| **Totaal** | **3281** |

---

## 4. Wat een externe beoordeling van tien vergelijkers opleverde

Er is een peiling gedaan over tien Nederlandse witgoedvergelijkers. Uitkomst:

1. Kieskeurig.nl — 550+ wasmachines, filters op vulgewicht, toerental, decibel,
   energieklasse én wasprogramma, reviews met cijfers, prijshistorie, vaak 4–7
   winkels per product
2. Tweakers.net
3. Vergelijk.nl
4. Knibble.nl
5. Beslist.nl
6. **Witgoedaanbod.nl**
7. Kelkoo.nl
8. Slimster.nl
9. Witgoed.com
10. Productenvergelijker.nl

Lof: rustig, snel, duidelijke categorieën, prijshistorie, koopgidsen, net
cookie- en affiliateverhaal.

Kritiek: zes winkels is weinig, veel producten hebben maar één prijs, geen
gebruikersreviews, geen filters op vulgewicht/toerental/energieklasse, en bijna
niemand kent de naam.

### Drie kanttekeningen

**Zesde van tien leest te vriendelijk.** Wat eronder staat, is grotendeels
verlaten: Kelkoo toont maanden oude data, Slimster is een offertesite waar
witgoed een restant is, Witgoed.com heeft nog letterlijk "schoenen" in de eigen
tekst staan, Productenvergelijker draait op een catalogus uit 2023. Van de sites
die écht werken staan we laatste.

**Het minpunt over de filters klopte maar half.** Toerental en energielabel
stónden er; alleen vulgewicht ontbrak echt. Maar de beoordelaar had wel iets
gezien: die filters heetten in feed-taal en stonden dichtgeklapt, en het
energielabelfilter had twee opties omdat maar 46 van de 255 wasmachines dat veld
gevuld hebben — waarvan 45 label A. Een filter dat niets onderscheidt bestaat in
de praktijk niet. Dat is inmiddels aangepakt.

**Bijna alle kritiek is één probleem, geen vijf.** Zes winkels, "veel producten
met één prijs" en "filters die niets discrimineren" zijn drie symptomen van te
weinig data per product. Precies hetzelfde tekort waardoor Google 100 pagina's te
dun vindt.

### De cijfers achter dat tekort

Winkeldekking, gemeten vandaag: **43% van de producten heeft twee of meer
aanbiedingen** (1212 van 2814). Bij wasmachines 25%.

Onderzocht en uitgesloten: het koppelen wérkt. Van 247 wasmachines zit er 53 in
de Expert-feed, en daarvan waren er al 52 gekoppeld. Matchen op merk plus
modelcode gaf nul extra treffers. **De winkels voeren onze modellen simpelweg
niet.**

Wat elke winkel toevoegt (`onmisbaar_voor` = aantal producten waarbij die winkel
de énige is met een tweede prijs):

| Winkel | Aanbiedingen | Enige winkel bij | Onmisbaar voor |
|---|---|---|---|
| Coolblue | 1422 | 728 | 239 |
| Expert | 921 | 14 | 207 |
| MediaMarkt | 1120 | 482 | 189 |
| EP | 860 | 14 | 138 |
| Bol | 695 | 364 | 103 |
| Alternate | 15 | 0 | 2 |

De strategische vraag daarachter: **Bol bepaalt nu wat er bestaat** en de andere
winkels kunnen alleen aansluiten. Kieskeurig doet het andersom. Dat is
vermoedelijk waarom zij 4 tot 7 winkels per product halen en wij 1 tot 2.

---

## 5. De vraag terug aan jullie

Kijk naar de hele site zoals Google ernaar kijkt, en zeg wat er moet veranderen
om beter gevonden en sneller gecrawld te worden.

Concreet zouden wij graag jullie oordeel horen over:

1. **4% indexering.** 137 van 3281. Wat zou volgens jullie het eerst moeten
   veranderen om dat te verhogen — en zit dat in de pagina's zelf, in de
   structuur ertussen, of in wat we in de sitemap zetten?

2. **Zetten we te veel in de sitemap?** 2814 productpagina's aanbieden terwijl er
   137 geïndexeerd zijn, kan lezen als een bak dunne pagina's. Is het beter om
   de sitemap te beperken tot producten die iets te vergelijken hebben — of de
   prioriteit naar dekking te laten meebewegen? De catalogus blijft hoe dan ook
   volledig bereikbaar; het gaat alleen om wat we actief aanbieden.

3. **De 57% één-winkel-pagina's.** Ontwerp 5c maakt die draaglijk en de
   categoriecontext geeft ze eigen inhoud. Is dat genoeg om ze indexeerbaar te
   maken, of hoort daar iets anders bij?

4. **Interne linkstructuur.** Elke productpagina wijst nu naar zijn categorie,
   zijn merkpagina, zijn energielabelpagina en zijn subtype. De categoriepagina
   wijst terug. Missen jullie een laag — bijvoorbeeld tussen categorie en
   product, of tussen merken onderling?

5. **Crawlsnelheid.** Wat kunnen wij doen zodat Google vaker langskomt? Wij
   verversen meerdere keren per dag; de `lastmod` in de sitemap beweegt mee.

6. **Wat wij níet moeten doen.** Als jullie iets voorstellen dat nieuwe URL's
   oplevert, noem er dan bij hoeveel het er worden. Wij hebben nu 3281 URL's met
   137 geïndexeerde; honderden nieuwe filtercombinaties zouden dat verhoudingsgetal
   alleen slechter maken.

### Twee dingen die wij vooraf zouden willen meegeven

**Alles wat wij bouwen moet waar zijn.** Dat is de rode draad geworden: geen
gegokt modelnummer, geen bezorgkosten die de feed niet levert, geen koopadvies bij
drie dagen historie, geen energielabel dat uit een leesfout komt. Als een
voorstel iets belooft dat de data niet draagt, bouwen wij het niet — en dat is
geen onwil, het is de enige reden dat deze site iets waard is naast een webshop.

**Het echte tekort is niet visueel.** 43% dekking en 35% gevulde specificaties
zijn wat de site tegenhouden. Elk ontwerp maakt dat draaglijker; geen ontwerp
lost het op. Als jullie ideeën hebben die dekking of spec-vulling verhogen, zijn
die meer waard dan elk visueel punt.
