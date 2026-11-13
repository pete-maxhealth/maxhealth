"""Persona 483 (v3.10.1401): the goal start pages (start/*.html, built by tools/build_start_pages.py) are consistent with the app and safe to publish.
Every page's start value is one the app understands and its demo is a real persona; the QR code decodes to exactly that start link; every local link
resolves; nothing links to Premium or names a real condition of the developer; no sideways scroll at phone width; QR hidden on a phone and shown on a PC;
the landing page tiles match the config. Needs no server. Invented data only."""
import sys, re, os, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import Findings
from playwright.sync_api import sync_playwright
import cv2
f = Findings()
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
app = open(os.path.join(R, 'maxhealth.html'), encoding='utf-8').read()
cfg = json.load(open(os.path.join(R, 'start', 'pages.json'), encoding='utf-8'))
links = re.search(r'const MH_START_LINKS = \{(.*?)\};', app, re.S).group(1)
known_start = set(re.findall(r'(\w+):\s*\{ c:', links)); personas = set(re.findall(r"\n    id: '(\w+)', name: '", app))
land = open(os.path.join(R, 'index.html'), encoding='utf-8').read()
with sync_playwright() as pw:
    b = pw.chromium.launch(); desk = b.new_context(viewport={'width': 1000, 'height': 900}, device_scale_factor=2).new_page()
    phone = b.new_context(viewport={'width': 390, 'height': 844}).new_page()
    for p in cfg['pages']:
        fn = os.path.join(R, 'start', p['slug'] + '.html'); t = open(fn, encoding='utf-8').read(); tag = p['slug']
        p['start'] in known_start or f.add('FAIL', f'{tag}: start={p["start"]} is not a start link the app knows {known_start}')
        p['demo'] in personas or f.add('FAIL', f'{tag}: demo={p["demo"]} is not a demo persona')
        f'maxhealth.html?start={p["start"]}' in t and f'maxhealth.html?demo={p["demo"]}' in t or f.add('FAIL', f'{tag}: the page does not link to its own start and demo')
        re.search(r'tally\.so|premium', t, re.I) and f.add('FAIL', f'{tag}: links or mentions Premium')
        re.search(r'GBM|glioblastoma|tumou?r', t, re.I) and f.add('FAIL', f'{tag}: names a condition it should not')
        'not a medical device' in t or f.add('FAIL', f'{tag}: no medical-device line')
        for h in re.findall(r'href="([^"#?]+)', t):
            if h.startswith(('http', 'mailto')): continue
            os.path.exists(os.path.normpath(os.path.join(R, 'start', h))) or f.add('FAIL', f'{tag}: broken link {h}')
        if p['slug'] not in land: f.add('FAIL', f'{tag}: not on the landing page tiles')
        desk.goto('file://' + os.path.abspath(fn)); desk.wait_for_timeout(200)
        el = desk.locator('.qrbox svg'); el.is_visible() or f.add('FAIL', f'{tag}: QR not shown on a PC')
        el.screenshot(path='/tmp/p483_qr.png'); got = cv2.QRCodeDetector().detectAndDecode(cv2.imread('/tmp/p483_qr.png'))[0]
        want = cfg['base'] + 'maxhealth.html?start=' + p['start']
        got == want or f.add('FAIL', f'{tag}: QR decodes to {got!r}, wanted {want!r}')
        phone.goto('file://' + os.path.abspath(fn)); phone.wait_for_timeout(200)
        phone.evaluate('document.documentElement.scrollWidth > innerWidth + 1') and f.add('FAIL', f'{tag}: scrolls sideways on a phone')
        phone.locator('.qrbox').is_visible() and f.add('FAIL', f'{tag}: QR box shown on a phone')
        phone.locator('.ondesk').first.is_visible() and f.add('FAIL', f'{tag}: the "scan this code" step shown on a phone')
    for pg, u in ((phone, 'start/index.html'), (phone, 'index.html')):
        pg.goto('file://' + os.path.abspath(os.path.join(R, u))); pg.wait_for_timeout(300)
        pg.evaluate('document.documentElement.scrollWidth > innerWidth + 1') and f.add('FAIL', f'{u}: scrolls sideways on a phone')
    b.close()
len(re.findall(r'<a href="start/(?!index)', land)) == len(cfg['pages']) or f.add('FAIL', 'landing tiles do not match the pages')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
