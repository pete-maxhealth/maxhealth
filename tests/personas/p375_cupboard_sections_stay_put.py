"""Persona 375: opening a section in My cupboards and then changing the shop keeps the sections (v3.10.1260).
Pete (4 Nov): "if you open one of the sub categories and do something else like change the shop, all sections open up." Seen with the Non-nutritional section.
Cause: the sections only drew when the shown list had more than 8 items, so a shop with few items flattened everything into one open list.
Covers: shop filter on/off, No shop, hiding a shop-less filter, tab switch and back, open state remembered, reload, the search flat list, and a small cupboard staying flat. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    foods = [('Chicken Breast', 'Asda'), ('Beef Mince', 'Asda'), ('Pork Chops', 'Asda'), ('Milk', 'Asda'), ('Cheddar', 'Asda'), ('Eggs', 'Asda'), ('Butter', 'Asda'), ('Yoghurt', 'Asda'), ('Apples', 'Asda'), ('Bananas', 'Asda'), ('Carrots', 'Asda'), ('Rice', 'Asda'), ('Pasta', 'Tesco'), ('Flour', 'Tesco')]
    for n, sh in foods: ev(f"mhStockTrack('{n}',{{base:'g',shop:'{sh}'}}); mhStockSetLevel(mhShopKey('{n}'),500)")
    ev("(()=>{const s=mhShopLoad(); ['Asda','Tesco','Lidl'].forEach(n=>{if(!s.shops.includes(n)) s.shops.push(n)}); mhShopSave(s)})()")
    for n, sh in [('Zzqx Bin bags', 'Asda'), ('Zzqx Foil', 'Tesco'), ('Zzqx Soap', 'Asda')]:
        ev(f"mhStockAddNonFood('{n}')"); ev(f"(()=>{{const o=mhStockLoad(); o.items[mhShopKey('{n}')].shop='{sh}'; mhStockSave(o)}})()")
    ev("try{mhStkBack()}catch(e){}; localStorage.setItem('mh_shop_pane','stock'); _shopUi.view='list'; mhCbState().fold={}; mhCbTab('all'); mhCbShop('')"); page.wait_for_timeout(400)
    NF = ev("MH_SHOP_WALK.length+1")
    AIS = "[...document.querySelectorAll('[data-cb-aisle]')].map(e=>e.dataset.cbAisle+':'+(mhCbIsShut('a'+e.dataset.cbAisle)?'shut':'open'))"
    ROWS = "document.querySelectorAll('#stockctlCard [data-stock]').length"
    def go(js): ev(js); page.wait_for_timeout(300)
    a0 = ev(AIS)
    if len(a0) < 3 or ev(ROWS) != 0 and any(x.endswith('open') for x in a0): f.add('BUG', f'0: sections start closed on the All tab: {a0}')
    go(f"mhCbFold('a{NF}')")
    if f"{NF}:open" not in ev(AIS) or ev(ROWS) != 3: f.add('BUG', f'1: opening Non-nutritional shows its 3 items: {ev(AIS)} rows={ev(ROWS)}')
    for shop in ['Tesco', 'Lidl', '__none', 'Asda', '']:
        go(f"mhCbShop('{shop}')"); a = ev(AIS); rows = ev(ROWS)
        n_nf = ev(f"Object.values(mhStockLoad().items).filter(i=>i.nonFood && ({'true' if shop=='' else ('!i.shop' if shop=='__none' else 'i.shop===' + repr(shop))})).length")
        if shop in ('Lidl', '__none'):
            if a: f.add('BUG', f'2[{shop}]: a shop with nothing in it shows no sections: {a}')
            continue
        if not a: f.add('BUG', f'2[{shop}]: the sections are still there after choosing the shop (got a flat list, {rows} rows)')
        elif any(x.endswith('open') for x in a if not x.startswith(f'{NF}:')): f.add('BUG', f'3[{shop}]: other sections stay closed: {a}')
        if a and n_nf and f'{NF}:open' not in a: f.add('BUG', f'4[{shop}]: Non-nutritional stays open: {a}')
        if a and rows != n_nf: f.add('BUG', f'5[{shop}]: only the open section shows its rows ({rows} rows, expected {n_nf})')
    # tab switch and back keeps what you opened
    go("mhCbTab('cupboard')"); go("mhCbTab('all')")
    a = ev(AIS)
    if f"{NF}:open" not in a or any(x.endswith('open') for x in a if not x.startswith(f'{NF}:')): f.add('BUG', f'6: tab switch and back keeps only Non-nutritional open: {a}')
    # reload keeps it
    page.reload(); page.wait_for_timeout(1200); ev("mhShopOpen()"); page.wait_for_timeout(400)
    a = ev(AIS)
    if a and (f"{NF}:open" not in a or any(x.endswith('open') for x in a if not x.startswith(f'{NF}:'))): f.add('BUG', f'7: after a reload the same section is open and the rest shut: {a}')
    # search is still a flat list, and a small cupboard is still flat
    go("mhCbQ('chicken')")
    if ev(AIS): f.add('BUG', '8: a search shows a flat list as before')
    go("mhCbQ('')")
    go("(()=>{const o=mhStockLoad(); Object.keys(o.items).slice(8).forEach(k=>delete o.items[k]); mhStockSave(o); mhShopRender()})()")
    if ev(AIS): f.add('BUG', f'9: eight items or fewer stay a flat list: {ev(AIS)}')
    if errs: f.add('BUG', f'JS errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
