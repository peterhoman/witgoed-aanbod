"""Taalknop weg (14 okt 2026): geen link naar /set-language meer, de site is
altijd Nederlands, ook met een oud 'en'-cookie, en de route ruimt dat cookie
op. Tijdelijke sqlite-database. Draaien: python test_taalknop_weg.py
"""
import os
import sys
import tempfile
sys.path.insert(0, '.')

pad = os.path.join(tempfile.mkdtemp(), 'taal_test.db')
os.environ['DATABASE_URL'] = 'sqlite:///' + pad.replace('\\', '/')

from app import create_app  # noqa: E402

fouten = 0


def check(naam, ok, extra=''):
    global fouten
    print(('OK   ' if ok else 'FOUT ') + naam + (f'  ({extra})' if extra and not ok else ''))
    fouten += (not ok)


app = create_app('development')
c = app.test_client()
c.set_cookie('lang', 'en')
for pad in ('/', '/over-ons', '/cookies'):
    r = c.get(pad)
    h = r.get_data(as_text=True)
    if r.status_code != 200:
        check(f'{pad} geeft 200', False, r.status_code)
        continue
    check(f'{pad}: geen link naar /set-language', '/set-language' not in h)
    check(f'{pad}: Nederlands ondanks en-cookie', 'lang="nl"' in h and 'Cookie Policy' not in h)

r = c.get('/set-language/en', headers={'Referer': 'http://localhost/over-ons'})
cookies = ' '.join(r.headers.getlist('Set-Cookie'))
check('oude route stuurt terug', r.status_code == 302 and r.headers.get('Location', '').endswith('/over-ons'),
      (r.status_code, r.headers.get('Location')))
check('oude route ruimt het taalcookie op', 'lang=;' in cookies and 'lang=en' not in cookies, cookies)

print(f'\n{fouten} fout')
sys.exit(1 if fouten else 0)
