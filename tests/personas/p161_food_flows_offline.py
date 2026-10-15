"""Persona 161: core food flows with no internet, on demo personas (everyday + low-carb): type a meal, log a library recipe,
barcode and food-database search explain themselves, recipe builder picks from the library, 'what fits' suggestions appear and
their ingredient picker offers the whole library. No JS errors anywhere."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def clicktext(page, txt):
    return page.evaluate("""(txt)=>{const els=[...document.querySelectorAll('button,span,div,a')].filter(e=>e.offsetParent&&e.textContent.includes(txt)).sort((a,b)=>a.textContent.length-b.textContent.length); if(!els[0]) return false; els[0].scrollIntoView({block:'center'}); els[0].click(); return true}""", txt)
def toasts(page): return page.evaluate("()=>[...document.querySelectorAll('.toast,#toast,[id*=oast]')].map(e=>e.innerText).filter(Boolean).join(' | ')")
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    for pid in ['alex', 'raj']:
        ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
        page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:160])); page.on('dialog', lambda d: d.dismiss())
        page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
        page.evaluate(f"startDemoMode('{pid}')"); page.wait_for_timeout(2500)
        ctx.set_offline(True); page.evaluate("window.dispatchEvent(new Event('offline'))"); page.wait_for_timeout(1200)
        page.evaluate("document.getElementById('maintab-log').click()"); page.wait_for_timeout(500)
        # 1 typed meal gets a preview
        page.fill('#chatInput', '2 eggs and a slice of toast'); page.evaluate("document.querySelector(\"button[onclick*='sendChat']\").click()"); page.wait_for_timeout(5000)
        if not page.evaluate("/READY TO LOG/i.test(document.body.innerText)"): f.add('FAIL', f'{pid}: typed meal offline gave no preview')
        page.evaluate("typeof cancelPreview==='function' && cancelPreview()")
        # 2 log a library recipe
        page.evaluate("document.getElementById('logtab-library').click()"); page.wait_for_timeout(700)
        n0 = page.evaluate("state.todayLog.length")
        clicktext(page, 'Log 1 serving'); page.wait_for_timeout(2500); clicktext(page, 'Log this meal'); page.wait_for_timeout(1500)
        if page.evaluate("state.todayLog.length") <= n0: f.add('FAIL', f'{pid}: library recipe did not log offline')
        # 3 barcode + food search explain themselves
        page.evaluate("openLiveBarcodeScanner()"); page.wait_for_timeout(800)
        if 'needs internet' not in toasts(page): f.add('FAIL', f'{pid}: barcode gave no offline explanation')
        page.evaluate("tryAISearchForIngredient('chicken')"); page.wait_for_timeout(800)
        if 'needs internet' not in toasts(page): f.add('FAIL', f'{pid}: food search gave no offline explanation')
        # 4 recipe builder picker
        page.evaluate("recipeAddFromLibrary()"); page.wait_for_timeout(600)
        rows = page.evaluate("document.querySelectorAll('#recipeLibPickerList [onclick*=_libPickerItemChosen]').length")
        if rows < 40: f.add('FAIL', f'{pid}: recipe picker offers only {rows} items')
        page.evaluate("closeRecipeLibPicker()")
        # 5 'what fits' suggestions and their ingredient picker
        page.evaluate("suggestMealFromLibrary('both')"); page.wait_for_timeout(5000)
        n = page.evaluate("(window._pendingLibraryCombos||[]).length")
        if not n: f.add('FAIL', f'{pid}: no meal suggestions offline')
        else:
            page.evaluate("openLibraryPickerForCombo(0)"); page.wait_for_timeout(500)
            rows = page.evaluate("document.querySelectorAll('#recipeLibPickerList [onclick*=_libPickerItemChosen]').length")
            if rows < 40: f.add('FAIL', f'{pid}: suggestion ingredient picker offers only {rows} items')
        print(pid, 'ok so far')
        ctx.close()
    br.close()
print('findings', len(f)); sys.exit(1 if f else 0)
