"""De EPREL-gegevens bij onze apparaten ophalen en bijhouden.

Draait mee met de scheduler, net als teksten_bijwerken. Kost niets -- de
openbare EPREL-API is gratis -- maar dat is geen reden om er hard tegenaan te
gaan: honderd apparaten per ronde, één verzoek tegelijk, een halve seconde
ertussen.

Twee soorten werk, in deze volgorde:

  1. apparaten die nog nooit gezocht zijn;
  2. rijen die ouder zijn dan _VERVERS_NA_DAGEN.

Dat tweede is geen luxe maar een licentievoorwaarde: "when the Data is
stored locally, fail to ensure that the Data is kept up to date and
corrections, restrictions or deletion of the Data are reflected and
implemented in the data resulting from Your use of the API" (artikel 4 lid
2f). Een model kan uit het register verdwijnen of een gecorrigeerd label
krijgen, en dan hoort onze kopie mee te bewegen.

Waarom dit niet kan ontsporen
-----------------------------
- Hoogstens _PER_RONDE apparaten per keer.
- Een misser wordt vastgelegd, dus onvindbare apparaten worden niet elke
  ronde opnieuw geprobeerd. Zonder dat zou een derde van de catalogus
  eeuwig herhaald worden.
- Een apparaat zonder energielabel (stofzuiger, koffiemachine, magnetron)
  wordt niet eens gezocht.
- Valt EPREL uit, dan stopt de ronde en probeert de volgende het opnieuw.
  Er wordt niets weggegooid.
"""

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Honderd apparaten per ronde, viermaal per dag: de hele catalogus is in
# ongeveer een week rond. Er is geen haast -- deze gegevens veranderen
# nauwelijks -- en rustig bevragen is hier de fatsoensregel.
_PER_RONDE = 100

# Hoe oud een rij mag worden voordat hij opnieuw wordt opgehaald.
_VERVERS_NA_DAGEN = 30

# Hoeveel van een ronde hoogstens aan verversen opgaat. Nieuwe apparaten
# gaan voor: die hebben nog helemaal niets.
_VERVERS_DEEL = 0.25


def _te_doen(limiet):
    """Apparaten die nog nooit gezocht zijn, op id."""
    from models import EprelData, Product

    gedaan = {r.product_id for r in EprelData.query.with_entities(
        EprelData.product_id).all()}
    uit = []
    for product in Product.query.filter_by(is_available=True).order_by(Product.id):
        if product.id not in gedaan:
            uit.append(product)
            if len(uit) >= limiet:
                break
    return uit


def _te_verversen(limiet):
    """Rijen die te oud zijn geworden, oudste eerst."""
    from models import EprelData, Product, utcnow

    grens = utcnow() - timedelta(days=_VERVERS_NA_DAGEN)
    rijen = (EprelData.query
             .filter(EprelData.opgehaald_at < grens)
             .order_by(EprelData.opgehaald_at)
             .limit(limiet).all())
    if not rijen:
        return []
    producten = {p.id: p for p in Product.query.filter(
        Product.id.in_([r.product_id for r in rijen])).all()}
    return [(r, producten[r.product_id]) for r in rijen
            if r.product_id in producten]


def _schrijf(rij, product, uitkomst):
    """De uitkomst van één zoekopdracht in een rij zetten."""
    from models import utcnow

    rij.product_id = product.id
    rij.opgehaald_at = utcnow()
    if uitkomst is None:
        # Niet gezocht: geen energielabel voor dit soort, of geen typenummer
        # in de titel. Vastleggen als misser, anders komt hij elke ronde terug.
        rij.gevonden = False
        rij.gezocht_op = None
        return
    rij.gevonden = bool(uitkomst.get('gevonden'))
    rij.gezocht_op = (uitkomst.get('gezocht_op') or '')[:255] or None
    if not rij.gevonden:
        return
    rij.registratienummer = uitkomst.get('registratienummer')
    rij.productgroep = uitkomst.get('productgroep')
    rij.modelnummer = (uitkomst.get('modelnummer') or '')[:120] or None
    rij.leverancier = (uitkomst.get('leverancier') or '')[:160] or None
    rij.energieklasse = (uitkomst.get('energieklasse') or '')[:10] or None
    rij.gegevens = uitkomst.get('gegevens')


def vul_eprel_gegevens(app):
    """Zoek nieuwe apparaten op in EPREL en ververs wat te oud is geworden."""
    from eprel import EprelFout, zoek
    from models import EprelData, db

    with app.app_context():
        aantal_ververs = int(_PER_RONDE * _VERVERS_DEEL)
        nieuw = _te_doen(_PER_RONDE - aantal_ververs)
        oud = _te_verversen(aantal_ververs)

        if not nieuw and not oud:
            logger.info("eprel: niets te doen, alles is opgehaald en actueel")
            return

        raak = mis = ververst = 0
        gestopt = None

        for product in nieuw:
            try:
                uitkomst = zoek(product.category.name if product.category else '',
                                product.title)
            except EprelFout as e:
                gestopt = str(e)
                break
            rij = EprelData(product_id=product.id)
            _schrijf(rij, product, uitkomst)
            db.session.add(rij)
            # Per apparaat vastleggen: valt de rest om, dan is dit binnen.
            db.session.commit()
            if rij.gevonden:
                raak += 1
            else:
                mis += 1

        if gestopt is None:
            for rij, product in oud:
                try:
                    uitkomst = zoek(
                        product.category.name if product.category else '',
                        product.title)
                except EprelFout as e:
                    gestopt = str(e)
                    break
                _schrijf(rij, product, uitkomst)
                db.session.commit()
                ververst += 1

        resterend = len(_te_doen(_PER_RONDE + 1))
        logger.info(
            "eprel: %d gevonden, %d niet gevonden, %d ververst, nog %s te doen%s",
            raak, mis, ververst,
            f"minstens {resterend}" if resterend > _PER_RONDE else resterend,
            f" -- gestopt: {gestopt}" if gestopt else "")
