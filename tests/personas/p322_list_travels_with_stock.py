"""Persona 322 (v3.10.1216): the shopping list (with its counts) travels in the stock file; receiving it replaces the other phone's list, after asking; the Other phone screen opens from the list. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("mhStockTrack('Zz Rice',{base:'g',pack:1000,shop:'Asda'}); mhStockSetLevel(mhShopKey('Zz Rice'),500)")
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zz Cream','own','',null,{qty:2}); mhShopSetAdd(s,'Zz Jam','own'); mhShopSave(s);})()")
    ev("switchTabById('shop'); mhShopOpen(); _shopUi.addOpen = true; mhShopRender()"); page.wait_for_timeout(300)
    if not ev("!!document.querySelector('.mh-tile') && [...document.querySelectorAll('.mh-tile')].some(b=>b.innerText.includes('Other phone'))"): f.add('BUG', 'the list screen has an Other phone tile')
    else:
        ev("[...document.querySelectorAll('.mh-tile')].find(b=>b.innerText.includes('Other phone')).click()"); page.wait_for_timeout(300)
        if 'Send from this phone' not in page.inner_text('body'): f.add('BUG', 'the Other phone screen offers Send and Receive')
    pack = ev("mhStockExport('Master')")
    if not pack or not pack.get('list') or len(pack['list']['items']) != 2: f.add('BUG', f'the file carries the list: {pack and pack.get("list")}')
    # the "other phone" has its own list
    ev("(()=>{const s=mhShopLoad(); s.items=[]; mhShopSetAdd(s,'Zz Other thing','own'); mhShopSave(s);})()")
    ev("localStorage.setItem('mh_last_full_backup_date', todayStr())")
    ev("p=>mhStockImportStart(p)", pack); page.wait_for_timeout(300)
    if 'shopping list' not in page.inner_text('body'): f.add('BUG', 'it says the list is replaced too')
    page.click('#appModalConfirm'); page.wait_for_timeout(500)
    got = ev("JSON.stringify(mhShopLoad().items.map(i=>[i.name,i.qty||1]).sort())")
    if got != '[["Zz Cream",2],["Zz Jam",1]]': f.add('BUG', f'the list is the master\'s, counts included: {got}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
