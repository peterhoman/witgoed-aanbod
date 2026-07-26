# Stand van zaken

Laatst bijgewerkt: 26 juli 2026. Alles hieronder staat live tenzij anders vermeld.

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
| Gevonden – niet geïndexeerd | 340 | wachtrij, geen actie nodig |
| Gecrawld – niet geïndexeerd | 100 | Google vond ze te dun: specs en dekking |
| Pagina met omleiding | 7 | correcte 301's, geen actie |
| Serverfout (5xx) | 1 | opgelost 26-07, validatie loopt |
| Niet gevonden (404) | 1 | opgeruimde pannenset, geen actie |

**Waar je op moet letten:** een nieuwe reden die erbij komt, of "Gecrawld – niet
geïndexeerd" dat hard oploopt. Dat laatste betekent dat Google steeds meer
pagina's te dun vindt.

Verschijnt er weer een **serverfout**, behandel die niet als klein. Op 26 juli
bleek één 5xx te komen door acht productpagina's die via interne links
onbereikbaar waren (kale `%` in de slug).

---

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

### 2. Prijsverloop-grafiek
Nog niet gebouwd volgens de designspec (periodeknoppen 90 dagen / 1 jaar, 150px hoog,
groene punt op de huidige waarde, maandlabels). De bestaande grafiek staat er nog.
Raakt `price_chart.py`, dus eigen stuk werk.

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
