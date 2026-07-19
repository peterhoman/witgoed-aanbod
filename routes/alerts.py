"""Prijsalert-routes: aanmelden (double opt-in), bevestigen, afmelden.

AVG-keuzes hier:
- Aanmelden slaat alléén e-mail + product + tijdstempel op; de alert doet
  niets tot de bevestigingsklik (double opt-in — voorkomt dat iemand
  andermans adres opgeeft).
- Bevestigen en afmelden werken met het cryptografisch willekeurige token
  uit de mail: geen login of account nodig.
- Afmelden verwijdert de rij volledig (dataminimalisatie).
- De respons op aanmelden verklapt niet of een adres al bestond
  (geen "dit e-mailadres is al aangemeld" — dat lekt wie zich waar heeft
  aangemeld); bestaand+onbevestigd krijgt gewoon opnieuw de
  bevestigingsmail.
"""
import re
import secrets

from flask import Blueprint, render_template, request, redirect, abort

from mailer import alerts_enabled, send_email
from models import db, Product, PriceAlert, utcnow

alerts_bp = Blueprint('alerts', __name__)

_EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]{2,}$')


@alerts_bp.route('/prijsalert', methods=['POST'])
def prijsalert_aanmelden():
    if not alerts_enabled():
        # Feature staat (nog) uit: formulier hoort dan niet eens zichtbaar
        # te zijn, maar een rechtstreekse POST moet ook netjes weigeren.
        abort(404)

    email = (request.form.get('email') or '').strip().lower()
    product_id = request.form.get('product_id', type=int)
    product = Product.query.get(product_id) if product_id else None

    if not product or not _EMAIL.match(email) or len(email) > 255:
        return render_template('alert_result.html', variant='ongeldig',
                               product=product), 400

    alert = PriceAlert.query.filter_by(product_id=product.id, email=email).first()
    if alert is None:
        alert = PriceAlert(product_id=product.id, email=email,
                           token=secrets.token_urlsafe(32),
                           last_notified_price=product.lowest_price)
        db.session.add(alert)
        db.session.commit()

    if not alert.confirmed:
        from price_alerts import bevestig_mail
        onderwerp, html = bevestig_mail(alert)
        send_email(alert.email, onderwerp, html)

    # Bewust altijd hetzelfde antwoord (nieuw, bestaand of al bevestigd).
    return render_template('alert_result.html', variant='aangemeld', product=product)


@alerts_bp.route('/prijsalert/bevestig/<token>')
def prijsalert_bevestigen(token):
    alert = PriceAlert.query.filter_by(token=token).first()
    if alert is None:
        return render_template('alert_result.html', variant='onbekend', product=None), 404
    if not alert.confirmed:
        alert.confirmed = True
        alert.confirmed_at = utcnow()
        # Referentieprijs verversen naar nú: tussen aanmelden en bevestigen
        # kan de prijs al bewogen zijn; de alert gaat over dalingen die de
        # aanvrager nog niet gezien heeft.
        alert.last_notified_price = alert.product.lowest_price
        db.session.commit()
    return render_template('alert_result.html', variant='bevestigd', product=alert.product)


@alerts_bp.route('/prijsalert/afmelden/<token>')
def prijsalert_afmelden(token):
    alert = PriceAlert.query.filter_by(token=token).first()
    if alert is None:
        # Ook een al-verwijderde alert toont "afgemeld": de klikker wil
        # gewoon zekerheid dat hij niets meer ontvangt.
        return render_template('alert_result.html', variant='afgemeld', product=None)
    product = alert.product
    db.session.delete(alert)
    db.session.commit()
    return render_template('alert_result.html', variant='afgemeld', product=product)
