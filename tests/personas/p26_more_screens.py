"""Persona 26: missed-day flow, lab results, Insights with a long history, demo mode, AI chat, carer view."""
import sys, re, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
f = Findings(); BLOCK = re.compile(r'^https?://(?!localhost)')
def fmt(d): return d.strftime('%d/%m/%y')
def onboard(page, cond='general'):
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Cy'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate(f"obSetCondition('{cond}')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
def S(page): return page.evaluate("JSON.parse(localStorage.getItem('maxhealth_v1')||'{}')")
FOOD = {"type": "food", "items": [{"name": "boiled egg", "amount": "2 eggs", "kcal": 156, "protein": 12.6, "fat": 10.6, "carbs": 1.1}], "message": "Two boiled eggs"}
AI_DAY = {"kcal": 2100, "protein": 120, "carbs": 90, "fat": 95, "fibre": 20, "polyols": 0, "breakdown": "Toast, curry, wine"}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; calls = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(BLOCK, lambda r: r.abort())
    def stub(route):
        req = json.loads(route.request.post_data or '{}'); calls.append(req)
        out = FOOD if req.get('system') else AI_DAY
        route.fulfill(status=200, content_type='application/json', body=json.dumps({"content": [{"type": "text", "text": json.dumps(out)}], "usage": {"input_tokens": 1, "output_tokens": 1}}))
    ctx.route(re.compile(r'^https://api\.anthropic\.com/.*'), stub)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    onboard(page)
    page.evaluate("localStorage.setItem('mh_provider','claude');localStorage.setItem('mh_apikey','sk-ant-test-123')"); page.reload(); page.wait_for_timeout(1200)

    # ── missed day ──
    yday = fmt(datetime.now() - timedelta(days=2))
    page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(300)
    page.evaluate("startMissedDayFlow()"); page.evaluate("d=>selectMissedDate(d)", yday); page.wait_for_timeout(300)
    page.evaluate("document.getElementById('missedDayConvMeals').value='toast, a curry and a glass of wine'"); page.evaluate("calculateMissedDayConv()"); page.wait_for_timeout(1800)
    if '2100' not in page.inner_text('#chatScroll'): f.add('BUG', 'missed-day result not shown')
    page.evaluate("saveMissedDayConv(2100,120,90,95,0,20)"); page.wait_for_timeout(1500)
    h = [x for x in S(page).get('history', []) if x.get('date') == yday]
    if len(h) != 1 or round(h[0]['totals']['kcal']) != 2100: f.add('BUG', f'missed day not saved correctly: {h}')
    import os
    mp = root + '/data/tables/master.csv'; master = open(mp).read() if os.path.exists(mp) else ''
    if yday not in master or '2100' not in master: f.add('BUG', 'missed day never reached the server master.csv')
    for bad, why in (('31/02/26', 'impossible date'), (fmt(datetime.now() + timedelta(days=3)), 'future date'), (fmt(datetime.now()), "today's date")):
        page.evaluate("startMissedDayFlow()"); page.evaluate("v=>{document.getElementById('missedDateCustom').value=v}", bad); page.evaluate("selectMissedDateCustom()"); page.wait_for_timeout(300)
        if page.evaluate("typeof _missedDayConvDate!=='undefined' && _missedDayConvDate") == bad:
            f.add('BUG', f'missed-day flow accepted an {why} ({bad})')
        page.evaluate("cancelMissedDayFlow()")

    # ── lab results ──
    page.evaluate("logLabPanel('20/09/26',{ldl:3.4,total_chol:5.6},[],'GP')"); page.evaluate("logLabPanel('20/06/26',{ldl:3.9},[],'GP')")
    labs = page.evaluate("loadLabResults()")
    if [l['date'] for l in labs] != ['20/09/26', '20/06/26']: f.add('BUG', f'lab panels not sorted newest first: {[l["date"] for l in labs]}')
    tr = page.evaluate("getLabMarkerTrend('ldl')")
    if not tr or len(tr) != 2: f.add('BUG', f'LDL trend should have 2 points: {tr}')
    for fn in ("renderLabResultsSettings()", "renderLabTrendChips()"):
        try: page.evaluate(fn)
        except Exception as e: f.add('JS-exception', f'{fn}: {str(e)[:120]}')

    # ── Insights with a long history ──
    d = days(60)
    write_hc_export(root, [{'date': x, 'steps': 5000 + i * 40, 'sleep_duration': 380 + (i % 7) * 12, 'hr_avg': 62 + i % 5, 'hrv': 40 + i % 9, 'spo2': 95 + (i % 3) * 0.7, 'weight': round(82 - i * 0.05, 1)} for i, x in enumerate(d)])
    run_pipeline(root)
    hist = [{'date': fmt(datetime.now() - timedelta(days=i)), 'log': [{'id': i, 'time': '12:00', 'description': 'x', 'kcal': 1800 + (i % 6) * 60, 'protein': 100, 'carbs': 30 + (i % 5) * 10, 'fat': 110, 'items': []}],
             'totals': {'kcal': 1800 + (i % 6) * 60, 'protein': 100, 'carbs': 30 + (i % 5) * 10, 'fat': 110}, 'mode': 'standard', 'notes': 'standard', 'symptoms': {'sx1': 1 + i % 5}} for i in range(3, 63)]
    page.evaluate("h=>{const x=JSON.parse(localStorage.getItem('maxhealth_v1'));x.history=h;localStorage.setItem('maxhealth_v1',JSON.stringify(x));saveSymptomDefs([{id:'sx1',name:'Headache',active:true}])}", hist)
    page.reload(); page.wait_for_timeout(2500)
    page.click("[onclick^=\"switchTab('insights'\"]"); page.wait_for_timeout(600)
    for tab in ('trends', 'reports'):
        page.evaluate("t=>switchSubTab('insights',t,null)", tab); page.wait_for_timeout(900)
    for fn in ("typeof renderPatterns==='function' && renderPatterns()", "typeof renderCompareMetrics==='function' && renderCompareMetrics()", "typeof renderTrends==='function' && renderTrends()"):
        try: page.evaluate(fn)
        except Exception as e: f.add('JS-exception', f'{fn[:40]}: {str(e)[:120]}')
    body = page.inner_text('body')
    if 'NaN' in body or 'undefined' in body or '[object Object]' in body: f.add('BUG', 'Insights shows NaN/undefined/[object Object]')

    # ── AI chat Q&A ──
    calls.clear()
    page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(300)
    page.evaluate("document.getElementById('chatInput').value='I had two boiled eggs for lunch'"); page.click("[onclick=\"sendChat()\"]"); page.wait_for_timeout(3000)
    if not calls: f.add('BUG', 'a free-text question never reached the AI')
    else:
        sysp = str(calls[0].get('system', ''))
        if 'Cy' not in sysp and '58' not in sysp: f.add('BUG', 'AI context lacks the profile (name/age)')
        page.wait_for_timeout(500)
        if '156' not in page.inner_text('body'): f.add('BUG', 'AI reply (156 kcal) not shown on the meal preview')

    # ── demo mode round trip ──
    before = page.evaluate("localStorage.getItem('maxhealth_v1')")
    page.evaluate("startDemoMode(DEMO_PERSONAS[0].id)"); page.wait_for_timeout(2500)
    if len(page.inner_text('body')) < 500: f.add('BUG', 'demo mode rendered an almost empty screen')
    page.evaluate("exitDemoMode()"); page.wait_for_timeout(2500)
    after = page.evaluate("localStorage.getItem('maxhealth_v1')")
    if json.loads(after).get('history') != json.loads(before).get('history'): f.add('BUG', 'exiting demo mode changed the real history')
    if errs: f.add('JS-exception', str(errs[:3]))

    # ── carer view ──
    p2 = ctx.new_page(); e2 = []; p2.on('pageerror', lambda e: e2.append(str(e)[:150]))
    p2.goto('http://localhost:5757/carer.html'); p2.wait_for_timeout(2000)
    if e2: f.add('JS-exception', f'carer.html: {e2[:2]}')
    if len(p2.inner_text('body')) < 50: f.add('BUG', 'carer.html is blank')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
