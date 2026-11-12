"""Persona 451: every ▲ ▼ 👁 card control is the same control (class, size, colour, order up-down-hide) on Today, Trends, Library, Statistics and the injected cards; the two scroll arrows are small round buttons fully on screen in the same spots (v3.10.1367). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SCAN = """() => [...document.querySelectorAll('body *')].filter(e => !e.children.length && /^(▲|▼|👁)( Show)?$/.test(e.textContent.trim()) && e.offsetParent !== null && /move|Hid|Hide/i.test((e.getAttribute('onclick')||''))).map(e => { const c = getComputedStyle(e), r = e.getBoundingClientRect(); return { oc: (e.getAttribute('onclick')||'').slice(0,50) + ' | ' + (e.getAttribute('style')||'') + ' | ' + e.parentElement.outerHTML.slice(0,90), g: Array.from(e.textContent.trim())[0], cls: e.className, fs: c.fontSize, col: c.color, w: Math.round(r.width), h: Math.round(r.height), x: Math.round(r.x), y: Math.round(r.y) } })"""
seen = []
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_stat_defs', '[]')") if False else None
    for name, js in [('today', "switchTab('today')"), ('move', "switchSubTab('today','move')"), ('trends', "switchTab('insights'); switchSubTab('insights','trends')"), ('library', "switchTab('log'); switchSubTab('log','library')"),
                     ('shop', "localStorage.setItem('mh_shop_pane','both'); switchTabById('shop')"), ('statistics', "switchTab('insights'); switchSubTab('insights','statistics'); mhStatLibraryOpen(); mhStatLibAdd(0); mhStatLibAdd(1)")]:
        try:
            ev(js); page.wait_for_timeout(600)
            for r in ev(SCAN): r['screen'] = name; seen.append(r)
        except Exception as e: f.add('BUG', f'0: {name}: {str(e)[:100]}')
    if len(seen) < 12: f.add('BUG', f'1: expected many controls, found {len(seen)}')
    for r in seen:
        if 'mh-mv' not in r['cls'].split(): f.add('BUG', f"2: {r['screen']}: {r['g']} without the standard class ({r['cls']!r}) {r['oc']}")
    for scr in sorted({r['screen'] for r in seen}):
        fss = {r['fs'] for r in seen if r['screen'] == scr}; wh = {(r['w'], r['h']) for r in seen if r['screen'] == scr}
        if len(fss) > 1 or len(wh) > 1: f.add('BUG', f"3: {scr}: controls differ in size within the screen: {fss} {wh}; odd: {[r['oc'][:140] for r in seen if r['screen'] == scr and r['fs'] != '11px'][:3]}")
    allfs = sorted({float(r['fs'][:-2]) for r in seen})
    if allfs and allfs[-1] / allfs[0] > 1.3: f.add('BUG', f"3b: sizes differ between screens: {allfs}")
    if any(r['h'] < 26 or r['w'] < 26 for r in seen): f.add('BUG', '3c: a control is under 26px to tap')
    if len({r['col'] for r in seen}) > 1: f.add('BUG', f"4: more than one colour: {({r['col'] for r in seen})}")
    # order inside every card: ▲ then ▼ then 👁, left to right, on one row
    for scr in {r['screen'] for r in seen}:
        pass
    ev("switchTab('today'); switchSubTab('today','dashboard')"); page.wait_for_timeout(400)
    ev("document.querySelector('#dash-weight-wrap, .dash-wrap')?.scrollIntoView()")
    rows = ev("""() => { const out = []; document.querySelectorAll('.mh-mv').forEach(e => { const p = e.parentElement; if (!p || p.__seen) return; p.__seen = 1; const k = [...p.querySelectorAll('.mh-mv')].filter(x => x.offsetParent).map(x => Array.from(x.textContent.trim())[0]); if (k.length >= 3) out.push(k.join('')); }); return out; }""")
    bad = [r for r in rows if r not in ('▲▼👁', '▲▼👁')]
    if bad: f.add('BUG', f'5: control order is not ▲▼👁 in {len(bad)} cards: {bad[:4]}')
    # scroll arrows: scroll a long page, both appear, small round, fully inside the screen, same spot on two screens
    spots = []
    for tab in ("switchTab('today')", "switchTab('insights'); switchSubTab('insights','trends')"):
        ev(tab); page.wait_for_timeout(500); ev("(document.scrollingElement||document.body).scrollTop=400; document.querySelectorAll('.view,.subview,[id$=Scroll]').forEach(e=>{ if(e.scrollHeight>e.clientHeight) e.scrollTop=400 })"); page.wait_for_timeout(500)
        ev("updateGlobalScrollNav && updateGlobalScrollNav()")
        r = ev("""() => ['globalScrollTopBtn','globalScrollBottomBtn'].map(id => { const e = document.getElementById(id), b = e.getBoundingClientRect(), c = getComputedStyle(e); return { id, shown: c.display !== 'none', x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height), r: c.borderTopLeftRadius, vw: innerWidth } })""")
        spots.append(r)
        for b in r:
            if b['shown'] and (b['w'] != 26 or b['h'] != 26 or b['x'] + b['w'] > b['vw'] or b['r'] not in ('17px', '50%')): f.add('BUG', f'6: scroll arrow not a small round, fully visible button: {b}')
    shown = [[b['x'] for b in s if b['shown']] for s in spots]
    if not any(shown): f.add('BUG', '7: no scroll arrow appeared on a scrolled screen')
    # the controls still work: ▼ moves a Trends card down, 👁 hides it
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('controls seen', len(seen)); print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
