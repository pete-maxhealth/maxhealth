"""Persona 516 (20 Nov 2026): desktop-size walk of every sub-tab and the big overlays, mouse only (no touch), 1280x800.
Covers: each Today / Log / Insights / Settings sub-tab clicked with the real mouse, nothing wider than the page column and no sideways scroll;
the exercise picker, the phone-to-phone / code-transfer overlay, the Statistics builder (with the saved-query filter) and the routines list stay inside the window;
the site search takes typing and Enter; Tab moves focus. Invented data, demo persona. No page errors."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SUBS = [('today', ['dash', 'move', 'supplements']), ('log', ['log', 'hist', 'library', 'shop']), ('insights', ['trends', 'stats', 'reports']), ('settings', ['manage', 'customise', 'import'])]
WIDE = """(sel)=>{const col=document.body.getBoundingClientRect(), bad=[];document.querySelectorAll(sel).forEach(e=>{const r=e.getBoundingClientRect(); if(r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&(r.right>col.right+2||r.left<col.left-2)&&!e.closest('[style*="overflow-x"],.mh-chips,.mh-pick-chips,table,svg,pre')) bad.push((e.id||e.className||e.tagName).toString().slice(0,40)+':'+Math.round(r.left)+'-'+Math.round(r.right))});return bad.slice(0,5)}"""
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 1280, 'height': 800}, has_touch=False, is_mobile=False, service_workers='block'); pg = ctx.new_page(); ev = pg.evaluate
    pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: d.dismiss()); pg.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort()) if False else None
    pg.goto('http://localhost:5757/?demo=alex'); pg.wait_for_timeout(3500); ev("var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'")
    for tab, subs in SUBS:
        pg.click(f'#maintab-{tab}'); pg.wait_for_timeout(500)
        for sub in subs:
            try: pg.click(f'#{tab}tab-{sub}', timeout=3000)
            except Exception: f.add('BUG', f'1: {tab}/{sub}: tab not clickable with the mouse'); continue
            pg.wait_for_timeout(700)
            if ev("document.documentElement.scrollWidth - document.documentElement.clientWidth") > 1: f.add('BUG', f'2: {tab}/{sub}: page scrolls sideways')
            bad = ev(f"({WIDE})('.subview.active *')")
            if bad: f.add('BUG', f'3: {tab}/{sub}: wider than the column: {bad}')
            if len(ev("document.querySelector('.subview.active')?.innerText||document.body.innerText")) < 40: f.add('BUG', f'4: {tab}/{sub}: looks empty')
    # exercise picker
    pg.click('#maintab-today'); pg.click('#todaytab-move'); pg.wait_for_timeout(700); pg.click('text=Add another exercise'); pg.wait_for_timeout(600)
    r = ev("(()=>{const p=document.querySelector('.mh-pick').getBoundingClientRect();return [p.left,p.right,p.top,p.bottom,innerWidth,innerHeight]})()")
    (r[0] >= -1 and r[1] <= r[4] + 1 and r[2] >= -1 and r[3] <= r[5] + 1) or f.add('BUG', f'5: exercise picker outside the window {r}')
    pg.click('#mhPickCats >> text=Water'); pg.wait_for_timeout(300); pg.keyboard.press('Escape'); ev("mhClosePicker()")
    # routines list
    ev("showRoutineList()"); pg.wait_for_timeout(500)
    bad = ev(f"({WIDE})('#routineListContainer *')"); bad and f.add('BUG', f'6: routines list wider than the column: {bad}')
    # transfer overlay
    pg.click('#maintab-settings'); pg.click('#settingstab-import'); pg.wait_for_timeout(500); ev("mhxOpen()"); pg.wait_for_timeout(600)
    r = ev("(()=>{const o=document.getElementById('mhXferOverlay'); if(!o) return null; const b=[...o.querySelectorAll('button')].filter(x=>x.getBoundingClientRect().width>0).map(x=>x.getBoundingClientRect()); return [Math.min(...b.map(x=>x.left)), Math.max(...b.map(x=>x.right)), innerWidth]})()")
    (r and r[0] >= -1 and r[1] <= r[2] + 1) or f.add('BUG', f'7: transfer overlay buttons outside the window {r}')
    ev("mhxClose && mhxClose()") if ev("typeof mhxClose==='function'") else ev("document.getElementById('mhXferOverlay')?.remove()")
    # statistics builder with the saved-query filter
    pg.click('#maintab-insights'); pg.click('#insightstab-stats'); pg.wait_for_timeout(500); pg.click('#view-stats button.run-btn >> nth=0'); pg.wait_for_timeout(600)
    ev("mhStatSet('subject','days')"); pg.wait_for_timeout(300)
    'ONLY DAYS WHEN' in pg.inner_text('#statsBuilder') or f.add('BUG', '8: the saved-query filter is missing from the builder at desktop size')
    bad = ev(f"({WIDE})('#statsBuilder *')"); bad and f.add('BUG', f'9: Statistics builder wider than the column: {bad}')
    # site search: click, type, Enter; Tab moves focus
    pg.click('[onclick*="openSiteSearch"], #siteSearchBtn, .search-btn') if ev("!!document.querySelector('[onclick*=\"openSiteSearch\"], #siteSearchBtn, .search-btn')") else f.add('BUG', '10: no site search button found')
    pg.wait_for_timeout(400); pg.keyboard.type('steps', delay=60); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    ev("typeof closeSiteSearch==='function' && closeSiteSearch()")
    pg.keyboard.press('Tab'); ev("document.activeElement && document.activeElement !== document.body") or f.add('BUG', '11: Tab did not move focus to anything')
    errs and f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f))
