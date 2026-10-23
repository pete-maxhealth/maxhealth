"""Persona 300: a long seeded random walk over every Shopping/stock action (add food and non-food, search, tick, ✕, filter, put back, hide/bring back/delete shops, default shop, counts, units, Shopping complete, undo, untrack) with the rules checked after every step (v3.10.1198). Invented data."""
import sys, random; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7
rnd = random.Random(SEED)
FOODS = ['Zzqx Mince', 'Zzqx Jam', 'Zzqx Rice', 'Zzqx Eggs', 'Zzqx Cheese', 'Zzqx Butter', 'Zzqx Beans', 'Zzqx Oats']
NONF = ['Zzqx Bleach', 'Zzqx Foil', 'Zzqx Bags']
SHOPS = ['Zzqx Lidl', 'Zzqx Nicks', 'Zzqx Heylo']
CHECK = """(() => {
  const s = mhShopLoad(), o = mhStockLoad(), bad = [], on = mhStockOn(), res = mhPlanReserved();
  s.items.forEach(i => { if (!s.shops.includes(i.shop)) bad.push('item on unknown shop: ' + i.name); });
  if (!s.shops.includes(s.def)) bad.push('default shop is not a shop'); if (!s.shops.includes(s.shop)) bad.push('current shop is not a shop');
  const keys = s.items.map(i => i.key + '|' + i.shop); if (new Set(keys).size !== keys.length) bad.push('duplicate list entry');
  if (on) s.items.forEach(i => { if (i.src === 'stock' && i.from === 'running low' && !i.checked) { const x = o.items[i.key]; if (x) { if (x.held) bad.push('filtered food on the list: ' + i.name); if (!x.nonFood && !mhStockIsLowRes(x, res)) bad.push('running-low entry for a food that is not low: ' + i.name); } } });
  Object.values(o.items).forEach(x => { if (x.level != null && x.level < 0) bad.push('negative stock: ' + x.name); if (x.shop && !s.shops.some(h => h.toLowerCase() === String(x.shop).toLowerCase())) bad.push('food bought at a shop that is gone: ' + x.name); });
  return bad;
})()"""
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("localStorage.setItem('mh_shop_pane','both')")
    ev("window.mhShopIsShut=()=>false; window.appConfirm=(m,fn)=>{ try{fn()}catch(e){console.error(e)} }"); ev("switchTabById('shop')"); page.wait_for_timeout(400)
    for n in FOODS: ev(f"mhStockTrack('{n}',{{base:'g',shop:'Asda'}}); mhStockSetLevel(mhShopKey('{n}'),{rnd.choice([0, 100, 600])}); mhStockSetReorder(mhShopKey('{n}'),300)")
    for n in NONF: ev(f"mhStockTrack('{n}',{{base:'each',shop:'Asda'}}); mhStockSetLevel(mhShopKey('{n}'),2)")
    ev("mhStockSweep(); mhShopRender()")
    def anyshop(): return rnd.choice(ev("mhShopLoad().shops"))
    def anyitem():
        its = ev("mhShopLoad().items.map(i=>i.id)"); return rnd.choice(its) if its else None
    def anyfood(): return rnd.choice(FOODS + NONF)
    def a_add_shop():
        n = rnd.choice(SHOPS); ev(f"mhShopAddShopNamed('{n}')")
    def a_set_shop(): ev("mhShopSetShop(%r)" % anyshop())
    def a_hide(): ev("mhShopOff(%r)" % anyshop())
    def a_unhide(): ev("mhShopOn(%r)" % anyshop())
    def a_delshop(): ev("mhShopDelShop(%r)" % anyshop())
    def a_default(): ev("mhShopDefaultSet(%r)" % anyshop())
    def a_level(): ev("mhStockSetLevel(mhShopKey(%r),%d)" % (anyfood(), rnd.choice([0, 50, 100, 400, 900])))
    def a_reorder(): ev("mhStockSetReorder(mhShopKey(%r),%d)" % (anyfood(), rnd.choice([100, 300, 500])))
    def a_use(): ev("mhStockAdjust(mhShopKey(%r),%d,'manual')" % (anyfood(), -rnd.choice([50, 200, 1000])))
    def a_unit(): ev("mhStockTrack(%r,{base:%r,shop:%r})" % (anyfood(), rnd.choice(['g', 'ml', 'each']), anyshop()))
    def a_tohand(): ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,%r,'stock','added by hand'); mhShopSave(s)})()" % anyfood())
    def a_typed(): ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,%r,'own'); mhShopSave(s)})()" % rnd.choice(['Zzqx Typed1', 'Zzqx Typed2', 'Zzqx Typed3']))
    def a_tick(): i = anyitem(); i and ev("mhShopToggle(%r)" % i)
    def a_x(): i = anyitem(); i and ev("mhShopRemove(%r)" % i)
    def a_search(): ev("mhShopLQ(%r)" % rnd.choice(['', 'zzqx', 'mince', 'nothing here', 'ch']))
    def a_release_all(): ev("_shopUi.heldSel={}; mhShopHeldFoods().forEach(x=>{_shopUi.heldSel[x.key]=true}); mhShopHeldRelease()")
    def a_release_one(): ev("(()=>{const h=mhShopHeldFoods(); if(!h.length) return; _shopUi.heldSel={}; _shopUi.heldSel[h[0].key]=true; mhShopHeldRelease()})()")
    def a_open_held(): ev("mhShopHeldToggle()")
    def a_complete(): ev("mhShopCompleteGo(%s,%s)" % (rnd.choice(['true', 'false']), rnd.choice(['true', 'false'])))
    def a_why_undo(): ev("mhShopWhyUndo()")
    def a_untrack(): ev("mhStockUntrack(mhShopKey(%r))" % anyfood())
    def a_retrack(): (lambda n: ev("mhStockTrack(%r,{base:'g',shop:%r}); mhStockSetLevel(mhShopKey(%r),%d); mhStockSetReorder(mhShopKey(%r),300)" % (n, anyshop(), n, rnd.choice([0, 600]), n)))(anyfood())
    def a_sweep(): ev("mhStockSweep()")
    acts = [a_add_shop, a_set_shop, a_hide, a_unhide, a_delshop, a_default, a_level, a_reorder, a_use, a_unit, a_tohand, a_typed, a_tick, a_x, a_x, a_search, a_release_all, a_release_one, a_open_held, a_complete, a_why_undo, a_untrack, a_retrack, a_sweep]
    log = []
    for step in range(220):
        act = rnd.choice(acts); log.append(act.__name__)
        try: act(); ev("mhShopRender()")
        except Exception as e: f.add('BUG', f'step {step} {act.__name__} raised: {str(e)[:150]}'); break
        bad = ev(CHECK)
        if bad: f.add('BUG', f'seed {SEED} step {step} after {act.__name__}: {bad[:3]} (recent: {log[-6:]})'); break
        if errs: f.add('BUG', f'seed {SEED} step {step} after {act.__name__}: page errors {errs[:2]}'); break
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
