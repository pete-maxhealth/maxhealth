"""Persona 274: My cupboards can be filtered by shop (v3.10.1169). Pete could not see what is in his Heylo cupboard. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const s=mhShopLoad(); ['Heylo','Asda'].forEach(n=>{if(!s.shops.includes(n)) s.shops.push(n)}); mhShopSave(s);
      [['Zz Flatbread','Heylo'],['Zz Crackers','Heylo'],['Zz Beans','Asda'],['Zz Rice','Asda'],['Zz Salt','']].forEach(([n,sh])=>{mhStockTrack(n,{base:'g',shop:sh||undefined}); mhStockSetLevel(mhShopKey(n),100);});})()""")
    ev("switchTabById('shop')"); ev("mhShopView('list')"); page.wait_for_timeout(500)
    names = lambda: ev("[...document.querySelectorAll('[data-stock]')].map(e=>e.dataset.stock).sort()")
    if len(names()) != 5: f.add('BUG', f'all shops shows every food: {names()}')
    page.click('[data-cbshop="Heylo"]'); page.wait_for_timeout(300)
    if names() != ['Zz Crackers', 'Zz Flatbread']: f.add('BUG', f'Heylo shows only Heylo foods: {names()}')
    page.click('[data-cbshop="Asda"]'); page.wait_for_timeout(300)
    if names() != ['Zz Beans', 'Zz Rice']: f.add('BUG', f'Asda shows only Asda foods: {names()}')
    page.click('[data-cbshop="__none"]'); page.wait_for_timeout(300)
    if names() != ['Zz Salt']: f.add('BUG', f'No shop shows the unassigned: {names()}')
    page.click('[data-cbshop="Heylo"]'); page.reload(); page.wait_for_timeout(1500)
    ev("document.getElementById('onboardingOverlay')?.remove()"); ev("switchTabById('shop')"); ev("mhShopView('list')"); page.wait_for_timeout(500)
    if names() != ['Zz Crackers', 'Zz Flatbread']: f.add('BUG', f'the shop filter is remembered: {names()}')
    page.click('[data-cbshop=""]'); page.wait_for_timeout(300)
    if len(names()) != 5: f.add('BUG', 'All shops brings everything back')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
