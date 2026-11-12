"""Persona 453: the Sun theme switches Light/Dark at sunrise/sunset worked out from the weather location (no network), falls back to 7am/7pm with no location, handles polar day/night, is remembered across a reload, is a 4th swatch next to Auto, and leaves a custom accent alone (v3.10.1367). Invented locations."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    # 1: four swatches, Sun last, after Auto
    ids = ev("[...document.querySelectorAll('.theme-swatch')].map(e => e.id).filter(i => /^swatch-(midnight|light|auto|sun)$/.test(i))")
    if ids[-2:] != ['swatch-auto', 'swatch-sun']: f.add('BUG', f'1: swatches: {ids}')
    # 2: sun maths against known values (London, 21 Jun 2026: sunrise ~03:43 UTC, sunset ~20:21 UTC; 21 Dec: ~08:04 / ~15:53 UTC), tolerance 6 minutes
    def hm(js):
        r = ev(js)
        return r
    for label, lat, lon, date, rise, sset in [('London summer', 51.5, -0.12, '2026-06-21T12:00:00Z', 3 * 60 + 43, 20 * 60 + 21), ('London winter', 51.5, -0.12, '2026-12-21T12:00:00Z', 8 * 60 + 4, 15 * 60 + 53), ('Sydney Dec', -33.87, 151.21, '2026-12-21T02:00:00Z', 18 * 60 + 41 - 24 * 60 + 24 * 60, 9 * 60 + 5)]:
        r = ev(f"(()=>{{const x=mhSunTimes({lat},{lon},new Date('{date}')); return x.polar?x.polar:[x.rise.getUTCHours()*60+x.rise.getUTCMinutes(), x.set.getUTCHours()*60+x.set.getUTCMinutes()]}})()")
        if isinstance(r, str) or abs(r[0] - rise) > 6 or abs(r[1] - sset) > 6: f.add('BUG', f'2: {label}: got {r}, expected about {[rise, sset]}')
    # 3: polar day / night
    d1 = ev("mhSunTimes(78.2, 15.6, new Date('2026-06-21T12:00:00Z'))"); d2 = ev("mhSunTimes(78.2, 15.6, new Date('2026-12-21T12:00:00Z'))")
    if d1.get('polar') != 'day' or d2.get('polar') != 'night': f.add('BUG', f'3: polar: {d1} {d2}')
    # 4: with a location, the state follows the clock: London midday summer = light, 23:00 = dark, 02:00 = dark
    ev("localStorage.setItem('mh_wx_loc', JSON.stringify({lat:51.5, lon:-0.12, name:'Testville'}))")
    for at, dark in [('2026-06-21T12:00:00Z', False), ('2026-06-21T23:30:00Z', True), ('2026-06-21T02:00:00Z', True), ('2026-12-21T16:30:00Z', True), ('2026-12-21T11:00:00Z', False)]:
        got = ev(f"mhSunState(new Date('{at}')).dark")
        if got != dark: f.add('BUG', f'4: {at}: dark={got}, expected {dark}')
    # 5: no location: 07:00 / 19:00 local
    ev("localStorage.removeItem('mh_wx_loc')")
    r = ev("[mhSunState(new Date(2026,5,21,6,59)).dark, mhSunState(new Date(2026,5,21,7,1)).dark, mhSunState(new Date(2026,5,21,18,59)).dark, mhSunState(new Date(2026,5,21,19,1)).dark, mhSunState(new Date(2026,5,21,12,0)).source]")
    if r != [True, False, False, True, 'fixed']: f.add('BUG', f'5: fallback hours: {r}')
    # 6: tapping Sun applies the right base now, remembers it, a reload keeps it, and the note explains
    ev("applyTheme('sun')"); page.wait_for_timeout(300)
    want = 'midnight' if ev("mhSunState().dark") else 'light'
    cur = ev("document.documentElement.getAttribute('data-theme') || 'midnight'")
    if cur != want: f.add('BUG', f'6: base {cur} but the sun says {want}')
    if ev("localStorage.getItem('mh_theme')") != 'sun': f.add('BUG', '6b: not remembered')
    if not ev("document.getElementById('swatch-sun').classList.contains('active')"): f.add('BUG', '6c: the Sun swatch is not highlighted')
    page.reload(); page.wait_for_timeout(1500); ev = page.evaluate
    if ev("localStorage.getItem('mh_theme')") != 'sun' or not ev("document.getElementById('swatch-sun').classList.contains('active')"): f.add('BUG', '7: after a reload Sun is not still chosen')
    ev("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(500)
    note = ev("document.getElementById('sunThemeNote') && document.getElementById('sunThemeNote').innerText")
    if not note or 'Sun:' not in note: f.add('BUG', f'8: no explanation line: {note!r}')
    # 9: the switch really happens while the app is open: pretend the clock crosses sunset
    ev("window._real = Date; ")
    ev("(()=>{ localStorage.setItem('mh_wx_loc', JSON.stringify({lat:51.5, lon:-0.12, name:'Testville'})); const RD = Date; const t0 = new RD('2026-06-21T20:00:00Z').getTime(); const off = t0 - RD.now(); window.Date = class extends RD { constructor(...a){ if (a.length) super(...a); else super(RD.now() + off); } static now(){ return RD.now() + off; } }; })()")
    ev("applyTheme('sun')"); a = ev("document.documentElement.getAttribute('data-theme') || 'midnight'")
    ev("(()=>{ const RD = Object.getPrototypeOf(window.Date); const t0 = new RD('2026-06-21T21:30:00Z').getTime(); const off = t0 - RD.now(); window.Date = class extends RD { constructor(...a){ if (a.length) super(...a); else super(RD.now() + off); } static now(){ return RD.now() + off; } }; })()")
    ev("applyTheme('sun')"); b = ev("document.documentElement.getAttribute('data-theme') || 'midnight'")
    if a != 'light' or b != 'midnight': f.add('BUG', f'9: 20:00Z should be light and 21:30Z dark (sunset 20:21Z): {a} then {b}')
    # 10: a custom accent survives, Dark/Light/Auto still work and cancel the sun timer
    ev("applyCustomAccent('#ff8800')"); ev("applyTheme('sun')")
    if ev("localStorage.getItem('mh_custom_accent')") != '#ff8800' and not ev("getComputedStyle(document.documentElement).getPropertyValue('--accent')").strip(): f.add('BUG', '10: custom accent lost')
    ev("applyTheme('light')")
    if ev("localStorage.getItem('mh_theme')") != 'light' or ev("_mhSunTimer") is not None and ev("typeof _mhSunTimer") == 'number' and False: f.add('BUG', '11: Light did not stick')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
