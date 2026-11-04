"""Persona 378: open and shut sections in the shopping list and My cupboards stay exactly as you left them, whatever you do next (v3.10.1263).
Pete (4 Nov): "Wherever you leave the focus when you update whatever it is you're doing, that state should stay for collapsed sub sections the same way as hide/show for the rest of the app."
Covers: adding to the list (typed food, typed non-nutritional, cupboard Low button), ticking, removing, switching shop and tab in the cupboards, editing a food and coming back, adding a cupboard non-food, reload. Invented data."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','list'); mhShopOpen()"); page.wait_for_timeout(300)
    ev("""(()=>{const s=mhShopLoad(); ['Asda','Tesco'].forEach(n=>{if(!s.shops.includes(n)) s.shops.push(n)}); s.def='Asda'; s.shop='Asda';
      [['Milk','Asda'],['Apples','Asda'],['Chicken','Asda'],['Rice','Asda'],['Cheddar','Tesco'],['Bananas','Tesco']].forEach(([n,sh])=>{mhShopSetAdd(s,n,'own','',null,{}); s.items[s.items.length-1].shop=sh}); mhShopSave(s)})()""")
    foods = [('Chicken Breast','Asda'),('Beef Mince','Asda'),('Pork Chops','Asda'),('Milk','Asda'),('Cheddar','Tesco'),('Eggs','Asda'),('Butter','Asda'),('Yoghurt','Asda'),('Apples','Tesco'),('Bananas','Asda'),('Carrots','Asda'),('Rice','Asda')]
    for n, sh in foods: ev(f"mhStockTrack('{n}',{{base:'g',shop:'{sh}'}}); mhStockSetLevel(mhShopKey('{n}'),500)")
    ev("_shopUi.view='list'; _shopUi.fold={}; mhCbState().fold={}; mhShopRender()"); page.wait_for_timeout(300)
    # ---- the shopping list
    LS = "JSON.stringify([...document.querySelectorAll('#mhShopPane .mh-aisle')].map(e=>e.innerText.replace(/\\s+/g,' ').trim().slice(0,22)))"
    def lst(): return ev(LS)
    ev("mhShopFold('m0_2')"); page.wait_for_timeout(200)   # open Dairy & Eggs under Asda
    base = lst(); fold0 = ev("JSON.stringify(_shopUi.fold)")
    if '▾' not in base: f.add('BUG', f'0: set-up: one list aisle is open: {base}')
    def add(kind, name, amount=''):
        ev(f"localStorage.setItem('mh_shop_pane','list'); _shopUi.view='list'; _shopUi.addOpen=true; mhShopRender(); mhShopAddKind('{kind}')"); page.wait_for_timeout(200)
        ev(f"document.getElementById('mhShopOwn').value='{name}'; if(document.getElementById('mhShopOwnAmount')) document.getElementById('mhShopOwnAmount').value='{amount}'; mhShopAddOwn()"); page.wait_for_timeout(500)
    add('food', 'Zzqx Pears')
    if ev("JSON.stringify(_shopUi.fold)") != fold0: f.add('BUG', f'1: a typed food add leaves every aisle as it was: {ev("JSON.stringify(_shopUi.fold)")}')
    if not ev("/Added Zzqx Pears to your Asda list \\(Fruit/.test(document.getElementById('mhShopPane').innerText)"): f.add('BUG', '1b: the message still says where it went')
    add('nonfood', 'Zzqx Sponges', '1 pack')
    if ev("JSON.stringify(_shopUi.fold)") != fold0: f.add('BUG', '2: a typed non-nutritional add leaves every aisle as it was')
    add('food', 'Zzqx Pears')   # again: already on the list
    if ev("JSON.stringify(_shopUi.fold)") != fold0: f.add('BUG', '3: adding something already there leaves the aisles alone')
    it = ev("mhShopLoad().items.find(i=>i.name==='Zzqx Pears').id")
    ev(f"mhShopToggle('{it}')"); page.wait_for_timeout(200)
    ev(f"mhShopRemove('{it}')"); page.wait_for_timeout(200)
    if ev("JSON.stringify(_shopUi.fold)") != fold0: f.add('BUG', '4: ticking and removing an item leave the aisles alone')
    ev("mhShopSetShop('Tesco'); mhShopSetShop('Asda')"); page.wait_for_timeout(200)
    if ev("JSON.stringify(_shopUi.fold)") != fold0: f.add('BUG', '5: changing shop leaves the aisles alone')
    # ---- My cupboards
    ev("localStorage.setItem('mh_shop_pane','stock'); _shopUi.view='list'; mhCbState().fold={}; mhCbTab('all'); mhCbShop(''); mhShopRender()"); page.wait_for_timeout(300)
    AIS = "JSON.stringify([...document.querySelectorAll('[data-cb-aisle]')].map(e=>e.dataset.cbAisle+':'+(mhCbIsShut('a'+e.dataset.cbAisle)?'shut':'open')))"
    a0 = json.loads(ev(AIS))
    if not a0 or any(x.endswith('open') for x in a0): f.add('BUG', f'6: aisles start shut: {a0}')
    first = a0[0].split(':')[0] if a0 else '0'
    ev(f"mhCbFold('a{first}')"); page.wait_for_timeout(200)
    want = {x.split(':')[0]: x.split(':')[1] for x in json.loads(ev(AIS))}
    def same(label):
        got = {x.split(':')[0]: x.split(':')[1] for x in json.loads(ev(AIS))}
        for k, v in got.items():
            if k in want and want[k] != v: f.add('BUG', f'{label}: aisle {k} was {want[k]} and is now {v}')
    for tab in ['cupboard', 'low', 'all']:
        ev(f"mhCbTab('{tab}')"); page.wait_for_timeout(200)
        got = json.loads(ev(AIS))
        for x in got:
            k, v = x.split(':')
            if k in want and want[k] != v: f.add('BUG', f'7[{tab}]: aisle {k} keeps its state when you change tab: {got}')
    ev("mhCbShop('Tesco')"); page.wait_for_timeout(200); same('8: change shop'); ev("mhCbShop('')"); page.wait_for_timeout(200)
    # edit a food and come back
    k = ev("mhShopKey('Beef Mince')"); tab0 = ev("[mhCbState().tab, mhCbState().shop]")
    ev(f"mhStockEditView('{k}')"); page.wait_for_timeout(300); ev("mhStkBack()"); page.wait_for_timeout(500)
    same('9: edit a food and come back')
    if ev("[mhCbState().tab, mhCbState().shop]") != tab0: f.add('BUG', '10: coming back keeps the tab and shop filter')
    ev("mhStockAddNonFood('Zzqx Bin bags')"); page.wait_for_timeout(300); ev("mhStkBack()"); page.wait_for_timeout(500)
    same('11: add a cupboard non-nutritional item')
    ev("mhStockLowNow(mhShopKey('Rice'),1)"); page.wait_for_timeout(300); same('12: Low button')
    page.reload(); page.wait_for_timeout(1200); ev("localStorage.setItem('mh_shop_pane','stock'); mhShopOpen()"); page.wait_for_timeout(400)
    same('13: after a reload')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
