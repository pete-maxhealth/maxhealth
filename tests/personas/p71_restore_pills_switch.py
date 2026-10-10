"""Persona 71: one Settings switch hides or shows every "Hidden:" restore strip; hidden cards stay hidden; default is shown; the choice survives a reload."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); localStorage.setItem('mh_trend_cards_hidden', JSON.stringify(['mcWeight','mcHR'])); renderTrends(); applyTrendCardsOrderAndVisibility();")
    page.wait_for_timeout(300)
    vis = lambda sel: page.evaluate("(s) => { const e = document.querySelector(s); return !!e && getComputedStyle(e).display !== 'none' && e.innerText.includes('Hidden'); }", sel)
    if not vis('#trendCardsRestoreStrip'): f.add('BUG', 'default should show the Hidden strip')
    if not page.evaluate("document.getElementById('settingShowRestorePills').checked"): f.add('BUG', 'switch should default to on')
    page.evaluate("mhSetRestorePills(false)")
    if vis('#trendCardsRestoreStrip'): f.add('BUG', 'switch off should hide the Trends strip')
    if page.evaluate("getComputedStyle(document.getElementById('mcWeight')).display") != 'none': f.add('BUG', 'hiding the strip must not un-hide the card')
    page.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=\"genericRestoreStrip-x\">Hidden: a</div><div id=\"dashboardRestoreStrip\">Hidden: b</div><div class=\"mh-restore-strip\">Hidden: c</div>')")
    for sel in ['#genericRestoreStrip-x', '#dashboardRestoreStrip', '.mh-restore-strip']:
        if page.evaluate("(s) => getComputedStyle(document.querySelector(s)).display", sel) != 'none': f.add('BUG', f'{sel} should be hidden by the switch')
    page.reload(); page.wait_for_timeout(1500)
    if page.evaluate("document.getElementById('settingShowRestorePills').checked"): f.add('BUG', 'choice did not survive reload')
    if not page.evaluate("document.body.classList.contains('mh-no-restore-pills')"): f.add('BUG', 'body class missing after reload')
    page.evaluate("mhSetRestorePills(true); applyTrendCardsOrderAndVisibility();")
    if not vis('#trendCardsRestoreStrip'): f.add('BUG', 'switching on should bring the strip back')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
