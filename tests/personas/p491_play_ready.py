"""Persona 491 (v3.10.1409): the web app is ready to be wrapped for Google Play: manifest has identity, scope covers the start page, separate 'any' and
'maskable' icons (maskable ones full-bleed, no transparent corners), no 'medical' category; the wrapper settings match the manifest and the live addresses; the
package name is the agreed one. No browser needed."""
import sys, json, os; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import Findings
from PIL import Image
f = Findings(); root = os.path.join(os.path.dirname(__file__), '..', '..')
m = json.load(open(os.path.join(root, 'manifest.json'))); t = json.load(open(os.path.join(root, 'android', 'twa-manifest.json')))
m.get('id') == m.get('start_url') or f.add('FAIL', 'manifest id should equal start_url so existing installs keep their identity')
m['start_url'].startswith(m['scope']) or f.add('FAIL', 'start_url outside scope')
'medical' not in m.get('categories', []) or f.add('FAIL', 'medical category would read as a medical-device claim to Play')
purp = {}
for i in m['icons']:
    for p in (i.get('purpose') or 'any').split(): purp.setdefault(p, []).append(i['sizes'])
for need in ('any', 'maskable'):
    ('192x192' in purp.get(need, []) and '512x512' in purp.get(need, [])) or f.add('FAIL', f'{need} icons need 192 and 512: {purp.get(need)}')
for i in m['icons']:
    if 'any' in (i.get('purpose') or 'any').split() and 'maskable' in (i.get('purpose') or '').split(): f.add('FAIL', 'icon marked both any and maskable')
    fp = os.path.join(root, i['src'].replace('/maxhealth/', '', 1)); os.path.exists(fp) or f.add('FAIL', 'missing ' + fp)
    if os.path.exists(fp):
        im = Image.open(fp).convert('RGBA'); w, h = im.size; f'{w}x{h}' == i['sizes'] or f.add('FAIL', f'{fp} is {w}x{h}, manifest says {i["sizes"]}')
        if 'maskable' in (i.get('purpose') or '').split():
            a = [im.getpixel(p)[3] for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
            all(x == 255 for x in a) or f.add('FAIL', f'maskable icon {fp} has transparent corners')
t['packageId'] == 'uk.co.pspence.maxedhealth' or f.add('FAIL', 'package name changed (it is permanent once on Play)')
base = 'https://' + t['host']
t['webManifestUrl'] == base + '/maxhealth/manifest.json' and t['fullScopeUrl'] == base + m['scope'] or f.add('FAIL', 'wrapper addresses do not match the manifest')
t['startUrl'].split('?')[0] == m['start_url'] and t['startUrl'].endswith('?src=play') or f.add('FAIL', 'wrapper start url must be the manifest start page with ?src=play (hides Premium)')
t['themeColor'] == m['theme_color'] and t['backgroundColor'] == m['background_color'] or f.add('FAIL', 'colours differ from the manifest')
t['iconUrl'].endswith('/icons/icon-512.png') and t['maskableIconUrl'].endswith('/icons/icon-maskable-512.png') or f.add('FAIL', 'wrapper icon urls')
t['enableNotifications'] is False or f.add('FAIL', 'notifications should stay off (nothing in the app sends them)')
print('findings', len(f))
