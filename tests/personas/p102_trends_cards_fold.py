"""Persona 102: Close all on Trends really folds the metric cards (Weight, Heart rate ...) to one-line bars; Open all opens them; tapping a bar opens just that card;
it respects the chosen group; the fold is remembered over a reload; Default clears it; hidden/empty cards are left alone and not counted."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(2000)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    ev = page.evaluate
    def show(): ev("['mcWeight','mcHR','mcCal'].forEach(i=>{ const e=document.getElementById(i); e.style.display=''; }); mhTcApply();"); page.wait_for_timeout(200)
    ev("switchTab('insights'); switchSubTab('insights','trends')"); page.wait_for_timeout(800); show()
    closed = lambda: ev("['mcWeight','mcHR','mcCal','mcSteps'].map(i=>document.getElementById(i).classList.contains('mh-dc-closed'))")
    btn = lambda n: f"document.querySelector('#view-trends .mh-pills-toolbar button:nth-of-type({n})')"
    ev(f"mhSectionsAll({btn(3)}, false)"); page.wait_for_timeout(300)
    if closed() != [True, True, True, False]: f.add('BUG', f'Close all did not fold shown cards only: {closed()}')
    bar = ev("document.querySelector('#mcWeight > .mh-dc-bar').textContent")
    if 'Weight' not in bar: f.add('BUG', f'bar text {bar}')
    ev("document.querySelector('#mcWeight > .mh-dc-bar').click()"); page.wait_for_timeout(200)
    if closed()[:3] != [False, True, True]: f.add('BUG', f'tapping a bar should open only that card: {closed()}')
    if ev("!!document.getElementById('metricDrillOverlay') && getComputedStyle(document.getElementById('metricDrillOverlay')).display") not in (False, 'none'): f.add('BUG', 'tapping the bar opened the chart lightbox')
    page.reload(); page.wait_for_timeout(2000); ev("switchTab('insights'); switchSubTab('insights','trends')"); page.wait_for_timeout(800); show()
    if closed()[:3] != [False, True, True]: f.add('BUG', f'fold not remembered: {closed()}')
    ev(f"mhSectionsAll({btn(2)}, true)"); page.wait_for_timeout(300)
    if closed() != [False, False, False, False]: f.add('BUG', f'Open all left cards folded: {closed()}')
    # group scope: only Body cards fold
    ev("mhTrendsGroupSet('body')"); ev(f"mhSectionsAll({btn(3)}, false)"); page.wait_for_timeout(300)
    c = closed()
    if c[0] is not True or c[1] is not False: f.add('BUG', f'group scope wrong {c}')
    ev("mhTrendsGroupSet('all')")
    keys = ev("mhLayoutKeys(document.getElementById('view-trends'))")
    if 'mh_collapse_tc_mcWeight' not in keys: f.add('BUG', f'Default would not clear card folds {keys}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
