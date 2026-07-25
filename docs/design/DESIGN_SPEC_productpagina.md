# Design spec: productdetailpagina

Voor: `/product/<slug>` op WitgoedAanbod.nl
Status: goedgekeurd door de eigenaar, nog niet gebouwd.
Prototype: `Witgoed Redesign.dc.html`, secties **5a** (desktop), **5b** (mobiel),
**5c** (één winkel). Open het bestand in een browser en scroll naar boven.

Lees eerst `00_LEES_DIT_EERST.md` en `DESIGN_SPEC_categoriepagina.md` — de tokens,
typografie en randvoorwaarden daaruit gelden hier onverkort en worden niet herhaald.

## Waarom deze pagina

Op de categoriepagina kiest de bezoeker kandidaten. Hier beslist hij. Dit is de enige
pagina waar het verschil tussen WitgoedAanbod en een webshop zichtbaar wordt: meerdere
winkels, prijsverloop, en de werkelijke kosten over de levensduur.

De huidige pagina heeft alle bouwstenen maar de verkeerde verhouding: de winkellijst is
een reeks losse regels onder een enkele "Beste prijs", en de vijftig specificatievelden
die in de data zitten staan er niet op.

## Drie ingrepen

1. **De winkellijst wordt de hoofdzaak** — een tabel met levertijd, bezorgkosten, prijs
   en het verschil met de laagste, met een knop per rij.
2. **Specificatieblok toevoegen** — acht kernvelden in twee kolommen, de rest achter
   "Alle 50 specificaties".
3. **Kosten over de levensduur** — stroomkosten per jaar en totale kosten over tien jaar,
   berekend uit energielabel en kWh-verbruik.

Plus een vierde, apart uitgewerkt: **de één-winkel-toestand (5c)**, die op ongeveer de
helft van de producten van toepassing is.

## 5a — Desktop

Contentbreedte 1240px, sectiepadding 28px.

### Bovenblok: twee kolommen

**Links, 440px vast (`flex-shrink: 0`):**

- Hoofdafbeelding 380px hoog, 12px radius, 1px lijnrand.
- Daaronder vier thumbnails in een `repeat(4, 1fr)`-grid, 68px hoog, 8px radius, `gap: 8px`.
  Alleen renderen als er meer dan één afbeelding is.

**Rechts (`flex: 1`, `min-width: 0`), `gap: 16px`:**

1. **Kop**
   - Eyebrow: `BOSCH · WGG244FONL` in IBM Plex Mono 12px, `letter-spacing: 0.06em`,
     tertiaire kleur. Merk in kapitalen.
     → Het modelnummer komt uit het bestaande `Model`-spec-veld. Is dat veld gevuld,
       toon het achter het merk met een `·` ertussen. Is het leeg, toon alleen het merk.
       Geen heuristiek op de titel — zie de afspraak onderaan.
   - `h1` 29px/800, `letter-spacing: -0.03em`, `line-height: 1.14`, `text-wrap: pretty`.
     **Niet clampen** — op de detailpagina staat de volledige titel.
   - Badgerij: energielabel als groene badge (`#218358`, witte tekst, 4px radius,
     IBM Plex Mono 11.5px/600), daarna de kernspecs als badges met alleen een rand.
     Maximaal vier specbadges: vulgewicht, toerental, geluid, bijzondere functie.

2. **Aanbiedingenblok** — kaart, 12px radius, 1px lijnrand, `overflow: hidden`.

   **Kop van het blok** (achtergrond `#e8f2fd`, onderrand `oklch(0.88 0.03 250)`,
   padding 16px 18px, flexrij met `align-items: flex-end`):
   - Links: eyebrow "LAAGSTE VAN 4 WINKELS" (IBM Plex Mono 11px, `0.1em`, uppercase,
     `oklch(0.45 0.1 258)`, 600), daaronder de prijs in IBM Plex Mono 34px/600,
     `letter-spacing: -0.035em`, `tabular-nums`, met daarnaast op dezelfde basislijn
     "bij Coolblue" in 13px secundair.
   - Rechts, rechts uitgelijnd: "€ 90 verschil tussen winkels" 13px/700 in groen, en
     daaronder "hoogste € 739,00" in IBM Plex Mono 12px tertiair.

   **Eén rij per winkel** (padding 14px 18px, onderrand `#eef0f4`, `gap: 16px`,
   `align-items: center`):
   - Winkellogo, 108px breed × 26px hoog, `flex-shrink: 0`. In het prototype een
     placeholder; gebruik de PNG's uit `/static/img/winkels/`.
   - Midden (`flex: 1`, `min-width: 0`): levertijd 13px op regel 1
     ("Morgen bezorgd", "Vandaag ophalen", "2 tot 4 werkdagen"), en op regel 2 in
     11.5px tertiair de bezorgvoorwaarde ("Gratis bezorging en installatie",
     "Bezorging € 29,95").
     → Bezorgkosten zijn hier essentieel: € 649 met € 29,95 bezorging is duurder dan
       € 669 gratis bezorgd. Heb je dat veld niet per winkel, laat de regel dan weg —
       vul hem niet met een aanname.
   - Rechts: prijs in IBM Plex Mono 19px/600 `tabular-nums`, en daaronder het verschil
     met de laagste: "laagste" in groen/600 op de goedkoopste rij, "+ € 20" in tertiair
     op de andere.
   - Knop "Bekijk →", 8px radius, 13.5px/700, `padding: 11px 17px`, `flex-shrink: 0`.
     **Alleen de goedkoopste rij krijgt de oranje knop**; de andere rijen krijgen een
     witte knop met lijnrand en donkere tekst. Zo blijft oranje één betekenis houden en
     is de aanbevolen actie meteen duidelijk — zonder de andere winkels te verstoppen.
   - De goedkoopste rij heeft achtergrond `oklch(0.965 0.026 250)` (lichtblauw).

   **Sortering:** oplopend op prijs. Altijd. Geen commissie-invloed, geen "aanbevolen"
   bovenaan. Dit is het vertrouwensanker van de site.

   **Voetregel** (11.5px, achtergrond `#f7f8fa`): "Prijzen incl. btw, excl.
   bezorgkosten, bijgewerkt vandaag 06:10. Wij ontvangen commissie bij aankoop via deze
   links — de rangorde is puur op prijs." De affiliate-disclosure blijft verplicht
   zichtbaar en de tijdstempel is een vertrouwenssignaal: laat hem staan.

3. **Twee kostenkaarten**, flexrij `gap: 12px`, elk `flex: 1`, 12px radius, 1px rand,
   padding 14px 16px:
   - "Stroomkosten per jaar" · `± € 41` (IBM Plex Mono 22px/600) ·
     onderregel 11.5px: "220 wasbeurten · 48 kWh/jaar · € 0,35/kWh".
   - "Over 10 jaar" · `€ 1.059` · onderregel: "aanschaf plus stroom — label D kost
     € 380 meer".

   **Berekening:** `kWh_per_jaar × prijs_per_kWh`. Zet `prijs_per_kWh` als
   configuratiewaarde (nu € 0,35), niet hardcoded per template. De vergelijking met een
   slechter label rekent hetzelfde apparaat door met het gemiddelde kWh-verbruik van
   label D in die categorie.

   **Voorwaarde:** alleen renderen als `kWh_per_jaar` bekend is. Geen schatting, geen
   "onbekend"-kaart. Ontbreekt het veld, laat de hele rij weg.

   *Dit is het inhoudelijk sterkste nieuwe element op de pagina. Een webshop vertelt
   niet dat een machine van € 100 meer over tien jaar goedkoper is.*

### Prijsverloop en prijsalert

Flexrij, `gap: 20px`, `padding-top: 28px`.

**Prijsverloop (`flex: 1`)** — kaart, padding 18px 20px:
- Kop: "Prijsverloop" 17px/700, subregel 12.5px: "Laagste prijs in 90 dagen. Nu
  **€ 40 onder** het gemiddelde." (het bedrag in groen/700).
- Rechtsboven twee periodeknoppen: "90 dagen" actief (blauw, wit, 6px radius),
  "1 jaar" inactief (lijnrand).
- Grafiek 150px hoog, met `border-bottom` en `border-left` als assen. Eén `polyline` in
  merkblauw, 2.5px, plus een groene punt op de huidige waarde met het bedrag ernaast.
  Geen vlakvulling, geen raster, geen tooltipbibliotheek. Onder de grafiek de
  maandlabels in IBM Plex Mono 11px, `justify-content: space-between`.
- De bestaande tabel "Alle prijswijzigingen (n)" blijft, maar ingeklapt onder de grafiek.
  Bij één wijziging: alleen de regel, geen tabelkop.

**Prijsalert (330px vast)** — lichtblauwe kaart met blauwe rand, 12px radius:
- "Wachten op een lagere prijs?" 16px/700.
- 13px: "Wij mailen zodra een van de vier winkels de prijs verlaagt. Gratis, afmelden
  met één klik." Het aantal winkels dynamisch.
- E-mailveld als witte pil met 4px padding en een blauwe knop "Zet alert" erin.
- 11px onder: "Alleen voor deze prijsalert. Zie ons privacybeleid." — link behouden.

De huidige pagina heeft hier een eigen `h2` met een belletje-emoji. Vervang die door de
tekstkop hierboven; geen emoji.

### Specificaties

De tabel bestaat al op de huidige pagina: 77 velden, ingeklapt op de eerste acht met een
"Toon meer"-knop. Bouw dus geen nieuwe tabel — het probleem is niet het aantal maar de
**ordening**. Acht willekeurige velden uit de feedvolgorde zeggen minder dan acht gekozen
velden, en 77 velden op een rij is onbruikbaar hoe je ze ook toont.

Drie wijzigingen aan wat er staat:

1. **Kies de zichtbare acht per categorie**, in plaats van de eerste acht uit de feed.
   Voor wasmachines: vulgewicht, energielabel, toerental, verbruik per jaar, geluid
   centrifugeren, waterverbruik, afmetingen (h×b×d), aantal programma's. Definieer zo'n
   lijstje per categorie; het is een korte configuratie, geen logica.
2. **Groepeer de uitgeklapte 77 in benoemde blokken** met een kop per blok: Prestaties,
   Verbruik en kosten, Afmetingen en installatie, Programma's en functies, Overig. Zonder
   groepen is uitklappen geen verbetering maar een muur.
3. **Styling** zoals in het prototype: grid `1fr 1fr` met `gap: 0 32px`, label links in
   secundaire kleur 13.5px, waarde rechts in 600 en IBM Plex Mono 13px, onderlijn
   `#eef0f4`, `padding: 9px 0`. Mobiel één kolom.

De knoptekst wordt "Alle 77 specificaties →" met het echte aantal, niet "Toon meer" — dan
weet de bezoeker wat hij krijgt. Alles blijft in de DOM, alleen visueel ingeklapt, zodat
er geen indexeerbare inhoud verdwijnt.

Overweeg de gekozen kernvelden ook als `additionalProperty` in de bestaande
`Product`-schema op te nemen — dit is unieke, gestructureerde inhoud per product.

### Beschrijving en koopgidsen

Flexrij, `gap: 20px`, `padding: 20px 28px 28px`.
- **Beschrijving (`flex: 1`)**: kop 17px/700, tekst 14px met `line-height: 1.62`,
  ingekort tot ongeveer vier regels met "Lees de volledige beschrijving →" eronder in
  merkblauw 13px/700. De volledige tekst blijft in de DOM — alleen visueel ingekort —
  zodat er geen indexeerbare inhoud verdwijnt.
- **Lees ook (330px vast)**: de bestaande koopgidsen-links, 13px/600 in merkblauw, elk
  met een onderlijn eronder, `gap: 11px`. Dit is een sterk intern linkblok; alle vijf
  links behouden.

Onder dit alles blijft de bestaande sectie "Gerelateerde Producten" met de
categoriekaarten uit `_macros.html` — ongewijzigd, dus met "vanaf", de winkelteller en
het conditionele knoplabel die daar al werken.

## 5b — Mobiel

390px, sectiepadding 16px. Zelfde inhoud, zelfde volgorde, één kolom.

Verschillen:

- Hoofdafbeelding 220px hoog, geen thumbnailrij (swipe of weglaten).
- `h1` 20px/800, `letter-spacing: -0.028em`. Badges 10.5px.
- **Prijsblok als eigen lichtblauwe kaart** (12px radius, blauwe rand): eyebrow,
  prijs in IBM Plex Mono 30px/600, "bij Coolblue" ernaast, en daaronder één regel
  "€ 90 verschil · hoogste € 739,00" in groen/700 12.5px.
- **Winkelrijen als losse kaarten** met `margin: 0 16px 8px`, 10px radius,
  `padding: 12px 14px`: winkelnaam 13px/700 + levertijd 11px links, prijs en verschil
  rechts, knop "Bekijk" daarnaast. De goedkoopste kaart krijgt een blauwe rand
  (`oklch(0.72 0.1 255)`) en de lichtblauwe achtergrond.
  Op mobiel geen bezorgvoorwaarde-regel — te weinig ruimte; die staat op de winkelpagina.
- **Kostenkaarten** naast elkaar, elk `flex: 1`, alleen het bedrag en het label
  (geen berekeningsregel).
- **Prijsverloop** compacter: 84px hoge grafiek, alleen de lijn, geen periodeknoppen,
  geen maandlabels. De subregel met "€ 40 onder het gemiddelde" blijft — dat is de
  boodschap, niet de grafiek.
- **Specificaties** in één kolom in plaats van twee.
- Alle tikbare elementen minimaal 44px hoog.

## 5c — Eén winkel

**Dit is het belangrijkste ontwerp van deze ronde**, want het geldt voor ongeveer de
helft van de producten (gemeten: 43% heeft twee of meer aanbiedingen; bij wasmachines
maar 21%).

Bij één aanbieding valt de vergelijking weg: geen laagste prijs, geen verschil, geen
lijst van winkels. Een kale prijs met één knop laat de site defect lijken. In plaats
daarvan: benoem de situatie en maak er iets nuttigs van.

Opbouw, van boven naar beneden:

1. **Compacte kop**: foto 84×100px links, eyebrow + titel + badges rechts. Kleiner dan
   in 5a, want er is minder te beslissen.
2. **Prijsblok** met de eyebrow "PRIJS BIJ 1 WINKEL" — niet "laagste prijs", want er is
   niets om laagste van te zijn. Prijs in IBM Plex Mono 30px/600, daaronder winkel en
   levertijd, en dan de oranje knop over de volle breedte:
   "Bekijk bij MediaMarkt →".
3. **Uitlegblok** (achtergrond `#e8f2fd`, met een 5px blauwe verticale accentbalk links):
   - "Dit model verkoopt nu bij één van onze zes winkels." 14px/700
   - "Wij checken de andere vijf dagelijks. Komt hij ergens goedkoper, dan mailen wij je."
     12.5px
   - Direct daaronder het e-mailveld met de knop **"Houd bij"**.
   - En een dekkingsbalkje van zes streepjes (6px hoog) met één gevuld, plus "1 van 6" —
     dezelfde visuele taal als op de categoriekaarten, zodat de bezoeker het herkent.

   *Dit is de kern: je verontschuldigt je niet voor ontbrekende data, je laat zien dat je
   actief zoekt. De prijsalert wordt hier de tweede hoofdactie in plaats van een
   bijzaak onderaan.*

4. **"Wel te vergelijken: 6 kg, label D"** — drie tot vijf alternatieven met hetzelfde
   vulgewicht en label die **wél** bij meerdere winkels liggen. Per regel: kleine foto
   46×54px, naam 12.5px/600, daaronder "bij 3 winkels · € 24 verschil" in groen/700, en
   rechts de prijs in IBM Plex Mono 14.5px/600.

   Selectie: zelfde categorie, vergelijkbaar vulgewicht en energielabel, gesorteerd op
   `retailer_count` aflopend. Dit maakt de pagina bruikbaar in plaats van doodlopend, en
   het zijn interne links naar precies je best gedekte producten.

Prijsverloop bij één winkel: alleen tonen als er daadwerkelijk prijswijzigingen zijn.
Eén punt is geen verloop.

## Afspraken die uit het traject volgen

Deze zijn eerder in de samenwerking vastgesteld en gelden ook hier:

- **Modelnummer alleen uit het `Model`-veld.** Toon het op de merkregel als het veld
  gevuld is, laat het weg als het leeg is (in een steekproef van veertien wasmachines was
  het vier keer gevuld). Geen heuristiek op de titel: die breekt op was/droog-sets
  ("WBWM5A5W9ML + Wisberg WBDR5AW9ML") en zet dan het verkeerde identificatienummer op de
  pagina. `MPN` is geen alternatief — AEG levert daar interne codes als "914 913 271" die
  geen koper herkent. Het `Model`-veld beter gevuld krijgen hoort bij het dekkingstraject.
- **Oranje betekent één ding.** Per pagina één oranje element per beslismoment: de
  koopknop van de goedkoopste winkel, en de zoekknop in de header. Nergens anders.
- **Groen betekent besparing.** Energielabel, prijsverschil, prijsdaling, en de
  winkeltelling bij alternatieven. Niet voor voorraadmeldingen — zet "Op voorraad" als
  grijze tekst, of toon alleen "niet op voorraad".
- **Prijzen in `font-variant-numeric: tabular-nums`.** Werkt dat niet in het huidige
  lettertype, controleer dan of `1111` en `8888` exact even breed zijn; zo niet, dan
  mist de font de feature en is IBM Plex Mono nodig voor prijzen alleen.
- **Structuur blijft.** Eén `h1`, breadcrumbs, alle interne links, alle structured data,
  alle affiliate-parameters en `rel`-attributen ongewijzigd. Stylen mag, structuur
  slopen niet.
- **Werk op een branch, niet op `main`.** `main` gaat via Railway automatisch live.

## Voorwaarde die boven dit ontwerp uitgaat

Bij 43% dekking is meer dan de helft van de productpagina's een 5c-pagina. Dit ontwerp
maakt die situatie draaglijk, maar lost hem niet op. Het verhogen van de EAN-matching —
te beginnen bij wasmachines, met 21% de zwakste categorie en vermoedelijk de best
bezochte — levert meer op dan elk visueel punt in dit document.

Zet de dekking als teller op `/api/sync-status` zodat het afleesbaar is in plaats van
geschat.
