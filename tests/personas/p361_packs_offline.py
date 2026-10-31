"""Persona 361 (v3.10.1251): starter packs load with NO internet. Every request to anything but the app's own server is refused; the "What are you tracking now?" picker still lists every shipped pack, a pack
opens to its preview, the Starter packs screen lists and opens one, a Spanish language file loads, and nothing at all was requested from GitHub. The server serves only plain .json files from starter_packs/
(a missing name and a path trying to reach another file both answer 404 and give nothing away). Invented data."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); R = '/home/claude/maxhealth/'
shipped = json.load(open(R + 'starter_packs/index.json'))['packs']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; ext = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
    def route(r):
        u = r.request.url
        if u.startswith('http://localhost'): r.continue_()
        else: ext.append(u); r.abort()
    ctx.route('**/*', route)
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.accept()); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(2000)
    # the app's own server
    r = ev("(async()=>{const o={}; for (const n of ['index.json','epilepsy_tracking.json','nope.json','..%2fserver.py','server.py','index.json%00.txt']) { try { const x = await fetch('/starter_packs/'+n); o[n]=[x.status, (await x.text()).slice(0,60)] } catch(e){ o[n]=['err'] } } return o})()")
    if r['index.json'][0] != 200 or r['epilepsy_tracking.json'][0] != 200: f.add('BUG', f'1: the server serves index.json and a pack: {r}')
    for n in ('nope.json', '..%2fserver.py', 'server.py', 'index.json%00.txt'):
        if r[n][0] != 404 or 'import' in r[n][1] or 'def ' in r[n][1]: f.add('BUG', f'2: {n} must answer 404 and leak nothing: {r[n]}')
    # picker lists every shipped pack with no internet
    ev("mhFocusOpen()"); p.wait_for_timeout(1200)
    n = ev("document.querySelectorAll('#mhFocusBody button[data-f]').length")
    if n != len(shipped) + 1: f.add('BUG', f'3: the picker lists "everything" plus all {len(shipped)} packs offline, got {n}')
    ev("document.querySelectorAll('#mhFocusBody button[data-f]')[1].click()"); p.wait_for_timeout(900)
    t = ev("document.body.innerText")
    if "Couldn't open" in t: f.add('BUG', '4: a pack opens to its preview offline')
    ev("document.querySelectorAll('[id^=mhFocus]').forEach(e=>e.id!=='mhFocusBody'&&e.remove()); 0")
    # Starter packs screen
    ev("mhStarterPacks(); 0"); p.wait_for_timeout(1200)
    t = ev("(document.getElementById('mhPackModal')||document.body).innerText")
    if "Couldn't reach" in t or shipped[0]['title'] not in t: f.add('BUG', f'5: the Starter packs screen lists the packs offline: {t[:120]!r}')
    # language
    d = ev("(async()=>{const x = await mhLangLoad('es'); return x ? Object.keys(x).length : 0})()")
    if d < 20: f.add('BUG', f'6: a language file loads offline: {d}')
    gh = [u for u in ext if 'github' in u]
    if gh: f.add('BUG', f'7: nothing requested from GitHub: {gh[:3]}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
