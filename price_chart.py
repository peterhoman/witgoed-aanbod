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
    'ep': '#4a3aa7',         # violet (toekomstige winkel)
    'alternate': '#c75373',  # framboos (CVD-veilig naast blauw/aqua/geel/groen/violet)
}
KLEUR_OVERIG = '#898781'

# Chrome-inkt (past bij de lichte site-achtergrond)
INK_SECUNDAIR = '#52514e'
INK_GEDEMPT = '#898781'
GRIDLIJN = '#e1e0d9'
BASISLIJN = '#c3c2b7'

BREEDTE, HOOGTE = 640, 220
MARGE_L, MARGE_R, MARGE_T, MARGE_B = 56, 12, 12, 26


def _euro(bedrag):
    """1234.5 -> '1.234,50' (Nederlandse notatie)."""
    s = f"{bedrag:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return s[:-3] if s.endswith(',00') else s


def _datum(dt):
    maanden = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun',
               'jul', 'aug', 'sep', 'okt', 'nov', 'dec']
    return f"{dt.day} {maanden[dt.month - 1]}"


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
    koopadvies = None
    if laagste_is_nu and len(rows) > 1:
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
    }

    # Grafiek pas tekenen als er iets te zien is: minstens twee meetdagen
    # of minstens één echte prijswijziging.
    dagen = (nu - sinds).days
    if dagen < 1 and len(rows) <= len(series):
        return resultaat

    t0, t1 = sinds, nu
    if t1 <= t0:
        t1 = t0 + timedelta(hours=1)
    prijzen = [p for _, p in alle_punten]
    p_min, p_max = min(prijzen), max(prijzen)
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

    # Gridlijnen + y-labels (3 niveaus)
    for i in range(3):
        prijs = p_min + (p_max - p_min) * i / 2
        yy = y(prijs)
        delen.append(f'<line x1="{MARGE_L}" y1="{yy:.1f}" x2="{BREEDTE - MARGE_R}" '
                     f'y2="{yy:.1f}" stroke="{GRIDLIJN}" stroke-width="1"/>')
        delen.append(f'<text x="{MARGE_L - 8}" y="{yy + 4:.1f}" text-anchor="end" '
                     f'font-size="11" fill="{INK_GEDEMPT}">&#8364; {_euro(prijs)}</text>')

    # Basislijn + x-labels (eerste en laatste datum)
    delen.append(f'<line x1="{MARGE_L}" y1="{MARGE_T + plot_h}" '
                 f'x2="{BREEDTE - MARGE_R}" y2="{MARGE_T + plot_h}" '
                 f'stroke="{BASISLIJN}" stroke-width="1"/>')
    delen.append(f'<text x="{MARGE_L}" y="{HOOGTE - 8}" font-size="11" '
                 f'fill="{INK_GEDEMPT}">{_datum(t0)}</text>')
    delen.append(f'<text x="{BREEDTE - MARGE_R}" y="{HOOGTE - 8}" text-anchor="end" '
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
                     f'stroke-width="2" stroke-linejoin="round"/>')
        # Markers op de echte wijzigingsmomenten, met native tooltip
        for dt, prijs in punten[:-1]:
            delen.append(
                f'<circle cx="{x(dt):.1f}" cy="{y(prijs):.1f}" r="4" fill="{kleur}" '
                f'stroke="#ffffff" stroke-width="2">'
                f'<title>{_datum(dt)}: &#8364; {_euro(prijs)} '
                f'({retailer_label(retailer)})</title></circle>')
        legenda.append({
            'winkel': retailer_label(retailer),
            'kleur': kleur,
            'prijs_nu': _euro(punten[-1][1]),
        })

    svg = (f'<svg viewBox="0 0 {BREEDTE} {HOOGTE}" role="img" '
           f'aria-label="Prijsverloop sinds {_datum(sinds)}" '
           f'style="width:100%;height:auto;font-family:system-ui,sans-serif;">'
           + ''.join(delen) + '</svg>')
    resultaat['svg'] = svg
    resultaat['legenda'] = legenda
    return resultaat
