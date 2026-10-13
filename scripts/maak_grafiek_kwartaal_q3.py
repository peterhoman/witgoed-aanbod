"""Grafiek kwartaalrapport juli-september 2026: verandering van de prijsindex
per categorie van 16 juli tot 1 oktober (start = 100). Zelfde stijl als de
persgrafiek op /pers (1600x900, Arial, donkerblauw). Dalingen blauw,
stijgingen oranje, van grootste daling naar stijging.

De cijfers staan hieronder vast (peildatum 1 okt), gecontroleerd tegen
/api/black-friday op 13 okt 12:00 (mand 1.747 apparaten).
Draaien: python scripts/maak_grafiek_kwartaal_q3.py
"""
from PIL import Image, ImageDraw, ImageFont

INDEX_1_OKT = {
    'Wasmachines': 97.6, 'Vaatwassers': 97.7, 'Stofzuigers': 97.8, 'Was-droogcombinaties': 97.8,
    'Drogers': 98.0, 'Koelkasten': 98.1, 'Fornuizen': 98.2, 'Magnetrons': 99.3,
    'Ovens & airfryers': 99.4, 'Kookplaten': 100.1, 'Afzuigkappen': 100.2, 'Koffiemachines': 101.0,
}
TOTAAL = 98.7
TITEL = 'Witgoed werd deze zomer iets goedkoper'
ONDERTITEL = 'Prijsverandering per categorie, 16 juli tot 1 oktober 2026'
BRON = ('Bron: WitgoedAanbod.nl, prijsindex (meetkundig gemiddelde, start 16 juli = 100). '
        'Vrij te gebruiken met bronvermelding.')
VOET = f'Alle categorieën samen: {TOTAAL - 100:+.1f}%'.replace('.', ',') + \
       '. Vaste groep van 1.747 apparaten, per apparaat de laagste prijs over de winkels.'
BLAUW, ORANJE, ZWART, GRIJS, LIJN = '#1f4e79', '#e0692a', '#141414', '#5a5a5a', '#d0d0d0'
UIT = 'static/img/pers/witgoedprijzen-zomer-2026'

W, H = 1600, 900
rijen = sorted(((naam, round(v - 100, 1)) for naam, v in INDEX_1_OKT.items()), key=lambda x: x[1])
NUL_X, SCHAAL = 900, 150          # pixels per procentpunt
Y0, STAP, BALK = 190, 50, 34


def pct(v):
    return f'{v:+.1f}%'.replace('.', ',')


# --- SVG ---
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
     'font-family="Arial, Helvetica, sans-serif">', f'<rect width="{W}" height="{H}" fill="#fff"/>',
     f'<text x="60" y="76" font-size="40" font-weight="700" fill="{ZWART}">{TITEL}</text>',
     f'<text x="60" y="120" font-size="24" fill="{GRIJS}">{ONDERTITEL}</text>']
for i, (naam, v) in enumerate(rijen):
    y = Y0 + i * STAP
    kleur = BLAUW if v < 0 else ORANJE
    breed = max(abs(v) * SCHAAL, 3)
    x = NUL_X - breed if v < 0 else NUL_X
    s.append(f'<text x="60" y="{y + 25}" font-size="26" fill="{ZWART}">{naam.replace("&", "&amp;")}</text>')
    s.append(f'<rect x="{x:.0f}" y="{y}" width="{breed:.0f}" height="{BALK}" rx="6" fill="{kleur}"/>')
    tx, anker = (x - 14, 'end') if v < 0 else (x + breed + 14, 'start')
    s.append(f'<text x="{tx:.0f}" y="{y + 25}" font-size="26" font-weight="700" fill="{ZWART}" '
             f'text-anchor="{anker}">{pct(v)}</text>')
onder = Y0 + len(rijen) * STAP
s.append(f'<line x1="{NUL_X}" y1="{Y0 - 12}" x2="{NUL_X}" y2="{onder - 6}" stroke="{GRIJS}" stroke-width="2"/>')
s.append(f'<line x1="60" y1="{onder + 12}" x2="{W - 60}" y2="{onder + 12}" stroke="{LIJN}" stroke-width="2"/>')
s.append(f'<text x="60" y="{onder + 50}" font-size="22" fill="{GRIJS}">{VOET}</text>')
s.append(f'<text x="60" y="{onder + 84}" font-size="22" fill="{GRIJS}">{BRON}</text>')
s.append('</svg>')
open(UIT + '.svg', 'w', encoding='utf-8').write('\n'.join(s))

# --- PNG (zelfde maten, met Pillow) ---
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)


def font(grootte, vet=False):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if vet else 'C:/Windows/Fonts/arial.ttf', grootte)
    except OSError:
        return ImageFont.load_default()


d.text((60, 76), TITEL, font=font(40, True), fill=ZWART, anchor='ls')
d.text((60, 120), ONDERTITEL, font=font(24), fill=GRIJS, anchor='ls')
for i, (naam, v) in enumerate(rijen):
    y = Y0 + i * STAP
    kleur = BLAUW if v < 0 else ORANJE
    breed = max(abs(v) * SCHAAL, 3)
    x = NUL_X - breed if v < 0 else NUL_X
    d.text((60, y + 25), naam, font=font(26), fill=ZWART, anchor='ls')
    d.rounded_rectangle([x, y, x + breed, y + BALK], radius=6, fill=kleur)
    if v < 0:
        d.text((x - 14, y + 25), pct(v), font=font(26, True), fill=ZWART, anchor='rs')
    else:
        d.text((x + breed + 14, y + 25), pct(v), font=font(26, True), fill=ZWART, anchor='ls')
d.line([NUL_X, Y0 - 12, NUL_X, onder - 6], fill=GRIJS, width=2)
d.line([60, onder + 12, W - 60, onder + 12], fill=LIJN, width=2)
d.text((60, onder + 50), VOET, font=font(22), fill=GRIJS, anchor='ls')
d.text((60, onder + 84), BRON, font=font(22), fill=GRIJS, anchor='ls')
im.save(UIT + '.png', optimize=True)
print('klaar:', UIT + '.png', UIT + '.svg')
