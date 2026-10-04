"""Zoekzin-pagina's (zoekkenmerken.py): alleen apparaten die echt zijn wat de kop belooft.
Titels zoals ze op 4 okt 2026 op de pagina stonden. Draaien: python test_zoekzin_regels.py
"""
import sys
sys.path.insert(0, '.')

from zoekkenmerken import KENMERKEN, telt_mee

d = KENMERKEN['koffiemachines']['volautomaat']
fouten = 0

def check(naam, ok):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam)
    fouten += (not ok)

# Stonden ten onrechte op de pagina: winkeltekst noemde "bonen" of zelfs
# "volautomaat", maar de titel zegt wat het is.
for titel in ['Braun PurEase KF 3100 BK koffiezetapparaat Filter - Zwart',
              'Philips Daily HD7461/20 - Compact koffiezetapparaat - Zwart',
              'Tornado TCM-1025A-GS - Koffiezetapparaat met Bonenmaler - 1.5 l',
              'Barista Filterkoffiezetapparaat met Bonenmaler - Warmhoudfunctie',
              'Sage SES450BSS the Bambino Brushed Stainless Steel - RVS - Pistonmachine',
              'De\'Longhi Dedica Style EC685.M - Pistonmachine - Metal',
              'Philips Senseo Original Plus CSA210 koffiepadapparaat']:
    check(f'valt af: {titel[:50]}', not telt_mee(d, titel, titel + ' koffie van verse bonen, net als een volautomaat'))

# Echte volautomaten, ook met woorden die elders uitsluiten.
for titel in ['De\'Longhi Magnifica Start ECAM220.60.B - Volautomatisch koffiezetapparaat - Koffiemachine met bonen',
              'De\'Longhi Rivelia - volautomatische espressomachine met Bean Switch System en handmatig stoompijpje',
              'Philips 5500 series LatteGo EP5547/90 - Volautomatische Espressomachine - AquaClean filter',
              'Krups Serenity EA4008 - Volautomatische espressomachine - Zwart']:
    check(f'telt mee: {titel[:50]}', telt_mee(d, titel, titel))

# Titel zonder het woord, winkeltekst wel: telt mee (Philips EP-reeks).
check('telt mee via winkeltekst', telt_mee(d, 'Philips 2200 Series EP2224/10 - Espressomachine',
                                          'Philips 2200 Series EP2224/10 volautomatische espressomachine'))
check('alleen "bonen" in de tekst is geen volautomaat',
      not telt_mee(d, 'Melitta AromaFresh X 1030-06', 'Melitta AromaFresh X met bonen en molen'))
check('ontkenning telt niet', not telt_mee(d, 'Espressomachine X', 'geen volautomaat maar een piston'))

# Andere zoekzin-pagina's (4 okt 2026, zelfde controle: past de goedkoopste
# bij wat de kop belooft?).
from types import SimpleNamespace
from zoekkenmerken import _tekst_van

def kenmerk(cat, slug, titel, specs=None, tekst=''):
    d2 = KENMERKEN[cat][slug]
    p = SimpleNamespace(title=titel, specs=specs or {}, description=tekst)
    return telt_mee(d2, titel, _tekst_van(p, d2['in_tekst']))

check('solo-magnetron is geen combimagnetron',
      not kenmerk('magnetrons', 'combimagnetron', 'Tomado TMS2003W - Solo magnetron - 20 liter',
                  {'Combi functie': 'Nee'}))
check('combimagnetron telt mee',
      kenmerk('magnetrons', 'combimagnetron', 'Samsung MC28H5015AK combimagnetron 28 l'))
check('"combinatie" is geen combi',
      not kenmerk('magnetrons', 'combimagnetron', 'Magnetron in combinatie met grill'))
check('kruimeldief is geen steelstofzuiger',
      not kenmerk('stofzuigers', 'steelstofzuiger', 'Olvy kruimeldief PRO - Draadloos - Kruimelzuiger'))
check('robot is geen steelstofzuiger',
      not kenmerk('stofzuigers', 'steelstofzuiger', 'Roborock Q7 robotstofzuiger draadloos'))
check('2-in-1 steelstofzuiger met kruimelzuiger telt mee',
      kenmerk('stofzuigers', 'steelstofzuiger', 'Mova S5 Sense - Steelstofzuiger Incl. Kruimelzuiger'))
check('draadloze steelzuiger zonder het woord telt mee',
      kenmerk('stofzuigers', 'steelstofzuiger', 'Dyson V8 snoerloos'))
check('Low Frost is geen no frost',
      not kenmerk('koelkasten', 'no-frost', 'Inventum KV1500B Low Frost koel-vriescombinatie',
                  tekst='Low Frost: minder ijsvorming dan zonder, maar geen echte no frost'))
check('no frost telt mee', kenmerk('koelkasten', 'no-frost', 'Bosch KGN39VLCT No Frost'))
check('specificatie "Dweilfunctie: Nee" telt niet',
      not kenmerk('stofzuigers', 'dweilfunctie', 'Luxari steelstofzuiger S1000', {'Dweilfunctie': 'Nee'}))
check('specificatie "Dweilfunctie: Ja" telt wel',
      kenmerk('stofzuigers', 'dweilfunctie', 'Robot X', {'Dweilfunctie': 'Ja'}))

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
