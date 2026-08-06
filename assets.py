"""Verkleinde css/js met een hash in de naam, plus zinnige cache-headers.

Designrapport 6 aug, punt 15. Twee dingen waren mis:

1. Flask stuurt statische bestanden standaard met Cache-Control: no-cache,
   dus elke bezoeker vroeg bij elk bezoek de volle 75 KB css opnieuw op.
2. main.css en main.js gingen onverkleind over de lijn (commentaar,
   inspringing) -- samen zo'n 19 KB die niets doet.

De oplossing hangt aan elkaar: verkleinen mag alleen agressief gecachet
worden als de naam meeverandert met de inhoud. Daarom krijgt het
verkleinde bestand een hash in de naam (main.<hash>.min.css in
static/gen/) en een cache van een jaar; verandert het bronbestand, dan
verandert de naam en haalt iedereen vanzelf de nieuwe op. De overige
statics (foto's, lettertypen, logo's) krijgen zeven dagen: lang genoeg om
te schelen, kort genoeg om een vervangen logo niet een jaar te missen.

Faalt het verkleinen (bibliotheek niet geïnstalleerd, schijf niet
beschrijfbaar), dan wijst asset() gewoon naar het origineel en doet de
site het onverminderd -- alleen langzamer, zoals nu.

Let op: de verkleinde css staat één map diep onder static/ (gen/), net
als css/. De relatieve verwijzingen in main.css (../fonts/..., ../img/...)
blijven daardoor kloppen. Verhuist gen/ ooit dieper, dan breken de
lettertypen.
"""
import hashlib
import os
from pathlib import Path

_BRONNEN = (
    ('css/main.css', 'css'),
    ('js/main.js', 'js'),
    ('js/babbelbot.js', 'js'),
)


def registreer(app):
    from datetime import timedelta
    from flask import request, url_for

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=7)

    verkleind = _bouw(Path(app.static_folder))

    @app.template_global('asset')
    def asset(pad):
        return url_for('static', filename=verkleind.get(pad, pad))

    @app.after_request
    def _jaar_cache_voor_gehashte_namen(response):
        # Alleen /static/gen/: dat zijn de enige bestanden waarvan de naam
        # meeverandert met de inhoud, dus de enige die 'immutable' aankunnen.
        if request.path.startswith('/static/gen/'):
            response.cache_control.public = True
            response.cache_control.max_age = 31536000
            response.cache_control.immutable = True
        return response


def _bouw(static_map):
    """Schrijf verkleinde kopieën naar static/gen/; geef {bron: doel} terug.

    Bij elke fout: leeg resultaat, de site draait dan op de originelen.
    Meerdere gunicorn-workers doen dit tegelijk; dezelfde inhoud geeft
    dezelfde naam, en os.replace is atomair, dus dat botst niet.
    """
    try:
        import rcssmin
        import rjsmin
    except ImportError:
        return {}

    verklein_per_soort = {'css': rcssmin.cssmin, 'js': rjsmin.jsmin}
    doelmap = static_map / 'gen'
    verkleind = {}
    try:
        doelmap.mkdir(exist_ok=True)
        for bron, soort in _BRONNEN:
            bronpad = static_map / bron
            if not bronpad.exists():
                continue
            klein = verklein_per_soort[soort](bronpad.read_text(encoding='utf-8'))
            hash10 = hashlib.md5(klein.encode('utf-8')).hexdigest()[:10]
            naam = f'{bronpad.stem}.{hash10}.min.{soort}'
            doel = doelmap / naam
            if not doel.exists():
                tijdelijk = doelmap / f'.{naam}.{os.getpid()}.tmp'
                tijdelijk.write_text(klein, encoding='utf-8')
                os.replace(tijdelijk, doel)
            verkleind[bron] = f'gen/{naam}'
        # Oude hashes opruimen (alleen relevant lokaal; op Railway begint
        # elke deploy met een schone container).
        actueel = {Path(pad).name for pad in verkleind.values()}
        for bestand in doelmap.glob('*.min.*'):
            if bestand.name not in actueel:
                bestand.unlink(missing_ok=True)
    except OSError:
        return {}
    return verkleind
