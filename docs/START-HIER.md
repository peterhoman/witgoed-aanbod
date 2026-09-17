# Start hier — overdracht aan een nieuwe sessie

Bijgewerkt **17 september 2026, 13:15** (het blok "Dagcontrole 17 september (middag)"
hieronder is het nieuwste, daaronder "Overdracht 17 september, slot"; oudere blokken en hoofdstukken blijven gelden waar de update
niets anders zegt). Lees dit eerst; het projectgeheugen van de chat
(MEMORY.md in de Claude-projectmap) draagt dezelfde feiten compact en is
leidend voor werkafspraken.

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
- Daisycon-feed Witgoedhuis: `curl -sI "https://daisycon.io/datafeed/?media_id=428244&program_id=6570&standard_id=6&language_code=nl&locale_id=1&type=xml&records=5"`
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
