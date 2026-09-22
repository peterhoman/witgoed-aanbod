# Wekelijkse rankingmeting — tien modelcodes live in Google

Afgesproken met Peter op 16 september 2026. Doel: zien of iets wat we doen
onze plek in de **gewone zoekresultaten** verandert. Search Console alleen
is daarvoor niet genoeg: de "positie 1-10" daar is bij ons grotendeels
Googles blok "Vergelijkingssites" (uit onze Merchant Center-feed), geen
blauwe link. Zie START-HIER, rankingmeting 16 september.

## Werkwijze (elke week, zelfde dag, zelfde tien)

Via Peters Chrome (claude-in-chrome), per zoekwoord twee pagina's:
`https://www.google.nl/search?q=<zoekwoord>&hl=nl&gl=nl` en dezelfde met
`&start=10`. Uitlezen met:

```js
const r=[...document.querySelectorAll('a h3')].map(h=>h.closest('a').href.replace(/^https?:\/\/(www\.)?/,'').split('/')[0]);
({n:r.length, wij:r.findIndex(d=>/witgoedaanbod/.test(d))+1, top:r.slice(0,10), module:/Vergelijkingssites/.test(document.body.innerText)})
```

Noteer: onze plek (pagina 1 = plek zoals gemeld; pagina 2 = 9 of 10 + plek;
niet gevonden = "–"), of het blok Vergelijkingssites er staat, en de eerste
drie domeinen. Google geeft per pagina 6 tot 10 gewone resultaten, dus
"niet in 2 pagina's" betekent ruwweg "niet in de top 18".

## De tien

| # | Zoekwoord | Waarom |
|---|---|---|
| 1 | aeg lr7386ud4 | meting 8 sept (meeste Shopping-klikken) |
| 2 | dyson v12 detect slim absolute | meting 8 sept; ons meest geklikte zoekwoord |
| 3 | inventum vki6010zil | meting 8 sept; 4 winkels bij ons |
| 4 | koenic kfz 621 d nf | meting 8 sept; MediaMarkt-huismerk |
| 5 | lg gbbsj10dpy | 53 vertoningen in 3 mnd, SC-positie 14 |
| 6 | bosch smv4emx01n | meeste vertoningen (120), SC-positie 6,5 |
| 7 | ok otd 8346 d | 110 vertoningen, 0 klikken, huismerk |
| 8 | koenic kwm 9116 a inv | 71 vertoningen, huismerk |
| 9 | samsung dv90dg52a0ahen | 100 vertoningen op SC-positie 2,2 (= module) |
| 10 | miele wck 370 wcs | 47 vertoningen, SC-positie 10 |

(Veripart VPMNVR50CW uit de meting van 8 sept is vervangen: dat product
heeft bij ons geen pagina meer.)

## Metingen

### Week 38 — dinsdag 16 september 2026 (nulmeting)

| # | Zoekwoord | Onze plek | Module | Eerste drie |
|---|---|---|---|---|
| 1 | aeg lr7386ud4 | – | ja | aeg.nl, mediamarkt, consumentenbond |
| 2 | dyson v12 detect slim absolute | – | ja | bol, coolblue, dyson.nl |
| 3 | inventum vki6010zil | – | ja | inventum.eu, youtube, electroworld |
| 4 | koenic kfz 621 d nf | – | nee | mediamarkt, tpwitgoed, knibble |
| 5 | lg gbbsj10dpy | – | nee | lg.com, mediamarkt, youtube |
| 6 | bosch smv4emx01n | **16** (pagina 2) | ja | bosch-home, mediamarkt, mediamarkt |
| 7 | ok otd 8346 d | – | nee | mediamarkt, kieskeurig, timcovoordeelmarkt |
| 8 | koenic kwm 9116 a inv | – | nee | mediamarkt, consumentenbond, mediamarkt |
| 9 | samsung dv90dg52a0ahen | – | ja | samsung, mediamarkt, coolblue |
| 10 | miele wck 370 wcs | – | ja | miele.nl, mediamarkt, kieskeurig |

**Stand: 1 van 10 in de top 18, en die op pagina 2.** Vergelijkers die wél
op pagina 1 staan: Kieskeurig (4x), Consumentenbond (3x), Tweakers (3x),
Knibble (3x), vergelijk.nl (3x), beslist.nl (2x), supersales (2x).

### Week 39 — dinsdag 22 september 2026

| # | Zoekwoord | Onze plek | Module | Eerste drie |
|---|---|---|---|---|
| 1 | aeg lr7386ud4 | – | ja | aeg.nl, mediamarkt, consumentenbond |
| 2 | dyson v12 detect slim absolute | – | ja | coolblue, bol, mediamarkt |
| 3 | inventum vki6010zil | – | nee (was ja) | inventum.eu, coolblue, youtube |
| 4 | koenic kfz 621 d nf | – | nee | mediamarkt, bol, tpwitgoed |
| 5 | lg gbbsj10dpy | – | nee | mediamarkt, lg.com, youtube |
| 6 | bosch smv4emx01n | **17** (pagina 2, was 16) | ja | bosch-home, mediamarkt, mediamarkt |
| 7 | ok otd 8346 d | – | nee | mediamarkt, kieskeurig, handleidingkwijt |
| 8 | koenic kwm 9116 a inv | – | nee | mediamarkt, consumentenbond, test-aankoop |
| 9 | samsung dv90dg52a0ahen | – | ja | samsung, mediamarkt, coolblue |
| 10 | miele wck 370 wcs | – | ja | miele.nl, mediamarkt, kieskeurig |
| 11 | witgoed prijsvergelijkers (sinds deze week) | – (niet in top 20) | nee | tweakers, witgoed.com, slimster |

**Stand: 1 van 10 in de top 18, onveranderd (de Bosch zakte van 16 naar
17).** Vergelijkers op pagina 1: Consumentenbond 5x, Tweakers 4x, Kieskeurig
3x, beslist.nl 3x, Knibble 2x, supersales 2x, vergelijk.nl 1x. Bij "witgoed
prijsvergelijkers" staat Witgoedwijzer.nl op pagina 2 (plek 9; op 8 sept nog
plek 3) en Slimster op 3.

**Opvallend:** de kleine winkels die Peter op 17 sept mailde staan zélf
organisch op pagina 1 of 2 bij deze modelcodes: Keukenloods (2x), Bemmel &
Kroon (2x), Correct, De Schouw, Electro World, plus wasdame.nl en welhof.com.
Google vindt een winkel die het apparaat verkoopt relevanter dan een
vergelijker met één of twee prijzen. De vier reparaties aan de energielabels
en de sitemap-datum van 18-21 sept kunnen hier nog niet in zitten.
