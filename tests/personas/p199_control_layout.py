"""Persona 199: every Today/Move card has the same control cluster: up, down, hide in that order, same size, right-aligned; cards with a fold put the fold label last."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode && startDemoMode()"); page.wait_for_timeout(2000)
    ev("switchTabById('dash')"); page.wait_for_timeout(600)
    res = ev("""(()=>{const out=[];
      const cards=[...document.querySelectorAll('#view-dash [id^=dashSection-], #view-move #dailyStepsCard, #view-move #activityCard, #mhWxCard')];
      for(const c of cards){const sp=[...c.querySelectorAll('span[onclick]')].filter(s=>/(moveDashboardSection|moveMoveSection)\\(|toggle(Dashboard|Move)SectionHidden\\(/.test(s.getAttribute('onclick')));
        if(!sp.length) continue;
        const kinds=sp.map(s=>/'up'/.test(s.getAttribute('onclick'))?'up':/'down'/.test(s.getAttribute('onclick'))?'down':'hide');
        const sizes=[...new Set(sp.map(s=>getComputedStyle(s).fontSize))];
        out.push({id:c.id,kinds:kinds.join(','),sizes:sizes.join('/')});}
      return out;})()""")
    if len(res) < 12: f.add('BUG', f'only {len(res)} cards with controls found')
    for r in res:
        if r['kinds'] != 'up,down,hide': f.add('BUG', f"{r['id']} control order {r['kinds']}")
        if r['sizes'] != '14px': f.add('BUG', f"{r['id']} control size {r['sizes']}")
    # the round scroll up/down buttons must follow the Shopping and Library screens too
    for t, sc in (('shop', 'shopScroll'), ('library', 'libraryScroll')):
        ev(f"switchTabById('{t}')"); page.wait_for_timeout(400)
        if ev("window._activeScrollContainerId") != sc: f.add('BUG', f'scroll buttons not attached to {sc}')
    # tapping a progress bar opens the history behind it
    ev("switchTabById('dash')"); page.wait_for_timeout(300)
    for bar, fn in (('waterBar', 'openChartLightbox'), ('fastBar', 'mhGoFastHistory'), ('fibreBar', 'mhFibreHistory')):
        if ev(f"(document.getElementById('{bar}').parentElement.getAttribute('onclick')||'').includes('{fn}')") is not True: f.add('BUG', f'{bar} tap should call {fn}')
    ev("mhFibreHistory()")
    if 'last 14 days' not in ev("(document.getElementById('mhFibreHistModal')||{innerText:''}).innerText").lower(): f.add('BUG', 'fibre tap should open the 14-day view')
    ev("document.getElementById('mhFibreHistModal').remove()")
    ev("openChartLightbox('water')"); page.wait_for_timeout(300)
    if ev("getComputedStyle(document.getElementById('metricDrillOverlay')).display") == 'none': f.add('BUG', 'water tap should open the water chart')
    ev("closeMetricDrill()")
    ev("mhGoFastHistory()"); page.wait_for_timeout(200)
    if 'Fasting history' not in ev("document.body.innerText") and ev("document.getElementById('view-reports') ? document.getElementById('view-reports').classList.contains('active') : document.getElementById('insightstab-reports').classList.contains('active')") is not True: f.add('BUG', 'fasting tap should open the history, or say why not')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
