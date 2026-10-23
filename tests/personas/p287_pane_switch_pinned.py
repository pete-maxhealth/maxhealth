"""Persona 287: the Shopping list / My cupboards switch stays in view when scrolled down a long list, and works from there (v3.10.1183). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("const s=mhShopLoad(); for(let i=0;i<60;i++)mhShopSetAdd(s,'Zzqx Item '+i,'own','',null); mhShopSave(s); mhStockTrack('Zzqx Rice',{base:'g'})")
    ev("localStorage.setItem('mh_shop_folds',JSON.stringify({fold:{},cb:{fold:{}}})); window.mhShopIsShut=()=>false")
    ev("switchTabById('shop')"); page.wait_for_timeout(600)
    ev("window.scrollTo(0, document.body.scrollHeight)"); ev("document.querySelectorAll('*').forEach(e=>{if(e.scrollHeight>e.clientHeight+200&&/auto|scroll/.test(getComputedStyle(e).overflowY))e.scrollTop=e.scrollHeight})"); page.wait_for_timeout(300)
    r = ev("(()=>{const e=document.getElementById('mhShopSwitch').getBoundingClientRect();return {t:e.top,b:e.bottom}})()")
    if r['t'] < -1 or r['b'] > 800: f.add('BUG', f'the switch is on screen after scrolling down: {r}')
    page.click('#mhShopSwitch [data-pane="stock"]'); page.wait_for_timeout(400)
    if not page.locator('#mhShopSwitch').count(): f.add('BUG', 'the switch is there on the cupboards pane too')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
