"""Persona 306: an entry on an earlier day can be marked 'ate out' from History: its stock is put back and it is left alone; tapping again takes it off again (v3.10.1208). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("window._mhLibQuiet=true")
    ev("mhStockTrack('Zzqx Cream',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Cream'),500); (()=>{const o=mhStockLoad(); o.items[mhShopKey('Zzqx Cream')].since=Date.parse('2026-10-01'); mhStockSave(o)})()")
    ev("(()=>{ const e={id:987654, name:'Zzqx Cream', description:'Zzqx Cream (250g)', time:'18:48', kcal:300, protein:2, carbs:3, fat:30, items:[{name:'Zzqx Cream', amount:'250g', kcal:300, protein:2, carbs:3, fat:30}]}; state.history.unshift({date:'20/10/26', log:[e], totals:{kcal:300,protein:2,carbs:3,fat:30}}); saveState(); mhStockOnLog(e,'2026-10-20'); })()")
    lv = lambda: ev("mhStockLoad().items[mhShopKey('Zzqx Cream')].level")
    after = lv()
    if after >= 500: f.add('BUG', f'setup: the meal took stock off: {after}')
    ev("switchTabById('hist')"); page.wait_for_timeout(500); ev("renderHistory()"); ev("(()=>{const h=document.querySelector('.hist-day-header, .hist-day'); h&&h.click(); const b=document.querySelector('.hist-day-body'); if(b) b.style.display='block'})()"); page.wait_for_timeout(300)
    if not ev("!!document.querySelector('[data-hist-ateout=\"987654\"]')"): f.add('BUG', 'History shows the ate-out button')
    glyphH = ev("[...document.querySelector('[data-hist-ateout=\"987654\"]').textContent].map(c=>c.codePointAt(0))"); glyphT = [0x1f37d]
    if glyphH != glyphT: f.add('BUG', f'History uses the same plate character as Today ({glyphH})')
    ev("mhStockAteOutHist('20/10/26',987654)"); page.wait_for_timeout(200)
    if lv() != 500: f.add('BUG', f'ate out puts the stock back: {lv()}')
    if not ev("state.history[0].log[0].noStock"): f.add('BUG', 'the entry is marked ate out')
    ev("mhStockAteOutHist('20/10/26',987654)"); page.wait_for_timeout(200)
    if lv() >= 500: f.add('BUG', f'tapping again takes the stock off again: {lv()}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
