"""Persona 72: Settings -> Manage has Advanced as an ordinary section chip holding the six technical cards; "All" still shows everything,
the Advanced chip shows only those six with a plain-English note, and the other chips no longer contain them."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
ADV = ['set-formulas','set-deviceprec','set-exoffset','set-stepsbaseline','set-reportprofiles','set-idletimeout']
EVERYDAY = ['set-profile','set-carbceilings','set-water','set-fasting','set-notifications','set-supplements','set-aiprovider','set-about','set-carer','set-tableware']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); switchTab('settings'); switchSubTab('settings','manage'); mhTopicSet('manage','all');"); page.wait_for_timeout(400)
    hid = lambda key: page.evaluate("(k) => { const u = genericUnitFor('manage', k); return u.length > 0 && u.every(e => getComputedStyle(e).display === 'none'); }", key)
    for k in ADV + EVERYDAY:
        if hid(k): f.add('BUG', f'{k} must show under All')
    chips = page.evaluate("[...document.querySelectorAll('#mhTopicBar-manage .mh-grp-chip')].map(c => c.innerText)")
    if not any('Advanced' in c for c in chips): f.add('BUG', f'no Advanced chip: {chips}')
    page.evaluate("mhTopicSet('manage','adv')"); page.wait_for_timeout(200)
    for k in ADV:
        if hid(k): f.add('BUG', f'{k} should show under the Advanced chip')
    for k in EVERYDAY:
        if not hid(k): f.add('BUG', f'{k} should not show under the Advanced chip')
    if 'Technical options' not in page.evaluate("document.getElementById('mhTopicBar-manage').innerText"): f.add('BUG', 'Advanced note missing')
    for g in ['me', 'ai', 'tracking', 'about']:
        page.evaluate("(g) => mhTopicSet('manage', g)", g)
        for k in ADV:
            if not hid(k): f.add('BUG', f'{k} leaked into the {g} chip')
    page.evaluate("siteSearchOpenSettings('set-formulas','manage','settings','')"); page.wait_for_timeout(600)
    if hid('set-formulas'): f.add('BUG', 'a settings search must still reveal an advanced card')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
