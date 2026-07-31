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

# De afloop van de laatste ronde, zodat /api/eprel hem kan tonen.
#
# Waarom in het geheugen en niet in de database: dit is toestand van het
# draaiende proces, geen gegeven over een apparaat. Gunicorn draait hier met
# 1 worker en 8 threads (zie railway.toml), dus de scheduler en de
# webpagina's zitten in hetzelfde proces en zien dezelfde waarde. Bij een
# herstart is hij leeg -- dat mag, want de eerstvolgende ronde vult hem
# opnieuw, en een afwijzing die blijft bestaan komt dan meteen weer terug.
#
# Zonder dit zou een blokkade door Brussel eruitzien als "er komt niets
# bij", en dan zoek je een week later naar de oorzaak. Dat is precies de
# stilte die deze week al twee keer tijd heeft gekost.
LAATSTE_RONDE = {
    'wanneer': None,
    'gevonden': 0,
    'niet_gevonden': 0,
    'ververst': 0,
    'afgebroken_door': None,
}


def _te_doen(limiet):
    """Apparaten die nog nooit gezocht zijn, om en om uit elke categorie.

    Niet op id, en dat is geen detail. Producten komen per categorie binnen
    bij een sync, dus hun id's liggen in blokken bij elkaar: de eerste ronde
    leverde 75 apparaten op waarvan er 30 een was-droogcombinatie waren en
    geen enkele een koelkast of oven. Dan weet je na een ronde nog steeds
    niet of de koppeling voor de rest van de catalogus deugt, en dat is
    precies wat je in deze fase wilt weten.

    Om en om uit elke categorie halen betekent dat de eerste ronde alle
    soorten raakt. Blijkt een categorie slecht te koppelen -- ovens en
    koelkasten hebben andere titelconventies dan wasmachines -- dan zie je
    dat meteen in plaats van over een week.

    Vaste volgorde op id binnen elke categorie, zodat een volgende ronde
    verdergaat waar deze ophield in plaats van dezelfde apparaten opnieuw te
    pakken.
    """
    from models import EprelData, Product

    gedaan = {r.product_id for r in EprelData.query.with_entities(
        EprelData.product_id).all()}

    per_categorie = {}
    for product in (Product.query.filter_by(is_available=True)
                    .order_by(Product.id)):
        if product.id in gedaan:
            continue
        per_categorie.setdefault(product.category_id, []).append(product)

    # Om en om: eerst van elke categorie de eerste, dan de tweede, enzovoort.
    # Een categorie die leegraakt valt vanzelf af, dus een kleine categorie
    # houdt de grote niet op.
    uit = []
    rijen = list(per_categorie.values())
    stand = 0
    while rijen and len(uit) < limiet:
        volgende = []
        for producten in rijen:
            if stand < len(producten):
                uit.append(producten[stand])
                if len(uit) >= limiet:
                    break
                volgende.append(producten)
        rijen = volgende if len(uit) < limiet else []
        stand += 1
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
    uitkomst = uitkomst or {}

    if not uitkomst.get('gezocht'):
        # Er is niet eens bij EPREL aangeklopt: dit soort staat er niet in,
        # of er valt geen typenummer uit de titel te halen. Wel vastleggen,
        # anders komt dit apparaat elke ronde terug -- maar niet als misser,
        # want het kan nooit een treffer worden.
        rij.gezocht = False
        rij.gevonden = False
        rij.gezocht_op = (uitkomst.get('reden') or '')[:255] or None
        return

    rij.gezocht = True
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
        # Eerst kijken of er iets te verversen valt. Zolang dat niet zo is --
        # de eerste maand na de start -- gaat de hele ronde naar nieuwe
        # apparaten in plaats van naar een gereserveerd kwart dat leegblijft.
        # Dat scheelt bij het vullen van 2.700 apparaten ruim twee dagen.
        oud = _te_verversen(int(_PER_RONDE * _VERVERS_DEEL))
        nieuw = _te_doen(_PER_RONDE - len(oud))

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

        from models import utcnow
        LAATSTE_RONDE.update({
            'wanneer': str(utcnow()),
            'gevonden': raak,
            'niet_gevonden': mis,
            'ververst': ververst,
            'afgebroken_door': gestopt,
        })

        resterend = len(_te_doen(_PER_RONDE + 1))
        logger.info(
            "eprel: %d gevonden, %d niet gevonden, %d ververst, nog %s te doen%s",
            raak, mis, ververst,
            f"minstens {resterend}" if resterend > _PER_RONDE else resterend,
            f" -- gestopt: {gestopt}" if gestopt else "")
