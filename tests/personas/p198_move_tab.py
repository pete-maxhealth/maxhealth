"""Persona 198: Move tab under Today. Daily steps and Today's activity live on their own tab; the Dashboard keeps a slim Move summary card; the Move cards have their own show/hide and reorder; saved Dashboard layouts migrate; Default on Move touches only Move; voice/typing layout commands and search still find the cards."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    # a layout saved before the Move tab: custom order, steps + activity in the list, steps and weather hidden
    old = ev("['water','weight','steps','activity','fasting','ketosis','macros','mealplan','macroratio','fibre','shopping','goalcheck','symptoms','treatment','weather','stats','log','guides','daymode']")
    ev("o=>{localStorage.setItem('mh_dashboard_order', JSON.stringify(o)); localStorage.setItem('mh_dashboard_hidden', JSON.stringify(['steps','weather']));}", old)
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    got = ev("getDashboardOrder()")
    if 'steps' in got or 'activity' in got: f.add('BUG', f'old keys left in the Dashboard order {got}')
    if got[:2] != ['water', 'weight'] or 'movesum' in got or 'shopping' in got: f.add('BUG', f'custom order not kept / old keys left {got[:5]}')
    if ev("getMoveHidden()") != ['steps']: f.add('BUG', f"a card hidden before should stay hidden on Move: {ev('getMoveHidden()')}")
    if ev("getDashboardHidden()") != ['weather']: f.add('BUG', f"dashboard hidden list wrong after migration {ev('getDashboardHidden()')}")
    ev("localStorage.removeItem('mh_dashboard_order'); localStorage.removeItem('mh_dashboard_hidden'); localStorage.removeItem('mh_move_hidden')"); page.reload(); page.wait_for_timeout(1500)
    if 'steps' in ev("DEFAULT_DASHBOARD_ORDER") or 'activity' in ev("DEFAULT_DASHBOARD_ORDER") or 'movesum' in ev("DEFAULT_DASHBOARD_ORDER"): f.add('BUG', 'default Dashboard order wrong')
    # the tab
    labels = ev("[...document.querySelectorAll('#view-today .sub-tab-row .sub-tab')].map(e=>e.textContent.trim())")
    if labels != ['Dashboard', 'Move', 'Supplements']: f.add('BUG', f'Today sub-tabs {labels}')
    if ev("!document.getElementById('dailyStepsCard').closest('#view-move') || !document.getElementById('activityCard').closest('#view-move')"): f.add('BUG', 'steps/activity cards not inside the Move tab')
    if ev("!!document.getElementById('view-dash').querySelector('#dailyStepsCard, #activityCard')"): f.add('BUG', 'steps/activity cards still on the Dashboard')
    if ev("!!document.getElementById('dashSection-movesum')"): f.add('BUG', 'Move glance card should not be on the Dashboard')
    ev("mhGoMove()"); page.wait_for_timeout(500)
    if ev("document.getElementById('view-move').classList.contains('active')") is not True or ev("document.getElementById('todaytab-move').classList.contains('active')") is not True: f.add('BUG', 'Open Move did not open the Move tab')
    if ev("document.getElementById('dailyStepsCard').getBoundingClientRect().height") < 40 or ev("document.getElementById('activityCard').getBoundingClientRect().height") < 40: f.add('BUG', 'Move cards not visible on the Move tab')
    # Move order and hide
    ev("moveMoveSection('steps','down')")
    if ev("getMoveOrder().slice(0,2)") != ['activity', 'steps']: f.add('BUG', 'Move reorder failed')
    if ev("[...document.getElementById('moveScroll').children].map(e=>e.id).filter(i=>i==='dailyStepsCard'||i==='activityCard')") != ['activityCard', 'dailyStepsCard']: f.add('BUG', 'Move reorder did not move the cards')
    page.reload(); page.wait_for_timeout(1500); ev("switchTabById('move')"); page.wait_for_timeout(400)
    if ev("getMoveOrder().slice(0,2)") != ['activity', 'steps'] or ev("[...document.getElementById('moveScroll').children].map(e=>e.id).filter(i=>i==='dailyStepsCard'||i==='activityCard')") != ['activityCard', 'dailyStepsCard']: f.add('BUG', 'Move order not remembered across reload')
    ev("toggleMoveSectionHidden('steps')")
    if ev("getComputedStyle(document.getElementById('dailyStepsCard')).display") != 'none': f.add('BUG', 'Move hide failed')
    if 'Steps' not in ev("document.getElementById('moveRestoreStrip').innerText"): f.add('BUG', 'no way to bring a hidden Move card back')
    ev("toggleMoveSectionHidden('steps')")
    if ev("getComputedStyle(document.getElementById('dailyStepsCard')).display") == 'none': f.add('BUG', 'Move restore failed')
    # Default on Move touches only Move
    ks = ev("mhLayoutKeys(document.getElementById('view-move'))")
    if 'mh_move_order' not in ks or 'mh_move_hidden' not in ks or 'mh_dashboard_order' in ks or 'mh_dashboard_hidden' in ks: f.add('BUG', f'Default on Move touches the wrong keys {ks}')
    # typing a layout command
    ev("handleLayoutQuery('hide the steps card')")
    if 'steps' not in ev("getMoveHidden()") or 'steps' in ev("getDashboardHidden()"): f.add('BUG', 'typed hide of the steps card went to the wrong list')
    ev("handleLayoutQuery('show the steps card')")
    if 'steps' in ev("getMoveHidden()"): f.add('BUG', 'typed show of the steps card failed')
    # search finds them on the Move tab
    hits = ev("(()=>{const l=SITE_SEARCH_SETTINGS; return l.filter(x=>['dash-activity','dash-steps','dash-strength-list'].includes(x.key)).map(x=>x.subtab)})()")
    if len(hits) != 3 or any(h != 'move' for h in hits): f.add('BUG', f'search index still points at the Dashboard for exercise cards {hits}')
    # content still renders
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
