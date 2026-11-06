"""Persona 408: the Data screen is grouped by what you want to do (v3.10.1303). Pete's plan: "Bring data in", "Move or back up", "Check it's complete".
Covers: the chips and their order, each chip shows only its own cards and All shows all five, the default card order follows the intents, an old saved chip
(Connect devices / Backup & restore) falls back to All instead of hiding everything, a chip choice survives a reload, show/hide and reorder on the cards still
work, no duplicate ids, Spanish chip labels. Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
CARDS = {'bring': ['imp-sync', 'imp-manual'], 'move': ['set-databackup', 'imp-restore'], 'check': ['imp-gaps']}
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("startDemoMode('doris')"); page.wait_for_timeout(1800)
    ev("switchTabById('import')"); page.wait_for_timeout(700)
    chips = ev("[...document.querySelectorAll('#mhTopicBar-import .mh-grp-chip')].map(e=>e.innerText)")
    if chips != ['All', 'Bring data in', 'Move or back up', "Check it's complete"]: f.add('BUG', f'1: chips: {chips}')
    # which top-level cards are visible
    VIS = "()=>{const o={}; for (const k of ['imp-sync','imp-manual','set-databackup','imp-restore','imp-gaps']) { const t=document.getElementById('title-'+k); const u=t&&t.closest('.import-card, .card-unit')||t; o[k]=!!u && !u.classList.contains('mh-grp-hide') && getComputedStyle(u).display!=='none'; } return o}"
    allv = ev(VIS)
    if not all(allv.values()): f.add('BUG', f'2: All shows every card: {allv}')
    # default order
    order = ev("()=>['imp-sync','imp-manual','set-databackup','imp-restore','imp-gaps'].map(k=>{const t=document.getElementById('title-'+k); const u=t&&(t.closest('.import-card, .card-unit')||t); return [k, u?u.getBoundingClientRect().top+scrollY:-1]}).sort((a,b)=>a[1]-b[1]).map(x=>x[0])")
    if order != ['imp-sync', 'imp-manual', 'set-databackup', 'imp-restore', 'imp-gaps']: f.add('BUG', f'3: default order follows the intents: {order}')
    for g, keys in CARDS.items():
        ev(f"mhTopicSet('import','{g}')"); page.wait_for_timeout(250)
        v = ev(VIS); want = {k: (k in keys) for k in v}
        if v != want: f.add('BUG', f'4: chip {g} shows {v}, wanted {want}')
    ev("mhTopicSet('import','move')"); page.reload(); page.wait_for_timeout(1800); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTabById('import')"); page.wait_for_timeout(600)
    # a chip choice is remembered across a reload (demo mode restarts the session, so check storage and the applied class)
    kept = ev("mhTopicGet('import')")
    if kept != 'move': f.add('BUG', f'5: chip after reload: {kept}')
    # an old saved chip must fall back to All, not hide everything
    for old in ('connect', 'history', 'backup'):
        ev(f"localStorage.setItem('mh_topic_import','{old}'); mhTopicApply('import')"); page.wait_for_timeout(200)
        v = ev(VIS)
        if not all(v.values()): f.add('BUG', f'6: an old saved chip "{old}" hides cards: {v}')
    ev("mhTopicSet('import','all')"); page.wait_for_timeout(200)
    # show/hide and reorder still work on a card
    before = ev(VIS)
    ev("()=>{const t=document.getElementById('title-imp-gaps'); const u=t.closest('.import-card, .card-unit')||t; return u.id||u.className}")
    ctl = ev("()=>({up:[...document.querySelectorAll('#view-import [onclick*=moveGenericSection]')].length, hide:[...document.querySelectorAll('#view-import [onclick*=toggleGenericSectionHidden]')].length})")
    if ctl['up'] < 5 or ctl['hide'] < 5: f.add('BUG', f'7: reorder and show/hide controls are on the five Data cards: {ctl}')
    TOP = "k=>{const t=document.getElementById('title-'+k); const u=t&&(t.closest('.import-card, .card-unit')||t); return u&&u.getBoundingClientRect().top+scrollY}"
    ev("moveGenericSection('import','imp-gaps','up')"); page.wait_for_timeout(300)
    if not ev(TOP, 'imp-gaps') < ev(TOP, 'imp-restore'): f.add('BUG', '7b: moving Missing Data up puts it above Restore')
    ev("moveGenericSection('import','imp-gaps','down')"); page.wait_for_timeout(300)
    ev("toggleGenericSectionHidden('import','imp-manual')"); page.wait_for_timeout(300)
    if ev(VIS)['imp-manual']: f.add('BUG', '7c: hiding Manual Entry hides it')
    ev("toggleGenericSectionHidden('import','imp-manual')"); page.wait_for_timeout(300)
    if not ev(VIS)['imp-manual']: f.add('BUG', '7d: showing Manual Entry brings it back')
    dups = ev("()=>{const seen={},d=[];document.querySelectorAll('[id]').forEach(e=>{if(seen[e.id])d.push(e.id);seen[e.id]=1});return d}")
    if dups: f.add('BUG', f'8: duplicate ids {dups}')
    ev("mhLangSet('es')"); page.wait_for_timeout(2500); ev("switchTabById('import')"); page.wait_for_timeout(600)
    es = ev("[...document.querySelectorAll('#mhTopicBar-import .mh-grp-chip')].map(e=>e.innerText).join('|')")
    if 'Traer datos' not in es or 'Mover o respaldar' not in es: f.add('BUG', f'9: Spanish chip labels: {es}')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
