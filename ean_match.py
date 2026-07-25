"""EAN's uit winkelfeeds koppelen aan onze producten.

Onze catalogus heeft nette 13-cijferige EAN's (gecontroleerd: 2781 van de
2781). De feeds zijn slordiger: in de Expert-feed staan 1046 EAN's van twaalf
cijfers en 43 van elf. Dat komt doordat de voorloopnul wegvalt zodra een veld
onderweg als getal wordt behandeld in plaats van als tekst -- "0194644178093"
wordt dan "194644178093".

Een exacte tekstvergelijking mist die producten dus, terwijl het gewoon
hetzelfde apparaat is. Gemeten op de Expert-feed: 27 producten die we
hierdoor niet koppelden.

sync_alternate.py en sync_ep.py deden dit al goed met een eigen kopie van
deze functie; die gebruiken hem nu ook, zodat alle winkels dezelfde regel
volgen.
"""


def ean_sleutel(ean):
    """Sleutel om EAN's van beide kanten mee te vergelijken.

    Voorloopnullen weg, zodat '0194644178093' en '194644178093' op dezelfde
    sleutel uitkomen. Bewust niet aanvullen tot 13: sommige feeds leveren
    GTIN-14 met een extra nul ervoor, en die valt met deze regel ook weg.
    """
    return str(ean or '').strip().lstrip('0')


def zoek_product(Product, ean):
    """Zoek een product bij een EAN uit een feed, tolerant voor nullen.

    Eerst de exacte treffer -- dat is verreweg het vaakst raak en kost één
    query. Pas als die niets oplevert, proberen we de varianten met en zonder
    voorloopnullen. Zo betaalt de normale gang van zaken niets extra.
    """
    ean = str(ean or '').strip()
    if not ean:
        return None

    product = Product.query.filter_by(ean=ean).first()
    if product:
        return product

    kaal = ean.lstrip('0')
    varianten = []
    for lengte in (13, 12, 14):
        if len(kaal) < lengte:
            varianten.append(kaal.zfill(lengte))
    if kaal != ean:
        varianten.append(kaal)

    for variant in varianten:
        product = Product.query.filter_by(ean=variant).first()
        if product:
            return product
    return None
