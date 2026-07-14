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

            if not all([name, email, subject, message]):
                logger.warning("Contact form: missing required fields")
                return jsonify({'error': 'Alle velden zijn verplicht'}), 400

            logger.info(f"[+] Contact bericht ontvangen van {email}: {subject}")
            logger.info(f"    Naam: {name}")
            logger.info(f"    Bericht: {message[:100]}...")

            return jsonify({
                'success': True,
                'message': 'Bedankt! We hebben je bericht ontvangen en nemen spoedig contact op.'
            }), 200

        except Exception as e:
            logger.error(f"[!] Contact form error: {e}")
            return jsonify({'error': 'Er is iets fout gegaan. Probeer het later opnieuw.'}), 500

    return render_template('legal/contact.html')
