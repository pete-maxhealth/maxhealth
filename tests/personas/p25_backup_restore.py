"""Persona 25: lose everything in the browser, restore from the server backup through the app's own screens. What is not restored is reported."""
import sys, re, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
f = Findings(); BLOCK = re.compile(r'^https?://(?!localhost)')
def fmt(d): return d.strftime('%d/%m/%y')
def onboard(page):
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Bea'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('female')"); page.fill('#onboardAge', '52'); page.fill('#onboardHeight', '170')
    page.fill('#onboardWeight', '74'); page.fill('#onboardTarget', '68')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('t2_diabetes')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); ctx.route(BLOCK, lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:150])); page.on('dialog', lambda d: d.accept())
    onboard(page)
    hist = [{'date': fmt(datetime.now() - timedelta(days=i)), 'log': [{'id': i, 'time': '12:00', 'description': f'Meal {i}', 'kcal': 500 + i, 'protein': 30, 'carbs': 20, 'fat': 25, 'items': []}],
             'totals': {'kcal': 500 + i, 'protein': 30, 'carbs': 20, 'fat': 25}, 'mode': 'standard', 'notes': 'standard', 'symptoms': {'sx1': 3}} for i in range(1, 11)]
    page.evaluate("h=>{const x=JSON.parse(localStorage.getItem('maxhealth_v1'));x.history=h;x.strengthLog=[{id:'s1',date:'01/10/26',exercise:'Squat',sets:[{reps:5,weight_kg:60,note:null}]}];localStorage.setItem('maxhealth_v1',JSON.stringify(x))}", hist)
    page.reload(); page.wait_for_timeout(1200)
    page.evaluate("saveLibrary([{name:'Greek Yoghurt',kcal:97,protein:9,carbs:4,fat:5,portion:'150g',category:'dairy'}])")
    page.evaluate("saveRecipes([{id:'r1',name:'Soup',servings:2,ingredients:[{name:'Leek',kcal:30,protein:1,carbs:5,fat:0,fibre:2}],steps:['Chop'],total:{kcal:30,protein:1,carbs:5,fat:0},created:'2026-10-01'}])")
    page.evaluate("saveRoutines([{id:'rt',name:'Legs',exercises:[{name:'Squat',sets:[{reps:5,weight_kg:60,note:''}]}]}])")
    page.evaluate("saveSymptomDefs([{id:'sx1',name:'Headache',active:true}])"); page.evaluate("setSymptomScore('sx1',3)")
    page.evaluate("saveTreatmentDefs([{id:'tr1',name:'PEMF',active:true}])")
    page.evaluate("localStorage.setItem('mh_treatment_log',JSON.stringify([{id:'t1',treatmentId:'tr1',date:'01/10/26',time:'09:00',note:'x'}]))")
    page.evaluate("localStorage.setItem('mh_lab_results',JSON.stringify([{id:'l1',date:'2026-09-20',values:{ldl:3.1}}]))")
    # settings the person has chosen
    SET = {'mh_theme': 'light', 'mh_units': 'imperial', 'mh_target_fat': '120', 'mh_provider': 'claude', 'mh_target_kcal_lose': '1800'}
    page.evaluate("s=>Object.entries(s).forEach(([k,v])=>localStorage.setItem(k,v))", SET)
    before = page.evaluate("Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.startsWith('mh_')||k==='maxhealth_v1').map(([k,v])=>[k,v.length]))")
    ok = page.evaluate("saveFullBackupToServer(false)"); page.wait_for_timeout(800)
    if not ok: f.add('BUG', 'saveFullBackupToServer failed')
    lst = json.loads(urllib.request.urlopen('http://localhost:5757/list-backups').read())
    if not lst.get('backups'): f.add('BUG', 'server lists no backups after saving one')
    date = (lst.get('backups') or [{}])[0].get('date')
    snap = page.evaluate("Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.startsWith('mh_')||k==='maxhealth_v1'))")
    # catastrophe
    page.evaluate("localStorage.clear()"); page.reload(); page.wait_for_timeout(1500)
    if date:
        page.evaluate("d=>executeRestoreFromBackup(d)", date); page.wait_for_timeout(4000)
    st = page.evaluate("JSON.parse(localStorage.getItem('maxhealth_v1')||'{}')")
    if len(st.get('history', [])) != 10: f.add('BUG', f'history after restore: {len(st.get("history", []))} days, expected 10')
    if len(st.get('strengthLog', [])) != 1: f.add('BUG', 'strength log not restored')
    if page.evaluate("loadLibrary().length") != 1: f.add('BUG', 'library not restored')
    if page.evaluate("loadRecipes().length") != 1: f.add('BUG', 'recipes not restored')
    if page.evaluate("loadRoutines().length") != 1: f.add('BUG', 'routines not restored')
    if page.evaluate("loadSymptomDefs().length") != 1: f.add('BUG', 'symptom definitions not restored')
    if page.evaluate("loadTreatmentLog().length") != 1: f.add('BUG', 'treatment log not restored')
    if not page.evaluate("localStorage.getItem('mh_lab_results')"): f.add('BUG', 'lab results not restored')
    # what a person would expect back but the backup does not carry
    after = page.evaluate("Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.startsWith('mh_')||k==='maxhealth_v1'))")
    lost = [k for k in snap if k not in after and k not in ('mh_last_full_backup_date',)]
    for k in lost: f.add('NOT-RESTORED', f'{k} (was {len(snap[k])} chars) is not in the backup')
    changed = [k for k in SET if after.get(k) != SET[k]]
    for k in changed: f.add('NOT-RESTORED', f'setting {k}={SET[k]!r} came back as {after.get(k)!r}')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
bugs = list(f)
print('findings', len(f), 'real bugs', len(bugs)); sys.exit(1 if bugs else 0)
