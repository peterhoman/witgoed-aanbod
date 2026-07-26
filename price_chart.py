"""Prijsverloop-grafiek voor productpagina's, server-side als inline SVG.

Bouwt uit de price_history-rijen (zie models.log_price: alleen echte
prijswijzigingen worden opgeslagen) een traptreden-grafiek per winkel,
plus de "laagste prijs sinds we meten"-informatie. Geen JavaScript of
externe libraries nodig; de SVG schaalt mee via viewBox.

Kleuren per winkel liggen vast (kleur volgt de winkel, nooit de positie
in de grafiek) en komen uit een CVD-gevalideerd categorisch palet. De
tekstlabels staan in gewone inktkleuren; alleen de lijn zelf draagt de
winkelkleur. Naast de grafiek hoort in het template een tabelweergave
van dezelfde data (toegankelijkheid + zoekmachines).
"""
from datetime import timedelta

from models import PriceHistory, retailer_label, utcnow

# Vaste kleur per winkel (categorische slots 1-5, gevalideerde volgorde).
SERIES_KLEUREN = {
    'bol': '#2a78d6',        # blauw
    'mediamarkt': '#1baf7a', # aqua
    'coolblue': '#eda100',   # geel
    'expert': '#008300',     # groen
    'ep': '#4a3aa7',         # violet
    'alternate': '#c75373',  # framboos (CVD-veilig naast blauw/aqua/geel/groen/violet)
}
KLEUR_OVERIG = '#898781'

# Chrome-inkt (past bij de lichte site-achtergrond)
INK_SECUNDAIR = '#52514e'
INK_GEDEMPT = '#898781'
BASISLIJN = '#c3c2b7'
# Groen betekent op deze site besparing (zie de designspec). De punt op de
# huidige laagste prijs is het enige groene element in de grafiek.
GROEN = '#218358'

# 640x150 in plaats van 640x220: de designspec vraagt om een compactere
# grafiek. De SVG schaalt mee via viewBox met width:100%, dus op de smalste
# mobiele kolom (~358px) komt dat uit op 84px hoog — precies wat 5b vraagt.
BREEDTE, HOOGTE = 640, 150
MARGE_L, MARGE_R, MARGE_T, MARGE_B = 52, 46, 12, 24


def _euro(bedrag):
    """1234.5 -> '1.234,50' (Nederlandse notatie)."""
    s = f"{bedrag:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return s[:-3] if s.endswith(',00') else s


def _datum(dt):
    maanden = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun',
               'jul', 'aug', 'sep', 'okt', 'nov', 'dec']
    return f"{dt.day} {maanden[dt.month - 1]}"


def _ontdubbel_per_dag(rows):
    """Eén meting per winkel per dag: de laatste van die dag.

    De syncs draaien meerdere keren per dag, en winkels met een repricer
    veranderen hun prijs binnen een dag heen en weer. Zonder ontdubbelen
    staat dezelfde dag twee keer in de tabel met twee prijzen, wat als een
    fout leest. De laatste meting van een dag is de stand aan het eind van
    die dag; dat is wat een prijsverloop hoort te tonen.
    """
    per_dag = {}
    for r in rows:                       # rows staan oplopend op tijd
        per_dag[(r.retailer, r.recorded_at.date())] = r
    return sorted(per_dag.values(), key=lambda r: r.recorded_at)


def _prijswijzigingen(rows):
    """Aantal keer dat een winkel echt van prijs verandert (geen herhalingen)."""
    laatst, aantal = {}, 0
    for r in rows:
        if r.retailer in laatst and laatst[r.retailer] != r.price:
            aantal += 1
        laatst[r.retailer] = r.price
    return aantal


def _wisselende_winkel(rows, nu, dagen=7, drempel=3):
    """Winkel die de afgelopen `dagen` vaker dan `drempel` van prijs wisselde.

    Dat is repricer-gedrag, geen prijsontwikkeling. Voor zo'n winkel is
    "dit is de laagste prijs" misleidend: morgen staat hij waarschijnlijk
    weer hoger. Geeft (winkel, laagste, hoogste) terug, of None.
    """
    grens = nu - timedelta(days=dagen)
    per_winkel = {}
    for r in rows:
        if r.recorded_at >= grens:
            per_winkel.setdefault(r.retailer, []).append(r.price)

    for retailer, prijzen in per_winkel.items():
        wisselingen = sum(1 for a, b in zip(prijzen, prijzen[1:]) if a != b)
        if wisselingen > drempel:
            return retailer, min(prijzen), max(prijzen)
    return None


def build_price_history(product):
    """Verzamel alles wat de productpagina over het prijsverloop toont.

    Geeft None terug zolang er geen historie is; anders een dict met de
    laagste geregistreerde prijs, de meetstartdatum, tabelrijen en — zodra
    er echt verloop te tekenen valt (meerdere dagen of een wijziging) —
    de SVG van de grafiek.
    """
    rows = (PriceHistory.query
            .filter_by(product_id=product.id)
            .order_by(PriceHistory.recorded_at.asc())
            .all())
    if not rows:
        return None

    nu = utcnow()
    # De ruwe metingen apart houden: het ontdubbelen hieronder wist juist het
    # bewijs van repricer-gedrag. Elf prijswisselingen binnen twee dagen
    # worden na ontdubbelen twee metingen, en dan valt er niets meer te
    # detecteren. Tabel en grafiek gebruiken de ontdubbelde reeks, de
    # gedragsanalyse de volledige.
    ruwe_rows = rows
    rows = _ontdubbel_per_dag(rows)

    # Series per winkel; elke lijn loopt door tot "nu" met de huidige prijs,
    # maar alleen voor winkels die het apparaat nog leverbaar aanbieden.
    actuele = {o.retailer: o.price for o in product.available_offers}
    series = {}
    for r in rows:
        series.setdefault(r.retailer, []).append((r.recorded_at, r.price))
    for retailer, prijs in actuele.items():
        if retailer in series:
            series[retailer].append((nu, prijs))

    alle_punten = [p for punten in series.values() for p in punten]
    laagste = min(rows, key=lambda r: r.price)
    sinds = rows[0].recorded_at

    # Tabel: de echte wijzigingsmomenten, nieuwste eerst.
    tabel = [{
        'datum': _datum(r.recorded_at),
        'winkel': retailer_label(r.retailer),
        'prijs': _euro(r.price),
    } for r in reversed(rows)]

    laagste_is_nu = bool(actuele) and min(actuele.values()) <= laagste.price

    # Koopadvies: alleen een uitspraak doen als de data dat eerlijk onderbouwt
    # — geen kunstmatige urgentie. Is de huidige prijs niet de laagste ooit,
    # dan melden we neutraal wat de laagste prijs was, zonder aan te sporen.
    # Beide op de ruwe reeks: of de prijs bewóóg is een feit over de metingen,
    # niet over wat we ervan tonen.
    wijzigingen = _prijswijzigingen(ruwe_rows)
    dagen_historie = (nu - sinds).days
    wisselaar = _wisselende_winkel(ruwe_rows, nu)

    koopadvies = None
    if wisselaar:
        # Repricer: de prijs pendelt heen en weer. "Laagste prijs ooit" is dan
        # een momentopname, geen bevinding. Wat een koper hieraan heeft is de
        # bandbreedte: zie je vandaag de bovenkant, wacht dan een dag.
        winkel, laag, hoog = wisselaar
        koopadvies = (f'Deze prijs wisselt bij {retailer_label(winkel)} regelmatig '
                      f'tussen &euro; {_euro(laag)} en &euro; {_euro(hoog)}.')
    elif laagste_is_nu and len(rows) > 1:
        koopadvies = 'Dit is de laagste prijs sinds we dit apparaat volgen — een goed moment om te kopen.'
    elif actuele:
        huidige_laagste = min(actuele.values())
        verschil = huidige_laagste - laagste.price
        # Alleen vermelden bij een merkbaar verschil (>3%); anders voegt de
        # zin niets toe aan de tabel die er al staat.
        if laagste.price > 0 and verschil / laagste.price > 0.03:
            koopadvies = (f'De laagste prijs sinds we meten was &euro; {_euro(laagste.price)} '
                          f'(op {_datum(laagste.recorded_at)}) — nu is de laagste prijs '
                          f'&euro; {_euro(huidige_laagste)}.')

    resultaat = {
        'laagste_prijs': _euro(laagste.price),
        'laagste_is_nu': laagste_is_nu,
        'koopadvies': koopadvies,
        'sinds': _datum(sinds),
        'tabel': tabel,
        'svg': None,
        'legenda': [],
        'te_kort': None,
    }

    # Te weinig historie: geen grafiek en geen conclusie. Bij drie dagen
    # meten en een vlakke lijn is "dit is de laagste prijs" een tautologie,
    # en een as van € 503 tot € 516 rond een rechte lijn suggereert beweging
    # die er niet is. Dan liever één eerlijke zin.
    if dagen_historie < 14 or wijzigingen == 0:
        resultaat['koopadvies'] = None
        resultaat['te_kort'] = (
            f'We volgen dit apparaat sinds {_datum(sinds)}. De prijs is sindsdien niet veranderd.'
            if wijzigingen == 0 else
            f'We volgen dit apparaat sinds {_datum(sinds)} — nog te kort voor een betrouwbaar prijsverloop.'
        )
        return resultaat

    t0, t1 = sinds, nu
    if t1 <= t0:
        t1 = t0 + timedelta(hours=1)
    prijzen = [p for _, p in alle_punten]
    p_min, p_max = min(prijzen), max(prijzen)
    # De echte uitersten apart bewaren: die komen als aslabel op de grafiek,
    # en de opgerekte waarden hieronder zijn tekenruimte, geen meting.
    echt_min, echt_max = p_min, p_max
    if p_max - p_min < 1:  # vlakke lijn: wat lucht eromheen
        p_min, p_max = p_min - 5, p_max + 5
    rek = (p_max - p_min) * 0.12
    p_min, p_max = max(0, p_min - rek), p_max + rek

    plot_b = BREEDTE - MARGE_L - MARGE_R
    plot_h = HOOGTE - MARGE_T - MARGE_B

    def x(dt):
        return MARGE_L + plot_b * ((dt - t0).total_seconds()
                                   / (t1 - t0).total_seconds())

    def y(prijs):
        return MARGE_T + plot_h * (1 - (prijs - p_min) / (p_max - p_min))

    delen = []

    # Assen als twee lijnen, geen raster. De designspec wil border-left en
    # border-bottom; een raster over een grafiek van twaalf dagen suggereert
    # een precisie die de meting niet heeft.
    delen.append(f'<line x1="{MARGE_L}" y1="{MARGE_T}" x2="{MARGE_L}" '
                 f'y2="{MARGE_T + plot_h}" stroke="{BASISLIJN}" stroke-width="1"/>')
    delen.append(f'<line x1="{MARGE_L}" y1="{MARGE_T + plot_h}" '
                 f'x2="{BREEDTE - MARGE_R}" y2="{MARGE_T + plot_h}" '
                 f'stroke="{BASISLIJN}" stroke-width="1"/>')

    # Twee prijslabels langs de as in plaats van drie rasterniveaus. De spec
    # noemt ze niet, maar zonder enige schaal is een lijn geen grafiek: dan
    # staat er een vorm zonder eenheid. Alleen de uitersten, gedempt.
    #
    # Is de laagste ooit gemeten prijs ook de prijs van nu, dan staat datzelfde
    # bedrag hieronder al als groene punt. Twee keer € 649 op dezelfde hoogte
    # leest als een fout, dus dan valt het aslabel weg.
    huidige_laagste = min(actuele.values()) if actuele else None
    aslabels = [p for p in (echt_max, echt_min)
                if huidige_laagste is None or abs(p - huidige_laagste) >= 0.01]
    for prijs in aslabels:
        delen.append(f'<text x="{MARGE_L - 8}" y="{y(prijs) + 4:.1f}" text-anchor="end" '
                     f'font-size="11" fill="{INK_GEDEMPT}">&#8364; {_euro(prijs)}</text>')

    # X-labels: de echte meetperiode. Geen maandlabels zoals de spec vraagt --
    # die gaan uit van 90 dagen, en dan staat er twaalf keer dezelfde maand.
    delen.append(f'<text x="{MARGE_L}" y="{HOOGTE - 6}" font-size="11" '
                 f'fill="{INK_GEDEMPT}">{_datum(t0)}</text>')
    delen.append(f'<text x="{BREEDTE - MARGE_R}" y="{HOOGTE - 6}" text-anchor="end" '
                 f'font-size="11" fill="{INK_GEDEMPT}">vandaag</text>')

    # Lijnen per winkel (traptreden: prijs geldt tot de volgende wijziging)
    legenda = []
    for retailer in sorted(series, key=lambda k: min(pr for _, pr in series[k])):
        punten = series[retailer]
        kleur = SERIES_KLEUREN.get(retailer, KLEUR_OVERIG)
        pad = f'M {x(punten[0][0]):.1f} {y(punten[0][1]):.1f}'
        for j in range(1, len(punten)):
            pad += (f' H {x(punten[j][0]):.1f}'
                    f' V {y(punten[j][1]):.1f}')
        delen.append(f'<path d="{pad}" fill="none" stroke="{kleur}" '
                     f'stroke-width="2.5" stroke-linejoin="round"/>')
        # Markers op de echte wijzigingsmomenten, met native tooltip. Geen
        # tooltipbibliotheek: <title> is een SVG-element, geen dependency.
        for dt, prijs in punten[:-1]:
            delen.append(
                f'<circle cx="{x(dt):.1f}" cy="{y(prijs):.1f}" r="3.5" fill="{kleur}" '
                f'stroke="#ffffff" stroke-width="2">'
                f'<title>{_datum(dt)}: &#8364; {_euro(prijs)} '
                f'({retailer_label(retailer)})</title></circle>')
        legenda.append({
            'winkel': retailer_label(retailer),
            'kleur': kleur,
            'prijs_nu': _euro(punten[-1][1]),
        })

    # Punt op de huidige laagste prijs, met het bedrag ernaast. Bij meerdere
    # winkels krijgt alleen de goedkoopste hem: er hoort er per grafiek één te
    # zijn.
    #
    # Groen alleen als die prijs ook de laagste is die wij ooit maten. De
    # designspec schrijft "een groene punt op de huidige waarde", maar dat gaat
    # uit van goed nieuws ("nu € 40 onder het gemiddelde"). Bij een stijgende
    # prijs staat die punt op het duurste moment ooit, en groen betekent op
    # deze site besparing. Dan is het een positiemarkering in gewone inkt, geen
    # aanbeveling.
    if huidige_laagste is not None:
        is_laagste_ooit = huidige_laagste <= echt_min + 0.01
        kleur_punt = GROEN if is_laagste_ooit else INK_SECUNDAIR
        eind_x, eind_y = x(t1), y(huidige_laagste)
        delen.append(f'<circle cx="{eind_x:.1f}" cy="{eind_y:.1f}" r="4.5" '
                     f'fill="{kleur_punt}" stroke="#ffffff" stroke-width="2"/>')
        delen.append(f'<text x="{eind_x + 8:.1f}" y="{eind_y + 4:.1f}" font-size="12" '
                     f'font-weight="700" fill="{kleur_punt}">'
                     f'&#8364; {_euro(huidige_laagste)}</text>')

    svg = (f'<svg viewBox="0 0 {BREEDTE} {HOOGTE}" role="img" '
           f'aria-label="Prijsverloop sinds {_datum(sinds)}" '
           f'style="width:100%;height:auto;font-family:system-ui,sans-serif;">'
           + ''.join(delen) + '</svg>')
    resultaat['svg'] = svg
    resultaat['legenda'] = legenda
    return resultaat
