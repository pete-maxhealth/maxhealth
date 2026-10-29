"""Persona 354 (v3.10.1245): the photo preview tells you that naming your plate or bowl lets the AI use its size, uses your own item's name as the example,
and tapping the line opens Tableware settings. Generic wording when there is no custom tableware; follows the set in use. Invented item names."""
import sys, re, base64, os, tempfile; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
png = os.path.join(tempfile.gettempdir(), 'p354.png')
open(png, 'wb').write(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='))
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(500)
    # any AI call must not leave the page
    ev("window.callHealthAI=async()=>'{}'; 0")
    p.set_input_files('#photoInput', png); p.wait_for_timeout(1500)
    if not ev("document.getElementById('photoPreviewWrap').offsetParent!==null"): f.add('BUG', '1: photo preview not shown')
    t = ev("document.getElementById('mhTwPhotoNote').textContent")
    if 'Name your plate or bowl' not in t or 'Home' not in t: f.add('BUG', f'2: generic hint with the set in use: {t}')
    if 'e.g.' in t: f.add('BUG', '3: no example without custom tableware')
    # custom item becomes the example
    ev("""(()=>{const s=JSON.parse(localStorage.getItem('mh_tableware')||'null')||{activeId:'home',revertOn:null,sets:[{id:'home',name:'Home',vals:{}}],custom:[]};
      s.custom=[{id:'c_zed',name:'Zed blue bowl',icon:'🥣',kind:'bowl',diam:16,cap:400,wt:null}]; localStorage.setItem('mh_tableware',JSON.stringify(s)); mhTwUse('home');})()""")
    p.wait_for_timeout(400)
    t = ev("document.getElementById('mhTwPhotoNote').textContent")
    if 'in the zed blue bowl' not in t: f.add('BUG', f'4: example uses the custom item name: {t}')
    # the AI prompt really does carry that item (so naming it works)
    if 'zed blue bowl' not in ev("mhTablewareLine()"): f.add('BUG', '5: the prompt includes the custom item')
    # tap opens settings on the tableware card
    p.locator('#mhTwPhotoNote').click(); p.wait_for_timeout(900)
    if not ev("(()=>{const e=document.getElementById('set-tableware-wrap');return !!e&&e.offsetParent!==null})()"): f.add('BUG', '6: tapping the line opens Tableware settings')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
