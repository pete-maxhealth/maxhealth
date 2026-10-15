"""Persona 166 (v3.10.1065): the TDEE estimate follows the Activity Level (same four multipliers), so a level set by the steps check and the estimate agree.
Falls back to the 30-day step average when no level is set."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("localStorage.setItem('mh_height_cm','180'); localStorage.setItem('mh_age','56'); localStorage.setItem('mh_sex','male'); state.weight=92.9")
    # 30 days averaging ~11,100 steps (the real-life case: 14-day average high, 30-day average lower)
    ev("state.history = Array.from({length:30},(_,i)=>({date: (()=>{const d=new Date(); d.setDate(d.getDate()-i); return String(d.getDate()).padStart(2,'0')+'/'+String(d.getMonth()+1).padStart(2,'0')+'/'+String(d.getFullYear()).slice(2)})(), steps: i<14?14000:8000, totals:{kcal:0}}))")
    avg = ev("getCurrentTDEE().avgSteps"); bmr = ev("getCurrentTDEE().bmr")
    check('30-day average is in the 8,000-12,000 band', 8000 < avg < 12000, str(avg))
    ev("localStorage.removeItem('mh_activity_level')"); t0 = ev("getCurrentTDEE()")
    check('no level set: step-average multiplier (1.55)', t0['actMult'] == 1.55 and t0['level'] is None, str(t0))
    for lvl, m in [('sedentary', 1.2), ('light', 1.375), ('moderate', 1.55), ('active', 1.725)]:
        ev(f"localStorage.setItem('mh_activity_level','{lvl}')"); t = ev("getCurrentTDEE()")
        check(f'level {lvl} uses {m}', t['actMult'] == m and t['tdee'] == round(bmr * m) and t['level'] == lvl, str(t))
    ev("localStorage.setItem('mh_activity_level','active'); renderSuggestedTargets()"); page.wait_for_timeout(300)
    txt = ev("(document.getElementById('suggestedTargetsContent')||{innerText:''}).innerText")
    check('card names the level next to the steps', 'Very active' in txt, txt[:200])
    ev("localStorage.setItem('mh_activity_level','bogus')"); t = ev("getCurrentTDEE()"); check('unknown level falls back to steps', t['actMult'] == 1.55)
    check('no JS errors', not errs, str(errs[:2]))
print('p166:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
