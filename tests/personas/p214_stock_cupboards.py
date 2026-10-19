"""Persona 214: Check the cupboards (v3.10.1121). Pete walks a long ingredient list typing what he has; every box saves as he goes, no submit.
Covers: the list shows every known ingredient with boxes (have, reorder at, one serving, shop); the library's portion unit and size are
shown for untracked rows but nothing is saved until an amount is given; an amount with no way to know the unit is refused and names the
problem (never guesses); a unit from the box or typed ("500 g") starts tracking; servings work both ways; the reorder box; a bad entry shows
on the row and saves nothing; shop and serving edits on a tracked row; going low puts it on the list; the filter box and the chips;
a long list shows the first batch and more on request; editing a row never re-renders the list (scroll and focus stay)."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    lib = [{'name': n, 'kcal': 100, 'protein': 1, 'fat': 1, 'carbs': 1, 'portion': p} for n, p in (('Whey protein', '25g'), ('Double Cream (Asda)', '30ml'), ('Eggs', '1'), ('Butter', '100g'))]
    lib += [{'name': f'Zz Spice {i:03d}', 'kcal': 5, 'protein': 0, 'fat': 0, 'carbs': 1, 'portion': '1g'} for i in range(100)]
    ev("l=>saveLibrary(l.concat(loadLibrary()))", lib); ev("mhShopView('stocklist')"); page.wait_for_timeout(300)
    R = lambda n: page.locator(f'[data-sl="{ev("n=>mhShopKey(n)", n)}"]')
    if R('Whey protein').count() != 1: f.add('BUG', 'a library ingredient must be on the list')
    for fld in ('amt', 'thr', 'serv', 'shop'):
        if not R('Whey protein').locator(f'[data-f="{fld}"]').count(): f.add('BUG', f'row needs a {fld} box')
    if R('Whey protein').locator('[data-f="serv"]').input_value() != '25' or R('Whey protein').locator('[data-f="unit"]').input_value() != 'g': f.add('BUG', 'a known library portion pre-fills the serving box and the unit')
    if ev("Object.keys(mhStockLoad().items).length") != 0: f.add('BUG', 'showing the list must not start tracking anything')
    # unit unknown and none typed: refuse, never guess
    R('Eggs').locator('[data-f="amt"]').fill('6'); R('Eggs').locator('[data-f="amt"]').blur(); page.wait_for_timeout(100)
    if not R('Eggs').locator('[data-err]').is_visible() or ev("Object.keys(mhStockLoad().items).length") != 0: f.add('BUG', 'a bare amount with no unit must be refused and say why, tracking nothing')
    # unit chosen in the box
    R('Eggs').locator('[data-f="unit"]').select_option('each'); R('Eggs').locator('[data-f="amt"]').fill('6'); R('Eggs').locator('[data-f="amt"]').blur(); page.wait_for_timeout(150)
    it = ev("k=>mhStockLoad().items[k]", ev("n=>mhShopKey(n)", 'Eggs'))
    if not it or it['level'] != 6 or it['base'] != 'each': f.add('BUG', f'unit from the box then an amount tracks it: {it}')
    # unit typed with the amount, serving from the box, saved as you go
    w = R('Whey protein'); w.locator('[data-f="amt"]').fill('500 g'); w.locator('[data-f="amt"]').blur(); page.wait_for_timeout(150)
    it = ev("k=>mhStockLoad().items[k]", ev("n=>mhShopKey(n)", 'Whey protein'))
    if not it or it['level'] != 500 or it['serving'] != 25 or it['base'] != 'g': f.add('BUG', f'typed unit starts tracking, library serving kept: {it}')
    w.locator('[data-f="thr"]').fill('5 servings'); w.locator('[data-f="thr"]').blur(); page.wait_for_timeout(150)
    if ev("k=>mhStockLoad().items[k].reorder", ev("n=>mhShopKey(n)", 'Whey protein')) != 125: f.add('BUG', '5 servings of 25 g is 125 g')
    w.locator('[data-f="amt"]').fill('4 servings'); w.locator('[data-f="amt"]').blur(); page.wait_for_timeout(150)
    if ev("k=>mhStockLoad().items[k].level", ev("n=>mhShopKey(n)", 'Whey protein')) != 100: f.add('BUG', '4 servings is 100 g')
    if not ev("k=>mhShopLoad().items.some(i=>i.key===k)", ev("n=>mhShopKey(n)", 'Whey protein')): f.add('BUG', 'at 100 g with reorder 125 g it must go on the shopping list')
    if 'low' not in w.locator('[data-st]').inner_text(): f.add('BUG', 'the row must show it is low')
    # bad entry saves nothing
    w.locator('[data-f="amt"]').fill('lots'); w.locator('[data-f="amt"]').blur(); page.wait_for_timeout(100)
    if ev("k=>mhStockLoad().items[k].level", ev("n=>mhShopKey(n)", 'Whey protein')) != 100 or not w.locator('[data-err]').is_visible(): f.add('BUG', 'a bad entry must show on the row and change nothing')
    # shop and serving on a tracked row
    ev("mhShopAddShop = mhShopAddShop; window.prompt=()=>'Tesco'"); ev("mhShopAddShop()"); ev("mhShopView('stocklist')"); page.wait_for_timeout(300)
    w = R('Whey protein'); w.locator('[data-f="shop"]').select_option('Tesco'); page.wait_for_timeout(100)
    w.locator('[data-f="serv"]').fill('30'); w.locator('[data-f="serv"]').blur(); page.wait_for_timeout(150)
    it = ev("k=>mhStockLoad().items[k]", ev("n=>mhShopKey(n)", 'Whey protein'))
    if it['shop'] != 'Tesco' or it['serving'] != 30 or it['level'] != 100: f.add('BUG', f'shop and serving save without touching the amount: {it}')
    # filters
    page.fill('#mhSlQ', 'whey'); page.wait_for_timeout(200)
    if page.locator('[data-sl]').count() != 1: f.add('BUG', 'the text filter narrows the list')
    page.fill('#mhSlQ', ''); page.wait_for_timeout(200); page.click('button[data-f="tracked"]'); page.wait_for_timeout(200)
    if page.locator('[data-sl]').count() != 2: f.add('BUG', f'Tracked chip shows tracked rows only: {page.locator("[data-sl]").count()}')
    page.click('button[data-f="low"]'); page.wait_for_timeout(200)
    if page.locator('[data-sl]').count() != 1: f.add('BUG', 'Low chip shows low rows only')
    page.click('button[data-f="not"]'); page.wait_for_timeout(200)
    if page.locator('[data-sl]').count() != 60 or 'Show more' not in page.inner_text('#mhShopPane'): f.add('BUG', 'a long list shows the first batch and offers more')
    page.click('text=Show more'); page.wait_for_timeout(200)
    if page.locator('[data-sl]').count() <= 60: f.add('BUG', 'Show more shows more')
    # editing a row must not rebuild the list
    page.click('button[data-f="all"]'); page.wait_for_timeout(200)
    ev("document.querySelector('#mhSlRows').dataset.mark='x'")
    R('Butter').locator('[data-f="amt"]').fill('250 g'); R('Butter').locator('[data-f="amt"]').blur(); page.wait_for_timeout(150)
    if ev("document.querySelector('#mhSlRows').dataset.mark") != 'x': f.add('BUG', 'saving a row must not re-render the list (it would lose your place)')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
