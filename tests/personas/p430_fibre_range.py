"""Persona 430: the Fibre history sheet used a fixed "last 14 days"; it now has the standard range control (starts on 14 days, remembered, 7/14/30/90/12 months/All/Custom, weekly averages when long)."""
import sys, datetime; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('dash')"); page.wait_for_timeout(400)
    # 120 days of history, a fibre figure on every day except every 5th
    ev("""(() => { const out = []; for (let i = 1; i <= 120; i++) { const d = new Date(); d.setDate(d.getDate() - i);
        const ds = String(d.getDate()).padStart(2,'0') + '/' + String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getFullYear()).slice(2);
        out.push({ date: ds, log: [], totals: { kcal: 1800, protein: 100, carbs: 40, fat: 120, fibre: (i % 5 === 0) ? 0 : 20 } }); } state.history = out; saveState(); })()""")
    rows = lambda: ev("[...document.querySelectorAll('#mhFibreHistModal .mh-rg ~ div')].filter(d=>d.style.display==='flex' && d.querySelector('div[style*=\"width:74px\"]')).length")
    ev("mhFibreHistory()"); page.wait_for_timeout(300)
    if not ev("!!document.querySelector('#mhFibreHistModal select.mh-rg-sel')"): f.add('BUG', 'range control is on the sheet')
    if 'last 14 days' not in ev("document.getElementById('mhFibreHistModal').innerText").lower(): f.add('BUG', 'starts on the period it always used (14 days)')
    if rows() != 14: f.add('BUG', f'14 day rows, got {rows()}')
    def pick(v): ev("(() => { const s = document.querySelector('#mhFibreHistModal select.mh-rg-sel'); s.value = %r; s.dispatchEvent(new Event('change')); })()" % str(v)); page.wait_for_timeout(300)
    pick(7)
    if rows() != 7 or 'last 7 days' not in ev("document.getElementById('mhFibreHistModal').innerText").lower(): f.add('BUG', f'7 days: {rows()} rows')
    pick(30)
    if rows() != 30: f.add('BUG', f'30 days: {rows()} rows')
    pick(90)
    t = ev("document.getElementById('mhFibreHistModal').innerText"); r = rows()
    if not (12 <= r <= 15) or 'w/c' not in t or 'weekly averages' not in t: f.add('BUG', f'90 days shows weekly averages: {r} rows')
    pick(0)
    if 'all time' not in ev("document.getElementById('mhFibreHistModal').innerText").lower(): f.add('BUG', 'All time named')
    # remembered after closing and reopening, and after a reload
    ev("document.getElementById('mhFibreHistModal').remove(); mhFibreHistory()"); page.wait_for_timeout(300)
    if ev("document.querySelector('#mhFibreHistModal select.mh-rg-sel').value") != '0': f.add('BUG', 'choice remembered when reopened')
    page.reload(); page.wait_for_timeout(1800); ev("mhFibreHistory()"); page.wait_for_timeout(300)
    if ev("document.querySelector('#mhFibreHistModal select.mh-rg-sel').value") != '0': f.add('BUG', 'choice remembered after reload')
    # custom dates: a 5-day window
    a = (datetime.date.today() - datetime.timedelta(days=6)).isoformat(); b = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    pick(-1)
    ev("(() => { const f = document.querySelector('#mhFibreHistModal .mh-rg-from'); f.value = %r; f.dispatchEvent(new Event('change')); })()" % a); page.wait_for_timeout(300)
    ev("(() => { const t = document.querySelector('#mhFibreHistModal .mh-rg-to'); t.value = %r; t.dispatchEvent(new Event('change')); })()" % b); page.wait_for_timeout(300)
    if rows() != 5: f.add('BUG', f'custom dates: 5 rows, got {rows()}')
    if ev("document.querySelector('#mhFibreHistModal .mh-rg-from').value") != a: f.add('BUG', 'custom from kept')
    page.locator('#mhFibreHistModal > div').screenshot(path='/tmp/claude-0/p430_fibre_range.png')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
