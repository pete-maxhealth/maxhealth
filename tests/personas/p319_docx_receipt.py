"""Persona 319: a Word (.docx) receipt can be chosen on the Import (receipt) screen: its text is read on the device (JSZip from lib/), columns kept apart, and the lines go through the same reader as pasted text (v3.10.1215). Invented receipt in tests/data/receipt_test.docx."""
import sys, os; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'receipt_test.docx')
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTabById('shop'); mhOrdOpen('receipt')"); page.wait_for_timeout(500)
    ev("(function(){const o=mhOrdLoad; window.mhOrdLoad=function(t,l,m){ window.__doctext=t; return o.apply(this,arguments); }})()")
    with page.expect_file_chooser() as fc: ev("mhOrdPick()")
    fc.value.set_files(PDF); page.wait_for_timeout(2500)
    txt = ev("(function(){const o=_shopUi.ord||{}; return JSON.stringify({stage:o.stage, label:o.label, rows:(o.rows||[]).map(r=>r.name+'|'+(r.amount||'')+'|'+(r.qty||'')), text:(o.text||'').slice(0,300)})})()")
    print(txt[:700]); print(repr(ev('window.__doctext')))
    body = page.inner_text('body')
    for n in ['Cheddar', 'Double Cream', 'Eggs']:
        if n not in body and n not in txt: f.add('BUG', f'the receipt line {n} is read from the Word file')
    if 'Zzqx Cheddar Cheese 400g|800 g|2' not in txt: f.add('BUG', f'2 x 400 g is tallied as 800 g, name kept clean: {txt[:200]}')
    if ev("_shopUi.view") != 'orderimport': f.add('BUG', 'goes to the import review screen')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
