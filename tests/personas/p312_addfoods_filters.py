"""Persona 312: Add foods lists: no separate No amount yet chip, Needs details covers it, herbs/spices/never-run-out foods are hidden from Not in my cupboards and Needs details with a note and Show/Hide, counting one makes it count like any other (v3.10.1213). Invented foods."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("window._mhLibQuiet=true")
    lib = [('a', 'Zzqx Cheddar', '100g'), ('b', 'Rosemary', '100g'), ('c', 'Zzqx Salt', '100g'), ('d', 'Zzqx Rice', '100g')]
    ev("saveLibrary(%s)" % str([{'id': i, 'name': n, 'kcal': 100, 'protein': 5, 'carbs': 5, 'fat': 5, 'portion': p} for i, n, p in lib]).replace("'", '"'))
    ev("mhRulesEdit(r=>{r.neverNames.push(mhShopKey('Zzqx Salt')); r.neverCats.push('herbs and spices')})")
    ev("mhStockTrack('Zzqx Rice',{base:'g',shop:'Asda'})")   # tracked, no amount, reorder or serving => needs details
    ev("mhStockTrack('Zzqx Salt',{base:'g',shop:'Asda'})")   # never-run-out, tracked, no amount => not needing details
    ev("switchTabById('shop'); mhSlGaps()"); page.wait_for_timeout(500)
    chips = ev("[...document.querySelectorAll('[data-f]')].map(b=>b.dataset.f)")
    if 'noamt' in chips: f.add('BUG', f'no separate No amount yet chip: {chips}')
    names = lambda: ev("[...document.querySelectorAll('#mhSlRows [data-pick]')].map(e=>e.closest('[data-sl]')?e.closest('[data-sl]').dataset.sl:e.dataset.pick)")
    rows = ev("mhSlFilter(mhSlRows()).map(r=>r.name)")
    if 'Zzqx Rice' not in rows: f.add('BUG', f'Needs details lists the tracked food with gaps: {rows}')
    if 'Zzqx Salt' in rows: f.add('BUG', f'Needs details leaves out the never-run-out food: {rows}')
    ev("mhSlF('not')"); rows = ev("mhSlFilter(mhSlRows()).map(r=>r.name)")
    if 'Zzqx Cheddar' not in rows or 'Rosemary' in rows: f.add('BUG', f'Not in my cupboards hides herbs/spices, keeps cheddar: {rows}')
    if not page.query_selector('#mhSlNeverNote'): f.add('BUG', 'a note says some are hidden')
    ev("mhSlNever(true)"); page.wait_for_timeout(300); rows = ev("mhSlFilter(mhSlRows()).map(r=>r.name)")
    if 'Rosemary' not in rows: f.add('BUG', f'Show them shows herbs and spices: {rows}')
    ev("mhSlNever(false)")
    # a herb the app does not know by name but you categorised in the Library is hidden too
    ev("saveLibrary([...loadLibrary(), {id:'e',name:'Zzqx Mixed Herb',kcal:5,protein:0,carbs:1,fat:0,portion:'1g',categories:['herbs and spices']}])")
    ev("mhSlF('not')"); rows = ev("mhSlFilter(mhSlRows()).map(r=>r.name)")
    if 'Zzqx Mixed Herb' in rows: f.add('BUG', f'the Library category herbs and spices counts: {rows}')
    # counting a herb yourself makes it count like any other
    ev("mhStockTrack('Rosemary',{base:'g',shop:'Asda'}); mhStockSetLevel(mhShopKey('Rosemary'),50)")
    if 'how much you have' in ev("mhStockGaps(mhStockLoad().items[mhShopKey('Rosemary')])") : f.add('BUG', 'counted herb has an amount')
    if not ev("mhStockGaps(mhStockLoad().items[mhShopKey('Rosemary')]).length"): f.add('BUG', 'a herb you count is checked like any other food')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
