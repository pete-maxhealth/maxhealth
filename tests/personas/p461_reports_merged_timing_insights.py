"""Persona 461 (v3.10.1376): two more Reports merges. "Fasting & when you eat" is one card with two parts (Fasting, When you eat); "Insights & what moves what" holds the old stand-alone "What seems to move what" as a part.
Each part keeps its own data-driven show/hide; the card shows when any part shows; one title, one fold, one ▲ ▼ 👁; saved layouts from before (with rpt-wheneat) carry over; search finds both by their old words. Demo persona, invented data."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    old = ['rpt-summary','rpt-insights-box','activitycredit','rpt-askai','rpt-export','rpt-sleepketo','rpt-fasting','rpt-wheneat','rpt-weightproto','rpt-treatment','rpt-gbm','rpt-research']
    page.add_init_script("localStorage.setItem('mh_reorder_reports', %s); localStorage.setItem('mh_reorder_hidden_reports', %s)" % (json.dumps(json.dumps(old[::-1])), json.dumps(json.dumps(['rpt-wheneat', 'rpt-weightproto']))))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    ev("switchTabById('reports')"); page.wait_for_timeout(800); ev("renderReports()"); page.wait_for_timeout(600)
    # structure
    for p in ('fasting-report-section', 'wheneat-report-section'):
        if not ev(f"!!document.querySelector('#rpt-fastcard #{p}')"): f.add('BUG', f'1: {p} is not inside the Fasting & when you eat card')
    if ev("!!document.getElementById('title-rpt-wheneat')"): f.add('BUG', '2: a separate When you eat title is still there')
    if 'Fasting & when you eat' not in ev("document.getElementById('title-rpt-fasting').textContent"): f.add('BUG', '3: card title')
    if not ev("!!document.querySelector('#rpt-insights-wrap #outcomes-report-section')"): f.add('BUG', '4: What seems to move what is not inside Insights')
    if ev("!!document.getElementById('title-rpt-outcomes')"): f.add('BUG', '5: a separate What seems to move what title is still there')
    if 'what moves what' not in ev("document.getElementById('title-rpt-insights-box').textContent"): f.add('BUG', '6: Insights title does not mention what moves what')
    # saved layout from before: same sequence, dead key dropped, hidden list cleaned
    order = ev("getGenericOrder('reports')"); hid = ev("getGenericHidden('reports')")
    want = [k for k in old[::-1] if k != 'rpt-wheneat']
    if order != want: f.add('BUG', f'7: old saved order not carried over in sequence: {order}')
    if hid != ['rpt-weightproto']: f.add('BUG', f'8: old hidden list not cleaned: {hid}')
    # card shows when any part shows, hides when none does
    ev("document.getElementById('fasting-report-section').style.display='none'; document.getElementById('wheneat-report-section').style.display='none'"); page.wait_for_timeout(100)
    if ev("getComputedStyle(document.getElementById('rpt-fastcard')).display") != 'none': f.add('BUG', '9: card should hide when neither part has data')
    ev("document.getElementById('wheneat-report-section').style.display='block'"); page.wait_for_timeout(100)
    if ev("getComputedStyle(document.getElementById('rpt-fastcard')).display") == 'none': f.add('BUG', '10: card should show when only When you eat has data')
    ev("document.getElementById('fasting-report-section').style.display='block'")
    # fold and hide act on the whole card
    ev("localStorage.removeItem('mh_collapse_rpt-fasting'); ev=0") if False else None
    a = ev("document.getElementById('rpt-fasting-wrap').style.display !== 'none'")
    ev("document.getElementById('title-rpt-fasting').click()"); page.wait_for_timeout(200)
    if a == ev("document.getElementById('rpt-fasting-wrap').style.display !== 'none'"): f.add('BUG', '11: the card does not fold')
    if ev("document.getElementById('wheneat-report-section').offsetParent !== null"): f.add('BUG', '12: folded card still shows a part')
    ev("document.getElementById('title-rpt-fasting').click()")
    ev("toggleGenericSectionHidden('reports','rpt-fasting')"); page.wait_for_timeout(300)
    if ev("document.getElementById('rpt-fastcard').offsetParent !== null"): f.add('BUG', '13: hide left the card showing')
    ev("toggleGenericSectionHidden('reports','rpt-fasting')"); page.wait_for_timeout(300)
    if ev("document.getElementById('rpt-fastcard').offsetParent === null"): f.add('BUG', '14: show did not bring the card back')
    if page.locator('#title-rpt-fasting .reorder-pos-badge').count() != 1: f.add('BUG', '15: the merged card lacks the standard reorder controls')
    ev("moveGenericSection('reports','rpt-fasting','down')"); ev("moveGenericSection('reports','rpt-fasting','up')")
    # Insights holds the outcomes part: fold Insights hides it
    ev("document.getElementById('outcomes-report-section').style.display='block'")
    a = ev("document.getElementById('outcomes-report-section').offsetParent !== null")
    ev("document.getElementById('title-rpt-insights-box').click()"); page.wait_for_timeout(200)
    if a and ev("document.getElementById('outcomes-report-section').offsetParent !== null"): f.add('BUG', '16: folding Insights left What seems to move what showing')
    ev("document.getElementById('title-rpt-insights-box').click()")
    # search
    S = ev("SITE_SEARCH_SETTINGS.map(x=>[x.key,x.label,x.keywords])")
    if any(k == 'rpt-wheneat' for k, _, _ in S): f.add('BUG', '17: search still has a separate When you eat entry')
    kw = {k: (l + ' ' + w).lower() for k, l, w in S}
    if 'when you eat' not in kw.get('rpt-fasting', '') or 'meal times' not in kw.get('rpt-fasting', ''): f.add('BUG', '18: search for rpt-fasting lacks the When you eat words')
    if 'move what' not in kw.get('rpt-insights-box', ''): f.add('BUG', '19: search for Insights lacks "what seems to move what"')
    # the real renders still fill their parts (no missing element errors)
    ev("renderFastingReport(); renderWhenYouEat(); renderOutcomesReport()"); page.wait_for_timeout(300)
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
