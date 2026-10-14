"""Persona 149: Meal plan is its own Today card with move / hide / fold controls; old saved orders gain it after Calories & macros."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState(); localStorage.setItem('mh_dashboard_order', JSON.stringify(['weight','daymode','ketosis','macros','macroratio','goalcheck','steps','symptoms','treatment','activity','weather','fasting','water','log','guides']))")
    page.reload(); page.wait_for_timeout(1800)
    o = ev("getDashboardOrder()")
    if o.index('mealplan') != o.index('macros') + 1: f.add('BUG', f'old saved order not migrated: {o}')
    if ev("document.getElementById('dashSection-macros').contains(document.getElementById('mhPlanBlock'))"): f.add('BUG', 'meal plan still inside the macros card')
    if not ev("document.getElementById('dashSection-mealplan').contains(document.getElementById('mhPlanBlock'))"): f.add('BUG', 'plan block not in its own card')
    for fn in ("moveDashboardSection('mealplan','up')", "moveDashboardSection('mealplan','down')", "toggleDashboardSectionHidden('mealplan')"):
        if fn not in ev("document.getElementById('dashSection-mealplan').innerHTML").replace('&#39;', "'"): f.add('BUG', f'missing control {fn}')
    ev("mhPlanRender()")
    if 'Plan a meal' not in ev("document.getElementById('mhPlanBlock').textContent"): f.add('BUG', 'plan a meal button missing')
    ev("toggleDashboardSectionHidden('mealplan')"); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('dashSection-mealplan')).display") != 'none': f.add('BUG', 'hide did not hide the card')
    ev("toggleDashboardSectionHidden('mealplan')"); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('dashSection-mealplan')).display") == 'none': f.add('BUG', 'restore did not show the card')
    if 'mealplan' not in ev("MH_DASH_CARDS.map(c=>c[0])"): f.add('BUG', 'not in the fold list')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
