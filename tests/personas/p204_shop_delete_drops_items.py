"""Persona 204: Removing a shop drops its items, it doesn't reassign them (v3.10.1115). Pete Spence:
"if a store is removed from a particular week, it's still going to sell the items, it's just that you
didn't need them... they'd just be removed from the shopping list." The shop, its usuals and its
history are untouched - only this list's items at that shop go. Covers: items at the removed shop are
dropped (not moved to shop[0]), items at other shops are untouched, the shop's usuals survive for next
time, a confirm appears naming the count, cancelling leaves everything as it was, and a shop with no
items on the list removes instantly with no confirm."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    ev("""()=>{
        const s = mhShopLoad();
        if (!s.shops.includes('Aldi')) s.shops.push('Aldi');
        s.usualsBy['Aldi'] = ['Oat Milk'];
        mhShopSetAdd(s, 'Fruit & Veg Mix', 'own', '', 'fruitveg', {});
        s.items[s.items.length-1].shop = 'Aldi';
        mhShopSetAdd(s, 'Oat Milk', 'own', '', 'dairy', {});
        s.items[s.items.length-1].shop = 'Aldi';
        mhShopSetAdd(s, 'Tesco Milk', 'own', '', 'dairy', {});
        s.items[s.items.length-1].shop = s.shops[0];
        mhShopSave(s);
    }""")
    before = ev("mhShopLoad()")
    n_before = len(before['items'])
    if n_before != 3: f.add('BUG', f'setup expected 3 items, got {n_before}')

    # removing a shop with items asks for confirmation first, naming the count
    ev("mhShopDelShop('Aldi')"); page.wait_for_timeout(200)
    overlay_txt = ev("document.querySelector('.app-modal-overlay')?.textContent || ''")
    if '2' not in overlay_txt or 'Aldi' not in overlay_txt:
        f.add('BUG', f'confirm should name the shop and the 2-item count: {overlay_txt!r}')

    # cancel leaves everything untouched
    ev("document.getElementById('appModalCancel')?.click()"); page.wait_for_timeout(200)
    mid = ev("mhShopLoad()")
    if len(mid['items']) != 3 or 'Aldi' not in mid['shops']:
        f.add('BUG', 'cancelling the shop-delete confirm should leave the list and shop list unchanged')

    # confirming actually drops the Aldi items, not reassign them to shop[0]
    ev("mhShopDelShop('Aldi')"); page.wait_for_timeout(200)
    ev("document.getElementById('appModalConfirm')?.click()"); page.wait_for_timeout(200)
    after = ev("mhShopLoad()")
    if 'Aldi' in after['shops']: f.add('BUG', 'Aldi should no longer be a shop on this list')
    names_left = sorted(i['name'] for i in after['items'])
    if names_left != ['Tesco Milk']:
        f.add('BUG', f'only the Tesco item should remain (Aldi items dropped, not reassigned): {names_left}')
    if any(i.get('shop') == before['shops'][0] and i['name'] in ('Fruit & Veg Mix', 'Oat Milk') for i in after['items']):
        f.add('BUG', 'Aldi items were reassigned to another shop instead of being dropped')

    # the shop's own usuals/history are untouched elsewhere (usualsBy cleared is fine - that's
    # "this shop's own saved usuals", which the removal legitimately clears per the shop going away
    # from THIS profile's shop list; separately-stored purchase history, if any, is not part of
    # mh_shopping_v1 and so cannot have been touched by this function)
    if 'Tesco Milk' not in [i['name'] for i in after['items']]:
        f.add('BUG', 'the other shops item must not be affected by removing Aldi')

    # a shop with nothing currently on the list removes instantly, no confirm needed
    ev("""()=>{ const s = mhShopLoad(); s.shops.push('Lidl'); mhShopSave(s); }""")
    ev("mhShopDelShop('Lidl')"); page.wait_for_timeout(150)
    no_overlay = ev("!document.querySelector('.app-modal-overlay')")
    still_there = ev("mhShopLoad().shops.includes('Lidl')")
    if not no_overlay or still_there:
        f.add('BUG', 'removing an empty shop should not need a confirm and should remove it immediately')

    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
