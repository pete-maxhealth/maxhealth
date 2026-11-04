"""Persona 373: adding a non-nutritional item from the Add to the list card keeps the card where it is on the screen (v3.10.1258).
Pete (4 Nov): "When you add an item to the non nutritional list, focus shifts to the shopping list rather than staying where it was."
The new item lands in My list ABOVE the Add card, so a plain redraw pushed the card down the screen. Covers the shelf Add, the Regular star, typed Add, three in a row,
reload, and that the food side and the My cupboards Low button still behave as before. Invented data; taps are real mouse taps (no scrolling to the target)."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 640}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','list')")
    ev("mhShopOpen()"); page.wait_for_timeout(300)
    for n in ['Zzqx Bin bags', 'Zzqx Cola', 'Zzqx Kitchen roll', 'Zzqx Teabags', 'Zzqx Toilet roll', 'Zzqx Soap']: ev(f"mhStockAddNonFood('{n}')")
    ev("_shopUi.view='list'; _shopUi.addOpen=true; mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    ev("(()=>{const s=mhShopLoad(); ['Zzqx Milk','Zzqx Eggs','Zzqx Bread','Zzqx Butter','Zzqx Cheese','Zzqx Rice','Zzqx Pasta','Zzqx Ham','Zzqx Jam','Zzqx Tea','Zzqx Oil','Zzqx Flour','Zzqx Sugar','Zzqx Salt'].forEach(n=>mhShopSetAdd(s,n,'list','',null,{})); mhShopSave(s); mhShopRender();})()"); page.wait_for_timeout(300)
    ev("mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    ev("document.querySelectorAll('.toast').forEach(t=>t.style.display='none')")
    ev("document.getElementById('mhNfShelf').scrollIntoView({block:'center'})"); page.wait_for_timeout(300)
    PANEL = "(()=>{const e=document.getElementById('mhShopAddPanel'); return e?Math.round(e.getBoundingClientRect().top):null})()"
    def tap(sel):
        bb = page.locator(sel).first.bounding_box(); cx, cy = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
        page.mouse.move(cx, cy); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(450)
    def onlist(n): return ev(f"mhShopLoad().items.some(i=>i.name==='{n}')")
    p0 = ev(PANEL)
    if p0 is None: f.add('BUG', '0: the Add card is not on screen to test with')
    tap('[data-nfshelf="Zzqx Teabags"] button:has-text("Add")')
    if not onlist('Zzqx Teabags'): f.add('BUG', '1: the shelf Add puts the item on the list')
    p1 = ev(PANEL)
    if p1 is None or abs(p1 - p0) > 3: f.add('BUG', f'2: the Add card stays where it was after a shelf Add (was {p0}, now {p1})')
    for n in ['Zzqx Soap', 'Zzqx Cola']:
        tap(f'[data-nfshelf="{n}"] button:has-text("Add")')
    p2 = ev(PANEL)
    if p2 is None or abs(p2 - p0) > 3: f.add('BUG', f'3: three Adds in a row still leave the card in place (was {p0}, now {p2})')
    if not (onlist('Zzqx Soap') and onlist('Zzqx Cola')): f.add('BUG', '3b: all three are on the list')
    tap('[data-nfshelf="Zzqx Bin bags"] button:has-text("Regular")')
    p3 = ev(PANEL)
    if p3 is None or abs(p3 - p0) > 3: f.add('BUG', f'4: the Regular star keeps the card in place (was {p0}, now {p3})')
    if not ev("!!mhShopUsualFind(mhShopLoad(), mhShopKey('Zzqx Bin bags'))"): f.add('BUG', '4b: Regular is set')
    # typed add (non-nutritional)
    page.fill('#mhShopOwn', 'Zzqx Sponges'); page.fill('#mhShopOwnAmount', '3 pack')
    p4a = ev(PANEL); tap('#mhShopAddPanel button:has-text("Add"):not([data-k])')
    if not onlist('Zzqx Sponges'): f.add('BUG', '5: typed Add puts the item on the list')
    p4 = ev(PANEL)
    if p4 is None or abs(p4 - p4a) > 3: f.add('BUG', f'6: typed Add keeps the card in place (was {p4a}, now {p4})')
    # the redraw alone does not throw you up the page
    st = ev("document.getElementById('shopScroll').scrollTop"); ev("mhShopRender()"); page.wait_for_timeout(200)
    st2 = ev("document.getElementById('shopScroll').scrollTop")
    if abs(st - st2) > 3: f.add('BUG', f'7: a plain redraw keeps the scroll position ({st} -> {st2})')
    # reload: everything is still there, and the shelf no longer offers what is on the list
    page.reload(); page.wait_for_timeout(1200); ev("mhShopOpen()"); page.wait_for_timeout(300); ev("_shopUi.addOpen=true; mhShopAddKind('nonfood')"); page.wait_for_timeout(300)
    if not all(onlist(n) for n in ['Zzqx Teabags', 'Zzqx Soap', 'Zzqx Cola', 'Zzqx Sponges']): f.add('BUG', '8: after a reload the items are still on the list')
    shelf = ev("[...document.querySelectorAll('[data-nfshelf]')].map(e=>e.dataset.nfshelf)")
    if 'Zzqx Teabags' in shelf or 'Zzqx Soap' in shelf: f.add('BUG', f'9: items already on the list are not offered again: {shelf}')
    # neighbours: a typed FOOD add still opens its aisle and shows the item (v3.10.1178), and the cupboards Low button still puts an item on the list
    ev("mhShopAddKind('food')"); page.wait_for_timeout(200); page.fill('#mhShopOwn', 'Zzqx Pears'); ev("mhShopAddOwn()"); page.wait_for_timeout(900)
    if not onlist('Zzqx Pears'): f.add('BUG', '10: a typed food add still works')
    ev("mhStockTrack('Zzqx Beans',{base:'g'}); mhStockSetLevel(mhShopKey('Zzqx Beans'),0); mhStockSetReorder(mhShopKey('Zzqx Beans'),900)"); ev("mhStockLowNow(mhShopKey('Zzqx Beans'))"); page.wait_for_timeout(300)
    if not onlist('Zzqx Beans'): f.add('BUG', '11: the cupboards Low button still puts the item on the list')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
