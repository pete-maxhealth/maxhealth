"""Persona 384: timing advice inside "When you eat" (v3.10.1271).
Pete (4 Nov): "we have age, sex, weight and everything else needed for another detailed AI response with its clinical/PT/nutritional advisor/treatment session providers hat on ... useful for personal use or third party."
Covers: the five advisers and the remembered choice; nothing is sent until a button is tapped; the prompt carries the profile, the timing figures, the chosen hat, the Proven/Early Stage/Speculative rule and no-directions rule; the "for my ..." version is addressed to the adviser; the answer shows with a Copy button; a repeat costs no second call; a failed call says so; with too few days there is no advice box. AI is stubbed. Invented data; real taps."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta, datetime, time as dtime
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n):
    meals = [('08:00', 30, 20, 10), ('13:00', 40, 30, 20), ('19:00', 50, 40, 30)]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': [{'id': 1000 + i, 'time': t, 'description': 'meal', 'kcal': 400, 'protein': p, 'carbs': c, 'fat': fa} for i, (t, p, c, fa) in enumerate(meals)], 'totals': {'kcal': 1200, 'protein': 120, 'carbs': 90, 'fat': 60}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', timezone_id='UTC')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    ctx.clock.install(time=datetime.combine(date.today(), dtime(12, 0)))
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("localStorage.setItem('mh_condition','general'); localStorage.setItem('mh_age','52'); localStorage.setItem('mh_sex','female'); localStorage.setItem('mh_height_cm','168'); state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("window._calls=[]; window.callHealthAI = async (p,o)=>{ window._calls.push(p); return window._fail ? {ok:false,error:'no signal'} : {ok:true,text:'TEST ADVICE one\\nTEST ADVICE two'}; }")
    show = lambda: (ev("switchTab('insights'); switchSubTab('insights','reports'); _rptRange=0; renderReports()"), page.wait_for_timeout(500))
    def tap(sel):
        ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none')")
        page.locator(sel).first.scroll_into_view_if_needed(); bb = page.locator(sel).first.bounding_box(); page.mouse.move(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(500)
    ev("state.history = " + json.dumps([day(i) for i in range(1, 3)]) + "; saveState()"); show()
    if ev("!!document.getElementById('wheneat-coach')") and ev("getComputedStyle(document.getElementById('wheneat-report-section')).display") != 'none': f.add('BUG', '1: no advice box with too few days')
    ev("state.history = " + json.dumps([day(i) for i in range(1, 11)]) + "; saveState()"); show()
    roles = ev("[...document.querySelectorAll('#wheneatRoles [data-role]')].map(e=>e.dataset.role)")
    if roles != ['coach', 'pt', 'dietitian', 'diabetes']: f.add('BUG', f'2: a standard profile sees four advisers, no oncology: {roles}')
    ev("localStorage.setItem('mh_condition','gbm')"); show()
    roles = ev("[...document.querySelectorAll('#wheneatRoles [data-role]')].map(e=>e.dataset.role)")
    if roles != ['coach', 'pt', 'dietitian', 'diabetes', 'oncology']: f.add('BUG', f'2b: a GBM profile also sees the oncology adviser: {roles}')
    if ev("window._calls.filter(p=>String(p).includes('WHEN THEY EAT (from logged meal times')).length") != 0: f.add('BUG', '3: nothing is sent until a button is tapped')
    tap('#wheneatRoles [data-role="diabetes"]')
    if ev("document.querySelector('#wheneatRoles .active')?.dataset.role") != 'diabetes': f.add('BUG', '4: tapping an adviser selects it')
    page.reload(); page.wait_for_timeout(1500); ev("window._calls=[]; window.callHealthAI = async (p,o)=>{ window._calls.push(p); return window._fail ? {ok:false,error:'no signal'} : {ok:true,text:'TEST ADVICE one\\nTEST ADVICE two'}; }"); show()
    if ev("document.querySelector('#wheneatRoles .active')?.dataset.role") != 'diabetes': f.add('BUG', '5: the choice is remembered after a reload')
    if 'diabetes team' not in ev("document.getElementById('wheneatCoachBtn2').innerText").lower(): f.add('BUG', '6: the second button names the adviser')
    tap('#wheneatCoachBtn')
    if ev("window._calls.filter(p=>String(p).includes('WHEN THEY EAT (from logged meal times')).length") != 1: f.add('BUG', '7: one coach call')
    pr = ev("window._calls.filter(p=>String(p).includes('WHEN THEY EAT (from logged meal times'))[0]||''")
    for want in ['Age 52', 'Sex female', 'diabetes dietitian', 'Proven, Early Stage or Speculative', 'Do not give medication', '10 days', 'Early morning', '30/20/10']:
        if want not in pr: f.add('BUG', f'8: the prompt carries {want!r}')
    if 'ADDRESSED TO' in pr: f.add('BUG', '9: the advice for me is not the third-party note')
    if 'TEST ADVICE one' not in ev("document.getElementById('wheneatCoachOut').innerText") or ev("getComputedStyle(document.getElementById('wheneatCoachCopy')).display") == 'none': f.add('BUG', '10: the answer shows with a Copy button')
    tap('#wheneatCoachBtn')
    if ev("window._calls.filter(p=>String(p).includes('WHEN THEY EAT (from logged meal times')).length") != 1: f.add('BUG', '11: a repeat costs no second call')
    tap('#wheneatCoachBtn2')
    if ev("window._calls.filter(p=>String(p).includes('WHEN THEY EAT (from logged meal times')).length") != 2 or 'ADDRESSED TO a diabetes dietitian' not in ev("window._calls.filter(p=>String(p).includes('WHEN THEY EAT (from logged meal times'))[1]||''"): f.add('BUG', '12: the for-my version is addressed to the adviser')
    tap('#wheneatRoles [data-role="oncology"]'); ev("window._fail=true"); tap('#wheneatCoachBtn')
    if 'oncology dietitian' not in ev("window._calls.filter(p=>String(p).includes('WHEN THEY EAT (from logged meal times')).slice(-1)[0]||''"): f.add('BUG', '13: another hat changes the prompt')
    if "Couldn't get advice" not in ev("document.getElementById('wheneatCoachOut').innerText"): f.add('BUG', '14: a failed call says so')
    ev("document.getElementById('wheneat-coach').scrollIntoView()"); page.screenshot(path='/tmp/p384.png')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
