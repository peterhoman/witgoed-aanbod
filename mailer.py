"""E-mailverzending voor prijsalerts, via Brevo's transactionele API.

Twee standen:
- Productie (BREVO_API_KEY gezet): echte verzending via https://api.brevo.com.
- Ontwikkeling (geen key, geen productie-omgeving): de mail wordt naar het
  log geschreven i.p.v. verstuurd, zodat de hele flow (aanmelden →
  bevestigen → alert) lokaal end-to-end te testen is zonder ooit echt te
  mailen. In productie zónder key wordt er niets verstuurd én niets
  gelogd met inhoud — de feature hoort dan uit te staan (is_configured
  bepaalt of het aanmeldformulier überhaupt getoond wordt).

Bewust requests-based (geen Brevo-SDK-dependency): het is één POST naar
één endpoint; de SDK zou de grootste dependency van het project zijn
voor het minste werk.
"""
import logging
import os

import requests
from flask import current_app

logger = logging.getLogger(__name__)

_BREVO_ENDPOINT = 'https://api.brevo.com/v3/smtp/email'


def is_configured():
    """Echte verzending mogelijk?"""
    return bool(current_app.config.get('BREVO_API_KEY'))


def _is_dev():
    return os.getenv('FLASK_ENV') != 'production' and not os.getenv('RAILWAY_ENVIRONMENT')


def alerts_enabled():
    """Mag de site het prijsalert-formulier tonen en aanmeldingen aannemen?
    Productie: alleen mét Brevo-key. Lokaal: altijd, met dev-logging in
    plaats van echte mail — zo is de hele flow te testen vóór de
    domeinverificatie rond is."""
    return is_configured() or _is_dev()


def send_email(to_email, subject, html):
    """Verstuur één transactionele mail. Geeft True terug bij succes
    (of dev-logging), False bij een verzendfout — nooit een exception,
    zodat een mailstoring een sync-run niet kan breken."""
    if not is_configured():
        if _is_dev():
            logger.warning("[DEV-MAIL] aan=%s onderwerp=%r\n%s", to_email, subject, html)
            return True
        logger.warning("Prijsalert-mail niet verstuurd (geen BREVO_API_KEY): %s", subject)
        return False

    payload = {
        'sender': {'email': current_app.config['ALERT_FROM_EMAIL'],
                   'name': current_app.config['ALERT_FROM_NAME']},
        'replyTo': {'email': current_app.config['ALERT_REPLY_TO']},
        'to': [{'email': to_email}],
        'subject': subject,
        'htmlContent': html,
    }
    try:
        resp = requests.post(
            _BREVO_ENDPOINT, json=payload, timeout=15,
            headers={'api-key': current_app.config['BREVO_API_KEY'],
                     'accept': 'application/json'})
        if resp.status_code in (200, 201):
            return True
        logger.error("Brevo weigerde mail (%s): %s", resp.status_code, resp.text[:300])
        return False
    except requests.RequestException as e:
        logger.error("Brevo onbereikbaar: %s", e)
        return False
