"""Persona 493 (v3.10.1410): Shopping > Add > Non-nutritional shelf rows give the item name room (it was squeezed to one or two letters beside two wide buttons).
At 360, 390 and 430 px every name is fully readable (not clipped by the 2-line limit for short names) and the buttons stay inside the row. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
NAMES = ['Anti-bacterial spray', 'Bin bags', 'Cotton wool pads', 'Fabric softener', 'Fluffy kitchen roll', 'Heavy duty dishwasher tablets']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for w in (360, 390, 430):
        page = b.new_context(viewport={'width': w, 'height': 900}, service_workers='block', device_scale_factor=1).new_page()
        page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
        ev("localStorage.setItem('mh_shop_pane','both')"); ev("mhShopOpen()"); page.wait_for_timeout(300)
        for n in NAMES: ev(f"mhStockTrack({n!r},{{base:'g'}}); (()=>{{const o=mhStockLoad(); o.items[mhShopKey({n!r})].nonFood=true; mhStockSave(o)}})()")
        ev("_shopUi.addOpen=true; mhShopAddKind('nonfood')"); page.wait_for_timeout(400)
        rows = ev("""[...document.querySelectorAll('#mhNfShelf [data-nfshelf]')].map(r=>{const n=r.firstElementChild, rr=r.getBoundingClientRect(), nr=n.getBoundingClientRect();
          const bs=[...r.querySelectorAll('button')].map(x=>x.getBoundingClientRect()); return {name:n.textContent, nameW:Math.round(nr.width), clipped:n.scrollHeight>n.clientHeight+1, lines:Math.round(nr.height/20),
          inside:bs.every(x=>x.left>=rr.left-1&&x.right<=rr.right+1)}})""")
        len(rows) == len(NAMES) or f.add('FAIL', f'{w}px: {len(rows)} shelf rows, expected {len(NAMES)} (nonFood tracking: {rows})')
        for r in rows:
            r['nameW'] >= 120 or f.add('FAIL', f'{w}px: "{r["name"]}" only {r["nameW"]}px wide')
            r['clipped'] and f.add('FAIL', f'{w}px: "{r["name"]}" clipped')
            r['inside'] or f.add('FAIL', f'{w}px: buttons spill out of the row for "{r["name"]}"')
        page.screenshot(path=f'/tmp/claude-0/shelf_{w}.png', clip={'x': 0, 'y': 0, 'width': w, 'height': 900}) if False else None
        ev("document.getElementById('mhNfShelf').scrollIntoView({block:'start'})"); page.wait_for_timeout(200); page.screenshot(path=f'/tmp/claude-0/shelf_{w}.png')
    errs and f.add('FAIL', f'page errors {errs}')
print('findings', len(f))
