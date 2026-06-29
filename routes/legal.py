from flask import Blueprint, render_template

legal_bp = Blueprint('legal', __name__)


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


@legal_bp.route('/contact')
def contact():
    return render_template('legal/contact.html')
