"""Persona 203: Bulk "no fibre" for structurally negligible categories (v3.10.1114). Pete Spence: herbs,
spices, dairy, meat, fish and oils either genuinely have no fibre, or (herbs/spices) the real per-100g
figure rounds away to nothing at a normal serving - USDA-sourced figures show even the highest dried
spices (oregano, basil) are only ~0.3-0.4g per teaspoon, below his own 0.5g "is it worth counting" bar.
Rather than a table of invented per-100g numbers, the audit offers one bulk action covering meat, fish,
dairy, fat and herbs & spices together. Covers: the bulk button appears only when there's something in
those categories outstanding, marks them all fibreChecked=0g in one tap, never touches a meal entry or
an item in another category, and the per-item flow for everything else is untouched."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()")
    ev("""saveLibrary([
        {id:'m1', name:'Chicken Breast', kcal:165, protein:31, carbs:0, fat:4, portion:'100g', categories:['meat','protein']},
        {id:'m2', name:'Smoked Salmon', kcal:117, protein:18, carbs:0, fat:4, portion:'100g', categories:['fish','protein']},
        {id:'m3', name:'Double Cream', kcal:340, protein:2, carbs:3, fat:36, portion:'100g', categories:['dairy','fat']},
        {id:'m4', name:'Olive Oil', kcal:884, protein:0, carbs:0, fat:100, portion:'1 tbsp', categories:['fat']},
        {id:'m5', name:'Dried Oregano', kcal:265, protein:9, carbs:49, fat:4, portion:'1 tsp', categories:['herbs and spices']},
        {id:'m6', name:'Chicken Casserole', kcal:300, protein:25, carbs:10, fat:12, portion:'1 serving', isMeal:true, categories:['meat']},
        {id:'m7', name:'Lentil Soup', kcal:120, protein:7, carbs:18, fat:2, portion:'1 bowl', categories:['beans and pulses']},
        {id:'m8', name:'Black Pepper', kcal:251, protein:10, carbs:64, fat:3, categories:['herbs and spices'], fibre:3, fibreChecked:true},
    ])""")
    ev("mhNutrientAudit()"); page.wait_for_timeout(300)

    modal_txt = ev("document.getElementById('mhAuditModal')?.textContent || ''")
    if 'Mark these' not in modal_txt: f.add('BUG', f'bulk button did not appear with eligible items present: {modal_txt[:200]!r}')
    if '5 as no fibre' not in modal_txt and 'Mark these 5' not in modal_txt:
        f.add('BUG', f'bulk count should be 5 (m1-m5; m6 is a meal, m7 is beans, m8 already checked), got: {modal_txt[:300]!r}')

    ev("mhAuditBulkNoFibre()"); page.wait_for_timeout(200)
    lib = ev("loadLibrary()")
    byId = {x['id']: x for x in lib}
    for mid in ['m1', 'm2', 'm3', 'm4', 'm5']:
        it = byId[mid]
        if it.get('fibre') != 0 or not it.get('fibreChecked'):
            f.add('BUG', f'{mid} ({it["name"]}) should be fibre=0, fibreChecked=true: {it}')
    meal = byId['m6']
    if meal.get('fibreChecked'): f.add('BUG', 'meal entry (Chicken Casserole) must not be swept up by the bulk action')
    lentil = byId['m7']
    if lentil.get('fibreChecked'): f.add('BUG', 'Lentil Soup (beans and pulses) must not be swept up by the bulk action')
    pepper = byId['m8']
    if pepper.get('fibre') != 3: f.add('BUG', 'already-checked Black Pepper should be left alone, not overwritten to 0')

    # second run with nothing left outstanding in those categories: no button, friendly toast
    ev("mhNutrientAudit()"); page.wait_for_timeout(200)
    modal_txt2 = ev("document.getElementById('mhAuditModal')?.textContent || ''")
    if 'Mark these' in modal_txt2: f.add('BUG', 'bulk button should disappear once nothing is outstanding in those categories')

    # the per-item manual flow (a non-eligible category) is untouched
    ev("mhAuditSave('m7', false)")  # no value typed - should be rejected same as before
    toast_ok = True  # mhAuditSave shows a toast and returns without saving when no value given; just confirm it wasn't marked
    lib2 = ev("loadLibrary()"); lentil2 = next(x for x in lib2 if x['id']=='m7')
    if lentil2.get('fibreChecked'): f.add('BUG', 'manual Save with no typed value should not have marked Lentil Soup checked')

    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
