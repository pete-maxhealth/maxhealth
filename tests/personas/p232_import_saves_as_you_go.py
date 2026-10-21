"""Persona 232: an import in progress is saved after every change (v3.10.1126). Pick a match, type an amount, untick a line, reload the page: opening Import again
brings it all back (ticks, amounts, the green Matched tick on a food picked by hand). Start again throws it away; applying it clears the saved copy. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary([{id:'l1',name:'Seriously Strong Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},{id:'l2',name:'Plain Rice',kcal:350,protein:7,carbs:78,fat:1,portion:'100g',useCount:1}])")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "Zzqx Strong Cheese 400g\n1.00\nZzqx Wibble Flakes 300g\n3.00\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("mhOrdLink(0,'Seriously Strong Cheddar','picked by you')"); ev("mhOrdSet(0,'amount','800 g')"); ev("mhOrdTick(1,false)"); page.wait_for_timeout(200)
    st = ev("document.querySelector('.mh-match-badge').dataset.state")
    if st != 'matched': f.add('BUG', f'1: a food picked by hand shows the green Matched state: {st}')
    if not ev("!!localStorage.getItem('mh_ord_draft_v1')"): f.add('BUG', '2: draft saved after changes')
    page.reload(); page.wait_for_timeout(1500); ev = page.evaluate
    ev("document.getElementById('onboardingOverlay')?.remove()")
    if ev("_shopUi.ord") is not None: f.add('BUG', '3: reload starts with nothing open (sanity)')
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(300)
    r = ev("(_shopUi.ord&&_shopUi.ord.rows||[]).map(r=>[r.track,r.from,r.amount,r.on])")
    if len(r) != 2 or r[0][0] != 'Seriously Strong Cheddar' or r[0][1] != 'picked by you' or r[0][2] != '800 g' or r[1][3] is not False: f.add('BUG', f'4: everything came back after a reload: {r}')
    if ev("document.querySelector('.mh-match-badge')?.dataset.state") != 'matched': f.add('BUG', '5: green Matched tick still shown after reload')
    ev("document.getElementById('mhOrdRows')||0"); ev("(()=>{const p=document.getElementById('mhShopPane'); for(let i=0;i<30;i++){const d=document.createElement('div'); d.style.height='80px'; d.textContent='pad'; p.appendChild(d);} const sc=document.getElementById('shopScroll'); sc.scrollTop=700; sc.dispatchEvent(new Event('scroll'));})()"); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('globalScrollTopBtn')).display") == 'none': f.add('BUG', '5b: the up arrow shows on the import screen once scrolled down')
    ev("mhShopRender()")
    page.click('button:has-text("Start again")'); page.wait_for_timeout(300)
    if ev("!!localStorage.getItem('mh_ord_draft_v1')") or ev("_shopUi.ord") is not None: f.add('BUG', '6: Start again throws the saved import away')
    page.fill('#mhOrdText', "Plain Rice 1kg\n1.00\n"); page.click('#mhOrdRead'); page.wait_for_timeout(300)
    ev("mhOrdSet(0,'amount','1000 g')"); ev("mhOrdTick(0,true)"); ev("mhOrdApply()"); page.wait_for_timeout(300)
    if ev("!!localStorage.getItem('mh_ord_draft_v1')"): f.add('BUG', '7: applying the import clears the saved copy')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
