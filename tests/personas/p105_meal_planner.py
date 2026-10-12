"""Persona 105: meal planner. Parser cases (plan words + time needed, never hijacks 'I had'), plan via preview -> planned list not log, totals eaten+planned,
over-ceiling warning, due prompt -> Yes moves it to the log at the planned time, Changed/Skipped, tomorrow, persistence, no page errors."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    # --- parser (fixed 'now' = 10:00 local)
    cases = [
        ("I'm planning on eating 2 eggs and toast at 1pm", ('13:00', '2 eggs and toast')),
        ("I'm going to have a steak at 19:30", ('19:30', 'a steak')),
        ("I'll have chicken salad at 12:30", ('12:30', 'chicken salad')),
        ("planning to eat porridge for breakfast at 8 tomorrow", ('08:00', None)),
        ("I'm planning dinner at 7", ('19:00', None)),
        ("I'm planning on eating a banana at noon", ('12:00', 'a banana')),
    ]
    for t, (tm, food) in cases:
        r = ev("(t)=>mhPlanParse(t, new Date(2026,9,12,10,0))", t)
        if not r or r['time'] != tm: f.add('BUG', f'parse {t!r} -> {r}')
        elif food and r['food'] != food: f.add('BUG', f'food {t!r} -> {r["food"]!r}')
    if ev("mhPlanParse('planning porridge at 8 tomorrow', new Date(2026,9,12,10,0)).date") != '2026-10-13': f.add('BUG', 'tomorrow date')
    for t in ["I had 2 eggs at 8am", "2 eggs and toast", "I ate chicken at 1pm", "I'm planning on eating eggs", "going to have eggs for 7"]:
        if ev("(t)=>mhPlanParse(t)", t): f.add('BUG', f'hijacked {t!r}')
    # --- plan through the preview: goes to the planned list, not the log
    ev("""(()=>{ window._pendingMealFoods=[{name:'Eggs',amount:'100g',kcal:150,protein:12,fat:10,carbs:1}]; window._pendingMealText='2 eggs';
      window._planPending={time:'23:59',date:localISODate(),t:Date.now()}; renderMealPreview(); })()""")
    if 'Ready to plan for 23:59' not in ev("document.getElementById('mealPreviewBubble').textContent"): f.add('BUG', 'preview header')
    if 'Add to plan' not in ev("document.getElementById('mealPreviewBubble').textContent"): f.add('BUG', 'plan button')
    if ev("[...document.querySelectorAll('#mealPreviewBubble button')].some(b=>/Plan for later/.test(b.textContent))"): f.add('BUG', 'plan-for-later button shown while planning')
    before = ev("state.todayLog.length")
    ev("confirmMealLog()"); page.wait_for_timeout(500)
    if ev("state.todayLog.length") != before: f.add('BUG', 'planned food went into the log')
    if len(ev("mhPlanLoad()")) != 1: f.add('BUG', 'not in plan list')
    if ev("window._planPending"): f.add('BUG', '_planPending left set')
    # normal preview shows Plan for later
    ev("window._pendingMealFoods=[{name:'X',amount:'100g',kcal:10,protein:1,fat:1,carbs:1}]; renderMealPreview()")
    if not ev("[...document.querySelectorAll('#mealPreviewBubble button')].some(b=>/Plan for later/.test(b.textContent))"): f.add('BUG', 'no Plan for later button')
    ev("cancelMealPreview()")
    # --- totals
    page.evaluate("updateDashboard()"); page.wait_for_timeout(300)
    t = ev("document.getElementById('mhPlanTotals') && document.getElementById('mhPlanTotals').textContent") or ''
    if '150' not in t or '= 150' not in t.replace('  ', ' ') and '= 150 kcal' not in t: f.add('BUG', f'totals {t[:200]!r}')
    ev("localStorage.setItem('mh_target_fat','200')"); ev("mhPlanRender()")
    if '/ 200g' not in (ev("document.getElementById('mhPlanTotals').textContent") or ''): f.add('BUG', 'fat target not shown in plan totals')
    ws = ev("[...document.querySelectorAll('.mh-plan-row button')].map(b=>Math.round(b.getBoundingClientRect().width))")
    if ws and (max(ws) - min(ws) > 2 or ev("document.documentElement.scrollWidth") > 392): f.add('BUG', f'plan buttons not uniform / page overflows {ws}')
    # over ceiling warning
    ev("localStorage.setItem('mh_target_carbs','10')")
    ev("(()=>{ const a=mhPlanLoad(); a.push({id:'pbig',date:localISODate(),time:'23:58',text:'Rice',foods:[{name:'Rice',kcal:200,protein:4,fat:1,carbs:45}],createdAt:1}); mhPlanSave(a); mhPlanRender(); })()")
    if 'over your ceiling' not in (ev("document.getElementById('mhPlanTotals').textContent") or ''): f.add('BUG', 'no carb warning')
    ev("mhPlanRemove('pbig')")
    # --- due: Yes -> log at planned time
    ev("(()=>{ const a=mhPlanLoad(); a.push({id:'pdue',date:localISODate(),time:'00:01',text:'Toast',foods:[{name:'Toast',amount:'100g',kcal:90,protein:3,fat:1,carbs:15}],createdAt:1}); mhPlanSave(a); mhPlanRender(); })()")
    if 'Did you eat this?' not in ev("document.getElementById('mhPlanBlock').textContent"): f.add('BUG', 'no due prompt')
    n = ev("state.todayLog.length")
    ev("mhPlanEat('pdue')"); page.wait_for_timeout(500)
    if ev("state.todayLog.length") <= n: f.add('BUG', 'Yes did not log')
    if not ev("state.todayLog.some(e=>e.time==='00:01')"): f.add('BUG', 'time not kept')
    if ev("mhPlanLoad().some(p=>p.id==='pdue')"): f.add('BUG', 'plan not removed after eaten')
    # skipped + changed + tomorrow not due
    ev("(()=>{ const a=mhPlanLoad(); a.push({id:'psk',date:localISODate(),time:'00:02',text:'Skip me',foods:[{name:'S',kcal:5,protein:0,fat:0,carbs:0}],createdAt:1},{id:'pch',date:localISODate(),time:'00:03',text:'Change me',foods:[{name:'C',kcal:5,protein:0,fat:0,carbs:0}],createdAt:1},{id:'ptm',date:localISODate(new Date(Date.now()+864e5)),time:'00:01',text:'Tmrw',foods:[{name:'T',kcal:5,protein:0,fat:0,carbs:0}],createdAt:1}); mhPlanSave(a); mhPlanRender(); })()")
    n = ev("state.todayLog.length"); ev("mhPlanRemove('psk')")
    if ev("state.todayLog.length") != n: f.add('BUG', 'skipped logged')
    ev("mhPlanChanged('pch')")
    if 'Change me' not in ev("document.getElementById('chatInput').value"): f.add('BUG', 'changed did not prefill')
    row = ev("document.querySelector('[data-plan=ptm]').textContent")
    if 'Did you eat this?' in row: f.add('BUG', 'tomorrow plan prompted as due')
    # persistence
    page.reload(); page.wait_for_timeout(1500)
    if not ev("mhPlanLoad().some(p=>p.id==='ptm')"): f.add('BUG', 'plan lost on reload')
    # stale plan dropped
    ev("(()=>{ const a=mhPlanLoad(); a.push({id:'pold',date:'2020-01-01',time:'10:00',text:'old',foods:[],createdAt:1}); mhPlanSave(a); mhPlanRender(); })()")
    if ev("mhPlanLoad().some(p=>p.id==='pold')"): f.add('BUG', 'stale plan kept')
    # auto mode
    ev("mhPlanSetAuto(true)")
    ev("(()=>{ const a=mhPlanLoad(); a.push({id:'pauto',date:localISODate(),time:'00:01',text:'Auto',foods:[{name:'A',kcal:7,protein:0,fat:0,carbs:0}],createdAt:1}); mhPlanSave(a); mhPlanRender(); })()"); page.wait_for_timeout(500)
    if ev("mhPlanLoad().some(p=>p.id==='pauto')") or not ev("state.todayLog.some(e=>e.description==='Auto')"): f.add('BUG', 'auto-log failed')
    # normal logging unaffected
    ev("window._pendingMealFoods=[{name:'Plain',amount:'100g',kcal:11,protein:1,fat:1,carbs:1}]; window._pendingMealText='plain'; renderMealPreview()")
    n = ev("state.todayLog.length"); ev("confirmMealLog()"); page.wait_for_timeout(500)
    if ev("state.todayLog.length") <= n: f.add('BUG', 'normal logging broken')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
