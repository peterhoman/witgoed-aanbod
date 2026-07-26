# Stand van zaken

Laatst bijgewerkt: 26 juli 2026 (na de SEO-ronde). Alles hieronder staat live tenzij anders vermeld.

---

## Dagelijkse controle

Vier cijfers, samen twee minuten. Noteer ze, want de bewéging zegt meer dan de
losse waarde.

### 1. Site zelf — één commando

```bash
python -c "
import urllib.request, re, random, json, time
B='https://www.witgoedaanbod.nl'
xml=urllib.request.urlopen(B+'/sitemap.xml',timeout=60).read().decode('utf-8','ignore')
urls=[u for u in re.findall(r'<loc>([^<]+)</loc>',xml) if '/product/' in u]
random.seed(11); steek=random.sample(urls,40); met=0
for u in steek:
    try: met += 1 if 'specs-card' in urllib.request.urlopen(u,timeout=30).read().decode('utf-8','ignore') else 0
    except Exception: pass
    time.sleep(0.05)
print('specificaties : %d%%' % (100*met/len(steek)))
d=json.load(urllib.request.urlopen(B+'/api/sync-status',timeout=30))
w=d['winkeldekking']['totaal']
print('winkeldekking : %d%% (%d van %d)' % (w['dekking_pct'],w['meerdere_winkels'],w['producten']))
for r in (d.get('paginaweergaven') or [])[:2]:
    print('%s  product=%s categorie=%s verhouding=%s' % (r['datum'],r.get('product'),r.get('categorie'),r.get('product_per_categorie')))
"
```

| Cijfer | Stand 26 juli | Wat je wilt zien |
|---|---|---|
| Specificaties gevuld | 35% | omhoog; was 18% op 24 juli, 28% op 25 juli |
| Winkeldekking | 43% (wasmachines 25%) | omhoog; beweegt alleen als er een winkel bijkomt |
| product_per_categorie | 2,1 tot 5,8 | omhoog = bezoekers komen dieper de site in |

Staan de specificaties na een paar dagen stil, dan haalt de Bol-sync ze niet op
en moet dat opnieuw onderzocht worden.

### 2. Google Search Console

Link, let op de `/u/0/`:

```
https://search.google.com/u/0/search-console?resource_id=sc-domain:witgoedaanbod.nl
```

Kijk bij **Indexeren → Pagina's**:

| Reden | Stand 26 juli | Betekenis |
|---|---|---|
| Geïndexeerd | 137 | het getal dat omhoog moet |
| **Gevonden – niet geïndexeerd** | **340** | **Google kent de URL en besluit hem niet te crawlen** |
| Gecrawld – niet geïndexeerd | 100 | Google vond ze te dun: specs en dekking |
| Pagina met omleiding | 7 | correcte 301's, geen actie |
| Serverfout (5xx) | 1 | opgelost 26-07, validatie loopt |
| Niet gevonden (404) | 1 | opgeruimde pannenset, geen actie |

**Hier stond dat die 340 een wachtrij was waar geen actie voor nodig is. Dat
klopt niet.** De designchat wees erop en heeft gelijk: "gevonden – niet
geïndexeerd" is Google die de URL kent en besluit hem niét op te halen. Het is
het grootste getal van de drie, en het is een structuurprobleem, geen
inhoudsprobleem. Daar zit het meeste verlies.

**Waar je op moet letten:** een nieuwe reden die erbij komt, of "Gecrawld – niet
geïndexeerd" dat hard oploopt. Dat laatste betekent dat Google steeds meer
pagina's te dun vindt.

**Vanaf nu per soort af te lezen.** De sitemap is opgesplitst in zeven
bestanden (producten, categorieën, merken, merk-per-categorie, facetten, gidsen,
overig) met `/sitemap.xml` als index. Search Console rapporteert dekking per
bestand, dus je ziet nu of die 137 productpagina's zijn of categoriepagina's —
en dus of een ingreep werkt. Zonder die splitsing was er niets te meten.

Verschijnt er weer een **serverfout**, behandel die niet als klein. Op 26 juli
bleek één 5xx te komen door acht productpagina's die via interne links
onbereikbaar waren (kale `%` in de slug).

---

---

## Werkwijze — lees dit voor je iets bouwt

Deze regels zijn niet vooraf bedacht maar deze week duur geleerd. Elke regel
staat er omdat het één keer misging.

**Meet op productie, niet lokaal.** De lokale database heeft 10 producten met
4 spec-velden; productie heeft er 2813 met tot 77. Lokaal ziet alles er goed
uit. Elke conclusie over hoe iets "eruitziet" of "werkt" moet tegen
witgoedaanbod.nl gecontroleerd worden. Meerdere keren bleek een bevinding een
artefact van de dunne lokale data.

**Test in een draaiende pagina, niet alleen in de functie.** Twee keer werkte
losse logica prima terwijl de pagina iets anders deed:
- een CSS-regel voor verborgen filteropties verloor op specificiteit, dus de
  "Meer (n)"-knop toonde het juiste aantal maar verborg niets;
- een Jinja-filter gebruikte `is number` op een tekstwaarde — dat is altijd
  onwaar, dus er werd nooit iets weggefilterd.
Beide gevonden door de knop echt in te drukken.

**Pas op met trefwoorden als deelstring.** `'ean'` zit ook in `cleansing`,
waardoor "Maximum cleansing temperatuur" bij "Merk en model" belandde. Dit is
twee keer gebeurd (ook bij de kleurnormalisatie). Test elke trefwoordenlijst
tegen de echte veldnamen uit `/api/category-specs/<slug>`.

**Beweer niets wat de data niet draagt.** Dit is de rode draad van het hele
project:
- geen koopadvies bij drie dagen historie en een vlakke lijn (dat was een
  tautologie);
- geen "0 dB" tonen, dat is een leeg veld;
- geen gegokt modelnummer uit de titel;
- geen bezorgkosten invullen die de feed niet levert;
- geen alternatieven tonen die geen alternatief zijn.
Ontbreekt data, laat het onderdeel weg. Nooit schatten.

**Controleer wat de designchat beweert.** De samenwerking werkt goed — hun
ontwerpoordeel is consistent scherp — maar ze kennen de code niet en hebben
zes keer iets beschreven dat er al was of er juist niet was: een branch die
niet bestond, chevrons die nooit gebouwd waren, een titel-clamp die er al
zat, een "vanaf"-weergave die al werkte, een specblok dat wél bestond, en een
prijsverschil-cijfer dat nergens stond. Verifieer eerst, bouw daarna. Meld het
ook terug — dat scheelt hun de volgende ronde.

**Een leesfout plant zich voort.** "Energielabel niet van toepassing" werd via
`waarde[:1]` een label E, en die ene fout stond op vijf plaatsen: de sitemap, de
facetroute, de FAQ, de categoriecontext en het sjabloon. Vier repareren en de
vijfde vergeten leverde een interne link naar een 404 op. Zit een regel op meer
dan één plek, zet hem dan op één plek en laat de rest hem gebruiken.

**Nooit naar `main` pushen.** Railway zet main automatisch live. Werken op een
branch, pull request, de eigenaar merget zelf.

**Schermafbeeldingen renderen op dubbele schaal.** Een header die 750px lijkt
is er 376. Meet met JavaScript, kijk niet naar het plaatje.

---

## Wat er 26 juli 's middags bij kwam — de SEO-ronde

Acht ingrepen, allemaal gericht op één ding: pagina's die Google wel crawlt maar
niet indexeert.

**Categoriecontext op elke productpagina.** Een alinea met onze eigen meting over
de categorie: "Dit model kost € 157: van de 422 andere stofzuigers die wij volgen
zijn er 333 duurder en 88 goedkoper." Werkt op élke pagina, ook de 65% zonder
specificaties en de 57% met één winkel — precies de dunne. Lopende tekst en geen
cijferraster, want het probleem is dat er te wéinig inhoud staat.

**Eigen meta-descriptions.** 84% van de productpagina's had de
leveranciersbeschrijving, hard afgekapt midden in een woord ("...8 automatische
pr") — en die tekst staat woordelijk ook bij Bol en de fabrikant. Nu komt hij uit
onze database en is hij per pagina uniek.

**Sitemapdatums klopten niet.** `lastmod` gaf onvoorwaardelijk de datum van
vandaag, voor alle 3281 URL's. Een sitemap die dagelijks beweert dat alles
veranderd is, leert Google om `lastmod` hier te negeren. `products.updated_at`
was geen oplossing: `last_synced` wordt bij elke sync onvoorwaardelijk gezet, dus
dat veld schuift mee. Nu komt de datum uit `price_history`, want dat schrijft
alleen weg bij een échte prijswijziging.

**Crawldiepte van 12 naar 2.** De categoriepagina toont 24 producten met alleen
vorige/volgende, dus het laatste product ligt elf klikken diep. De merkfacetten
zijn de korte route, maar die kapten zelf ook op 24 af — 31 facetten zijn groter,
samen 437 producten. Nu 100 per pagina, en alle merken worden gelinkt in plaats
van de eerste twaalf.

**Verfijningslinks en kruimelpad met merk.** Elke productpagina wijst nu ook naar
zijn merk-, energielabel- en subtypepagina, en het kruimelpad heeft een merkstap
die ook in de structured data staat. Uitsluitend naar pagina's die al bestaan;
geen nieuwe filtercombinaties.

**Filterzijbalk gerepareerd.** Van "Waarde energielabel / Toerental centrifuge /
Stand display / Positie deur scharnier" naar "Energielabel / Vulgewicht /
Toerental / Type lader". Vulgewicht ontbrak door toeval: vrijwel élk spec-veld
zit op dezelfde 46 van de 255 wasmachines, dus bij dat gelijkspel besliste de
feedvolgorde.

**Twee verzonnen uitspraken over energielabels weg.** Ovens leveren "Energielabel
niet van toepassing"; de eerste letter daarvan is een E. Daardoor stond er een
facetpagina in de sitemap die beweerde het zuinigste model te tonen (een
pizzaoven), en beantwoordde de categoriepagina "wat is het zuinigste label?" met
"E" — in FAQPage-structured-data, dus zichtbaar in Google.

**Sitemap opgesplitst per soort.** Zie hierboven bij Search Console.

---

## Wat er 25 en 26 juli live is gegaan

Achttien pull requests.

**Filters gaven verkeerde antwoorden.** Merken werden per schrijfwijze gesplitst
(AEG naast Aeg), kleurwaarden bevatten capaciteit en kortingen. Wie op rvs-ovens
filterde zag er 4 van de 24. Aantallen kloppen nu overal.

**Zijbalk van 1647 naar 715px**, sticky op desktop, geen scrollgebied-in-scrollgebied
meer. Filtergroepen klappen in; de gekozen waarden staan in de dichtgeklapte kop.

**Twee fouten op elke pagina van de site**: het logo was een tweede `h1` (overal
dezelfde tekst), en tussen 769 en 1100px kon je de site zijwaarts wegschuiven.

**Nieuwe productpagina** volgens `docs/design/DESIGN_SPEC_productpagina.md`:
winkeloverzicht als hoofdzaak, kosten over tien jaar, geordende specificaties, en
een apart ontwerp voor apparaten bij één winkel (5c) — dat geldt voor ruim de helft
van de catalogus.

**Bezoekers blijven op de site.** De knop op productkaarten ging bij één winkel
rechtstreeks naar de verkoper; dat gold voor 57% van de kaarten. Nu leiden alle
kaartknoppen naar de eigen productpagina, en pas dáár staat "Naar Coolblue →".

**Gelijke prijzen zijn eerlijk.** Bij drie winkels à € 569 kreeg er één "laagste" en
de andere twee "+ € 0,00". Nu krijgt elke winkel met de laagste prijs dat label, en
de volgorde wordt bepaald door de bezorgkosten in plaats van het alfabet.

**Twee lekken in de sync gedicht.** EAN's met weggevallen voorloopnul (27 apparaten),
en specificaties die bij elke mislukte detail-aanroep werden gewist (de 82% hierboven).

---

## Wat nog open staat

### 1. Dekking verhogen — het enige dat echt uitmaakt
43% van de apparaten heeft meer dan één winkel; bij wasmachines 25%.

Onderzocht en uitgesloten: het koppelen werkt. Van 247 wasmachines zit er 53 in de
Expert-feed en daarvan waren er al 52 gekoppeld. Matchen op merk plus modelcode gaf
nul extra treffers. **De winkels voeren onze modellen simpelweg niet.**

Twee chats gaven strategisch advies; ze zijn het eens: volledige catalogus behouden
voor SEO, maar de site inrichten rondom producten die écht vergelijkbaar zijn.
Concrete ideeën die nog niet gebouwd zijn:

- Een dekkingsscore als sorteerfactor in categorieën (voorzichtig: eerst als
  tiebreaker, niet als hoofdsortering — anders zakken populaire modellen weg puur
  omdat één winkel ze voert).
- Sitemap-prioriteit naar dekking.
- Nieuwe feeds beoordelen op "hoeveel producten gaan van 1 naar 2 winkels", niet op
  hoeveel producten ze bevatten. **Dit is gebouwd**: `winkelbijdrage` op
  /api/sync-status. Stand 26 juli: Coolblue 237, Expert 202, MediaMarkt 190,
  EP 125, Bol 105, Alternate 1. Die laatste laat zien wanneer een winkel niets
  toevoegt.
- De grote vraag: is Bol wel de juiste basis voor de catalogus? Nu bepaalt Bol wat
  er bestaat en kunnen de anderen alleen aansluiten.

### 2. Prijsverloop-grafiek — grotendeels af, drie onderdelen wachten op tijd
Compacter (640×150), raster vervangen door twee assen, punt op de huidige prijs.
Die punt is alleen groen als de huidige prijs ook de laagste is die wij ooit
maten: de spec vroeg altijd groen, maar bij een stijgende prijs staat hij dan op
het duurste moment ooit.

**Niet gebouwd, en dat is bewust.** Periodeknoppen "90 dagen / 1 jaar",
maandlabels en "nu € 40 onder het gemiddelde" gaan alle drie uit van maanden
historie. Wij meten sinds 14 juli. Steekproef van 45 productpagina's op 26 juli:
**nul met een grafiek**, 23 "te weinig dagen", 22 "prijs niet veranderd".

De drempel staat op 14 dagen, dus rond **28 juli** verschijnt de grafiek voor het
eerst op producten met een prijswijziging. Dat is het moment om te kijken of hij
klopt — niemand heeft hem ooit op productie gezien.

### 2b. Modelcode en EPREL — het spoor dat spec-vulling kan oplossen
De EU-energielabeldatabase EPREL is verplicht voor wasmachines, drogers,
koelkasten, vaatwassers en ovens, en bevat precies de velden die bij ons leeg
zijn: label, kWh, vulgewicht, toerental, geluid, waterverbruik, afmetingen.
Officiële bron, dus te vermelden op de site — een vertrouwenssignaal dat geen
webshop heeft.

Twee horden, allebei gemeten op 26 juli:

- **De API vraagt een sleutel.** Elk eindpunt geeft 403 "Missing Authentication
  Token". Aan te vragen bij de Europese Commissie. Zonder sleutel geen data.
- **EPREL matcht op modelcode.** Ons `Model`-veld is bij 74% leeg, en van de 26%
  die gevuld is bevat een deel geen code maar rommel ("Amerikaanse koelkast").

Onderzocht en uitgesloten als bron voor die modelcode: Expert (9049 producten,
geen modelveld), EP (4629, geen modelveld), Alternate (levert wél MPN bij 26169
producten, maar nul overlap met onze catalogus — 0 van 39 in een steekproef).
Bol levert zijn specificaties compleet; het lege `Model`-veld is Bol's data, geen
fout in onze verwerking. MediaMarkt en Coolblue zijn nog niet bekeken; daarvoor
staat `/api/feed-velden/<winkel>` klaar.

**Wat het wél kansrijk maakt: 69% van de producttitels bevat een
modelcode-vorm** (steekproef van 49; één had meerdere kandidaten, en dat was een
was/droog-set). Dat botst niet met de regel "nooit een modelnummer uit de titel
gokken", want de kandidaat wordt niet getoond maar aan EPREL voorgelegd. Bevestigt
EPREL hem niet, dan gebeurt er niets. Geen bewering zonder bron.

### 2c. Wat de designchat voorstelde en niet doorgaat
Zij stelden voor de catalogus te bouwen op EAN's die in twee of meer feeds
voorkomen, en de circa 1600 solo-producten op `noindex` te zetten. **Afgewezen.**
Het spreekt de koers tegen (volledige catalogus behouden) en het haalt de
categoriecontext weg bij precies de pagina's waarvoor die gebouwd is.

### 3. Voordeligwitgoed.nl via TradeTracker
Aanvraag loopt, winkel moet nog goedkeuren. 447 producten, dagelijks ververst.
Zodra de feed-URL beschikbaar is: vooraf meten hoeveel apparaten van één naar
twee winkels gaan, en bij hoeveel zij de nieuwe laagste prijs worden. Controleer
ook of hun feed bezorgkosten en levertijd levert — bij een prijsvechter is
"goedkoopste productprijs" niet hetzelfde als goedkoopste totaal.

### 4. Screenshots voor de designchat
Van 5a (meerdere winkels), 5b (mobiel) en 5c (één winkel). Lukte niet omdat het
browserpaneel dichtviel; design kreeg in plaats daarvan directe links.

---

## Google Search Console

**Account: `pfmhoman@gmail.com`.** Directe link, sla deze op:

```
https://search.google.com/u/0/search-console?resource_id=sc-domain:witgoedaanbod.nl
```

Let op de `/u/0/`. Met meerdere Google-accounts in dezelfde browser komt Search
Console vaak uit op een ander accountnummer, en dan krijg je het
welkomstscherm te zien alsof er geen property is. Dat is dan misleidend: de
property bestaat wel, je kijkt alleen met het verkeerde account.

Het is een **domein-property** (`sc-domain:witgoedaanbod.nl`), dus hij dekt
www en niet-www, http en https tegelijk. DNS-geverifieerd; het TXT-record
staat bij TransIP:

```
google-site-verification=CwTSwDoBq1Hg1yEr9aYxXcjaURT6VlGagjU3YfX2J-0
```

De losse HTML-verificatietag in `config.py` is iets anders: die is voor
Merchant Center (gratis Shopping-vermeldingen), zelfde account. Beide moeten
blijven staan; Google hercontroleert periodiek.

## Dingen om te weten

- **Lokale database is dun**: 10 producten, 4 spec-velden. Veel is daardoor lokaal
  niet te zien. Wil je het winkeloverzicht met meerdere winkels bekijken, dan moet je
  testaanbiedingen toevoegen.
- **Toestemmingen staan ruim** in `.claude/settings.local.json` (python, awk, curl,
  browsertools). `rm` en `git push` vragen nog wel. Dat bestand blijft buiten git.
- **Nooit naar `main` pushen**: Railway zet dat automatisch live. Werken op een
  branch, pull request, zelf mergen.
- **Ontwerpdocumenten** staan in `docs/design/`.
