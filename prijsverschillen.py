"""
Prijsverschillen tussen winkels: de cijfers achter /onderzoek/prijsverschillen-witgoed.

Waarom (17 september 2026): een jong domein komt organisch niet van pagina 2
af zonder links van andere sites. Wat wij hebben en blogs, journalisten en
woonsites niet: de prijzen van zeven winkels over ruim duizend apparaten,
dag na dag. Deze module maakt daar één publicatie van die maandelijks
vanzelf bijblijft: hoeveel scheelt hetzelfde apparaat tussen winkels, in
welke categorie het meest, welke winkel het vaakst de goedkoopste is en
hoe vaak prijzen wisselen. Alles uit de database, niets geschat; wat de
data niet draagt (bv. "duurder dan vorig jaar" -- historie sinds 14 juli
2026) staat er niet.

Gemeten op 17 september 2026 als nulmeting: 1.126 apparaten met >=2
winkels, gemiddeld EUR 51 (10,3%) verschil, 371 met >=EUR 50, 193 met
>=EUR 100; Coolblue vaakst goedkoopste (470), dan MediaMarkt (397).
"""

import time
from datetime import timedelta

from sqlalchemy import text

from models import db, Product, Category, utcnow, retailer_label, RETAILER_LABELS

_CACHE = {}
_TTL = 6 * 60 * 60  # de cijfers veranderen alleen bij een sync; zes uur is ruim

TOP_N = 10
WISSEL_DAGEN = 30
MAX_PCT = 0.60  # groter verschil = waarschijnlijk andere uitvoering of feedfout


def _rond(x, n=0):
    return round(float(x), n) if x is not None else 0


def cijfers():
    """Alle cijfers voor de pagina, als één dict. Gecachet."""
    nu = time.time()
    hit = _CACHE.get('data')
    if hit and nu - hit[0] < _TTL:
        return hit[1]

    # Per apparaat: laagste en hoogste leverbare prijs, bij hoeveel winkels.
    # Setjes (wasmachine + droger) blijven buiten beschouwing: bij een set
    # levert de ene winkel soms alleen het hoofdapparaat onder dezelfde code.
    # Verschillen boven MAX_PCT laten we ook weg: dat is vaker een andere
    # uitvoering of een feedfout dan een echt prijsverschil, en één zo'n
    # regel zou het gemiddelde en de toplijst scheeftrekken.
    per_product = db.session.execute(text("""
        select o.product_id, min(o.price) as mn, max(o.price) as mx, count(*) as n,
               (array_agg(o.retailer order by o.price asc))[1]  as goedkoopste,
               (array_agg(o.retailer order by o.price desc))[1] as duurste
        from offers o
        join products p on p.id = o.product_id
        join categories c on c.id = p.category_id
        where o.is_available and o.price > 0 and p.is_available
          and c.name <> 'Apparaatsets'
        group by o.product_id
        having count(*) >= 2
    """)).fetchall()
    per_product = [r for r in per_product
                   if (float(r.mx) - float(r.mn)) / float(r.mn) <= MAX_PCT]

    if not per_product:
        data = {'apparaten': 0}
        _CACHE['data'] = (nu, data)
        return data

    ids = [r.product_id for r in per_product]
    producten = {p.id: p for p in Product.query.filter(Product.id.in_(ids)).all()}
    categorieen = {c.id: c for c in Category.query.all()}

    verschillen = [(float(r.mx) - float(r.mn)) for r in per_product]
    pcts = [(float(r.mx) - float(r.mn)) / float(r.mn) for r in per_product]
    gesorteerd = sorted(verschillen)
    mediaan = gesorteerd[len(gesorteerd) // 2]

    totaal = {
        'apparaten': len(per_product),
        'gem_eur': _rond(sum(verschillen) / len(verschillen)),
        'gem_pct': _rond(100 * sum(pcts) / len(pcts), 1),
        'mediaan_eur': _rond(mediaan),
        'gelijk': sum(1 for v in verschillen if v < 0.01),
        'vanaf_50': sum(1 for v in verschillen if v >= 50),
        'vanaf_100': sum(1 for v in verschillen if v >= 100),
        'vanaf_200': sum(1 for v in verschillen if v >= 200),
        'som_eur': _rond(sum(verschillen)),
    }

    # Per categorie.
    per_cat = {}
    for r, v, pct in zip(per_product, verschillen, pcts):
        p = producten.get(r.product_id)
        if not p:
            continue
        c = per_cat.setdefault(p.category_id, {'n': 0, 'som': 0.0, 'som_pct': 0.0,
                                                 'vanaf_50': 0, 'max': None})
        c['n'] += 1
        c['som'] += v
        c['som_pct'] += pct
        c['vanaf_50'] += 1 if v >= 50 else 0
        if c['max'] is None or v > c['max'][0]:
            c['max'] = (v, r)
    categorie_rijen = []
    for cid, c in per_cat.items():
        cat = categorieen.get(cid)
        if not cat or c['n'] < 10:
            continue
        v, r = c['max']
        p = producten[r.product_id]
        categorie_rijen.append({
            'categorie': cat,
            'apparaten': c['n'],
            'gem_eur': _rond(c['som'] / c['n']),
            'gem_pct': _rond(100 * c['som_pct'] / c['n'], 1),
            'vanaf_50': c['vanaf_50'],
            'max_eur': _rond(v),
            'max_product': p,
            'max_goedkoopste': retailer_label(r.goedkoopste),
            'max_duurste': retailer_label(r.duurste),
            'max_mn': float(r.mn),
            'max_mx': float(r.mx),
        })
    categorie_rijen.sort(key=lambda x: -x['gem_eur'])

    # Grootste verschillen (top N), alleen apparaten met een productpagina.
    top = []
    for r, v in sorted(zip(per_product, verschillen), key=lambda x: -x[1]):
        p = producten.get(r.product_id)
        if not p:
            continue
        top.append({
            'product': p,
            'categorie': categorieen.get(p.category_id),
            'mn': float(r.mn), 'mx': float(r.mx), 'verschil': _rond(v),
            'pct': _rond(100 * v / float(r.mn)),
            'goedkoopste': retailer_label(r.goedkoopste),
            'duurste': retailer_label(r.duurste),
            'winkels': int(r.n),
        })
        if len(top) >= TOP_N:
            break

    # Welke winkel is het vaakst de goedkoopste, en hoe vaak doet hij mee.
    aanwezig = db.session.execute(text("""
        select o.retailer, count(*) as n
        from offers o
        join products p on p.id = o.product_id
        where o.is_available and o.price > 0 and p.is_available
          and o.product_id in (
              select product_id from offers where is_available and price > 0
              group by product_id having count(*) >= 2)
        group by o.retailer
    """)).fetchall()
    aanwezig = {r.retailer: int(r.n) for r in aanwezig}
    goedkoopste_teller = {}
    for r in per_product:
        goedkoopste_teller[r.goedkoopste] = goedkoopste_teller.get(r.goedkoopste, 0) + 1
    winkels = []
    for code in RETAILER_LABELS:
        n_aanwezig = aanwezig.get(code, 0)
        if n_aanwezig < 20:
            continue
        n_goedkoopste = goedkoopste_teller.get(code, 0)
        winkels.append({
            'winkel': retailer_label(code),
            'aanwezig': n_aanwezig,
            'goedkoopste': n_goedkoopste,
            'aandeel_pct': _rond(100 * n_goedkoopste / n_aanwezig, 1),
        })
    winkels.sort(key=lambda w: -w['aandeel_pct'])

    # Hoe vaak wisselen prijzen: wijzigingen per winkel in de laatste 30 dagen,
    # afgezet tegen het aantal aanbiedingen van die winkel.
    grens = utcnow() - timedelta(days=WISSEL_DAGEN)
    # Alleen aanbiedingen die nu nog leverbaar zijn, anders tellen verdwenen
    # producten mee en kom je boven de 100% uit.
    wissel = db.session.execute(text("""
        select h.retailer, count(*) as wijzigingen, count(distinct h.product_id) as apparaten
        from price_history h
        join offers o on o.product_id = h.product_id and o.retailer = h.retailer
        where h.recorded_at >= :grens and o.is_available and o.price > 0
        group by h.retailer
    """), {'grens': grens}).fetchall()
    aanbiedingen = db.session.execute(text("""
        select retailer, count(*) as n from offers where is_available and price > 0 group by retailer
    """)).fetchall()
    aanbiedingen = {r.retailer: int(r.n) for r in aanbiedingen}
    wisselingen = []
    for r in wissel:
        n_aanb = aanbiedingen.get(r.retailer, 0)
        if n_aanb < 20:
            continue
        wisselingen.append({
            'winkel': retailer_label(r.retailer),
            'aanbiedingen': n_aanb,
            'wijzigingen': int(r.wijzigingen),
            'apparaten_gewijzigd': int(r.apparaten),
            'aandeel_gewijzigd_pct': _rond(100 * int(r.apparaten) / n_aanb, 1),
            'per_aanbieding': _rond(int(r.wijzigingen) / n_aanb, 1),
        })
    wisselingen.sort(key=lambda w: -w['per_aanbieding'])

    eerste = db.session.execute(text("select min(recorded_at) from price_history")).scalar()

    data = {
        'totaal': totaal,
        'categorieen': categorie_rijen,
        'top': top,
        'winkels': winkels,
        'wisselingen': wisselingen,
        'wissel_dagen': WISSEL_DAGEN,
        'historie_sinds': eerste,
        'stand': utcnow(),
        'aantal_winkels': len(RETAILER_LABELS),
    }
    _CACHE['data'] = (nu, data)
    return data
