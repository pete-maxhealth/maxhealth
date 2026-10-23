"""Persona 277: list and cupboard aisles start closed, opening one is remembered across a reload, a search opens them (v3.10.1172). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SEED = """(()=>{['Chicken Breast','Cheddar','Pasta','Beef Mince','Butter','Frozen Peas','Olive Oil','Basmati Rice','Spinach Bag','Whole Milk'].forEach(n=>{mhStockTrack(n,{base:'g',shop:'Asda'});mhStockSetLevel(mhShopKey(n),500);});const s=mhShopLoad();['Milk','Spinach'].forEach(n=>mhShopSetAdd(s,n,'own','',null));mhShopSave(s);})()"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev(SEED)
    ev("switchTabById('shop')"); page.wait_for_timeout(600)
    lst = "document.querySelectorAll('#mhShopPane [data-item]').length"; cup = "document.querySelectorAll('#stockctlCard [data-stock]').length"
    if ev(lst) != 0 or ev(cup) != 0: f.add('BUG', f'sections start closed: list rows {ev(lst)}, cupboard rows {ev(cup)}')
    if not ev("document.querySelectorAll('#stockctlCard [data-cb-aisle]').length"): f.add('BUG', 'cupboard aisle headings are still shown')
    ev("document.querySelector('#stockctlCard [data-cb-aisle]').click()"); page.wait_for_timeout(300)
    n1 = ev(cup)
    if n1 < 1: f.add('BUG', 'tapping an aisle opens it')
    ev("document.querySelector('#mhShopPane .mh-aisle span[onclick]').click()"); page.wait_for_timeout(300)
    if ev(lst) < 1: f.add('BUG', 'tapping a list aisle opens it')
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("switchTabById('shop')"); page.wait_for_timeout(600)
    if ev(cup) != n1 or ev(lst) < 1: f.add('BUG', f'what you opened stays open after a reload: cupboard {ev(cup)} (was {n1}), list {ev(lst)}')
    ev("mhCbFoldAll(true)"); ev("mhCbState().q='cheddar'; mhShopRender()"); page.wait_for_timeout(300)
    if ev(cup) < 1: f.add('BUG', 'a search shows its matches even when aisles are closed')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
