"""Persona 113: planner fasting heads-up. Silent when you do not track fasting; says how long after the last meal and when the goal would be reached when a plan ends a fast early; silent when the goal is met or the plan is under the fast threshold; no page errors."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("window.mhFastingNow=()=>({lastMs:Date.now()-3*3600000,hours:3,stale:false,goalH:12})")
    P = """([h,k])=>{const d=new Date(Date.now()+h*3600000);const p=n=>String(n).padStart(2,'0');
      return mhPlanFastNote({date:d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate()),time:p(d.getHours())+':'+p(d.getMinutes())},k)}"""
    if ev(P, [2, 300]): f.add('BUG', 'note shown when fasting is not tracked')
    ev("localStorage.setItem('mh_fasting_goal_h','12')")
    n = ev(P, [2, 300])
    if 'Heads up' not in n or '12h' not in n or 'h' not in n.split('after')[0]: f.add('BUG', f'no/odd note {n!r}')
    if ev(P, [10, 300]): f.add('BUG', 'note shown although goal is met')
    if ev(P, [2, 10]): f.add('BUG', 'note shown for a plan under the fast threshold')
    if ev("mhPlanFastNote({date:'2020-01-01',time:'10:00'},300)"): f.add('BUG', 'note for a past plan')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
