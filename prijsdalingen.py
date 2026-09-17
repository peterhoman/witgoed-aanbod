"""
Echte prijsdalingen van de afgelopen week, per categorie.

Waarom (17 september 2026): Google Trends laat zien dat mensen niet op
"goedkope wasmachine" of "witgoed prijsvergelijker" zoeken, maar op
"wasmachine aanbieding" en "droger aanbieding". Een winkel noemt alles een
aanbieding; wij kunnen uit onze eigen prijshistorie (price_history, sinds
14 juli 2026, zeven winkels, dag na dag) bewijzen welke prijzen écht
gedaald zijn. Gemeten op productie op 17 september: per week 170-360
dalingen van minstens 10% én 30 euro, waarvan ruim de helft een week later
nog geldt. Genoeg om per categorie elke week een pagina te vullen.

Spelregels (bewust streng, anders is het een lijst met ruis):
- minstens DREMPEL_PCT én DREMPEL_EUR lager dan de vorige prijs van
  dezelfde winkel;
- de verlaagde prijs geldt nú nog (huidige aanbieding = die prijs, en
  leverbaar): een prijs die alweer terugsprong telt niet;
- de daling is van de afgelopen VENSTER_DAGEN dagen;
- per apparaat één regel (de grootste daling);
- een categorie krijgt pas een pagina bij MIN_PER_PAGINA apparaten; route,
  categorielinks en sitemap gebruiken allemaal deze module, zodat ze het
  nooit oneens zijn.

Geen "duurder/goedkoper dan vorig jaar": de historie is daar te kort voor.
"""

import time
from datetime import timedelta

from sqlalchemy import text

from models import db, Product, Offer, Category, utcnow, retailer_label

DREMPEL_PCT = 0.10
DREMPEL_EUR = 30.0
VENSTER_DAGEN = 7
MIN_PER_PAGINA = 5

# Procescache per categorie: de prijzen veranderen alleen bij een sync, en
# gunicorn draait met één worker (zie routes/main.py voor hetzelfde patroon).
_CACHE = {}
_TTL = 15 * 60


def _leeg_cache():
    _CACHE.clear()


def _ruwe_dalingen():
    """Alle prijsverlagingen in het venster: (product_id, winkel, van, naar, wanneer).

    Eén query over price_history met een window-functie: per apparaat en
    winkel de vorige regel, en alleen de regels waar de prijs daalde.
    """
    grens = utcnow() - timedelta(days=VENSTER_DAGEN)
    q = text("""
        with h as (
            select product_id, retailer, price, recorded_at,
                   lag(price) over (partition by product_id, retailer
                                    order by recorded_at) as vorige
            from price_history
        )
        select product_id, retailer, vorige, price, recorded_at
        from h
        where vorige is not null
          and price < vorige
          and recorded_at >= :grens
          and (vorige - price) >= :min_eur
          and (vorige - price) / vorige >= :min_pct
    """)
    return db.session.execute(q, {'grens': grens, 'min_eur': DREMPEL_EUR,
                                  'min_pct': DREMPEL_PCT}).fetchall()


def _alle_dalingen():
    """{category_id: [daling, ...]} voor de hele site, gesorteerd op procent.

    Een daling is een dict met product, winkel(code), winkel_naam, van, naar,
    verschil, pct, wanneer, goedkoopste (bool: is deze winkel nu de
    goedkoopste voor dit apparaat).
    """
    nu = time.time()
    hit = _CACHE.get('alles')
    if hit and nu - hit[0] < _TTL:
        return hit[1]

    ruw = _ruwe_dalingen()
    if not ruw:
        _CACHE['alles'] = (nu, {})
        return {}

    product_ids = {r.product_id for r in ruw}
    offers = (Offer.query.filter(Offer.product_id.in_(product_ids),
                                 Offer.is_available == True, Offer.price > 0)
              .all())
    per_product_offer = {}
    laagste = {}
    for o in offers:
        per_product_offer[(o.product_id, o.retailer)] = o
        if o.product_id not in laagste or o.price < laagste[o.product_id]:
            laagste[o.product_id] = o.price

    producten = {p.id: p for p in Product.query.filter(
        Product.id.in_(product_ids), Product.is_available == True).all()}

    beste_per_product = {}
    for r in ruw:
        p = producten.get(r.product_id)
        o = per_product_offer.get((r.product_id, r.retailer))
        # De verlaagde prijs moet nu nog gelden bij die winkel.
        if not p or not o or abs(o.price - r.price) > 0.01:
            continue
        verschil = float(r.vorige) - float(r.price)
        pct = verschil / float(r.vorige)
        kandidaat = {
            'product': p,
            'winkel': r.retailer,
            'winkel_naam': retailer_label(r.retailer),
            'van': float(r.vorige),
            'naar': float(r.price),
            'verschil': verschil,
            'pct': pct,
            'pct_rond': int(round(pct * 100)),
            'wanneer': r.recorded_at,
            'goedkoopste': abs(laagste.get(r.product_id, o.price) - o.price) < 0.01,
        }
        # Per apparaat één regel: de grootste daling in procenten.
        vorige = beste_per_product.get(r.product_id)
        if not vorige or kandidaat['pct'] > vorige['pct']:
            beste_per_product[r.product_id] = kandidaat

    per_categorie = {}
    for d in beste_per_product.values():
        per_categorie.setdefault(d['product'].category_id, []).append(d)
    for lijst in per_categorie.values():
        lijst.sort(key=lambda d: (-d['pct'], -d['verschil']))

    _CACHE['alles'] = (nu, per_categorie)
    return per_categorie


def dalingen_voor(category):
    """Lijst dalingen voor één categorie (kan leeg zijn)."""
    return _alle_dalingen().get(category.id, [])


def heeft_pagina(category):
    """Krijgt deze categorie een prijsdalingenpagina (route, links, sitemap)?"""
    return len(dalingen_voor(category)) >= MIN_PER_PAGINA


def overzicht():
    """[(category, aantal, grootste daling)] voor alle categorieën met een pagina."""
    alles = _alle_dalingen()
    uit = []
    for c in Category.query.order_by(Category.name).all():
        lijst = alles.get(c.id, [])
        if len(lijst) >= MIN_PER_PAGINA:
            uit.append((c, len(lijst), lijst[0]))
    uit.sort(key=lambda x: -x[1])
    return uit


def nieuwste_moment(lijst):
    """Laatste dalingsmoment in een lijst, voor de sitemap-lastmod."""
    return max((d['wanneer'] for d in lijst), default=None)
