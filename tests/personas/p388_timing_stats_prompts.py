"""Persona 388: meal timing in Statistics and as example questions (v3.10.1279).
Pete (4 Nov): "a few prompts showing how the data could be used and on statistics." Covers: five new Statistics measures (eating occasions, first meal, last meal, protein before noon, carbs after 5pm) by day, weekday and week, times shown as clock times, summing times turned into an average, example questions added once to an existing saved list (not again, not after you delete them), and seeded for a new install. Invented data."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
def day(n, meals):
    log = [{'id': n * 10 + i, 'time': t, 'description': 'Zzqx meal', 'kcal': 400, 'protein': p, 'carbs': c, 'fat': 5} for i, (t, p, c) in enumerate(meals)]
    return {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': log, 'totals': {'kcal': 1600, 'protein': 100, 'carbs': 20, 'fat': 60}}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    # new install: seeded
    names = ev("loadSavedPrompts().map(p=>p.name)")
    if 'Protein spread' not in names or 'Around treatment sessions' not in names or len(names) != len(set(names)): f.add('BUG', '1: a new install has the timing questions once: ' + str(names))
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("state.history = " + json.dumps([day(1, [('08:00', 30, 2), ('20:00', 40, 5)]), day(2, [('10:00', 25, 2), ('22:00', 45, 9)])]) + "; saveState()")
    R = lambda o: ev("(o=>{const r=mhStatRun(o);return r.rows.map(x=>[x.label,Math.round(x.value*100)/100,x.n])})(%s)" % json.dumps(o))
    r = R({'subject': 'days', 'measure': 'meallast', 'agg': 'sum', 'order': 'time', 'period': 30, 'output': 'list'})
    if sorted(x[1] for x in r) != [20, 22]: f.add('BUG', f'2: last meal per day: {r}')
    r = R({'subject': 'weeks', 'measure': 'meallast', 'agg': 'sum', 'order': 'time', 'period': 30, 'output': 'list'})
    if not r or not (20 < max(x[1] for x in r) < 23): f.add('BUG', f'3: summing last-meal times becomes an average, not 42: {r}')
    r = R({'subject': 'weekdays', 'measure': 'evecarb', 'agg': 'avg', 'order': 'time', 'period': 30, 'output': 'list'})
    if not r or sorted(x[1] for x in r if x[1]) != [5, 9]: f.add('BUG', f'4: carbs after 5pm by weekday: {r}')
    r = R({'subject': 'days', 'measure': 'amprot', 'agg': 'sum', 'order': 'time', 'period': 30, 'output': 'list'})
    if sorted(x[1] for x in r) != [25, 30]: f.add('BUG', f'5: protein before noon: {r}')
    r = R({'subject': 'days', 'measure': 'mealn', 'agg': 'sum', 'order': 'time', 'period': 30, 'output': 'list'})
    if [x[1] for x in r] != [2, 2]: f.add('BUG', f'6: eating occasions: {r}')
    txt = ev("(()=>{const el=document.createElement('div'); el.innerHTML=mhStatRender(mhStatRun({subject:'days',measure:'meallast',agg:'sum',order:'time',period:30,output:'table'})); return el.innerText})()")
    if '20:00' not in txt or '22:00' not in txt: f.add('BUG', '7: times show as clock times: ' + txt[:100])
    if not ev("Object.keys(mhStatMeasures('weekdays')).includes('mealfirst')"): f.add('BUG', '8: listed among the measures')
    # existing saved list: added once
    ev("localStorage.removeItem('mh_prompts_timing_v1'); localStorage.setItem('mh_saved_prompts', JSON.stringify([{id:1,name:'Mine',text:'x',scope:'history'}]))")
    n1 = ev("loadSavedPrompts().map(p=>p.name)")
    if 'Mine' not in n1 or 'Protein spread' not in n1 or len(n1) != 7: f.add('BUG', '9: existing list keeps its own and gains 6: ' + str(n1))
    ev("saveSavedPrompts(loadSavedPrompts().filter(p=>p.name!=='Protein spread'))")
    n2 = ev("loadSavedPrompts().map(p=>p.name)")
    if 'Protein spread' in n2 or len(n2) != 6: f.add('BUG', '10: a deleted example is not added back: ' + str(n2))
    # shown in the saved prompts manager
    ev("switchTab('insights'); switchSubTab('insights','reports')"); page.wait_for_timeout(400); ev("openSavedPromptsManager('setAskStarter')"); page.wait_for_timeout(500)
    if 'Weekdays vs weekends' not in ev("document.body.innerText"): f.add('BUG', '11: the examples are in the Browse saved prompts list')
    page.screenshot(path='/tmp/p388.png')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
