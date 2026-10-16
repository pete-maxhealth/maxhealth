"""Persona 170 (v3.10.1070): Today shows FOOD IN / EXERCISE OUT / ROOM LEFT side by side inside Calories & macros; the numbers
agree with the calorie card (target + exercise - eaten)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    for pid in ['alex', 'doris', 'maria']:
        ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(2200)
        ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(400)
        t = ev("document.getElementById('inOutStrip').textContent")
        check(f'{pid}: strip shows IN, OUT and ROOM/OVER', 'IN' in t and 'OUT' in t and ('ROOM LEFT' in t or 'OVER' in t), t)
        # numbers agree: room = base + out - eaten
        r = ev("(()=>{const eaten=Math.round(calcTotals(state.todayLog).kcal); const base=TARGETS[state.dayMode].kcal; const acts=getActivities().reduce((s,a)=>s+calcActivityKcal(a),0)+calcNonWalkingStepsKcal(getNonWalkingStepsToday().remainder); const txt=document.getElementById('inOutStrip').textContent.replace(/,/g,''); const nums=(txt.match(/\\d+/g)||[]).map(Number); return {eaten,base,acts,room:base+acts-eaten,txt}})()")
        check(f'{pid}: room left matches target + exercise - eaten', str(abs(r['room'])) in r['txt'].replace(',', ''), str(r))
    ev("startDemoMode('alex')"); page.wait_for_timeout(2000)
    ev("(()=>{const a=getActivities(); a.forEach(x=>{if(x.type==='walking'){x.enabled=true;x.duration='45'}}); saveActivities(a); renderActivityCard(); updateDashboard();})()"); page.wait_for_timeout(500)
    t = ev("document.getElementById('inOutStrip').textContent")
    check('logging a walk raises OUT above zero', re.search(r'OUT\s*\+\d', t) is not None, t)
    check('no JS errors', not errs, str(errs[:2]))
print('p170:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
