"""Meta-omschrijvingen mogen niet midden in een woord eindigen.

Gemeten 22 september op productie: 11 van 60 categorie-, merk- en
filterpagina's eindigden op "... MediaMarkt, Coolblu" of "... Voordeligwitgo",
omdat de opsomming van zeven winkels de tekst over de 160 tekens duwde en er
een kale [:160] stond. Draaien: python test_meta_kort.py
"""
import sys
sys.path.insert(0, '.')

from routes.main import _meta_kort

GEVALLEN = [
    # (invoer, verwachte uitkomst)
    ("Kort genoeg.", "Kort genoeg."),
    # De echte tekst van /category/wasmachines op 22 september (200 tekens).
    ("Vergelijk 216 wasmachines op prijs en specificaties van o.a. Miele, "
     "Samsung, Hisense al vanaf € 259. Vind de laagste prijs bij o.a. Bol.com, "
     "MediaMarkt, Coolblue, Expert, Alternate, EP en Voordeligwitgoed.",
     "Vergelijk 216 wasmachines op prijs en specificaties van o.a. Miele, "
     "Samsung, Hisense al vanaf € 259. Vind de laagste prijs bij o.a. Bol.com, "
     "MediaMarkt."),
    # Merkpagina: "... Alternate, EP en Voordeligwitgo" mag niet; ook geen los "en".
    ("Vergelijk 3 AEG wasdroogcombinaties op prijs. Bekijk actuele prijzen en "
     "prijsverloop bij Bol.com, MediaMarkt, Coolblue, Expert, Alternate, EP en "
     "Voordeligwitgoed.",
     "Vergelijk 3 AEG wasdroogcombinaties op prijs. Bekijk actuele prijzen en "
     "prijsverloop bij Bol.com, MediaMarkt, Coolblue, Expert, Alternate, EP."),
    # Dubbele spaties en regeleinden worden één spatie.
    ("Twee  woorden\nop  een rij.", "Twee woorden op een rij."),
]

fouten = 0
for invoer, verwacht in GEVALLEN:
    uit = _meta_kort(invoer)
    ok = (uit == verwacht and len(uit) <= 160 and uit.endswith('.')
          and not uit.endswith((' en.', ' bij.', ' o.a..')))
    print(("OK   " if ok else "FOUT ") + repr(uit))
    if not ok:
        fouten += 1
        print("   verwacht:", repr(verwacht))

# De uitkomst mag nooit langer zijn dan 160 en nooit een afgebroken woord bevatten.
lang = "woord " * 60
uit = _meta_kort(lang)
assert len(uit) <= 160 and uit.endswith("woord."), uit

print(f"\n{len(GEVALLEN)} gevallen, {fouten} fout")
sys.exit(1 if fouten else 0)
