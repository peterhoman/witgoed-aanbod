from flask import Blueprint, render_template, request, jsonify
import logging

logger = logging.getLogger(__name__)

legal_bp = Blueprint('legal', __name__)


@legal_bp.route('/over-ons')
def over_ons():
    return render_template('legal/over_ons.html')


@legal_bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')


@legal_bp.route('/disclaimer')
def disclaimer():
    return render_template('legal/disclaimer.html')


@legal_bp.route('/cookies')
def cookies():
    return render_template('legal/cookies.html')


@legal_bp.route('/voorwaarden')
def voorwaarden():
    return render_template('legal/voorwaarden.html')


@legal_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()

            # Honeypot: onzichtbaar veld dat mensen leeg laten maar
            # spam-bots invullen. Gevuld -> doen alsof het gelukt is
            # (geen mail), zodat de bot niets leert van de afwijzing.
            if request.form.get('website', '').strip():
                logger.info("Contact form: honeypot gevuld, genegeerd")
                return jsonify({'success': True,
                                'message': 'Bedankt! We hebben je bericht ontvangen en nemen spoedig contact op.'}), 200

            if not all([name, email, subject, message]):
                logger.warning("Contact form: missing required fields")
                return jsonify({'error': 'Alle velden zijn verplicht'}), 400

            # Doormailen naar de eigen inbox via Brevo (mailer.py); het
            # antwoordadres is de invuller zelf, dus "Beantwoorden" in de
            # mailbox antwoordt direct richting de bezoeker.
            from html import escape
            from flask import current_app
            from mailer import send_email
            html = (
                '<div style="font-family:system-ui,Arial,sans-serif;max-width:560px;">'
                f'<h2 style="font-size:18px;">Contactformulier witgoedaanbod.nl</h2>'
                f'<p><strong>Naam:</strong> {escape(name)}<br>'
                f'<strong>E-mail:</strong> {escape(email)}<br>'
                f'<strong>Onderwerp:</strong> {escape(subject)}</p>'
                f'<p style="white-space:pre-wrap;border-left:3px solid #e1e0d9;'
                f'padding-left:12px;">{escape(message)}</p>'
                '</div>'
            )
            verstuurd = send_email(current_app.config['CONTACT_TO_EMAIL'],
                                   f"Contactformulier: {subject[:80]}",
                                   html, reply_to=email)
            logger.info(f"[+] Contact bericht van {email}: {subject} (mail verstuurd: {verstuurd})")

            if not verstuurd:
                # Eerlijk zijn i.p.v. een bericht in het niets laten verdwijnen.
                return jsonify({'error': 'Versturen is nu niet mogelijk. '
                                'Mail ons direct via info@witgoedaanbod.nl.'}), 500

            return jsonify({
                'success': True,
                'message': 'Bedankt! We hebben je bericht ontvangen en nemen spoedig contact op.'
            }), 200

        except Exception as e:
            logger.error(f"[!] Contact form error: {e}")
            return jsonify({'error': 'Er is iets fout gegaan. Probeer het later opnieuw.'}), 500

    return render_template('legal/contact.html')
