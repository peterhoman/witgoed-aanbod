# Lees dit eerst

Ontwerpdocumentatie voor het redesign van WitgoedAanbod.nl, geschreven in een designchat
in opdracht van de eigenaar. Dit is **geen** productiecode.

## Wat zit hier in

| Bestand | Inhoud | Status |
|---|---|---|
| `DESIGN_SPEC_categoriepagina.md` | Categoriepagina desktop + mobiel, tokens, typografie, alle randvoorwaarden | Grotendeels gebouwd en live |
| `DESIGN_SPEC_productpagina.md` | Productdetailpagina desktop + mobiel + de één-winkel-variant | Goedgekeurd, nog niet gebouwd |
| `Witgoed Redesign.dc.html` | Het prototype. Open in een browser. | Referentie |

**Let op de bestandsnamen.** Deze documenten heten bewust niet `README.md`, omdat de repo
zelf al een `README.md` heeft met de installatiehandleiding. Die twee zijn eerder met
elkaar verward, wat tot een misverstand leidde over wat er wel en niet ontworpen was.

## Hoe je het prototype leest

`Witgoed Redesign.dc.html` bevat vijf iteraties, **nieuwste bovenaan**. Elke variant heeft
een zichtbaar label waarnaar in de specs wordt verwezen.

| id | Wat | Gebruiken? |
|----|-----|-----------|
| `5a` `5b` `5c` | Productpagina: desktop, mobiel, één winkel | **Ja — te bouwen** |
| `4a` `4b` | Categoriepagina: desktop met sidebar, mobiel met inklapbaar filter | **Ja — grotendeels gebouwd** |
| `3a` | Mobiele richting waaruit de kleurkeuzes komen | Referentie |
| `1a` `1b` `1c` `2a` | Verworpen richtingen | Alleen context |

De filterknoppen en groepskoppen in het prototype zijn klikbaar.

## De drie afspraken die boven alles gaan

1. **Niet naar `main`.** `main` gaat via Railway automatisch naar productie. Werk op een
   branch, lever een PR, de eigenaar test lokaal en zet zelf live.
2. **Structuur is SEO-dragend.** Eén `h1`, breadcrumbs, interne links, structured data,
   affiliate-parameters en `rel`-attributen blijven ongewijzigd. Stylen mag, structuur
   slopen niet.
3. **Productkaarten, filters en koopknoppen zijn heilig.** Verander geen gedrag zonder
   overleg. Het inklapbare filter boven de resultaten op mobiel en het filter naast de
   resultaten op desktop komen uit echte gebruikersfeedback.

## Wat er inmiddels gebouwd en live staat

Uit de samenwerking met de bouwer, ter voorkoming van dubbel werk:

- Merk- en kleurfacetten genormaliseerd (AEG/Aeg samengevoegd, kleurwaarden meerwaardig,
  feedrommel uitgesloten). Dit repareerde filters die stelselmatig te weinig resultaten
  gaven: AEG toonde 33 van 40, Wit 27 van 35, RVS 4 van 24.
- Stille afkapping op tien filteropties vervangen door "Meer (n)"; zoekveld bij groepen
  boven 25 opties.
- Filtergroepen inklapbaar met `<details>`/`<summary>`, alleen Prijs open bij laden,
  gekozen waarden in de dichtgeklapte kop. Sidebar van 1647px naar 715px.
- Sticky sidebar op desktop boven 768px.
- Scroll tot eerste product op mobiel van 950px naar 496px.
- Prijs uit de linkkleur gehaald.
- Header: één oranje element (de zoekknop).
- Dekkingsbalk vult aaneengesloten; "vanaf" en winkelteller op de kaarten; conditioneel
  knoplabel "Vergelijk n prijzen" of "Bekijk aanbieding".

## Wat nog open staat

- **Productpagina bouwen** volgens `DESIGN_SPEC_productpagina.md`.
- **EAN-dekking verhogen.** Gemeten over de hele catalogus via `/api/sync-status`:
  43% van de producten heeft twee of meer aanbiedingen (1196 van 2789). Per categorie
  loopt dat van afzuigkappen 63% tot **wasmachines 25%** (63 van 256) — de zwakste
  categorie en vermoedelijk de best bezochte. Dit levert meer op dan elk visueel punt in
  deze documenten. Begin bij wasmachines.
- **Tokenrefactor** (spacing- en typografieschaal in `:root`). Bewaren tot het
  ontwerpwerk klaar is: het raakt honderden regels en maakt de HTML-diffs onleesbaar die
  nu het controlemiddel zijn.
- **Modelnummer als eigen veld uit de feeds.** Hoort bij het dekkingstraject.
- Nog niet ontworpen: zoekresultatenpagina (staat op noindex, lage prioriteit) en de
  homepage.

## Mascotte

De mascotte blijft waar hij nu is: in de hero van de homepage. Niet op de categorie- of
productpagina — daar staat hij vandaag ook niet, en dat is een bewuste keuze van de
eigenaar.
