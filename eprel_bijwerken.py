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
from datetime import datetime, timedelta

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


# Eenmalige inhaalslag voor drogers (21 september 2026). Tot die dag zocht
# eprel.py drogers alleen in het oude register; alles wat daarvóór is
# opgehaald moet opnieuw, nu met het nieuwe register voorop: de 71 rijen uit
# 'tumbledriers', en de drogers die toen "niet gevonden" waren (modellen van
# na 1 juli 2025 staan alleen in het nieuwe register). Dat het bij één keer
# blijft zit in de peildatum: na het opnieuw ophalen is opgehaald_at nieuwer
# en valt de rij hier niet meer onder, ook als hij in het oude register
# blijft staan. Zonder peildatum zou zo'n rij elke ronde opnieuw aan de beurt
# komen en het verversbudget van 25 per ronde opeten.
#
# Daarnaast: een rij die in een vervallen register blijft staan kijken we
# wekelijks na in plaats van maandelijks. Fabrikanten melden hun drogers nog
# steeds opnieuw aan, en zolang dat niet gebeurd is tonen wij geen klasse. Dat
# zijn hoogstens enkele tientallen verzoeken per week.
# 21 september 2026 14:00 UTC: de laatste ronde met de oude code liep rond
# 09:13 UTC, de eerste met de nieuwe rond 15:13 UTC. Alles van voor dit moment
# is dus met de oude code opgehaald; wat de nieuwe code ophaalt valt erbuiten en
# komt niet nog eens aan de beurt.
_DROGERS_HERZIEN_VOOR = datetime(2026, 9, 21, 14, 0)
_VERVALLEN_REGISTER_NA_DAGEN = 7


def _drogers_in_te_halen(limiet):
    from eprel_specs import VEROUDERDE_LABELGROEPEN
    from models import Category, EprelData, Product, db, utcnow

    voor_peildatum = EprelData.opgehaald_at < _DROGERS_HERZIEN_VOOR
    oud_register = EprelData.productgroep.in_(list(VEROUDERDE_LABELGROEPEN))
    week_oud = EprelData.opgehaald_at < utcnow() - timedelta(
        days=_VERVALLEN_REGISTER_NA_DAGEN)
    droger_niet_gevonden = db.and_(
        EprelData.gevonden.is_(False),
        EprelData.product_id.in_(
            db.session.query(Product.id).join(Category, Category.id == Product.category_id)
            .filter(Category.slug == 'drogers')))
    return (EprelData.query
            .filter(db.or_(
                db.and_(oud_register, db.or_(voor_peildatum, week_oud)),
                db.and_(droger_niet_gevonden, voor_peildatum)))
            .order_by(EprelData.opgehaald_at)
            .limit(limiet).all())


def _afwijkend_typenummer(limiet):
    """Koppelingen waar het gevonden typenummer niet precies het gezochte is,
    opgehaald vóór de peildatum.

    Tot 21 september 2026 nam eprel._bevraag altijd de eerste treffer, terwijl
    EPREL op "begint met" zoekt. Gemeten: van 1.275 koppelingen 885 exact, 380
    langer, 10 anders. De meeste langere zijn goed (AEG en Beko zetten hun
    productcode erachter), maar een deel hangt aan een zustermodel terwijl het
    exacte model gewoon in het register staat (LG RT90X8 -> RT90X8BC). Opnieuw
    opzoeken met de nieuwe keuze zet die recht; wie goed stond, blijft goed.
    In Python gefilterd: 1.300 rijen, en "zonder opmaak vergelijken" is in SQL
    niet draagbaar tussen Postgres en SQLite.
    """
    from eprel import _kaal
    from models import EprelData

    uit = []
    for rij in (EprelData.query.filter(EprelData.gevonden.is_(True),
                                       EprelData.opgehaald_at < _DROGERS_HERZIEN_VOOR)
                .order_by(EprelData.opgehaald_at)):
        codes = {_kaal(c) for c in (rij.gezocht_op or '').split(',')}
        if _kaal(rij.modelnummer) not in codes:
            uit.append(rij)
            if len(uit) >= limiet:
                break
    return uit


def _inhaalslag(limiet):
    """Eerst de drogers (daar staat een fout label), dan de rest."""
    rijen = _drogers_in_te_halen(limiet)
    if len(rijen) < limiet:
        al = {r.id for r in rijen}
        rijen += [r for r in _afwijkend_typenummer(limiet) if r.id not in al]
    return rijen[:limiet]


def _te_verversen(limiet):
    """Rijen die te oud zijn geworden, oudste eerst. De inhaalslag gaat voor:
    dat zijn rijen waarvan we weten dat ze fout zijn of kunnen zijn."""
    from models import EprelData, Product, utcnow

    rijen = _inhaalslag(limiet)
    if len(rijen) < limiet:
        grens = utcnow() - timedelta(days=_VERVERS_NA_DAGEN)
        al = [r.id for r in rijen]
        rest = EprelData.query.filter(EprelData.opgehaald_at < grens)
        if al:
            rest = rest.filter(~EprelData.id.in_(al))
        rijen += (rest.order_by(EprelData.opgehaald_at)
                  .limit(limiet - len(rijen)).all())
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
        #
        # Uitzondering: zolang de inhaalslag voor drogers loopt, mag die de
        # hele ronde gebruiken. Dat zijn rijen waarvan we wéten dat ze fout
        # zijn (195 op 21 september 2026); met een kwart per ronde duurt dat
        # twee dagen, met een hele ronde twaalf uur. Nog steeds honderd
        # apparaten per ronde, dus Brussel merkt geen verschil.
        inhaal = len(_inhaalslag(_PER_RONDE))
        oud = _te_verversen(max(inhaal, int(_PER_RONDE * _VERVERS_DEEL)))
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
