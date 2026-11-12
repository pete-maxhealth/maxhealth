"""Persona 464 (v3.10.1379): the Reports topic row has no chip for a topic whose cards are all hidden. The Losing weight start hides the Treatment card on Reports, so no Treatment chip; showing the card brings the chip back; a normal start still has all chips. Demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
chips = "[...document.querySelectorAll('#mhTopicBar-reports .mh-grp-chip')].filter(c=>c.offsetParent!==null).map(c=>c.textContent.trim())"
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev("startDemoMode('doris')"); page.wait_for_timeout(2500)
    ev("switchTab('insights'); switchSubTab('insights','reports')"); page.wait_for_timeout(1000)
    c0 = ev(chips)
    if 'Treatment' not in c0 or len(c0) < 5: f.add('BUG', f'1: a normal start should show every chip: {c0}')
    ev("mhPackApply(MH_FIRST_RUN_PACKS.loss, ['layout'], 'replace')"); page.reload(); page.wait_for_timeout(2500)
    ev("startDemoMode('doris')") if False else None
    ev("switchTab('insights'); switchSubTab('insights','reports')"); page.wait_for_timeout(1000)
    c1 = ev(chips)
    if 'Treatment' in c1: f.add('BUG', f'2: Losing weight start still has a Treatment chip: {c1}')
    if 'Analysis' not in c1: f.add('BUG', f'3: other chips went missing: {c1}')
    vis = ev("(()=>{const e=document.getElementById('title-rpt-treatment')||document.querySelector('[id*=rpt-treatment]'); return e? e.offsetParent!==null : null})()")
    if vis: f.add('BUG', '4: the Treatment card still shows on Reports')
    ev("saveGenericHidden('reports', getGenericHidden('reports').filter(k => k !== 'rpt-treatment'))"); page.wait_for_timeout(400)
    if 'Treatment' not in ev(chips): f.add('BUG', '5: showing the card did not bring the chip back')
    ev("mhTopicSet('reports','treat')"); page.wait_for_timeout(300); ev("saveGenericHidden('reports', getGenericHidden('reports').concat(['rpt-treatment']))"); page.wait_for_timeout(300)
    if 'Treatment' not in ev(chips): f.add('BUG', '6: the chip you are on must not vanish under you')
    ev("mhTopicSet('reports','all')")
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
