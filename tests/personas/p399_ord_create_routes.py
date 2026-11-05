"""Persona 399: "Create new" on an import line goes down the Log routes, typing last (v3.10.1293). Pete (5 Nov): "Typing should be a last resort not a default setting".
Covers: chooser order, search/AI open the shared search panel prefilled, a result saves to the library only (no meal logged), you land back on the list with the line linked,
the panel has no Log button/amount while owned by the import, cancel leaves nothing behind (normal Log panel unchanged), Type it still reaches Add Food, scan sets and expires the target.
Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTabById('shop'); mhOrdOpen('receipt')"); page.wait_for_timeout(400)
    ev("t=>mhOrdLoad(t,'test')", "1 x Zzqx Oat Biscuits 300g\t£1.20\n2 x Zzqx Hazel Spread 350g\t£3.00"); page.wait_for_timeout(500)
    snap = lambda: ev("JSON.stringify(Object.keys(localStorage).filter(k=>/log|meal|entries/i.test(k)&&!/library|stock|shop/i.test(k)).sort().map(k=>[k,localStorage.getItem(k)]))")
    before = snap(); lib0 = ev("loadLibrary().length")
    # 1 chooser
    ev("mhOrdCreate(0)"); page.wait_for_timeout(300)
    labs = ev("[...document.querySelectorAll('[data-create] button')].map(b=>b.textContent.trim())")
    if len(labs) != 4 or not labs[0].startswith('🔍') or not labs[1].startswith('✨') or not labs[2].startswith('📷') or not labs[3].startswith('⌨'): f.add('BUG', f'1: chooser order, typing last: {labs}')
    if ev("document.getElementById('addFoodModal').classList.contains('open')||getComputedStyle(document.getElementById('addFoodModal')).display!=='none'&&document.getElementById('addFoodModal').offsetParent!==null"): f.add('BUG', '2: Create new no longer opens the typed form straight away')
    same = ev("(()=>{const a=document.querySelector('[data-create] button'),b=[...document.querySelectorAll('[data-ord=\"0\"] button')].find(x=>/Match/.test(x.textContent));return a.className===b.className&&getComputedStyle(a).fontSize===getComputedStyle(b).fontSize})()")
    if not same: f.add('BUG', '3: chooser buttons look like the row buttons')
    page.screenshot(path='/tmp/p399_chooser.png')
    # 2 search online
    ev("mhOrdFind(0,'search')"); page.wait_for_timeout(500)
    if not ev("document.getElementById('foodSearchOverlay').classList.contains('open')"): f.add('BUG', '4: search opens the shared panel')
    if 'Oat Biscuits' not in ev("document.getElementById('foodSearchInput').value"): f.add('BUG', '5: search prefilled with the line name')
    ev("_selectedFoodItem={name:'Zzqx Oat Biscuits',brand:'Zzqx',kcal:450,prot:7,carb:60,fat:20,fibre:3,polyols:0,satFat:9,sugars:20,salt:1};document.getElementById('foodSearchView').style.display='none';document.getElementById('foodAmountView').classList.add('open')"); page.wait_for_timeout(300)
    vis = lambda sel: ev("s=>{const e=document.querySelector(s);return !!e&&getComputedStyle(e).display!=='none'}", sel)
    if vis('.food-amount-log'): f.add('BUG', '6: no Log button while an import line owns the panel')
    if vis('.food-amount-row'): f.add('BUG', '7: no amount box while an import line owns the panel')
    if 'library' not in ev("document.querySelector('.food-amount-save').textContent"): f.add('BUG', '8: Save says it goes to the library')
    page.screenshot(path='/tmp/p399_panel.png')
    ev("saveFoodToLibraryFromPanel()"); page.wait_for_timeout(500)
    if ev("document.getElementById('foodSearchOverlay').classList.contains('open')"): f.add('BUG', '9: panel closes after saving')
    row = ev("(_shopUi.ord.rows[0])&&{t:_shopUi.ord.rows[0].track,f:_shopUi.ord.rows[0].from}")
    if not row or 'Zzqx Oat Biscuits' not in row['t'] or 'saved' not in (row['f'] or ''): f.add('BUG', f'10: line linked to the saved food: {row}')
    if ev("loadLibrary().length") != lib0 + 1: f.add('BUG', '11: one library entry added')
    if snap() != before: f.add('BUG', '12: nothing is logged as a meal')
    if ev("_shopUi.view") != 'orderimport': f.add('BUG', '13: back on the import list')
    if ev("_ordSearchTarget") is not None: f.add('BUG', '14: target cleared after saving')
    # 3 AI
    ev("mhOrdFind(1,'ai')"); page.wait_for_timeout(500)
    if not ev("document.getElementById('foodSearchOverlay').classList.contains('open')"): f.add('BUG', '15: AI opens the shared panel')
    ev("closeFoodSearch()")
    if ev("_ordSearchTarget") is not None: f.add('BUG', '16: cancelling clears the target')
    # 4 normal Log panel unaffected afterwards
    ev("openFoodSearch();_selectedFoodItem={name:'Zzqx Plain',brand:'',kcal:100,prot:1,carb:1,fat:1};document.getElementById('foodSearchView').style.display='none';document.getElementById('foodAmountView').classList.add('open')"); page.wait_for_timeout(300)
    if not vis('.food-amount-log') or not vis('.food-amount-row'): f.add('BUG', '17: ordinary Log panel keeps Log and amount')
    if ev("document.querySelector('.food-amount-save').textContent.trim()") != '💾 Save': f.add('BUG', '18: ordinary Save label unchanged')
    ev("closeFoodSearch()")
    # 5 type it
    ev("mhOrdCreate(1)"); ev("mhOrdFind(1,'type')"); page.wait_for_timeout(400)
    if 'Hazel' not in ev("document.getElementById('addFoodName').value") or not ev("_addFoodOrdContext"): f.add('BUG', '19: Type it opens Add Food with the name and returns to the line')
    # 6 scan sets target
    ev("closeAddFoodModal()"); ev("mhOrdFind(1,'scan')"); page.wait_for_timeout(300)
    if not ev("_ordSearchTarget"): f.add('BUG', '20: scan sets the target')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
