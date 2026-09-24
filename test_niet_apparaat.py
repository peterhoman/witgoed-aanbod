"""Opruimregel voor niet-apparaten (catalogus_uitzonderingen.is_geen_apparaat).

Titels zijn letterlijk van de live site (24 september 2026). Draaien:
python test_niet_apparaat.py
"""
import sys
sys.path.insert(0, '.')
from catalogus_uitzonderingen import is_geen_apparaat

WEG = [  # moeten van de site
    'GreenChef Diamond Hapjespan 28cm met deksel - 4.25L - PFAS-vrije antikleeflaag - Hapjespan inductie - Keramische pan - Ovenbestendig tot 160°C - Koelgreep - Glazen deksel - Zwart',
    'GreenPan Cambridge Hapjespan 28cm met deksel - 4.2L - PFAS-vrije antikleeflaag',
    'BK Profiline soeppan 24cm - 6l - RVS - PFAS-vrij',
    '3 x NIVEA MEN – Gezichtscrème – Sensitive, Gevoelige huid, SPF30 – 50 ml - Koffie - Koffiezetapparaat - Koffiezetapparaat',
    'Demeyere Alu Pro 5 Ceraforce wok - 30 cm',
    'Philips Sonicare opzetborstels 8 stuks',
    'Tefal Ingenio pannenset 10-delig - inductie',
]
BLIJFT = [  # echte apparaten, ook met een lastig woord erin
    'Ninja CRISPi 4-in-1 compact glazen kooksysteem - Airfryer, Roast, Recrisp, Keep Warm',
    'Bosch SMV4ECX30E vaatwasser met bestekkorf - inbouw',
    'Siemens LC65KDK60 - IQ100 - Afzuigkap met geurfilter',
    'Miele W1 WEB 368 PowerWash wasmachine 8 kg',
    'Bosch HSG7361B1 Serie 8 - Inbouwoven - Stoomoven',
    'Smeg EGF03CREU creme koffiemolen',
    'Philips 1000 serie stofzuiger met zak - 750 W',
    'De\'Longhi Magnifica Evo - volautomatische espressomachine',
]
fouten = 0
for t in WEG:
    ok = is_geen_apparaat(t); print(('OK   ' if ok else 'FOUT ') + 'weg:   ' + t[:70]); fouten += (not ok)
for t in BLIJFT:
    ok = not is_geen_apparaat(t); print(('OK   ' if ok else 'FOUT ') + 'blijft: ' + t[:70]); fouten += (not ok)
print(f"\n{len(WEG) + len(BLIJFT)} gevallen, {fouten} fout")
sys.exit(1 if fouten else 0)
