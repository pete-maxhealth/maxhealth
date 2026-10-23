"""Persona 225: the My cupboards view stays short however big the food library is (v3.10.1124). Pete's worry: a flat list of every food would be endless.
A library of 300 foods plus 17 held items. Covers: only held items are listed (never the 300); tabs All / Fridge / Freezer / Cupboard / Non-nutritional /
Low / Use soon with counts, and a tab with nothing in it is not shown; each tab shows the right rows; more than eight rows are grouped by aisle and an aisle folds
(and stays folded through a re-render); a short tab is flat; the search filters held rows, offers foods in the library that are not held (at most six, never the
whole library) with an add button that opens the add form, and offers a typed name as a new food; tapping a row opens it; the open item can be put on the shopping
list (with its shop; a second try says it is already there, no duplicate) and removed from the cupboards; the wording says "in my cupboards", not "tracked"."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 3000}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("for (let i = 0; i <= MH_SHOP_WALK.length + 1; i++) mhCbState().fold['a' + i] = false")   # aisles now start closed (v3.10.1172); this test looks inside them
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("l=>saveLibrary(l.concat(loadLibrary()))", [{'name': f'Library Food {i}', 'kcal': 100, 'protein': 5, 'fat': 3, 'carbs': 10, 'portion': '100g'} for i in range(300)] + [{'name': 'Smoked Mackerel', 'kcal': 300, 'protein': 20, 'fat': 25, 'carbs': 0, 'portion': '100g'}])
    held = [('Chicken Breast', 'g', 1000, 'fridge'), ('Beef Mince', 'g', 500, 'freezer'), ('Whole Milk', 'ml', 2000, 'fridge'), ('Cheddar', 'g', 400, 'fridge'), ('Butter', 'g', 250, 'fridge'), ('Eggs', 'each', 12, 'fridge'),
            ('Frozen Peas', 'g', 800, 'freezer'), ('Fish Fingers', 'each', 10, 'freezer'), ('Basmati Rice', 'g', 1000, ''), ('Pasta', 'g', 500, ''), ('Baked Beans', 'g', 400, ''), ('Porridge Oats', 'g', 1000, ''),
            ('Olive Oil', 'ml', 500, ''), ('Brown Bread', 'each', 1, ''), ('Toilet roll', 'each', 9, ''), ('Bin bags', 'each', 40, '')]
    ev("""(h)=>{ h.forEach(([n,b,l,st])=>{ mhStockTrack(n,{base:b,pack:l,serving:null,shop:'Asda'}); const k=mhShopKey(n); mhStockSetLevel(k,l); if(st) mhStockSetStore(k,st); });
      const o=mhStockLoad(); ['Toilet roll','Bin bags'].forEach(n=>{ o.items[mhShopKey(n)].nonFood=true; });
      o.items[mhShopKey('Butter')].reorder=500; o.items[mhShopKey('Whole Milk')].useBy=new Date(Date.now()+86400000).toISOString().slice(0,10); mhStockSave(o); }""", held)
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    rows = lambda: ev("()=>[...document.querySelectorAll('#stockctlBody [data-stock]')].map(e=>e.dataset.stock)")
    tabs = lambda: ev("()=>[...document.querySelectorAll('#mhCbTabs button')].map(b=>b.textContent.trim())")
    txt = lambda sel: ev("(s)=>document.querySelector(s)?.innerText || ''", sel)

    # held only, never the library
    r = rows()
    if len(r) != 16: f.add('BUG', f'only the 16 held items are listed, not the library: {len(r)}')
    if any('Library Food' in x for x in r): f.add('BUG', 'library foods that are not held must not be listed')
    card = txt('#stockctlCard')
    if '16 in my cupboards' not in card: f.add('BUG', f'summary says how many are in my cupboards: {card[:200]!r}')
    if 'tracked' in card.lower(): f.add('BUG', 'the card no longer says tracked')
    # tabs
    t = tabs()
    want = ['All (16)', 'Fridge (5)', 'Freezer (3)', 'Cupboard (6)', 'Non-nutritional (2)', 'Low (1)', 'Use soon (5)']   # the suggested 3-day fridge life makes every fridge item use-soon until you set its own length
    if t != want: f.add('BUG', f'tabs with counts: {t}')
    # grouping by aisle when long, fold survives
    if ev("document.querySelectorAll('#stockctlBody [data-cb-aisle]').length") < 3: f.add('BUG', 'more than eight rows are grouped by aisle')
    first = ev("document.querySelector('#stockctlBody [data-cb-aisle]').dataset.cbAisle"); n0 = len(rows())
    ev("(a)=>mhCbFold('a'+a)", first); ev("mhShopRender()")
    if len(rows()) >= n0: f.add('BUG', 'folding an aisle hides its rows, and stays folded through a re-render')
    ev("(a)=>mhCbFold('a'+a)", first)
    if len(rows()) != n0: f.add('BUG', 'unfolding brings them back')
    # each tab shows the right rows, short tabs are flat
    ev("mhCbTab('fridge')"); r = rows()
    if sorted(r) != ['Butter', 'Cheddar', 'Chicken Breast', 'Eggs', 'Whole Milk']: f.add('BUG', f'fridge tab: {r}')
    if ev("document.querySelectorAll('#stockctlBody [data-cb-aisle]').length"): f.add('BUG', 'a short tab is flat, no aisle headers')
    ev("mhCbTab('freezer')")
    if sorted(rows()) != ['Beef Mince', 'Fish Fingers', 'Frozen Peas']: f.add('BUG', f'freezer tab: {rows()}')
    ev("mhCbTab('cupboard')")
    if 'Toilet roll' in rows() or 'Bin bags' in rows() or len(rows()) != 6: f.add('BUG', f'cupboard tab is food without a fridge or freezer: {rows()}')
    ev("mhCbTab('nonfood')")
    if sorted(rows()) != ['Bin bags', 'Toilet roll']: f.add('BUG', f'non-nutritional tab: {rows()}')
    ev("mhCbTab('low')")
    if rows() != ['Butter']: f.add('BUG', f'low tab: {rows()}')
    ev("mhCbTab('soon')")
    if sorted(rows()) != ['Butter', 'Cheddar', 'Chicken Breast', 'Eggs', 'Whole Milk']: f.add('BUG', f'use soon tab: {rows()}')
    ev("mhCbTab('all')")
    # search: held rows filter, library foods offered (capped), typed name offered
    ev("mhCbQ('chedd')"); page.wait_for_timeout(100)
    if rows() != ['Cheddar']: f.add('BUG', f'search filters the held rows: {rows()}')
    ev("mhCbQ('library food 1')"); page.wait_for_timeout(100)
    offered = ev("document.querySelectorAll('#stockctlBody [data-add-food]').length")
    if rows() or offered > 7 or offered < 2: f.add('BUG', f'library hits are offered, at most six plus the typed one: {offered}, rows {rows()}')
    ev("mhCbQ('smoked mack')"); page.wait_for_timeout(100)
    if 'Smoked Mackerel' not in txt('#stockctlBody'): f.add('BUG', 'a library food that is not held is offered by search')
    page.click('[data-add-food="Smoked Mackerel"]'); page.wait_for_timeout(250)
    if ev("_shopUi.view") != 'stockedit' and 'Smoked Mackerel' not in txt('#mhShopPane'): f.add('BUG', f'the add button opens the form for it: {ev("_shopUi.view")}')
    ev("mhShopView('list')"); ev("mhCbQ('zzqx fruit')"); page.wait_for_timeout(100)
    if 'Add “zzqx fruit” as a new food' not in txt('#stockctlBody'): f.add('BUG', 'a typed name is offered as a new food')
    ev("mhCbQ('')")
    # open a row, add to list, remove (the list's current shop is Tesco; Cheddar is bought at Asda and must go under Asda)
    ev("()=>{ const s=mhShopLoad(); s.shops.push('Tesco'); s.shop='Tesco'; mhShopSave(s); }")
    page.click('[data-stock="Cheddar"] [onclick^="mhStockEditView"]'); page.wait_for_timeout(250)
    body = txt('#mhShopPane')
    if 'Add to shopping list' not in body or 'Remove from my cupboards' not in body: f.add('BUG', f'the open item offers add to list and remove: {body[-200:]!r}')
    page.click('button:has-text("Add to shopping list")'); page.wait_for_timeout(250)
    it = ev("mhShopLoad().items.find(i=>i.key===mhShopKey('Cheddar'))")
    if not it or it['shop'] != 'Asda' or it.get('src') != 'stock': f.add('BUG', f'it is on the list under its shop: {it}')
    ev("mhStockEditView(mhShopKey('Cheddar'))"); page.wait_for_timeout(200); page.click('button:has-text("Add to shopping list")'); page.wait_for_timeout(200)
    if ev("mhShopLoad().items.filter(i=>i.key===mhShopKey('Cheddar')).length") != 1: f.add('BUG', 'a second add must not duplicate it')
    ev("mhStockEditView(mhShopKey('Cheddar'))"); page.wait_for_timeout(200); page.click('button:has-text("Remove from my cupboards")'); page.wait_for_timeout(200); ev("(i)=>document.getElementById(i)?.click()", 'appModalConfirm'); page.wait_for_timeout(250)
    if ev("!!mhStockLoad().items[mhShopKey('Cheddar')]"): f.add('BUG', 'remove takes it out of the cupboards')
    if not ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Cheddar'))"): f.add('BUG', 'removing from the cupboards leaves the shopping list alone')
    # a tab with nothing in it is not shown
    ev("()=>{ const o=mhStockLoad(); o.items[mhShopKey('Butter')].reorder=100; mhStockSave(o); }"); ev("mhCbTab('all')"); ev("mhShopRender()")
    if any(x.startswith('Low') for x in tabs()): f.add('BUG', f'a tab with nothing in it is hidden: {tabs()}')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
