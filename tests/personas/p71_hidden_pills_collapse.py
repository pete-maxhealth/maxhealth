"""Persona 71: each screen gets one "Filters & hidden" button that shows or hides every chip row and Hidden: strip (closed by default, one global
state, persisted), plus Open all / Close all for the collapsible cards on that screen."""
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
    page.evaluate("localStorage.setItem('mh_onboarded','1'); localStorage.setItem('mh_trend_cards_hidden', JSON.stringify(['mcWeight','mcHR','mcSteps'])); switchTab('insights'); renderTrends(); applyTrendCardsOrderAndVisibility();")
    page.wait_for_timeout(500)
    disp = lambda sel: page.evaluate("(s) => { const e = document.querySelector(s); return e ? getComputedStyle(e).display : 'missing'; }", sel)
    tb = page.evaluate("document.querySelector('#view-trends .mh-pills-toolbar')?.innerText || ''")
    if 'Filters & hidden (3)' not in tb.replace('\n', ' '): f.add('BUG', f'Trends toolbar should show the hidden count, got {tb!r}')
    if disp('#trendCardsRestoreStrip') != 'none': f.add('BUG', 'Hidden strip should be collapsed by default')
    if disp('#mhTrendsGroupBar') != 'none': f.add('BUG', 'chip row should be collapsed by default')
    page.evaluate("document.querySelector('#view-trends .mh-pills-toolbar .main').click()"); page.wait_for_timeout(300)
    if disp('#trendCardsRestoreStrip') == 'none' or disp('#mhTrendsGroupBar') == 'none': f.add('BUG', 'the one button should reveal the chip row and the Hidden strip')
    page.evaluate("switchTab('settings'); switchSubTab('settings','manage'); mhTopicApply('manage');"); page.wait_for_timeout(500)
    if disp('#mhTopicBar-manage') == 'none': f.add('BUG', 'open state should be global (Settings chips visible too)')
    if not page.evaluate("!!document.querySelector('#view-manage .mh-pills-toolbar')"): f.add('BUG', 'Settings Manage has no toolbar')
    # Open all / Close all
    page.evaluate(r"""() => { window.sects = () => [...new Set([...document.querySelectorAll('#view-manage [onclick*="toggleSection("]')].map(h => (/toggleSection\(\s*'[^']+'\s*,\s*'([^']+)'/.exec(h.getAttribute('onclick')) || [])[1]).filter(Boolean))].map(id => document.getElementById(id)).filter(Boolean); }""")
    page.evaluate("[...document.querySelectorAll('#view-manage .mh-pills-toolbar button')].find(b => b.innerText === 'Close all').click()"); page.wait_for_timeout(200)
    closed = page.evaluate("sects().filter(e => e.style.display === 'none').length")
    total = page.evaluate("sects().length")
    if total < 3 or closed != total: f.add('BUG', f'Close all should close every section on the screen ({closed}/{total})')
    page.evaluate("[...document.querySelectorAll('#view-manage .mh-pills-toolbar button')].find(b => b.innerText === 'Open all').click()"); page.wait_for_timeout(200)
    opened = page.evaluate("sects().filter(e => e.style.display !== 'none').length")
    if opened != total: f.add('BUG', f'Open all should open every section on the screen ({opened}/{total})')
    page.reload(); page.wait_for_timeout(1500)
    if not page.evaluate("document.body.classList.contains('mh-pills-open')"): f.add('BUG', 'open state did not persist')
    page.evaluate("mhTogglePills()")
    page.evaluate("switchTab('insights'); applyTrendCardsOrderAndVisibility();"); page.wait_for_timeout(400)
    if disp('#trendCardsRestoreStrip') != 'none': f.add('BUG', 'toggling off should collapse again')
    # restoring a card still works from the opened strip
    page.evaluate("mhTogglePills(); document.querySelector('#trendCardsRestoreStrip button').click()"); page.wait_for_timeout(300)
    if len(page.evaluate("JSON.parse(localStorage.getItem('mh_trend_cards_hidden')||'[]')")) != 2: f.add('BUG', 'restore from the opened strip no longer works')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
