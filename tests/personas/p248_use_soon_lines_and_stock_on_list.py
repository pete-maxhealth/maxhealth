"""Persona 248: Use soon is one line per food with its amount and a 💡 Ideas button that focuses the meal-idea prompt on it; shopping list rows show the stock behind them (v3.10.1143).
Pete: "1 entry per line, go to ingredient, get a suggestion" and "display stock amount alongside the ingredient so nothing is unexpected". Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("saveLibrary([{id:'l1',name:'Zzqx Kimchi',kcal:60,protein:2,carbs:8,fat:1,portion:'100g',useCount:5},{id:'l2',name:'Zzqx Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5}])")
    ev("""(()=>{ mhStockTrack('Zzqx Kimchi',{base:'g',pack:400,shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Kimchi'),400);
      mhStockTrack('Zzqx Cheddar',{base:'g',pack:400,shop:'Asda'}); mhStockSetLevel(mhShopKey('Zzqx Cheddar'),800);
      const o=mhStockLoad(); const d=new Date(Date.now()+86400000), y=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
      Object.values(o.items).forEach(i=>{i.useBy=y;}); mhStockSave(o); })()""")
    ev("mhShopOpen()"); page.wait_for_timeout(400)
    rows = ev("[...document.querySelectorAll('[data-soon-row]')].map(e=>e.innerText.replace(/\\n+/g,' | '))")
    if len(rows) != 2: f.add('BUG', f'1: one line per food: {rows}')
    elif not any('Zzqx Kimchi' in r and '400' in r and 'tomorrow' in r for r in rows): f.add('BUG', f'2: each line shows its amount and when: {rows}')
    # Ideas button: the prompt is focused on that food, and the focus is cleared afterwards
    ev("window.__p=''; window.callHealthAI=async(p)=>{window.__p=p; return {ok:true,text:'{\"combos\":[]}'}}")
    ev("mhUseUpIdea('Zzqx Kimchi')"); page.wait_for_timeout(900)
    p = ev("window.__p") or ''
    if 'FOCUS' not in p or 'Zzqx Kimchi' not in p.split('FOCUS')[1][:200]: f.add('BUG', '3: Ideas asks the AI to build around that food')
    ev("window.__p=''; suggestMealFromLibrary('both')"); page.wait_for_timeout(700)
    if 'FOCUS' in (ev("window.__p") or ''): f.add('BUG', '4: the focus is cleared afterwards')
    # buttons exist on the lines
    if page.locator('[data-soon-row] button:has-text("Ideas")').count() != 2: f.add('BUG', '5: an Ideas button on each line')
    # shopping list shows stock
    ev("(()=>{const s=mhShopLoad(); s.items=[]; mhShopSave(s); mhStockLowNow(mhShopKey('Zzqx Cheddar'));})()")
    ev("mhShopView('list')"); page.wait_for_timeout(300)
    t = ev("document.querySelector('[data-item^=\"Zzqx Cheddar\"]')?.innerText||''")
    if 'running low' not in t or '800' not in t: f.add('BUG', f'6: the list row shows the stock behind it: {t!r}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
