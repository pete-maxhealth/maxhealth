"""Persona 495 (v3.10.1412): the shopping Add box "New food" row and the Add foods picker offer the same new-food routes as Log (online, AI, barcode, label);
saving continues: from the Add box the food also goes on the list, from the picker you come back to the picker. Invented data."""
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
    ev("mhStockTrack('Zzqx Cheese',{base:'g'})")
    routes = lambda: ev("[...document.querySelectorAll('[data-newroutes] button')].map(b=>b.textContent.trim()+'|'+b.dataset.c)")
    # shopping Add box
    ev("_shopUi.addOpen=true; mhShopAddKind('food')"); page.wait_for_timeout(300)
    ev("document.getElementById('mhShopOwn').value='Wholemeal wraps'; mhShopSug()"); page.wait_for_timeout(300)
    r = routes(); len(r) == 4 and all(x.endswith('|shop') for x in r) or f.add('FAIL', f'Add box routes: {r}')
    ev("document.querySelector('[data-newroutes] button').click()"); page.wait_for_timeout(500)
    ev("document.getElementById('foodSearchOverlay').classList.contains('open')") or f.add('FAIL', 'Add box: online route did not open the panel')
    ev("mhOrdSearchDone(_ordSearchTarget,'Wholemeal wraps')"); page.wait_for_timeout(500)
    ev("mhShopLoad().items.some(i=>i.name==='Wholemeal wraps')") or f.add('FAIL', 'Add box: new food not put on the list')
    ev("(_shopUi.stk&&_shopUi.stk.name)||''") == 'Wholemeal wraps' or f.add('FAIL', 'Add box: cupboards form not opened')
    # picker
    ev("_shopUi.stk=null; mhShopView('list'); mhSlOpen(); mhSlQ('Seeded rolls')"); page.wait_for_timeout(400)
    r = routes(); len(r) == 4 and all(x.endswith('|picker') for x in r) or f.add('FAIL', f'picker routes: {r}')
    ev("mhStockNewFind('ai','Seeded rolls','picker')"); page.wait_for_timeout(400)
    ev("document.getElementById('foodSearchOverlay').classList.contains('open')") or f.add('FAIL', 'picker: AI route did not open the panel')
    ev("mhOrdSearchDone(_ordSearchTarget,'Seeded rolls')"); page.wait_for_timeout(500)
    ev("(_shopUi.stk&&_shopUi.stk.name)||''") == 'Seeded rolls' or f.add('FAIL', 'picker: cupboards form not opened')
    ev("mhShopLoad().items.some(i=>i.name==='Seeded rolls')") and f.add('FAIL', 'picker must not put the food on the shopping list')
    # a known food shows no routes
    ev("_shopUi.stk=null; mhShopView('list'); _shopUi.addOpen=true; mhShopRender()"); ev("document.getElementById('mhShopOwn').value='Zzqx Cheese'; mhShopSug()"); page.wait_for_timeout(300)
    r = routes(); r == [] or f.add('FAIL', f'routes shown for a known food: {r}')
    errs and f.add('FAIL', f'page errors {errs}')
print('findings', len(f))
