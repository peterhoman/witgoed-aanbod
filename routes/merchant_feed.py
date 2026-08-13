"""Productfeed voor Google Merchant Center: /feeds/google-merchant.xml.

Waarom dit bestaat (10 aug 2026): de producten stonden tot nu toe in
Merchant Center doordat Google ze zelf van onze pagina's plukte. Zulke
artikelen vervallen ~30 dagen na Googles laatste bezoek, en omdat Google
de pagina's amper herbezoekt is het account leeggelopen (1.380 -> 0).
Met een eigen feed bepalen wij wat er staat en verloopt er niets.

LET OP: deze feed staat klaar maar is bewust nog NIET aangemeld in
Merchant Center. Aanmelden gebeurt pas na de uitslag van de lopende
accountbeoordeling ("Verkeerde voorstelling", aangevraagd 4 aug), en
alleen als die uitslag niet wijst op "site verkoopt zelf niets" als
kernprobleem. Googles beleid is op verkopers geschreven; een expliciet
verbod op vergelijkers is er niet, en Google heeft deze site eerder
zelf als bron opgevoerd (1.280 goedgekeurde producten), maar het blijft
een besluit dat Peter neemt met de uitslag in de hand.

Keuzes, allemaal volgens de kernregel "beweer niets wat de data niet
draagt":

- Alleen leverbare producten met een geldig 13-cijferig EAN, een foto en
  een prijs. Voorbeeldproducten (is_example) blijven eruit.
- g:price is de laagste leverbare prijs -- exact wat de pagina toont.
- g:image_link gaat via de wsrv-verkleiner (filter_helpers.foto_url, op
  800px) — dezelfde adressen die de site aan bezoekers toont. Eerst stond
  hier de originele winkelfoto, maar de fotoserver van Coolblue
  (coolblue.bynder.com) verbiedt alle crawlers in robots.txt, waardoor
  Googlebot-Image 1.049 foto's niet mocht ophalen en Merchant Center die
  producten afkeurde (gemeten 12 aug). wsrv laat Googlebot wél toe.
- Geen g:shipping: de winkelfeeds leveren geen betrouwbare bezorgkosten,
  dus die verzinnen we niet. Keurt Google producten af op ontbrekende
  verzendkosten, dan is dat zichtbaar in Merchant Center en beslissen we
  dan -- niet vooraf met een gegokt bedrag.
- g:energy_efficiency_class alleen als EPREL de klasse echt kent (A-G).
- De productlink is percent-gecodeerd zoals in de sitemap (De'Longhi,
  "Hot & Cold"), en wijst met www, zodat de doorstuur nooit meespeelt.
- g:id is het interne product-id: stabiel, ook als een titel of slug
  ooit wijzigt. Het EAN staat al in g:gtin.

De XML wordt met ElementTree opgebouwd: geen handmatige escaping, geen
kans op een kapot bestand door een & of < in een titel.
"""
from urllib.parse import quote
from xml.etree import ElementTree as ET

import requests
from flask import Blueprint, Response, abort, current_app

from filter_helpers import foto_url
from models import Product, EprelData
from product_specs import merknaam

merchant_bp = Blueprint('merchant', __name__)

_G = 'http://base.google.com/ns/1.0'
_GELDIGE_KLASSEN = {'A', 'B', 'C', 'D', 'E', 'F', 'G'}
# Merchant Center kapt titels op 150 tekens en beschrijvingen op 5000.
_MAX_TITEL = 150
_MAX_BESCHRIJVING = 5000


def _geldig_ean(ean):
    ean = (ean or '').strip()
    return ean if len(ean) == 13 and ean.isdigit() else None


def _beschrijving(product):
    """Eigen tekst boven de winkeltekst; leeg veld liever dan opvulsel."""
    tekst = (product.ai_description or product.description or '').strip()
    return tekst[:_MAX_BESCHRIJVING] if tekst else None


def _energieklassen():
    """{product_id: 'A'} voor apparaten waarvan EPREL de klasse kent."""
    rijen = (EprelData.query.filter_by(gevonden=True)
             .with_entities(EprelData.product_id, EprelData.energieklasse).all())
    klassen = {}
    for pid, klasse in rijen:
        letter = (klasse or '').strip().upper()[:1]
        if letter in _GELDIGE_KLASSEN:
            klassen[pid] = letter
    return klassen


def _sub(item, naam, tekst, ns=False):
    el = ET.SubElement(item, f'{{{_G}}}{naam}' if ns else naam)
    el.text = tekst
    return el


@merchant_bp.route('/feeds/google-merchant.xml')
def google_merchant_feed():
    site = current_app.config['SITE_URL'].rstrip('/')
    ET.register_namespace('g', _G)

    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    _sub(channel, 'title', 'WitgoedAanbod.nl')
    _sub(channel, 'link', site + '/')
    _sub(channel, 'description',
         'Witgoed vergelijken: actuele prijzen van Nederlandse winkels.')

    klassen = _energieklassen()
    # selectinload: alle aanbiedingen in één extra query, in plaats van één
    # query per product zodra lowest_price ze aanraakt. Bij 2.800 producten
    # is dat het verschil tussen 2 queries en 2.800 (bekende valkuil).
    from sqlalchemy.orm import selectinload
    producten = (Product.query.options(selectinload(Product.offers))
                 .filter_by(is_available=True)
                 .filter(Product.image_url.isnot(None)).all())

    aantal = 0
    for product in producten:
        ean = _geldig_ean(product.ean)
        prijs = product.lowest_price
        # 'not product.image_url' naast het isnot(None)-filter in de query:
        # bij een handvol producten levert de feed een LEGE tekst als
        # fotoveld, en dat is niet NULL. Zonder foto geen vermelding --
        # Google eist image_link, en een item zonder wordt afgekeurd.
        if (not ean or not prijs or prijs <= 0 or product.is_example
                or not product.image_url):
            continue

        item = ET.SubElement(channel, 'item')
        _sub(item, 'id', str(product.id), ns=True)
        _sub(item, 'title', product.title[:_MAX_TITEL])
        beschrijving = _beschrijving(product)
        if beschrijving:
            _sub(item, 'description', beschrijving)
        _sub(item, 'link',
             f"{site}/product/{quote(product.slug, safe='-._~')}")
        # Via ons EIGEN domein (plan B, 13 aug): de route /fotos/feed/…
        # hieronder geeft de foto door. Zo draait Googles crawl-controle
        # uitsluitend op ónze robots.txt — niet op die van wsrv of van de
        # fotoserver van een winkel, waar wij niets over te zeggen hebben.
        _sub(item, 'image_link', f'{site}/fotos/feed/{product.id}.webp', ns=True)
        _sub(item, 'price', f'{prijs:.2f} EUR', ns=True)
        _sub(item, 'availability', 'in_stock', ns=True)
        _sub(item, 'condition', 'new', ns=True)
        _sub(item, 'gtin', ean, ns=True)
        # merknaam() geeft dezelfde nette schrijfwijze als de paginatitels
        # ("LG", niet "Lg"); valt terug op het kale merkveld.
        merk = merknaam(product) or product.brand
        if merk:
            _sub(item, 'brand', merk, ns=True)
        if product.id in klassen:
            _sub(item, 'energy_efficiency_class', klassen[product.id], ns=True)
        aantal += 1

    xml = ET.tostring(rss, encoding='unicode', xml_declaration=True)
    resp = Response(xml, mimetype='application/xml')
    # Voor de dagelijkse controle: aantal zonder de feed te hoeven parsen.
    resp.headers['X-Aantal-Producten'] = str(aantal)
    return resp


@merchant_bp.route('/fotos/feed/<int:product_id>.webp')
def feed_foto(product_id):
    """De feedfoto, geserveerd vanaf ons eigen domein.

    Waarom (plan B na 12-13 aug): Merchant Center keurde eerst 725
    producten af omdat de fotoserver van Coolblue alle crawlers weert, en
    de wsrv-route bleef ter beoordeling. Met deze route staat het
    foto-adres op ons eigen domein, waar onze eigen robots.txt Googlebot
    en Googlebot-Image uitdrukkelijk toelaat. De route haalt de foto
    server-side bij wsrv (die haalt hem bij de winkel) en geeft de bytes
    door; een dag cachen zodat herhaalde crawls ons niet belasten.

    /fotos/ staat bewust NIET in robots._UITGESLOTEN.
    """
    product = Product.query.get_or_404(product_id)
    if not product.image_url:
        abort(404)
    try:
        # Met een herkenbare afzender: wsrv weigert de kale standaard-
        # useragent van requests (403, gemeten 13 aug), maar laat een
        # nette zelfbenoemde proxy gewoon door.
        antwoord = requests.get(
            foto_url(product.image_url, 800), timeout=25,
            headers={'User-Agent':
                     'WitgoedAanbod-fotoproxy/1.0 (+https://www.witgoedaanbod.nl)'})
    except requests.RequestException:
        abort(404)
    if antwoord.status_code != 200:
        abort(404)
    resp = Response(antwoord.content,
                    mimetype=antwoord.headers.get('Content-Type', 'image/webp'))
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp
