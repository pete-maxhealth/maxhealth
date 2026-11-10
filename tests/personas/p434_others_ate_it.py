"""Persona 434: "Others ate it" on Use soon lines and on the Past use-by line takes stock off without counting it as waste or as your meal; Undo puts it back (v3.10.1332).
Pete (9 Nov 2026): "no way to delete expired portions that other people ate". Also: removing a different cupboard food leaves you on the same screen (his Ideas screen popped up). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','both')")
    ev("""(()=>{ ['Zzqx Pate','Zzqx Cheddar','Zzqx Old Ham'].forEach(n=>{ mhStockTrack(n,{base:'g',pack:400,shop:'Asda'}); mhStockSetLevel(mhShopKey(n),400); });
      const o=mhStockLoad(), iso=n=>{const d=new Date(Date.now()+n*86400000); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
      o.items[mhShopKey('Zzqx Pate')].useBy=iso(1); o.items[mhShopKey('Zzqx Cheddar')].useBy=iso(2); o.items[mhShopKey('Zzqx Old Ham')].useBy=iso(-2); mhStockSave(o); })()""")
    ev("mhShopOpen()"); page.wait_for_timeout(500)
    lvl = lambda n: ev(f"mhStockLoad().items[mhShopKey('{n}')]?.level")
    mealsBefore = ev("(state.todayLog||[]).length")
    # 1 the button is on each Use soon line, and the link on the Past use-by line, laid out beside Ideas
    if page.locator('[data-soon-row] button:has-text("Others ate")').count() != 2: f.add('BUG', '1a: an Others ate button on each Use soon line')
    if not page.locator('[data-expired] a:has-text("others ate it")').count(): f.add('BUG', '1b: a link on the Past use-by line')
    # 1c (v3.10.1361) the name on the Past use-by line opens the food to check its amount and use-by date
    page.locator('[data-expired] [data-expired-go]').first.click(); page.wait_for_timeout(400)
    if not page.locator('[data-f],#mhStkAmt,[id^="mhStk"]').count() and 'Zzqx Old Ham' not in page.inner_text('body'): f.add('BUG', '1c: tapping an expired name opens the food')
    if ev("!!_shopUi.stk") is not True: f.add('BUG', '1d: the food edit screen opened from Past use-by')
    ev("mhStkBack()"); page.wait_for_timeout(300)
    page.locator('[data-use-soon]').screenshot(path='/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p434_soon.png')
    # 2 part of it: 150 g
    page.locator('[data-soon-row="Zzqx Pate"] button:has-text("Others ate")').click(); page.wait_for_timeout(300)
    page.fill('#appPromptInput', '150'); page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if lvl('Zzqx Pate') != 250: f.add('BUG', f'2a: 150 g off 400 leaves 250: {lvl("Zzqx Pate")}')
    if ev("(mhStockLoad().waste||[]).length"): f.add('BUG', '2b: not counted as waste')
    if ev("(state.todayLog||[]).length") != mealsBefore: f.add('BUG', '2c: not logged as your meal')
    if ev("mhStockLoad().ledger.filter(l=>l.s==='others').length") != 1: f.add('BUG', '2d: recorded in the ledger as eaten by others')
    # 3 Undo puts it back
    page.locator('#toast .toast-undo').click(); page.wait_for_timeout(400)
    if lvl('Zzqx Pate') != 400: f.add('BUG', f'3: Undo puts the 150 g back: {lvl("Zzqx Pate")}')
    # 4 all of it (empty box) on the expired ham: gone from Past use-by, no waste, no meal
    page.locator('[data-expired] a:has-text("others ate it")').click(); page.wait_for_timeout(300)
    page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if lvl('Zzqx Old Ham') != 0 or page.locator('[data-expired]').count(): f.add('BUG', f'4a: the expired ham is off stock and off the Past use-by line: {lvl("Zzqx Old Ham")}')
    if ev("(mhStockLoad().waste||[]).length") or ev("(state.todayLog||[]).length") != mealsBefore: f.add('BUG', '4b: still no waste note and no meal')
    # 5 removing a different cupboard food leaves you on the same screen with no meal-idea picker
    n = page.locator('[onclick*="mhStockUntrackAsk"]').count()
    page.locator('[onclick*="mhStockUntrackAsk"]').nth(n-1).scroll_into_view_if_needed(); page.locator('[onclick*="mhStockUntrackAsk"]').nth(n-1).click(); page.wait_for_timeout(300)
    page.click('#appModalConfirm'); page.wait_for_timeout(1000)
    if ev("!!document.querySelector('.mh-mealpicker')") or not page.locator('#stockctlBody').is_visible(): f.add('BUG', '5: removing a food leaves you on the Shopping screen, no meal-idea picker')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); sys.exit(1 if f else 0)
