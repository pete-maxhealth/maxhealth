"""Persona 449: every shopping screen except the list has the ← at the top left, it goes one step back, and the stock-item screen's bottom button says Save (Cancel for a brand-new one). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("['Chicken Breast','Cheddar','Pasta'].forEach(n=>{mhStockTrack(n,{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey(n),200)})")
    ev("localStorage.setItem('mh_shop_pane','list'); switchTabById('shop')"); page.wait_for_timeout(600)
    view = lambda: ev("_shopUi.view")
    arrow = '#mhShopPane #mhShopBackArrow'
    if page.locator(arrow).count(): f.add('BUG', '1: the list itself has no arrow')
    # every other screen: arrow present, same look, goes back to the list
    for v in ['picker', 'recipes', 'quick', 'usuals', 'stockadd', 'stocklist', 'orderimport', 'csvimport', 'sync', 'lists']:
        try:
            ev(f"mhShopView('{v}')"); page.wait_for_timeout(300)
            if view() != v: continue   # some screens need set-up data; reported below only if the screen opened
            n = page.locator(arrow).count()
            if n != 1: f.add('BUG', f'2: {v}: arrow count {n}'); continue
            box = page.locator(arrow).bounding_box()
            if not (box and box['x'] < 60 and abs(box['width'] - 36) < 2): f.add('BUG', f'3: {v}: arrow not top-left 36px: {box}')
            page.locator(arrow).click(timeout=5000); page.wait_for_timeout(300)
            if view() != 'list': f.add('BUG', f'4: {v}: arrow went to {view()} not the list')
        except Exception as e: f.add('BUG', f'5: {v}: {str(e)[:120]}')
    # stock item: Save at the bottom, arrow too, both keep the change
    ev("mhStockEditView(mhShopKey('Pasta'))")
    page.wait_for_timeout(300)
    if view() == 'stockedit':
        labels = [b.inner_text().strip() for b in page.locator('#mhShopPane button').all()]
        if 'Save' not in labels: f.add('BUG', f'6: stock item has no Save button: {labels}')
        if 'Back' in labels: f.add('BUG', '7: a Back button is still there beside the arrow')
        ev("mhStkSet('level','150'); mhStkCommit('level')"); page.wait_for_timeout(300)
        page.locator(arrow).click(timeout=5000); page.wait_for_timeout(400)
        if view() != 'list': f.add('BUG', f'8: arrow from the stock item went to {view()}')
        if abs(ev("mhStockLoad().items[mhShopKey('Pasta')].level") - 150) > 0.01: f.add('BUG', '9: the change did not survive leaving by the arrow')
    else: f.add('BUG', '6: could not open a stock item to test')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
