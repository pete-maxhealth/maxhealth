"""Persona 290: on a Needs details row, how a food is counted stays a dropdown after an amount is typed, and changing it asks first and clears the amounts (v3.10.1189). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhStockTrack('Zzqx Noodles',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Noodles'),228)")
    ev("switchTabById('shop')"); page.wait_for_timeout(400)
    ev("_shopUi.view='stocklist'; mhSlState().f='all'; mhSlState().q='Zzqx Noodles'; mhShopRender()"); page.wait_for_timeout(500)
    sel = '[data-sl] select[data-f="unitset"]'
    if not page.locator(sel).count(): f.add('BUG', 'a tracked food shows a unit dropdown on its row')
    else:
        page.select_option(sel, 'ml'); page.wait_for_timeout(300)
        if not page.locator('#appModalConfirm').count(): f.add('BUG', 'changing the unit asks first when there is an amount')
        else:
            page.click('#appModalConfirm'); page.wait_for_timeout(500)
            it = ev("mhStockLoad().items[mhShopKey('Zzqx Noodles')]")
            if it['base'] != 'ml' or it['level'] is not None: f.add('BUG', f'it is now counted in ml with the amounts cleared: {it}')
    # cancelling leaves it alone
    ev("mhStockTrack('Zzqx Beans',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Beans'),100); mhSlState().q='Zzqx Beans'; mhShopRender()"); page.wait_for_timeout(400)
    page.select_option(sel, 'each'); page.wait_for_timeout(300)
    if page.locator('#appModalCancel').count(): page.click('#appModalCancel'); page.wait_for_timeout(300)
    elif page.locator('#appModalClose').count(): page.click('#appModalClose'); page.wait_for_timeout(300)
    if ev("mhStockLoad().items[mhShopKey('Zzqx Beans')].base") != 'g': f.add('BUG', 'cancelling keeps it in g')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
