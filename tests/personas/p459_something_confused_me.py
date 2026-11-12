"""Persona 459: "Something confused me" (Pete, 12 Nov 2026). Reachable from the bottom of Today and from Settings > About and by search; the sheet names the screen and app version, lets the person tick what it was
and type a line; Copy/Share text holds only that (nothing from the log); nothing is sent by the app; Close and tapping outside both close it; a second open starts clean. Demo persona, invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block', permissions=['clipboard-read', 'clipboard-write']); page = ctx.new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    sent = []; page.on('request', lambda r: sent.append(r.url) if r.method == 'POST' and 'localhost:5757' not in r.url else None)
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    names = [n for n in ev("(loadLibrary()||[]).slice(0,40).map(x=>x.name)") if n and len(n) > 3][:15]
    if len(names) < 5: f.add('BUG', '0: the demo has too few foods to check for leaks')
    ev("switchTab('today'); switchSubTab('today','dash')"); page.wait_for_timeout(600)
    link = page.locator('#dashSection-guides a', has_text='Something confused me')
    if link.count() < 1: f.add('BUG', '1: no "Something confused me" link at the bottom of Today')
    else:
        link.first.scroll_into_view_if_needed(); link.first.click(); page.wait_for_timeout(300)
    if not ev("!!document.getElementById('mhConfusedModal')"): f.add('BUG', '2: the sheet did not open')
    scr = ev("document.getElementById('mhConfusedScreen')?.textContent || ''")
    if scr != 'Today › Dashboard': f.add('BUG', f'3: the screen is not named: {scr!r}')
    ev("document.querySelector('#mhConfusedChips button').click()"); ev("document.getElementById('mhConfusedWords').value='the carb bar made no sense to me'")
    ev("document.getElementById('mhConfusedCopy').click()"); page.wait_for_timeout(300)
    txt = ev("navigator.clipboard.readText()")
    for need in ('v3.10.', scr, 'I did not understand', 'the carb bar made no sense'):
        if need not in txt: f.add('BUG', f'4: copied text lacks {need!r}: {txt!r}')
    for leak in names + ['kcal', 'doris', 'Doris']:
        if leak in txt: f.add('BUG', f'5: copied text carries log or persona data: {leak}')
    ev("document.querySelector('#mhConfusedChips button').click()")   # tick off again
    ev("document.getElementById('mhConfusedShare').click()"); page.wait_for_timeout(300)
    txt2 = ev("navigator.clipboard.readText()")
    if 'What it was' in txt2: f.add('BUG', '6: an un-ticked choice is still in the text')
    # v3.10.1377: lands on the existing feedback form (GitHub issue), prefilled
    ev("document.querySelector('#mhConfusedChips button').click(); window.__op=null; window.open=function(u){window.__op=u; return null}")
    ev("document.getElementById('mhConfusedForm').click()")
    u = ev("window.__op || ''")
    if '/issues' not in u or 'labels=feedback' not in u or 'Confused' not in u or 'I%20did%20not%20understand' not in u: f.add('BUG', f'6b: feedback form link not prefilled: {u!r}')
    for leak in names + ['kcal']:
        if leak in u: f.add('BUG', f'6c: feedback link carries log data: {leak}')
    ev("document.querySelector('#mhConfusedChips button').click()")
    ev("document.getElementById('mhConfusedClose').click()")
    if ev("!!document.getElementById('mhConfusedModal')"): f.add('BUG', '7: Close did not close it')
    ev("mhConfusedOpen()"); ev("document.getElementById('mhConfusedModal').click()")
    if ev("!!document.getElementById('mhConfusedModal')"): f.add('BUG', '8: tapping outside did not close it')
    ev("mhConfusedOpen()")
    if ev("document.getElementById('mhConfusedWords').value") != '' or ev("document.getElementById('mhConfusedChip').dataset.v||''") != '': f.add('BUG', '9: second open is not clean')
    ev("document.getElementById('mhConfusedModal').remove()")
    # Settings > About button and search
    ev("switchTabById('manage')"); page.wait_for_timeout(500)
    b = page.get_by_text('SOMETHING CONFUSED ME', exact=False)
    if b.count() < 1: f.add('BUG', '10: no button under Settings > About')
    else:
        ev("document.querySelectorAll('[onclick=\"mhConfusedOpen()\"]').forEach(e=>{ if(e.tagName==='BUTTON') e.click() })"); page.wait_for_timeout(300)
        if not ev("!!document.getElementById('mhConfusedModal')"): f.add('BUG', '11: the Settings button did not open the sheet')
        ev("document.getElementById('mhConfusedModal')?.remove()")
    if not ev("SITE_SEARCH_SETTINGS.some(x=>/confused/i.test(x.keywords))"): f.add('BUG', '12: search does not find it by "confused"')
    if sent: f.add('BUG', f'13: the app sent something by itself: {sent}')
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
