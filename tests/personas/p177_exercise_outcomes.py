"""Persona 177 (v3.10.1076): 'what your own days suggest' reports a real association, stays silent on noise and on small samples."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
BUILD = """((mode)=>{
  const out=[]; const base=new Date('2026-08-01T12:00:00');
  for(let i=0;i<40;i++){const d=new Date(base); d.setDate(d.getDate()+i);
    const dd=String(d.getDate()).padStart(2,'0'),mm=String(d.getMonth()+1).padStart(2,'0'),yy=String(d.getFullYear()).slice(2);
    const racket=(i%3===0); const prevRacket=((i-1)%3===0)&&i>0;
    let sleep=420+((i*7)%11-5)*2, hrv=50+((i*5)%7-3);
    if(mode==='effect'&&prevRacket){sleep+=55; hrv+=8}
    out.push({date:`${dd}/${mm}/${yy}`,log:[],totals:{kcal:2000,protein:100,carbs:30,fat:100},sleep_duration:sleep,hrv:hrv,
      exercises: racket?[{type:'badminton',name:'🏸 Badminton',duration:'60',effort:'Moderate',kcal:500}]:[]});
  } return out})"""
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    r = ev(f"mhExerciseOutcomes({BUILD}('effect'))")
    check('a built-in racket effect on next-night sleep is found', any(o['group'] == 'racket & court' and o['measure'] == 'next-night sleep' and o['diff'] > 40 for o in r), str(r)[:300])
    check('HRV effect also found', any(o['measure'] == 'next-day HRV' for o in r))
    check('wording names both groups and the sample sizes', all(('days vs' in o['text'] and 'rest days' in o['text']) for o in r))
    r0 = ev(f"mhExerciseOutcomes({BUILD}('none'))")
    check('no effect built in -> nothing reported', r0 == [], str(r0))
    r1 = ev(f"mhExerciseOutcomes({BUILD}('effect').slice(0,12))")
    check('too few days -> nothing reported', r1 == [], str(r1))
    ev("startDemoMode('alex')"); page.wait_for_timeout(2200)
    ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(300); ev("renderReports()"); page.wait_for_timeout(300)
    txt = ev("document.getElementById('exercise-report-content').innerText")
    check('report carries the Early Stage block and the caution', 'EARLY STAGE' in txt and 'not proof of cause' in txt)
    check('no JS errors', not errs, str(errs[:2]))
print('p177:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
