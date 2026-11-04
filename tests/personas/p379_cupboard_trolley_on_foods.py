"""Persona 379: every food row in My cupboards has the trolley too (v3.10.1264).
Pete (4 Nov): "My cupboard should have the shopping trolley icons too because that's where you check the stock and add items where stock isn't a consideration."
Grey trolley = not on the list (tap to add); coloured trolley + ON LIST = on the list (tap to take off, Undo). A food put on by hand is not tidied away when it is not low.
Covers: food and non-food rows, add, tidy-up (reconcile) keeps it, reload, take off, Undo, a LOW food the app added goes to Filtered like the list's X. Invented data; real taps."""
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
    for n in ['Zzqx Rice', 'Zzqx Beans', 'Zzqx Pasta']: ev(f"mhStockTrack('{n}',{{base:'g',shop:'Asda'}}); mhStockSetLevel(mhShopKey('{n}'),800)")
    ev("mhStockSetReorder(mhShopKey('Zzqx Pasta'),500); mhStockSetLevel(mhShopKey('Zzqx Pasta'),100)")   # Pasta is low
    ev("mhStockAddNonFood('Zzqx Soap')"); page.wait_for_timeout(200)
    ev("try{mhStkBack()}catch(e){}; localStorage.setItem('mh_shop_pane','stock'); _shopUi.view='list'; mhCbState().fold={}; mhCbTab('all'); mhCbShop(''); mhShopRender()"); page.wait_for_timeout(300)
    ev("(()=>{const s=mhShopLoad(); s.items=s.items.filter(i=>!/Zzqx/.test(i.name)); mhShopSave(s)})()")
    for tab in ['cupboard']: ev(f"mhCbTab('{tab}')"); page.wait_for_timeout(300)
    ev("mhCbFoldAll(false)"); page.wait_for_timeout(300)
    def tap(sel):
        ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none')")
        bb = page.locator(sel).first.bounding_box(); page.mouse.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(450)
    onlist = lambda n: ev(f"mhShopLoad().items.some(i=>i.name==='{n}')")
    def state(n): return ev(f"(()=>{{const r=[...document.querySelectorAll('#stockctlCard [data-stock]')].find(e=>e.dataset.stock==='{n}'); if(!r) return 'norow'; return r.querySelector('[data-lowlist]')?'on':r.querySelector('[data-lowbtn]')?'off':'none'}})()")
    row = lambda n: f'#stockctlCard [data-stock="{n}"]'
    ev("document.getElementById('stockctlCard').scrollIntoView()")
    for n in ['Zzqx Rice', 'Zzqx Beans', 'Zzqx Pasta']:
        if state(n) != 'off': f.add('BUG', f'1: {n} (a food) shows a trolley: {state(n)}')
    tap(f'{row("Zzqx Rice")} [data-lowbtn]')
    if not onlist('Zzqx Rice') or state('Zzqx Rice') != 'on': f.add('BUG', f'2: tapping the trolley puts the food on the list and shows ON LIST: {state("Zzqx Rice")}')
    it = ev("mhShopLoad().items.find(i=>i.name==='Zzqx Rice')")
    if not it or it['from'] != 'added by hand': f.add('BUG', f'3: it is marked as added by hand: {it and it['from']}')
    ev("mhShopReconcile(); mhShopRender()"); page.wait_for_timeout(300)
    if not onlist('Zzqx Rice'): f.add('BUG', '4: the stock tidy-up does not remove a food you put on by hand')
    page.reload(); page.wait_for_timeout(1200); ev("localStorage.setItem('mh_shop_pane','stock'); mhShopOpen(); mhCbTab('cupboard'); mhCbFoldAll(false)"); page.wait_for_timeout(400)
    if state('Zzqx Rice') != 'on': f.add('BUG', '5: still on the list after a reload')
    ev("document.getElementById('stockctlCard').scrollIntoView()")
    tap(f'{row("Zzqx Rice")} [data-lowlist]')
    if onlist('Zzqx Rice') or state('Zzqx Rice') != 'off': f.add('BUG', f'6: tapping ON LIST takes the food off: {state("Zzqx Rice")}')
    if not ev("!!mhStockLoad().items[mhShopKey('Zzqx Rice')]"): f.add('BUG', '7: it stays in My cupboards')
    ev("document.querySelector('#toast .toast-undo')?.click()"); page.wait_for_timeout(400)
    if not onlist('Zzqx Rice'): f.add('BUG', '8: Undo puts it back')
    # a LOW food the app put on the list by itself: ON LIST then takes it off the way the list's X does (Filtered, Undo)
    ev("mhStockSweep && mhStockSweep(); mhShopRender()"); page.wait_for_timeout(300)
    if onlist('Zzqx Pasta') and state('Zzqx Pasta') == 'on':
        tap(f'{row("Zzqx Pasta")} [data-lowlist]')
        held = ev("!!(mhStockLoad().items[mhShopKey('Zzqx Pasta')]||{}).held")
        if onlist('Zzqx Pasta') or not held: f.add('BUG', f'9: a low food the app added goes to Filtered when taken off: onlist={onlist("Zzqx Pasta")} held={held}')
    # non-nutritional still behaves as in 1261
    ev("mhCbTab('nonfood')"); page.wait_for_timeout(300)
    if state('Zzqx Soap') != 'off': f.add('BUG', f'10: the non-nutritional row keeps its trolley: {state("Zzqx Soap")}')
    ev("mhCbTab('cupboard')"); page.wait_for_timeout(300); ev("document.getElementById('stockctlCard').scrollIntoView()"); page.screenshot(path='/tmp/p379.png')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
