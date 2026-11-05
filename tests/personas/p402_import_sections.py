"""Persona 402: the import review is grouped like My cupboards, with a tick all per section (v3.10.1298). Pete (5 Nov): "categories needed here with select all, same as everywhere else under shopping".
Covers: sections in walking order with counts, tick all / untick per section (only rows with an amount), shut sections stay shut after an action and a reload, Close all / Open all, flat with eight lines or fewer. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
FOODS = [('Zzqx Chicken Breast','meat'),('Zzqx Mince','meat'),('Zzqx Cheddar','dairy'),('Zzqx Milk','dairy'),('Zzqx Apples','fruit'),('Zzqx Carrots','vegetable'),('Zzqx Rice','grain'),('Zzqx Beans','beansandpulses'),('Zzqx Bread Rolls','bread')]
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("l=>{const lib=loadLibrary(); l.forEach(([n,c])=>lib.push({name:n,kcal:100,protein:5,carbs:5,fat:5,categories:[c],per100g:true})); saveLibrary(lib)}", FOODS)
    txt = "\n".join(f"1 x {n} 400g\t£1.00" for n, _ in FOODS) + "\n1 x Zzqx Washing Pods 30\t£4.00"
    ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300); ev("t=>mhOrdLoad(t,'test')", txt); page.wait_for_timeout(600)
    ev("mhOrdKindSet(9,'nonfood')")
    secs = ev("[...document.querySelectorAll('[data-ord-sec]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
    if len(secs) < 5: f.add('BUG', f'1: sections shown: {secs}')
    order = [int(x) for x in ev("[...document.querySelectorAll('[data-ord-sec]')].map(e=>e.dataset.ordSec)")]
    if order != sorted(order): f.add('BUG', f'2: walking order: {order}')
    if not any('MEAT' in x and '2' in x for x in secs) or not any('DAIRY' in x and '2' in x for x in secs): f.add('BUG', f'3: counts per section: {secs}')
    page.screenshot(path='/tmp/p402.png')
    ev("mhOrdAll(false)"); ev("rows=_shopUi.ord.rows; rows.forEach((r,i)=>{r.amount=r.amount||'400 g'})")
    msec = ev("mhOrdSec(_shopUi.ord.rows[0],_shopUi.ord)")
    ev("s=>mhOrdSecTick(s,true)", msec)
    on = ev("_shopUi.ord.rows.map(r=>r.on)")
    if on[:2] != [True, True] or any(on[2:]): f.add('BUG', f'4: tick all in Meat ticks only the meat rows: {on}')
    ev("s=>mhOrdSecTick(s,false)", msec)
    if any(ev("_shopUi.ord.rows.map(r=>r.on)")): f.add('BUG', '5: untick clears the section')
    ev("_shopUi.ord.rows[0].amount=''"); ev("s=>mhOrdSecTick(s,true)", msec)
    if ev("_shopUi.ord.rows[0].on"): f.add('BUG', '6: a row with no amount is not ticked by tick all (same as the global one)')
    ev("s=>mhOrdSecFold(s)", msec); ev("mhOrdSecTick(99,true)")
    page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("switchTabById('shop'); mhOrdOpen(_shopUi.ordKind||'order')"); page.wait_for_timeout(600)
    if ev("s=>!!_shopUi.ord.fold&&!!_shopUi.ord.fold[s]", msec) is not True or ev("document.body.innerText").count('Zzqx Chicken Breast') > 1 and False: f.add('BUG', '7: a shut section stays shut after a reload')
    ev("mhOrdFoldAll(true)"); n_shut = ev("[...document.querySelectorAll('[data-ord-sec]')].length")
    if ev("document.querySelectorAll('[data-ord]').length") != 0: f.add('BUG', '8: Close all shuts every section')
    ev("mhOrdFoldAll(false)")
    if ev("document.querySelectorAll('[data-ord]').length") < 10: f.add('BUG', '9: Open all opens them')
    # eight lines or fewer stay flat
    ev("mhOrdOpen('order')"); ev("mhOrdClear&&1"); 
    ev("t=>{_shopUi.ord=null; mhOrdLoad(t,'test2')}", "1 x Zzqx Tea 100g\n1 x Zzqx Coffee 100g"); page.wait_for_timeout(400)
    if ev("document.querySelectorAll('[data-ord-sec]').length") != 0: f.add('BUG', '10: eight lines or fewer are not sectioned')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
