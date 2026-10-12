"""Persona 89: the per-screen '↺ Default' button and Settings 'Reset layout on every screen' put cards back to standard (open/closed, hidden, order, filter) without touching logged data and come back to the same screen; collapsed Today bars show live values."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    errs = []
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2500)
    ev = page.evaluate
    def calm(): ev("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    calm(); ev("switchTab('dashboard')"); page.wait_for_timeout(800)
    # live value on a collapsed bar
    ev("document.getElementById('displayWeight').innerHTML = '92.6<span>kg</span>'")
    ev("mhDcSet('weight', true); mhDcApply()")
    bar = ev("(document.querySelector('#dashSection-weight > .mh-dc-bar')||{}).textContent") or ''
    if '92.6' not in bar: f.add('BUG', f'collapsed Weight bar has no live value: {bar!r}')
    # make a mess of the layout and add real data that must survive
    ev("localStorage.setItem('mh_collapse_dc_water','closed'); localStorage.setItem('mh_dashboard_hidden', JSON.stringify(['weight'])); localStorage.setItem('mh_dashboard_order', JSON.stringify(['water','weight']));")
    ev("localStorage.setItem('mh_marker_data', 'keep-me')")
    st_before = ev("localStorage.getItem('maxhealth_v1')")
    # per-screen reset
    ev("[...document.querySelectorAll('.mh-pills-toolbar button')].filter(b=>b.offsetParent!==null && /Default/.test(b.textContent))[0].click()"); page.wait_for_timeout(400)
    if not ev("!!document.getElementById('appModalConfirm')"): f.add('BUG', 'no confirmation before resetting')
    ev("document.getElementById('appModalConfirm').click()"); page.wait_for_timeout(3500)
    keys = ev("['mh_collapse_dc_weight','mh_collapse_dc_water','mh_dashboard_hidden','mh_dashboard_order'].filter(k=>localStorage.getItem(k)!==null)")
    if keys: f.add('BUG', f'layout keys survived the screen reset: {keys}')
    if ev("localStorage.getItem('mh_marker_data')") != 'keep-me': f.add('BUG', 'reset removed non-layout data')
    if st_before is not None and ev("localStorage.getItem('maxhealth_v1')") is None: f.add('BUG', 'reset removed the saved state')
    calm()
    if not ev("document.getElementById('view-dash').classList.contains('active')"): f.add('BUG', 'did not return to the Today dashboard after the reset')
    # whole-app reset from Settings
    ev("localStorage.setItem('mh_collapse_dc_water','closed'); localStorage.setItem('mh_trend_cards_hidden', JSON.stringify(['x'])); localStorage.setItem('mh_reorder_manage', JSON.stringify(['a'])); localStorage.setItem('mh_topic_reports','x')")
    ev("mhResetAllLayout()"); page.wait_for_timeout(400)
    ev("document.getElementById('appModalConfirm').click()"); page.wait_for_timeout(3500)
    left = ev("['mh_collapse_dc_water','mh_trend_cards_hidden','mh_reorder_manage','mh_topic_reports'].filter(k=>localStorage.getItem(k)!==null)")
    if left: f.add('BUG', f'Settings reset left layout keys: {left}')
    if ev("localStorage.getItem('mh_marker_data')") != 'keep-me': f.add('BUG', 'Settings reset removed non-layout data')
    if not ev("typeof mhResetAllLayout === 'function' && /Reset layout on every screen/.test(document.documentElement.innerHTML)"): f.add('BUG', 'Settings button missing')
    if errs and any('ServiceWorker' not in e for e in errs): f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
