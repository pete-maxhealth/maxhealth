"""Persona 376: in My cupboards a non-nutritional item's trolley is grey when it is not on the list, and a coloured trolley + ON LIST when it is; tapping ON LIST takes it off (v3.10.1261).
Pete (4 Nov): "I should be able to click on list to take it out of the trolley." Covers: add, take off, Undo, take off then add again, the shopping list itself, reload, Low food rows unaffected. Invented data; real taps."""
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
    for n in ['Zzqx Bin bags', 'Zzqx Soap']: ev(f"mhStockAddNonFood('{n}')")
    ev("try{mhStkBack()}catch(e){}; localStorage.setItem('mh_shop_pane','stock'); _shopUi.view='list'; mhCbState().fold={}; mhCbTab('nonfood'); mhShopRender()"); page.wait_for_timeout(400)
    def tap(sel):
        ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none')")
        bb = page.locator(sel).first.bounding_box(); cx, cy = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
        page.mouse.move(cx, cy); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(450)
    onlist = lambda n: ev(f"mhShopLoad().items.some(i=>i.name==='{n}')")
    row = lambda n: f'#stockctlCard [data-stock="{n}"]'
    def state(n): return ev(f"(()=>{{const r=document.querySelector('#stockctlCard [data-stock=\"{n}\"]'); if(!r) return 'norow'; return r.querySelector('[data-lowlist]')?'on':r.querySelector('[data-lowbtn]')?'off':'none'}})()")
    ev("document.getElementById('stockctlCard').scrollIntoView()")
    if state('Zzqx Soap') != 'off': f.add('BUG', f'1: not on the list shows the trolley button: {state("Zzqx Soap")}')
    if ev(f"getComputedStyle(document.querySelector('{row('Zzqx Soap')} [data-lowbtn]')).opacity") == '1': f.add('BUG', '2: the trolley is greyed out when not on the list')
    tap(f'{row("Zzqx Soap")} [data-lowbtn]')
    if not onlist('Zzqx Soap') or state('Zzqx Soap') != 'on': f.add('BUG', f'3: tapping the trolley puts it on the list and shows ON LIST: {state("Zzqx Soap")}')
    txt = ev(f"document.querySelector('{row('Zzqx Soap')} [data-lowlist]').innerText")
    if 'ON LIST' not in txt or '🛒' not in txt: f.add('BUG', f'4: on-list state shows a trolley and ON LIST: {txt!r}')
    tap(f'{row("Zzqx Soap")} [data-lowlist]')
    if onlist('Zzqx Soap') or state('Zzqx Soap') != 'off': f.add('BUG', f'5: tapping ON LIST takes it off the list: {state("Zzqx Soap")}')
    if not ev("!!mhStockLoad().items[mhShopKey('Zzqx Soap')] && !mhStockLoad().items[mhShopKey('Zzqx Soap')].held"): f.add('BUG', '6: it stays on the shelf and is not moved to Filtered')
    # Undo
    ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='')")
    ev("document.querySelector('#toast .toast-undo')?.click()"); page.wait_for_timeout(400)
    if not onlist('Zzqx Soap') or state('Zzqx Soap') != 'on': f.add('BUG', '7: Undo puts it back on the list')
    tap(f'{row("Zzqx Soap")} [data-lowlist]'); tap(f'{row("Zzqx Soap")} [data-lowbtn]')
    if not onlist('Zzqx Soap'): f.add('BUG', '8: off then on again works')
    # the other item is untouched and the list shows only what is on it
    if onlist('Zzqx Bin bags') or state('Zzqx Bin bags') != 'off': f.add('BUG', '9: the other item is not affected')
    page.reload(); page.wait_for_timeout(1200); ev("localStorage.setItem('mh_shop_pane','stock'); mhShopOpen(); mhCbTab('nonfood')"); page.wait_for_timeout(400)
    if state('Zzqx Soap') != 'on' or state('Zzqx Bin bags') != 'off': f.add('BUG', f'10: after a reload the states hold: {state("Zzqx Soap")}/{state("Zzqx Bin bags")}')
    ev("document.getElementById('stockctlCard').scrollIntoView()"); page.screenshot(path='/tmp/p376.png')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
