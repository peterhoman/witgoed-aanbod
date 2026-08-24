"""Deelplaatje (og:image) en logo, gemaakt uit de eigen huisstijl.

Waarom dit bestaat
------------------
base.html verwijst sinds de bouw naar /static/img/og-image.png, maar dat
bestand bestond niet: op productie gaf het een 404. Gevolg: wie een link
naar de site deelde op WhatsApp, Facebook of LinkedIn kreeg alleen een
kale link zonder plaatje. Gevonden op 24 augustus 2026, bij het invullen
van het Trustpilot-profiel (dat om een logo van 400x300 vroeg).

Beide beelden komen uit dezelfde bron zodat ze niet uit elkaar lopen: de
mascotte uit static/img/mascot.png plus de merkkleuren uit main.css.

Opnieuw draaien
---------------
    python scripts/maak_beeldmateriaal.py

LET OP: het aantal winkels staat in de ondertitel. Komt er een winkel bij
of valt er een weg, werk dan AANTAL_WINKELS hieronder bij en draai het
script opnieuw -- anders staat er een getal dat de data niet draagt, en
dat is precies wat deze site nergens doet.
"""
from PIL import Image, ImageDraw, ImageFont

AANTAL_WINKELS = 7

PRIMARY = (0, 144, 218)      # --primary  #0090DA
DONKER = (0, 114, 173)       # --primary-dark #0072AD
ACCENT = (255, 107, 53)      # --accent   #FF6B35
WIT = (255, 255, 255)

MASCOTTE = 'static/img/mascot.png'
VET = 'C:/Windows/Fonts/segoeuib.ttf'
GEWOON = 'C:/Windows/Fonts/segoeui.ttf'


def _font(px, vet=True):
    return ImageFont.truetype(VET if vet else GEWOON, px)


def maak(breedte, hoogte, uitvoer, titel_px, sub_px, ondertitel,
         mascotte_hoogte, marge_rechts):
    """Eén beeld: merkblauw vlak, mascotte rechts, naam en ondertitel links."""
    mascotte = Image.open(MASCOTTE).convert('RGBA')
    img = Image.new('RGB', (breedte, hoogte), PRIMARY)
    teken = ImageDraw.Draw(img)
    teken.polygon([(0, hoogte), (breedte, hoogte),
                   (breedte, int(hoogte * 0.58))], fill=DONKER)

    schaal = mascotte_hoogte / mascotte.height
    mascotte = mascotte.resize((max(1, int(mascotte.width * schaal)),
                                mascotte_hoogte), Image.LANCZOS)
    mascotte_x = breedte - mascotte.width - marge_rechts
    img.paste(mascotte, (mascotte_x, hoogte - mascotte.height - int(hoogte * 0.05)),
              mascotte)

    # De tekst krijgt precies de ruimte links van de mascotte; het
    # lettertype krimpt tot het past, zodat een langere ondertitel nooit
    # over de mascotte heen loopt.
    x = int(breedte * 0.07)
    beschikbaar = mascotte_x - x - int(breedte * 0.03)

    titel = _font(titel_px)
    while teken.textlength('WitgoedAanbod.nl', font=titel) > beschikbaar and titel_px > 10:
        titel_px -= 2
        titel = _font(titel_px)

    y = int(hoogte * 0.26)
    teken.text((x, y), 'Witgoed', font=titel, fill=WIT)
    na_wit = teken.textbbox((x, y), 'Witgoed', font=titel)
    teken.text((na_wit[2], y), 'Aanbod', font=titel, fill=ACCENT)
    na_accent = teken.textbbox((na_wit[2], y), 'Aanbod', font=titel)
    teken.text((na_accent[2], y), '.nl', font=titel, fill=WIT)

    if ondertitel:
        sub = _font(sub_px, vet=False)
        while teken.textlength(ondertitel, font=sub) > beschikbaar and sub_px > 8:
            sub_px -= 1
            sub = _font(sub_px, vet=False)
        teken.text((x, na_wit[3] + int(hoogte * 0.05)), ondertitel, font=sub, fill=WIT)

    img.save(uitvoer, 'PNG', optimize=True)
    print('geschreven:', uitvoer, img.size)


if __name__ == '__main__':
    # 1200x630 is de maat die WhatsApp, Facebook, LinkedIn en X verwachten.
    maak(1200, 630, 'static/img/og-image.png', 88, 38,
         f'Vergelijk witgoedprijzen bij {AANTAL_WINKELS} winkels', 400, 60)
    # 400x300 is wat Trustpilot als logo aanraadt.
    maak(400, 300, 'static/img/logo-400x300.png', 30, 14,
         f'Vergelijk {AANTAL_WINKELS} winkels', 165, 14)
