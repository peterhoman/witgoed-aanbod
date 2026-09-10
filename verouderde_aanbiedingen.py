"""Aanbiedingen die te lang niet zijn ververst niet meer als leverbaar tonen.

Waarom dit bestaat
------------------
Op 10 september 2026 bleek dat de site bij 572 EP-aanbiedingen een prijs
toonde die sinds eind juli niet meer was ververst. EP's feed levert sinds
begin augustus nog maar 373 van de 980 aanbiedingen die wij kennen; de
veiligheidsklep in de sync (minder dan de helft terug = niets opruimen)
hield die 600 rijen terecht vast, maar liet ze ook gewoon als "leverbaar"
op de site staan. Bij 326 apparaten was die zes weken oude EP-prijs de
laagste, en dus de prijs die wij als vergelijking toonden. Bij Coolblue
stonden op dezelfde manier 325 aanbiedingen uit juli.

Een prijsvergelijker die oude prijzen als actueel toont is erger dan een
die minder winkels toont. Daarom: een aanbieding die langer dan
DREMPEL_DAGEN niet is ververst, wordt op niet-leverbaar gezet. De rij
blijft bestaan, zodat de aanbieding meteen terugkomt zodra de feed haar
weer levert -- de sync zet is_available dan gewoon weer op wat de feed zegt.

Drie dagen is ruim: elke winkel wordt twee keer per dag gelezen, dus dit
grijpt pas in na zes gemiste beurten. Een haperende nacht kost niets.

Draait in de uurlijkse opruimronde (catalogus_uitzonderingen.pas_toe).
"""
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

DREMPEL_DAGEN = 3


def verberg_verouderde(db, dagen=DREMPEL_DAGEN):
    """Zet aanbiedingen die langer dan `dagen` niet zijn ververst op
    niet-leverbaar en werk de prijs van de betrokken producten bij.

    Geeft (aantal_verborgen, aantal_producten_bijgewerkt) terug.
    """
    from models import Offer, Product, utcnow

    grens = utcnow() - timedelta(days=dagen)
    verouderd = (Offer.query
                 .filter(Offer.is_available.is_(True),
                         Offer.last_synced < grens)
                 .all())
    if not verouderd:
        return 0, 0

    per_winkel = {}
    product_ids = set()
    for offer in verouderd:
        offer.is_available = False
        per_winkel[offer.retailer] = per_winkel.get(offer.retailer, 0) + 1
        product_ids.add(offer.product_id)
    db.session.flush()

    # De categorie- en zoekpagina's kijken naar products.price en
    # products.is_available, niet naar de aanbiedingen zelf. Zonder deze stap
    # zou een verborgen aanbieding nog steeds de laagste prijs in het filter
    # bepalen.
    bijgewerkt = 0
    for product in Product.query.filter(Product.id.in_(product_ids)).all():
        product.refresh_pricing()
        bijgewerkt += 1
    db.session.commit()

    logger.warning("[!] %d aanbiedingen ouder dan %d dagen verborgen (%s); %d producten bijgewerkt",
                   len(verouderd), dagen,
                   ', '.join(f"{w} {n}" for w, n in sorted(per_winkel.items(), key=lambda x: -x[1])),
                   bijgewerkt)
    return len(verouderd), bijgewerkt


def telling_per_winkel(db, dagen=DREMPEL_DAGEN):
    """Hoeveel aanbiedingen per winkel langer dan `dagen` niet ververst zijn,
    leverbaar of niet. Voor /api/sync-status: dit is het cijfer dat laat zien
    dat een feed stilstaat, nog voordat iemand het op de site merkt."""
    from models import Offer, utcnow

    grens = utcnow() - timedelta(days=dagen)
    rijen = (db.session.query(Offer.retailer, db.func.count(Offer.id))
             .filter(Offer.last_synced < grens)
             .group_by(Offer.retailer)
             .all())
    return {winkel: aantal for winkel, aantal in rijen}
