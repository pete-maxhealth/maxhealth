"""Persona 205: Saved shopping lists with a merge-or-replace choice (v3.10.1116). Pete Spence asked for saved/named
lists so a shop's list can be pulled back in after a gap. Covers: saving a shop's items (hidden items left out, ticks not
saved, non-food amount kept); saving over an existing name asks first and cancelling changes nothing; saving the whole list;
using a list when nothing of yours is at its shops just brings it in with no prompt (and re-adds a shop that was removed);
using a list when you already have items at its shops shows the inline choice naming the count; Add what is missing keeps your
items and ticks and adds only the rest; Replace takes only that shop's items off first and never touches other shops; Cancel
changes nothing; rename (a clashing name is refused) and delete (cancel keeps it); the Saved lists button shows its count;
the prompt-driven save path works; and the saved lists are in the backup and come back through a real restore."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.on('dialog', lambda d: d.accept('Prompted Name') if d.type == 'prompt' else d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)

    def lists(): return ev("mhShopListsLoad().lists.map(l=>({id:l.id,name:l.name,items:l.items}))")
    def items(): return ev("mhShopLoad().items.map(i=>({name:i.name,shop:i.shop,checked:i.checked,hidden:i.hidden,nonFood:i.nonFood,amount:i.amount}))")
    def lid(name): return next((l['id'] for l in lists() if l['name'] == name), None)
    def modal_click(which): ev("document.getElementById('%s')?.click()" % which); page.wait_for_timeout(200)
    def has_modal(): return ev("!!document.querySelector('.app-modal-overlay')")

    # ── set up a list across two shops ─────────────────────────────────────────────────────────────
    ev("""()=>{
        const s = mhShopLoad(); s.shops.push('Butchers');
        mhShopSetAdd(s, 'Eggs', 'own', '', 'dairy', {});
        mhShopSetAdd(s, 'Butter', 'own', '', 'dairy', {});
        mhShopSetAdd(s, 'Toilet roll', 'own', '', null, {nonFood: true, amount: '24 pack'});
        mhShopSetAdd(s, 'Hidden thing', 'own', '', 'dairy', {});
        mhShopSetAdd(s, 'Sirloin steak', 'own', '', 'meat', {}); s.items[s.items.length-1].shop = 'Butchers';
        s.items.find(i => i.name === 'Hidden thing').hidden = true;
        s.items.find(i => i.name === 'Eggs').checked = true;
        mhShopSave(s);
    }""")

    # A. saving this shop: hidden left out, ticks not saved, non-food amount kept
    ev("mhShopListSaveNamed('shop','Asda weekly')")
    ls = lists()
    if len(ls) != 1 or ls[0]['name'] != 'Asda weekly': f.add('BUG', f'saving should create one list called Asda weekly: {[l["name"] for l in ls]}')
    else:
        nm = sorted(i['name'] for i in ls[0]['items'])
        if nm != ['Butter', 'Eggs', 'Toilet roll']: f.add('BUG', f'saved list should hold Butter, Eggs, Toilet roll (no hidden item, no other shop): {nm}')
        if any('checked' in i for i in ls[0]['items']): f.add('BUG', 'ticks must not be saved in a saved list')
        tr = next((i for i in ls[0]['items'] if i['name'] == 'Toilet roll'), {})
        if not tr.get('nonFood') or tr.get('amount') != '24 pack': f.add('BUG', f'non-food item and its amount should be kept: {tr}')

    # B. same name (any case) asks first; cancel changes nothing; confirm replaces and keeps the original name
    ev("""()=>{ const s = mhShopLoad(); mhShopSetAdd(s, 'Jam', 'own', '', 'sweet', {}); mhShopSave(s); }""")
    ev("mhShopListSaveNamed('shop','asda WEEKLY')"); page.wait_for_timeout(200)
    if not has_modal(): f.add('BUG', 'saving over an existing name should ask for confirmation')
    modal_click('appModalCancel')
    if len(lists()) != 1 or len(lists()[0]['items']) != 3: f.add('BUG', 'cancelling the replace confirm should leave the saved list as it was')
    ev("mhShopListSaveNamed('shop','asda WEEKLY')"); page.wait_for_timeout(200); modal_click('appModalConfirm')
    ls = lists()
    if len(ls) != 1 or ls[0]['name'] != 'Asda weekly' or len(ls[0]['items']) != 4:
        f.add('BUG', f'confirming should replace in place, keep the original name, and now hold 4 items: {[(l["name"], len(l["items"])) for l in ls]}')

    # C. save the whole list; and a Butchers-only list
    ev("mhShopListSaveNamed('all','Everything')")
    whole = next((l for l in lists() if l['name'] == 'Everything'), None)
    if not whole or sorted({i['shop'] for i in whole['items']}) != ['Asda', 'Butchers']:
        f.add('BUG', f'whole-list save should include every shop: {whole and sorted({i["shop"] for i in whole["items"]})}')
    ev("()=>{ const s = mhShopLoad(); mhShopSwitch(s, 'Butchers'); mhShopSave(s); }")
    ev("mhShopListSaveNamed('shop','Butchers only')")
    ev("()=>{ const s = mhShopLoad(); mhShopSwitch(s, 'Asda'); mhShopSave(s); }")
    if len(lists()) != 3: f.add('BUG', f'expected 3 saved lists by now, got {len(lists())}')

    # D. using a list with nothing of yours at its shop brings it straight in (and re-adds a removed shop)
    ev("mhShopDelShop('Butchers')"); page.wait_for_timeout(200); modal_click('appModalConfirm')
    if 'Butchers' in ev("mhShopLoad().shops"): f.add('BUG', 'setup: Butchers should have been removed')
    ev("mhShopView('lists')"); ev("id=>mhShopListUse(id)", lid('Butchers only')); page.wait_for_timeout(200)
    if has_modal() or ev("!!document.getElementById('mhShopListChoice')"): f.add('BUG', 'no merge/replace prompt should appear when nothing of yours is at that list\'s shops')
    if 'Butchers' not in ev("mhShopLoad().shops"): f.add('BUG', 'applying a saved list should bring its shop back')
    if not any(i['name'] == 'Sirloin steak' and i['shop'] == 'Butchers' for i in items()): f.add('BUG', 'Sirloin steak should be back on the list under Butchers')

    # E. merge: keeps what you have (and its tick), adds only what is missing, leaves other shops alone
    ev("""()=>{ const s = mhShopLoad(); s.items = s.items.filter(i => i.name !== 'Butter'); mhShopSetAdd(s, 'Cheese', 'own', '', 'dairy', {}); mhShopSave(s); }""")
    ev("mhShopView('lists')"); ev("id=>mhShopListUse(id)", lid('Asda weekly')); page.wait_for_timeout(200)
    choice = ev("document.getElementById('mhShopListChoice')?.textContent || ''")
    if not choice: f.add('BUG', 'using a list when you already have items at its shop should show the inline merge/replace choice')
    elif 'Add what is missing' not in choice or 'Replace' not in choice: f.add('BUG', f'choice should offer Add what is missing and Replace: {choice[:160]!r}')
    asda_now = len([i for i in items() if i['shop'] == 'Asda'])
    if str(asda_now) not in choice: f.add('BUG', f'choice should name how many items you already have ({asda_now}): {choice[:160]!r}')
    res = ev("id=>mhShopListApply(id,'merge')", lid('Asda weekly')); page.wait_for_timeout(200)
    it = items(); names = [i['name'] for i in it]
    if res['added'] != 1 or res['there'] != 3: f.add('BUG', f'merge should add just Butter and find the other 3 already there: {res}')
    if len(names) != len(set(n.lower() for n in names)): f.add('BUG', f'merge must never duplicate an item: {names}')
    if not next((i for i in it if i['name'] == 'Eggs'), {}).get('checked'): f.add('BUG', 'merge must leave an existing item (and its tick) exactly as it was')
    if 'Cheese' not in names: f.add('BUG', 'merge must keep items you already had that are not in the saved list')
    if 'Sirloin steak' not in names: f.add('BUG', 'merge must not touch other shops')

    # F. replace: takes that shop's items off first, never touches other shops
    ev("mhShopView('lists')"); ev("id=>mhShopListUse(id)", lid('Asda weekly'))
    res = ev("id=>mhShopListApply(id,'replace')", lid('Asda weekly')); page.wait_for_timeout(200)
    it = items(); asda = sorted(i['name'] for i in it if i['shop'] == 'Asda')
    if asda != ['Butter', 'Eggs', 'Jam', 'Toilet roll']: f.add('BUG', f'replace should leave exactly the saved list at that shop (Cheese gone): {asda}')
    # Asda had Eggs, Toilet roll, Jam, Cheese, Butter and the hidden item = 6 off; the saved list brings 4 on
    if res['removed'] != 6 or res['added'] != 4: f.add('BUG', f'replace should take 6 off (hidden one included) and put 4 on: {res}')
    if next((i for i in it if i['name'] == 'Eggs'), {}).get('checked'): f.add('BUG', 'a replaced item comes in fresh, unticked')
    if not any(i['name'] == 'Sirloin steak' and i['shop'] == 'Butchers' for i in it): f.add('BUG', 'replace must not touch other shops')

    # G. cancel changes nothing
    before = items()
    ev("mhShopView('lists')"); ev("id=>mhShopListUse(id)", lid('Asda weekly')); ev("mhShopListCancelUse()")
    if items() != before or ev("!!document.getElementById('mhShopListChoice')"): f.add('BUG', 'Cancel should close the choice and change nothing')

    # H. rename (a clashing name is refused) and delete (cancel keeps it)
    if not ev("id=>mhShopListRenameTo(id,'Asda weekly shop')", lid('Asda weekly')): f.add('BUG', 'rename to a free name should work')
    if ev("id=>mhShopListRenameTo(id,'everything')", lid('Asda weekly shop')): f.add('BUG', 'rename to another list\'s name (any case) should be refused')
    if 'Asda weekly shop' not in [l['name'] for l in lists()]: f.add('BUG', 'a refused rename must leave the name as it was')
    ev("id=>mhShopListDelete(id)", lid('Butchers only')); page.wait_for_timeout(200); modal_click('appModalCancel')
    if 'Butchers only' not in [l['name'] for l in lists()]: f.add('BUG', 'cancelling delete should keep the saved list')
    ev("id=>mhShopListDelete(id)", lid('Butchers only')); page.wait_for_timeout(200); modal_click('appModalConfirm')
    if 'Butchers only' in [l['name'] for l in lists()]: f.add('BUG', 'confirming delete should remove the saved list')
    if len(items()) != len(before): f.add('BUG', 'deleting a saved list must not touch the shopping list')

    # I. the button shows its count; the view lists rows; the prompt-driven save works
    ev("_shopUi.addOpen = true; mhShopView('list')"); page.wait_for_timeout(200)
    txt = ev("document.getElementById('mhShopAddPanel')?.textContent || ''")
    n_saved = len(lists())
    if f'Saved lists ({n_saved})' not in txt: f.add('BUG', f'Add items panel should show a Saved lists ({n_saved}) button: {txt[-200:]!r}')
    ev("mhShopView('lists')"); page.wait_for_timeout(200)
    rows = ev("document.querySelectorAll('#mhShopPane [data-list]').length")
    if rows != n_saved or not ev("!!document.getElementById('mhShopListSaveBar')"): f.add('BUG', f'lists view should show {n_saved} rows and the save bar, saw {rows}')
    ev("mhShopListSaveAs('shop')"); page.wait_for_timeout(300)
    if 'Prompted Name' not in [l['name'] for l in lists()]: f.add('BUG', 'the prompt-driven Save should create a list with the typed name')

    # J. the saved lists are in the backup and come back through a real restore
    sk = ev("_BACKUP_SETTINGS_SKIP.test('mh_shopping_lists_v1')")
    if sk: f.add('BUG', 'the saved-lists key must not match the backup skip pattern')
    raw = ev("localStorage.getItem('mh_shopping_lists_v1')")
    payload = ev("buildFullBackupPayload()")
    if (payload.get('settings') or {}).get('mh_shopping_lists_v1') != raw: f.add('BUG', 'saved lists must be in the full backup payload')
    ev("localStorage.removeItem('mh_shopping_lists_v1')")
    if lists(): f.add('BUG', 'setup: lists should be gone before the restore')
    ev("p=>mhApplyBackupObject(p,'test')", payload)
    if ev("localStorage.getItem('mh_shopping_lists_v1')") != raw: f.add('BUG', 'a restore must bring the saved lists back exactly')

    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
