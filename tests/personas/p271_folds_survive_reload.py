"""Persona 271: folds on My cupboards and the shopping list survive a reload (v3.10.1166). Pete: both lists did not keep their state. Close all, a single closed aisle, Use soon
Show all and a closed shopping-list group are now remembered. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    names = ['Apple','Banana','Carrot','Bread roll','Milk','Cheese','Chicken','Rice','Pasta','Eggs','Butter','Yoghurt','Salmon','Onion','Tomato','Beans']
    ev("""(ns)=>{ns.forEach((n,i)=>{ mhStockTrack('Zz '+n,{base:'g',store:i<10?'fridge':'cupboard'}); mhStockSetLevel(mhShopKey('Zz '+n),500); });}""", names)
    ev("""(()=>{const o=mhStockLoad(); const d=new Date(Date.now()+86400000); const iso=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); Object.values(o.items).forEach(i=>{ i.useBy=iso; }); mhStockSave(o);})()""")
    ev("switchTabById('shop')"); ev("mhShopView('list')"); page.wait_for_timeout(500)
    page.click('[data-use-soon] >> text=Show all'); page.wait_for_timeout(300)
    page.click('#mhCbFoldAll >> text=Close all'); page.wait_for_timeout(300)
    page.click('#mhCbFoldAll >> text=Open all'); page.wait_for_timeout(300)
    first = ev("document.querySelector('[data-cb-aisle]').dataset.cbAisle")
    page.click('[data-cb-aisle="' + first + '"]'); page.wait_for_timeout(300)
    ev("mhShopFold('q2')"); page.wait_for_timeout(200)
    before = ev("document.querySelectorAll('[data-stock]').length")
    page.reload(); page.wait_for_timeout(1500)
    ev("document.getElementById('onboardingOverlay')?.remove()"); ev("switchTabById('shop')"); ev("mhShopView('list')"); page.wait_for_timeout(500)
    if ev("document.querySelectorAll('[data-stock]').length") != before: f.add('BUG', 'the closed aisle stays closed after a reload')
    if ev("!!mhCbState().fold['a'+%s]" % first) is not True: f.add('BUG', 'the aisle fold is remembered')
    if ev("!!mhCbState().soonAll") is not True: f.add('BUG', 'Use soon Show all is remembered')
    if ev("!!_shopUi.fold && _shopUi.fold['q2']") is not True: f.add('BUG', 'a closed shopping-list group is remembered')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
