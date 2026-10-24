"""Persona 311: a meal already in today's log but timed for later is counted in the Today tiles and the tiles say how much of it is still to come (v3.10.1212); it sits beside the planned line, an earlier-timed or approximate meal never shows it, and it clears when the meal is deleted. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTabById('dash')"); page.wait_for_timeout(400)
    txt = lambda i: ev("(()=>{const e=document.getElementById('%s');return e&&e.style.display!=='none'?e.textContent:''})()" % i)
    put = lambda e: ev("(()=>{state.todayLog.push(%s); saveState(); updateDashboard();})()" % e)
    put("{id:'z1',description:'Zzqx early',time:'00:01',kcal:200,protein:10,carbs:5,fat:12}"); page.wait_for_timeout(300)
    if txt('calPlanned'): f.add('BUG', 'a meal already eaten earlier shows no later line')
    put("{id:'z2',description:'Zzqx later',time:'23:50',kcal:162,protein:2,carbs:2,fat:14}"); page.wait_for_timeout(300)
    for i, want in [('calPlanned', 'includes 162 kcal logged for 23:50'), ('protPlanned', 'includes 2g logged for 23:50'), ('carbPlanned', 'includes 2g logged for 23:50'), ('fatPlanned', 'includes 14g logged for 23:50')]:
        if want not in txt(i): f.add('BUG', f'{i} shows "{want}": got "{txt(i)}"')
    if ev("Math.round(calcTotals(state.todayLog).kcal)") != 362: f.add('BUG', 'the later meal is still counted in the day')
    put("{id:'z3',description:'Zzqx approx',time:'23:55',timeApprox:true,kcal:50,protein:1,carbs:1,fat:1}"); page.wait_for_timeout(300)
    if 'includes 162 kcal' not in txt('calPlanned'): f.add('BUG', 'an approximate-time meal is not counted as later')
    # beside a plan
    ev("mhPlanAdd([{name:'Zzqx Plan',amount:'1',kcal:100,protein:1,fat:1,carbs:1}],'Zzqx Plan',{time:'23:30',date:localISODate()})"); page.wait_for_timeout(400)
    t = txt('calPlanned')
    if '+100 kcal planned' not in t or 'logged for 23:50' not in t: f.add('BUG', f'planned and later lines sit together: "{t}"')
    # delete the later meal: line goes
    ev("(()=>{state.todayLog=state.todayLog.filter(e=>e.id!=='z2'); saveState(); updateDashboard();})()"); page.wait_for_timeout(300)
    if 'logged for' in txt('calPlanned'): f.add('BUG', 'deleting the meal clears the later line')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
