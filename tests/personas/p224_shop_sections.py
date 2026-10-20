"""Persona 224: the Shopping page is one flow of three sections with the same controls (v3.10.1124). Pete's complaint: the page looked haphazard,
with stacked buttons, three different hide styles and no way to fold, hide or reorder most of it. Covers: My list, Add to the list and Stock
control are each a card with a title, a ? help, and the standard "▲ ▼ 👁 ▾ hide" controls; the default order is list, add, stock; any section
moves up and down (the ends refuse) and the order is remembered; the eye hides a section and leaves a way back, for each of the three; the old
two-area layout (stock, list, hidden) is read and upgraded, not lost; the Add section's open/closed choice is remembered and starts open only
while the list is empty; the Add buttons are a two-column grid of tiles, not a stack; fold on My list hides its body and survives a re-render;
the green Shopping complete button shows only once something is ticked; Copy list lives in the list section; the old duplicate page title is gone."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 3000}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    vis = lambda sel: ev("(s)=>{const e=document.querySelector(s); return !!e && getComputedStyle(e).display!=='none'}", sel)
    order = lambda: ev("()=>[...document.querySelectorAll('#mhShopPane > .water-card')].map(c=>c.id)")
    ctl = lambda cid: ev("(i)=>document.querySelector('#'+i+' .mh-ctl')?.innerText.replace(/\\s+/g,' ').trim() || ''", cid)

    # 1. empty list: the Add section starts open, three cards, standard controls, default order
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    if order() != ['shoplistCard', 'shopaddCard', 'stockctlCard']: f.add('BUG', f'default order list, add, stock: {order()}')
    for cid, nm in (('shoplistCard', 'my list'), ('shopaddCard', 'add to the list'), ('stockctlCard', 'my cupboards')):
        head = ev("(i)=>document.querySelector('#'+i+' .water-header')?.innerText || ''", cid)
        if nm not in head.lower() or '?' not in head: f.add('BUG', f'{cid}: title and ? expected: {head!r}')
        c = ctl(cid)
        if not c.startswith('▲ ▼ 👁 ▾') and cid != 'shopaddCard': f.add('BUG', f'{cid}: standard controls expected, got {c!r}')
    if '▲ ▼ 👁' not in ctl('shopaddCard'): f.add('BUG', f'the Add section has the standard controls: {ctl("shopaddCard")!r}')
    if 'Shopping list' in ev("document.getElementById('mhShopPane').innerText.split('\\n')[0]"): f.add('BUG', 'the old duplicate page title is gone from the list view')
    if not vis('#mhShopAddPanel'): f.add('BUG', 'an empty list starts with the Add section open')

    # 2. tiles: two to a row, none stretched
    tiles = ev("()=>[...document.querySelectorAll('#mhShopAddPanel .mh-tile')].map(b=>{const r=b.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.left), Math.round(r.width)]})")
    if len(tiles) < 6: f.add('BUG', f'the Add section has its tiles: {tiles}')
    elif tiles[0][0] != tiles[1][0] or tiles[0][1] == tiles[1][1] or max(t[2] for t in tiles) > 250: f.add('BUG', f'tiles sit two to a row and are not stretched: {tiles}')

    # 3. with something on the list, a remembered closed Add section, and the complete button only once ticked
    ev("()=>{const s=mhShopLoad(); ['Whole Milk','Eggs'].forEach(n=>mhShopSetAdd(s,n,'own','',null,{})); mhShopSave(s);}"); ev("_shopUi.addOpen = undefined; mhShopOpen()"); page.wait_for_timeout(250)
    if vis('#mhShopAddPanel'): f.add('BUG', 'with items on the list the Add section starts closed')
    if '▸ show' not in ctl('shopaddCard'): f.add('BUG', f'a closed Add section says show: {ctl("shopaddCard")!r}')
    if ev("!!document.querySelector('#shoplistBody button[onclick=\"mhShopComplete()\"]')"): f.add('BUG', 'no Shopping complete button until something is ticked')
    ev("mhShopAddToggle()"); page.wait_for_timeout(150)
    if not vis('#mhShopAddPanel'): f.add('BUG', 'the Add control opens the section')
    page.reload(); page.wait_for_timeout(1200); ev("mhShopOpen()"); page.wait_for_timeout(250)
    if not vis('#mhShopAddPanel'): f.add('BUG', 'the open/closed choice of the Add section is remembered across a reload')
    ev("mhShopAddToggle()")
    ev("()=>{const s=mhShopLoad(); s.items[0].checked=true; mhShopSave(s);}"); ev("mhShopOpen()"); page.wait_for_timeout(200)
    if not ev("!!document.querySelector('#shoplistBody button[onclick=\"mhShopComplete()\"]')"): f.add('BUG', 'a ticked item brings the Shopping complete button')
    if 'Copy list' not in ev("document.getElementById('shoplistBody')?.innerText || ''"): f.add('BUG', 'Copy list lives in the list section')

    # 4. reorder: any section, ends refuse, remembered
    ev("mhShopSecMove('add','up')"); page.wait_for_timeout(150)
    if order() != ['shopaddCard', 'shoplistCard', 'stockctlCard']: f.add('BUG', f'Add moves up: {order()}')
    ev("mhShopSecMove('add','up')")
    if order() != ['shopaddCard', 'shoplistCard', 'stockctlCard']: f.add('BUG', 'the top section cannot move further up')
    ev("mhShopOpen()"); page.wait_for_timeout(150)
    if order() != ['shopaddCard', 'shoplistCard', 'stockctlCard']: f.add('BUG', 'the order is remembered')
    ev("mhShopSecMove('stock','down')")
    if order() != ['shopaddCard', 'shoplistCard', 'stockctlCard']: f.add('BUG', 'the bottom section cannot move further down')
    ev("mhShopSecMove('stock','up')"); ev("mhShopSecMove('stock','up')")
    if order() != ['stockctlCard', 'shopaddCard', 'shoplistCard']: f.add('BUG', f'Stock moves to the top in two steps: {order()}')
    ev("localStorage.removeItem(MH_STOCK_LAYOUT_KEY)"); ev("mhShopOpen()")
    if order() != ['shoplistCard', 'shopaddCard', 'stockctlCard']: f.add('BUG', f'no saved layout means the default order: {order()}')

    # 5. hide each section and bring it back
    for sid, cid, showid in (('list', 'shoplistCard', 'mhSecShow_list'), ('add', 'shopaddCard', 'mhSecShow_add'), ('stock', 'stockctlCard', 'mhStockShow')):
        ev("(i)=>mhShopSecHide(i)", sid); page.wait_for_timeout(120)
        if ev("(c)=>!!document.getElementById(c)", cid) or not ev("(c)=>!!document.getElementById(c)", showid): f.add('BUG', f'{sid}: the eye removes the section and leaves a way back')
        ev("(i)=>document.getElementById(i).click()", showid); page.wait_for_timeout(120)
        if not ev("(c)=>!!document.getElementById(c)", cid): f.add('BUG', f'{sid}: the way back brings the section back')

    # 6. fold My list and survive a re-render
    ev("mhCardBody('shoplist')"); ev("mhShopRender()")
    if vis('#shoplistBody') or '▸ show' not in ev("document.getElementById('shoplistBodyIcon').textContent"): f.add('BUG', 'fold hides the list body, says show, and survives a re-render')
    ev("mhCardBody('shoplist')")
    if not vis('#shoplistBody'): f.add('BUG', 'fold opens again')

    # 7. the old layout is upgraded, not lost
    ev("localStorage.setItem(MH_STOCK_LAYOUT_KEY, JSON.stringify({order:['stock','list'],hidden:true}))")
    lay = ev("mhStockLayout()")
    if lay['order'] != ['stock', 'list', 'add'] or not lay['hid'].get('stock') or not lay['hidden']: f.add('BUG', f'the old two-area layout upgrades: {lay}')
    ev("localStorage.removeItem(MH_STOCK_LAYOUT_KEY)")
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
