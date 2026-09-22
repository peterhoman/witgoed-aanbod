"""Gezondheidscontrole: één adres dat GEZOND of STORING antwoordt.

Waarom dit bestaat
------------------
Gebouwd op 18 september 2026, een week voordat Peter acht dagen weg is. De
site draait vanzelf, maar niets waarschuwde als een winkelfeed stilvalt.
Dat is duur geworden sinds twee dingen samen bestaan:

- de veiligheidsklep (verouderde_aanbiedingen.py) zet aanbiedingen die drie
  dagen niet zijn ververst op niet-leverbaar; terecht, oude prijzen tonen is
  erger;
- een product zonder leverbare aanbieding krijgt 'noindex' (product.html).

Valt de Coolblue-feed stil, dan gaan na drie dagen 741 productpagina's die
alleen bij Coolblue staan op noindex; bij MediaMarkt 509. De voorpagina
blijft dan gewoon werken, dus een gewone bereikbaarheidsmeter ziet niets.

Dit adres wordt elke vijf minuten gelezen door UptimeRobot (gratis plan) en
die mailt Peter bij STORING. De meter slaat aan op de foutstatus 503 én op
het ontbreken van het woord GEZOND, zodat beide soorten meting werken.

De grenzen zijn gemeten, niet geschat (productie, 18 september 2026):
bij elke gezonde winkel was géén enkele leverbare aanbieding ouder dan 14
uur. Alleen EP had 54 van de 400 (13,5%) ouder dan 36 uur: dat is de
bekende halve feed van EP, geen storing. De grenzen liggen daar ruim boven,
want een loos alarm op vakantie kost meer dan een uur later gewaarschuwd
worden. Controleer de grenzen opnieuw als er een winkel bij komt of als
een winkel structureel anders gaat leveren.

Sinds 21 september 2026 is er een vierde controle: een bevroren feed, te
herkennen aan prijzen die niet meer bewegen. Zie BEWEGENDE_WINKELS hieronder
voor het waarom en de gemeten grenzen.

Bewust NIET gecontroleerd: EPREL (een afgebroken ronde kost niets),
prijssprongen en foto's. Alleen wat geld of vindbaarheid kost.
"""
from datetime import datetime, timedelta, timezone

# Elke winkel wordt minstens twee keer per dag gelezen (Bol vier keer). Na
# 30 uur zijn er dus minstens twee beurten gemist; de veiligheidsklep grijpt
# pas na 72 uur in. Er blijft dan ruim anderhalve dag om te handelen.
MAX_UREN_SINDS_SYNC = 30

# Een sync kan "draaien" terwijl de feed maar een deel levert (EP, augustus).
# Dan schuift de laatste sync wel op, maar blijft een deel van de
# aanbiedingen oud. Gezond = 0%; EP staat structureel op ~14%.
OUD_NA_UREN = 36
MAX_AANDEEL_OUD = 0.30
MIN_AANBIEDINGEN_VOOR_AANDEEL = 50   # bij 19 aanbiedingen (Alternate) zegt een percentage niets

# 2.923 leverbaar op 18 september 2026. Onder de 2.500 (-15%) is er iets
# groots weggevallen. Vaste bodem omdat er geen dagelijkse geschiedenis van
# dit getal wordt bewaard; pas aan als de catalogus blijvend krimpt of groeit.
MIN_LEVERBARE_PRODUCTEN = 2500

# Een routine die meer dan twee uur over haar geplande tijd heen is, zit vast.
MAX_UREN_OVER_TIJD = 2

# Bevroren feed (toegevoegd 21 september 2026). De controles hierboven kijken
# naar offers.last_synced, en elke sync zet dat op nu voor alles wat in de feed
# STAAT. Een feed die bevroren is maar nog alles opsomt, ververst last_synced
# dus gewoon en glipt langs de veiligheidsklep en langs de winkelcontrole. Dat
# bleek bij het toetsen van de Witgoedhuis-feed: 15 dagen niet gewijzigd, alles
# "op voorraad", actieprijzen die al voorbij waren. Wij zouden zulke prijzen
# als actueel tonen.
# Herkenbaar aan het uitblijven van prijswijzigingen. Gemeten over 60 dagen
# price_history: het langste gat zonder enige prijswijziging was 6 uur bij Bol,
# 24 uur bij Coolblue en 36 uur bij MediaMarkt. 60 uur ligt daar ruim boven.
# Bewust alleen deze drie: Expert had gaten van 48 uur, Voordeligwitgoed 144 en
# Alternate 420; daar zegt stilte niets en geeft ze alleen loos alarm. EP niet
# omdat die feed al half is. Komt er een grote winkel bij: eerst meten.
BEWEGENDE_WINKELS = ('bol', 'coolblue', 'mediamarkt')
MAX_UREN_ZONDER_PRIJSWIJZIGING = 60

WINKELS = ('bol', 'mediamarkt', 'coolblue', 'expert', 'alternate', 'ep',
           'voordeligwitgoed')

VERWACHTE_ROUTINES = (
    'Bol.com Product Sync', 'MediaMarkt Product Sync', 'Coolblue Product Sync',
    'Expert Product Sync', 'Alternate Product Sync', 'EP Product Sync',
    'Voordeligwitgoed Product Sync', 'Eigen productteksten bijwerken',
    'EPREL-gegevens bijwerken', 'Catalogusuitzonderingen toepassen',
    'IndexNow: gewijzigde adressen melden',
)


def _nu():
    """UTC zonder tijdzone, net als alle datumkolommen (zie models.utcnow)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def controleer_winkels(db, Offer, nu=None):
    """Meldingen over winkels waarvan de prijzen niet meer ververst worden."""
    nu = nu or _nu()
    meldingen, cijfers = [], {}
    grens_oud = nu - timedelta(hours=OUD_NA_UREN)
    for winkel in WINKELS:
        basis = db.session.query(db.func.count(Offer.id)).filter(
            Offer.retailer == winkel, Offer.is_available.is_(True))
        leverbaar = basis.scalar() or 0
        oud = basis.filter(Offer.last_synced < grens_oud).scalar() or 0
        laatst = (db.session.query(db.func.max(Offer.last_synced))
                  .filter(Offer.retailer == winkel).scalar())
        uren = None if laatst is None else round((nu - laatst).total_seconds() / 3600, 1)
        cijfers[winkel] = {'leverbaar': leverbaar, 'ouder_dan_36u': oud,
                           'uren_sinds_laatste_sync': uren}
        if uren is None:
            meldingen.append(f"{winkel}: nog nooit gelezen.")
        elif uren > MAX_UREN_SINDS_SYNC:
            meldingen.append(
                f"{winkel}: prijzen {uren:.0f} uur niet ververst (grens "
                f"{MAX_UREN_SINDS_SYNC}). Na 72 uur gaan deze aanbiedingen op "
                f"niet-leverbaar.")
        elif (leverbaar >= MIN_AANBIEDINGEN_VOOR_AANDEEL
              and oud / leverbaar > MAX_AANDEEL_OUD):
            meldingen.append(
                f"{winkel}: {oud} van de {leverbaar} leverbare aanbiedingen "
                f"zijn ouder dan {OUD_NA_UREN} uur. De feed levert "
                f"waarschijnlijk maar een deel.")
    return meldingen, cijfers


def controleer_prijsbeweging(db, PriceHistory, nu=None, sla_over=()):
    """Meldingen over grote winkels waar geen enkele prijs meer beweegt.

    `sla_over`: winkels waarvoor de winkelcontrole al alarm sloeg; een sync die
    niet loopt verklaart de stilte al, twee meldingen over hetzelfde is ruis.
    """
    nu = nu or _nu()
    meldingen, cijfers = [], {}
    for winkel in BEWEGENDE_WINKELS:
        laatst = (db.session.query(db.func.max(PriceHistory.recorded_at))
                  .filter(PriceHistory.retailer == winkel).scalar())
        uren = None if laatst is None else round((nu - laatst).total_seconds() / 3600, 1)
        cijfers[winkel] = {'uren_sinds_laatste_prijswijziging': uren}
        if winkel in sla_over:
            continue
        if uren is None:
            meldingen.append(f"{winkel}: nog nooit een prijswijziging vastgelegd.")
        elif uren > MAX_UREN_ZONDER_PRIJSWIJZIGING:
            meldingen.append(
                f"{winkel}: al {uren:.0f} uur geen enkele prijswijziging (grens "
                f"{MAX_UREN_ZONDER_PRIJSWIJZIGING}; normaal hooguit 36). De feed "
                f"wordt wel gelezen maar lijkt bevroren: de prijzen op de site "
                f"kunnen verouderd zijn.")
    return meldingen, cijfers


def controleer_catalogus(Product):
    leverbaar = Product.query.filter_by(is_available=True).filter(
        Product.is_example.isnot(True)).count()
    meldingen = []
    if leverbaar < MIN_LEVERBARE_PRODUCTEN:
        meldingen.append(
            f"Nog maar {leverbaar} leverbare producten (bodem "
            f"{MIN_LEVERBARE_PRODUCTEN}). Er is een groot deel weggevallen.")
    return meldingen, {'leverbare_producten': leverbaar}


def controleer_routines(jobs, nu_utc=None):
    """`jobs`: lijst van (naam, volgende_run) zoals de planner ze geeft;
    volgende_run is een datum mét tijdzone of None (gepauzeerd)."""
    nu_utc = nu_utc or datetime.now(timezone.utc)
    meldingen = []
    namen = {naam for naam, _ in jobs}
    for verwacht in VERWACHTE_ROUTINES:
        if verwacht not in namen:
            meldingen.append(f"Routine ontbreekt in de planner: {verwacht}.")
    for naam, volgende in jobs:
        if volgende is None:
            meldingen.append(f"Routine staat stil (geen volgende beurt): {naam}.")
        elif volgende < nu_utc - timedelta(hours=MAX_UREN_OVER_TIJD):
            uren = (nu_utc - volgende).total_seconds() / 3600
            meldingen.append(f"Routine is {uren:.0f} uur over tijd: {naam}.")
    return meldingen, {'routines_gepland': len(jobs)}


def rapport(db, Offer, Product, jobs, ai_sleutel_aanwezig, PriceHistory):
    """(gezond, meldingen, cijfers). Elke controle staat los: faalt er één
    met een fout, dan is dat zelf een melding en lopen de andere door."""
    meldingen, cijfers = [], {}

    def prijsbeweging():
        # Winkels die de winkelcontrole al noemde niet nog eens melden.
        al_gemeld = {w for w in BEWEGENDE_WINKELS
                     if any(m.startswith(w + ':') for m in meldingen)}
        return controleer_prijsbeweging(db, PriceHistory, sla_over=al_gemeld)

    onderdelen = (
        ('winkels', lambda: controleer_winkels(db, Offer)),
        ('prijsbeweging', prijsbeweging),      # na 'winkels': gebruikt haar meldingen
        ('catalogus', lambda: controleer_catalogus(Product)),
        ('routines', lambda: controleer_routines(jobs)),
    )
    for naam, controle in onderdelen:
        try:
            m, c = controle()
            meldingen += m
            cijfers[naam] = c
        except Exception as fout:  # een kapotte controle mag niet GEZOND opleveren
            meldingen.append(f"Controle '{naam}' kon niet draaien: {fout}")
    if not ai_sleutel_aanwezig:
        meldingen.append("De sleutel voor de eigen productteksten ontbreekt; "
                         "nieuwe producten krijgen geen tekst.")
    return (not meldingen), meldingen, cijfers


def als_tekst(gezond, meldingen, cijfers, nu=None):
    """Leesbaar op een telefoon: Peter opent dit adres vanuit de mail."""
    nu = nu or _nu()
    regels = ['GEZOND' if gezond else 'STORING',
              f"Gecontroleerd {nu:%d-%m-%Y %H:%M} UTC", '']
    if meldingen:
        regels += ['Wat er aan de hand is:'] + [f"- {m}" for m in meldingen] + ['']
    for winkel, c in (cijfers.get('winkels') or {}).items():
        regels.append(f"{winkel}: {c['leverbaar']} leverbaar, laatste sync "
                      f"{c['uren_sinds_laatste_sync']} uur geleden, "
                      f"{c['ouder_dan_36u']} ouder dan {OUD_NA_UREN} uur")
    for winkel, c in (cijfers.get('prijsbeweging') or {}).items():
        regels.append(f"{winkel}: laatste prijswijziging "
                      f"{c['uren_sinds_laatste_prijswijziging']} uur geleden")
    if 'catalogus' in cijfers:
        regels.append(f"Leverbare producten: {cijfers['catalogus']['leverbare_producten']}")
    if 'routines' in cijfers:
        regels.append(f"Routines gepland: {cijfers['routines']['routines_gepland']} "
                      f"van {len(VERWACHTE_ROUTINES)}")
    return '\n'.join(regels) + '\n'
