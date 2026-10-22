"""Persona 270: My cupboards, Close all / Open all and Add foods within reach (v3.10.1164). Pete could not see Add foods without first collapsing every aisle group, and the Use soon
list ran on for 15 rows. Now: an Add foods button sits at the top of the card; Close all / Open all shuts or opens every aisle group and the Use soon list in one tap; Use soon shows
five with Show all / Show fewer, and folds from its heading. Invented data."""
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
    ev("""(ns)=>{ns.forEach((n,i)=>{ mhStockTrack('Zz '+n,{base:'g',store:i<10?'fridge':'cupboard'}); mhStockSetLevel(mhShopKey('Zz '+n),500); mhStockSetUseBy && 0; const o=mhStockLoad(); o.items[mhShopKey('Zz '+n)].useBy=todayStr?undefined:undefined; mhStockSave(o);}); }""", names)
    # Use soon needs use-by dates tomorrow
    ev("""(()=>{const o=mhStockLoad(); const d=new Date(Date.now()+86400000); const iso=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); Object.values(o.items).forEach(i=>{ i.useBy=iso; }); mhStockSave(o);})()""")
    ev("switchTabById('shop')"); ev("mhShopView('list')"); page.wait_for_timeout(500)
    if not page.locator('#mhCbAddRow button').count(): f.add('BUG', 'an Add foods button sits at the top of My cupboards')
    # it comes before the search box and before the aisle groups
    order = ev("(()=>{const a=document.getElementById('mhCbAddRow'), q=document.getElementById('mhCbQ'), g=document.querySelector('[data-cb-aisle]'); return [a.compareDocumentPosition(q) & 4 ? 1 : 0, a.compareDocumentPosition(g) & 4 ? 1 : 0];})()")
    if order != [1, 1]: f.add('BUG', f'Add foods is above the search and the groups: {order}')
    # Use soon: five shown, Show all
    nrows = lambda: ev("document.querySelectorAll('[data-soon-row]').length")
    if nrows() != 5: f.add('BUG', f'Use soon shows five rows first: {nrows()}')
    page.click('[data-use-soon] >> text=Show all'); page.wait_for_timeout(300)
    if nrows() != 16: f.add('BUG', f'Show all shows every one: {nrows()}')
    page.click('[data-use-soon] >> text=Show fewer'); page.wait_for_timeout(300)
    if nrows() != 5: f.add('BUG', 'Show fewer goes back to five')
    # Close all
    groups = ev("document.querySelectorAll('[data-cb-aisle]').length")
    if groups < 2: f.add('BUG', f'setup: several aisle groups: {groups}')
    page.click('#mhCbFoldAll >> text=Close all'); page.wait_for_timeout(300)
    if ev("document.querySelectorAll('[data-cb-aisle]').length") != groups: f.add('BUG', 'the group headings stay')
    if ev("document.querySelectorAll('[data-stock]').length") != 0: f.add('BUG', 'Close all shuts every group, no food rows show')
    if nrows() != 0: f.add('BUG', 'Close all also shuts the Use soon list')
    if 'Use soon' not in page.inner_text('[data-use-soon]'): f.add('BUG', 'the Use soon heading stays so it can be opened')
    page.click('#mhCbFoldAll >> text=Open all'); page.wait_for_timeout(300)
    if ev("document.querySelectorAll('[data-stock]').length") < 16: f.add('BUG', 'Open all opens every group')
    if nrows() < 5: f.add('BUG', 'Open all opens Use soon')
    # the button opens the Add foods screen, clean
    page.click('#mhCbAddRow button'); page.wait_for_timeout(400)
    if ev("_shopUi.view") != 'stocklist' or ev("mhSlState().q") != '': f.add('BUG', 'Add foods opens the Add foods screen with an empty search')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
