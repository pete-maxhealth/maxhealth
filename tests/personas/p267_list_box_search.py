"""Persona 267: the list's Add box is the search (v3.10.1160). Typing "heylo flat" shows the foods you know right under the box; one tap puts the food on the SELECTED
shop's list (a library food not yet in the cupboards also opens the stock form with that shop already filled and comes back to the list); a name that matches nothing offers
"New food" on the same shop; with stock off the food just goes on the list. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const l=loadLibrary(); l.push({name:'Heylo Flatbread',portion:'60 g',kcal:150,protein:5,fat:2,carbs:25}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l)); const s=mhShopLoad(); if(!s.shops.includes('Heylo')) s.shops.push('Heylo'); s.shop='Heylo'; mhShopSave(s);})()""")
    ev("mhStockTrack('Zz Seed',{base:'g'})")
    ev("switchTabById('shop')"); ev("mhShopView('list')"); ev("_shopUi.addOpen=true; mhShopRender()"); page.wait_for_timeout(300)
    if page.locator('#mhShopOwn').get_attribute('placeholder') != 'Search or type a food': f.add('BUG', 'the box says it searches')
    page.fill('#mhShopOwn', 'heylo flat'); page.wait_for_timeout(200)
    if 'Heylo Flatbread' not in page.inner_text('#mhShopSug'): f.add('BUG', 'typing shows the library food under the box')
    if 'New food' not in page.inner_text('#mhShopSug'): f.add('BUG', 'and offers New food when it is not exactly there')
    page.click('#mhShopSug button >> nth=0'); page.wait_for_timeout(500)
    row = ev("mhShopLoad().items.filter(i=>i.key===mhShopKey('Heylo Flatbread')).map(i=>i.shop)")
    if row != ['Heylo']: f.add('BUG', f'one tap puts it on the Heylo list: {row}')
    if not ev("!!_shopUi.stk"): f.add('BUG', 'a library food not in the cupboards opens the stock form')
    elif ev("_shopUi.stk.shop") != 'Heylo' or ev("_shopUi.stk.shopAsk"): f.add('BUG', 'the form already knows the shop (Heylo), no question')
    ev("mhStkBack()"); page.wait_for_timeout(300)
    if ev("_shopUi.view") != 'list': f.add('BUG', 'back to the list')
    # a name that matches nothing: New food on the same shop
    ev("_shopUi.addOpen=true; mhShopRender()"); page.wait_for_timeout(200)
    page.fill('#mhShopOwn', 'Zzqx Brand New'); page.wait_for_timeout(200)
    t = page.inner_text('#mhShopSug')
    if 'New food: Zzqx Brand New' not in t: f.add('BUG', f'no match offers a new food: {t}')
    else:
        page.click('#mhShopSug button >> nth=0'); page.wait_for_timeout(400)
        if ev("mhShopLoad().items.filter(i=>i.key===mhShopKey('Zzqx Brand New')).map(i=>i.shop)") != ['Heylo']: f.add('BUG', 'new food goes on the selected shop')
        if ev("_shopUi.stk && _shopUi.stk.shop") != 'Heylo': f.add('BUG', 'its stock form has the shop')
    ev("mhStkBack()")
    # a cupboard food: straight on the list, no form
    ev("mhStockTrack('Heylo Wraps',{base:'g',shop:'Heylo'}); mhShopView('list'); _shopUi.addOpen=true; mhShopRender()"); page.wait_for_timeout(200)
    page.fill('#mhShopOwn', 'wraps'); page.wait_for_timeout(200); page.click('#mhShopSug button >> nth=0'); page.wait_for_timeout(400)
    if ev("_shopUi.stk") or not ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Heylo Wraps'))"): f.add('BUG', 'a cupboard food goes straight on the list')
    # stock off: library food just goes on the list
    ev("mhStockSetOn(false); mhShopView('list'); _shopUi.addOpen=true; mhShopRender()"); page.wait_for_timeout(200)
    ev("(()=>{const l=loadLibrary(); l.push({name:'Zz Offbread',portion:'50 g',kcal:1,protein:1,fat:1,carbs:1}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));})()")
    page.fill('#mhShopOwn', 'offbread'); page.wait_for_timeout(200); page.click('#mhShopSug button >> nth=0'); page.wait_for_timeout(400)
    if ev("_shopUi.stk") or not ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Zz Offbread'))"): f.add('BUG', 'stock off: the food just goes on the list')
    # removing a mistake: one tap on the row's ✕ (no Edit mode), and Undo brings it back
    ev("mhShopView('list'); const s=mhShopLoad(); mhShopSetAdd(s,'Heylo','own','',null); mhShopSave(s); mhShopRender()"); page.wait_for_timeout(300)
    page.click('[data-item="Heylo"] [data-rm]'); page.wait_for_timeout(300)
    if ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Heylo'))"): f.add('BUG', 'one tap on the cross removes it, without Edit mode')
    page.click('#toast span >> text=Undo'); page.wait_for_timeout(300)
    if not ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Heylo'))"): f.add('BUG', 'Undo brings it back')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
