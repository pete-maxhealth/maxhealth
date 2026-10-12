"""Persona 115: a day with no food but a symptom score or a tag is kept at rollover (it used to vanish); a day with nothing is not invented; an existing wearable-only entry gets the score merged; no duplicates after reload; food-less days do not count as logged food days."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
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
def roll(page, day, symptoms=None, notes='', tagnotes=None, hist=None):
    page.evaluate("""([y,sx,notes,tn,hist])=>{const x=JSON.parse(localStorage.getItem('maxhealth_v1'));x.lastDate=y;x.todayLog=[];x.notes=notes;x.tagNotes=tn||{};
        if(hist) x.history=[hist].concat(x.history||[]);
        localStorage.setItem('maxhealth_v1',JSON.stringify(x)); localStorage.setItem('mh_today_notes',notes);
        if(sx){ sx.date=y; localStorage.setItem('mh_symptom_log',JSON.stringify(sx)); } else localStorage.removeItem('mh_symptom_log'); }""", [day, symptoms, notes, tagnotes, hist])
    page.reload(); page.wait_for_timeout(2000)
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); ctx.route(BLOCK, lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:150]))
    onboard(page)
    page.evaluate("saveSymptomDefs([{id:'sx1',name:'Headache',active:true}])")
    d = lambda n: fmt(datetime.now() - timedelta(days=n))
    # A: symptom only
    roll(page, d(5), {'sx1': 4})
    h = [x for x in S(page).get('history', []) if x.get('date') == d(5)]
    if len(h) != 1 or (h[0].get('symptoms') or {}) != {'sx1': 4}: f.add('BUG', f'A symptom-only day lost: {h}')
    elif (h[0].get('totals') or {}).get('kcal') != 0 or h[0].get('log'): f.add('BUG', 'A entry should have no food')
    # B: tag only
    roll(page, d(4), None, 'Treatment: Massage', {'Treatment: Massage': 'left leg'})
    h = [x for x in S(page).get('history', []) if x.get('date') == d(4)]
    if len(h) != 1 or 'Massage' not in (h[0].get('notes') or ''): f.add('BUG', f'B tag-only day lost: {h}')
    elif (h[0].get('tagNotes') or {}).get('Treatment: Massage') != 'left leg': f.add('BUG', 'B tag note lost')
    # C: nothing at all
    roll(page, d(3), None, 'standard')
    if [x for x in S(page).get('history', []) if x.get('date') == d(3)]: f.add('BUG', 'C empty day was invented')
    # D: existing wearable-only entry gets the score merged
    roll(page, d(2), {'sx1': 2}, 'standard', None, {'date': d(2), 'log': [], 'totals': {'kcal': 0, 'protein': 0, 'carbs': 0, 'fat': 0}, 'steps': 5000})
    h = [x for x in S(page).get('history', []) if x.get('date') == d(2)]
    if len(h) != 1 or (h[0].get('symptoms') or {}) != {'sx1': 2} or h[0].get('steps') != 5000: f.add('BUG', f'D merge failed: {h}')
    # reload: no duplicates
    page.reload(); page.wait_for_timeout(1500)
    dates = [x.get('date') for x in S(page).get('history', [])]
    if len(dates) != len(set(dates)): f.add('BUG', f'duplicates after reload {dates}')
    # symptom metric sees the days; food stats do not count them
    n = page.evaluate("state.history.filter(d=>d.symptoms&&d.symptoms.sx1!=null).length")
    if n < 2: f.add('BUG', f'symptom days visible {n}')
    if page.evaluate("state.history.filter(d=>(d.totals?.kcal||0)>0).length") != 0: f.add('BUG', 'food-less days counted as logged food')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
