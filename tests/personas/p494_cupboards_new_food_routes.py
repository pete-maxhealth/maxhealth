"""Persona 494 (v3.10.1411): typing a brand-new food in My cupboards (search box, and the Add a food screen) offers the same routes as Log: search online, AI,
barcode, label photo; typing stays as the last resort. A route opens the Log-style panel as a library-only save; saving continues into the cupboards for that food.
Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','both')"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("mhStockTrack('Zzqx Cheese',{base:'g'})"); ev("mhShopRender()"); page.wait_for_timeout(200)
    def probe():
        return ev("""(()=>{const r=document.querySelector('[data-newroutes]'); if(!r) return null; const b=[...r.querySelectorAll('button')].map(x=>x.textContent.trim());
          return {b, typed: !!document.querySelector('[data-add-food],#mhStockTypedNew')}})()""")
    ev("mhCbQ('Wholemeal wraps')"); page.wait_for_timeout(300)
    p = probe(); p or f.add('FAIL', 'cupboards search: no new-food routes shown')
    if p:
        for need in ('Search online', 'Try AI', 'Scan barcode', 'Read a label', 'Enter manually'):
            any(need in x for x in p['b']) or f.add('FAIL', f'cupboards search: missing {need}: {p["b"]}')
        p['typed'] or f.add('FAIL', 'typing as last resort row is gone')
    # the routes sit right under the search box (not below the shop chips and lists)
    gap = ev("(()=>{const q=document.getElementById('mhCbQ').getBoundingClientRect(), r=document.querySelector('[data-newroutes]').getBoundingClientRect(); return Math.round(r.top-q.bottom)})()")
    gap < 60 or f.add('FAIL', f'cupboards: routes are {gap}px below the search box')
    # existing food: no routes
    ev("mhCbQ('Zzqx Cheese')"); page.wait_for_timeout(300); probe() is None or f.add('FAIL', 'routes shown for a food that is already in the cupboards')
    # online route opens the Log-style panel, library only
    ev("mhCbQ('Wholemeal wraps')"); page.wait_for_timeout(300)
    ev("document.querySelector('[data-newroutes] button:not([data-manual])').click()"); page.wait_for_timeout(500)
    ev("document.getElementById('foodSearchOverlay').classList.contains('open')") or f.add('FAIL', 'online route did not open the search panel')
    ev("document.getElementById('foodSearchInput').value") == 'Wholemeal wraps' or f.add('FAIL', 'search not pre-filled with the typed name')
    ev("!!_ordSearchTarget && !!_ordSearchTarget.cb") or f.add('FAIL', 'route not tied to the cupboards')
    # saving continues into the cupboards for that food
    ev("mhOrdSearchDone(_ordSearchTarget,'Wholemeal wraps')"); page.wait_for_timeout(500)
    ev("document.getElementById('foodSearchOverlay').classList.contains('open')") and f.add('FAIL', 'panel still open after save')
    ev("(_shopUi.stk&&_shopUi.stk.name)||''") == 'Wholemeal wraps' or f.add('FAIL', f'cupboards form not opened for the new food: {ev("_shopUi.stk&&_shopUi.stk.name")}')
    ev("_ordSearchTarget") is None or f.add('FAIL', 'target left behind')
    # Add a food screen
    ev("_shopUi.stk=null; mhShopView('stockadd'); mhStockQ('Seeded rolls')"); page.wait_for_timeout(300); probe() or f.add('FAIL', 'Add a food screen: no new-food routes')
    gap = ev("(()=>{const q=document.getElementById('mhStockQ').getBoundingClientRect(), r=document.querySelector('[data-newroutes]').getBoundingClientRect(); return Math.round(r.top-q.bottom)})()")
    gap < 60 or f.add('FAIL', f'Add a food screen: routes are {gap}px below the search box')
    # barcode route sets a target and clears if nothing opens
    ev("mhStockNewFind('ai','Seeded rolls')"); page.wait_for_timeout(300)
    ev("document.getElementById('foodSearchOverlay').classList.contains('open')") or f.add('FAIL', 'AI route did not open the panel')
    ev("closeFoodSearch()")
    # neighbours: the order-import routes still work (row-bound target)
    ev("_ordSearchTarget=null; mhOrdSearchDone({i:0},'x')")   # no import open: must not throw
    errs and f.add('FAIL', f'page errors {errs}')
print('findings', len(f))
