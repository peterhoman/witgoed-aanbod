"""Verfijningslinks van een productpagina naar bestaande facetpagina's.

Waarom dit bestaat
------------------
De categoriecontext (zie category_context.py) zet inhoud op een dunne
productpagina. Dit doet iets anders: het verdeelt crawl- en linkwaarde beter
over de pagina's die er al zijn. Een productpagina wijst nu alleen omhoog naar
zijn categorie; de facetpagina's daaronder — 279 merkpagina's, 22
energielabelpagina's, 5 subtypepagina's — krijgen alleen links vanaf de
categoriepagina zelf.

De harde voorwaarde
-------------------
Uitsluitend linken naar facetpagina's die AL bestaan en AL in de sitemap staan.
Nieuwe filtercombinaties verzinnen zou honderden extra dunne pagina's opleveren,
en dat is dunne inhoud bestrijden met meer dunne inhoud.

Daarom rekent dit bestand met dezelfde bron als routes/seo.py: een link
verschijnt alleen als de bijbehorende facetpagina daadwerkelijk producten heeft.
Levert dat niets op, dan verdwijnt het hele blok.

Wat het kost
------------
Eén query per categorie, gecachet met dezelfde opzet en TTL als
_category_facets in routes/main.py. Een paginaweergave kost dus niets.
"""
import time
from collections import Counter, defaultdict

from filter_helpers import canonical_brand, energielabel_letter, slugify

_CACHE = {}
_TTL = 15 * 60  # seconden

_LABEL_SPEC = 'Waarde energielabel'


def _bouw_index(category_id, slug):
    """Tellingen per merk, energielabel en subtype voor één categorie.

    Alleen leverbare producten, want dat is ook wat de facetpagina's tonen en
    wat de sitemap meetelt. Alleen de twee kolommen die we nodig hebben, geen
    volledige productrijen.
    """
    from models import db, Product
    from routes.main import SUBCATEGORY_SPECS

    subtype_veld = SUBCATEGORY_SPECS.get(slug)
    rijen = (db.session.query(Product.brand, Product.specs)
             .filter(Product.category_id == category_id,
                     Product.is_available.is_(True))
             .all())

    merken = defaultdict(lambda: {'casing': Counter(), 'aantal': 0})
    labels = Counter()
    subtypes = Counter()
    for merk, specs in rijen:
        naam = (merk or '').strip()
        if naam:
            merken[naam.lower()]['casing'][naam] += 1
            merken[naam.lower()]['aantal'] += 1

        specs = specs or {}
        letter = energielabel_letter(specs.get(_LABEL_SPEC))
        if letter:
            labels[letter] += 1
        if subtype_veld:
            waarde = str(specs.get(subtype_veld) or '').strip()
            if waarde:
                subtypes[waarde] += 1

    return {
        # Zelfde ontdubbeling als compute_brand_facet: de feeds leveren "AEG"
        # naast "Aeg", en dat is één merk met één facetpagina.
        'merken': {sleutel: {'naam': canonical_brand(sleutel, data['casing']),
                             'aantal': data['aantal']}
                   for sleutel, data in merken.items()},
        'labels': labels,
        'subtype_veld': subtype_veld,
        'subtypes': subtypes,
    }


def _index(category_id, slug):
    nu = time.time()
    hit = _CACHE.get(category_id)
    if hit and nu - hit[0] < _TTL:
        return hit[1]
    data = _bouw_index(category_id, slug)
    _CACHE[category_id] = (nu, data)
    return data


def merk_facetpagina(product):
    """De merkpagina van dit apparaat binnen zijn categorie, of None.

    Apart opvraagbaar omdat het kruimelpad hem ook gebruikt: "Home /
    Wasmachines / Bosch / <model>" mag alleen die derde stap tonen als de
    pagina er echt is. Geeft {'naam', 'url', 'aantal'}.
    """
    categorie = product.category
    if categorie is None:
        return None
    index = _index(categorie.id, categorie.slug)
    # De slug is ongevoelig voor schrijfwijze (slugify verlaagt), dus "Aeg" en
    # "AEG" wijzen naar dezelfde pagina.
    merk = index['merken'].get((product.brand or '').strip().lower())
    if not merk:
        return None
    return {
        'naam': merk['naam'],
        'url': f"/category/{categorie.slug}/merk/{slugify(merk['naam'])}",
        'aantal': merk['aantal'],
    }


def verfijningslinks(product):
    """Links naar bestaande facetpagina's die op dit apparaat van toepassing zijn.

    Geeft {'kop': ..., 'links': [{'url', 'tekst', 'aantal'}]} of None.

    Hooguit drie: het merk binnen deze categorie, het energielabel, en het
    subtype (voorlader/bovenlader, warmtepomp/condens). Elk verschijnt alleen
    als de facetpagina er echt is.
    """
    categorie = product.category
    if categorie is None:
        return None

    index = _index(categorie.id, categorie.slug)
    naam = categorie.name.lower()
    specs = product.specs or {}
    links = []

    # 1. Merk binnen deze categorie.
    merk = merk_facetpagina(product)
    if merk:
        links.append({
            'url': merk['url'],
            'tekst': f"{merk['naam']} {naam}",
            'aantal': merk['aantal'],
        })

    # 2. Energielabel. Alleen een kale letter A t/m G telt -- ovens leveren
    #    "Energielabel niet van toepassing", en daar bestaat geen pagina voor.
    letter = energielabel_letter(specs.get(_LABEL_SPEC))
    if letter and index['labels'].get(letter):
        links.append({
            'url': f"/category/{categorie.slug}/energielabel/{letter.lower()}",
            'tekst': f"{categorie.name} met energielabel {letter}",
            'aantal': index['labels'][letter],
        })

    # 3. Subtype, alleen voor de twee categorieën met schone data (voorlader/
    #    bovenlader, warmtepomp/condens). Zie SUBCATEGORY_SPECS.
    veld = index['subtype_veld']
    waarde = str(specs.get(veld) or '').strip() if veld else ''
    if waarde and index['subtypes'].get(waarde):
        links.append({
            'url': f"/category/{categorie.slug}/type/{slugify(waarde)}",
            'tekst': waarde,
            'aantal': index['subtypes'][waarde],
        })

    if not links:
        return None
    return {'kop': f"Meer {naam} bekijken", 'links': links}
