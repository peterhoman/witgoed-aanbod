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

print('ALLES GOED' if ok else 'ER GAAT IETS FOUT')
sys.exit(0 if ok else 1)
