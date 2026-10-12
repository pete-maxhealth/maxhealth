"""Persona 88: Close all on Today really collapses the big cards (Weight, Calories & macros, Macro ratio, Water, Fasting ...) to one-line bars, the count is honest, tapping a bar opens just that card, Open all restores everything, and an empty card gets no bar."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    errs = []
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2500)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    page.evaluate("switchTab('dashboard')"); page.wait_for_timeout(800)
    ev = page.evaluate
    h = lambda i: ev("(i)=>{const e=document.getElementById(i);return e&&e.offsetParent?Math.round(e.getBoundingClientRect().height):0}", i)
    ids = ['dashSection-weight', 'dashSection-macros', 'macroRatioCard', 'dashSection-water', 'dashSection-fasting']
    before = {i: h(i) for i in ids}
    ev("[...document.querySelectorAll('.mh-pills-toolbar button')].filter(b=>b.offsetParent!==null && /Close all/.test(b.textContent))[0].click()"); page.wait_for_timeout(500)
    after = {i: h(i) for i in ids}
    for i in ids:
        if not (0 < after[i] < 70): f.add('BUG', f'{i} did not shrink to a bar: {before[i]} -> {after[i]}')
    toast = ev("(document.querySelector('.toast, #toast')||{}).textContent") or ''
    import re as _re
    m = _re.search(r'Closed (\d+)', toast)
    shrunk = sum(1 for i in ids if after[i] < before[i])
    if not m or int(m.group(1)) < shrunk: f.add('BUG', f'toast count {toast!r} below the {shrunk} cards that shrank')
    if ev("document.getElementById('dashSection-goalcheck').querySelector(':scope > .mh-dc-bar') !== null && document.getElementById('dashSection-goalcheck').offsetParent !== null && document.getElementById('dashSection-goalcheck').getBoundingClientRect().height > 8 && !document.getElementById('dashSection-goalcheck').classList.contains('mh-dc-closed')"): f.add('BUG', 'empty card misbehaves')
    # persists across a re-render
    ev("updateDashboard()"); page.wait_for_timeout(300)
    if h('dashSection-weight') >= 70: f.add('BUG', 'collapsed state lost on re-render')
    # tapping the bar opens only that card
    ev("document.querySelector('#dashSection-weight > .mh-dc-bar').click()"); page.wait_for_timeout(300)
    if h('dashSection-weight') < 70: f.add('BUG', 'tapping the bar did not open the Weight card')
    if h('dashSection-macros') >= 70: f.add('BUG', 'opening Weight also opened Macros')
    ev("[...document.querySelectorAll('.mh-pills-toolbar button')].filter(b=>b.offsetParent!==null && /Open all/.test(b.textContent))[0].click()"); page.wait_for_timeout(500)
    for i in ids:
        if h(i) < before[i] - 5: f.add('BUG', f'Open all did not restore {i}: {before[i]} -> {h(i)}')
    if errs and any('ServiceWorker' not in e for e in errs): f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
