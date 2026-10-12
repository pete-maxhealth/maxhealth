"""Persona 119: with a Settings topic chip active (About & setup), the up/down buttons visibly move the card past hidden neighbours."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("localStorage.setItem('mh_topic_manage','about')"); ev("switchTab && switchTab('manage')"); page.wait_for_timeout(600)
    ev("makeContainerReorderable(document.getElementById('view-manage'),'manage'); mhTopicApply('manage'); applyGenericOrder('manage')")
    ev("localStorage.setItem('mh_reorder_manage', JSON.stringify(['set-aiprovider','set-profile','set-premium','set-water','set-about','set-fasting','set-setup','set-carbceilings','set-exoffset','set-deviceprec','set-formulas','set-carer','set-notifications','set-idletimeout','set-tableware','set-stepsbaseline','set-supplements','set-symptoms','set-treatments','set-labresults','set-reportprofiles']))"); ev("applyGenericOrder('manage')")
    vis = "[...document.querySelectorAll('#view-manage .section-title')].filter(e=>e.offsetParent&&/^title-set-/.test(e.id)).map(e=>e.id)"
    before = ev(vis)
    if len(before) < 2: f.add('BUG', f'expected 2+ visible cards in About topic, got {before}')
    else:
        last = before[-1].replace('title-', '')
        ev(f"moveGenericSection('manage','{last}','up')"); after = ev(vis)
        if after == before: f.add('BUG', f'up did nothing visibly {before}')
        if after[-2] != before[-1]: f.add('BUG', f'not moved up one visible slot {after}')
        ev(f"moveGenericSection('manage','{last}','down')")
        if ev(vis) != before: f.add('BUG', 'down did not restore')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
