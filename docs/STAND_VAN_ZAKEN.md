# Stand van zaken — 25 juli 2026

Overdracht voor de volgende sessie. Alles hieronder staat live tenzij anders vermeld.

---

## Eerst dit, morgenochtend

**Controleer of de specificaties terugkomen.** Dit is de belangrijkste openstaande
vraag van gisteren.

Open drie willekeurige productpagina's en kijk of er een blok "Specificaties" staat.
Gisteren had 82% van de catalogus er geen (gemeten: 11 van 60 producten). De oorzaak
is gerepareerd, maar het herstel gebeurt pas als de Bol-sync de gegevens opnieuw
ophaalt — die draait elke zes uur.

- Zie je specificaties verschijnen waar ze gisteren ontbraken → het werkt, niets doen.
- Blijft het leeg na een paar syncrondes → er zit iets anders achter, opnieuw
  onderzoeken.

Een snelle steekproef:

```bash
python -c "
import urllib.request, re, random
xml = urllib.request.urlopen('https://www.witgoedaanbod.nl/sitemap.xml', timeout=60).read().decode('utf-8','ignore')
urls = [u for u in re.findall(r'<loc>([^<]+)</loc>', xml) if '/product/' in u]
random.seed(11)
met = 0
steek = random.sample(urls, 30)
for u in steek:
    h = urllib.request.urlopen(u, timeout=30).read().decode('utf-8','ignore')
    met += 1 if 'specs-card' in h else 0
print('met specificaties: %d van %d (%.0f%%)' % (met, len(steek), 100*met/len(steek)))
"
```

Gisteren: 18%. Alles daarboven is winst.

---

## Twee cijfers om te volgen

Allebei op `/api/sync-status`, geen cookies, geen toestemming nodig.

| Cijfer | Gisteren | Wat het betekent |
|---|---|---|
| `paginaweergaven` → `product_per_categorie` | 2,97 | Hoeveel productpagina's per categoriepagina. Stijgt dit, dan werkt de nieuwe knop. |
| `winkeldekking` → `totaal.dekking_pct` | 43% | Aandeel apparaten met meer dan één winkel. Bij wasmachines 25%. |

De paginateller begon gisteren, dus er is nog geen vergelijking met de periode
ervoor. Over een paar dagen wel.

---

## Wat er gisteren live is gegaan

Acht pull requests.

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
  hoeveel producten ze bevatten. Die meting kan vooraf.
- De grote vraag: is Bol wel de juiste basis voor de catalogus? Nu bepaalt Bol wat
  er bestaat en kunnen de anderen alleen aansluiten.

### 2. Prijsverloop-grafiek
Nog niet gebouwd volgens de designspec (periodeknoppen 90 dagen / 1 jaar, 150px hoog,
groene punt op de huidige waarde, maandlabels). De bestaande grafiek staat er nog.
Raakt `price_chart.py`, dus eigen stuk werk.

### 3. Screenshots voor de designchat
Van 5a (meerdere winkels), 5b (mobiel) en 5c (één winkel).

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
