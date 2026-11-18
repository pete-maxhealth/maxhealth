"""Persona 499: a food bought that is not a cupboard food is named, not dropped silently (v3.10.1423). Pete ticks Cheese (not in his
cupboards) and Whey (tracked) and taps Shopping complete: the review lists only Whey and says Cheese was not added; with nothing tracked the
list message names it; a ticked item at another shop stays and is said so."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("localStorage.setItem('mh_shop_pane','both')"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    ev("mhStockTrack('Whey protein',{base:'g',pack:750,serving:25,shop:'Asda'})")
    def setup(names, other=None):
        ev("""([ns,o])=>{const s=mhShopLoad();s.items=[];ns.forEach(n=>mhShopSetAdd(s,n,'own','',null));s.items.forEach(i=>{i.checked=true;i.shop=s.shop;});
          if(o){mhShopSetAdd(s,o,'own','',null);const x=s.items[s.items.length-1];x.checked=true;x.shop='Tesco';if(!s.shops.includes('Tesco'))s.shops.push('Tesco');}
          const so=mhStockLoad();delete so.review;mhStockSave(so);mhShopSave(s);}""", [names, other])
        ev("mhShopComplete()"); page.click("#appModalConfirm"); page.wait_for_timeout(250)
    setup(['Whey protein', 'Cheese'])
    t = page.inner_text('#mhShopPane')
    if not page.locator('[data-notin]').count() or 'Cheese' not in page.locator('[data-notin]').inner_text(): f.add('BUG', 'the review must say Cheese is not in the cupboards')
    if page.locator('[data-bought] >> text=Cheese').count(): f.add('BUG', 'Cheese must not be a review row')
    page.click('text=Leave stock as it was'); page.wait_for_timeout(150)
    setup(['Cheese'])
    m = page.inner_text('#mhShopPane')
    if 'Cheese' not in m or 'not added' not in m: f.add('BUG', f'the message names the food that did not go to the cupboards: {m!r}')
    setup(['Cheese'], other='Butter')
    m = page.inner_text('#mhShopPane')
    if 'another shop' not in m or not ev("mhShopLoad().items.some(i=>i.name==='Butter')"): f.add('BUG', f'a ticked item at another shop stays and is said so: {m!r}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
