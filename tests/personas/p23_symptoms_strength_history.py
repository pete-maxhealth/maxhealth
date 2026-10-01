"""Persona 23: symptoms reaching history at rollover, treatments, a routine workout through to the server, History screen."""
import sys, re, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
f = Findings(); BLOCK = re.compile(r'^https?://(?!localhost)')
def fmt(d): return d.strftime('%d/%m/%y')
def onboard(page):
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Sam'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '47'); page.fill('#onboardHeight', '180')
    page.fill('#onboardWeight', '85'); page.fill('#onboardTarget', '80')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('moderate')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1200)
def S(page): return page.evaluate("JSON.parse(localStorage.getItem('maxhealth_v1')||'{}')")
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); ctx.route(BLOCK, lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:150])); page.on('dialog', lambda d: d.accept('right leg'))
    onboard(page)

    # ── symptoms: score today, roll the day over, the score must be in history ──
    page.evaluate("saveSymptomDefs([{id:'sx1',name:'Headache',active:true},{id:'sx2',name:'Fatigue',active:true}])")
    page.evaluate("setSymptomScore('sx1',4)"); page.evaluate("setSymptomScore('sx2',2)")
    yday = fmt(datetime.now() - timedelta(days=1))
    page.evaluate("""y=>{const x=JSON.parse(localStorage.getItem('maxhealth_v1'));x.lastDate=y;
        x.todayLog=[{id:1,time:'08:00',description:'Eggs',kcal:300,protein:20,carbs:2,fat:22,items:[]}];
        localStorage.setItem('maxhealth_v1',JSON.stringify(x));
        const l=JSON.parse(localStorage.getItem('mh_symptom_log'));l.date=y;localStorage.setItem('mh_symptom_log',JSON.stringify(l));}""", yday)
    page.reload(); page.wait_for_timeout(2000)
    h = [x for x in S(page).get('history', []) if x.get('date') == yday]
    if not h: f.add('BUG', 'rollover did not write yesterday')
    elif (h[0].get('symptoms') or {}) != {'sx1': 4, 'sx2': 2}: f.add('BUG', f'symptom scores did not reach history at rollover: {h[0].get("symptoms")}')
    page.reload(); page.wait_for_timeout(1500)
    h = [x for x in S(page).get('history', []) if x.get('date') == yday]
    if len(h) != 1 or (h[0].get('symptoms') or {}) != {'sx1': 4, 'sx2': 2}: f.add('BUG', 'symptoms lost or history duplicated after a second load')
    if page.evaluate("loadSymptomLog().sx1") not in (None,): f.add('BUG', 'today started with yesterday\'s symptom scores')

    # ── treatments: define, log, delete ──
    page.evaluate("saveTreatmentDefs([{id:'tr1',name:'PEMF',active:true}])")
    page.evaluate("logTreatmentSession('tr1')")
    lg = page.evaluate("loadTreatmentLog()")
    if len(lg) != 1 or lg[0].get('treatmentId') != 'tr1' or lg[0].get('date') != fmt(datetime.now()): f.add('BUG', f'treatment session not logged correctly: {lg}')
    elif lg[0].get('note') != 'right leg': f.add('BUG', f'treatment note lost: {lg[0].get("note")}')
    page.evaluate("id=>deleteTreatmentSession(id)", lg[0]['id'] if lg else '')
    if page.evaluate("loadTreatmentLog().length") != 0: f.add('BUG', 'treatment session not deleted')

    # ── routine workout → strength log → server → restore ──
    ex = [{'name': 'Bench Press', 'sets': [{'reps': 8, 'weight_kg': 40, 'note': ''}, {'reps': 8, 'weight_kg': 42.5, 'note': ''}]},
          {'name': 'Row', 'sets': [{'reps': 10, 'weight_kg': 30, 'note': ''}]}]
    page.evaluate("e=>saveRoutines([{id:'rt1',name:'Push Pull',exercises:e}])", ex)
    page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(300)
    page.evaluate("applyRoutine('rt1')"); page.wait_for_timeout(300)
    page.evaluate("document.getElementById('routineSessionDuration').value='45'")
    page.evaluate("saveRoutineSession()"); page.wait_for_timeout(1500)
    sl = S(page).get('strengthLog', [])
    if len(sl) != 2: f.add('BUG', f'expected 2 strength entries from the routine, found {len(sl)}')
    else:
        if [len(s['sets']) for s in sl] != [2, 1]: f.add('BUG', f'set counts wrong: {[len(s["sets"]) for s in sl]}')
        if sl[0]['sets'][1]['weight_kg'] != 42.5: f.add('BUG', f'weight changed: {sl[0]["sets"][1]}')
    res = page.evaluate("getActivities().find(a=>a.type==='resistance')")
    if not res or not res.get('enabled') or str(res.get('duration')) != '45': f.add('BUG', f'Resistance activity not credited with 45 min: {res}')
    csv_text = urllib.request.urlopen('http://localhost:5757/strength').read().decode()
    if 'Bench Press' not in csv_text or '42.5' not in csv_text: f.add('BUG', 'strength session never reached the server CSV')
    page.evaluate("()=>{const x=JSON.parse(localStorage.getItem('maxhealth_v1'));x.strengthLog=[];localStorage.setItem('maxhealth_v1',JSON.stringify(x))}")
    page.reload(); page.wait_for_timeout(3500)
    sl2 = S(page).get('strengthLog', [])
    if len(sl2) != 2: f.add('BUG', f'strength log not restored from the server after a wipe ({len(sl2)} sessions)')
    elif sl2[0]['sets'][1]['weight_kg'] != 42.5: f.add('BUG', f'restored weight wrong: {sl2[0]["sets"][1]}')

    # ── History screen with several days ──
    seed = []
    for i in range(1, 6):
        d = fmt(datetime.now() - timedelta(days=i))
        seed.append({'date': d, 'log': [{'id': i, 'time': '12:00', 'description': f'Meal {i}', 'kcal': 400 + i, 'protein': 30, 'carbs': 10, 'fat': 20, 'items': []}],
                     'totals': {'kcal': 400 + i, 'protein': 30, 'carbs': 10, 'fat': 20}, 'mode': 'standard', 'notes': 'standard'})
    page.evaluate("s=>{const x=JSON.parse(localStorage.getItem('maxhealth_v1'));x.history=s;localStorage.setItem('maxhealth_v1',JSON.stringify(x))}", seed)
    page.reload(); page.wait_for_timeout(1500)
    page.click("[onclick^=\"switchTab('insights'\"]"); page.wait_for_timeout(500)
    try: page.evaluate("switchSubTab('insights','history',null)")
    except Exception: pass
    page.evaluate("renderHistory()"); page.wait_for_timeout(500)
    body = page.inner_text('#histEntries')
    for i in (1, 3, 5):
        if str(400 + i) not in body: f.add('BUG', f'History does not show day {i} ({400+i} kcal)')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
