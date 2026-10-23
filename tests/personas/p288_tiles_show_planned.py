"""Persona 288: the four Today tiles show a small planned line from the Meal plan, and drop it when the plan is eaten or removed (v3.10.1184). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("switchTabById('today')"); page.wait_for_timeout(500)
    txt = lambda i: ev("(()=>{const e=document.getElementById('%s');return e&&e.style.display!=='none'?e.textContent:''})()" % i)
    if any(txt(i) for i in ['calPlanned', 'protPlanned', 'carbPlanned', 'fatPlanned']): f.add('BUG', 'no line when nothing is planned')
    ev("mhPlanAdd([{name:'Zzqx Bar',amount:'1',kcal:140,protein:7,fat:9,carbs:6}],'Zzqx Bar',{time:'23:30',date:localISODate()})"); page.wait_for_timeout(500)
    for i, want in [('calPlanned', '+140 kcal planned'), ('protPlanned', '+7g planned'), ('carbPlanned', '+6g planned'), ('fatPlanned', '+9g planned')]:
        if want not in txt(i): f.add('BUG', f'{i} shows "{want}": got "{txt(i)}"')
    if '140 kcal total' not in txt('calPlanned'): f.add('BUG', f'the line also gives the total: "{txt("calPlanned")}"')
    # a planned meal for tomorrow does not count today
    ev("mhPlanRemove(mhPlanLoad()[0].id)"); page.wait_for_timeout(300)
    ev("mhPlanAdd([{name:'Zzqx Later',amount:'1',kcal:300,protein:5,fat:5,carbs:5}],'Zzqx Later',{time:'12:00',date:localISODate(new Date(Date.now()+86400000))})"); page.wait_for_timeout(400)
    if txt('calPlanned'): f.add('BUG', 'tomorrow\'s plan is not shown on today\'s tile')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
