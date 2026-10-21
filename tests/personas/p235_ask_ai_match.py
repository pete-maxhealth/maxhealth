"""Persona 235: "Ask AI" in the Match picker (v3.10.1128). The AI only ever chooses from foods the person already has. A reply that is not exactly one of their names
is thrown away; a good one is offered with "Use this" and never links on its own; pressing it turns the row green Matched; an AI outage says so and leaves manual matching. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary([{id:'l1',name:'Seriously Strong Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g'},{id:'l2',name:'Plain Rice',kcal:350,protein:7,carbs:78,fat:1,portion:'100g'}])")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "SS CHSE 400G\n2.00\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    ev("window._prompt=null; window.callHealthAI = async (p)=>{window._prompt=p; return {ok:true,text:'\"Seriously Strong Cheddar\".'}}; 0")
    if not ev("!!document.querySelector('[data-ord=\"0\"] button:not([disabled])')"): f.add('BUG', '0: row rendered')
    page.click('[data-ord="0"] button:has-text("Ask AI")'); page.wait_for_timeout(500)
    pr = ev("window._prompt") or ''
    if 'SS CHSE' not in pr or 'Seriously Strong Cheddar' not in pr or 'Plain Rice' not in pr or 'NONE' not in pr: f.add('BUG', f'1: the AI is shown the line and only the person\'s own foods: {pr[:200]}')
    if ev("_shopUi.ord.rows[0].from") not in (None, '', False) and ev("_shopUi.ord.rows[0].from") == 'picked by you': f.add('BUG', '2: the AI answer links nothing by itself')
    if not ev("!!document.querySelector('[data-ai] button')"): f.add('BUG', '3: a Use this button is offered')
    page.click('[data-ai] button:has-text("Use this")'); page.wait_for_timeout(300)
    if ev("document.querySelector('[data-ord=\"0\"] .mh-match-badge')?.dataset.state") != 'matched' or ev("_shopUi.ord.rows[0].track") != 'Seriously Strong Cheddar': f.add('BUG', '4: Use this turns the row green Matched')
    # invented name is thrown away
    ev("mhOrdOpen('receipt')"); ev("_shopUi.ord.rows[0].from=null; _shopUi.ord.rows[0].track='SS CHSE'; mhShopRender()")
    ev("window.callHealthAI = async ()=>({ok:true,text:'Wensleydale Deluxe'}); 0"); page.click('[data-ord="0"] button:has-text("Ask AI")'); page.wait_for_timeout(500)
    if ev("!!document.querySelector('[data-ai] button')") or 'did not find' not in (ev("document.querySelector('[data-ai]')?.textContent") or ''): f.add('BUG', '5: a name that is not one of theirs is thrown away')
    ev("window.callHealthAI = async ()=>({ok:true,text:'NONE'}); 0"); ev("mhOrdAskAI(0)"); page.wait_for_timeout(400)
    if ev("!!document.querySelector('[data-ai] button')"): f.add('BUG', '6: NONE offers nothing')
    ev("window.callHealthAI = async ()=>({ok:false,error:'offline'}); 0"); ev("mhOrdAskAI(0)"); page.wait_for_timeout(400)
    if 'not available' not in (ev("document.querySelector('[data-ai]')?.textContent") or ''): f.add('BUG', '7: an outage is explained and manual matching remains')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
