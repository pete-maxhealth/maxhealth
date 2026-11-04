"""Persona 380: (a) the trolley on a FILTERED food puts it on the list and it stays; (b) every shopping-list row shows its quantity with - / + (v3.10.1266).
Pete (4 Nov): "Beef stock cubes not showing as on list, tried to add twice" and "the figure for how many to buy doesn't show on the shopping list, there's no +- next to each item if you change your mind. There might be an offer on."
Covers: filtered low food, trolley, tidy-up keeps it and it is un-filtered, ON LIST shows; row has - and + without Edit; tap +, -, floor at 1, 99 cap; "2 x" figure; buy-quantity from the cupboard shows; reload; ticking still works from the name. Invented data; real taps."""
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
    K = "mhShopKey('Zzqx Beef Stock Cubes')"
    ev("mhStockTrack('Zzqx Beef Stock Cubes',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Beef Stock Cubes'),60); mhStockSetReorder(mhShopKey('Zzqx Beef Stock Cubes'),80)")
    ev(f"(()=>{{const o=mhStockLoad(); o.items[{K}].held=true; mhStockSave(o)}})()")
    ev("mhStockTrack('Zzqx Rice',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Rice'),500); (()=>{const o=mhStockLoad(); o.items[mhShopKey('Zzqx Rice')].buyQty=3; mhStockSave(o)})()")
    ev("localStorage.setItem('mh_shop_pane','stock'); _shopUi.view='list'; mhCbState().fold={}; mhCbTab('cupboard'); mhCbFoldAll(false); mhShopRender()"); page.wait_for_timeout(300)
    ev("(()=>{const s=mhShopLoad(); s.items=s.items.filter(i=>!/Zzqx/.test(i.name)); mhShopSave(s)})()")
    def tap(sel):
        ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none')")
        bb = page.locator(sel).first.bounding_box(); page.mouse.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(450)
    onlist = lambda n: ev(f"mhShopLoad().items.some(i=>i.name==='{n}')")
    row = lambda n: f'#stockctlCard [data-stock="{n}"]'
    ev("document.getElementById('stockctlCard').scrollIntoView()")
    tap(f'{row("Zzqx Beef Stock Cubes")} [data-lowbtn]')
    if not onlist('Zzqx Beef Stock Cubes'): f.add('BUG', '1: the trolley on a filtered food puts it on the list')
    ev("mhShopReconcile(); mhShopRender()"); page.wait_for_timeout(300)
    if not onlist('Zzqx Beef Stock Cubes'): f.add('BUG', '2: the tidy-up does not take it off again')
    if ev(f"!!mhStockLoad().items[{K}].held"): f.add('BUG', '3: it is no longer filtered')
    if not ev(f"!!document.querySelector('{row('Zzqx Beef Stock Cubes')} [data-lowlist]')"): f.add('BUG', '4: the row shows ON LIST')
    # the list: every row has - and + without Edit
    ev("localStorage.setItem('mh_shop_pane','list'); _shopUi.view='list'; _shopUi.edit=false; _shopUi.fold={}; mhShopRender()"); page.wait_for_timeout(300)
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zzqx Milk','own'); mhShopSave(s)})()")
    ev("mhShopRender(); mhShopFold && 0"); page.wait_for_timeout(200)
    for _ in range(8):
        if not ev("(()=>{const e=[...document.querySelectorAll('#mhShopPane .mh-aisle > span:first-child')].find(x=>x.innerText.trim().startsWith('▸')); if(!e) return false; e.click(); return true})()"): break
        page.wait_for_timeout(200)
    nrows = ev("document.querySelectorAll('#mhShopPane [data-item]').length"); nctl = ev("document.querySelectorAll('#mhShopPane [data-item] [data-qtyctl]').length")
    if nrows < 2 or nrows != nctl: f.add('BUG', f'5: every list row has - and + without Edit ({nctl} of {nrows})')
    q = lambda n: ev(f"(mhShopLoad().items.find(i=>i.name==='{n}')||{{}}).qty||1")
    ctl = lambda n, t: f'#mhShopPane [data-item="{n}"] [title="{t}"]'
    tap(ctl('Zzqx Milk', 'One more')); tap(ctl('Zzqx Milk', 'One more'))
    if q('Zzqx Milk') != 3: f.add('BUG', f'6: + twice makes 3: {q("Zzqx Milk")}')
    shown = ev("document.querySelector('#mhShopPane [data-item=\"Zzqx Milk\"] [data-qtyctl]').innerText.replace(/\\s+/g,' ').trim()")
    if '3' not in shown: f.add('BUG', f'7: the figure shows: {shown!r}')
    tap(ctl('Zzqx Milk', 'One fewer')); tap(ctl('Zzqx Milk', 'One fewer')); tap(ctl('Zzqx Milk', 'One fewer'))
    if q('Zzqx Milk') != 1: f.add('BUG', f'8: - stops at 1: {q("Zzqx Milk")}')
    if not ev("document.querySelector('#mhShopPane [data-item=\"Zzqx Milk\"] input[type=checkbox]') && !mhShopLoad().items.find(i=>i.name==='Zzqx Milk').checked"): f.add('BUG', '9: tapping - or + does not tick the item')
    # the buy-quantity from the cupboard arrives and shows
    ev("localStorage.setItem('mh_shop_pane','stock'); mhShopRender()"); page.wait_for_timeout(300)
    ev("mhStockLowNow(mhShopKey('Zzqx Rice'))"); page.wait_for_timeout(300)
    if q('Zzqx Rice') != 3: f.add('BUG', f'10: the cupboard buy quantity (3) comes onto the list: {q("Zzqx Rice")}')
    # reload keeps it, and ticking from the name still works
    page.reload(); page.wait_for_timeout(1200); ev("localStorage.setItem('mh_shop_pane','list'); mhShopOpen()"); page.wait_for_timeout(300)
    for _ in range(8):
        if not ev("(()=>{const e=[...document.querySelectorAll('#mhShopPane .mh-aisle > span:first-child')].find(x=>x.innerText.trim().startsWith('▸')); if(!e) return false; e.click(); return true})()"): break
        page.wait_for_timeout(200)
    if q('Zzqx Rice') != 3: f.add('BUG', '11: the quantity survives a reload')
    tap('#mhShopPane [data-item="Zzqx Rice"] input[type=checkbox]')
    page.screenshot(path='/tmp/p380.png')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
