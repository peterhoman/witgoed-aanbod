"""Prijsalert-kern: mailteksten + de daling-detectie die na elke sync draait.

De detectie (check_price_alerts) haakt aan op het einde van elke
winkel-sync, net als controleer_bestaande_fotos in icecat.py. Regels:

- Alleen bevestigde alerts (double opt-in afgerond) op leverbare producten.
- We mailen pas bij een daling van minstens DALING_DREMPEL (2%) t.o.v.
  last_notified_price (de prijs bij aanmelding, of bij de vorige alert):
  centen-schommelingen leveren geen mail op, en na elke mail schuift de
  lat mee omlaag zodat dezelfde daling nooit twee keer gemeld wordt.
- Niet-leverbare producten slaan we stil over (geen mail "hij is weg!"
  — de alert blijft staan en wordt weer actief zodra het product terug is).
- Een mailstoring breekt de sync nooit (send_email vangt alles af) en
  laat last_notified_price ongemoeid, zodat de volgende sync het opnieuw
  probeert.
"""
import logging
from html import escape

from flask import current_app

from mailer import send_email
from models import db, PriceAlert, utcnow

logger = logging.getLogger(__name__)

DALING_DREMPEL = 0.02  # minstens 2% onder de laatst gemelde prijs


def _euro(bedrag):
    s = f"{bedrag:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return s[:-3] if s.endswith(',00') else s


def _mail_shell(binnenkant):
    """Compacte, tabelloze HTML die in elke mailclient leesbaar blijft."""
    return (
        '<div style="font-family:system-ui,Arial,sans-serif;max-width:560px;'
        'margin:0 auto;color:#2b2b2b;line-height:1.6;">'
        f'{binnenkant}'
        '<p style="font-size:12px;color:#898781;border-top:1px solid #e1e0d9;'
        'padding-top:12px;margin-top:28px;">WitgoedAanbod.nl vergelijkt prijzen '
        'van o.a. Bol, Coolblue, MediaMarkt en Expert. Je ontvangt deze mail '
        'omdat dit e-mailadres een prijsalert aanvroeg.</p>'
        '</div>'
    )


def bevestig_mail(alert):
    site = current_app.config['SITE_URL']
    titel = escape(alert.product.title)
    link = f"{site}/prijsalert/bevestig/{alert.token}"
    onderwerp = 'Bevestig je prijsalert'
    html = _mail_shell(
        f'<h2 style="font-size:20px;">Nog &eacute;&eacute;n klik</h2>'
        f'<p>Je vroeg een prijsalert aan voor <strong>{titel}</strong>. '
        f'Klik op de knop om te bevestigen dat dit e-mailadres van jou is &mdash; '
        f'zonder bevestiging sturen we niets.</p>'
        f'<p style="margin:24px 0;"><a href="{link}" style="background:#2a78d6;'
        f'color:#ffffff;padding:12px 24px;border-radius:8px;text-decoration:none;'
        f'font-weight:600;">Bevestig prijsalert</a></p>'
        f'<p style="font-size:13px;color:#52514e;">Niet zelf aangevraagd? '
        f'Doe dan niets &mdash; zonder klik verlopen deze gegevens vanzelf.</p>'
    )
    return onderwerp, html


def alert_mail(alert, nieuwe_prijs):
    site = current_app.config['SITE_URL']
    titel = escape(alert.product.title)
    product_link = f"{site}/product/{alert.product.slug}"
    afmeld_link = f"{site}/prijsalert/afmelden/{alert.token}"
    oude = alert.last_notified_price
    onderwerp = f"Prijsdaling: {alert.product.title[:60]}"
    html = _mail_shell(
        f'<h2 style="font-size:20px;">De prijs is gedaald &#128201;</h2>'
        f'<p><strong>{titel}</strong> is nu te koop voor '
        f'<strong style="font-size:18px;">&euro; {_euro(nieuwe_prijs)}</strong>'
        + (f' <span style="color:#898781;text-decoration:line-through;">'
           f'&euro; {_euro(oude)}</span>' if oude else '')
        + '.</p>'
        f'<p style="margin:24px 0;"><a href="{product_link}" style="background:#2a78d6;'
        f'color:#ffffff;padding:12px 24px;border-radius:8px;text-decoration:none;'
        f'font-weight:600;">Bekijk alle prijzen</a></p>'
        f'<p style="font-size:13px;color:#52514e;">Geen alerts meer voor dit '
        f'product? <a href="{afmeld_link}">Meld je hier af</a>.</p>'
    )
    return onderwerp, html


def check_price_alerts(db_session=None):
    """Doorloop alle bevestigde alerts en mail waar de prijs echt daalde.
    Aan te roepen binnen een app-context, na afloop van een sync."""
    alerts = (PriceAlert.query.filter_by(confirmed=True)
              .join(PriceAlert.product).all())
    verstuurd = 0
    for alert in alerts:
        product = alert.product
        if not product.is_available:
            continue
        huidige = product.lowest_price
        referentie = alert.last_notified_price
        if huidige is None or referentie is None:
            continue
        if huidige > referentie * (1 - DALING_DREMPEL):
            continue
        onderwerp, html = alert_mail(alert, huidige)
        if send_email(alert.email, onderwerp, html):
            alert.last_notified_price = huidige
            alert.last_notified_at = utcnow()
            verstuurd += 1
    if verstuurd:
        db.session.commit()
        logger.info("Prijsalerts verstuurd: %d", verstuurd)
    return verstuurd
