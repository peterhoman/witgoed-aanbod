#!/usr/bin/env python
"""
Seed the database with original buying guides.

Written to give visitors genuine, independent advice (not copied from
manufacturer or retailer marketing text), addressing Bol.com's affiliate
review feedback that the site needs more "added value" content beyond
plain product listings.

Safe to re-run: existing guides (matched by slug) are replaced.
"""

from app import create_app
from models import db, Category, Guide

WASMACHINE_GUIDE = {
    'slug': 'wasmachine-kopen-waar-op-letten',
    'title': 'Wasmachine kopen: waar moet je op letten?',
    'excerpt': 'Vulgewicht, toerental, energielabel en geluidsniveau uitgelegd, zodat je een wasmachine kiest die echt bij je huishouden past.',
    'category_slug': 'wasmachines',
    'content': """
<h2>Bepaal eerst je vulgewicht</h2>
<p>Het vulgewicht (uitgedrukt in kg) bepaalt hoeveel was je in één keer kunt draaien. Als vuistregel geldt: reken ongeveer 1 kg was per gezinslid, plus wat extra voor beddengoed en handdoeken.</p>
<ul>
    <li><strong>7 kg:</strong> geschikt voor 1-2 personen</li>
    <li><strong>8-9 kg:</strong> geschikt voor een gezin van 3-4 personen</li>
    <li><strong>10 kg en meer:</strong> voor grotere gezinnen of wie liever minder vaak wast</li>
</ul>
<p>Een te kleine machine betekent vaker wassen; een te grote machine verbruikt onnodig meer water en stroom bij kleinere ladingen.</p>

<h2>Toerental centrifugeren</h2>
<p>Het toerental (rpm) bepaalt hoe droog je was uit de machine komt. Hoe hoger het toerental, hoe droger de was — maar ook hoe meer slijtage aan kleding en hoe meer geluid tijdens het centrifugeren.</p>
<ul>
    <li><strong>1200 rpm en lager:</strong> zachter voor kleding, iets vochtiger resultaat</li>
    <li><strong>1400 rpm:</strong> de meest gangbare middenweg</li>
    <li><strong>1600 rpm en hoger:</strong> droogste resultaat, handig als je ook een droger gebruikt en tijd wilt besparen</li>
</ul>

<h2>Energielabel en verbruik</h2>
<p>Sinds de herziening van de energielabels lopen de klassen van A (zuinigst) tot G. Een zuinigere wasmachine kost vaak iets meer in aanschaf, maar bespaart op de lange termijn op je energierekening — zeker als je regelmatig wast. Let ook op het waterverbruik per wasbeurt, dat staat meestal in de specificaties vermeld.</p>

<h2>Type belading: voorlader of bovenlader</h2>
<p>De meeste wasmachines zijn voorladers. Bovenladers zijn vaak smaller en daardoor handig in krappe ruimtes, maar het aanbod is beperkter en ze zijn gemiddeld iets duurder per liter trommelinhoud.</p>

<h2>Geluidsniveau</h2>
<p>Als je wasmachine in of naast een leefruimte staat (bijvoorbeeld een open keuken), is het geluidsniveau tijdens centrifugeren relevant. Machines met een laag geluidsniveau (rond 70 dB of lager tijdens centrifugeren) zijn merkbaar rustiger.</p>

<h2>Handige extra's</h2>
<p>Sommige machines hebben functies zoals een beladingssensor (past het water- en energieverbruik automatisch aan de hoeveelheid was aan), een quick-wash-programma, of stoomfuncties om kreuken te verminderen. Leuk om mee te nemen, maar niet essentieel — bepaal eerst je basisbehoefte (vulgewicht, toerental, energielabel) voordat je op extra's let.
</p>
""",
}

KOELKAST_GUIDE = {
    'slug': 'koelkast-kopen-complete-gids',
    'title': 'Koelkast kopen: de complete gids',
    'excerpt': 'Inhoud, type, energielabel en No Frost uitgelegd, zodat je een koelkast kiest die past bij je keuken en je huishouden.',
    'category_slug': 'koelkasten',
    'content': """
<h2>Hoeveel inhoud heb je nodig?</h2>
<p>De inhoud van een koelkast wordt uitgedrukt in liters. Als richtlijn:</p>
<ul>
    <li><strong>Tot 100 liter (tafelmodel):</strong> handig als bijzet-koelkast of voor een studentenkamer</li>
    <li><strong>150-250 liter:</strong> geschikt voor 1-2 personen</li>
    <li><strong>250-350 liter:</strong> geschikt voor een gezin van 3-4 personen</li>
    <li><strong>350 liter en meer:</strong> voor grotere huishoudens of wie graag voorraad inslaat</li>
</ul>

<h2>Type: koelkast, koel-vriescombinatie of Amerikaanse koelkast</h2>
<p>Een losse koelkast heeft alleen koelruimte. Een koel-vriescombinatie combineert koelen en vriezen in één toestel — handig als je geen aparte vriezer wilt of hebt. Amerikaanse koelkasten (side-by-side) bieden veel inhoud en vaak extra's zoals een waterdispenser, maar zijn ook aanzienlijk breder.</p>

<h2>No Frost versus handmatig ontdooien</h2>
<p>Bij een koelkast of vriezer zonder No Frost-techniek vormt zich na verloop van tijd ijs, waardoor je regelmatig moet ontdooien. No Frost-modellen voorkomen ijsvorming automatisch, wat onderhoud bespaart — dit zie je vaak terug in een iets hogere aanschafprijs.</p>

<h2>Energielabel</h2>
<p>Een koelkast staat, in tegenstelling tot een wasmachine, vrijwel de hele dag aan. Het energielabel heeft daardoor relatief veel invloed op je jaarlijkse energiekosten. Een zuiniger toestel (hogere klasse op het label) is vaak iets duurder in aanschaf, maar verdient zich op termijn terug via een lagere energierekening.</p>

<h2>Geluidsniveau</h2>
<p>Omdat een koelkast continu draait, kan geluid opvallen, zeker in een open keuken. Let op het aantal dB in de specificaties: onder de 40 dB is over het algemeen nauwelijks hoorbaar.</p>

<h2>Afmetingen en inbouw versus vrijstaand</h2>
<p>Meet altijd de beschikbare ruimte (hoogte, breedte, diepte, en ook de ruimte om deuren volledig te kunnen openen) voordat je een koelkast bestelt. Inbouwkoelkasten zijn ontworpen om naadloos in keukenkasten te passen, maar zijn vaak duurder en minder flexibel qua formaatkeuze dan vrijstaande modellen.</p>
""",
}


def seed():
    app = create_app()

    with app.app_context():
        for guide_data in [WASMACHINE_GUIDE, KOELKAST_GUIDE]:
            Guide.query.filter_by(slug=guide_data['slug']).delete()

            category = Category.query.filter_by(slug=guide_data['category_slug']).first()

            guide = Guide(
                title=guide_data['title'],
                slug=guide_data['slug'],
                excerpt=guide_data['excerpt'],
                content=guide_data['content'].strip(),
                category_id=category.id if category else None,
            )
            db.session.add(guide)
            print(f"[+] Added guide: {guide_data['title']}")

        db.session.commit()
        print("\n[+] Guides seeded successfully")


if __name__ == '__main__':
    seed()
