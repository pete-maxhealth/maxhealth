"""Persona 57: Settings > Import > Missing Data lists finished days lacking steps / heart rate / sleep, each opening Manual Entry on that day."""
import sys, re, os, json, urllib.request; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
def iso(n): return (date.today() - timedelta(days=n)).isoformat()
with fresh_server() as root, sync_playwright() as pw:
    tdir = os.path.join(root, 'data', 'tables'); os.makedirs(tdir, exist_ok=True)
    rows = ['date,steps,hr_resting,hr_avg,sleep_duration']
    rows.append(f'{iso(9)},8000,55,70,420')            # complete
    rows.append(f'{iso(8)},8000,55,70,420')            # complete
    rows.append(f'{iso(7)},9000,56,71,400')           # complete
    # iso(6) has no row at all
    rows.append(f'{iso(5)},,,,')                       # empty row
    rows.append(f'{iso(4)},7000,,,380')               # no heart rate
    rows.append(f'{iso(3)},7000,57,72,')              # no sleep
    rows.append(f'{iso(2)},7000,57,72,390')           # complete
    rows.append(f'{iso(1)},,57,72,390')               # no steps
    rows.append(f'{date.today().isoformat()},100,,,')   # today: must be ignored
    open(os.path.join(tdir, 'combined.csv'), 'w').write('\n'.join(rows) + '\n')
    j = json.loads(urllib.request.urlopen('http://localhost:5757/data-gaps?days=14').read())
    got = {g['date']: g['missing'] for g in j['gaps']}
    exp = {iso(6): ['steps', 'heart rate', 'sleep'], iso(5): ['steps', 'heart rate', 'sleep'], iso(4): ['heart rate'], iso(3): ['sleep'], iso(1): ['steps']}
    if got != exp: f.add('BUG', f'gaps wrong: got {got} expected {exp}')
    if date.today().isoformat() in got: f.add('BUG', 'today must not be listed as a gap')
    if iso(10) in got or iso(12) in got: f.add('BUG', 'days before the first recorded day must not be gaps')
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("switchTabById('settings')"); page.evaluate("switchSubTab('settings','import')"); page.wait_for_timeout(1500)
    n = page.evaluate("document.querySelectorAll('#mhGapsList > div').length")
    txt = page.evaluate("document.getElementById('mhGapsList').textContent")[:200]
    if n != 5: f.add('BUG', f'expected 5 gap rows, saw {n}: {txt}')
    # card has hide + reorder like every other card
    if not page.evaluate("!!document.getElementById('title-imp-gaps')"): f.add('BUG', 'no card title')
    if not page.evaluate("(document.getElementById('title-imp-gaps').parentElement.textContent||'').includes('Missing Data')"): f.add('BUG', 'card title missing')
    page.evaluate("document.querySelectorAll('#mhGapsList > div')[0].click()"); page.wait_for_timeout(1300)
    got_date = page.evaluate("document.getElementById('manualEntryDate').value")
    if got_date != iso(1): f.add('BUG', f'first row should open {iso(1)}, got {got_date}')
    # card exposes the generic hide/reorder controls
    ctrl = page.evaluate("(() => { const c = document.getElementById('title-imp-gaps').closest('.card-unit'); return c ? c.querySelectorAll('[onclick*=\"Generic\"], .mh-reorder, [title=\"Hide\"]').length : -1; })()")
    print('ctrl', ctrl)
    if ctrl <= 0: f.add('BUG', 'no hide / reorder controls injected on the Missing Data card')
    # cloud mode (no local server): no link to a form that cannot save, and the card explains itself
    page.evaluate("_serverOnline = false; updateTrendsDayLabel(); mhLoadDataGaps()"); page.wait_for_timeout(300)
    if page.evaluate("getComputedStyle(document.getElementById('trendsDayEdit')).display !== 'none'"): f.add('BUG', 'edit-this-day link shown without a local server')
    if 'cloud mode' not in page.evaluate("document.getElementById('mhGapsList').textContent"): f.add('BUG', 'Missing Data card does not explain itself in cloud mode')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
