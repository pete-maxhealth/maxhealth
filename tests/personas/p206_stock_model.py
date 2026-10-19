"""Persona 206: Stock control model (v3.10.1118). Pete Spence: a packet of whey might be 30 servings at 25 g, the reorder level
might be 5 servings, and "2 portions" or "25 g" must both work. Covers: either-unit entry (g, kg, ml, l, each, servings, portions,
packs) giving the same base amount; never guessing (a bare number needs a unit unless counted each; servings need a serving size;
packs need a pack size; grams and ml never convert); display in both forms; a stock-take freezing the past; using and reversing
stock (exactly, including when it was clamped at zero, and never twice); the reorder sweep (once per low spell, under the right
shop, waiting when that shop is not on this trip, an item already on the list is not duplicated); changing the counting unit
clears amounts; untracking; old ledger lines pruned; and the stock key is in the backup and comes back through a real restore."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    def parse(s, it): return ev("([s,i])=>mhStockParse(s,i)", [s, it])
    whey = {'base': 'g', 'pack': 750, 'serving': 25}; cream = {'base': 'ml', 'pack': 300, 'serving': None}; eggs = {'base': 'each', 'pack': 6, 'serving': None}
    def ok(s, it, want, label):
        r = parse(s, it)
        if not r.get('ok') or abs(r['base'] - want) > 1e-6: f.add('BUG', f'{label}: {s!r} should be {want}, got {r}')
    def bad(s, it, code, label):
        r = parse(s, it)
        if r.get('ok') or r.get('code') != code: f.add('BUG', f'{label}: {s!r} should be refused as {code!r}, got {r}')

    # A. either form means the same thing
    ok('125 g', whey, 125, 'grams'); ok('5 servings', whey, 125, 'servings'); ok('2 portions', whey, 50, 'portions'); ok('1 serving', whey, 25, 'one serving')
    ok('0.5 kg', whey, 500, 'kg'); ok('1 pack', whey, 750, 'pack'); ok('2 packs', whey, 1500, 'packs'); ok('50g', whey, 50, 'no space')
    ok('0.25 l', cream, 250, 'litres'); ok('250 ml', cream, 250, 'ml'); ok('1 pack', cream, 300, 'cream pack')
    ok('6', eggs, 6, 'bare number is fine for each'); ok('6 each', eggs, 6, 'each'); ok('2 packs', eggs, 12, 'packs of each')
    if parse('2 servings', whey)['base'] != parse('50 g', whey)['base']: f.add('BUG', '2 servings and 50 g must be the same amount')
    # B. never guess
    bad('5', whey, 'needs-unit', 'bare number on grams'); bad('5', cream, 'needs-unit', 'bare number on ml')
    bad('5 ml', whey, 'mismatch', 'ml on a grams item'); bad('5 g', cream, 'mismatch', 'grams on an ml item'); bad('5 g', eggs, 'mismatch', 'grams on each')
    bad('3 servings', cream, 'needs-serving', 'servings without a serving size'); bad('1 pack', {'base': 'g', 'pack': None, 'serving': 25}, 'needs-pack', 'packs without a pack size')
    bad('abc', whey, 'format', 'rubbish'); bad('5 flurbs', whey, 'unit', 'unknown unit'); bad('', whey, 'format', 'empty'); bad('-5 g', whey, 'format', 'negative')
    # C. shown both ways
    fm = lambda it, b: ev("([i,b])=>mhStockFmt(i,b)", [it, b])
    if fm(whey, 125) != '125 g (5 servings)': f.add('BUG', f'display should be both forms: {fm(whey, 125)!r}')
    if fm(whey, 25) != '25 g (1 serving)': f.add('BUG', f'singular serving: {fm(whey, 25)!r}')
    if fm(cream, 250) != '250 ml': f.add('BUG', f'no serving size means no servings shown: {fm(cream, 250)!r}')
    if fm(eggs, 6) != '6' or fm(whey, None) != 'not set': f.add('BUG', f'each and unknown display: {fm(eggs, 6)!r} {fm(whey, None)!r}')

    # D. tracking, stock-take, using and reversing
    k = ev("mhStockTrack('Whey protein', {base:'g', pack:750, serving:25, shop:'Asda'}).key")
    lvl = lambda: ev("(k)=>mhStockLoad().items[k].level", k)
    ledger = lambda: ev("(k)=>mhStockLoad().ledger.filter(l=>l.k===k).length", k)
    if ev("(k)=>mhStockAdjust(k,-25,'log','e0')", k): f.add('BUG', 'adjusting an item whose amount is not set must do nothing')
    ev("(k)=>mhStockSetLevel(k,750)", k)
    ev("(k)=>mhStockAdjust(k,-25,'log','e1')", k)
    if lvl() != 725: f.add('BUG', f'using 25 g from 750 should leave 725: {lvl()}')
    if ev("(k)=>mhStockReverse('e1')", k) != 1 or lvl() != 750: f.add('BUG', f'deleting the entry should put the 25 g back: {lvl()}')
    if ev("()=>mhStockReverse('e1')") != 0 or lvl() != 750: f.add('BUG', 'reversing the same entry twice must not add stock twice')
    ev("(k)=>mhStockSetLevel(k,20)", k); ev("(k)=>mhStockAdjust(k,-25,'log','e2')", k)
    if lvl() != 0: f.add('BUG', f'stock never goes below zero: {lvl()}')
    ev("()=>mhStockReverse('e2')")
    if lvl() != 20: f.add('BUG', f'reversing a clamped use must restore exactly what was taken (20), got {lvl()}')
    # a stock-take freezes the past
    ev("(k)=>mhStockSetLevel(k,750)", k); ev("(k)=>mhStockAdjust(k,-25,'log','e3')", k)
    ev("(k)=>mhStockSetLevel(k,1000)", k)
    if ledger() != 0: f.add('BUG', 'a stock-take should drop the older ledger lines for that item')
    if ev("()=>mhStockReverse('e3')") != 0 or lvl() != 1000: f.add('BUG', f'an entry from before a stock-take must not change stock any more: {lvl()}')
    # editing an entry = reverse then apply the new amount
    ev("(k)=>mhStockAdjust(k,-25,'log','e4')", k); ev("()=>mhStockReverse('e4')"); ev("(k)=>mhStockAdjust(k,-50,'log','e4')", k)
    if lvl() != 950: f.add('BUG', f'editing 25 g to 50 g should leave 950: {lvl()}')
    # old lines are pruned
    ev("""(k)=>{ const o = mhStockLoad(); o.ledger.push({k, d:-5, t: Date.now() - 61*86400000, s:'log', e:'old'}); mhStockSave(o); }""", k)
    if ev("()=>mhStockLoad().ledger.some(l=>l.e==='old')"): f.add('BUG', 'ledger lines older than 60 days should be pruned')

    # E. the reorder sweep
    ev("(k)=>{ mhStockSetLevel(k,150); mhStockSetReorder(k,125); }", k)
    on_list = lambda key: ev("(key)=>mhShopLoad().items.filter(i=>i.key===key).map(i=>({shop:i.shop,src:i.src,from:i.from}))", key)
    ev("(k)=>mhStockAdjust(k,-25,'log','e5')", k)      # 125 = at the reorder level
    got = on_list(k)
    if len(got) != 1 or got[0]['shop'] != 'Asda' or got[0]['src'] != 'stock' or got[0]['from'] != 'running low':
        f.add('BUG', f'running low should add it once under its shop, tagged running low: {got}')
    ev("(k)=>mhStockAdjust(k,-25,'log','e6')", k)
    if len(on_list(k)) != 1: f.add('BUG', 'a second use while still low must not add it again')
    ev("(k)=>{ const s = mhShopLoad(); s.items = s.items.filter(i=>i.key!==k); mhShopSave(s); }", k)
    ev("(k)=>mhStockAdjust(k,-25,'log','e7')", k)
    if on_list(k): f.add('BUG', 'once you take it off the list yourself it must not come straight back while still low')
    ev("(k)=>mhStockSetLevel(k,750)", k); ev("()=>mhStockSweep()")
    if ev("(k)=>mhStockLoad().items[k].lowFlag", k): f.add('BUG', 'restocking above the reorder level should clear the low spell')
    ev("(k)=>mhStockSetLevel(k,140)", k); ev("(k)=>mhStockAdjust(k,-30,'log','e8')", k)
    if len(on_list(k)) != 1: f.add('BUG', 'running low again after a restock should put it back on the list')
    # reorder in servings is the same as in grams
    r = parse('5 servings', whey)['base']
    if ev("(k)=>mhStockLoad().items[k].reorder", k) != 125 or r != 125: f.add('BUG', 'reorder at 5 servings is 125 g')
    # an item already on the list is not duplicated, and a hidden one comes back
    ev("""()=>{ const s = mhShopLoad(); mhShopSetAdd(s,'Olive oil','own','','fat',{}); s.items.find(i=>i.name==='Olive oil').hidden = true; mhShopSave(s); }""")
    ko = ev("mhStockTrack('Olive oil', {base:'ml', pack:500, shop:'Asda'}).key"); ev("(k)=>{ mhStockSetLevel(k,100); mhStockSetReorder(k,200); mhStockSweep(); }", ko)
    got = ev("(k)=>mhShopLoad().items.filter(i=>i.key===k).map(i=>({hidden:i.hidden}))", ko)
    if len(got) != 1 or got[0]['hidden']: f.add('BUG', f'an item already on the list is not duplicated, and a hidden one is brought back: {got}')
    # F. a shop that is not on this trip waits; it arrives when that shop does
    kb = ev("mhStockTrack('Mature cheddar', {base:'g', pack:400, shop:'Butchers'}).key"); ev("(k)=>{ mhStockSetLevel(k,50); mhStockSetReorder(k,100); mhStockSweep(); }", kb)
    if on_list(kb): f.add('BUG', 'an item from a shop that is not on this trip must wait, not be put under another shop')
    ev("()=>{ const s = mhShopLoad(); s.shops.push('Butchers'); mhShopSave(s); mhStockSweep(); }")
    got = on_list(kb)
    if len(got) != 1 or got[0]['shop'] != 'Butchers': f.add('BUG', f'it should arrive under its own shop when that shop joins the list: {got}')
    # G. changing what it is counted in clears amounts; untracking
    ev("(k)=>mhStockTrack('Whey protein', {base:'ml', pack:750, serving:25, shop:'Asda'})", k)
    if ev("(k)=>[mhStockLoad().items[k].level, mhStockLoad().items[k].reorder]", k) != [None, None]: f.add('BUG', 'changing the counting unit must clear the amounts (they would mean something else)')
    if not ev("(k)=>mhStockUntrack(k)", k) or ev("(k)=>!!mhStockLoad().items[k]", k): f.add('BUG', 'untracking should remove it')
    if ev("(k)=>mhStockLoad().ledger.some(l=>l.k===k)", k): f.add('BUG', 'untracking should drop its ledger lines')
    if ev("()=>mhStockTrack('X', {base:'oz'})") is not None: f.add('BUG', 'an unknown counting unit must be refused')
    # H. big, in the backup, and back through a real restore
    ev("""()=>{ for (let i = 0; i < 300; i++) mhStockTrack('Stocked ingredient number ' + i, {base:'g', pack:500, serving:25, shop:'Asda'}); }""")
    raw = ev("localStorage.getItem('mh_shopping_stock_v1')")
    if ev("_BACKUP_SETTINGS_SKIP.test('mh_shopping_stock_v1')"): f.add('BUG', 'the stock key must not match the backup skip pattern')
    payload = ev("buildFullBackupPayload()")
    if (payload.get('settings') or {}).get('mh_shopping_stock_v1') != raw: f.add('BUG', 'stock must be in the full backup')
    ev("localStorage.removeItem('mh_shopping_stock_v1')"); ev("p=>mhApplyBackupObject(p,'test')", payload)
    if ev("localStorage.getItem('mh_shopping_stock_v1')") != raw: f.add('BUG', 'a restore must bring stock back exactly')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
