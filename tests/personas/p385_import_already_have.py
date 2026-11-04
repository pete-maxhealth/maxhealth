"""Persona 385: CSV and receipt review rows say when a new-looking food is close to one already held (v3.10.1273).
Pete (4 Nov): duplicates should be checked on every add route. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("mhStockTrack('Zzqx Beef Stock Cubes',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Beef Stock Cubes'),60)")
    ev("(()=>{const o=mhStockLoad(), k=mhShopKey('Zzqx Beef Stock Cubes'); o.items[k].held=true; mhStockSave(o)})()")
    ev("mhShopCsvLoad('item,qty\\nZzqx Beef Stock Cubes Gold,1\\nQqvv Plain Oddity,1\\n','t.csv')"); page.wait_for_timeout(400)
    ev("_shopUi.csv.rows.forEach(r=>{r.asked=true})"); ev("mhShopRender()"); page.wait_for_timeout(300)
    n = ev("document.querySelectorAll('.mh-have-note').length"); t = ev("document.body.innerText")
    if n != 1 or 'in Filtered' not in t: f.add('BUG', f'1: CSV row near a Filtered food gets one note naming Filtered: n={n}')
    page.screenshot(path='/tmp/p385.png')
    if 'Qqvv Plain Oddity' not in t: f.add('BUG', '2: unrelated row still listed')
    row = ev("[...document.querySelectorAll('[data-csv]')].map(e=>e.dataset.csv+'|'+!!e.querySelector('.mh-have-note'))")
    if 'Qqvv Plain Oddity|true' in row: f.add('BUG', f'3: no note on an unrelated row: {row}')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
