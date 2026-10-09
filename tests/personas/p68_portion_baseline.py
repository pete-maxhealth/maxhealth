"""Persona 68: the portion edit measures against the amount the entry shows NOW (the form's numbers are for that amount), repeated
edits compound correctly, and a save that changes nothing (e.g. only the meal time) keeps the amount and the portion badge."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    page.evaluate("""state.todayLog = [{id:1, time:'08:00', description:'MCT Oil', amount:'8g', _origAmount:'15g', _portionPct:53, kcal:126, protein:0, fat:14, carbs:0}];
        saveState(); updateDashboard(); switchTab('today')""")
    page.wait_for_timeout(400)
    g = lambda: page.evaluate("(()=>{const e=state.todayLog[0];return [e.amount,e._portionPct||0,e.kcal]})()")
    page.evaluate("editLogEntry(1)"); page.wait_for_timeout(200)
    if '(now 8g)' not in page.evaluate("document.getElementById('log-entry-1').innerText"): f.add('BUG', 'box should say the amount it measures against is the one shown now (8g)')
    page.fill('#edit-grams-1', '8g')
    if abs(page.evaluate("parseFloat(document.getElementById('edit-pct-1').value)") - 100) > 0.2: f.add('BUG', 'typing the current amount should be 100%')
    page.fill('#edit-grams-1', '4g'); page.evaluate("saveLogEdit(1)")
    a, p, k = g()
    if (a, k) != ('4g', 63) or p != 27: f.add('BUG', f'halving 8g should give 4g / 63 kcal / badge 27 (53% x 50%), got {a} / {k} / {p}')
    # time-only save changes nothing else
    page.evaluate("editLogEntry(1)"); page.wait_for_timeout(200)
    page.fill('#edit-time-1', '08:30'); page.evaluate("saveLogEdit(1)")
    a2, p2, k2 = g()
    if (a2, p2, k2) != (a, p, k): f.add('BUG', f'a time-only save altered the entry: {(a,p,k)} -> {(a2,p2,k2)}')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
