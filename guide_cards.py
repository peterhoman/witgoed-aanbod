"""Productkaarten in koopgidsen: visuele toplijst met live prijzen.

Gidsteksten (guides.content) kunnen placeholders bevatten die bij het
renderen worden vervangen door een kaart met productfoto, ranglabel,
actuele laagste prijs en een knop naar de productpagina — vergelijkbaar
met de toplijsten van affiliate-reviewsites, maar dan met prijzen die
live uit de database komen in plaats van hardgecodeerd.

Twee varianten:

  <!--productkaart ean=4242005522118 rank=1 label="De beste" pros="Energielabel B|Stilste: 59 dB" cons="Duurste van de lijst"-->
      Kaart op basis van een apparaat in de database (EAN). Toont foto,
      titel, laagste prijs + aantal winkels en een knop naar de
      productpagina. Is het apparaat (tijdelijk) niet leverbaar, dan
      wordt de kaart stilletjes overgeslagen: liever geen kaart dan een
      dode knop. Optionele pros/cons (gescheiden met |) verschijnen als
      plus- en minpunten op de kaart en worden verzameld tot Pros & Cons
      structured data (Google's rich result voor redactionele reviews) —
      zichtbare tekst en schema blijven zo automatisch synchroon.

  <!--merkkaart merk=Samsung categorie=drogers naam="Samsung 5000-serie" rank=3 label="Middenklasser"-->
      Kaart zonder specifiek apparaat; de knop wijst naar het merkfilter
      in de categorie. Voor modellen uit een video die (nog) niet exact
      op de site staan.
"""
import json
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


def _kaart_html(rank, label, titel, url, foto, prijsregel, knoptekst,
                pros=(), cons=()):
    foto_html = (f'<img src="{escape(foto, quote=True)}" alt="{escape(titel, quote=True)}" '
                 f'loading="lazy" class="top-card-img">' if foto else '')
    notes = ''
    if pros or cons:
        items = ''.join(f'<span class="note-pro">&#10003; {escape(p)}</span>' for p in pros)
        items += ''.join(f'<span class="note-con">&minus; {escape(c)}</span>' for c in cons)
        notes = f'<div class="top-card-notes">{items}</div>'
    return (
        f'<div class="top-card">'
        f'<span class="top-card-rank">{rank}</span>'
        f'{foto_html}'
        f'<div class="top-card-info">'
        f'<span class="top-card-label">{escape(label)}</span>'
        f'<strong class="top-card-title">{escape(titel)}</strong>'
        f'{prijsregel}'
        f'{notes}'
        f'</div>'
        f'<a href="{escape(url, quote=True)}" class="btn-primary top-card-btn">{escape(knoptekst)} &rarr;</a>'
        f'</div>'
    )


def _split_notes(waarde):
    return tuple(s.strip() for s in (waarde or '').split('|') if s.strip())


def _render_productkaart(match, verzameld=None):
    a = _attrs(match.group(1))
    product = Product.query.filter_by(ean=a.get('ean', ''), is_available=True).first()
    if product is None:
        return ''  # niet (meer) leverbaar: kaart weglaten in plaats van dode knop
    prijs = product.lowest_price
    winkels = product.retailer_count
    pros, cons = _split_notes(a.get('pros')), _split_notes(a.get('cons'))
    if verzameld is not None and (pros or cons):
        verzameld.append({'titel': product.title,
                          'url': f'/product/{product.slug}',
                          'pros': pros, 'cons': cons})
    prijsregel = (f'<span class="top-card-price">Laagste prijs: '
                  f'<strong>&euro; {_euro(prijs)}</strong>'
                  + (f' <small>bij {winkels} winkels</small>' if winkels > 1 else '')
                  + '</span>')
    return _kaart_html(a.get('rank', ''), a.get('label', ''), product.title,
                       f'/product/{product.slug}', product.image_url,
                       prijsregel, 'Bekijk alle prijzen', pros, cons)


def _render_merkkaart(match):
    a = _attrs(match.group(1))
    merk, categorie = a.get('merk', ''), a.get('categorie', '')
    url = f'/category/{categorie}?brand={merk}'
    # Representatieve productfoto van hetzelfde merk in dezelfde categorie,
    # zodat de kaart niet kaal is naast de kaarten mét product.
    foto = None
    voorbeeld = (Product.query
                 .join(Product.category)
                 .filter(Product.brand.ilike(merk),
                         Product.is_available.is_(True),
                         Product.image_url.isnot(None))
                 .filter_by(slug=categorie)
                 .first())
    if voorbeeld:
        foto = voorbeeld.image_url
    prijsregel = ('<span class="top-card-price">Actuele prijzen in de vergelijker</span>')
    return _kaart_html(a.get('rank', ''), a.get('label', ''), a.get('naam', merk),
                       url, foto, prijsregel, f'Bekijk {merk}-aanbod')


def _notes_itemlist(notes):
    return {'@type': 'ItemList',
            'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': n}
                                for i, n in enumerate(notes, 1)]}


def _pros_cons_schema(verzameld):
    """ItemList van Products met review + positive/negativeNotes.

    Google's Pros & Cons-rich-result geldt alleen voor redactionele
    reviewpagina's (zoals onze gidsen); de teksten komen uit dezelfde
    kaart-attributen die zichtbaar op de pagina staan.
    """
    items = []
    for i, p in enumerate(verzameld, 1):
        review = {'@type': 'Review',
                  'author': {'@type': 'Organization', 'name': 'WitgoedAanbod.nl'}}
        if p['pros']:
            review['positiveNotes'] = _notes_itemlist(p['pros'])
        if p['cons']:
            review['negativeNotes'] = _notes_itemlist(p['cons'])
        items.append({'@type': 'ListItem', 'position': i,
                      'item': {'@type': 'Product', 'name': p['titel'],
                               'url': p['url'], 'review': review}})
    data = {'@context': 'https://schema.org', '@type': 'ItemList',
            'itemListElement': items}
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False) + '</script>')


def collect_pros_cons_by_ean(guides):
    """Verzamel alle pros/cons-attributen uit <!--productkaart-->-comments
    over de gegeven gidsen heen, in een {ean: {'pros': [...], 'cons': [...],
    'guide_slug': ...}}-dict.

    Hergebruikt de redactionele pros/cons die al in de 5 videogidsen staan
    (guides_content.py), zodat categoriepagina's diezelfde tekst kunnen
    tonen zonder iets te verzinnen voor de duizenden producten die geen
    eigen redactionele beoordeling hebben — die tonen simpelweg niets.
    """
    resultaat = {}
    for guide in guides:
        for match in _PRODUCTKAART.finditer(guide.content or ''):
            a = _attrs(match.group(1))
            ean = (a.get('ean') or '').strip()
            pros, cons = _split_notes(a.get('pros')), _split_notes(a.get('cons'))
            if not ean or not (pros or cons):
                continue
            # Eerste vermelding wint: een product staat zelden in meerdere
            # gidsen, maar bij twijfel is de oudste (eerst geschreven) tekst
            # net zo goed als een willekeurige latere.
            if ean not in resultaat:
                resultaat[ean] = {'pros': pros, 'cons': cons, 'guide_slug': guide.slug}
    return resultaat


def render_guide_content(content):
    """Vervang kaart-placeholders in gidstekst door gerenderde kaarten."""
    if '<!--productkaart' not in content and '<!--merkkaart' not in content:
        return content
    verzameld = []
    content = _PRODUCTKAART.sub(lambda m: _render_productkaart(m, verzameld), content)
    content = _MERKKAART.sub(_render_merkkaart, content)
    if verzameld:
        content += _pros_cons_schema(verzameld)
    return content
