"""Persona 258: a product found by barcode or Open Food Facts can be kept in the cupboards (v3.10.1154). The pack size and serving come from the product's own data
(never guessed); how much you have and the reorder level stay empty and show as "needs details". Off when stock is switched off; no overwrite of an item you already keep. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    q = lambda s: ev("mhProductQty(%r)" % s)
    cases = {'400 g': ('g', 400), '1.5 L': ('ml', 1500), '330 ml': ('ml', 330), '2 kg': ('g', 2000), '75 cl': ('ml', 750), '1,5 l': ('ml', 1500)}
    for k, (b, n) in cases.items():
        r = q(k)
        if not r or r['base'] != b or r['pack'] != n: f.add('BUG', f'1: {k!r} reads as {b} {n}: {r}')
    for k in ['6 x 60g', '', 'about a pound', '0 g', '12 slices']:
        if q(k) is not None: f.add('BUG', f'2: {k!r} is not guessed at: {q(k)}')
    P = "{name:'Zzqx Wrap',brand:'Zzqhey',kcal:200,prot:5,carb:30,fat:5,qty:'400 g',servingQty:60}"
    ev("_selectedFoodItem=%s; mhProductCupboardRow(true)" % P)
    if ev("getComputedStyle(document.getElementById('foodAmountCupboardRow')).display") != 'none': f.add('BUG', '3: with stock off the tick is hidden')
    ev("mhStockTrack('Zzqx Seed',{base:'g'})")
    ev("_selectedFoodItem=%s; mhProductCupboardRow(true)" % P)
    if ev("getComputedStyle(document.getElementById('foodAmountCupboardRow')).display") != 'flex' or not ev("document.getElementById('foodAmountCupboard').checked"): f.add('BUG', '4: a barcode scan offers it, ticked')
    ev("_selectedFoodItem=%s; mhProductCupboardRow(false)" % P)
    if ev("document.getElementById('foodAmountCupboard').checked"): f.add('BUG', '5: a name search offers it, unticked')
    # ticked + Save to library keeps it
    ev("document.getElementById('foodAmountCupboard').checked=true; saveFoodToLibraryFromPanel()"); page.wait_for_timeout(300)
    it = ev("mhStockLoad().items[mhShopKey('Zzqx Wrap (Zzqhey)')]")
    if not it or it['base'] != 'g' or it['pack'] != 400 or it['serving'] != 60: f.add('BUG', f'6: kept with the product\'s own pack and serving: {it}')
    if it and (it['level'] is not None or it['reorder'] is not None): f.add('BUG', f'7: how much you have and the reorder level are not guessed: {it}')
    if it and not ev("mhStockGaps(mhStockLoad().items[mhShopKey('Zzqx Wrap (Zzqhey)')]).length"): f.add('BUG', '8: it shows as needs details')
    # unticked keeps nothing; second product, via Log
    ev("_selectedFoodItem={name:'Zzqx Soup',brand:'',kcal:50,prot:2,carb:5,fat:1,qty:'1 L'}; mhProductCupboardRow(false); document.getElementById('foodAmountGrams').value=100; logFoodFromDatabase()"); page.wait_for_timeout(300)
    if ev("!!mhStockLoad().items[mhShopKey('Zzqx Soup')]"): f.add('BUG', '9: unticked keeps nothing')
    ev("_selectedFoodItem={name:'Zzqx Soup',brand:'',kcal:50,prot:2,carb:5,fat:1,qty:'1 L'}; mhProductCupboardRow(false); document.getElementById('foodAmountCupboard').checked=true; document.getElementById('foodAmountGrams').value=100; logFoodFromDatabase()"); page.wait_for_timeout(300)
    s2 = ev("mhStockLoad().items[mhShopKey('Zzqx Soup')]")
    if s2 and s2['serving'] is not None: f.add('BUG', f'10b: no serving in the product data, so none is invented: {s2}')
    if not s2 or s2['base'] != 'ml' or s2['pack'] != 1000: f.add('BUG', f'10: kept when logging, litres read as ml: {s2}')
    # already kept: not overwritten, row says so
    ev("(()=>{const o=mhStockLoad(); o.items[mhShopKey('Zzqx Wrap (Zzqhey)')].pack=123; mhStockSave(o);})()")
    ev("_selectedFoodItem=%s; mhProductCupboardRow(true)" % P)
    if 'Already' not in ev("document.getElementById('foodAmountCupboardTxt').textContent") or ev("document.getElementById('foodAmountCupboard').checked"): f.add('BUG', '11: an item you already keep says so')
    ev("mhStockFromProduct(%s)" % P)
    if ev("mhStockLoad().items[mhShopKey('Zzqx Wrap (Zzqhey)')].pack") != 123: f.add('BUG', '12: what you already keep is never overwritten')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
