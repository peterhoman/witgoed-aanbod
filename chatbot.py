"""Billy, de advies-chatbot: vraag in gewone taal -> 2-3 productadviezen.

Veiligheidsontwerp (belangrijkste keuze):
- Het taalmodel KIEST alleen uit een door ons samengestelde shortlist en
  levert per keuze een reden; het identificeert producten met hun EAN.
- De server bouwt daarna zelf de productkaarten (naam, prijs, link) uit de
  database. Prijzen of links uit het model worden nooit gebruikt, en een
  EAN die niet in de shortlist zat wordt genegeerd — een verzonnen product
  kán dus nooit op het scherm komen.
- Geen (of geen passende) shortlist -> vast "geen resultaat"-antwoord
  zónder API-aanroep.

Zonder OPENROUTER_API_KEY: in productie staat de hele feature uit (widget
onzichtbaar, endpoint weigert); lokaal geeft _mock_advies een deterministisch
testantwoord zodat de flow end-to-end te testen is, net als de dev-modus
van mailer.py.
"""
import difflib
import json
import logging
import os
import re

import requests
from flask import current_app

from models import Product, Category

logger = logging.getLogger(__name__)

_OPENROUTER_ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions'

GEEN_RESULTAAT_TEKST = ('Helaas hebben we op dit moment geen product dat aan '
                        'deze wensen voldoet.')

# Volgorde is betekenisvol: de combi-termen staan vóór wasmachine/droger,
# anders wint "wasmachine" het van "wasmachine die ook kan drogen".
_CATEGORIE_KEYWORDS = [
    ('wasdroogcombinaties', ('was-droog', 'wasdroog', 'combi', '2-in-1', '2 in 1',
                             'ook kan drogen', 'ook droogt', 'ook kunnen drogen',
                             'wassen en drogen', 'wast en droogt')),
    ('wasmachines', ('wasmachine', 'wasautomaat', 'voorlader', 'bovenlader')),
    ('drogers', ('droger', 'warmtepomp', 'condensdroger')),
    ('koelkasten', ('koelkast', 'koel-vries', 'koelvries', 'amerikaanse koelkast',
                    'vriezer', 'diepvries')),
    ('vaatwassers', ('vaatwasser', 'afwasmachine', 'vaatwasmachine')),
    ('magnetrons', ('magnetron', 'combimagnetron')),
    ('ovens', ('oven', 'airfryer', 'air fryer', 'heteluchtfriteuse')),
    ('stofzuigers', ('stofzuiger', 'steelstofzuiger', 'robotstofzuiger')),
    ('koffiemachines', ('koffie', 'espresso', 'volautomaat', 'nespresso')),
    ('fornuizen', ('fornuis',)),
    ('kookplaten', ('kookplaat', 'inductie')),
    ('afzuigkappen', ('afzuigkap',)),
]

# Getallen direct gevolgd door een eenheid zijn specs, geen budget.
_SPEC_EENHEID = re.compile(
    r'\b(\d+(?:[.,]\d+)?)\s*(kg|kilo|toeren|rpm|r/min|liter|db|cm|couverts?|personen|persoons)\b',
    re.IGNORECASE)
_GETAL = re.compile(r'\b(\d{2,5})\b')


def detecteer_categorie(vraag):
    """Eerste categorie waarvan een keyword in de vraag voorkomt, of None.

    Twee rondes: eerst exact (substring), daarna fuzzy per woord zodat
    spelfouten als "wasmachiene" of "vaatwaser" ook herkend worden — de
    AI zelf kan daar prima mee overweg, dus de voorfilter moet niet
    strenger zijn dan de AI. Fuzzy alleen op woorden/keywords van >= 5
    tekens: bij korte woorden geeft gelijkenis te veel valse treffers
    ("boven" lijkt op "oven")."""
    v = vraag.lower()

    def _match(kw):
        if ' ' in kw:
            return kw in v
        # Woordgrens aan de voorkant: "oven" mag "ovens" matchen maar
        # niet het woord "boven"; "droger" wel "drogers".
        return re.search(r'\b' + re.escape(kw), v) is not None

    for slug, keywords in _CATEGORIE_KEYWORDS:
        if any(_match(kw) for kw in keywords):
            return slug

    woorden = [w for w in re.findall(r'[a-zà-ü]+', v) if len(w) >= 5]
    for slug, keywords in _CATEGORIE_KEYWORDS:
        for kw in keywords:
            if len(kw) < 5 or ' ' in kw:
                continue
            for woord in woorden:
                if difflib.SequenceMatcher(None, woord, kw).ratio() >= 0.82:
                    return slug
    return None


def detecteer_budget(vraag):
    """Grootste 'kaal' bedrag (>= 100) in de vraag, met eenheid-getallen
    (9 kg, 1400 toeren, 45 dB) eruit gefilterd. None als er geen staat."""
    zonder_specs = _SPEC_EENHEID.sub(' ', vraag)
    bedragen = [int(m) for m in _GETAL.findall(zonder_specs) if int(m) >= 100]
    return max(bedragen) if bedragen else None


def bouw_shortlist(categorie_slug, budget, maximum=12):
    """Leverbare producten in de categorie, binnen budget, gespreid over de
    prijsrange (niet alleen de goedkoopste): het model moet kunnen kiezen
    tussen budget-, midden- en topmodellen."""
    categorie = Category.query.filter_by(slug=categorie_slug).first()
    if not categorie:
        return []
    q = (Product.query.filter_by(category_id=categorie.id, is_available=True)
         .filter(Product.ean.isnot(None)).order_by(Product.price.asc()))
    if budget:
        q = q.filter(Product.price <= budget)
    producten = q.all()
    if len(producten) <= maximum:
        return producten
    stap = len(producten) / maximum
    return [producten[int(i * stap)] for i in range(maximum)]


def _product_regel(p):
    specs = p.specs or {}
    spec_delen = [f"{k}: {v}" for k, v in list(specs.items())[:6]]
    return (f"EAN {p.ean} | {p.title} | € {p.lowest_price:.2f} | "
            + (' | '.join(spec_delen) if spec_delen else 'geen specs bekend'))


_SYSTEEM_PROMPT = """Je bent Billy, de productadviseur van WitgoedAanbod.nl (een Nederlandse prijsvergelijker, geen winkel).

Regels:
- Kies UITSLUITEND uit de meegegeven productlijst; identificeer elk gekozen product met zijn EAN exact zoals opgegeven.
- Verzin NOOIT producten, prijzen of eigenschappen die niet in de lijst staan.
- Sluit de lijst niet goed aan bij de vraag, forceer dan GEEN dichtstbijzijnd alternatief: zet "geen_passend_product" op true en laat "advies" leeg.
- Adviseer maximaal 3 producten, met per product 1-2 zinnen onderbouwing in gewoon Nederlands, toegespitst op de vraag.
- Noem geen kortingscodes of cashback-acties.

Antwoord ALLEEN met geldige JSON, zonder tekst eromheen, in dit formaat:
{"geen_passend_product": false, "toelichting": "korte inleiding van 1 zin", "advies": [{"ean": "1234567890123", "reden": "..."}]}"""


def _roep_openrouter(vraag, shortlist):
    productlijst = '\n'.join(_product_regel(p) for p in shortlist)
    payload = {
        'model': current_app.config['OPENROUTER_MODEL'],
        'messages': [
            {'role': 'system', 'content': _SYSTEEM_PROMPT},
            {'role': 'user', 'content': f"Vraag van de bezoeker: {vraag}\n\nBeschikbare producten:\n{productlijst}"},
        ],
        'temperature': 0.3,
        'max_tokens': 700,
    }
    resp = requests.post(
        _OPENROUTER_ENDPOINT, json=payload, timeout=30,
        headers={'Authorization': f"Bearer {current_app.config['OPENROUTER_API_KEY']}",
                 # Aanbevolen door OpenRouter voor herkenbaarheid in hun dashboard
                 'HTTP-Referer': current_app.config['SITE_URL'],
                 'X-Title': 'WitgoedAanbod.nl Billy'})
    resp.raise_for_status()
    tekst = resp.json()['choices'][0]['message']['content']
    # Sommige modellen wikkelen JSON toch in ```json-hekjes.
    tekst = re.sub(r'^```(?:json)?\s*|\s*```$', '', tekst.strip())
    return json.loads(tekst)


def _mock_advies(shortlist):
    """Deterministisch dev-antwoord (geen key, lokale omgeving): maakt de
    hele flow testbaar zonder ooit echt een API aan te roepen."""
    return {'geen_passend_product': False,
            'toelichting': '(dev-testantwoord, geen echte AI-keuze)',
            'advies': [{'ean': p.ean, 'reden': 'Dev-modus: eerste product uit de shortlist.'}
                       for p in shortlist[:2]]}


def _is_dev():
    return os.getenv('FLASK_ENV') != 'production' and not os.getenv('RAILWAY_ENVIRONMENT')


def chat_enabled():
    return bool(current_app.config.get('OPENROUTER_API_KEY')) or _is_dev()


def beantwoord_vraag(vraag):
    """Volledige pijplijn: vraag -> respons-dict voor de widget.

    Respons-vormen:
      {'type': 'advies', 'toelichting': str, 'producten': [{naam, prijs,
        url, reden, winkels}]}
      {'type': 'geen_resultaat', 'tekst': str}
      {'type': 'fout', 'tekst': str}   (wordt niet gecachet)
    """
    categorie = detecteer_categorie(vraag)
    if categorie is None:
        # Geen apparaat herkend: nette uitleg i.p.v. een API-gok.
        return {'type': 'geen_resultaat',
                'tekst': ('Ik kan helpen met apparaten die we vergelijken '
                          '(zoals wasmachines, drogers, koelkasten, vaatwassers, '
                          'ovens en stofzuigers). Noem het soort apparaat in je '
                          'vraag, dan zoek ik met je mee!')}, categorie

    budget = detecteer_budget(vraag)
    shortlist = bouw_shortlist(categorie, budget)
    if not shortlist:
        return {'type': 'geen_resultaat', 'tekst': GEEN_RESULTAAT_TEKST}, categorie

    try:
        if current_app.config.get('OPENROUTER_API_KEY'):
            uitkomst = _roep_openrouter(vraag, shortlist)
        else:
            uitkomst = _mock_advies(shortlist)
    except Exception as e:
        logger.error("Billy/OpenRouter-fout: %s", e)
        return {'type': 'fout',
                'tekst': 'Het advies lukt op dit moment even niet. Probeer het zo opnieuw.'}, categorie

    if uitkomst.get('geen_passend_product') or not uitkomst.get('advies'):
        return {'type': 'geen_resultaat', 'tekst': GEEN_RESULTAAT_TEKST}, categorie

    # Kaarten bouwen uit ÓNZE data; onbekende EAN's stil negeren.
    per_ean = {p.ean: p for p in shortlist}
    producten = []
    for keuze in uitkomst['advies'][:3]:
        p = per_ean.get(str(keuze.get('ean', '')).strip())
        if p is None:
            continue
        producten.append({
            'naam': p.title,
            'prijs': f"{p.lowest_price:.2f}".replace('.', ','),
            'url': f"/product/{p.slug}",
            'winkels': p.retailer_count,
            'reden': str(keuze.get('reden', ''))[:300],
        })
    if not producten:
        return {'type': 'geen_resultaat', 'tekst': GEEN_RESULTAAT_TEKST}, categorie

    return {'type': 'advies',
            'toelichting': str(uitkomst.get('toelichting', ''))[:300],
            'producten': producten}, categorie
