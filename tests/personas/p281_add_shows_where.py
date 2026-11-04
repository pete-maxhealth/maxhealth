"""Persona 281: adding an item to the list leaves every aisle as it was (v3.10.1263, was: opened its aisle, v3.10.1178) and says which aisle it went into, also when it is already there. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Spinach','own','',null); mhShopSave(s)")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    rows = "[...document.querySelectorAll('#mhShopPane [data-item]')].map(e=>e.dataset.item)"
    if ev(rows): f.add('BUG', f'aisles start closed: {ev(rows)}')
    ev("_shopUi.addOpen = true; mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    page.fill('#mhShopOwn', 'Zzqx Washing up liquid'); ev("mhShopAddOwn()"); page.wait_for_timeout(600)
    if ev(rows): f.add('BUG', f'adding does not open an aisle: {ev(rows)}')
    if not ev("mhShopLoad().items.some(i=>i.name==='Zzqx Washing up liquid')"): f.add('BUG', 'the item is on the list')
    msg = ev("document.getElementById('mhShopPane').innerText")
    if 'Added Zzqx Washing up liquid to your Asda list (Non-nutritional)' not in msg: f.add('BUG', f'the message says where it went: {msg[:200]!r}')
    # again: already there, still shown, and the message says so
    ev("mhShopFoldSave(); _shopUi.fold = {}; mhShopRender()"); page.wait_for_timeout(300)
    ev("mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    page.fill('#mhShopOwn', 'zzqx washing up liquid'); ev("mhShopAddOwn()"); page.wait_for_timeout(600)
    if ev(rows): f.add('BUG', 'adding it again does not open an aisle')
    if 'is already on your Asda list' not in ev("document.getElementById('mhShopPane').innerText"): f.add('BUG', 'adding it again says it is already there, and where')
    if ev("mhShopLoad().items.filter(i=>/washing up liquid/i.test(i.name)).length") != 1: f.add('BUG', 'no duplicate is made')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
