"""Persona 432: cards that looked at a fixed period now use the standard range control: weight trend (was 14 weigh-ins), Fasting "your usual" (was 30 days), "Used up or binned" (was 30 days), Missing data (was 14 days), Activity credit (was a Window box), and the Sleep chart (was the newest 28 nights). Each starts on the period it always used."""
import sys, datetime; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def pick(page, scope, v):
    page.evaluate("(([sc,v]) => { const s = document.querySelector(sc + ' select.mh-rg-sel'); s.value = String(v); s.dispatchEvent(new Event('change')); })(%s)" % __import__('json').dumps([scope, v])); page.wait_for_timeout(400)
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('dash')"); page.wait_for_timeout(400)
    # 120 days of history: weight falls fast over the last 7 days and rises slowly before; timed meals; steps/hr/sleep present except a few days; exercise on days 20-25
    ev("""(() => { const out = []; for (let i = 1; i <= 120; i++) { const d = new Date(); d.setDate(d.getDate() - i);
        const ds = String(d.getDate()).padStart(2,'0') + '/' + String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getFullYear()).slice(2);
        const w = i <= 7 ? 80 + i * 0.3 : 82.1 - (i - 7) * 0.05;
        const e = { date: ds, weight: Math.round(w * 10) / 10, log: [{ name: 'a', time: '08:00', kcal: 400, protein: 30, carbs: 5, fat: 20 }, { name: 'b', time: '19:00', kcal: 800, protein: 50, carbs: 10, fat: 50 }], totals: { kcal: 1200, protein: 80, carbs: 15, fat: 70 },
          steps: (i === 3 || i === 40) ? 0 : 8000, hr_resting: 60, sleep_duration: (i === 3 || i === 40) ? 0 : 450, mode: 'standard' };
        if (i >= 20 && i <= 25) e.exercises = [{ name: 'Walk', duration: 30, kcal: 200 }];
        out.push(e); } state.history = out; state.weight = 79.5; saveState(); })()""")
    # ---- 1. weight trend
    ev("updateDashboard()"); page.wait_for_timeout(500)
    t14 = ev("document.getElementById('weightTrendPrediction').textContent")
    if '▾' not in t14 or '14d' not in t14 and 'target in' not in t14: f.add('BUG', 'weight trend starts on 14 days and shows it can be tapped: ' + t14)
    ev("document.getElementById('weightTrendPrediction').click()"); page.wait_for_timeout(300)
    if not ev("!!document.querySelector('#mhWtTrendModal select.mh-rg-sel')"): f.add('BUG', 'tapping the trend opens the range sheet')
    pick(page, '#mhWtTrendModal', 7); t7 = ev("document.getElementById('weightTrendPrediction').textContent")
    pick(page, '#mhWtTrendModal', 90); t90 = ev("document.getElementById('weightTrendPrediction').textContent")
    if t7 == t90 or '↓' not in t7 or '↑' in t7: f.add('BUG', f'the period changes the trend (7 days falling, 90 days other): {t7!r} vs {t90!r}')
    if ev("document.querySelector('#mhWtTrendModal select.mh-rg-sel').value") != '90': f.add('BUG', 'sheet keeps the choice')
    ev("document.getElementById('mhWtTrendModal').remove()")
    page.locator('#weightTrendPrediction').scroll_into_view_if_needed(); page.screenshot(path='/tmp/claude-0/p432_weight.png')
    # ---- 2. fasting usual
    ev("localStorage.removeItem('mh_rg_fastusual'); localStorage.setItem('mh_cardinfo_fasting','open'); mhCardBodyApply(); mhRenderFastingCard()"); page.wait_for_timeout(300)  # the picker sits behind the card's ? (12 Nov 2026)
    u = ev("document.getElementById('fastUsualLine').textContent")
    if '29 logged days' not in u or 'last 30 days' not in u: f.add('BUG', 'fasting usual starts on 30 days: ' + u[:120])
    if not ev("!!document.querySelector('#fastUsualRange select.mh-rg-sel')"): f.add('BUG', 'fasting card has the range control')
    pick(page, '#fastUsualRange', 7); u = ev("document.getElementById('fastUsualLine').textContent")
    if '6 logged days' not in u: f.add('BUG', 'fasting usual follows 7 days: ' + u[:120])
    pick(page, '#fastUsualRange', 90); u = ev("document.getElementById('fastUsualLine').textContent")
    if '89 logged days' not in u: f.add('BUG', 'fasting usual follows 90 days: ' + u[:120])
    page.locator('#fastUsualRange').scroll_into_view_if_needed(); page.screenshot(path='/tmp/claude-0/p432_fasting.png')
    # ---- 3. waste
    ev("""(() => { const o = mhStockLoad(); o.waste = []; const now = Date.now(); [[2,'Milk'],[10,'Bread'],[50,'Cheese'],[200,'Ham']].forEach(([d,n]) => mhWasteNote(o, { k: n.toLowerCase(), n, b: 'each', a: 1, t: now - d * 864e5 })); mhStockSave(o); })()""")
    kept = ev("mhStockLoad().waste.length")
    if kept != 4: f.add('BUG', f'waste older than 30 days is kept for ranges: {kept}')
    ev("localStorage.removeItem('mh_rg_waste')"); h = ev("mhStockExtrasHtml(mhStockLoad())")
    if 'in the last 30 days' not in h or 'Milk' not in h or 'Bread' not in h or 'Cheese' in h: f.add('BUG', 'waste starts on 30 days')
    if 'mh-rg-sel' not in h: f.add('BUG', 'waste has the range control')
    ev("mhRgSet('waste', 30, '365', null)"); h = ev("mhStockExtrasHtml(mhStockLoad())")
    if 'Ham' not in h or 'last 12 months' not in h: f.add('BUG', 'waste follows 12 months')
    ev("mhRgSet('waste', 30, '7', null)"); h = ev("mhStockExtrasHtml(mhStockLoad())")
    if 'Bread' in h or 'Milk' not in h: f.add('BUG', 'waste follows 7 days')
    # ---- 4. missing data (browser-only path)
    ev("_serverOnline = false"); page.evaluate("document.getElementById('mhGapsList') || (document.body.insertAdjacentHTML('beforeend','<div id=\"mhGapsRange\"></div><div id=\"mhGapsList\"></div>'))")
    ev("localStorage.removeItem('mh_rg_gaps')"); ev("mhLoadDataGaps()"); page.wait_for_timeout(500)
    t = ev("document.getElementById('mhGapsList').innerText")
    if 'steps' not in t or 'sleep' not in t or ev("document.querySelectorAll('#mhGapsList > div').length") != 1: f.add('BUG', 'starts on 14 days: only day 3 is a gap: ' + t[:150])
    if 'mh-rg-sel' not in ev("document.getElementById('mhGapsRange').innerHTML"): f.add('BUG', 'range control present on first load')
    ev("mhRgSet('gaps', 14, '90', 'mhLoadDataGaps')"); page.wait_for_timeout(400)
    n90 = ev("document.querySelectorAll('#mhGapsList > div').length")
    if n90 < 2: f.add('BUG', f'90 days shows the second gap (day 40): {n90} rows')
    ev("mhRgSet('gaps', 14, '7', 'mhLoadDataGaps')"); page.wait_for_timeout(400)
    n7 = ev("document.querySelectorAll('#mhGapsList > div').length")
    if n7 != 1: f.add('BUG', f'7 days shows only day 3: {n7} rows')
    if 'mh-rg-sel' not in ev("document.getElementById('mhGapsRange').innerHTML"): f.add('BUG', 'missing data has the range control')
    # ---- 5. activity credit
    ev("renderActivityCreditBalance()"); page.wait_for_timeout(200)
    t = ev("document.getElementById('activityCreditBalance').innerText")
    if 'No logged exercise in the last 14 days' not in t: f.add('BUG', 'credit starts on 14 days: ' + t[:120])
    ev("mhRgSet('actcredit', 14, '30', 'renderActivityCreditBalance')"); page.wait_for_timeout(300)
    t = ev("document.getElementById('activityCreditBalance').innerText")
    if 'last 30 days' not in t or 'No logged exercise' in t: f.add('BUG', 'credit follows 30 days: ' + t[:160])
    if not ev("!!document.querySelector('#activityCreditBalance select.mh-rg-sel')"): f.add('BUG', 'credit has the range control (not a number box)')
    if ev("!!document.getElementById('activityCreditWindowInput')"): f.add('BUG', 'the old Window box is gone')
    # ---- 7. goal check banner
    ev("localStorage.setItem('mh_goal','gain'); localStorage.removeItem('mh_rg_goalcheck'); window._dismissedWarnings = new Set(); checkGoalMismatch()"); page.wait_for_timeout(300)
    g = ev("document.getElementById('goalMismatchBanner').innerText")
    if 'over the last 14 days' not in g or 'gain-phase' not in g: f.add('BUG', 'goal check starts on 14 days: ' + g[:200])
    if '~2 weeks' in g: f.add('BUG', 'no fixed "2 weeks" wording left')
    if not ev("!!document.querySelector('#goalMismatchBanner select.mh-rg-sel')"): f.add('BUG', 'goal check has the range control')
    pick(page, '#goalMismatchBanner', 7); g = ev("document.getElementById('goalMismatchBanner').innerText")
    if 'over the last 7 days' not in g: f.add('BUG', 'goal check follows 7 days: ' + g[:200])
    pick(page, '#goalMismatchBanner', 365); g = ev("document.getElementById('goalMismatchBanner').innerText")
    if 'last 12 months' not in g: f.add('BUG', 'goal check follows 12 months: ' + g[:200])
    pick(page, '#goalMismatchBanner', 7); ev("localStorage.setItem('mh_goal','lose'); checkGoalMismatch()"); page.wait_for_timeout(300)
    g = ev("document.getElementById('goalMismatchBanner').innerText")
    if 'nothing to flag over the last 7 days' not in g or not ev("!!document.querySelector('#goalMismatchBanner select.mh-rg-sel')"): f.add('BUG', 'with their own period chosen, a quiet line keeps the control: ' + g[:200])
    pick(page, '#goalMismatchBanner', 14)
    if ev("document.getElementById('goalMismatchBanner').style.display") != 'none': f.add('BUG', 'back on 14 days with nothing to flag: banner gone again')
    if ev("localStorage.getItem('mh_rg_goalcheck')") is not None: f.add('BUG', 'default period is not stored')
    # ---- 6. sleep chart
    ev("_rptRange = 30; renderSleepReport()"); page.wait_for_timeout(200)
    c30 = ev("(document.querySelector('#sleep-report-content') || {innerText:''}).innerText")
    if 'EACH WEEK' in c30.upper() and 'AVERAGE NIGHT' in c30.upper().split('EACH WEEK')[1][:30]: pass
    cols30 = ev("document.querySelectorAll('#sleep-report-content [title*=\"/\"]').length")
    ev("_rptRange = 90; renderSleepReport()"); page.wait_for_timeout(200)
    t90 = ev("document.getElementById('sleep-report-content').innerText").upper()
    if 'EACH WEEK, AVERAGE NIGHT' not in t90: f.add('BUG', 'a long range shows weekly columns')
    cols90 = ev("document.querySelectorAll('#sleep-report-content [title^=\"week of\"]').length")
    if not (11 <= cols90 <= 15): f.add('BUG', f'about 13 weekly columns for 90 days, got {cols90}')
    ev("_rptRange = 7; renderSleepReport()"); page.wait_for_timeout(200)
    if 'EACH NIGHT' not in ev("document.getElementById('sleep-report-content').innerText").upper(): f.add('BUG', 'a short range still shows each night')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
