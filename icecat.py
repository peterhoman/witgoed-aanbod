"""
Foto-vangnet voor productafbeeldingen: drie lagen, geen handmatig speurwerk.

Sommige winkel-feeds leveren voor een product geen enkele foto (Coolblue/Awin
stuurt dan letterlijk 'noimage.gif'), en soms verloopt een eerder gevulde
asset-URL later stilletjes (een winkel-CDN die een link laat verlopen). Elke
winkel-sync roept aan het eind, in volgorde, drie stappen aan:

1. controleer_bestaande_fotos() — steekproef van al gevulde foto's op dode
   links (harde HTTP-foutstatus); wist een kapotte URL zodat stap 2/3 'm
   opnieuw kan vullen.
2. vul_ontbrekende_fotos() — voor elk product zonder foto (leeg of net
   gewist) een poging bij Open Icecat, de gratis productdatabank waarin
   fabrikanten (Philips, Krups, Roborock, ...) hun eigen foto's publiceren,
   opvraagbaar op EAN.
3. MANUAL_IMAGE_OVERRIDES — handmatig gevonden foto's voor de hardnekkige
   rest (merken achter Icecats betaalde laag, of EANs die Icecat niet kent).

Zonder foto blijft een product gewoon de nette template-placeholder tonen —
nooit een kapot img-icoon. Account: gratis Open Icecat-kanaalpartner
(shopname hieronder, aangemaakt 2026-07-17); geen wachtwoord/token nodig
voor de open content.
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
    # Liebherr Cue 2331 — MediaMarkt's asset-URL is verlopen (404); Expert's
    # eigen feed heeft 'm niet overschreven omdat image_url niet leeg was.
    '4016803145530': 'https://www.expert.nl/media/frontend/catalog/products/172/372635172/1260x1260/372635172-12055142.jpg',
}

# HTTP-statuscodes die een asset ondubbelzinnig als kapot bestempelen.
# Netwerkfouten (timeout, DNS) tellen expliciet niet mee: die kunnen
# tijdelijk zijn en zijn geen reden om een werkende foto te wissen.
_BROKEN_STATUS_MIN = 400

# Steekproefgrootte per sync-run voor de kapotte-linkcheck hieronder.
BROKEN_LINK_BATCH = 40


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


def _is_broken(url):
    """True als deze URL ondubbelzinnig geen foto meer levert.

    Een winkel-CDN laat een asset soms verlopen zonder dat de sync dat ooit
    merkt: 'image_url is niet leeg' geldt al als 'heeft een foto', ook als
    de link inmiddels een 404 teruggeeft (soms zelfs mét een klein
    placeholder-plaatje als body — de statuscode is dan het enige
    betrouwbare signaal, niet de aanwezigheid van response-bytes).
    """
    try:
        response = requests.head(url, timeout=8, allow_redirects=True)
        if response.status_code in (405, 501):
            # Niet elke CDN ondersteunt HEAD; val terug op een lichte GET.
            response = requests.get(url, timeout=8, stream=True)
        return response.status_code >= _BROKEN_STATUS_MIN
    except requests.RequestException:
        return False


def controleer_bestaande_fotos(db, Product):
    """Steekproef van al gevulde foto's controleren op dode links.

    Wist een URL bij een harde HTTP-foutstatus, zodat de rest van de
    vangnet-keten (winkel-feed op de volgende sync, dan Icecat, dan een
    handmatige override) 'm vanzelf weer aanvult — zie vul_ontbrekende_fotos.
    Draait op een willekeurige steekproef per sync-run (niet de hele
    catalogus per keer, dat zou elke sync merkbaar vertragen); bij ~2.700
    producten en meerdere syncs per dag is de hele catalogus binnen een
    week of twee een keer gecontroleerd.
    """
    producten = (Product.query
                 .filter(Product.image_url.isnot(None), Product.image_url != '')
                 .order_by(db.func.random())
                 .limit(BROKEN_LINK_BATCH).all())
    gewist = 0
    for product in producten:
        if _is_broken(product.image_url):
            logger.info(f"[!] Kapotte foto-link gewist: {product.title} "
                        f"({product.ean}) -> {product.image_url}")
            product.image_url = None
            gewist += 1
    if gewist:
        db.session.commit()
    logger.info(f"[+] Foto-linkcheck: {gewist} van {len(producten)} "
                f"gecontroleerde links kapot")
    return gewist


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
    winkel-sync (tot 12u later). Overschrijft bewust ook een niet-lege
    image_url: een regel in deze dict betekent dat de bestaande foto (leeg
    óf kapot, zoals een verlopen CDN-asset) al vastgesteld is als slecht.
    """
    if not MANUAL_IMAGE_OVERRIDES:
        return 0
    producten = Product.query.filter(Product.ean.in_(MANUAL_IMAGE_OVERRIDES.keys())).all()
    aangepast = 0
    for product in producten:
        nieuw = MANUAL_IMAGE_OVERRIDES[product.ean.strip()]
        if product.image_url != nieuw:
            product.image_url = nieuw
            aangepast += 1
    if aangepast:
        db.session.commit()
        logger.info(f"[+] Handmatige foto-overrides toegepast: {aangepast}")
    return aangepast
