"""Persona 275: Add foods stops listing the same product twice (v3.10.1170). Pete held "Cauliflower Rice" and the list still offered "Cauliflower Rice (Asda)" as a separate food.
A food that differs from one you already hold only by the shop's brand is hidden, with a line saying how many and a button to show them; two unheld variants are both left (nothing to
compare them to); an exact search for the hidden name still finds it; Tick all shown never ticks a hidden one. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    names = ['Zzqx Cauliflower Rice', 'Zzqx Cauliflower Rice (Asda)', 'Zzqx Cauliflower Frozen (Asda)', 'Zzqx Chicken Mince', 'Zzqx Chicken Mince (Asda)', 'Zzqx Oat Milk (Asda)']
    ev("l=>saveLibrary(l.concat(loadLibrary()))", [{'name': n, 'kcal': 100, 'protein': 5, 'fat': 3, 'carbs': 10, 'portion': '100g'} for n in names])
    ev("""(()=>{ mhStockTrack('Zzqx Cauliflower Rice',{base:'g',pack:1200}); mhStockSetLevel(mhShopKey('Zzqx Cauliflower Rice'),1200);
      mhStockTrack('Zzqx Oat Milk (Asda)',{base:'ml',pack:1000}); mhStockSetLevel(mhShopKey('Zzqx Oat Milk (Asda)'),1000); })()""")
    ev("switchTabById('shop')"); ev("mhSlOpen()"); page.wait_for_timeout(400)
    rows = lambda: ev("()=>[...document.querySelectorAll('#mhSlRows input[data-pick]')].map(e=>e.dataset.pick)")
    has = lambda r, n: n.lower() in [x.lower() for x in r]
    page.fill('#mhSlQ', 'zzqx'); page.wait_for_timeout(400)
    r = rows()
    if has(r, 'Zzqx Cauliflower Rice (Asda)'): f.add('BUG', f'the shop variant of a food you hold is hidden: {r}')
    for want in ['Zzqx Cauliflower Rice', 'Zzqx Cauliflower Frozen (Asda)', 'Zzqx Chicken Mince', 'Zzqx Chicken Mince (Asda)', 'Zzqx Oat Milk (Asda)']:
        if not has(r, want): f.add('BUG', f'{want} must still be listed: {r}')
    if has(r, 'Zzqx Oat Milk'): f.add('BUG', 'the plain name of a food held under its (Asda) name is hidden too, not only the other way round')
    note = ev("document.getElementById('mhSlTwinNote')?.innerText || ''")
    if '1 food is hidden' not in note or 'Zzqx Cauliflower Rice' not in note: f.add('BUG', f'a line says one food is hidden and why: {note!r}')
    # show them
    page.click('#mhSlTwinNote button'); page.wait_for_timeout(300)
    r = rows()
    if not has(r, 'Zzqx Cauliflower Rice (Asda)'): f.add('BUG', f'Show them brings the hidden food back: {r}')
    note = ev("document.getElementById('mhSlTwinNote')?.innerText || ''")
    if 'Showing 1 food' not in note: f.add('BUG', f'and the line now says they are shown: {note!r}')
    page.click('#mhSlTwinNote button'); page.wait_for_timeout(300)
    if has(rows(), 'Zzqx Cauliflower Rice (Asda)'): f.add('BUG', 'Hide them hides it again')
    # an exact search still finds it
    page.fill('#mhSlQ', 'zzqx cauliflower rice (asda)'); page.wait_for_timeout(400)
    if not has(rows(), 'Zzqx Cauliflower Rice (Asda)'): f.add('BUG', f'typing the exact name finds it even though it is hidden: {rows()}')
    # tick all shown never ticks a hidden one
    page.fill('#mhSlQ', 'zzqx cauliflower'); page.wait_for_timeout(400)
    page.click('button:has-text("Tick all shown")'); page.wait_for_timeout(300)
    sel = ev("Object.keys(mhSlState().sel)")
    if any('asda' in k and 'rice' in k for k in sel): f.add('BUG', f'Tick all shown ticked a hidden food: {sel}')
    # after the held food is removed the twin is offered again
    ev("(()=>{const o=mhStockLoad(); delete o.items[mhShopKey('Zzqx Cauliflower Rice')]; mhStockSave(o);})()"); ev("mhSlOpen()"); page.wait_for_timeout(300)
    page.fill('#mhSlQ', 'zzqx cauliflower'); page.wait_for_timeout(400)
    if not has(rows(), 'Zzqx Cauliflower Rice (Asda)'): f.add('BUG', 'with nothing held, both variants are listed again')
    if ev("!!document.getElementById('mhSlTwinNote')"): f.add('BUG', 'and no hidden-foods line is shown')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
