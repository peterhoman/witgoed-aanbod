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


def _zonder_tekst(limiet):
    """Leverbare producten zonder eigen beschrijving, op id."""
    from models import AIContent, Product

    klaar = {r.product_id for r in
             AIContent.query.filter_by(content_type=_SOORT).all()}
    uit = []
    for product in Product.query.filter_by(is_available=True).order_by(Product.id):
        if product.id not in klaar:
            uit.append(product)
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


def vul_ontbrekende_teksten(app):
    """Schrijf beschrijvingen voor producten die er nog geen hebben.

    Publiceert meteen wat de controle schoon doorkomt; wat wordt aangestreept
    blijft opgeslagen maar onzichtbaar, zodat het nagelezen kan worden zonder
    dat er iets verkeerds op de site staat.
    """
    from ai_content import (Budgetstop, TekstFout, bewaak_budget, controleer,
                            schrijf_beschrijving, telbare_specs)
    from models import AIContent, db

    with app.app_context():
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

        producten = _zonder_tekst(_PER_RONDE)
        if not producten:
            logger.info("teksten bijwerken: elk leverbaar product heeft al een tekst")
            return

        geschreven, gepubliceerd, gevlagd, mislukt, euro = 0, 0, 0, 0, 0.0
        for product in producten:
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
            except Exception as e:
                logger.exception("teksten bijwerken: onverwachte fout bij %s",
                                 product.slug)
                mislukt += 1
                continue

            k = uitkomst['kosten']
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
