"""
Icecat-vangnet voor ontbrekende productfoto's.

Sommige winkel-feeds leveren voor een product geen enkele foto (Coolblue/Awin
stuurt dan letterlijk 'noimage.gif'). Open Icecat is een gratis, wereldwijde
productdatabank waarin fabrikanten (o.a. Philips, Krups, Roborock) zelf hun
productfoto's publiceren, opvraagbaar op EAN. Elke winkel-sync roept aan het
eind vul_ontbrekende_fotos() aan: voor de paar producten zonder foto proberen
we er alsnog een bij Icecat op te halen.

Merken achter de betaalde laag ("brand restrictions") of onbekende EANs geven
gewoon geen resultaat; die producten houden de nette template-placeholder.
Account: gratis Open Icecat-kanaalpartner (shopname hieronder, aangemaakt
2026-07-17); er is geen wachtwoord of token nodig voor de open content.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

API_URL = 'https://live.icecat.biz/api'

# Ruim boven het aantal bekende fotoloze producten, maar begrensd zodat een
# gek databasebeeld niet tot duizenden API-calls per sync kan leiden.
MAX_PER_RUN = 25

# Laatste redmiddel voor producten die noch in hun winkel-feed, noch bij
# Icecat een foto hebben: meestal Coolblue-exclusieve modellen die Icecat
# niet kent, of merken achter Icecats betaalde laag (Melitta). Handmatig
# gevonden op de winkel-/fabrikantwebsite, en per URL geverifieerd dat hij
# als browser-embed vanaf ons eigen domein laadt (curl/bots kunnen door
# CDN-botbescherming een valse 403 geven terwijl de foto in een echte
# browser prima laadt — dus altijd zo verifiëren, niet alleen met curl).
MANUAL_IMAGE_OVERRIDES = {
    # Bosch WAN2827CNL Iron Assist — alleen bij Coolblue, geen feed-foto.
    '4242005535446': 'https://image.coolblue.nl/max/700xauto/products/2235063',
    # Siemens WM14N27XFG smartFinish — alleen bij Coolblue, geen feed-foto.
    '4242003978344': 'https://image.coolblue.nl/max/700xauto/products/2235171',
    # Melitta Look Therm Perfection 1025-16 — bij Icecat achter betaalde laag.
    '4006508222483': 'https://www.melitta.de/media/560x560/2a/77/a6/1726063696/kaffeemaschine-melitta-look-therm-schwarz-fkm-melitta-perfection-v-perfection-schwarz-therm-v-melitta-look-6769050-.png',
}


def _shopname():
    return os.getenv('ICECAT_SHOPNAME', 'pfmhoman')


def fetch_image(ean):
    """Foto-URL voor deze EAN uit Open Icecat, of None."""
    try:
        response = requests.get(
            API_URL,
            params={'shopname': _shopname(), 'lang': 'nl', 'GTIN': ean},
            timeout=20,
        )
        if response.status_code != 200:
            return None
        image = (response.json().get('data') or {}).get('Image') or {}
        return image.get('HighPic') or image.get('Pic500x500') or None
    except (requests.RequestException, ValueError) as e:
        logger.warning(f"[!] Icecat-fout voor EAN {ean}: {e}")
        return None


def vul_ontbrekende_fotos(db, Product):
    """Zoek voor producten zonder foto een afbeelding bij Icecat.

    Geeft het aantal gevulde foto's terug. Faalt stil (met logregel):
    een Icecat-storing mag nooit een winkel-sync laten mislukken.
    """
    zonder_foto = (Product.query
                   .filter(db.or_(Product.image_url.is_(None),
                                  Product.image_url == ''))
                   .limit(MAX_PER_RUN).all())
    gevuld = 0
    for product in zonder_foto:
        ean = (product.ean or '').strip()
        if not ean:
            continue
        url = fetch_image(ean) or MANUAL_IMAGE_OVERRIDES.get(ean)
        if url:
            product.image_url = url
            gevuld += 1
            logger.info(f"[+] Foto via Icecat/handmatig: {product.title} ({ean})")
    if gevuld:
        db.session.commit()
    logger.info(f"[+] Icecat-vangnet: {gevuld} van {len(zonder_foto)} "
                f"fotoloze producten gevuld")
    return gevuld


def apply_manual_image_overrides(db, Product):
    """Handmatige foto's meteen toepassen, los van de sync-cyclus.

    Draait bij elke app-start (zie app.py) zodat een net toegevoegde regel
    in MANUAL_IMAGE_OVERRIDES niet hoeft te wachten op de eerstvolgende
    winkel-sync (tot 12u later). Idempotent: raakt alleen producten die nu
    nog geen foto hebben.
    """
    if not MANUAL_IMAGE_OVERRIDES:
        return 0
    producten = Product.query.filter(
        Product.ean.in_(MANUAL_IMAGE_OVERRIDES.keys()),
        db.or_(Product.image_url.is_(None), Product.image_url == ''),
    ).all()
    for product in producten:
        product.image_url = MANUAL_IMAGE_OVERRIDES[product.ean.strip()]
    if producten:
        db.session.commit()
        logger.info(f"[+] Handmatige foto-overrides toegepast: {len(producten)}")
    return len(producten)
