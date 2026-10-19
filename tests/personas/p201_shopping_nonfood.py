"""Persona 201: Non-food shopping items (pet food, toilet roll, cleaning supplies). Pete Spence: "add non food
items... excluded from any search, statistics etc... We'd also need to add an amount like toilet roll 24 pack
or 2 bottles of whole milk." Covers: the Food/Not food toggle on manual add, the amount field, a non-food item
never leaking into the food library, Quick list, My foods or recipe search, its own always-last "Not food"
section with the same fold/tick-all as a real aisle, the amount showing on the row and in Copy list."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; saveState()")
    ev("saveLibrary([{id:'t1',name:'Whole Milk',kcal:60,protein:3,carbs:5,fat:3,useCount:5}])")
    ev("mhShopOpen()"); page.wait_for_timeout(300)

    # default is Food; switching to Not food shows the amount field and changes the placeholder
    if ev("_shopUi.addKind") == 'nonfood': f.add('BUG', 'should default to Food')
    ev("mhShopAddKind('nonfood')"); page.wait_for_timeout(100)
    if not ev("!!document.getElementById('mhShopOwnAmount')"): f.add('BUG', 'amount field should appear for Not food')

    # add a non-food item with an amount
    ev("document.getElementById('mhShopOwn').value='Toilet roll'; document.getElementById('mhShopOwnAmount').value='24 pack'; mhShopAddOwn()")
    item = ev("mhShopLoad().items.find(i=>i.name==='Toilet roll')")
    if not item or not item.get('nonFood') or item.get('amount') != '24 pack' or item.get('cat') != 'nonfood':
        f.add('BUG', f'non-food item not saved correctly: {item}')

    # the row shows the amount, and it sits in its own "Not food" section, not lumped into "Other"
    row_txt = ev("document.querySelector('[data-item=\"Toilet roll\"]')?.textContent || ''")
    if '24 pack' not in row_txt: f.add('BUG', f'amount not shown on the row: {row_txt!r}')
    secs = ev("[...document.querySelectorAll('.mh-aisle span')].map(e=>e.textContent)")
    if not any('Not food' in s for s in secs): f.add('BUG', f'no "Not food" section header found: {secs}')

    # a non-food item must never show up as a food suggestion anywhere
    known = ev("mhShopKnown().map(x=>x.name)")
    if 'Toilet roll' in known: f.add('BUG', 'non-food item leaked into mhShopKnown (My foods / recipe search)')
    ranked = ev("mhShopRanked().map(x=>x.name)")
    if 'Toilet roll' in ranked: f.add('BUG', 'non-food item leaked into mhShopRanked (Quick list)')
    if 'Toilet roll' in ev("mhShopLoad().recent"): f.add('BUG', 'non-food item should not feed "recently added" suggestions')

    # adding a food item by the same flow (Food selected) behaves exactly as before - no amount, real category
    ev("_shopUi.addOpen=true; mhShopAddKind('food')")
    ev("document.getElementById('mhShopOwn').value='Whole Milk'; mhShopAddOwn()")
    milk = ev("mhShopLoad().items.find(i=>i.name==='Whole Milk')")
    if not milk or milk.get('nonFood') or milk.get('amount') or milk.get('cat') == 'nonfood':
        f.add('BUG', f'a normal food item was affected by the Not food toggle: {milk}')

    # tick-all on the Not food section works the same as any other aisle
    ev("""()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Cat food','own','',null,{nonFood:true,amount:'1 tin'}); mhShopSave(s);}""")
    sec_idx = ev("mhShopSection('nonfood')")
    ev(f"mhShopTickSection({sec_idx})")
    checked = ev("mhShopLoad().items.filter(i=>i.nonFood).every(i=>i.checked)")
    if not checked: f.add('BUG', 'tick-all on the Not food section did not tick its items')

    # Copy list includes the amount
    ev("""()=>{const s=mhShopLoad(); s.items.forEach(i=>i.checked=false); mhShopSave(s);}""")
    ev("""window.__copied=null; navigator.clipboard.writeText=t=>{window.__copied=t; return Promise.resolve();}; mhShopCopy();""")
    page.wait_for_timeout(100)
    copied = ev("window.__copied") or ''
    if 'Toilet roll (24 pack)' not in copied: f.add('BUG', f'copied list missing the amount: {copied!r}')

    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
