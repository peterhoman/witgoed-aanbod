"""Black Friday-cijfers (black_friday.py): de rekenregels, zonder database.
Draaien: python test_black_friday.py
"""
import sys
from datetime import datetime as D
sys.path.insert(0, '.')

import black_friday as bf

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra else ''))
    if not ok:
        fouten += 1

# 1. Prijs op een moment = laatste rij op of vóór dat moment.
r = [(D(2026, 7, 14), 500.0), (D(2026, 8, 10), 450.0), (D(2026, 9, 5), 480.0)]
check('prijs vóór de eerste rij is onbekend', bf.prijs_op(r, D(2026, 7, 1)) is None)
check('prijs geldt tot de volgende wijziging', bf.prijs_op(r, D(2026, 8, 31)) == 450)
check('prijs op het moment van wijziging is de nieuwe', bf.prijs_op(r, D(2026, 8, 10)) == 450)

# 2. Laagste in een venster telt ook de prijs die bij het begin al gold.
check('laagste in venster zonder wijziging = geldende prijs',
      bf.laagste_tussen(r, D(2026, 7, 20), D(2026, 8, 1)) == 500)
check('laagste in venster met daling', bf.laagste_tussen(r, D(2026, 7, 20), D(2026, 9, 30)) == 450)

# 3. Apparaatprijs = laagste over de winkels.
r2 = [(D(2026, 7, 10), 470.0)]
check('laagste over winkels', bf.apparaatprijs_op([r, r2], D(2026, 7, 20)) == 470)

# 4. Jevons: twee apparaten, één 10% omlaag, één gelijk -> ~94,9.
check('jevons', bf.jevons([(100, 90), (200, 200)]) == 94.9, bf.jevons([(100, 90), (200, 200)]))
check('jevons slaat ontbrekende prijzen over', bf.jevons([(100, None), (100, 110)]) == 110.0)

# 5. Vaste mand: een reeks die pas na de start begint, of nu niet leverbaar
#    is, valt eruit (anders meet je assortimentswisseling).
reeksen = {
    (1, 'coolblue'): r,
    (1, 'bol'): [(D(2026, 9, 1), 300.0)],        # nieuw na de start
    (2, 'mediamarkt'): [(D(2026, 7, 1), 800.0)],  # niet meer leverbaar
}
mand = bf.maak_mand(reeksen, {(1, 'coolblue'), (1, 'bol')}, D(2026, 7, 16))
check('alleen reeksen van vóór de start en nu leverbaar', mand == {1: {'coolblue': r}}, mand)

# 6. Peilmomenten: start, elke eerste van de maand, nu.
m = bf.peilmomenten(D(2026, 7, 16), D(2026, 10, 3, 18))
check('peilmomenten', [x.strftime('%m-%d') for x in m] == ['07-16', '08-01', '09-01', '10-01', '10-03'],
      [x.strftime('%m-%d') for x in m])

# 7. Omnibus: prijs op 1 okt (480) tegenover laagste in 90 dagen (450) = 6,7% boven.
info = {1: ('Wasmachines', 'Test', '123')}
o = bf.omnibus({1: {'coolblue': r}}, info, D(2026, 10, 1), D(2026, 7, 14), details=5)
check('omnibus: boven laagste', o['apparaten_lijst'][0]['boven_laagste_pct'] == 6.7, o)
check('omnibus: venster ingekort tot begin historie', o['venster_vanaf'] == '2026-07-14')
check('omnibus: telt >5%', o['meer_dan_5pct_boven_laagste'] == 1)

# 8. Black Friday-week: daling in de week die onder alles van daarvoor zakt.
rbf = r + [(D(2026, 11, 27, 6), 399.0), (D(2026, 12, 2), 480.0)]
w = bf.black_friday_week({1: {'coolblue': rbf}}, info, D(2026, 11, 23), D(2026, 7, 14))
check('bf-week: echt lager', w['echt_lager_dan_ooit_in_90_dagen'] == 1, w)
check('bf-week: verschil t.o.v. laagste', w['mediaan_verschil_pct'] == -11.3, w['mediaan_verschil_pct'])
# Een "korting" die alleen terugkeert naar een eerdere laagste prijs is geen echte daling.
rnep = [(D(2026, 7, 14), 450.0), (D(2026, 10, 1), 600.0), (D(2026, 11, 26), 450.0)]
w2 = bf.black_friday_week({1: {'coolblue': rnep}}, info, D(2026, 11, 23), D(2026, 7, 14))
check('bf-week: terug naar oude prijs = gelijk', w2['gelijk_aan_laagste'] == 1, w2)

# 9. Index per categorie waarschuwt bij een te kleine mand.
ic = bf.index_per_categorie({1: {'coolblue': r}}, info, [D(2026, 7, 16), D(2026, 8, 15)])
check('index per categorie', ic[0]['index'] == {'2026-07-16': 100.0, '2026-08-15': 90.0}, ic)
check('kleine mand krijgt waarschuwing', 'let_op' in ic[0])

# 10. Per winkel: EP en Alternate niet.
iw = bf.index_per_winkel({1: {'coolblue': r, 'ep': r, 'alternate': r}}, [D(2026, 7, 16)])
check('ep en alternate niet per winkel', [x['winkel'] for x in iw] == ['coolblue'], iw)

# 11. Voorbeelden: alleen apparaten met twee winkels, één per categorie.
info2 = {1: ('Wasmachines', 'A', '1'), 2: ('Wasmachines', 'B', '2'), 3: ('Drogers', 'C', '3')}
v = bf.voorbeelden({1: {'coolblue': r, 'bol': r2}, 2: {'coolblue': r, 'bol': r},
                    3: {'coolblue': r}}, info2, D(2026, 7, 16))
check('voorbeelden: één per categorie, minstens twee winkels',
      [x['ean'] for x in v] == ['2'], [x['ean'] for x in v])

# 12. Voorbeelden: een reeks die bijna elke dag wijzigt (Bol-ruis) valt af.
from datetime import timedelta
ruis = [(D(2026, 7, 14) + timedelta(days=d), 400.0 + (d % 2) * 50) for d in range(80)]
v2 = bf.voorbeelden({1: {'coolblue': r, 'bol': ruis}, 2: {'coolblue': r, 'mediamarkt': r2}},
                    {1: ('Wasmachines', 'A', '1'), 2: ('Drogers', 'B', '2')}, D(2026, 7, 16))
check('voorbeelden: ruisreeks valt af', [x['ean'] for x in v2] == ['2'], [x['ean'] for x in v2])

# 13. Mand zonder ruis: de ruisreeks valt af en wordt per winkel geteld.
weg = {}
m2 = bf.maak_mand({(1, 'coolblue'): r, (1, 'bol'): ruis}, {(1, 'coolblue'), (1, 'bol')},
                  D(2026, 7, 16), nu=D(2026, 10, 3), weggelaten=weg)
check('mand: ruisreeks weg, telling per winkel', list(m2[1]) == ['coolblue'] and weg == {'bol': 1},
      (list(m2[1]), weg))
check('mand zonder nu: alles blijft (oud gedrag)',
      len(bf.maak_mand({(1, 'bol'): ruis}, {(1, 'bol')}, D(2026, 7, 16))[1]) == 1)

print()
print('ALLES GOED' if not fouten else f'{fouten} FOUT(EN)')
sys.exit(1 if fouten else 0)
