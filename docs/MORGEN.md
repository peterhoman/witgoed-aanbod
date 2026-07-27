# Waar we staan — verder op 27 juli

Kort overdrachtsbriefje, geschreven aan het eind van 26 juli. Dit is een
takenlijst, geen toestandsbeschrijving: de echte stand staat in
`STAND_VAN_ZAKEN.md`. Weggooien zodra het afgewerkt is.

---

## 1. Afgehandeld op 27 juli: is dat MPN-veld bruikbaar?

Ja, maar bij ongeveer de helft van de merken, en alleen bij Coolblue.
616 geverifieerde modelcodes van 1237, MediaMarkt levert er nul. De volledige
uitkomst staat in `STAND_VAN_ZAKEN.md` onder "Modelcode en EPREL".

Wat overblijft: de modelcode uit de titel halen en door EPREL laten bevestigen.
Dat kan pas als de sleutel er is.

---

## 2. Wat er buiten ons om loopt

**EPREL-sleutel.** Aanvraag is 26 juli 's avonds gemaild naar
`ENER-ENERGY-LABELLING@ec.europa.eu`, met de ondertekende verklaring erbij.
Ondertekend met een zelfgemaakt certificaat, en dat is in de mail ook gemeld —
mogelijk willen ze een gekwalificeerde handtekening. Komt er een afwijzing, dan
staat er in hun antwoord wat ze wél willen.

Het certificaat staat in
`C:\Users\Avantius\AppData\Roaming\Adobe\Acrobat\DC\Security\PeterHoman.pfx`,
met een kopie op een eigen plek. Het wachtwoord hoort in de wachtwoordkluis.

**TradeTracker / Voordeligwitgoed.nl.** Liep al. 447 producten. Zodra de feed-URL
er is: eerst meten hoeveel apparaten van één naar twee winkels gaan, vóór
aansluiten. Zie `winkelbijdrage` op `/api/sync-status`.

---

## 3. Kijken, geen werk

**28 juli: de prijsverloop-grafiek verschijnt voor het eerst.** De meting begon
14 juli en de drempel staat op veertien dagen. Open dan een productpagina van een
apparaat waarvan de prijs bewoog en kijk of hij klopt. Niemand heeft die grafiek
ooit op de echte site gezien.

**De dagelijkse controle.** Het commando staat bovenaan `STAND_VAN_ZAKEN.md`.
Uitgangswaarden van 26 juli: specificaties 35%, winkeldekking 43%
(wasmachines 25%).

**Search Console, nu per soort.** De sitemap is opgesplitst in zeven bestanden.
Vanaf nu is per soort af te lezen of die 137 geïndexeerde pagina's producten of
categoriepagina's zijn — en dus of het werk van 26 juli iets doet. Verwacht
daar geen verandering binnen een paar dagen.

---

## 4. Wat 26 juli 's middags live ging

Acht ingrepen, allemaal gericht op pagina's die Google wel crawlt maar niet
indexeert. Volledig beschreven in `STAND_VAN_ZAKEN.md`; hier alleen de lijst:

1. Categoriecontext op elke productpagina — eigen meetgegevens als eigen inhoud
2. Eigen meta-descriptions — 84% was afgekapte leverancierstekst
3. Sitemapdatums die alleen bij een echte wijziging bewegen
4. Crawldiepte van twaalf naar twee via de merkfacetten
5. Verfijningslinks op de productpagina
6. Kruimelpad met merkstap, ook in de structured data
7. Filterzijbalk: Energielabel, Vulgewicht, Toerental in plaats van feednamen
8. Twee verzonnen uitspraken over energielabels opgeruimd

---

## 5. Besluiten die vastliggen

**Geen `noindex` op de circa 1600 één-winkel-producten.** De designchat stelde
dat voor; afgewezen. Het spreekt de koers tegen en haalt de categoriecontext weg
bij precies de pagina's waarvoor die gebouwd is.

**Drie onderdelen van de prijsverloop-spec wachten op data**, niet op tijd:
periodeknoppen, maandlabels en "onder het gemiddelde". Alle drie gaan uit van
maanden historie. Kan zodra er drie maanden ligt.

---

## 6. Waar het echte tekort zit

Onveranderd, en het is goed om dat te blijven zien: **43% dekking en 35% gevulde
specificaties**. Al het werk van 26 juli maakt de dunne pagina's draaglijker en
beter vindbaar. Geen enkel ontwerp lost het onderliggende tekort op.

EPREL is het eerste spoor dat daar écht aan zou kunnen komen. Vandaar dat punt 1
van deze lijst zo klein is en toch bovenaan staat.
