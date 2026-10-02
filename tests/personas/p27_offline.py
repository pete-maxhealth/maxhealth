"""Persona 27: offline mode - banner, internet-only features explain themselves, save-for-later queue, review on reconnect."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
f = Findings(); BLOCK = re.compile(r'^https?://(?!localhost)')
def onboard(page):
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
def S(page): return page.evaluate("JSON.parse(localStorage.getItem('maxhealth_v1')||'{}')")
FOOD = {"type": "food", "items": [{"name": "lentil chorizo stew", "amount": "300g", "kcal": 420, "protein": 25, "fat": 20, "carbs": 30}], "message": "Lentil chorizo stew"}
bar_cls = "document.getElementById('mhNetBar').className"
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; calls = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(BLOCK, lambda r: r.abort())
    def stub(route):
        calls.append(1)
        route.fulfill(status=200, content_type='application/json', body=json.dumps({"content": [{"type": "text", "text": json.dumps(FOOD)}], "usage": {"input_tokens": 1, "output_tokens": 1}}))
    ctx.route(re.compile(r'^https://api\.anthropic\.com/.*'), stub)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    onboard(page)
    page.evaluate("localStorage.setItem('mh_provider','claude');localStorage.setItem('mh_apikey','sk-ant-test-123')"); page.reload(); page.wait_for_timeout(1500)

    # online: no banner
    if page.evaluate(bar_cls) != '': f.add('BUG', 'banner showing while online')

    # an internet request fails -> offline detected and banner appears
    page.evaluate("fetch('https://example.com/x').catch(()=>{})"); page.wait_for_timeout(1500)
    if page.evaluate(bar_cls) != 'off': f.add('BUG', f'no offline banner after an internet failure: {page.evaluate(bar_cls)!r}')
    if 'offline' not in page.inner_text('#mhNetBar').lower(): f.add('BUG', 'offline banner has no text')
    # banner stays on every main tab
    for tab in ('today', 'log', 'insights'):
        page.click(f"[onclick^=\"switchTab('{tab}'\"]"); page.wait_for_timeout(300)
        vis = page.evaluate("(()=>{const r=document.getElementById('mhNetBar').getBoundingClientRect();return r.height>10&&r.top>=0})()")
        if not vis: f.add('BUG', f'offline banner not visible on the {tab} tab')

    # internet-only features explain themselves and make no network call
    n0 = len(calls)
    page.evaluate("runMultiAICheck()"); page.wait_for_timeout(300)
    if 'needs internet' not in page.inner_text('body') : f.add('BUG', 'no "needs internet" explanation when tapping Verify across 3 AIs offline')
    if len(calls) != n0: f.add('BUG', 'AI call made while offline')
    page.evaluate("document.body.insertAdjacentHTML('beforeend','<button id=tstBtn onclick=\"runMultiAICheck()\">Verify</button>')")
    content = page.evaluate("getComputedStyle(document.getElementById('tstBtn'),'::after').content")
    if 'needs internet' not in content: f.add('BUG', f'AI button has no "needs internet" note offline: {content!r}')

    # meal typed offline -> choices, no AI call; save for later
    page.click("[onclick^=\"switchTab('log'\"]"); page.wait_for_timeout(300)
    page.evaluate("processMessage('homemade lentil and chorizo stew with kale')"); page.wait_for_timeout(600)
    if 'save it for when' not in page.inner_text('#chatScroll').lower(): f.add('BUG', 'no save-for-later choice offered offline')
    if len(calls) != n0: f.add('BUG', 'AI call made for a meal while offline')
    page.evaluate("mhOfflineSave()"); page.wait_for_timeout(300)
    q = page.evaluate("JSON.parse(localStorage.getItem('mh_offline_queue')||'[]')")
    if len(q) != 1 or 'stew' not in q[0]['text']: f.add('BUG', f'queue wrong: {q}')
    if '1 saved entry waiting' not in page.inner_text('#mhNetBar').lower(): f.add('BUG', f'banner does not show the waiting entry: {page.inner_text("#mhNetBar")!r}')
    if page.evaluate("S=>_collectBackupSettings()", None).get('mh_offline_queue') is None: f.add('BUG', 'saved entries are not part of the backup')
    # manual path still works offline
    page.evaluate("mhOfflineChoice('toast')"); page.evaluate("mhOfflineManual()"); page.wait_for_timeout(200)
    if not page.query_selector('#manualEntryBubble'): f.add('BUG', 'manual entry form did not open offline')
    page.evaluate("document.getElementById('manualEntryBubble')?.remove()")

    # reload while still offline: queue survives and the app notices it is offline
    page.reload(); page.wait_for_timeout(3500)
    if page.evaluate("mhQueueCount()") != 1: f.add('BUG', 'queue lost on reload')
    if page.evaluate(bar_cls) != 'off': f.add('BUG', f'after reload with a saved entry and no internet the banner is {page.evaluate(bar_cls)!r}, expected off')

    # connection returns
    ctx.route(re.compile(r'^https://www\.gstatic\.com/.*'), lambda r: r.fulfill(status=204, body=''))
    page.evaluate("window.dispatchEvent(new Event('online'))"); page.wait_for_timeout(1500)
    if page.evaluate(bar_cls) != 'back': f.add('BUG', f'no back-online banner: {page.evaluate(bar_cls)!r}')
    if 'review' not in page.inner_text('#mhNetBar').lower(): f.add('BUG', 'back-online banner has no Review button')
    # queued time is kept: pretend it was saved at 07:45
    page.evaluate("()=>{const q=JSON.parse(localStorage.getItem('mh_offline_queue'));q[0].time='07:45';localStorage.setItem('mh_offline_queue',JSON.stringify(q))}")
    n1 = len(calls)
    page.evaluate("mhReviewQueue()"); page.wait_for_timeout(2500)
    if len(calls) == n1: f.add('BUG', 'review did not send the saved meal to the AI')
    if 'log it' not in page.inner_text('#chatScroll').lower(): f.add('BUG', 'no confirm preview after review (entries must never log unseen)')
    if S(page).get('todayLog'): f.add('BUG', 'saved entry logged WITHOUT confirmation')
    page.evaluate("confirmMealLog()"); page.wait_for_timeout(1200)
    tl = S(page).get('todayLog') or []
    if len(tl) != 1 or tl[0].get('time') != '07:45': f.add('BUG', f'confirmed entry wrong or lost its saved time: {[(e.get("description"), e.get("time")) for e in tl]}')
    if page.evaluate("mhQueueCount()") != 0 or page.evaluate(bar_cls) != '': f.add('BUG', 'queue/banner not cleared after reviewing the only entry')

    # saved for a past day that exists in history -> logs on that day
    d2 = (datetime.now() - timedelta(days=2)).strftime('%d/%m/%y')
    page.evaluate("d=>{const x=JSON.parse(localStorage.getItem('maxhealth_v1'));x.history=x.history||[];x.history.unshift({date:d,log:[],totals:{kcal:0,protein:0,carbs:0,fat:0},mode:'standard',notes:'standard'});localStorage.setItem('maxhealth_v1',JSON.stringify(x))}", d2)
    page.reload(); page.wait_for_timeout(1500)
    page.evaluate("d=>localStorage.setItem('mh_offline_queue',JSON.stringify([{id:1,text:'homemade lentil and chorizo stew with kale',img:null,mime:null,date:d,time:'19:10',savedAt:''}]))", d2)
    page.evaluate("mhReviewQueue()"); page.wait_for_timeout(2500); page.evaluate("confirmMealLog()"); page.wait_for_timeout(1200)
    st = S(page); h = [x for x in st.get('history', []) if x.get('date') == d2]
    if not h or not h[0].get('log') or h[0]['log'][-1].get('time') != '19:10': f.add('BUG', f'entry saved for {d2} did not land on that day with its time: {h[0].get("log") if h else None}')
    if len(st.get('todayLog') or []) != 1: f.add('BUG', 'past-day entry also leaked into today')

    # cancel path: nothing logged, no override left behind for the next normal log
    page.evaluate("localStorage.setItem('mh_offline_queue',JSON.stringify([{id:2,text:'homemade lentil and chorizo stew with kale',img:null,mime:null,date:'x',time:'03:33',savedAt:''}]))")
    page.evaluate("mhReviewQueue()"); page.wait_for_timeout(2500); page.evaluate("cancelMealPreview()"); page.wait_for_timeout(300)
    if len(S(page).get('todayLog') or []) != 1: f.add('BUG', 'cancelled review still logged something')
    if page.evaluate("window._mhQueuedOverride") is not None: f.add('BUG', 'override left behind after cancel')
    page.evaluate("processMessage('two boiled eggs')"); page.wait_for_timeout(2500); page.evaluate("confirmMealLog()"); page.wait_for_timeout(1000)
    tl = S(page).get('todayLog') or []
    if any(e.get('time') == '03:33' for e in tl): f.add('BUG', 'a later normal log inherited the cancelled entry\'s saved time')

    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
