"""Draait alle test_*.py in de projectmap en geeft per bestand de uitkomst.
Draaien: python scripts/alle_tests.py
"""
import glob
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
mislukt = []
for bestand in sorted(glob.glob('test_*.py')):
    r = subprocess.run([sys.executable, bestand], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=600)
    regels = [x for x in (r.stdout + r.stderr).splitlines() if x.startswith('FOUT')]
    status = 'goed' if r.returncode == 0 else 'MISLUKT'
    print(f'{bestand:34} {status}' + (f'  {regels[:3]}' if regels else ''))
    if r.returncode != 0:
        mislukt.append(bestand)
        if not regels:
            print('   ', (r.stdout + r.stderr).strip().splitlines()[-3:])
print('\nALLES GOED' if not mislukt else f'\n{len(mislukt)} MISLUKT: {mislukt}')
