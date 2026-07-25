# Handoff: WitgoedAanbod.nl — visueel redesign categorie- en productweergave

## Overzicht

WitgoedAanbod.nl is een prijsvergelijker voor witgoed die de prijzen van zes winkels
(Bol.com, Coolblue, MediaMarkt, Expert, Alternate, EP) naast elkaar zet. De site is
ongeveer drie weken live. Dit pakket bevat een visueel redesign van de categoriepagina
en de productweergave: strakker, moderner, en mobiel als leidende viewport.

**Doel van deze opdracht: alleen de presentatielaag verbeteren.** De informatiearchitectuur,
de affiliate-links, de filterlogica en de SEO-dragende structuur blijven zoals ze zijn.

## ⚠ Randvoorwaarden — lees dit eerst

Deze zijn door de eigenaar expliciet gesteld. Ze gaan boven elke visuele voorkeur in dit document.

1. **Niet naar `main` pushen.** `main` gaat via Railway automatisch naar productie.
   Werk op een aparte branch en lever een PR op. De eigenaar test lokaal en zet zelf live.
2. **Structuur is SEO-dragend.** Koppenhiërarchie (één `h1`, daarna `h2`/`h3`),
   breadcrumbs, interne links naar categorieën/gidsen/merken, en alle structured data
   (`Product`, `Offer`, `AggregateOffer`, `BreadcrumbList`, `ItemList`) moeten
   ongewijzigd blijven. Stylen mag; DOM-structuur slopen of koppen naar `div` omzetten niet.
3. **Productkaarten, filters en koopknoppen zijn heilig.** Elke affiliate-uitgaande link,
   `rel`-attribuut, tracking-parameter (`subid`, `epi`, `utm_*`) en `data-*`-hook blijft
   intact en op dezelfde plek in de flow. Verander het aantal koopknoppen per kaart niet
   zonder overleg.
4. **De mobiele verbeteringen van deze week komen uit echte gebruikersfeedback.**
   Het inklapbare filter boven de resultaten op mobiel en het filter naast de resultaten
   op desktop zijn bewuste, geteste keuzes. Behoud dat gedrag exact — dit redesign
   verandert alleen de vormgeving ervan.
5. **Geen nieuwe frontend-dependencies** zonder overleg. Wat hier staat is te bouwen met
   CSS die de site al heeft.

## Over de designbestanden

`Witgoed Redesign.dc.html` is een **designreferentie in HTML** — een prototype dat de
bedoelde vormgeving en het bedoelde gedrag toont. Het is **geen productiecode om over te
nemen**. De opdracht is om deze ontwerpen te herbouwen in de bestaande omgeving van de
site (Jinja2/Flask-templates met de huidige CSS-opzet), met de patronen die daar al
gelden. Neem geen inline styles over: zet ze om naar de bestaande klassenstructuur.

Het prototype gebruikt een runtime met eigen `<sc-for>` / `<sc-if>` tags. Dat is puur
prototype-mechaniek. In de echte site zijn dat gewoon `{% for %}` en `{% if %}`.

## Fidelity

**High-fidelity.** Kleuren, typografie, spacing en interacties zijn definitief bedoeld.
Neem de waarden uit *Design tokens* letterlijk over. De structuur eronder is echter
bestaand — pas de bestaande templates aan, bouw geen nieuwe pagina.

Uitzondering: alle **productafbeeldingen zijn placeholders** (gestreepte vlakken met de
tekst "productfoto"). Daar komen de bestaande `wsrv.nl`-image-URL's. Idem voor
"mascotte" — dat is `/static/img/mascot.png`. De winkellogo's staan in het prototype als
tekst; gebruik de echte PNG's uit `/static/img/winkels/`.

## Ontwerpiteraties in het prototype

Het bestand bevat vier iteraties, nieuwste bovenaan. **Alleen turn 4 is de goedgekeurde
richting.** De rest staat er als context voor de gemaakte keuzes.

| id | Naam | Status |
|----|------|--------|
| `4a` | Categoriepagina desktop — filter ernaast | **Te bouwen** |
| `4b` | Categoriepagina mobiel — filter inklapbaar | **Te bouwen** |
| `3a` | Merkblauw, mobiel | Referentie: hier komen de kleurkeuzes uit |
| `2a` | Warm & precies | Verworpen — te warm, past niet bij banner/video |
| `1a` | Precisie | Basis voor de dichtheid en de mono-prijsuitlijning van 4a/4b |
| `1b` | Vertrouwd | Verworpen — kleurpalet paste niet bij de merkkleur |
| `1c` | Contrast | Verworpen — te donker om over gidsen en blog vol te houden |

## Design tokens

Ontleend aan de live site (blauw en oranje zijn de bestaande merkkleuren) en aangevuld
met een neutrale schaal. Als de codebase al variabelen voor blauw/oranje heeft: gebruik
die en voeg alleen de ontbrekende neutralen toe.

### Kleuren

| Rol | Waarde | oklch (referentie) | Gebruik |
|-----|--------|--------------------|---------|
| Merkblauw | `#1c71d8` | `oklch(0.55 0.19 258)` | Header, filterknoppen, actieve chips, primaire acties, links |
| Merkblauw donker | `#1657ab` | `oklch(0.48 0.18 258)` | Hover op blauwe knoppen |
| Merkblauw diep | `#12457f` | `oklch(0.45 0.16 258)` | Categorie-navigatiebalk onder de header |
| Blauw licht (vlak) | `#e8f2fd` | `oklch(0.955 0.028 250)` | Achtergrond keuzehulp- en videogidsblok, actieve-filterbalk |
| Blauw op donker | `#bcd8f5` | `oklch(0.87 0.09 250)` | Het "Aanbod"-deel van het logo, secundaire tekst op blauw |
| Oranje CTA | `#f4682a` | `oklch(0.67 0.19 42)` | **Uitsluitend** de koopknop "Vergelijk prijzen" |
| Oranje CTA hover | `#dc5418` | `oklch(0.6 0.19 42)` | Hover op de koopknop |
| Groen (besparing) | `#218358` | `oklch(0.5 0.13 155)` | Energielabelbadge, prijsverschil, prijsdaling |
| Tekst | `#282b33` | `oklch(0.25 0.015 258)` | Koppen en hoofdtekst |
| Tekst secundair | `#5d626e` | `oklch(0.44 0.02 258)` | Intro's, beschrijvingen |
| Tekst tertiair | `#7b8090` | `oklch(0.52 0.02 258)` | Merknaam op kaart, labels, breadcrumb |
| Kaart | `#fdfdfe` | `oklch(0.995 0.003 250)` | Achtergrond van kaarten en sidebar |
| Paginavlak | `#f7f8fa` | `oklch(0.985 0.005 250)` | Achtergrond van het paginacanvas |
| Vlak subtiel | `#f0f2f6` | `oklch(0.965 0.014 250)` | Filterbalk mobiel, uitgeklapt filterpaneel |
| Lijn | `#e2e5ea` | `oklch(0.9 0.012 250)` | Randen van kaarten, sidebar, inputs |
| Lijn licht | `#eef0f4` | `oklch(0.94 0.012 250)` | Scheidingslijnen binnen kaarten en lijsten |

**Belangrijke kleurregel:** op de huidige site concurreert oranje met de blauwe links.
In dit redesign is oranje **alleen** de koopknop — één oranje element per productkaart.
Alles wat navigeert of filtert is blauw. Verruim dit niet.

**Tweede regel:** geen enkel groot vlak staat op puur `#ffffff`. Het paginacanvas is
`#f7f8fa`, de kaarten daarop `#fdfdfe`. Dit was een expliciete wens ("anders heel wit").

### Typografie

Twee families:

- **Nunito Sans** (400, 600, 700, 800) — alle UI-tekst en koppen. Sluit aan op de
  huidige site.
- **IBM Plex Mono** (500, 600) — **uitsluitend** prijzen, aantallen, tellers en
  eyebrow-labels. Reden: `font-variant-numeric: tabular-nums` laat prijzen in een lijst
  of grid exact onder elkaar uitlijnen, wat vergelijken merkbaar sneller maakt.
  Dit is functioneel, geen decoratie — bewaar het.

| Rol | Family | Size | Weight | Letter-spacing | Line-height |
|-----|--------|------|--------|----------------|-------------|
| H1 desktop | Nunito Sans | 34px | 800 | -0.03em | 1.08 |
| H1 mobiel | Nunito Sans | 24px | 800 | -0.03em | 1.15 |
| Kaarttitel desktop | Nunito Sans | 14px | 700 | -0.01em | 1.32 |
| Kaarttitel mobiel | Nunito Sans | 13.5px | 700 | -0.01em | 1.3 |
| Prijs desktop | IBM Plex Mono | 21px | 600 | -0.025em | 1.1 |
| Prijs mobiel | IBM Plex Mono | 20px | 600 | -0.025em | 1.15 |
| Body / intro | Nunito Sans | 14.5px | 400 | — | 1.55 |
| Sidebar-groepskop | Nunito Sans | 13.5px | 700 | — | — |
| Filteroptie | Nunito Sans | 13px | 400 | — | — |
| Label / meta | Nunito Sans | 11.5px | 400–600 | — | 1.45 |
| Eyebrow ("VIDEOGIDS") | IBM Plex Mono | 10.5px | 400 | 0.12em, uppercase | — |
| Badge / count | IBM Plex Mono | 10.5–11.5px | 600 | — | — |

Alle langere tekstblokken krijgen `text-wrap: pretty`.

### Spacing, radii, overig

- Spacing: 4 / 6 / 8 / 12 / 14 / 16 / 22 / 26 / 28px. Sectiepadding desktop 28px,
  mobiel 16px.
- Radius: 3px badge · 6–8px knop/input · 10px infoblok · 12px kaart en sidebar ·
  999px chip.
- Randen: 1px `#e2e5ea`. Filter-inputs en het zoekveld 1.5px in merkblauw.
- **Geen box-shadows.** Diepte komt van randen en van het lichtverschil tussen kaart
  en canvas. Dit houdt de pagina rustig bij veel kaarten naast elkaar.
- Hover op kaart: `border-color` naar `oklch(0.72 0.08 258)` (≈ `#8fb4e0`).
  Geen transform, geen shadow — voorkomt reflow-ruis in een grid.
- Raakvlakken op mobiel: elke tikbare regel minimaal 44px hoog.

## Schermen

### 1. Categoriepagina — desktop (`4a`)

**Doel:** de bezoeker filtert een categorie terug naar een handvat kandidaten en klikt
door naar de productpagina of direct naar de winkel.

**Canvas:** 1240px contentbreedte. Sectiepadding 28px links/rechts.

**Verticale opbouw, van boven naar beneden:**

1. **Header** — hoogte ±62px, achtergrond merkblauw, tekst wit.
   Links het logo (18px/800, "Witgoed" wit + "Aanbod" in `#bcd8f5`).
   Daarnaast het zoekveld: witte pil, `border-radius: 8px`, `padding: 4px`,
   max-breedte 460px, met een oranje "Zoek"-knop erin (6px radius).
   Rechts uitgelijnd: `♡ Verlanglijst 0`, Koopgidsen, Blog, en een NL-taalpil
   (1px rand, 5px radius). Font 13px.
2. **Categorienavigatie** — balk in merkblauw diep (`#12457f`), padding 11px 28px,
   font 13px in `#e8f2fd`, `gap: 22px`, één regel, horizontaal scrollend bij overflow.
   Alle twaalf categorieën als links — dit is een interne-linkblok, dus behouden.
3. **Breadcrumb** — 12.5px tertiaire tekst, `margin-bottom: 10px`. Blijft `BreadcrumbList`.
4. **Paginakop** — flexrij, `align-items: flex-end`, `justify-content: space-between`.
   Links (max 620px): `h1` "Drogers vergelijken" + intro van één regel met het aantal
   modellen, het aantal merken en het tijdstip van bijwerken.
   Rechts twee kerncijfers, gescheiden door een 1px verticale lijn:
   `6` / "winkels vergeleken" en `€ 128` (in groen) / "gem. prijsverschil".
   Cijfers in IBM Plex Mono 22px/600, labels 11.5px.
   *Het prijsverschil is het argument van de site — daarom staat het in de kop.*
5. **Keuzehulp + videogids** — flexrij, `gap: 16px`, `padding-top: 22px`.
   Beide blokken: achtergrond `#e8f2fd`, 1px rand in merkblauw, 10px radius.
   - Keuzehulp (flexibel breed): ronde witte 42px-badge met vraagteken, dan titel
     15px/700 + subregel 13px, dan rechts een blauwe knop "Start keuzehulp →".
   - Videogids (400px vast): 96×58px videothumbnail met witte ronde play-button
     (24px) erop, dan eyebrow "VIDEOGIDS", titel 14px/700, en de link
     "Lees onze gids →" in 12.5px/600 merkblauw.

   > Op de huidige site staan deze blokken los onder elkaar en zijn ze samen hoog.
   > Hier staan ze naast elkaar en zijn ze compacter. **Beide blokken blijven bestaan
   > met dezelfde links** — dit is puur een hoogtereductie zodat het eerste product
   > eerder in beeld komt.

6. **Merk- en typechips** — wrappende rij, `gap: 8px`, `padding-top: 20px`.
   Witte pil, 1px lijnrand, 999px radius, `padding: 7px 13px`, font 12.5px.
   Hover: rand en tekst naar merkblauw. Sluit af met "Alle merken →" zonder rand,
   in merkblauw 700. Deze chips zijn interne links — behouden zoals ze nu zijn.
7. **Twee kolommen** — flexrij, `gap: 24px`, `align-items: flex-start`.

**Sidebar (262px, vaste breedte, `flex-shrink: 0`):**

Kaart met 12px radius en 1px rand.

- Kop: "Filters" 15px/700 links, "Wissen" 12px/600 merkblauw rechts. 14px 16px padding,
  onderrand.
- Actieve-filterbalk: achtergrond `#e8f2fd`, label "Actief:" 11.5px, daarna elk actief
  filter als blauwe chip met een `×` (999px radius, 11.5px/600, wit op merkblauw).
- Daaronder per filtergroep één rij:
  - **Klikbare kop** (padding 13px 16px): naam 13.5px/700 links; rechts een hint
    (11px tertiair, bv. "€ 0 – € 2.000" of "1 gekozen") en een chevron `▾`/`▴` in
    merkblauw. Hover: achtergrond `#f7f8fa`. Cursor pointer, `user-select: none`.
  - **Uitgeklapte body:** lijst opties, `gap: 9px`, `padding: 0 16px 14px`.
    Per optie: links een 15px checkbox (3px radius, 1.5px rand `#c4c8d2`, gevuld met
    merkblauw als aangevinkt) + het label 13px; rechts het aantal in IBM Plex Mono
    11.5px tertiair. Hover: label naar merkblauw.
  - Elke groep gescheiden door een 1px lijn in `#eef0f4`.
- Groepen en beginstand: **Prijs** (open), **Merk** (open), **Energielabel** (dicht),
  **Type droger** (dicht), **Capaciteit** (dicht).
  → Rationale: de twee filters die het meest gebruikt worden staan open, de rest is
  dichtgeklapt zodat de sidebar niet langer wordt dan de eerste rij producten.
- Afsluitend een blauwe knop over de volle breedte: "149 drogers tonen".

**Resultatenkolom (`flex: 1`, `min-width: 0`):**

- Balk boven het grid: links "**149 drogers** gevonden" (aantal in 700), rechts
  "Sorteren op" + een select-achtige knop met "Laagste prijs" en een chevron.
  14px onderpadding, 1px onderlijn.
- Grid: `repeat(3, 1fr)`, `gap: 16px`.

**Productkaart (desktop):** kolom-flex, 12px radius, 1px rand, `overflow: hidden`.

1. Afbeeldingsvlak 168px hoog. Wishlist-hartje rechtsboven: 26px witte cirkel met
   1px rand, 10px van de rand.
2. Body `padding: 14px`, `gap: 8px`, `flex: 1`:
   - Merknaam 11.5px/600 tertiair.
   - Titel 14px/700, `min-height: 37px` zodat de prijsblokken over de kaarten heen
     op één lijn liggen.
   - Specbadges: energielabel als groene badge met witte tekst, daarnaast de capaciteit
     als badge met alleen een rand. Beide IBM Plex Mono 10.5px, 3px radius.
   - Dan `margin-top: auto` en `padding-top: 10px` voor het onderblok:
     - Rij: links "vanaf" 10.5px + prijs in IBM Plex Mono 21px/600 tabular-nums;
       rechts het prijsverschil in groen 10.5px/700 ("€ 90 verschil").
     - **Winkeldekking:** zes streepjes van 5px hoog, `flex: 1` elk, `gap: 3px`,
       3px radius. Gevuld in merkblauw voor elke winkel die dit model verkoopt, de rest
       in `#e2e5ea`. Rechts ernaast "4/6" in IBM Plex Mono 10.5px.
       *Nieuw element. Reden: het maakt in het overzicht al zichtbaar bij hoeveel
       winkels een model te koop is — meer winkels betekent meer kans op een lage prijs,
       en het is precies wat een vergelijker onderscheidt van een webshop.*
     - **Koopknop:** volledige breedte, oranje, 8px radius, `padding: 11px`, tekst
       "Vergelijk prijzen" 13.5px/700 wit, gecentreerd.
     - Onderaan de bestaande "Aan vergelijking toevoegen"-checkbox: 14px vierkant met
       3px radius + label 11.5px tertiair.

### 2. Categoriepagina — mobiel (`4b`)

**Canvas:** 390px. Sectiepadding 16px.

Zelfde inhoud en zelfde volgorde als desktop, met deze verschillen:

1. **Header** — merkblauw, logo links, `♡ 0` en een hamburger (twee 17×2px witte lijnen)
   rechts.
2. **Kop** — breadcrumb 11.5px, `h1` 24px/800, dan één metaregel 13px:
   "149 modellen · 6 winkels · vandaag bijgewerkt".
3. **Keuzehulp** — één compact blok, lichtblauw met blauwe rand: titel 13.5px/700,
   subregel 12px "3 korte vragen", en rechts een blauwe knop "Start →".
   De videogids komt op mobiel lager op de pagina te staan (niet in dit scherm getoond),
   omdat de keuzehulp bovenaan meer oplevert.
4. **Chiprij** — horizontaal scrollend, `gap: 7px`, chips niet afbreken
   (`white-space: nowrap`).
5. **Filterbalk** — dit is het belangrijkste onderdeel. Achtergrond `#f0f2f6`, 1px lijn
   boven en onder, `padding: 11px 16px`, flexrij met `gap: 8px`:
   - **Eén blauwe Filters-knop**: hamburger-icoontje (drie lijnen van 12/8/4px), het
     woord "Filters", een witte ronde teller met het aantal actieve filters in blauw,
     en een chevron `▾`/`▴`. 8px radius, 13.5px/700.
   - Daarnaast, `flex: 1`, de sorteerknop: wit, 1px rand, 8px radius, "Laagste prijs"
     met chevron.

   > **Dit gedrag is expliciet gevraagd en mag niet veranderen:** het filter is één
   > inklapbare knop **boven** de resultaten. Ingeklapt sta je direct bij de producten.
   > Er komt nooit een volledig uitgeklapt filterblok waar de bezoeker eerst langs moet
   > scrollen.

6. **Uitgeklapt filterpaneel** — schuift uit onder de balk, achtergrond `#f0f2f6`,
   onderrand.
   - Bovenaan de actieve filters als blauwe chips met `×`, plus een "Wissen"-link.
   - Daaronder dezelfde groepen als op desktop, elk met een klikbare kop
     (13.5px/700 + hint + chevron) en een uitklapbare body. Op mobiel zijn de opties
     **chips** in plaats van checkboxrijen: wit, 1px rand, 8px radius,
     `padding: 8px 12px`, 12.5px, met het aantal er kleiner en grijzer achter.
     Chips wrappen; ze scrollen niet.
   - Afsluitende blauwe knop over de volle breedte: "149 drogers tonen". Sluit het
     paneel.
   - Groepen apart inklapbaar houden is hier functioneel: zo wordt het paneel nooit
     langer dan het scherm.
7. **Resultaten** — koptekst "**149 drogers** gevonden" 12.5px, daarna een verticale
   lijst (geen grid). Rijen gescheiden door 1px `#eef0f4`, `padding: 14px 16px`.

**Productrij (mobiel):** flexrij, `gap: 13px`.

- Links een kolom van 82px: afbeelding 96px hoog (8px radius, 1px rand), en er direct
  onder de zes winkelstreepjes (4px hoog, `gap: 2px`) — compacter dan op desktop en
  zonder de "4/6"-tekst.
- Rechts (`flex: 1`, `min-width: 0`, `gap: 6px`): merknaam 11px/600 · titel 13.5px/700 ·
  specbadges (groen energielabel + capaciteit) · dan een rij met links
  "vanaf · bij 4 winkels" 10.5px + prijs in IBM Plex Mono 20px/600 en rechts het
  prijsverschil in groen · en onderaan de oranje koopknop over de volle breedte
  (11px padding, 8px radius, 13.5px/700).

## Interacties en gedrag

| Interactie | Gedrag |
|---|---|
| Klik op sidebar-groepskop (desktop) | Klapt die groep open/dicht. Chevron draait `▾`↔`▴`. Andere groepen blijven onaangeroerd (geen accordeon). |
| Klik op Filters-knop (mobiel) | Klapt het hele filterpaneel open/dicht. Chevron op de knop draait mee. |
| Klik op groepskop in mobiel paneel | Klapt die groep open/dicht, zelfde state als desktop. |
| Klik op "149 drogers tonen" | Sluit het mobiele paneel (op desktop: past de filters toe en scrollt niet). |
| Klik op filteroptie | Zet het filter aan/uit, werkt de teller op de Filters-knop bij, en voegt/verwijdert de chip in de actieve-filterbalk. |
| Klik op chip-`×` | Verwijdert dat filter. |
| Klik op "Wissen" | Verwijdert alle filters, teller naar 0. |
| Hover op productkaart | Alleen `border-color`. Geen transform, geen shadow. |
| Hover op oranje knop | Naar `#dc5418`. |
| Hover op blauwe knop | Naar `#1657ab`. |
| Hover op chip / filteroptie | Rand en/of tekst naar merkblauw. |
| Klik op koopknop | Onveranderd: bestaande affiliate-flow, inclusief alle parameters en `rel`-attributen. |

**Transities:** houd het rustig. `transition: border-color 120ms ease, background-color
120ms ease` op interactieve elementen. Het open/dicht klappen mag een
`max-height`- of `grid-template-rows`-transitie van ~180ms krijgen, maar een directe
toggle is ook acceptabel — liever geen animatie dan een schokkende animatie.

**Responsive:** één breekpunt volstaat. Onder ±900px gaat de sidebar over in de mobiele
filterbalk boven de resultaten; het grid gaat van drie kolommen naar een verticale lijst.
Tussenstap van twee kolommen op tablet mag, maar is niet uitgewerkt.

## State

Weinig, en het meeste bestaat al:

- `activeFilters` — bestaand. Voedt de chips, de teller op de mobiele knop en het
  resultaataantal.
- `openGroups` — per filtergroep open/dicht. Beginstand: Prijs open, Merk open, rest dicht.
  Mag client-side; hoeft niet in de URL.
- `mobileFilterOpen` — één boolean. **Beginstand dicht** op de echte site, zodat de
  bezoeker direct bij de producten staat. (In het prototype staat hij open zodat je het
  paneel ziet zonder te klikken.)
- `sortOrder` — bestaand.

Filters en sortering blijven in de URL zoals nu, zodat gefilterde views deelbaar en
indexeerbaar blijven. Verander de parameternamen niet.

## Assets

Alles komt uit de bestaande site — er zijn geen nieuwe assets nodig.

| In het prototype | Echte bron |
|---|---|
| Gestreept vlak "productfoto" | Bestaande `wsrv.nl`-image-URL's per product |
| Gestreept vlak "mascotte" | `/static/img/mascot.png` |
| Winkelnamen als tekst | `/static/img/winkels/{bol,coolblue,mediamarkt,expert,alternate,ep}.png` |
| Videothumbnail met play-button | Bestaande YouTube-thumbnail (`youtube-nocookie`-embed) |
| Vraagteken-badge keuzehulp | Bestaand keuzehulp-icoon |

Fonts: Nunito Sans en IBM Plex Mono, beide Google Fonts. Als Nunito Sans al lokaal
gehost is, gebruik die. Host IBM Plex Mono er liefst bij in plaats van een extra
externe request — er zijn maar twee gewichten nodig (500, 600) en alleen cijfers,
`€`, `/` en hoofdletters worden gebruikt, dus een subset is genoeg.

## Wat hier bewust níet in zit

Zodat er geen verkeerde aannames ontstaan:

- **De productdetailpagina met alle zes prijzen** staat als mobiel ontwerp in het
  prototype (`3a`, onderste scherm) maar is niet uitgewerkt voor desktop. Bouw die niet
  op eigen initiatief — vraag het eerst.
- **De zoekresultatenpagina** is niet ontworpen.
- **De homepage** staat in `3a` maar is niet de goedgekeurde richting voor turn 4.
- Alle prijzen, aantallen en modelnamen in het prototype zijn **voorbeelddata**
  (deels overgenomen uit de live site) — geen fixtures om te gebruiken.

## Bestanden in dit pakket

- `README.md` — dit document.
- `Witgoed Redesign.dc.html` — het prototype. Open het in een browser. De vier
  iteraties staan onder elkaar, nieuwste bovenaan; turn 4 is de goedgekeurde richting.
  De filterknoppen en groepskoppen zijn klikbaar.

## Voorgestelde werkwijze

1. Nieuwe branch vanaf `main`, bijvoorbeeld `redesign/categorie-filter`.
2. Voeg eerst de ontbrekende tokens toe aan de bestaande CSS-variabelen — verander de
   bestaande blauw- en oranjewaarden niet.
3. Bouw de sidebar en de mobiele filterbalk om, met het bestaande filterformulier
   en dezelfde name-attributen eronder.
4. Bouw de productkaart om. Vergelijk daarna de gerenderde HTML met de oude versie:
   dezelfde links, dezelfde `rel`- en tracking-parameters, dezelfde structured data.
5. Controleer voor de PR: één `h1` per pagina, breadcrumbs intact, alle interne
   categorielinks aanwezig, structured data valideert, geen wijziging in URL-parameters.
6. PR openen, niet mergen. De eigenaar test lokaal en zet zelf live.
