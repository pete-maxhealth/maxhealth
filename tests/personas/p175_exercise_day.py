"""Persona 175 (v3.10.1075): per-day exercise summary feeds History days and the metric chart (minutes, resistance volume)."""
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
    # arithmetic on a synthetic day
    d = ev("""(()=>{state.strengthLog=[{id:'a',date:'01/10/26',exercise:'Bicep Curl',sets:[{reps:12,weight_kg:20},{reps:12,weight_kg:20},{reps:8,weight_kg:25}]},{id:'b',date:'01/10/26',exercise:'Squats',sets:[{reps:10,weight_kg:60}]}];
      return mhExerciseDay({date:'01/10/26',exercises:[{type:'badminton',name:'🏸 Badminton',duration:'60',effort:'Hard',kcal:630},{type:'walking',name:'🚶 Walking',duration:'30',effort:'Easy',kcal:90},{type:'exercise',name:'Padel with Dave',duration:'45',effort:'Moderate',kcal:300},{type:'x',name:'rest',duration:'',effort:'Easy',kcal:0}]})})()""")
    check('minutes and sessions add up (rest day entries ignored)', d['minutes'] == 135 and d['sessions'] == 3, str(d['minutes']))
    check('kcal and hard minutes', d['kcal'] == 1020 and d['hardMin'] == 60)
    check('categories: racket (badminton + typed padel), walk', d['byCat'].get('racket', {}).get('minutes') == 105 and d['byCat'].get('walk', {}).get('minutes') == 30, str(d['byCat']))
    check('resistance totals: 2 exercises, 4 sets, volume = 12*20+12*20+8*25+10*60', d['res']['exercises'] == 2 and d['res']['sets'] == 4 and d['res']['volumeKg'] == 1280, str(d['res']))
    check('set formatting groups identical sets', ev("mhFmtSets([{reps:12,weight_kg:20},{reps:12,weight_kg:20},{reps:8,weight_kg:25}])") == '2 × 12 @ 20kg, 1 × 8 @ 25kg')
    check('empty day gives no panel', ev("mhExerciseDayHtml({date:'02/10/26',exercises:[]})") == '')
    # demo persona: history day body + chart series
    ev("startDemoMode('alex')"); page.wait_for_timeout(2200)
    n = ev("state.history.filter(d=>mhExerciseDayHtml(d)!=='').length")
    check('history days with exercise show the panel', n > 0, str(n))
    ev("document.getElementById('maintab-log')?.click()"); page.wait_for_timeout(300)
    ev("typeof renderHistory==='function' && renderHistory()"); page.wait_for_timeout(300)
    html = ev("document.body.innerHTML")
    check('panel is in the History DOM', 'EXERCISE' in html and 'min' in html)
    series = ev("getDrillData('exercise_min', 0).length")
    check('minutes metric has data', series > 0, str(series))
    ev("state.strengthLog.length || 0")
    check('metrics exist in config and compare list', ev("!!DRILL_CONFIG.exercise_min && !!DRILL_CONFIG.res_volume && MM_METRIC_GROUPS.find(g=>g.label==='Exercise').match({key:'res_volume'})"))
    ev("document.getElementById('maintab-insights').click()"); page.wait_for_timeout(300)
    ev("renderReports()"); page.wait_for_timeout(400)
    sec = ev("document.getElementById('exercise-report-section').style.display")
    txt = ev("document.getElementById('exercise-report-content').innerText")
    check('Exercise report shows for an active persona', sec == 'block' and 'ACTIVE DAYS' in txt and 'MINUTES PER WEEK' in txt and 'WHAT YOU DID' in txt, txt[:120])
    check('report numbers agree with the per-day maths', ev("(()=>{const days=getReportHistory(); const st=mhExerciseRangeStats(days); return st.minutes===days.reduce((n,d)=>n+mhExerciseDay(d).minutes,0)})()"))
    ev("startDemoMode('doris')"); page.wait_for_timeout(2000); ev("renderReports()")
    check('Doris (walks, aqua, yoga) also gets a report', ev("document.getElementById('exercise-report-section').style.display") == 'block')
    ev("state.history=[]; renderReports()")
    check('no history -> section hidden, no crash', ev("document.getElementById('exercise-report-section').style.display") == 'none')
    check('no JS errors', not errs, str(errs[:2]))
print('p175:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
