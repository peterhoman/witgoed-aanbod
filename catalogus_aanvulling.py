"""Catalogusaanvulling: witgoed dat bij twee of meer van onze winkels te koop is,
maar niet op de site staat, als nieuw product aanmaken. PROEF van 100.

Waarom dit bestaat (6 oktober 2026)
-----------------------------------
Alleen Bol, Coolblue en MediaMarkt maken producten aan; Expert, EP,
Voordeligwitgoed, Alternate en Witgoedhuis hangen alleen prijzen aan wat al
bestaat. Gemeten op 6 oktober: 552 witgoed-EAN's die bij twee of meer winkels
te koop zijn, staan niet op de site -- vooral Miele (126), Liebherr (113), AEG
(97) en Bosch (63), bijna altijd bij Expert en EP samen. Peter gaf op 6 oktober
ja op een proef van 100 (via de specialist-chat); de rest komt pas na een
meting in Search Console en een nieuw ja.

Regels
------
- Alleen een EAN die bij minstens twee van de vijf feeds hierboven staat
  (nieuw en op voorraad; de feeds bevatten alleen leverbare artikelen).
- Dezelfde opschoning als de MediaMarkt-sync: categorie op titel, niet-
  apparaten en uitsluitwoorden eruit, minimumprijs per categorie, nette
  adressen (product_slug).
- Dubbelcheck vóór het aanmaken: zelfde merk en zelfde typenummer als een
  bestaand product (andere EAN = kleurvariant of andere verpakking) -> niet
  aanmaken, alleen tellen.
- Verdeling van de proef (VERDELING), en binnen elke categorie eerst de
  apparaten die in EPREL staan. De EPREL-uitkomst wordt meteen bewaard.
- PROEF_MAXIMUM is een vaste grens over alle rondes samen: staan er 100 in
  de tabel catalogus_aanvullingen, dan doet de routine niets meer.

Na het aanmaken draaien de vijf winkelsyncs, zodat de prijzen er meteen aan
hangen; de tekst- en EPREL-routines pakken de nieuwe producten daarna zelf op.
"""
import logging
import re
import time
import urllib.request

from ean_match import ean_sleutel

logger = logging.getLogger(__name__)

PROEF_MAXIMUM = 100   # niet verhogen zonder Peters ja (zie docstring)
VERDELING = {'koelkasten': 45, 'wasmachines': 18, 'vaatwassers': 15, 'drogers': 10,
             'ovens': 4, 'kookplaten': 4, 'stofzuigers': 4}
MIN_WINKELS = 2
EPREL_POGINGEN_PER_PLEK = 3   # hoeveel kandidaten we in EPREL proberen per plek


def _tradetracker(module_naam, winkel):
    """[(ean, titel, merk, prijs, foto, beschrijving, winkel)] uit een TradeTracker-feed."""
    import importlib
    import json
    mod = importlib.import_module(module_naam)
    req = urllib.request.Request(mod.FEED_URL_DEFAULT, headers={'User-Agent': 'witgoedaanbod-sync/1.0'})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.load(resp)
    uit = []
    for p in data.get('products', []):
        props = p.get('properties') or {}
        def een(w):
            return w[0] if isinstance(w, list) and w else w
        ean = een(props.get('EAN')) or een(props.get('GTIN'))
        prijs = (p.get('price') or {}).get('amount')
        if not ean or not prijs:
            continue
        beelden = p.get('images') or []
        uit.append((str(ean), (p.get('name') or '').strip(), een(props.get('brand')) or '',
                    float(prijs), beelden[0] if beelden else '', p.get('description') or '', winkel))
    return uit


def _witgoedhuis():
    import xml.etree.ElementTree as ET
    from sync_witgoedhuis import FEED_URL_DEFAULT
    uit, url = [], FEED_URL_DEFAULT
    while url:
        req = urllib.request.Request(url, headers={'User-Agent': 'witgoedaanbod-sync/1.0'})
        with urllib.request.urlopen(req, timeout=180) as r:
            url = r.headers.get('X-Next-Url')
            boom = ET.fromstring(r.read())
        for p in boom.iter('product'):
            i = p.find('product_info')
            if i is None:
                continue
            def v(n):
                e = i.find(n)
                return (e.text or '').strip() if e is not None and e.text else ''
            if v('condition') not in ('', 'new') or v('in_stock').lower() != 'true':
                continue
            if v('ean') and v('price'):
                foto = next((e.text.strip() for e in i.iter('location') if e.text), '')
                # Witgoedhuis zet vaak alleen merk + typenummer in de titel; de
                # categorie erachter zodat de indeling op titel werkt.
                uit.append((v('ean'), f"{v('title')} {v('category')}".strip(), v('brand'),
                            float(v('price')), foto, v('description'), 'witgoedhuis'))
        time.sleep(0.5)
    return uit


def _feeds():
    rijen = []
    for module, winkel in (('sync_expert', 'expert'), ('sync_ep', 'ep'),
                           ('sync_voordeligwitgoed', 'voordeligwitgoed'),
                           ('sync_alternate', 'alternate')):
        try:
            rijen += _tradetracker(module, winkel)
        except Exception as e:  # één haperende feed mag de rest niet tegenhouden
            logger.warning(f"aanvulling: feed {winkel} overgeslagen: {e}")
    try:
        rijen += _witgoedhuis()
    except Exception as e:
        logger.warning(f"aanvulling: feed witgoedhuis overgeslagen: {e}")
    return rijen


def kandidaten(rijen):
    """{ean-sleutel: {'winkels', 'titel', 'merk', 'prijs', 'foto', 'beschrijving', 'cat', 'ean'}}
    voor witgoed dat bij MIN_WINKELS of meer winkels staat. Zuiver: geen database."""
    from catalogus_uitzonderingen import is_geen_apparaat
    from sync_mediamarkt import classify
    from sync_products import EXCLUDE_KEYWORDS, MIN_PRICES

    # Eerst per EAN groeperen: Witgoedhuis zet vaak alleen merk + typenummer
    # in de titel, dus de indeling komt van de beste titel van alle winkels
    # samen; daarna telt elke winkel die het apparaat voert.
    per_ean = {}
    for r in rijen:
        per_ean.setdefault(ean_sleutel(r[0]), []).append(r)
    uit = {}
    for k, groep in per_ean.items():
        titels = sorted({r[1] for r in groep}, key=lambda t: (classify(t) is None, -len(t)))
        titel = titels[0]
        cat = classify(titel)
        laag = titel.lower()
        if not cat or is_geen_apparaat(titel) or any(w in laag for w in EXCLUDE_KEYWORDS):
            continue
        geldig = [r for r in groep if r[3] >= MIN_PRICES.get(cat, 0)]
        winkels = {r[6] for r in geldig}
        if len(winkels) < MIN_WINKELS:
            continue
        uit[k] = {'winkels': winkels, 'ean': groep[0][0], 'titel': titel, 'cat': cat,
                  'merk': next((r[2] for r in geldig if r[2]), ''),
                  'prijs': min(r[3] for r in geldig),
                  'foto': next((r[4] for r in geldig if r[4]), ''),
                  'beschrijving': next((r[5] for r in geldig if r[5]), '')}
    return uit


def _typecodes(titel):
    """Typenummers zonder opmaak, voor de dubbelcheck ('KFN 4397 CD' -> 'kfn4397cd')."""
    from eprel import _kaal, codes_uit_titel
    codes = codes_uit_titel(titel)
    # Alleen het volledige nummer: de ingekorte zoekvorm ("WEA 135" uit
    # "WEA 135 WCS") zou WCS en WPS -- twee machines -- gelijk maken.
    vol = [c for c in codes if not any(o != c and o.startswith(c) for o in codes)]
    return {_kaal(c) for c in vol if len(_kaal(c)) >= 5}


def is_dubbel(merk, titel, bestaande):
    """Zelfde merk en zelfde typenummer als een bestaand product? `bestaande`
    is {merk-kleine-letters: [set(typecodes), ...]}. Een code die met de andere
    begint telt ook ('kfn4397cd' en 'kfn4397cdel125')."""
    codes = _typecodes(titel)
    if not codes:
        return False
    for andere in bestaande.get((merk or '').lower(), []):
        for a in codes:
            for b in andere:
                if a == b or a.startswith(b) or b.startswith(a):
                    return True
    return False


def vul_catalogus_aan(app):
    """Plannertaak: tot PROEF_MAXIMUM nieuwe producten aanmaken, dan de syncs."""
    with app.app_context():
        from eprel import zoek
        from eprel_bijwerken import _schrijf
        from filter_helpers import product_slug
        from models import CatalogusAanvulling, Category, EprelData, Product, db, utcnow
        from sync_products import guess_brand

        al = CatalogusAanvulling.query.count()
        ruimte = PROEF_MAXIMUM - al
        if ruimte <= 0:
            logger.info(f"aanvulling: proefmaximum ({PROEF_MAXIMUM}) bereikt, niets te doen")
            return {'aangemaakt': 0, 'reden': 'proefmaximum bereikt'}

        kand = kandidaten(_feeds())
        bekend = {ean_sleutel(p.ean) for p in Product.query.with_entities(Product.ean)}
        kand = {k: v for k, v in kand.items() if k not in bekend}

        # Dubbelcheck: merk + typenummer tegen alle bestaande producten.
        bestaande = {}
        for p in Product.query.with_entities(Product.brand, Product.title):
            codes = _typecodes(p.title or '')
            if codes:
                bestaande.setdefault((p.brand or '').lower(), []).append(codes)
        dubbel = 0
        schoon = []
        for v in kand.values():
            merk = v['merk'] or guess_brand(v['titel'])
            if is_dubbel(merk, v['titel'], bestaande):
                dubbel += 1
                continue
            v['merk'] = merk
            schoon.append(v)

        # Per categorie: al aangemaakte meetellen, dan EPREL-treffers voorop.
        gedaan = {}
        for r in CatalogusAanvulling.query.all():
            gedaan[r.categorie] = gedaan.get(r.categorie, 0) + 1
        categorieen = {c.slug: c for c in Category.query.all()}
        gekozen = []
        for cat, aantal in VERDELING.items():
            plekken = min(aantal - gedaan.get(cat, 0), ruimte - len(gekozen))
            if plekken <= 0 or cat not in categorieen:
                continue
            pool = sorted((v for v in schoon if v['cat'] == cat),
                          key=lambda v: (-len(v['winkels']), -len(_typecodes(v['titel']))))
            met, zonder, geprobeerd = [], [], 0
            for v in pool:
                if len(met) >= plekken:
                    break
                if geprobeerd < plekken * EPREL_POGINGEN_PER_PLEK:
                    geprobeerd += 1
                    try:
                        v['eprel'] = zoek(cat, f"{v['merk']} {v['titel']}", pauze=0.5)
                    except Exception as e:
                        logger.warning(f"aanvulling: EPREL-fout, verder zonder: {e}")
                        v['eprel'] = None
                    if v['eprel'] and v['eprel'].get('gevonden'):
                        met.append(v)
                        continue
                zonder.append(v)
            # Dubbelcheck ook binnen deze ronde (6 okt: drie Miele-apparaten
            # kwamen twee keer binnen, als kleurvariant met een eigen EAN).
            deze = []
            for v in met + zonder:
                if len(deze) >= plekken:
                    break
                if is_dubbel(v['merk'], v['titel'], bestaande):
                    dubbel += 1
                    continue
                bestaande.setdefault((v['merk'] or '').lower(), []).append(_typecodes(v['titel']))
                deze.append(v)
            gekozen += deze

        nieuw = []
        for v in gekozen:
            cat = categorieen[v['cat']]
            p = Product(ean=v['ean'], title=v['titel'][:255], brand=(v['merk'] or '')[:100] or None,
                        description=v['beschrijving'] or None, price=v['prijs'],
                        image_url=v['foto'] or None, bol_url='', category_id=cat.id,
                        slug=product_slug(v['titel'], v['ean']), retailer=sorted(v['winkels'])[0],
                        specs={}, is_available=False, last_synced=utcnow())
            db.session.add(p)
            db.session.flush()
            db.session.add(CatalogusAanvulling(product_id=p.id, ean=v['ean'], categorie=v['cat'],
                                               winkels=','.join(sorted(v['winkels'])),
                                               eprel=bool(v.get('eprel') and v['eprel'].get('gevonden'))))
            if v.get('eprel') is not None:
                rij = EprelData(product_id=p.id)
                db.session.add(rij)
                _schrijf(rij, p, v['eprel'])
            nieuw.append(p.slug)
        db.session.commit()
        logger.info(f"aanvulling: {len(nieuw)} aangemaakt, {dubbel} dubbelen tegengehouden, "
                    f"{len(kand)} kandidaten")

    # Prijzen er meteen aan hangen: de offers-only syncs koppelen op EAN.
    if nieuw:
        from sync_alternate import sync_alternate
        from sync_ep import sync_ep
        from sync_expert import sync_expert
        from sync_voordeligwitgoed import sync_voordeligwitgoed
        from sync_witgoedhuis import sync_witgoedhuis
        for sync in (sync_expert, sync_ep, sync_voordeligwitgoed, sync_alternate, sync_witgoedhuis):
            try:
                sync()
            except Exception as e:
                logger.warning(f"aanvulling: {sync.__name__} na het aanmaken mislukt: {e}")
    return {'aangemaakt': len(nieuw), 'dubbel': dubbel, 'kandidaten': len(kand), 'adressen': nieuw}
