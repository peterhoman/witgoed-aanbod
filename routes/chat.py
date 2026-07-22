"""Babbelbot-endpoint: /api/chat-advies (POST {vraag}).

Kostenbeheersing in drie lagen vóór er ook maar één API-call gebeurt:
1. Cache: identieke vraag (genormaliseerd + gehasht) binnen 24u -> zelfde
   antwoord uit de database, geen API-call.
2. Rate limit per IP: 8 vragen per 5 minuten (in het procesgeheugen;
   gunicorn draait met 1 worker, en dat een herstart de tellers leegt is
   voor dit doel prima).
3. Dagplafond over de hele site: bij meer dan DAG_PLAFOND echte API-calls
   per dag krijgt iedereen een vriendelijke "druk"-melding — een virale
   piek of misbruik kan zo nooit een onbeperkte rekening veroorzaken.
"""
import hashlib
import json
import time
from collections import defaultdict, deque

from flask import Blueprint, jsonify, request

from chatbot import beantwoord_vraag, chat_enabled
from models import db, ChatCache, ChatLog, utcnow

chat_bp = Blueprint('chat', __name__)

CACHE_GELDIG_SECONDEN = 24 * 3600
RATE_LIMIT_AANTAL = 8
RATE_LIMIT_VENSTER = 5 * 60
DAG_PLAFOND = 400

_verzoeken_per_ip = defaultdict(deque)
_dag_teller = {'dag': None, 'aantal': 0}


def _rate_limited(ip):
    nu = time.time()
    q = _verzoeken_per_ip[ip]
    while q and nu - q[0] > RATE_LIMIT_VENSTER:
        q.popleft()
    if len(q) >= RATE_LIMIT_AANTAL:
        return True
    q.append(nu)
    return False


def _dag_plafond_bereikt():
    vandaag = utcnow().date()
    if _dag_teller['dag'] != vandaag:
        _dag_teller['dag'] = vandaag
        _dag_teller['aantal'] = 0
    return _dag_teller['aantal'] >= DAG_PLAFOND


def _normaliseer(vraag):
    return ' '.join(vraag.lower().split())


@chat_bp.route('/api/chat-advies', methods=['POST'])
def chat_advies():
    if not chat_enabled():
        return jsonify({'type': 'fout', 'tekst': 'De adviseur is momenteel niet beschikbaar.'}), 503

    data = request.get_json(silent=True) or {}
    vraag = str(data.get('vraag', '')).strip()
    if not vraag or len(vraag) > 500:
        return jsonify({'type': 'fout', 'tekst': 'Stel een vraag van maximaal 500 tekens.'}), 400

    ip = request.headers.get('X-Forwarded-For', request.remote_addr or '?').split(',')[0].strip()
    if _rate_limited(ip):
        return jsonify({'type': 'fout',
                        'tekst': 'Even rustig aan — probeer het over een paar minuten opnieuw.'}), 429

    vraag_hash = hashlib.sha256(_normaliseer(vraag).encode()).hexdigest()

    cache = ChatCache.query.filter_by(vraag_hash=vraag_hash).first()
    cache_vers = (cache is not None and
                  (utcnow() - cache.created_at).total_seconds() < CACHE_GELDIG_SECONDEN)

    db.session.add(ChatLog(vraag=vraag[:500], cache_hit=cache_vers))
    db.session.commit()

    if cache_vers:
        return jsonify(json.loads(cache.antwoord))

    if _dag_plafond_bereikt():
        return jsonify({'type': 'fout',
                        'tekst': 'De adviseur heeft het erg druk vandaag. Probeer het morgen opnieuw.'}), 503

    respons, categorie = beantwoord_vraag(vraag)

    # Categorie achteraf bijschrijven op de zojuist gelogde vraag.
    log = ChatLog.query.filter_by(vraag=vraag[:500]).order_by(ChatLog.id.desc()).first()
    if log and categorie:
        log.categorie = categorie
        db.session.commit()

    # Alleen echte antwoorden cachen; fouten moeten opnieuw geprobeerd worden.
    if respons['type'] in ('advies', 'geen_resultaat'):
        _dag_teller['aantal'] += 1
        if cache is None:
            db.session.add(ChatCache(vraag_hash=vraag_hash, antwoord=json.dumps(respons)))
        else:
            cache.antwoord = json.dumps(respons)
            cache.created_at = utcnow()
        db.session.commit()

    return jsonify(respons)
