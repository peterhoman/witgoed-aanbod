"""Nieuwe producten vanzelf van een eigen beschrijving voorzien.

Waarom dit bestaat
------------------
Op 27-07 kregen 2806 producten in een keer een eigen tekst, via een batch die
met de hand werd gestart. Daarmee is het gat van dat moment gedicht, maar bij
elke sync komen er producten bij, en die zouden anders stilletjes terugvallen
op de verkooptekst van de winkel -- precies de dubbele inhoud waarvoor Google
100 van onze 449 beoordeelde pagina's oversloeg.

Dit draait mee met de scheduler, dus zonder webadres en zonder beheersleutel.

Waarom dit niet kan ontsporen
-----------------------------
De eigenaar heeft op een eerdere site meegemaakt dat een generator bleef
herschrijven; dat kostte bijna 800 euro voordat iemand het doorhad. Vier
grenzen, en ze staan er alle vier los van elkaar:

1. Alleen producten ZONDER tekst. Deze routine herschrijft nooit. Een bestaande
   tekst wordt niet aangeraakt, wat er ook met de gegevens gebeurt. (Het
   herschrijven bij wezenlijk rijkere data blijft bestaan, maar alleen op de
   route die een mens zelf start -- niet hier, onbewaakt, om vier uur 's nachts.)
2. Hoogstens _PER_RONDE per keer. Een gat van duizend producten wordt in
   porties gedicht, niet in een klap.
3. Het dagplafond (AI_DAGLIMIET_EURO) wordt voor ELKE tekst opnieuw getoetst,
   niet een keer vooraf. Loopt het toch vol, dan stopt hij halverwege.
4. Zonder ANTHROPIC_API_KEY doet hij niets.

Bij de normale gang van zaken -- een handvol nieuwe producten per sync -- kost
dit een paar cent per dag. De gemeten gemiddelde prijs over 2806 teksten was
een halve cent per stuk.
"""

import logging

logger = logging.getLogger(__name__)

# Hoeveel teksten er per ronde hoogstens bijkomen. Ruim boven wat een sync
# normaal oplevert, en klein genoeg dat een onverwacht gat in porties wordt
# gedicht in plaats van in een keer.
_PER_RONDE = 25

# Onder deze soort staan de teksten die voor de site bedoeld zijn; gelijk aan
# routes.main._TEKST_SOORT.
_SOORT = 'beschrijving'

# Onder deze soort staat een enkele rij die niets anders doet dan onthouden
# wanneer deze routine voor het laatst gedraaid heeft. Geen product, geen
# tekst voor de site -- alleen een datumstempel in generated_at.
#
# Waarom in ai_content en niet in een eigen tabel: dat scheelt een migratie
# op een draaiende database voor een gegeven dat uit één datum bestaat. Alle
# bestaande overzichten filteren op content_type, dus deze rij komt nergens
# tussen de teksten terecht; in /api/teksten/diagnose is hij zichtbaar onder
# rijen_per_soort, wat precies de plek is waar je hem zoekt.
_MARKERING = 'routine-laatst-gedraaid'


# Een nieuw product wacht op de EPREL-zoekronde voordat het een tekst krijgt.
# Gemeten 15 okt 2026: de Wisberg WBKVC200A20NFZ kreeg om 18:39 een tekst
# ("energielabel niet bekend") en een kwartier later vond EPREL het label,
# dat de pagina sindsdien toont. Elke rij in eprel_data (ook een misser)
# betekent "is opgezocht"; na _EPREL_WACHT_UREN schrijven we hoe dan ook.
_EPREL_WACHT_UREN = 48


def _zonder_tekst(limiet):
    """Leverbare producten zonder eigen beschrijving, op id."""
    from datetime import timedelta

    from models import AIContent, EprelData, Product, utcnow

    klaar = {r.product_id for r in
             AIContent.query.filter_by(content_type=_SOORT).all()}
    opgezocht = {r.product_id for r in
                 EprelData.query.with_entities(EprelData.product_id).all()}
    wacht_tot = utcnow() - timedelta(hours=_EPREL_WACHT_UREN)
    uit = []
    for product in Product.query.filter_by(is_available=True).order_by(Product.id):
        if product.id in klaar:
            continue
        if (product.id not in opgezocht and product.created_at
                and product.created_at > wacht_tot):
            continue
        uit.append(product)
        if len(uit) >= limiet:
            break
    return uit


# Eenmalige uitzondering op "deze routine herschrijft nooit" (13 okt 2026,
# Peters ja via de specialist-chat): de teksten van de proefproducten uit
# catalogus_aanvulling.py zijn geschreven zonder EPREL-gegevens in de prompt
# en zeggen daardoor "energielabel niet bekend" terwijl de pagina het label
# wél toont. Alleen die producten, alleen teksten van vóór dit moment, en
# alleen als er nu EPREL-gegevens zijn. Zelfbeperkend: een herschreven tekst
# is van ná dit moment en komt niet meer in aanmerking. Hoogstens ~100 stuks,
# per tekst langs de noodrem, in porties van _PER_RONDE.
#
# Uitgebreid op 13 okt 2026 (tweede ja van Peter): ook de ~475 andere
# producten met een EPREL-treffer waarvan de tekst "niet bekend" of "geen
# specificaties" zegt (193 noemden het energielabel onbekend terwijl de pagina
# het toont; scripts/meting_teksten_zonder_eprel.py). Zelfde grenzen: alleen
# teksten van vóór _PROEF_HERZIEN_VOOR, alleen met EPREL, per tekst langs de
# noodrem. Herzien gaat in porties van _HERZIEN_PER_RONDE (~575 stuks, ca.
# EUR 3 in totaal, binnen twee dagen klaar bij vier rondes per dag).
_PROEF_HERZIEN_VOOR = __import__('datetime').datetime(2026, 10, 13, 0, 0)
_HERZIEN_PER_RONDE = 100
# 15 okt 2026: ook "ontbreekt" ("Een energielabel ontbreekt in de gegevens"),
# 60 oude teksten met een EPREL-treffer.
# 16 okt 2026 (steekproef SEO-chat, Siemens WG64F7ACNL): ook "geen technische
# gegevens vastgelegd", "geen verdere specificaties", "onbekend" e.d. --
# 120 oude teksten met een EPREL-treffer. Alleen teksten van voor 13 okt.
_ZEGT_ONBEKEND = ('%niet bekend%', '%geen specificaties%', '%ontbreekt%',
                  '%geen technische gegevens%', '%geen verdere specificaties%',
                  '%geen gegevens%', '%niet vastgelegd%', '%onbekend%',
                  '%geen nadere%', '%niet opgenomen%', '%niet beschikbaar%')
# Teksten (van elke datum) die het label onbekend noemen terwijl EPREL nu een
# energieklasse heeft: herschrijven. Geen lus: de nieuwe tekst krijgt de
# klasse mee en noemt hem dus niet meer onbekend.
_LABEL_ONBEKEND = __import__('re').compile(
    r'energie(label|klasse)[^.]{0,60}(niet bekend|onbekend|ontbreekt)', __import__('re').I)


def _proefteksten_om_te_herzien(limiet):
    """[(product, tekstrij)] voor proefproducten, en voor producten waarvan de
    tekst "niet bekend"/"geen specificaties" zegt, met een tekst van vóór de
    EPREL-reparatie en met EPREL-gegevens die nu wel in de prompt gaan.
    Proefproducten eerst."""
    from ai_content import _eprel_regels
    from models import AIContent, CatalogusAanvulling, Product, db

    # Loopt er een herzieningsbatch (half tarief), dan hier niets dubbel doen.
    if AIContent.query.filter_by(content_type=_HERZIEN_BATCH_SOORT).first():
        return []

    proef =[r.product_id for r in CatalogusAanvulling.query.all() if r.product_id]
    onbekend = [p.id for p in Product.query.with_entities(Product.id).filter(
        Product.is_available.is_(True),
        db.or_(*[Product.ai_description.ilike(w) for w in _ZEGT_ONBEKEND])).all()]
    volgorde = {pid: i for i, pid in enumerate(proef + [p for p in onbekend if p not in set(proef)])}
    ids = list(volgorde)
    if not ids:
        return []
    uit = []
    rijen = (AIContent.query
             .filter(AIContent.content_type == _SOORT,
                     AIContent.product_id.in_(ids),
                     AIContent.generated_at < _PROEF_HERZIEN_VOOR).all())
    for rij in sorted(rijen, key=lambda r: volgorde[r.product_id]):
        product = Product.query.get(rij.product_id)
        if product is None or not product.is_available or not _eprel_regels(product):
            continue
        uit.append((product, rij))
        if len(uit) >= limiet:
            return uit

    # Daarna: teksten van elke datum die het label onbekend noemen terwijl
    # EPREL nu een energieklasse levert.
    al = {p.id for p, _ in uit}
    for product in Product.query.filter(
            Product.is_available.is_(True),
            db.or_(Product.ai_description.ilike('%energielabel%'),
                   Product.ai_description.ilike('%energieklasse%'))).order_by(Product.id):
        if product.id in al or not _LABEL_ONBEKEND.search(product.ai_description or ''):
            continue
        if not any(r.startswith('- Energieklasse:') for r in _eprel_regels(product)):
            continue
        rij = AIContent.query.filter_by(product_id=product.id, content_type=_SOORT).first()
        if rij is None:
            continue
        uit.append((product, rij))
        if len(uit) >= limiet:
            break
    return uit


def _publiceer_wat_schoon_werd():
    """Opgeslagen teksten die de controle nu wel doorkomen alsnog zichtbaar maken.

    De controle draait bij elke aanroep opnieuw over alles wat er ligt, dus een
    verfijning van de regels verandert met terugwerkende kracht het oordeel over
    bestaande teksten. Zonder deze stap zouden die teksten opgeslagen blijven en
    onzichtbaar, en zou er een handmatige publicatieronde nodig zijn -- terwijl
    de tekst er allang is en betaald.

    Aanleiding: de zeef streepte 19 teksten aan, waarvan er 15 alleen het woord
    "aanbieding" bevatten in de betekenis "dit artikel" ("Deze aanbieding
    betreft een combinatie van twee losse apparaten"). Na het verfijnen van die
    regel horen ze gewoon op de site.

    Kost niets: er wordt niets geschreven bij het model, alleen gekopieerd.
    """
    from ai_content import controleer
    from models import AIContent, Product, db

    zonder = {p.id: p for p in Product.query.filter(
        Product.ai_description.is_(None), Product.is_available.is_(True)).all()}
    if not zonder:
        return 0

    aantal = 0
    for rij in AIContent.query.filter(
            AIContent.content_type == _SOORT,
            AIContent.product_id.in_(zonder.keys())).all():
        if not (rij.content or '').strip() or controleer(rij.content):
            continue
        zonder[rij.product_id].ai_description = rij.content
        aantal += 1
    if aantal:
        db.session.commit()
    return aantal


def _ruim_proefteksten_op():
    """De proefrondes van 27 juli weggooien; die worden nergens gebruikt.

    proef-v1 (17 rijen) en proef-v2 (28 rijen) waren de steekproeven waarmee
    de instructie is afgesteld voordat de hele catalogus werd geschreven. Ze
    staan los van de teksten op de site en houden alleen ruimte bezet.

    Zelfbeperkend: zodra ze weg zijn doet deze functie niets meer.
    """
    from models import AIContent, db

    aantal = AIContent.query.filter(
        AIContent.content_type.like('proef-%')).delete(synchronize_session=False)
    if aantal:
        db.session.commit()
    return aantal


def laatste_run(app):
    """Wanneer deze routine voor het laatst gedraaid heeft (naïeve UTC), of None.

    Gelezen door de scheduler om de eerstvolgende run te verankeren aan het
    laatste échte draaimoment in plaats van aan de processtart. Zie de uitleg
    bij _noteer_run.
    """
    from models import AIContent

    try:
        with app.app_context():
            rij = AIContent.query.filter_by(content_type=_MARKERING).first()
            return rij.generated_at if rij else None
    except Exception as e:
        # Een lege of onbereikbare database mag het opstarten niet tegenhouden;
        # zonder stempel valt de scheduler terug op zijn oude gedrag.
        logger.warning("teksten bijwerken: laatste draaimoment onbekend -- %s", e)
        return None


def _noteer_run():
    """Vastleggen dat de routine nu gedraaid heeft.

    Zonder dit stempel bestaat het draaimoment alleen in het geheugen van het
    proces, en dat is precies wat er bij elke uitrol verdwijnt: een
    'interval'-job vuurt pas ná het hele interval, dus met een paar deploys op
    een dag schuift hij telkens vooruit en draait hij niet meer.

    Dit is dezelfde constructie die de zes winkel-syncs al hebben (die haken
    aan offers.last_synced, zie scheduler.eerste_run). Deze routine schrijft
    alleen bij als er iets te schrijven valt, dus er is geen bestaand veld dat
    betrouwbaar zegt dat hij gedraaid heeft -- vandaar een eigen stempel.
    """
    from models import AIContent, db, utcnow

    rij = AIContent.query.filter_by(content_type=_MARKERING).first()
    if rij is None:
        rij = AIContent(
            content_type=_MARKERING,
            content='Markering: wanneer teksten_bijwerken voor het laatst draaide.')
        db.session.add(rij)
    rij.generated_at = utcnow()
    db.session.commit()


def vul_ontbrekende_teksten(app):
    """Schrijf beschrijvingen voor producten die er nog geen hebben.

    Publiceert meteen wat de controle schoon doorkomt; wat wordt aangestreept
    blijft opgeslagen maar onzichtbaar, zodat het nagelezen kan worden zonder
    dat er iets verkeerds op de site staat.
    """
    with app.app_context():
        # Het stempel hoort bij elke afloop gezet te worden, ook bij een ronde
        # die halverwege stopt op het dagplafond of die zonder sleutel meteen
        # terugkeert: hij zegt "deze routine is langs geweest", niet "er is
        # tekst geschreven". Zonder finally zou een ronde zonder werk als
        # achterstallig blijven gelden.
        try:
            _draai_ronde(app)
        finally:
            _noteer_run()


# Herziening van ALLE oude teksten (van voor _PROEF_HERZIEN_VOOR) bij een
# EPREL-treffer, via de Batch API tegen half tarief (Peters ja 16 okt 2026,
# met als voorwaarde: alleen via batch, ~EUR 4). Eén batch tegelijk; de
# administratierij (content_type _HERZIEN_BATCH_SOORT, content = batch-id)
# bestaat zolang hij loopt. Zolang er een loopt, doet de herziening tegen vol
# tarief (_proefteksten_om_te_herzien) niets, zodat niets dubbel betaald wordt.
# Zelfbeperkend: een verwerkte tekst is van na de afkapdatum en komt nooit
# meer in aanmerking.
_HERZIEN_BATCH_SOORT = 'herzien-batch'
_HERZIEN_BATCH_MAX = 800
# Gemeten 16 okt 2026: 643 batchteksten kostten EUR 5,71.
_BATCH_EURO_PER_TEKST = 0.009


def _batch_kandidaten(limiet=_HERZIEN_BATCH_MAX):
    """Leverbare producten met een tekst van voor de afkapdatum en EPREL-gegevens."""
    from ai_content import _eprel_regels
    from models import AIContent, EprelData, Product

    met_eprel = {r.product_id for r in EprelData.query.with_entities(EprelData.product_id)
                 .filter(EprelData.gevonden.is_(True)).all()}
    uit = []
    for rij in (AIContent.query
                .filter(AIContent.content_type == _SOORT,
                        AIContent.generated_at < _PROEF_HERZIEN_VOOR,
                        AIContent.product_id.in_(met_eprel))
                .order_by(AIContent.product_id)):
        product = Product.query.get(rij.product_id)
        if product is None or not product.is_available or not _eprel_regels(product):
            continue
        uit.append(product)
        if len(uit) >= limiet:
            break
    return uit


def _herzien_via_batch(app, sleutel):
    """Lever de herziening in als batch, of verwerk hem als hij klaar is."""
    from ai_content import batch_resultaten, batch_toestand, controleer, dien_batch_in
    from models import AIContent, Product, db

    rij = AIContent.query.filter_by(content_type=_HERZIEN_BATCH_SOORT).first()
    if rij is None:
        kandidaten = _batch_kandidaten()
        if not kandidaten:
            return
        # Noodrem ook voor batches (Peters akkoord 17 okt 2026): de eerste
        # batch kostte EUR 5,71 en bracket 16 okt op EUR 5,85, boven de grens,
        # omdat het bedrag pas bij het verwerken geboekt wordt. Nu vooraf
        # rekenen: wat vandaag al uitgegeven is plus _BATCH_EURO_PER_TEKST per
        # tekst moet onder de daggrens blijven; de rest gaat een dag later.
        from ai_content import besteed_vandaag
        ruimte = app.config['AI_DAGLIMIET_EURO'] - besteed_vandaag()
        past = int(max(ruimte, 0) // _BATCH_EURO_PER_TEKST)
        if past <= 0:
            logger.info("teksten bijwerken: herzieningsbatch wacht op de noodrem "
                        "(nog EUR %.2f ruimte vandaag)", ruimte)
            return
        if len(kandidaten) > past:
            logger.info("teksten bijwerken: noodrem: %d van %d teksten in deze batch, "
                        "de rest later", past, len(kandidaten))
            kandidaten = kandidaten[:past]
        batch_id = dien_batch_in(kandidaten, model=app.config.get('ANTHROPIC_MODEL'),
                                 api_key=sleutel)
        db.session.add(AIContent(product_id=None, content_type=_HERZIEN_BATCH_SOORT,
                                 content=batch_id, cost=0.0))
        db.session.commit()
        logger.info("teksten bijwerken: herzieningsbatch %s ingeleverd met %d teksten",
                    batch_id, len(kandidaten))
        return

    batch_id = rij.content
    toestand = batch_toestand(batch_id, sleutel)
    if not toestand['klaar']:
        logger.info("teksten bijwerken: herzieningsbatch %s nog bezig (%s)", batch_id, toestand)
        return

    opgeslagen, gepubliceerd, overgeslagen, mislukt, euro = 0, 0, 0, 0, 0.0
    for uitkomst in batch_resultaten(batch_id, sleutel):
        try:
            if uitkomst['fout']:
                mislukt += 1
                continue
            product = Product.query.get(uitkomst['product_id'])
            oud = AIContent.query.filter_by(product_id=uitkomst['product_id'],
                                            content_type=_SOORT).first()
            # Intussen al (tegen vol tarief) herschreven of verdwenen: laten.
            if product is None or (oud is not None and oud.generated_at
                                   and oud.generated_at >= _PROEF_HERZIEN_VOOR):
                overgeslagen += 1
                continue
            if oud is not None:
                db.session.delete(oud)
            k = uitkomst['kosten']
            db.session.add(AIContent(
                product_id=product.id, content_type=_SOORT, content=uitkomst['tekst'],
                tokens_used=(k['invoer'] + k['uitvoer'] + k['cache_geschreven'] + k['cache_gelezen']),
                cost=k['euro'], bron_specs=None))
            if not controleer(uitkomst['tekst']):
                product.ai_description = uitkomst['tekst']
                gepubliceerd += 1
            db.session.commit()
            opgeslagen += 1
            euro += k['euro']
        except Exception:
            db.session.rollback()
            mislukt += 1
            logger.exception("teksten bijwerken: batchtekst verwerken mislukt (%s)",
                             uitkomst.get('product_id'))
    db.session.delete(rij)
    db.session.commit()
    logger.info("teksten bijwerken: herzieningsbatch %s verwerkt: %d opgeslagen (%d live), "
                "%d overgeslagen, %d mislukt, EUR %.4f", batch_id, opgeslagen, gepubliceerd,
                overgeslagen, mislukt, euro)


def _draai_ronde(app):
    """Het eigenlijke werk. Draait binnen de app-context van de aanroeper."""
    from ai_content import (Budgetstop, TekstFout, bewaak_budget, controleer,
                            schrijf_beschrijving)
    from models import AIContent, db

    # Deze twee kosten niets en hebben geen sleutel nodig, dus ze staan
    # vooraan: ook een ronde waarin niets te schrijven valt (of waarin de
    # sleutel ontbreekt) moet ze uitvoeren.
    alsnog = _publiceer_wat_schoon_werd()
    opgeruimd = _ruim_proefteksten_op()
    if alsnog or opgeruimd:
        logger.info("teksten bijwerken: %d alsnog zichtbaar gemaakt, "
                    "%d proefrijen opgeruimd", alsnog, opgeruimd)

    sleutel = app.config.get('ANTHROPIC_API_KEY')
    if not sleutel:
        logger.info("teksten bijwerken: geen ANTHROPIC_API_KEY, overgeslagen")
        return

    # De batchherziening mag de rest van de ronde nooit tegenhouden.
    try:
        _herzien_via_batch(app, sleutel)
    except Exception:
        logger.exception("teksten bijwerken: batchherziening mislukt")

    producten = [(p, None) for p in _zonder_tekst(_PER_RONDE)]
    # Ontbrekende teksten gaan voor; met de ruimte die overblijft de
    # proefteksten herzien (zie _PROEF_HERZIEN_VOOR).
    if len(producten) < _PER_RONDE:
        producten += _proefteksten_om_te_herzien(_HERZIEN_PER_RONDE)
    if not producten:
        logger.info("teksten bijwerken: elk leverbaar product heeft al een tekst")
        return

    geschreven, gepubliceerd, gevlagd, mislukt, euro = 0, 0, 0, 0, 0.0
    for product, oude_rij in producten:
        try:
            # Voor elke tekst opnieuw toetsen, niet een keer vooraf: anders
            # merkt een ronde die uit de hand loopt het plafond pas als het
            # geld op is.
            bewaak_budget(app.config['AI_DAGLIMIET_EURO'])
            uitkomst = schrijf_beschrijving(
                product, model=app.config.get('ANTHROPIC_MODEL'),
                api_key=sleutel)
        except Budgetstop as e:
            logger.warning("teksten bijwerken: gestopt door de noodrem -- %s", e)
            break
        except TekstFout as e:
            logger.warning("teksten bijwerken: %s voor %s", e, product.slug)
            mislukt += 1
            continue
        except Exception:
            logger.exception("teksten bijwerken: onverwachte fout bij %s",
                             product.slug)
            mislukt += 1
            continue

        k = uitkomst['kosten']
        # Herziening: de oude rij gaat weg, er hoort er per product precies
        # een te zijn. Wordt de nieuwe aangestreept, dan blijft de oude tekst
        # tot die tijd zichtbaar staan (ai_description wordt dan niet gewist).
        if oude_rij is not None:
            db.session.delete(oude_rij)
        db.session.add(AIContent(
            product_id=product.id, content_type=_SOORT,
            content=uitkomst['tekst'],
            tokens_used=(k['invoer'] + k['uitvoer']
                         + k['cache_geschreven'] + k['cache_gelezen']),
            cost=k['euro'], bron_specs=uitkomst['bron_specs']))
        # Alleen zichtbaar maken wat schoon is. Een aangestreepte tekst
        # blijft staan om nagelezen te worden; het product houdt zolang de
        # winkeltekst, wat beter is dan een zin die over een maand niet
        # meer klopt.
        if controleer(uitkomst['tekst']):
            gevlagd += 1
        else:
            product.ai_description = uitkomst['tekst']
            gepubliceerd += 1
        # Meteen vastleggen: valt de rest om, dan is dit binnen en is het
        # betaalde werk niet weg.
        db.session.commit()
        geschreven += 1
        euro += k['euro']

    resterend = len(_zonder_tekst(_PER_RONDE + 1))
    logger.info(
        "teksten bijwerken: %d geschreven (%d live, %d aangestreept, "
        "%d mislukt), EUR %.4f, nog %s zonder tekst",
        geschreven, gepubliceerd, gevlagd, mislukt, euro,
        f"minstens {resterend}" if resterend > _PER_RONDE else resterend)
