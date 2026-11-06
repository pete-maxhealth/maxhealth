"""Persona 407: bulk "remove all non-nutritional" in My cupboards (v3.10.1302). Pete (5 Nov): imports made before Undo existed filled the cupboards with household items.
Covers: the button shows only on the Non-nutritional tab with the right count, asks first, removes only non-food, keeps stock figures in Recently removed,
one Undo brings them all back with their levels, survives a reload, and the Recently removed list can restore one at a time. Invented data, demo persona."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
NF = ['Zzqx Bin Bags', 'Zzqx Washing Pods', 'Zzqx Toilet Roll']; FD = ['Zzqx Rice', 'Zzqx Oats']
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("startDemoMode('doris')"); page.wait_for_timeout(1800)
    ev("n=>{n[0].forEach((x,i)=>{mhStockTrack(x,{base:'each'}); const k=mhShopKey(x); const o=mhStockLoad(); o.items[k].nonFood=true; mhStockSave(o); mhStockSetLevel(k,3+i)}); n[1].forEach((x,i)=>{mhStockTrack(x,{base:'g'}); mhStockSetLevel(mhShopKey(x),500+i)})}", [NF, FD])
    N = ev('mhCbNonFoodKeys().length')   # the demo may carry some of its own
    names = lambda: ev("Object.values(mhStockLoad().items).map(i=>i.name).sort().join('|')")
    ev("switchTabById('shop'); mhShopView('list'); mhShopPaneSet('stock')"); page.wait_for_timeout(500)
    ev("mhCbTab('all')"); page.wait_for_timeout(300)
    if ev("!!document.getElementById('mhCbBulkNonFood')"): f.add('BUG', '1: the bulk button shows on the All tab')
    ev("mhCbTab('nonfood')"); page.wait_for_timeout(300)
    txt = ev("(document.getElementById('mhCbBulkNonFood')||{}).innerText||''")
    if str(N) not in txt: f.add('BUG', f'2: bulk button missing or wrong count: "{txt}"')
    page.screenshot(path='/tmp/p407.png')
    ev("document.querySelector('#mhCbBulkNonFood button').click()"); page.wait_for_timeout(300)
    if not ev("!!document.querySelector('.app-modal-overlay')"): f.add('BUG', '3: it asks before removing')
    elif names().count('Zzqx') < 5: f.add('BUG', '3b: nothing is removed before the answer')
    # cancel first
    ev("document.getElementById('appModalCancel').click()"); page.wait_for_timeout(300)
    if sum(n in names() for n in NF) != 3 or ev('mhCbNonFoodKeys().length') != N: f.add('BUG', '4: cancel keeps everything')
    ev("document.querySelector('#mhCbBulkNonFood button').click()"); page.wait_for_timeout(300)
    ev("document.getElementById('appModalConfirm').click()"); page.wait_for_timeout(500)
    now = names()
    if any(n in now for n in NF): f.add('BUG', f'5: the non-food items are removed: {now}')
    if not all(n in now for n in FD): f.add('BUG', f'6: foods are left alone: {now}')
    if ev("!!document.getElementById('mhCbBulkNonFood')"): f.add('BUG', '7: the bulk button goes when none are left')
    if ev("mhStockRemovedLoad().length") != N: f.add('BUG', f'8: all three are kept in Recently removed: {ev("mhStockRemovedLoad().length")}')
    ev("mhCbTab('all')"); page.wait_for_timeout(300)
    if 'Zzqx Bin Bags' in ev("document.body.innerText").split('Recently removed')[0]: f.add('BUG', '9: removed item still listed')
    # Undo (the toast action)
    undone = ev("(()=>{const b=[...document.querySelectorAll('#toast button, #toast span, #toast a')].find(x=>/undo/i.test(x.innerText)); if(b){b.click(); return true} return false})()"); page.wait_for_timeout(500)
    if not undone: f.add('BUG', '10: the message offers Undo')
    else:
        now = names()
        if not all(n in now for n in NF + FD): f.add('BUG', f'11: Undo brings all of them back: {now}')
        lv = ev("Object.values(mhStockLoad().items).filter(i=>i.nonFood).map(i=>i.level).sort().join(',')")
        if not all(v in lv.split(',') for v in ('3','4','5')): f.add('BUG', f'12: stock figures come back with them: {lv}')
        if ev("mhCbNonFoodKeys().length") != N or ev("mhStockRemovedLoad().length") != 0: f.add('BUG', '13: Recently removed is empty after Undo')
    # remove again, reload, restore one by one
    ev("mhCbTab('nonfood')"); ev("mhCbRemoveNonFood()"); page.wait_for_timeout(300)
    ev("document.getElementById('appModalConfirm').click()"); page.wait_for_timeout(500)
    page.reload(); page.wait_for_timeout(1500)
    if ev("mhStockRemovedLoad().length") != N or any(n in names() for n in NF): f.add('BUG', '14: removal and Recently removed survive a reload')
    ev("k=>mhStockRestoreRemoved(k)", ev("mhShopKey('Zzqx Toilet Roll')")); page.wait_for_timeout(300)
    if 'Zzqx Toilet Roll' not in names() or 'Zzqx Bin Bags' in names(): f.add('BUG', '15: restoring one brings back only that one')
    if ev("!!document.getElementById(\"mhCbBulkNonFood\")") and False: pass
    d = ev(r"""()=>{const seen={}, d=[]; document.querySelectorAll('[id]').forEach(e=>{if(seen[e.id])d.push(e.id); seen[e.id]=1}); return d}""")
    if d: f.add('BUG', f'16: duplicate ids {d}')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
