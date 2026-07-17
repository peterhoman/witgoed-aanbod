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
        url = fetch_image(ean)
        if url:
            product.image_url = url
            gevuld += 1
            logger.info(f"[+] Foto via Icecat: {product.title} ({ean})")
    if gevuld:
        db.session.commit()
    logger.info(f"[+] Icecat-vangnet: {gevuld} van {len(zonder_foto)} "
                f"fotoloze producten gevuld")
    return gevuld
