"""Zoekt dubbele sleutels in TEKSTEN (subpagina_teksten.py): bij een dict wint
stilzwijgend de laatste, dus een dubbele sleutel gooit tekst weg.
Draaien: python scripts/dubbele_teksten.py
"""
import ast
from collections import Counter

boom = ast.parse(open('subpagina_teksten.py', encoding='utf-8').read())
for knoop in ast.walk(boom):
    if isinstance(knoop, ast.Assign) and getattr(knoop.targets[0], 'id', '') == 'TEKSTEN':
        sleutels = [ast.literal_eval(k) for k in knoop.value.keys]
        dubbel = [k for k, n in Counter(sleutels).items() if n > 1]
        print(len(sleutels), 'teksten; dubbel:', dubbel or 'geen')
