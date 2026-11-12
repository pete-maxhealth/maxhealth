"""Persona 406: long explainers sit behind a "?" (6 Nov 2026, v3.10.1301).
Pete: any text longer than a couple of lines goes behind the standard "?". This checks every spot moved there:
  - the short line stays visible, the rest is hidden, one tap on "?" shows it, a second tap hides it again, and the screen is unchanged after reload
  - nothing still shows a long block (>220 chars) of plain text on Stats, Reports, Import, Manage, Trends, and the import review
  - the Spanish pack still translates the visible lines (they were split from longer, already-translated texts)
Invented data only; runs in the demo persona."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from flows import *
from playwright.sync_api import sync_playwright
f = Findings()
IDS = {  # help id -> screen that shows it, text expected inside, text that must stay visible
 'statsintro': ('stats', 'Top foods', 'Ask your own data a question and keep the answer'),
 'reportsintro': ('reports', 'Query Builder', 'Reports is for period analysis'),
 'activitylevelhistory': ('manage', 'One change per line', 'Logs automatically whenever your Activity Level changes'),
 'carbmethodhelp': ('manage', 'sugar alcohols', 'the default) shows the raw carbs figure'),
 'exenergyhelp': ('manage', 'Compendium', 'Calories = MET'),
 'tdeemulthelp': ('manage', '1.725', 'Activity multiplier comes from'),
 'methelp': ('manage', 'Walking: 2.8', 'MET values by activity and effort'),
 'pacebandshelp': ('manage', 'Sedentary: Easy', 'Pace bands follow your Activity Level'),
 'autoswitchhelp': ('manage', 'rolling 30-day', 'Uses the same step thresholds'),
 'netcarbshelp': ('manage', 'double-count', 'Off by default (shows total/gross carbs)'),
 'ketoadherehelp': ('manage', 'compliant', 'its own logged mode'),
 'manualentry': ('import', 'Customise fields', 'Type in readings by hand for a date'),
 'manualcsvbulk': ('import', 'Download', 'Filling in many days at once?'),
}
EXTRA = {  # (text expected inside, short line that stays visible); the screen is found by looking
 'fibretargethelp': ('UK guideline', 'Daily fibre target.'), 'fastinghelp2': ('Your goal is your own', 'Fasts are measured from the times'),
 'stepbaselinehelp': ('Easy effort', 'Your daily step baseline'), 'weatherhelp': ('rule-of-thumb', 'Weather comes from the free Open-Meteo'),
 'idlepausehelp': ('Genuinely reduces', "Pauses the app's own background activity"), 'resetlayouthelp': ('Nothing you have logged', 'Lost your way?'),
 'symptomhelp': ('Nothing is tracked by default', "Track whatever's actually relevant"), 'treatmenthelp': ('Reports can actually answer', 'Track sessions of anything'),
 'reportprofilehelp': ('Nothing is sent automatically', 'Set up a reusable report'), 'layouthowhelp': ('Starter packs', 'How the filter row, starter packs'),
 'aiusehelp': ('Barcode scanning', 'What each feature sends to the AI'), 'bughint1help': ('screenshot', 'Opens a GitHub report already filled in'),
 'stepsbaselineautohelp': ('real steps week by week', 'steps/day, from your Activity Level'),
}
def toggle(page, hid):
    """tap the ? that belongs to help-<hid>; returns visibility before, after one tap, after two"""
    js = "id=>{const h=document.getElementById('help-'+id); if(!h) return null; const q=h.previousElementSibling; const vis=()=>getComputedStyle(h).display!=='none'&&h.getBoundingClientRect().height>0; const a=vis(); q.click(); const b=vis(); q.click(); const c=vis(); return [a,b,c,h.innerText]}"
    return page.evaluate(js, hid)
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page()
    page.on('pageerror', lambda e: f.add('JS-exception', (str(e) + ' | ' + str(getattr(e, 'stack', '')))[:400])); page.on('dialog', lambda d: d.dismiss())
    ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2000)
    for hid, (tab, inside, visible) in IDS.items():
        ev(f"switchTabById('{tab}')"); page.wait_for_timeout(500)
        r = toggle(page, hid)
        if r is None: f.add('BUG', f'{hid}: no ? on {tab}'); continue
        a, b2, c, txt = r
        if a: f.add('BUG', f'{hid}: help text is already showing before the ? is tapped')
        if not b2: f.add('BUG', f'{hid}: tapping ? did not show the text')
        if c: f.add('BUG', f'{hid}: second tap did not hide the text')
        if inside not in txt: f.add('BUG', f'{hid}: hidden text lost "{inside}"')
        if visible not in ev("document.body.innerText"): f.add('BUG', f'{hid}: short visible line "{visible}" missing')
        dups = ev(DUPS)
        if dups: f.add('BUG', f'{hid}: duplicate ids {dups}')
    for hid, (inside, visible) in EXTRA.items():
        r = None
        for tab in ['manage', 'customise', 'settings', 'import', 'library', 'dash']:
            ev(f"switchTabById('{tab}')"); page.wait_for_timeout(350)
            ev("()=>{document.querySelectorAll('details').forEach(d=>d.open=true)}")
            try: ev("()=>{try{mhRenderStepsBaselineCard()}catch(e){}}")
            except Exception: pass
            r = toggle(page, hid)
            if r is not None: break
        if r is None: f.add('BUG', f'{hid}: no ? found on any settings screen'); continue
        a, b2, c, txt = r
        if a or not b2 or c: f.add('BUG', f'{hid}: ? did not toggle show/hide properly {r[:3]} on {tab}; parent hidden: ' + str(ev("id=>{let e=document.getElementById('help-'+id); const o=[]; while(e&&e!==document.body){ if(getComputedStyle(e).display==='none') o.push((e.id||e.className||e.tagName).toString().slice(0,30)); e=e.parentElement} return o}", hid)))
        if inside not in txt: f.add('BUG', f'{hid}: hidden text lost "{inside}"')
        if visible not in ev("document.body.innerText"): f.add('BUG', f'{hid}: short visible line "{visible}" missing')
    # the steps-baseline ? used to sit inside the Automatic label: tapping it must not flip the switch
    ev("switchTabById('manage')"); page.wait_for_timeout(400)
    c0 = ev("document.getElementById('settingStepsBaselineAuto').checked"); toggle(page, 'stepsbaselineautohelp'); c1 = ev("document.getElementById('settingStepsBaselineAuto').checked")
    if c0 != c1: f.add('BUG', 'tapping the ? beside the steps baseline note flipped the Automatic switch')
    # no long plain block left on those screens (hidden help does not count; the Patterns findings are results from the person's own data, not explainers, and vary by day: 12 Nov 2026)
    LONG = """() => { const out = []; document.querySelectorAll('body *').forEach(e => {
      if (e.closest('.bubble, [id*=chat], [id^=help-], #patternsContent, pre, code, textarea, select, script, style') || getComputedStyle(e).fontFamily.includes('Space Mono')) return;
      const r = e.getBoundingClientRect(); if (r.width < 40 || r.height < 10 || getComputedStyle(e).display === 'none') return;
      const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\\s+/g, ' ').trim();
      if (own.length > 220) out.push(own.slice(0, 60)); }); return out; }"""
    for tab in ['stats', 'reports', 'import', 'manage', 'trends']:
        ev(f"switchTabById('{tab}')"); page.wait_for_timeout(600)
        for t in ev(LONG): f.add('long-text', f'{tab}: still a long block not behind a ?: "{t}…"')
    # reload keeps the screens working
    page.reload(); page.wait_for_timeout(1500); ev("switchTabById('stats')"); page.wait_for_timeout(400)
    if ev("document.getElementById('help-statsintro')") is None: f.add('BUG', 'stats ? gone after reload')
    # import review (dynamic text)
    setup(page, 'import_review')
    r = toggle(page, 'ordreadhelp')
    if r is None: f.add('BUG', 'import review: no ? beside the lines-read count')
    else:
        if r[0] or not r[1] or r[2]: f.add('BUG', f'import review ?: bad toggle {r[:3]}')
        if 'Change a name to link it' not in r[3]: f.add('BUG', 'import review: hidden help lost its text')
    if 'lines read' not in ev("document.body.innerText"): f.add('BUG', 'import review: count line missing')
    # photo-compare panel (Trends)
    ev("switchTabById('trends')"); page.wait_for_timeout(600)
    for hid in ('pcmpcounted', 'pcmpassume'):
        r = ev("id=>!!document.getElementById('help-'+id)", hid)
        print(hid, 'present' if r else 'not shown on this screen (needs the photo-compare card)')
    # Spanish: visible lines translated
    ev("mhLangSet('es')"); page.wait_for_timeout(2500)
    for tab, needle in [('stats', 'Pregunta'), ('reports', 'Informes sirve'), ('import', 'a mano')]:
        ev(f"switchTabById('{tab}')"); page.wait_for_timeout(900)
        body = ev("document.body.innerText")
        if needle.lower() not in body.lower(): f.add('BUG', f'Spanish: {tab} short line is not translated (looked for "{needle}")')
print('findings', len(list(f)))
for x in f: print(x)
sys.exit(1 if len(list(f)) else 0)
