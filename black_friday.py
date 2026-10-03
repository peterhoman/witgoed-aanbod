"""
Black Friday-prijsonderzoek: de cijfers achter /api/black-friday. Leest alleen.

Waarom (3 oktober 2026, Peters ja): de specialist-chat wil in de week van
2-6 november /onderzoek/black-friday-witgoed-2026 publiceren, met een
tweede meting 16-20 november en een dagmeting op 27 november. De vraag is
of Black Friday-prijzen echt lager zijn dan in de maanden ervoor. Dat kan
alleen met eigen prijshistorie, en die hebben wij (price_history, sinds
14 juli 2026). Deze pagina levert de ruwe cijfers zodat die chat ze zelf
kan opvragen; de tekst komt later en beweert alleen wat hier staat.

Vier keuzes die de uitkomst bepalen, en waarom:

1. VASTE MAND. Een reeks (apparaat x winkel) telt alleen mee als hij al
   een prijs had op de startdatum EN de winkel het apparaat nu nog levert
   (aanbieding leverbaar en de afgelopen drie dagen ververst). Zonder die
   regel meet je assortimentswisseling: komt er in november een goedkoop
   model bij, dan lijkt de categorie goedkoper terwijl geen enkele prijs
   daalde. Beperking: price_history bewaart alleen prijzen, geen
   leverbaarheid; een apparaat dat tussendoor een week uitverkocht was,
   zit er dus wel in.
2. Prijs van een apparaat op een moment = de laagste prijs over de winkels
   in de mand op dat moment. price_history krijgt alleen een rij bij een
   wijziging, dus de prijs op moment t is de laatste rij op of vóór t.
3. Index = meetkundig gemiddelde van de prijsverhoudingen (Jevons), x100.
   Dat is de gangbare manier voor een prijsindex zonder verkoopaantallen,
   en één dure oven telt niet zwaarder dan een goedkope magnetron.
4. EP en Alternate staan niet in de vergelijking per winkel: EP levert
   sinds augustus maar een deel van de feed, Alternate heeft ~20
   apparaten. Ze tellen wel mee in de laagste prijs per apparaat (dat is
   de prijs die een bezoeker bij ons ziet).

Setjes (categorie Apparaatsets) blijven buiten beschouwing, zoals in
prijsverschillen.py.
"""

import math
import time
from datetime import datetime, timedelta

_CACHE = {}
_TTL = 60 * 60  # prijzen veranderen alleen bij een sync

START = datetime(2026, 7, 16)        # eerste volledige dag met historie
BF_WEEK = datetime(2026, 11, 23)     # maandag; Black Friday is vrijdag 27 nov
BF_DAGEN = 8                         # t/m Cyber Monday 30 nov
OMNIBUS_DAGEN = 90
PEILDATA = (datetime(2026, 9, 1), datetime(2026, 10, 1), datetime(2026, 11, 1))
NIET_PER_WINKEL = ('ep', 'alternate')
VERS_DAGEN = 3
MIN_MAND = 10  # kleinere categorieën staan erbij, maar met een waarschuwing
GELIJK = 0.005  # binnen een halve procent = dezelfde prijs (afronding)


# ---------------------------------------------------------------------------
# Rekenen op reeksen. Een reeks is een lijst (tijdstip, prijs), oplopend.
# Deze functies kennen geen database en zijn los te testen.
# ---------------------------------------------------------------------------

def prijs_op(reeks, t):
    """De geldende prijs op moment t: de laatste rij op of vóór t."""
    geldend = None
    for moment, prijs in reeks:
        if moment > t:
            break
        geldend = prijs
    return geldend


def laagste_tussen(reeks, van, tot):
    """Laagste prijs die ergens in [van, tot] gold, of None."""
    kandidaten = []
    begin = prijs_op(reeks, van)
    if begin is not None:
        kandidaten.append(begin)
    kandidaten += [p for m, p in reeks if van < m <= tot]
    return min(kandidaten) if kandidaten else None


def apparaatprijs_op(reeksen, t):
    """Laagste prijs over de winkels van één apparaat op moment t."""
    prijzen = [p for p in (prijs_op(r, t) for r in reeksen) if p]
    return min(prijzen) if prijzen else None


def apparaat_laagste_tussen(reeksen, van, tot):
    prijzen = [p for p in (laagste_tussen(r, van, tot) for r in reeksen) if p]
    return min(prijzen) if prijzen else None


def jevons(paren):
    """Index (basis 100) uit (basisprijs, prijs nu)-paren."""
    logs = [math.log(nu / basis) for basis, nu in paren if basis and nu]
    if not logs:
        return None
    return round(100 * math.exp(sum(logs) / len(logs)), 1)


def mediaan(waarden):
    w = sorted(waarden)
    if not w:
        return None
    m = len(w) // 2
    return w[m] if len(w) % 2 else (w[m - 1] + w[m]) / 2


def peilmomenten(start, nu):
    """Start, de eerste van elke maand daarna, en nu."""
    momenten = [start]
    jaar, maand = start.year, start.month
    while True:
        maand += 1
        if maand > 12:
            jaar, maand = jaar + 1, 1
        moment = datetime(jaar, maand, 1)
        if moment >= nu:
            break
        momenten.append(moment)
    momenten.append(nu)
    return momenten


def _pct(a, b):
    """Hoeveel procent ligt a boven b."""
    return round(100 * (a - b) / b, 1)


# ---------------------------------------------------------------------------
# De vier onderdelen. Invoer: mand = {product_id: {winkel: reeks}} (alleen
# reeksen die in de vaste mand zitten) en info = {product_id: (categorie,
# titel, ean)}.
# ---------------------------------------------------------------------------

def index_per_categorie(mand, info, momenten):
    per_cat = {}
    for pid, reeksen in mand.items():
        per_cat.setdefault(info[pid][0], []).append(list(reeksen.values()))
    uit = []
    for cat, apparaten in sorted(per_cat.items()):
        basis = [apparaatprijs_op(r, momenten[0]) for r in apparaten]
        rij = {'categorie': cat, 'apparaten': len(apparaten), 'index': {}}
        if len(apparaten) < MIN_MAND:
            rij['let_op'] = f'minder dan {MIN_MAND} apparaten: niet publiceren'
        for t in momenten:
            nu = [apparaatprijs_op(r, t) for r in apparaten]
            rij['index'][t.strftime('%Y-%m-%d')] = jevons(zip(basis, nu))
        uit.append(rij)
    return uit


def index_totaal(mand, momenten):
    apparaten = [list(r.values()) for r in mand.values()]
    basis = [apparaatprijs_op(r, momenten[0]) for r in apparaten]
    return {t.strftime('%Y-%m-%d'): jevons(zip(basis, [apparaatprijs_op(r, t) for r in apparaten]))
            for t in momenten}


def index_per_winkel(mand, momenten):
    per_winkel = {}
    for reeksen in mand.values():
        for winkel, reeks in reeksen.items():
            if winkel not in NIET_PER_WINKEL:
                per_winkel.setdefault(winkel, []).append(reeks)
    uit = []
    for winkel, reeksen in sorted(per_winkel.items()):
        basis = [prijs_op(r, momenten[0]) for r in reeksen]
        rij = {'winkel': winkel, 'reeksen': len(reeksen), 'index': {}}
        for t in momenten:
            rij['index'][t.strftime('%Y-%m-%d')] = jevons(zip(basis, [prijs_op(r, t) for r in reeksen]))
        uit.append(rij)
    return uit


def omnibus(mand, info, peildatum, eerste_data, details=0):
    """Prijs op de peildatum tegenover de laagste prijs in de 90 dagen ervoor.

    Dezelfde vergelijking die de Omnibus-richtlijn winkels oplegt bij een
    kortingsclaim. Begint de historie later dan 90 dagen terug, dan is het
    venster korter en staat dat er eerlijk bij.
    """
    van = max(peildatum - timedelta(days=OMNIBUS_DAGEN), eerste_data)
    rijen = []
    for pid, reeksen in mand.items():
        r = list(reeksen.values())
        op = apparaatprijs_op(r, peildatum)
        laagste = apparaat_laagste_tussen(r, van, peildatum)
        if op and laagste:
            rijen.append((pid, op, laagste, _pct(op, laagste)))
    boven = [x[3] for x in rijen]
    uit = {
        'peildatum': peildatum.strftime('%Y-%m-%d'),
        'venster_vanaf': van.strftime('%Y-%m-%d'),
        'venster_dagen': (peildatum - van).days,
        'apparaten': len(rijen),
        'op_laagste_prijs': sum(1 for b in boven if b <= 100 * GELIJK),
        'meer_dan_5pct_boven_laagste': sum(1 for b in boven if b > 5),
        'meer_dan_10pct_boven_laagste': sum(1 for b in boven if b > 10),
        'gemiddeld_boven_laagste_pct': round(sum(boven) / len(boven), 1) if boven else None,
        'mediaan_boven_laagste_pct': mediaan(boven),
    }
    if details:
        rijen.sort(key=lambda x: -x[3])
        uit['apparaten_lijst'] = [{
            'ean': info[pid][2], 'titel': info[pid][1], 'categorie': info[pid][0],
            'prijs_op_peildatum': op, 'laagste_90_dagen': laagste, 'boven_laagste_pct': b,
        } for pid, op, laagste, b in rijen[:details]]
    return uit


def black_friday_week(mand, info, week_start, eerste_data):
    """Laagste prijs in de Black Friday-week tegenover de 90 dagen ervoor."""
    week_eind = week_start + timedelta(days=BF_DAGEN)
    van = max(week_start - timedelta(days=OMNIBUS_DAGEN), eerste_data)
    lager = gelijk = hoger = 0
    verschillen, per_cat = [], {}
    for pid, reeksen in mand.items():
        r = list(reeksen.values())
        in_week = apparaat_laagste_tussen(r, week_start, week_eind)
        ervoor = apparaat_laagste_tussen(r, van, week_start - timedelta(seconds=1))
        if not in_week or not ervoor:
            continue
        v = _pct(in_week, ervoor)
        verschillen.append(v)
        c = per_cat.setdefault(info[pid][0], {'apparaten': 0, 'echt_lager': 0})
        c['apparaten'] += 1
        if v < -100 * GELIJK:
            lager += 1
            c['echt_lager'] += 1
        elif v > 100 * GELIJK:
            hoger += 1
        else:
            gelijk += 1
    return {
        'week': f"{week_start:%Y-%m-%d} t/m {week_eind - timedelta(days=1):%Y-%m-%d}",
        'vergeleken_met': f"laagste prijs {van:%Y-%m-%d} t/m {week_start - timedelta(days=1):%Y-%m-%d}",
        'apparaten': len(verschillen),
        'echt_lager_dan_ooit_in_90_dagen': lager,
        'gelijk_aan_laagste': gelijk,
        'duurder_dan_laagste': hoger,
        'mediaan_verschil_pct': mediaan(verschillen),
        'per_categorie': dict(sorted(per_cat.items())),
    }


def voorbeelden(mand, info, start, aantal=5):
    """Apparaten met de meeste prijsbeweging, elk uit een andere categorie.

    Voor de voorbeeldgrafieken: de volledige reeks per winkel vanaf de start.
    Alleen apparaten met minstens twee winkels in de mand, anders valt er
    niets te vergelijken.
    """
    kandidaten = []
    for pid, reeksen in mand.items():
        if len(reeksen) < 2:
            continue
        wijzigingen = sum(1 for r in reeksen.values() for m, _ in r if m > start)
        kandidaten.append((wijzigingen, pid))
    kandidaten.sort(reverse=True)
    gekozen, gezien = [], set()
    for wijzigingen, pid in kandidaten:
        cat = info[pid][0]
        if cat in gezien:
            continue
        gezien.add(cat)
        reeksen = mand[pid]
        gekozen.append({
            'ean': info[pid][2], 'titel': info[pid][1], 'categorie': cat,
            'prijswijzigingen': wijzigingen,
            'reeksen': {w: [[m.strftime('%Y-%m-%d %H:%M'), p] for m, p in r
                            if m >= start or m == max(x for x, _ in r if x <= start)]
                        for w, r in sorted(reeksen.items())},
        })
        if len(gekozen) == aantal:
            break
    return gekozen


def maak_mand(reeksen, leverbaar, start):
    """Vaste mand: reeksen met een prijs op de start, die nu nog leverbaar zijn.

    reeksen   = {(product_id, winkel): [(tijdstip, prijs), ...]}
    leverbaar = set van (product_id, winkel) die nu leverbaar en vers zijn
    """
    mand = {}
    for (pid, winkel), reeks in reeksen.items():
        if (pid, winkel) not in leverbaar:
            continue
        if prijs_op(reeks, start) is None:
            continue
        mand.setdefault(pid, {})[winkel] = reeks
    return mand


# ---------------------------------------------------------------------------
# De database. Alleen lezen.
# ---------------------------------------------------------------------------

def cijfers(start=START, bf_week=None, details=0, nu=None):
    from models import Category, Offer, PriceHistory, Product, utcnow

    nu = nu or utcnow()
    sleutel = (start, bf_week, details)
    hit = _CACHE.get(sleutel)
    if hit and time.time() - hit[0] < _TTL:
        return hit[1]

    rijen = (PriceHistory.query
             .with_entities(PriceHistory.product_id, PriceHistory.retailer,
                            PriceHistory.recorded_at, PriceHistory.price)
             .order_by(PriceHistory.product_id, PriceHistory.retailer,
                       PriceHistory.recorded_at).all())
    reeksen = {}
    eerste_data = None
    for pid, winkel, moment, prijs in rijen:
        if not prijs or prijs <= 0:
            continue
        reeksen.setdefault((pid, winkel), []).append((moment, float(prijs)))
        if eerste_data is None or moment < eerste_data:
            eerste_data = moment
    if eerste_data is None:
        return {'fout': 'price_history is leeg'}

    vers = nu - timedelta(days=VERS_DAGEN)
    sets = {c.id for c in Category.query.filter_by(name='Apparaatsets').all()}
    leverbaar = {(o.product_id, o.retailer) for o in
                 Offer.query.with_entities(Offer.product_id, Offer.retailer)
                 .filter(Offer.is_available.is_(True), Offer.price > 0,
                         Offer.last_synced >= vers).all()}

    mand = maak_mand(reeksen, leverbaar, start)
    categorieen = {c.id: c.name for c in Category.query.all()}
    info = {}
    producten = (Product.query.with_entities(Product.id, Product.category_id,
                                             Product.title, Product.ean)
                 .filter(Product.id.in_(list(mand))).all()) if mand else []
    for p in producten:
        if p.category_id in sets:
            continue
        info[p.id] = (categorieen.get(p.category_id, '?'), (p.title or '')[:120], p.ean)
    mand = {pid: r for pid, r in mand.items() if pid in info}

    momenten = peilmomenten(start, nu)
    data = {
        'uitleg': ('Alleen lezen. Vaste mand: apparaat x winkel met een prijs op de '
                   'startdatum dat de winkel nu nog levert. Prijs per apparaat = '
                   'laagste over de winkels. Index = meetkundig gemiddelde van de '
                   'prijsverhoudingen, start = 100. EP en Alternate niet per winkel '
                   '(EP halve feed, Alternate te klein). Setjes niet. Historie '
                   'sinds 14 juli 2026, alleen bij een prijswijziging opgeslagen.'),
        'gemeten': nu.strftime('%Y-%m-%d %H:%M'),
        'historie_vanaf': eerste_data.strftime('%Y-%m-%d'),
        'start': start.strftime('%Y-%m-%d'),
        'mand': {
            'apparaten': len(mand),
            'reeksen': sum(len(r) for r in mand.values()),
            'apparaten_met_2_of_meer_winkels': sum(1 for r in mand.values() if len(r) >= 2),
        },
        '1_index_totaal': index_totaal(mand, momenten),
        '1_index_per_categorie': index_per_categorie(mand, info, momenten),
        '2_omnibus': [omnibus(mand, info, d, eerste_data, details)
                      for d in PEILDATA if d <= nu],
        '4_index_per_winkel': index_per_winkel(mand, momenten),
        '5_voorbeelden': voorbeelden(mand, info, start),
    }
    week = bf_week or BF_WEEK
    if bf_week or nu >= BF_WEEK + timedelta(days=1):
        data['3_black_friday_week'] = black_friday_week(mand, info, week, eerste_data)
    else:
        data['3_black_friday_week'] = {
            'status': 'nog niet te meten: vanaf 24 november 2026',
            'proef': 'geef ?bf=JJJJ-MM-DD mee om een eerdere week te meten',
        }
    _CACHE[sleutel] = (time.time(), data)
    return data
