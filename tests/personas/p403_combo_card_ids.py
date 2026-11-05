"""Persona 403: "+ add ingredient" / amount / swap / remove / log on a suggestion card act on THAT card, even after several "Next meal idea" rounds (v3.10.1299). Pete (5 Nov): clicked + add ingredient on a Next meal idea card, nothing changed on it.
Cause: each round restarted the card numbers at 0, so the second round's card 0 shared its id (and its slot in the pending list) with the first round's. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("()=>{const lib=loadLibrary(); [['Zzqx Marmite',5],['Zzqx Crackerbread',14],['Zzqx Olives',30],['Zzqx Cheese',25]].forEach(([n,g])=>lib.push({name:n,kcal:100,protein:5,carbs:2,fat:5,portion:g+'g',per100g:false})); saveLibrary(lib)}")
    ev("switchTabById('chat')")
    lib = "loadLibrary()"
    # round 1 and round 2, each one card
    ev("()=>renderLibraryComboSuggestions({combos:[{items:['Zzqx Marmite','Zzqx Crackerbread'],note:'round one'}]}, loadLibrary(), [], {})")
    ev("()=>renderLibraryComboSuggestions({combos:[{items:['Zzqx Olives'],note:'round two'}]}, loadLibrary(), [], {})")
    page.wait_for_timeout(300)
    cards = ev("[...document.querySelectorAll('[id^=combo-card-]')].map(e=>e.id)")
    if len(cards) != len(set(cards)): f.add('BUG', f'1: card ids are unique across rounds: {cards}')
    # add Cheese to the SECOND (newest) card through the real picker route
    idx_new = ev("()=>[...document.querySelectorAll('[id^=combo-card-]')].pop().querySelector('[onclick^=openLibraryPickerForCombo]').getAttribute('onclick').match(/\\((\\d+)\\)/)[1]")
    ev("i=>openLibraryPickerForCombo(+i)", idx_new)
    li = ev("()=>loadLibrary().findIndex(l=>l.name==='Zzqx Cheese')")
    ev("i=>_libPickerItemChosen(i)", li); page.wait_for_timeout(300)
    texts = ev("[...document.querySelectorAll('[id^=combo-card-]')].map(e=>e.innerText)")
    if 'Zzqx Cheese' not in texts[-1]: f.add('BUG', f'2: the new card shows the ingredient just added: {[t[:60] for t in texts]}')
    if 'Zzqx Cheese' in texts[0]: f.add('BUG', '3: the OLD card must not change')
    # amount edit and remove on the new card also hit that card
    idx_old = ev("()=>[...document.querySelectorAll('[id^=combo-card-]')][0].querySelector('[onclick^=removeComboItem]').getAttribute('onclick').match(/\\((\\d+),/)[1]")
    if idx_old == idx_new: f.add('BUG', f'4: old and new card point at different slots (old {idx_old}, new {idx_new})')
    ev("i=>removeComboItem(+i,0)", idx_new); page.wait_for_timeout(200)
    texts = ev("[...document.querySelectorAll('[id^=combo-card-]')].map(e=>e.innerText)")
    if 'Zzqx Olives' in texts[-1] or 'Zzqx Marmite' not in texts[0]: f.add('BUG', f'5: remove acts on the new card only: {[t[:50] for t in texts]}')
    # logging the old card logs ITS items, not the new round's
    ev("i=>logSuggestedCombo(+i)", idx_old); page.wait_for_timeout(500)
    names = ev("state.todayLog.map(e=>JSON.stringify(e)).join(' ')")
    if 'Zzqx Marmite' not in names: f.add('BUG', f'6: logging the old card logs its own items: {names[:200]}')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
