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
- g:image_link is de originele winkelfoto, niet de wsrv-verkleining:
  dezelfde URL die in de gestructureerde data staat, zodat Google een
  foto ziet die hij al kent.
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

from flask import Blueprint, Response, current_app

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
        if not ean or not prijs or prijs <= 0 or product.is_example:
            continue

        item = ET.SubElement(channel, 'item')
        _sub(item, 'id', str(product.id), ns=True)
        _sub(item, 'title', product.title[:_MAX_TITEL])
        beschrijving = _beschrijving(product)
        if beschrijving:
            _sub(item, 'description', beschrijving)
        _sub(item, 'link',
             f"{site}/product/{quote(product.slug, safe='-._~')}")
        _sub(item, 'image_link', product.image_url, ns=True)
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
