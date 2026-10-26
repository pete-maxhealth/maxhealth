"""Persona 324 (v3.10.1218): "How many packs to buy each time it runs low" on a cupboard item. When the item goes low the list says "3 x Milk", the shop-floor row shows it, changing it autosaves with Undo like the other fields, it survives reload, and finishing the shop offers 3 packs as the bought amount. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("mhStockOn = ()=>true; mhStockTrack('Zz Milk',{base:'ml',pack:1000,shop:'Asda'}); mhStockSetLevel(mhShopKey('Zz Milk'),3000); mhStockSetReorder(mhShopKey('Zz Milk'),1000)")
    ev("switchTabById('shop'); mhStockEditView(mhShopKey('Zz Milk'))"); page.wait_for_timeout(400)
    if not ev("!!document.getElementById('mhStkBuy')"): f.add('BUG', 'the cupboard item has a how-many-packs field')
    else:
        page.fill('#mhStkBuy', '3'); page.dispatch_event('#mhStkBuy', 'change'); page.wait_for_timeout(300)
        if ev("mhStockLoad().items[mhShopKey('Zz Milk')].buyQty") != 3: f.add('BUG', 'typing 3 saves it straight away')
        if 'Buy each time' not in page.inner_text('body'): f.add('BUG', 'the change shows in the Undo trail like the other fields')
        page.fill('#mhStkBuy', ''); page.dispatch_event('#mhStkBuy', 'change'); page.wait_for_timeout(200)
        if ev("mhStockLoad().items[mhShopKey('Zz Milk')].buyQty") is not None: f.add('BUG', 'emptying it goes back to one')
        page.fill('#mhStkBuy', '3'); page.dispatch_event('#mhStkBuy', 'change'); page.wait_for_timeout(200)
    # it runs low: the list says 3 x
    ev("mhStockSetLevel(mhShopKey('Zz Milk'),500); mhStockSweep()"); ev("mhShopView('list'); mhShopLQ('Zz Milk')"); page.wait_for_timeout(400)
    q = ev("(mhShopLoad().items.find(i=>i.key===mhShopKey('Zz Milk'))||{}).qty")
    if q != 3: f.add('BUG', f'a low item arrives on the list as 3: {q}')
    if '3 × Zz Milk' not in ev("document.body.innerText.replace(/\\s+/g,' ')"): f.add('BUG', 'the shop-floor row reads 3 × Zz Milk')
    # reload keeps it
    page.reload(); page.wait_for_timeout(1500)
    if ev("mhStockLoad().items[mhShopKey('Zz Milk')].buyQty") != 3: f.add('BUG', 'it survives a reload')
    # finish the shop
    ev("(()=>{const s=mhShopLoad(); s.items.find(i=>i.key===mhShopKey('Zz Milk')).checked=true; mhShopSave(s); mhShopCompleteGo(false,false);})()"); page.wait_for_timeout(300)
    d = ev("mhBoughtDefault(mhStockLoad().items[mhShopKey('Zz Milk')])")
    if d != '3000 ml': f.add('BUG', f'3 packs of 1000 ml offered as 3000 ml: {d}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
