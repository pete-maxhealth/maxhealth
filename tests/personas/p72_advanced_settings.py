"""Persona 72: Settings -> Manage hides the rarely-used cards behind an Advanced chip; they keep working, search reveals them, choice persists."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
ADV = ['set-formulas','set-deviceprec','set-exoffset','set-stepsbaseline','set-reportprofiles','set-idletimeout']
ESS = ['set-profile','set-carbceilings','set-water','set-fasting','set-notifications','set-supplements','set-aiprovider','set-about','set-carer','set-tableware']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); switchTab('settings'); switchSubTab('settings','manage'); mhTopicApply('manage');"); page.wait_for_timeout(400)
    hid = lambda key: page.evaluate("(k) => { const u = genericUnitFor('manage', k); return u.length > 0 && u.every(e => getComputedStyle(e).display === 'none'); }", key)
    for k in ADV:
        if not hid(k): f.add('BUG', f'{k} should be hidden while Advanced is off')
    for k in ESS:
        if hid(k): f.add('BUG', f'{k} is everyday and must stay visible')
    if 'Advanced ▸' not in page.evaluate("document.getElementById('mhTopicBar-manage').innerText"): f.add('BUG', 'Advanced chip missing or wrong label')
    page.evaluate("mhAdvToggle('manage')")
    for k in ADV:
        if hid(k): f.add('BUG', f'{k} should show when Advanced is on')
    page.reload(); page.wait_for_timeout(1500)
    page.evaluate("switchTab('settings'); switchSubTab('settings','manage'); mhTopicApply('manage');"); page.wait_for_timeout(300)
    if hid('set-formulas'): f.add('BUG', 'Advanced-on did not survive reload')
    page.evaluate("mhAdvToggle('manage')")
    if not hid('set-formulas'): f.add('BUG', 'toggling off should hide again')
    page.evaluate("siteSearchOpenSettings('set-formulas','manage','settings','')"); page.wait_for_timeout(600)
    if hid('set-formulas'): f.add('BUG', 'a settings search must reveal the advanced card it found')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
