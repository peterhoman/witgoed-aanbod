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

print('ALLES GOED' if ok else 'ER GAAT IETS FOUT')
sys.exit(0 if ok else 1)
