"""Persona 230: every receipt row shows ONE clear match state (v3.10.1125). A sure or picked match shows a green "Matched"; a closest-guess shows an
amber "Check this"; a food with nothing in the library shows "New food". A long matched name is shown in full under the box. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""saveLibrary([
      {id:'l1',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5},
      {id:'l2',name:'Gluten Free Cumberland Sausages',kcal:200,protein:12,carbs:6,fat:14,portion:'100g',useCount:2}
    ])""")
    ev("mhShopOpen()"); ev("mhOrdOpen('receipt')"); page.wait_for_timeout(200)
    page.fill('#mhOrdText', "Cheddar 400g\n1.00\nExceptional Cumberland Pork Sausages 400g\n2.00\nZzqx Wibble Flakes 300g\n3.00\n"); page.click('#mhOrdRead'); page.wait_for_timeout(400)
    b = ev("[...document.querySelectorAll('.mh-match-badge')].map(e=>[e.dataset.state,e.textContent])")
    st = [x[0] for x in b]
    if st != ['matched', 'check', 'new']: f.add('BUG', f'1: one badge per row, in order matched / check / new: {b}')
    if b and 'Matched' not in b[0][1]: f.add('BUG', f'1: matched row says Matched: {b}')
    if len(b) > 1 and 'Check this' not in b[1][1]: f.add('BUG', f'1: guess row says Check this: {b}')
    full = ev("[...document.querySelectorAll('.mh-match-full')].map(e=>e.textContent)")
    if not any('Gluten Free Cumberland Sausages' in x for x in full): f.add('BUG', f'2: long matched name shown in full: {full}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
