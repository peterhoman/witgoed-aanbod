from flask import Blueprint, render_template, request, jsonify
import logging

logger = logging.getLogger(__name__)

legal_bp = Blueprint('legal', __name__)


@legal_bp.route('/over-ons')
def over_ons():
    return render_template('legal/over_ons.html')


@legal_bp.route('/productteksten')
def productteksten():
    """Hoe de productbeschrijvingen tot stand komen.

    Google vraagt hierom: waar automatisering of AI de inhoud grotendeels
    maakt, hoort erbij te staan hoe en waarom. Dat past niet in een regel
    onder de tekst zelf -- vandaar een korte verwijzing daar en het hele
    verhaal hier.

    Nog niet in de navigatie of de sitemap: de beschrijvingen staan op dit
    moment alleen in de tabel ai_content en nog op geen enkele productpagina.
    De pagina gaat mee zodra de teksten live gaan.
    """
    return render_template('legal/productteksten.html')


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


@legal_bp.route('/retourneren')
def retourneren():
    """Retourbeleid-uitleg (vergelijker: retour loopt via de winkel).
    Vereist door Google Merchant Center als retourbeleid-URL."""
    return render_template('legal/retourneren.html')


# Woorden waaraan je ziet dat het bericht ergens over gaat: over een
# apparaat, een prijs, een bestelling of over deze site. Eén treffer is
# genoeg. Dit heeft de taaltoets vervangen -- zie _is_spam.
_ONDERWERP = (
    'wasmachine', 'wasdroger', 'droger', 'koelkast', 'vriezer', 'vaatwasser',
    'afwasmachine', 'oven', 'magnetron', 'airfryer', 'friteuse', 'stofzuiger',
    'kookplaat', 'fornuis', 'afzuigkap', 'koffie', 'espresso', 'apparaat',
    'witgoed', 'wasmachines', 'koelkasten',
    'prijs', 'prijzen', 'aanbieding', 'korting', 'goedkoop', 'euro', 'kosten',
    'bestell', 'besteld', 'order', 'levering', 'bezorg', 'garantie', 'retour',
    'winkel', 'coolblue', 'bol.com', 'mediamarkt', 'vergelijk',
    'model', 'merk', 'energielabel', 'storing', 'defect', 'kapot',
    'link werkt', 'klopt niet', 'werkt niet',
)

# Bewust NIET in de lijst hierboven: 'website', 'site', 'pagina' en
# 'expert'. Elke SEO-aanbieding noemt "uw website", en dan zou dat woord
# het bericht laten passeren -- gemeten met "Wij bieden linkbuilding en
# gastartikelen aan voor uw website". Wie een echte melding doet over de
# site noemt daarnaast vrijwel altijd een apparaat, een winkel of wat er
# niet werkt, en komt daar dus alsnog door.

# Waar de bots om vragen. Stuk voor stuk dingen die deze site niet heeft:
# wij hebben geen nieuwsbrief, geen mailinglijst en geen eigen acties.
_SPAM_VRAAG = (
    'newsletter', 'email updates', 'e-mail updates', 'mailing list',
    'special offers', 'subscribe', 'seo services', 'link building',
    'guest post', 'backlink', 'crypto', 'casino',
    # Nederlandse varianten, na de inzending van 4 september 2026.
    'nieuwsbrief', 'mailinglijst', 'aanmelden voor', 'inschrijv',
    'linkbuilding', 'gastartikel', 'samenwerking aanbieden',
)


def _is_spam(onderwerp, bericht):
    """Ziet dit bericht eruit als bot-spam?

    Twee voorwaarden tegelijk, want elk apart is te grof:

    1. het bericht gaat nergens over -- geen apparaat, geen prijs, geen
       bestelling, niets over deze site, EN
    2. er wordt gevraagd om iets wat wij niet hebben.

    Alleen op trefwoorden filteren zou een Nederlander treffen die vraagt
    "hebben jullie een nieuwsbrief over wasmachine-aanbiedingen?" -- die
    noemt een apparaat en komt er dus gewoon door.

    De eerste voorwaarde was tot 5 september 2026 "er staat geen enkel
    Nederlands woord in". Dat werkte tegen de eerste twee inzendingen
    (22 en 31 augustus, allebei Engels), maar op 4 september kwam
    dezelfde soort inzending in het Nederlands binnen: onderwerp
    "Nieuwsbriefinschrijving", bericht "Ik ontvang graag meer informatie.
    Neem contact met mij op via e-mail.", met opnieuw een naam die niet
    bij het e-mailadres paste. Vol Nederlandse woorden, dus het filter
    liet hem door.

    Taal is dus geen bruikbaar onderscheid meer; onderwerp wel. Een echte
    vraag aan een witgoedvergelijker gaat over een apparaat, een prijs,
    een bestelling of over de site zelf. Een bot die zich inschrijft voor
    een nieuwsbrief die niet bestaat, noemt niets daarvan.
    """
    tekst = f' {onderwerp} {bericht} '.lower()
    gaat_ergens_over = any(w in tekst for w in _ONDERWERP)
    vraagt_om = any(w in tekst for w in _SPAM_VRAAG)
    return vraagt_om and not gaat_ergens_over


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

            # Zelfde afhandeling als de honeypot: doen alsof het gelukt
            # is, zodat de bot niet leert wat hem tegenhoudt.
            if _is_spam(subject, message):
                logger.info("Contact form: als spam herkend, genegeerd (%s)",
                            subject[:40])
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
