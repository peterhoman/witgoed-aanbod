"""Productkaarten in koopgidsen: visuele toplijst met live prijzen.

Gidsteksten (guides.content) kunnen placeholders bevatten die bij het
renderen worden vervangen door een kaart met productfoto, ranglabel,
actuele laagste prijs en een knop naar de productpagina — vergelijkbaar
met de toplijsten van affiliate-reviewsites, maar dan met prijzen die
live uit de database komen in plaats van hardgecodeerd.

Twee varianten:

  <!--productkaart ean=4242005522118 rank=1 label="De beste"-->
      Kaart op basis van een apparaat in de database (EAN). Toont foto,
      titel, laagste prijs + aantal winkels en een knop naar de
      productpagina. Is het apparaat (tijdelijk) niet leverbaar, dan
      wordt de kaart stilletjes overgeslagen: liever geen kaart dan een
      dode knop.

  <!--merkkaart merk=Samsung categorie=drogers naam="Samsung 5000-serie" rank=3 label="Middenklasser"-->
      Kaart zonder specifiek apparaat; de knop wijst naar het merkfilter
      in de categorie. Voor modellen uit een video die (nog) niet exact
      op de site staan.
"""
import re
from html import escape

from models import Product

_PRODUCTKAART = re.compile(r'<!--productkaart\s+([^>]*?)-->')
_MERKKAART = re.compile(r'<!--merkkaart\s+([^>]*?)-->')
_ATTR = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')


def _attrs(tekst):
    return {m.group(1): (m.group(2) if m.group(2) is not None else m.group(3))
            for m in _ATTR.finditer(tekst)}


def _euro(bedrag):
    s = f"{bedrag:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return s[:-3] if s.endswith(',00') else s


def _kaart_html(rank, label, titel, url, foto, prijsregel, knoptekst):
    foto_html = (f'<img src="{escape(foto, quote=True)}" alt="{escape(titel, quote=True)}" '
                 f'loading="lazy" class="top-card-img">' if foto else '')
    return (
        f'<div class="top-card">'
        f'<span class="top-card-rank">{rank}</span>'
        f'{foto_html}'
        f'<div class="top-card-info">'
        f'<span class="top-card-label">{escape(label)}</span>'
        f'<strong class="top-card-title">{escape(titel)}</strong>'
        f'{prijsregel}'
        f'</div>'
        f'<a href="{escape(url, quote=True)}" class="btn-primary top-card-btn">{escape(knoptekst)} &rarr;</a>'
        f'</div>'
    )


def _render_productkaart(match):
    a = _attrs(match.group(1))
    product = Product.query.filter_by(ean=a.get('ean', ''), is_available=True).first()
    if product is None:
        return ''  # niet (meer) leverbaar: kaart weglaten in plaats van dode knop
    prijs = product.lowest_price
    winkels = product.retailer_count
    prijsregel = (f'<span class="top-card-price">Laagste prijs: '
                  f'<strong>&euro; {_euro(prijs)}</strong>'
                  + (f' <small>bij {winkels} winkels</small>' if winkels > 1 else '')
                  + '</span>')
    return _kaart_html(a.get('rank', ''), a.get('label', ''), product.title,
                       f'/product/{product.slug}', product.image_url,
                       prijsregel, 'Bekijk alle prijzen')


def _render_merkkaart(match):
    a = _attrs(match.group(1))
    merk, categorie = a.get('merk', ''), a.get('categorie', '')
    url = f'/category/{categorie}?brand={merk}'
    prijsregel = ('<span class="top-card-price">Actuele prijzen in de vergelijker</span>')
    return _kaart_html(a.get('rank', ''), a.get('label', ''), a.get('naam', merk),
                       url, None, prijsregel, f'Bekijk {merk}-aanbod')


def render_guide_content(content):
    """Vervang kaart-placeholders in gidstekst door gerenderde kaarten."""
    if '<!--productkaart' not in content and '<!--merkkaart' not in content:
        return content
    content = _PRODUCTKAART.sub(_render_productkaart, content)
    content = _MERKKAART.sub(_render_merkkaart, content)
    return content
