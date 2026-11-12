"""Persona 136: the "Your usual" part of the merged Patterns & routine tile on Trends (v3.10.1375: it used to be its own card). Demo: a labelled static sample that disappears on exit. Real: built from /pattern-signals (here a stubbed response) with no universal grades; still-learning states are shown honestly; an error or missing data shows nothing."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
GOOD = {'status': 'All 4 signals ready, compared with your own history.', 'meal_windows': {'Breakfast': '08:00-08:20', 'Dinner': '19:00-19:30'},
        'sleep_circadian': {'duration': '7h05m', 'typical_bedtime': '23:10', 'bedtime_spread': '±18 min', 'regularity': 'fairly regular', 'recent_vs_usual': 'in line with your usual'},
        'activity_pattern': {'usual_steps': '6,000', 'this_week_vs_usual': 'noticeably higher than usual'},
        'hrv_baseline': {'baseline_hrv': '45ms', 'latest_hrv': '30ms', 'status': 'below your usual range', 'usual_range': '40-50ms'}}
LEARN = {'status': '1 of 4 signals ready, still building: sleep, activity, hrv.', 'meal_windows': {}, 'sleep_circadian': {'status': 'building (1 of 3 nights)'}, 'activity_pattern': {'usual_steps': '6,000', 'status': 'building (2 of 7 days)'}, 'hrv_baseline': {}}
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    def card(): return ev("(()=>{const e=document.getElementById('mcRoutine'); return e && !e.hidden && e.style.display!=='none' ? e.textContent : ''})()")
    def serve(payload, status=200):
        page.unroute('**/pattern-signals*')
        page.route('**/pattern-signals*', lambda r: r.fulfill(status=status, content_type='application/json', body=json.dumps(payload)))
    serve(GOOD); ev("mhRoutineCard()"); page.wait_for_timeout(700); t = card()
    for need in ('Breakfast 08:00-08:20', '7h05m', 'bed about 23:10', 'noticeably higher than usual', 'below your usual range', 'from your own history'):
        if need not in t: f.add('BUG', f'routine part missing "{need}": {t[:160]!r}')
    if any(w in t for w in ('Excellent', 'Regular exercise')): f.add('BUG', 'universal grade shown')
    # layout controls: reorder, filter, collapse, hide / restore, and a saved order from before the card existed
    ev("switchTab('insights', document.getElementById('maintab-insights'))"); page.wait_for_timeout(900); ev("mhRoutineCard()"); page.wait_for_timeout(700)
    gi = lambda: ev("getGenericOrder('trends')")
    o = gi()
    if 'trends-routine' in o or 'trends-patterns' not in o: f.add('BUG', f'merged tile: the order should hold trends-patterns and no separate trends-routine {o}')
    if ev("!document.querySelector('#patternsCard #mcRoutine')"): f.add('BUG', 'routine is not inside the Patterns & routine tile')
    if ev("!!document.getElementById('title-trends-routine')"): f.add('BUG', 'a separate Your routine title is still on the page')
    if 'Patterns & routine' not in ev("document.getElementById('title-trends-patterns').textContent"): f.add('BUG', 'tile title does not say Patterns & routine')
    if 'mcRoutine' in ev("getTrendCardsOrder()"): f.add('BUG', 'routine still in the metric-card order')
    if page.locator('#title-trends-patterns .reorder-pos-badge').count() != 1: f.add('BUG', 'the merged tile lacks the standard reorder controls')
    # a layout saved before the merge (a separate trends-routine key, hidden or ordered) must not break or reset anything
    ev("localStorage.setItem('mh_reorder_trends', JSON.stringify(['trends-wellness','trends-routine','trends-patterns','trends-periodcmp'])); localStorage.setItem('mh_reorder_hidden_trends', JSON.stringify(['trends-routine','trends-periodcmp']))")
    o2 = gi(); h2 = ev("getGenericHidden('trends')")
    if o2 != ['trends-wellness', 'trends-patterns', 'trends-periodcmp']: f.add('BUG', f'old saved order not carried over in the same sequence: {o2}')
    if h2 != ['trends-periodcmp']: f.add('BUG', f'old hidden list not cleaned (periodcmp stays hidden, routine key dropped): {h2}')
    ev("localStorage.removeItem('mh_reorder_trends'); localStorage.removeItem('mh_reorder_hidden_trends')"); ev("applyGenericOrder('trends')")
    ev("moveGenericSection('trends','trends-patterns','down')"); page.wait_for_timeout(200)
    ev("moveGenericSection('trends','trends-patterns','up')"); page.wait_for_timeout(200)
    if gi() != o: f.add('BUG', 'move down then up did not return to the start')
    ev("mhTrendsGroupSet('body')"); page.wait_for_timeout(300)
    if ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'Body filter still shows the routine part')
    ev("mhTrendsGroupSet('patterns')"); page.wait_for_timeout(300)
    if not ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'Patterns filter hides the routine part')
    ev("mhTrendsGroupSet('all')"); page.wait_for_timeout(200)
    a1 = ev("document.getElementById('trends-patterns-wrap').style.display !== 'none'")
    ev("toggleSection('trends-patterns','trends-patterns-wrap','trends-patterns-icon')"); page.wait_for_timeout(200)
    if a1 == ev("document.getElementById('trends-patterns-wrap').style.display !== 'none'"): f.add('BUG', 'merged tile does not fold')
    if ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'folded tile still shows the routine part')
    ev("toggleSection('trends','trends-patterns','trends-patterns-icon')") if False else ev("toggleSection('trends-patterns','trends-patterns-wrap','trends-patterns-icon')")
    ev("toggleGenericSectionHidden('trends','trends-patterns')"); page.wait_for_timeout(400)
    if ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'hide did not hide the routine part')
    if 'trends-patterns' not in ev("getGenericHidden('trends')"): f.add('BUG', 'hidden list missing the merged tile')
    ev("toggleGenericSectionHidden('trends','trends-patterns')"); page.wait_for_timeout(900); ev("mhRoutineCard()"); page.wait_for_timeout(700)
    if not ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'unhide did not bring the routine part back')
    ev("localStorage.setItem('mh_trend_cards_order', JSON.stringify(['mcRoutine'].concat(DEFAULT_TREND_CARDS_ORDER.slice().reverse())))")
    mig = ev("getTrendCardsOrder()")
    if 'mcRoutine' in mig or len(mig) != ev('DEFAULT_TREND_CARDS_ORDER.length'): f.add('BUG', f'old saved order not migrated {mig[:3]}')
    ev("localStorage.removeItem('mh_trend_cards_order')")
    serve(LEARN); ev("mhRoutineCard()"); page.wait_for_timeout(700); t = card()
    if 'Still learning' not in t or 'building (1 of 3 nights)' not in t: f.add('BUG', f'learning state not shown honestly {t[:160]!r}')
    serve({'error': 'Required data files not found'}, 404); ev("mhRoutineCard()"); page.wait_for_timeout(700)
    if card(): f.add('BUG', 'card shown for a missing-data response')
    serve({'error': 'boom'}, 500); ev("mhRoutineCard()"); page.wait_for_timeout(700)
    if card(): f.add('BUG', 'card shown on a server error')
    ev("startDemoMode(DEMO_PERSONAS[0].id)"); page.wait_for_timeout(2800); t = card()
    if 'EXAMPLE ONLY' not in t or 'Premium' not in t: f.add('BUG', f'demo routine part not labelled {t[:120]!r}')
    page.get_by_text('7 Days', exact=True).first.click(); page.wait_for_timeout(1200)
    if not ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'demo routine card not visible in the 7 Days view')
    ev("exitDemoMode()"); page.wait_for_timeout(1800)
    if card(): f.add('BUG', 'routine card left behind after the demo')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
