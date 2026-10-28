"""Persona 347 (v3.10.1234): logging a food picked from your own library no longer asks "Save to your library?" again.
A genuinely new food (not in the library) still offers to save. Library size is unchanged by logging a library food."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 430, 'height': 1000}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    ev("switchTab('log',document.getElementById('maintab-log'))"); p.wait_for_timeout(600)
    n0 = ev("loadLibrary().length")
    modal_open = lambda: ev("document.getElementById('saveLibraryModal').classList.contains('open')")
    for letters, chip in (('egg', 1), ('butt', None)):
        ev("openFoodSearch()"); p.wait_for_timeout(500)
        p.locator('#foodSearchInput').fill(letters); p.wait_for_timeout(900)
        p.locator('[onclick*="selectLibraryResult(0"]').first.click(); p.wait_for_timeout(700)
        if chip is not None: p.locator('[onclick*="setPortionSuggestion"]:visible').nth(chip).click()
        else: p.locator('#foodAmountGrams').fill('10')
        p.wait_for_timeout(400); p.locator('[onclick*="logFoodFromDatabase"]:visible').click(); p.wait_for_timeout(1500)
        if modal_open(): f.add('BUG', f'"{letters}": library food offered for saving again')
    if ev("loadLibrary().length") != n0: f.add('BUG', 'library size changed after logging library foods')
    meals = ev("JSON.stringify(state.todayLog||[]).toLowerCase()")
    if 'egg' not in meals or 'butter' not in meals: f.add('BUG', 'logged foods missing from today: ' + meals[:200])
    # a food that is NOT in the library still offers to save
    ev("closeSaveLibraryModal()")
    ev("_selectedFoodItem={name:'Zzz test crisps',brand:'',kcal:500,prot:6,carb:50,fat:30,fibre:0,polyols:0}; _lastFoodSourceType='barcode'; document.getElementById('foodAmountGrams').value='30'; logFoodFromDatabase()")
    p.wait_for_timeout(1500)
    if not modal_open(): f.add('BUG', 'a genuinely new food must still offer "Save to your library?"')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f); print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
