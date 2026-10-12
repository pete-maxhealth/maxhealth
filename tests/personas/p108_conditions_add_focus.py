"""Persona 108: condition labels. Packs stamp their condition on what they ADD, shared symptoms get both labels, your own stay unlabelled,
the condition filter narrows Compare Metrics pickers (several ticks = union, none = all), and 'Add as another focus' unions two layouts."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("saveSymptomDefs([{id:'mine1',name:'My own thing',active:true}])")
    ids = ev("Object.keys(DASHBOARD_SECTION_LABELS).slice(0,4)")
    A = {'mhpack':1,'_cond':{'id':'cluster','name':'Cluster headache'},'sets':{'symptoms':{'data':[{'id':'a1','name':'Headache','active':True},{'id':'a2','name':'Eye watering','active':True}]},'treatments':{'data':[{'id':'t1','name':'Oxygen','active':True}]},'layout':{'data':{'mh_dashboard_hidden':json.dumps(ids[:3])}}}}
    B = {'mhpack':1,'_cond':{'id':'tumour','name':'Brain tumour'},'sets':{'symptoms':{'data':[{'id':'b1','name':'Headache','active':True},{'id':'b2','name':'Fatigue','active':True}]},'layout':{'data':{'mh_dashboard_hidden':json.dumps(ids[1:4])}}}}
    ev("(p)=>mhPackApply(p,['symptoms','treatments'],'merge')", A)
    ev("(p)=>mhPackApply(p,['symptoms','treatments'],'merge')", B)
    d = {s['name']: s.get('conds') for s in ev("loadSymptomDefs()")}
    if d.get('My own thing'): f.add('BUG', f'own symptom labelled {d}')
    if d.get('Eye watering') != ['cluster']: f.add('BUG', f'cluster label {d}')
    if d.get('Fatigue') != ['tumour']: f.add('BUG', f'tumour label {d}')
    if d.get('Headache') != ['cluster','tumour']: f.add('BUG', f'shared symptom gets both labels {d}')
    if len(ev("mhCondList()")) != 2: f.add('BUG', 'registry')
    titles = lambda: ev("getAllOverlayableMetrics().filter(m=>m.isSymptom).map(m=>m.title)")
    if len(titles()) != 4: f.add('BUG', f'no filter should show all: {titles()}')
    ev("mhCondToggle('tumour')")
    t = titles()
    if 'Fatigue' not in t or 'Eye watering' in t or 'My own thing' not in t: f.add('BUG', f'tumour filter {t}')
    ev("mhCondToggle('cluster')")
    if 'Eye watering' not in titles() or 'Fatigue' not in titles(): f.add('BUG', 'two ticks should union')
    if 'Brain tumour' not in ev("mhCondChipsHtml()"): f.add('BUG', 'chips missing')
    ev("mhCondToggle('cluster'); mhCondToggle('tumour')")
    if len(titles()) != 4: f.add('BUG', 'clearing filter')
    # layout union: switch to A, then add B
    ev("(p)=>{ mhPackApply(p,['layout'],'replace'); }", A)
    if json.loads(ev("localStorage.getItem('mh_dashboard_hidden')")) != ids[:3]: f.add('BUG', 'A layout not applied')
    page.evaluate("(p)=>{ setTimeout(()=>mhFocusAdd(p),0) }", B); page.wait_for_timeout(2500)
    h = json.loads(ev("localStorage.getItem('mh_dashboard_hidden')") or '[]')
    if sorted(h) != sorted(ids[1:3]): f.add('BUG', f'union hidden {h} expected {ids[1:3]}')
    base = json.loads(ev("localStorage.getItem('mh_layout_base')") or '{}')
    if sorted(json.loads(base.get('mh_dashboard_hidden', '[]'))) != sorted(ids[1:3]): f.add('BUG', 'base not updated')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
