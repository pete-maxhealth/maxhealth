"""Persona 136: the "Your routine" card on Trends. Demo: a labelled static sample that disappears on exit. Real: built from /pattern-signals (here a stubbed response) with no universal grades; still-learning states are shown honestly; an error or missing data shows nothing."""
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
        if need not in t: f.add('BUG', f'routine card missing "{need}": {t[:160]!r}')
    if any(w in t for w in ('Excellent', 'Regular exercise')): f.add('BUG', 'universal grade shown')
    # layout controls: reorder, filter, collapse, hide / restore, and a saved order from before the card existed
    ev("switchTab('insights', document.getElementById('maintab-insights'))"); page.wait_for_timeout(900); ev("mhRoutineCard()"); page.wait_for_timeout(700)
    gi = lambda: ev("getGenericOrder('trends')")
    o = gi()
    if o.index('trends-routine') != o.index('trends-patterns') - 1: f.add('BUG', f'routine not straight before Patterns by default {o}')
    if 'mcRoutine' in ev("getTrendCardsOrder()"): f.add('BUG', 'routine still in the metric-card order')
    if page.locator('#title-trends-routine .reorder-pos-badge').count() != 1: f.add('BUG', 'routine title lacks the same reorder controls as Patterns')
    # cards with no data hide themselves and the mover skips unseen cards; show the neighbour so the move is visible
    # (Journey and Body composition moved to Move in v3.10.1216, so Routine is now first: go down, then back up)
    ev("moveGenericSection('trends','trends-routine','down')"); page.wait_for_timeout(200)
    if gi().index('trends-routine') != o.index('trends-routine') + 1: f.add('BUG', 'move down did not reorder')
    ev("moveGenericSection('trends','trends-routine','up')"); page.wait_for_timeout(200)
    if gi().index('trends-routine') != o.index('trends-routine'): f.add('BUG', 'move up did not return to the start')
    ev("mhTrendsGroupSet('body')"); page.wait_for_timeout(300)
    if ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'Body filter still shows the routine card')
    ev("mhTrendsGroupSet('patterns')"); page.wait_for_timeout(300)
    if not ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'Patterns filter hides the routine card')
    ev("mhTrendsGroupSet('all')"); page.wait_for_timeout(200)
    a1 = ev("document.getElementById('trends-routine-wrap').style.display !== 'none'")
    ev("toggleSection('trends-routine','trends-routine-wrap','trends-routine-icon')"); page.wait_for_timeout(200)
    if a1 == ev("document.getElementById('trends-routine-wrap').style.display !== 'none'"): f.add('BUG', 'routine card does not fold')
    ev("toggleSection('trends-routine','trends-routine-wrap','trends-routine-icon')")
    ev("toggleGenericSectionHidden('trends','trends-routine')"); page.wait_for_timeout(400)
    if card() and ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'hide did not hide the routine card')
    if 'trends-routine' not in ev("getGenericHidden('trends')"): f.add('BUG', 'hidden list missing the routine card')
    ev("toggleGenericSectionHidden('trends','trends-routine')"); page.wait_for_timeout(900); ev("mhRoutineCard()"); page.wait_for_timeout(700)
    if not ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'unhide did not bring the routine card back')
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
    if 'EXAMPLE ONLY' not in t or 'Premium' not in t: f.add('BUG', f'demo routine card not labelled {t[:120]!r}')
    page.get_by_text('7 Days', exact=True).first.click(); page.wait_for_timeout(1200)
    if not ev("document.getElementById('mcRoutine').offsetParent !== null"): f.add('BUG', 'demo routine card not visible in the 7 Days view')
    ev("exitDemoMode()"); page.wait_for_timeout(1800)
    if card(): f.add('BUG', 'routine card left behind after the demo')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
