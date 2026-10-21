"""Persona 233: CSV import rows show the same one match state as receipt import (v3.10.1126): a suggested near match says "Check this", picking the
food by hand turns it green "Matched", a food nobody knows says "New food". Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    ev("l=>saveLibrary(l.concat(loadLibrary()))", [{'name': 'Double Cream (Aldi)', 'kcal': 471, 'protein': 1.5, 'fat': 48, 'carbs': 1.7, 'portion': '30ml'}])
    ev("mhShopCsvLoad('Item,Qty\\nCream double (Aldi),1\\nZzqx Wibble Flakes,2\\n','t.csv')"); page.wait_for_timeout(300)
    st = ev("[...document.querySelectorAll('[data-csv] .mh-match-badge')].map(e=>[e.closest('[data-csv]').dataset.csv,e.dataset.state])")
    d = dict(st)
    if d.get('Cream double (Aldi)') != 'check': f.add('BUG', f'1: a suggested near match says Check this: {st}')
    if d.get('Zzqx Wibble Flakes') != 'new': f.add('BUG', f'2: an unknown food says New food: {st}')
    ev("mhCsvPick(0,'Double Cream (Aldi)'); mhShopRender()"); page.wait_for_timeout(200)
    st = dict(ev("[...document.querySelectorAll('[data-csv] .mh-match-badge')].map(e=>[e.closest('[data-csv]').dataset.csv,e.dataset.state])"))
    if st.get('Cream double (Aldi)') != 'matched': f.add('BUG', f'3: picking it turns it green Matched: {st}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
