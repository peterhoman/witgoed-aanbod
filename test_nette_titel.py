"""Koppen: feedtitels met een hoofdletter per woord worden netjes.

Alle invoer hieronder is letterlijk gemeten op de live site op 22 september
2026 (H1's van productpagina's). Draaien: python test_nette_titel.py
"""
import sys
sys.path.insert(0, '.')

from titel_netjes import nette_titel

GEVALLEN = [
    ("LG Rt90x8 - Warmtepompdroger 9kg 62 Db Energielabel B",
     "LG RT90X8 - Warmtepompdroger 9 kg 62 dB energielabel B"),
    ("Haier Hw90-b14939 I-pro 3 - Wasmachine Voorlader 9 Kg 1400 Rpm 67 Db",
     "Haier HW90-B14939 I-pro 3 - Wasmachine voorlader 9 kg 1400 rpm 67 dB"),
    ("Bosch Kge398ibp - Koel-vriescombinatie Breedte 60 Cm Hoogte 201 Inhoud 375 L",
     "Bosch KGE398IBP - Koel-vriescombinatie breedte 60 cm hoogte 201 inhoud 375 l"),
    ("LG Gsxe90evdd Instaview - Amerikaanse Koelkast Breedte 92.8 Cm",
     "LG GSXE90EVDD Instaview - Amerikaanse koelkast breedte 92.8 cm"),
    ("Siemens Hk9r3a250 - Fornuis Keramisch 3 Phases (perilex)- Breedte 60 Cm",
     "Siemens HK9R3A250 - Fornuis keramisch 3 phases (perilex)- breedte 60 cm"),
    ("Cosori Xxl Dual Basket - Heteluchtfriteuse Zwart 85 Kg 1750 W",
     "Cosori XXL Dual Basket - Heteluchtfriteuse zwart 85 kg 1750 W"),
    ("Samsung Jet™ 95s Pet Vs70h28glt/wa - Steelstofzuiger Accuduur 60 Min",
     "Samsung Jet™ 95s Pet VS70H28GLT/WA - Steelstofzuiger accuduur 60 min"),
    # "muur" staat er in kleine letters, dus dit is geen hoofdletter-per-woord-
    # feed: alleen typenummer en eenheid worden aangeraakt.
    ("Etna Ad690zt  - Afzuigkap (muur Bevestigde Kap) Breedte 89.8 Cm 770 M³",
     "Etna AD690ZT  - Afzuigkap (muur Bevestigde Kap) Breedte 89.8 cm 770 M³"),
    ("OK. Owm 8126 - Wasmachine Voorlader 8 Kg 1400 Rpm 76 Db",
     "OK. Owm 8126 - Wasmachine voorlader 8 kg 1400 rpm 76 dB"),
    # Titels die al goed zijn (Coolblue, Bol) blijven precies zo.
    ("Bosch WGG244FONL - Serie 6 - Wasmachine met stoom - 9 kg",
     "Bosch WGG244FONL - Serie 6 - Wasmachine met stoom - 9 kg"),
    ("Samsung SuperSpeed WW90DG6U25LBU3 - 6000 serie - Wasmachine 9 kg",
     "Samsung SuperSpeed WW90DG6U25LBU3 - 6000 serie - Wasmachine 9 kg"),
    ("AEG TR96CVC810 AbsoluteCare Pro", "AEG TR96CVC810 AbsoluteCare Pro"),
    ("LG F4WR7011S1W wasmachine 11 kg met AI DD voor slimme sensoren",
     "LG F4WR7011S1W wasmachine 11 kg met AI DD voor slimme sensoren"),
    # Gemengde schrijfwijze (kleine letters komen voor): alleen de eenheid
    # wordt aangeraakt, de rest blijft zoals de winkel het schreef.
    ("Inventum VWM1010B Wasmachine - 10kg - 1400 toeren - Energielabel A",
     "Inventum VWM1010B Wasmachine - 10 kg - 1400 toeren - Energielabel A"),
    ("Philips Airfryer met Stoomfunctie 5000-serie – NA541/00 – PFAS vrij",
     "Philips Airfryer met Stoomfunctie 5000-serie – NA541/00 – PFAS vrij"),
    ("Smeg DCF02BLMEU Mat Zwart", "Smeg DCF02BLMEU Mat Zwart"),
    ("Eufy Omni C28 Wit", "Eufy Omni C28 Wit"),
    ("Ninja Dubbele Airfryer XXL - 7.6 Liter - 2020 Model - Dual Zone Technologie - AF300EU",
     "Ninja dubbele airfryer XXL - 7.6 liter - 2020 model - Dual Zone Technologie - AF300EU"),
    ("Miele Wwd 380 Wcs Powerwash - Wasmachine Voorlader 9 Kg 1400 Rpm 72 Db",
     "Miele Wwd 380 Wcs Powerwash - Wasmachine voorlader 9 kg 1400 rpm 72 dB"),
    ("", ""),
    (None, ""),
]

fouten = 0
for invoer, verwacht in GEVALLEN:
    uit = nette_titel(invoer)
    ok = uit == verwacht
    print(("OK   " if ok else "FOUT ") + repr(uit))
    if not ok:
        fouten += 1
        print("   verwacht:", repr(verwacht))
print(f"\n{len(GEVALLEN)} gevallen, {fouten} fout")
sys.exit(1 if fouten else 0)
