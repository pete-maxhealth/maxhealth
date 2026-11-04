"""Persona 377: the app starts each session on the DEFAULT shop, and new cupboard items use it (v3.10.1262).
Pete (4 Nov): "Things are defaulting to Tesco rather than Asda. We should be able to set our own default." A Default shop picker exists (v3.10.1198) but the last-picked shop was remembered for ever.
Covers: reload after tapping Tesco lands on Asda, adds then go to Asda, the picker still changes the default, viewing a shop in the session still sends adds there (p197), typed non-nutritional into cupboards. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','list'); mhShopOpen()"); page.wait_for_timeout(300)
    ev("(()=>{const s=mhShopLoad(); ['Asda','Tesco'].forEach(n=>{if(!s.shops.includes(n)) s.shops.push(n)}); s.def='Asda'; mhShopSave(s)})()")
    ev("mhShopSetShop('Tesco')"); page.wait_for_timeout(200)
    if ev("JSON.parse(localStorage.getItem(MH_SHOP_KEY)).shop") != 'Tesco': f.add('BUG', '0: set-up: Tesco was the last shop picked')
    shopof = lambda n: ev(f"(mhShopLoad().items.find(i=>i.name==='{n}')||{{}}).shop")
    def add(kind, name, amount=''):
        ev(f"localStorage.setItem('mh_shop_pane','list'); _shopUi.view='list'; _shopUi.addOpen=true; mhShopRender(); mhShopAddKind('{kind}')"); page.wait_for_timeout(250)
        ev(f"document.getElementById('mhShopOwn').value='{name}'; if(document.getElementById('mhShopOwnAmount')) document.getElementById('mhShopOwnAmount').value='{amount}'; mhShopAddOwn()"); page.wait_for_timeout(600)
    # a new session starts on the default shop
    page.reload(); page.wait_for_timeout(1200); ev("localStorage.setItem('mh_shop_pane','list'); mhShopOpen()"); page.wait_for_timeout(300)
    if ev("mhShopLoad().shop") != 'Asda': f.add('BUG', f'1: after reopening the app the shop in use is the default: {ev("mhShopLoad().shop")}')
    add('food', 'Zzqx Pears')
    if shopof('Zzqx Pears') != 'Asda': f.add('BUG', f'2: a typed food goes to the default shop: {shopof("Zzqx Pears")}')
    add('nonfood', 'Zzqx Sponges', '1 pack')
    if shopof('Zzqx Sponges') != 'Asda': f.add('BUG', f'3: a typed non-nutritional goes to the default shop: {shopof("Zzqx Sponges")}')
    # inside the session, the shop you are on still takes what you add (v3.10.1105)
    ev("mhShopSetShop('Tesco')"); add('food', 'Zzqx Plums')
    if shopof('Zzqx Plums') != 'Tesco': f.add('BUG', f'4: while on Tesco, adds go to Tesco: {shopof("Zzqx Plums")}')
    # a new cupboard non-nutritional item uses the default shop, whichever shop is being viewed
    ev("mhStockAddNonFood('Zzqx Bin bags')"); page.wait_for_timeout(300)
    sh = ev("(mhStockLoad().items[mhShopKey('Zzqx Bin bags')]||{}).shop")
    if sh != 'Asda': f.add('BUG', f'5: a new cupboard non-nutritional item is Asda: {sh!r}')
    # the picker changes the default; the next session starts on it
    ev("try{mhStkBack()}catch(e){}; localStorage.setItem('mh_shop_pane','list'); _shopUi.view='list'; mhShopRender()"); page.wait_for_timeout(300)
    if not ev("!!document.querySelector('#mhShopDef select')"): f.add('BUG', '6: the Default shop picker is on the list')
    ev("mhShopDefaultSet('Tesco')"); page.wait_for_timeout(300)
    page.reload(); page.wait_for_timeout(1200); ev("localStorage.setItem('mh_shop_pane','list'); mhShopOpen()"); page.wait_for_timeout(300)
    if ev("mhShopLoad().def") != 'Tesco' or ev("mhShopLoad().shop") != 'Tesco': f.add('BUG', f'7: new default Tesco holds after reopening: {ev("[mhShopLoad().def, mhShopLoad().shop]")}')
    add('food', 'Zzqx Grapes')
    if shopof('Zzqx Grapes') != 'Tesco': f.add('BUG', f'8: adds follow the new default: {shopof("Zzqx Grapes")}')
    if shopof('Zzqx Pears') != 'Asda': f.add('BUG', '9: earlier items keep their own shop')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
