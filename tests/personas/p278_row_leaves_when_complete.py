"""Persona 278: in Needs details a food drops off the list once it is complete, and the bar stays small so Tick all shown works (v3.10.1173). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{['Zzqx Alpha','Zzqx Beta','Zzqx Gamma'].forEach(n=>mhStockTrack(n,{base:'g',shop:'Asda'}));})()""")
    ev("switchTabById('shop')"); ev("mhSlOpen()"); page.wait_for_timeout(400)
    ev("mhSlState().f='gaps'; mhShopRender()"); page.wait_for_timeout(300)
    rows = "document.querySelectorAll('#mhSlRows [data-sl]').length"
    if ev(rows) != 3: f.add('BUG', f'three foods need details: {ev(rows)}')
    # a bar that stays small
    page.click('button:has-text("Tick all shown")'); page.wait_for_timeout(300)
    if ev("mhSlTickedRows().length") != 3: f.add('BUG', 'Tick all shown ticks all three')
    hgt = ev("document.getElementById('mhSlBulk').offsetHeight")
    if hgt > 150: f.add('BUG', f'the bar stays small: {hgt}px')
    ev("mhSlPickAll(false)"); page.wait_for_timeout(200)
    # complete one food: it leaves
    k = ev("mhShopKey('Zzqx Alpha')"); sel = '[data-sl="%s"]' % k
    for fld, val in (('amt', '300'), ('thr', '100'), ('serv', '50')):
        page.fill(sel + ' [data-f="%s"]' % fld, val); page.dispatch_event(sel + ' [data-f="%s"]' % fld, 'change'); page.wait_for_timeout(250)
        if fld != 'serv' and not ev("!!document.querySelector('%s')" % sel): f.add('BUG', f'it stays until complete (after {fld})')
    page.wait_for_timeout(1100)
    if ev("!!document.querySelector('%s')" % sel): f.add('BUG', 'a complete food leaves the Needs details list')
    if ev(rows) != 2: f.add('BUG', f'two foods are left: {ev(rows)}')
    if '2 shown' not in page.inner_text('#mhSlShownN'): f.add('BUG', 'the shown count updates')
    if 'Needs details (2)' not in page.inner_text('button:has-text("Needs details")'): f.add('BUG', 'the chip count updates')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
