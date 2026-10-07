"""Persona 50: topic chips on Reports and Settings->Manage filter the flat lists, persist, never hide a searched-for section, and leave 👁/▲▼ alone."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    for scope, tab, sub, topic, shown, hidden in [
        ('reports', 'insights', 'reports', 'ask', ['rpt-askai', 'rpt-export'], ['rpt-summary', 'rpt-treatment', 'seasonal']),
        ('import', 'settings', 'import', 'backup', ['set-databackup', 'imp-preview'], ['imp-sync', 'imp-manual', 'imp-master']),
        ('manage', 'settings', 'manage', 'tracking', ['set-supplements', 'set-labresults'], ['set-profile', 'set-aiprovider', 'set-about']),
    ]:
        page.evaluate(f"switchTab('{tab}'); switchSubTab('{tab}','{sub}')"); page.wait_for_timeout(900)
        chips = page.evaluate(f"[...document.querySelectorAll('#mhTopicBar-{scope} .mh-grp-chip')].map(c=>c.textContent)")
        if len(chips) < 4 or chips[0] != 'All': f.add('BUG', f'{scope} chips wrong: {chips}')
        page.evaluate(f"mhTopicSet('{scope}','{topic}')")
        isHid = lambda key: page.evaluate(f"(()=>{{const t=document.getElementById(GENERIC_SECTION_IDS['{scope}']['{key}'][0]);const u=t&&(t.closest('.card-unit')||t);return u?u.classList.contains('mh-grp-hide'):null}})()")
        for k in shown:
            if isHid(k) is not False: f.add('BUG', f'{scope}/{topic}: {k} should show, hidden={isHid(k)}')
        for k in hidden:
            if isHid(k) is not True: f.add('BUG', f'{scope}/{topic}: {k} should be filtered out, hidden={isHid(k)}')
    # persists
    page.reload(); page.wait_for_timeout(1500)
    page.evaluate("switchTab('settings'); switchSubTab('settings','manage')"); page.wait_for_timeout(900)
    if page.evaluate("document.querySelector('#mhTopicBar-manage .mh-grp-chip.active')?.textContent") != 'Health tracking': f.add('BUG', 'manage topic not remembered')
    # searching for a filtered-out section resets the filter so it is visible
    page.evaluate("siteSearchOpenSettings('set-tableware', 'manage', 'settings', '')"); page.wait_for_timeout(900)
    hid = page.evaluate("(()=>{const t=document.getElementById('title-set-tableware');return (t.closest('.card-unit')||t).classList.contains('mh-grp-hide')})()")
    if hid: f.add('BUG', 'search landed on a section hidden by a topic chip')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
