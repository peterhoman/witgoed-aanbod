"""Witgoedhuis-feed lezen (sync_witgoedhuis.py) en de Daisycon-klikreferentie.
Draaien: python test_witgoedhuis.py
"""
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0, '.')

from affiliate_ref import voeg_clickref_toe
from sync_witgoedhuis import _record, _winkeladres

fouten = 0

def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)

LINK = ('https://ds1.nl/c/?si=6570&li=1483214&wi=428244&pid=abc'
        '&dl=wasmachines%2Fbosch-wgg04409nl.html')

def product(**velden):
    basis = {'ean': '4242005254590', 'price': '549.00', 'price_old': '649.00',
             'price_shipping': '0', 'in_stock': 'true', 'condition': 'new', 'link': LINK}
    basis.update(velden)
    xml = '<product_info>' + ''.join(f'<{k}>{v}</{k}>' for k, v in basis.items() if v is not None)
    xml += '<images><image><location>https://witgoedhuis.nl/foto.jpg</location></image></images>'
    return ET.fromstring((xml + '</product_info>').replace('&', '&amp;'))

uit = _record(product())
check('gewoon product wordt gelezen', uit is not None)
if uit:
    sleutel, r = uit
    check('prijs', r['price'] == 549.0)
    check('van-prijs alleen als hoger', r['strikethrough_price'] == 649.0)
    check('bezorgkosten 0 = gratis', r['delivery_cost'] == 0.0)
    check('winkeladres uit dl', r['url'] == 'https://www.witgoedhuis.nl/wasmachines/bosch-wgg04409nl.html', r['url'])
    check('trackinglink met ws=EAN', 'ds1.nl' in r['affiliate_url'] and 'ws=4242005254590' in r['affiliate_url'],
          r['affiliate_url'])
    check('foto', r['image_url'] == 'https://witgoedhuis.nl/foto.jpg')
check('tweedehands valt af', _record(product(condition='used')) is None)
check('refurbished valt af', _record(product(condition='refurbished')) is None)
check('niet op voorraad valt af', _record(product(in_stock='false')) is None)
check('zonder EAN valt af', _record(product(ean='')) is None)
check('zonder prijs valt af', _record(product(price='')) is None)
check('van-prijs gelijk aan prijs telt niet', _record(product(price_old='549.00'))[1]['strikethrough_price'] is None)
check('geen dl: geen winkeladres', _winkeladres('https://ds1.nl/c/?si=6570&li=1') is None)
check('Daisycon-klikreferentie alleen op ds1.nl',
      voeg_clickref_toe('https://example.com/x', 'daisycon', '123') == 'https://example.com/x')
check('bestaande Awin-klikreferentie ongewijzigd',
      'clickref=123' in voeg_clickref_toe('https://www.awin1.com/pclick.php?p=1', 'awin', '123'))

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
