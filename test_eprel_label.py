# Proef: een energieklasse uit een vervallen EPREL-register wordt niet getoond en niet naar Google gestuurd.
# Draaien vanuit de projectmap:  python test_eprel_label.py
import sys, os
sys.path.insert(0, os.getcwd())
import eprel_specs

ok = True
def check(naam, voorwaarde, extra=''):
    global ok
    print(('GOED ' if voorwaarde else 'FOUT ') + naam + (' -> ' + extra if extra and not voorwaarde else ''))
    ok = ok and voorwaarde

g = {'energyClass': 'APPP', 'noise': 62, 'ratedCapacity': 9}
droger = eprel_specs._regels(g, 'tumbledriers')
was = eprel_specs._regels(g, 'washingmachines2019')
oven = eprel_specs._regels({'energyClass': 'AP'}, 'ovens')

check('droger uit het oude register: geen energieklasse', not any(l == 'Energieklasse' for l, _ in droger), str(droger))
check('droger: de overige gegevens blijven staan', ('Geluidsniveau', '62 dB') in droger and ('Vulgewicht', '9 kg') in droger, str(droger))
check('wasmachine: klasse blijft, A+++ netjes geschreven', ('Energieklasse', 'A+++') in was, str(was))
check('oven: A+ blijft (ovens hebben de plus-schaal nog)', ('Energieklasse', 'A+') in oven, str(oven))
check('lege of onbekende productgroep: klasse geldt gewoon', eprel_specs.klasse_geldt_nog(None) and eprel_specs.klasse_geldt_nog('') and eprel_specs.klasse_geldt_nog('dishwashers2019'))
check('hoofdletters en spaties maken niet uit', not eprel_specs.klasse_geldt_nog(' TumbleDriers '))

kern = [('Waarde energielabel', 'C'), ('Geluidsniveau', '62 dB')]
k_droger, _ = eprel_specs.ontdubbel_specs({'regels': droger}, kern, [])
k_was, _ = eprel_specs.ontdubbel_specs({'regels': was}, kern, [])
check('droger: het winkellabel komt terug in de specificaties', ('Waarde energielabel', 'C') in k_droger, str(k_droger))
check('wasmachine: EPREL wint nog steeds van het winkelveld', ('Waarde energielabel', 'C') not in k_was, str(k_was))

# Botsende labels: het gekleurde blokje valt weg, de rest blijft
kosten = {'label': 'D', 'jaar_kwh': 200, 'jaar_kosten': '60', 'meerkosten_slechter_label': {'label': 'E', 'bedrag': '120'}}
botst = eprel_specs.label_zonder_botsing(kosten, {'regels': [('Energieklasse', 'E'), ('Geluidsniveau', '38 dB')]})
check('winkel D, register E: blokje weg', botst['label'] is None, str(botst))
check('winkel D, register E: zin over meerkosten weg', botst['meerkosten_slechter_label'] is None, str(botst))
check('winkel D, register E: stroomkosten blijven staan', botst['jaar_kosten'] == '60' and botst['jaar_kwh'] == 200, str(botst))
check('het origineel is niet aangepast (geen bijwerking op gecachte gegevens)', kosten['label'] == 'D' and kosten['meerkosten_slechter_label'] is not None)
gelijk = eprel_specs.label_zonder_botsing(kosten, {'regels': [('Energieklasse', 'D')]})
check('winkel D, register D: blokje blijft', gelijk['label'] == 'D' and gelijk['meerkosten_slechter_label'] is not None)
check('kleine letter en spatie tellen niet als botsing', eprel_specs.label_zonder_botsing({'label': ' d '}, {'regels': [('Energieklasse', 'D')]})['label'] == ' d ')
check('geen EPREL-blok: niets verandert', eprel_specs.label_zonder_botsing(kosten, None) is kosten)
check('EPREL zonder klasse (droger oud register): winkellabel blijft', eprel_specs.label_zonder_botsing(kosten, {'regels': droger})['label'] == 'D')
check('geen stroomkosten: blijft None', eprel_specs.label_zonder_botsing(None, {'regels': [('Energieklasse', 'E')]}) is None)

# De feed: de hele klasse, niet alleen de eerste letter
from routes.merchant_feed import _GELDIGE_KLASSEN
def feedklasse(ruw):
    k = eprel_specs._fmt_klasse((ruw or '').strip().upper())
    return k if k in _GELDIGE_KLASSEN else None
check('feed: AP wordt A+ (was: afgekapt tot A)', feedklasse('AP') == 'A+')
check('feed: APPP wordt A+++', feedklasse('APPP') == 'A+++')
check('feed: gewone letters ongewijzigd', [feedklasse(x) for x in 'ABCDEFG'] == list('ABCDEFG'))
check('feed: rommel gaat niet mee', feedklasse('NVT') is None and feedklasse('') is None and feedklasse(None) is None and feedklasse('H') is None)

# De koppeling zelf: nieuw drogerregister voorop, en de exacte treffer wint
import eprel
check('drogers: nieuw register eerst, oud als vangnet',
      eprel.groepen_voor('Drogers', 'Bosch WQG133DBNL warmtepompdroger') == ['tumbledryers20232534', 'tumbledriers'],
      str(eprel.groepen_voor('Drogers', 'Bosch WQG133DBNL warmtepompdroger')))
check('was-droogcombinatie blijft in haar eigen register',
      eprel.groepen_voor('Combi Was-Droog', 'AEG LWR9506BN4 was-droogcombinatie') == ['washerdriers2019'])
lg = [{'modelIdentifier': m} for m in ('RT90X8BC', 'RT90X8C', 'RT90X8', 'RT90X8B', 'RT90X8YB')]
check('exacte treffer wint van de eerste (LG RT90X8, zoals EPREL ze echt teruggeeft)',
      eprel._kies_treffer(lg, 'Rt90x8')['modelIdentifier'] == 'RT90X8')
check('zonder exacte treffer blijft de eerste gelden (AEG met productcode erachter)',
      eprel._kies_treffer([{'modelIdentifier': 'TR73CB96 916099294'}], 'TR73CB96')['modelIdentifier'] == 'TR73CB96 916099294')
check('schrijfwijze met streepje of schuine streep telt als gelijk',
      eprel._kies_treffer([{'modelIdentifier': 'HW90-B14939S8'}, {'modelIdentifier': 'HW90B14939'}], 'Hw90-b14939')['modelIdentifier'] == 'HW90B14939')
check('geen treffers: None', eprel._kies_treffer([], 'X1234') is None)

# Hoort de treffer bij dit apparaat? De vier echte misgrepen van 21 september, en wat goed moet blijven
kk = eprel.koppeling_klopt
check('AEG met productcode erachter: klopt', kk('TR73CB96', 'TR73CB96 916099294', 'AEG TR73CB96 SensiDry'))
check('landcode erachter: klopt', kk('WF5S1045BB', 'WF5S1045BB/PL', 'Hisense 5S Serie WF5S1045BB'))
check('gezocht op het staartje, titel bevat het hele nummer: klopt', kk('Hs61w', 'W8F HS61W', 'Whirlpool W8f Hs61w - Maxispace'))
check('merknaam voor het nummer, titel bevat het: klopt', kk('WBDW40CB', 'Wisberg WBDW40CB', 'Wisberg WBDW40CB'))
check('Whirlpool W2F HD624 is NIET de P2F HD624 A', not kk('Hd624', 'P2F HD624 A', 'Whirlpool W2f Hd624 - Vrijstaande Vaatwasser'))
check('Inventum KK550B is NIET de RKK550B/02', not kk('KK550B', 'RKK550B/02', 'Inventum KK550B tafelmodel koelkast'))
check('Etna Vv856wit -> KVV856WIT: niet te bewijzen, dus niet', not kk('Vv856wit', 'KVV856WIT', 'Etna Vv856wit Vrijstaand Vrieskast'))
check('meerdere gezochte codes: een die past is genoeg', kk('X99, TR73CB96', 'TR73CB96 916099294', 'AEG iets'))
check('leeg gevonden nummer: klopt niet', not kk('ABC123', '', 'titel') and not kk('ABC123', None, 'titel'))
check('kies_treffer slaat een treffer over waar het nummer alleen middenin zit',
      eprel._kies_treffer([{'modelIdentifier': 'P2F HD624 A'}], 'Hd624', 'Whirlpool W2f Hd624') is None)
check('kies_treffer: tweede treffer klopt wel',
      eprel._kies_treffer([{'modelIdentifier': 'P2F HD624 A'}, {'modelIdentifier': 'W2F HD624 X'}], 'Hd624',
                          'Whirlpool W2F HD624 X - Vrijstaand')['modelIdentifier'] == 'W2F HD624 X')

# De inhaalslag: rijen uit het oude register en niet-gevonden drogers, precies één keer
from datetime import timedelta
from flask import Flask
from models import db, Product, Category, EprelData, utcnow
import eprel_bijwerken
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db.init_app(app)
with app.app_context():
    db.create_all()
    drogers = Category(name='Drogers', slug='drogers'); was = Category(name='Wasmachines', slug='wasmachines')
    db.session.add_all([drogers, was]); db.session.commit()
    voor = eprel_bijwerken._DROGERS_HERZIEN_VOOR - timedelta(days=5)
    na = max(eprel_bijwerken._DROGERS_HERZIEN_VOOR, utcnow()) + timedelta(hours=1)
    def maak(n, cat, **kw):
        p = Product(ean=str(n), title='t' + str(n), price=1, bol_url='x', slug=str(n), category_id=cat.id)
        db.session.add(p); db.session.flush()
        db.session.add(EprelData(product_id=p.id, **kw)); db.session.commit()
        return p.id
    a = maak(1, drogers, gevonden=True, productgroep='tumbledriers', opgehaald_at=voor)
    b = maak(2, drogers, gevonden=False, opgehaald_at=voor)
    c = maak(3, was, gevonden=False, opgehaald_at=voor)
    d = maak(4, was, gevonden=True, productgroep='washingmachines2019', opgehaald_at=voor)
    e = maak(5, drogers, gevonden=True, productgroep='tumbledriers', opgehaald_at=na)
    f = maak(6, drogers, gevonden=False, opgehaald_at=na)
    g = maak(7, drogers, gevonden=True, productgroep='tumbledryers20232534', opgehaald_at=voor)
    gekozen = {r.product_id for r in eprel_bijwerken._drogers_in_te_halen(100)}
    check('inhaalslag: droger uit het oude register, opgehaald voor de peildatum', a in gekozen)
    check('inhaalslag: droger die toen niet gevonden was', b in gekozen)
    check('inhaalslag: wasmachine die niet gevonden was doet NIET mee', c not in gekozen)
    check('inhaalslag: gewone wasmachine doet NIET mee', d not in gekozen)
    check('na het opnieuw ophalen komt een rij niet nog eens aan de beurt', e not in gekozen and f not in gekozen)
    check('droger die al in het nieuwe register staat doet NIET mee', g not in gekozen)
    rij = EprelData.query.filter_by(product_id=e).first()
    rij.opgehaald_at = utcnow() - timedelta(days=8); db.session.commit()
    check('oud register en een week niet nagekeken: wel weer aan de beurt',
          e in {r.product_id for r in eprel_bijwerken._drogers_in_te_halen(100)})
    h = maak(8, was, gevonden=True, productgroep='washingmachines2019', gezocht_op='Hw90-b14939',
             modelnummer='HW90-B14939S8', opgehaald_at=voor)
    i = maak(9, was, gevonden=True, productgroep='washingmachines2019', gezocht_op='WAN28', modelnummer='wan28',
             opgehaald_at=voor)
    j = maak(10, was, gevonden=True, productgroep='washingmachines2019', gezocht_op='X1', modelnummer='X1BC',
             opgehaald_at=na)
    afw = {r.product_id for r in eprel_bijwerken._afwijkend_typenummer(100)}
    check('afwijkend typenummer van voor de peildatum: opnieuw opzoeken', h in afw)
    check('exact gelijk (alleen hoofdletters anders): met rust laten', i not in afw)
    check('afwijkend maar al met de nieuwe code opgehaald: met rust laten', j not in afw)
    alles = [r.product_id for r in eprel_bijwerken._inhaalslag(100)]
    check('inhaalslag: drogers eerst, dan afwijkende typenummers, niets dubbel',
          set(alles[:3]) == {a, b, e} and alles.index(h) >= 3 and len(alles) == len(set(alles)), str(alles))
    paren = eprel_bijwerken._te_verversen(10)
    check('_te_verversen zet de inhaalslag voorop en levert (rij, product)',
          [r.product_id for r, p in paren][:1] != [] and all(p is not None for r, p in paren) and {a, b} <= {r.product_id for r, p in paren})

print('ALLES GOED' if ok else 'ER GAAT IETS FOUT')
sys.exit(0 if ok else 1)
