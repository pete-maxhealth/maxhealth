"""Persona 42: the app page never sends Clear-Site-Data (one shipped briefly on 6 Oct and the app stuck on its splash screen; 'storage'/'cookies' would also wipe the user's data)."""
import sys, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
with fresh_server() as root:
    for path in ('/', '/maxhealth'):
        r = urllib.request.urlopen('http://localhost:5757' + path)
        h = r.headers.get('Clear-Site-Data', '')
        if h: f.add('BUG', f'{path}: Clear-Site-Data header {h!r} must not be sent')
        if 'no-store' not in (r.headers.get('Cache-Control') or ''): f.add('BUG', f'{path}: lost no-store')
    r = urllib.request.urlopen('http://localhost:5757/last-hits'); 
    if b'hits' not in r.read(): f.add('BUG', '/last-hits missing')
print('findings', len(f)); sys.exit(1 if f else 0)
