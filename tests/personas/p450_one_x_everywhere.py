"""Persona 450: every ✕ in the app is the same ✕ (one glyph, one of two classes: .mh-x inline remove/clear/dismiss, .mh-x-close round close for a whole screen), same size and colour; none is a different × or a hand-styled box (v3.10.1367). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SCAN = """() => [...document.querySelectorAll('body *')].filter(e => !e.children.length && /^\\s*[✕×✖✗]\\s*$/.test(e.textContent) && e.offsetParent !== null).map(e => { const c = getComputedStyle(e); return { cls: e.className || '', tag: e.tagName, txt: e.textContent.trim(), fs: c.fontSize, col: c.color, bg: c.backgroundColor, w: Math.round(e.getBoundingClientRect().width), h: Math.round(e.getBoundingClientRect().height), where: (e.closest('[id]')||{}).id || '' } })"""
seen = []
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("['Whole Milk','Eggs'].forEach(n=>{mhStockTrack(n,{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey(n),500)}); mhShopAddShopNamed('Aldi'); mhShopSetShop('Asda')")
    def scan(name):
        for r in ev(SCAN): r['screen'] = name; seen.append(r)
    for name, js in [('shop both', "localStorage.setItem('mh_shop_pane','both'); switchTabById('shop')"), ('shop stocklist', "mhShopView('stocklist')"), ('stock edit', "mhStockEditView(mhShopKey('Eggs'))"), ('shop usuals', "mhShopView('usuals')"),
                     ('log', "switchTab('log')"), ('food search', "openFoodSearch()"), ('library', "closeFoodSearch(); switchTab('log'); switchSubTab('log','library')"), ('history', "switchSubTab('log','history')"),
                     ('today', "switchTab('today')"), ('insights', "switchTab('insights')"), ('statistics', "switchSubTab('insights','statistics')"), ('settings', "switchTab('settings')")]:
        try: ev(js); page.wait_for_timeout(500); scan(name)
        except Exception as e: f.add('BUG', f'0: {name}: {str(e)[:100]}')
    if len(seen) < 3: f.add('BUG', f'1: expected several ✕ on these screens, found {len(seen)}')
    for r in seen:
        c = r['cls'].split() if isinstance(r['cls'], str) else []
        if r['txt'] != '✕': f.add('BUG', f"2: {r['screen']}: a '{r['txt']}' instead of ✕ ({r['cls']})")
        if 'mh-x' not in c and 'mh-x-close' not in c: f.add('BUG', f"3: {r['screen']}: ✕ without the standard class ({r['cls']!r}, {r['tag']})")
        if 'mh-x' in c and (r['fs'] != '16px' or r['w'] < 28 or r['h'] < 28): f.add('BUG', f"4: {r['screen']}: inline ✕ not 16px / 28px tap: {r['fs']} {r['w']}x{r['h']}")
        if 'mh-x-close' in c and (r['fs'] != '18px' or r['w'] != 36 or r['h'] != 36): f.add('BUG', f"5: {r['screen']}: round close not 18px / 36px: {r['fs']} {r['w']}x{r['h']}")
    cols = {r['col'] for r in seen if 'mh-x' in r['cls'].split()}
    if len(cols) > 1: f.add('BUG', f'6: inline ✕ in more than one colour: {cols}')
    # the ✕ still works: a shop's ✕ hides it, the food-search ✕ closes the search
    ev("localStorage.setItem('mh_shop_pane','both'); switchTabById('shop')"); page.wait_for_timeout(500)
    if page.locator('#mhShopPane [data-hideshop="Aldi"]').count(): page.locator('#mhShopPane [data-hideshop="Aldi"]').first.click(timeout=5000); page.wait_for_timeout(400)
    if page.locator('#mhShopPane [data-hideshop="Aldi"]').count(): f.add('BUG', '7: the shop ✕ did not hide the shop')
    ev("openFoodSearch()"); page.wait_for_timeout(400); page.locator('.mh-x-close').first.click(timeout=5000); page.wait_for_timeout(400)
    if ev("getComputedStyle(document.getElementById('foodSearchOverlay')||document.body).display") == 'flex' and ev("!!document.querySelector('.food-search-overlay.open, #foodSearchOverlay.open')"): f.add('BUG', '8: the search ✕ did not close it')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('seen', len(seen)); print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
