"""Persona 11: the food library, used like a person uses it - add, edit, search, log a portion,
delete, and get it all back after the browser is wiped."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
U = 'http://localhost:5757'
f = Findings()
def boot(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    pg.goto(U + '/'); pg.wait_for_timeout(1200)
    return pg, errs
def onboard(pg, cond='general'):
    pg.evaluate("onboardNext(2)"); pg.fill('#onboardName', 'Test'); pg.evaluate("onboardNext(3)")
    pg.evaluate("obSetSex('male')"); pg.fill('#onboardAge', '50'); pg.fill('#onboardHeight', '178')
    pg.fill('#onboardWeight', '80'); pg.fill('#onboardTarget', '75')
    pg.evaluate("onboardNext(4)"); pg.evaluate("obSetActivity('light')"); pg.evaluate("obSetGoal('lose')")
    pg.evaluate("onboardNext(5)"); pg.evaluate(f"obSetCondition('{cond}')")
    pg.evaluate("onboardNext(6)"); pg.evaluate("onboardFinish()"); pg.wait_for_timeout(1200)
def open_library(pg):
    pg.click("[onclick^=\"switchTab('log'\"]"); pg.click("[onclick^=\"switchSubTab('log','library'\"]"); pg.wait_for_timeout(500)
def add_via_modal(pg, item):
    pg.evaluate("(it) => promptSaveToLibrary(it)", item)
    pg.fill('#saveModalName', item['name'])
    pg.evaluate("confirmSaveToLibrary()"); pg.wait_for_timeout(500)
LIB = "JSON.parse(localStorage.getItem('maxhealth_foods')||'[]')"
chk = lambda ok, msg: None if ok else f.add('BUG', msg)

with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    pg, errs = boot(b); onboard(pg); open_library(pg)
    chk(pg.evaluate(LIB) == [], 'a new user\'s library should start empty')
    body = pg.inner_text('body')
    chk(not re.search(r'\b(NaN|undefined)\b', body), 'NaN/undefined on an empty Library screen')
    # add several items, including awkward names
    names = ['Chicken breast', 'Greek yoghurt 0%', 'Mum\'s "special" stew | with pipe, and comma', 'Crème fraîche 🥣', 'Oats']
    for i, n in enumerate(names):
        add_via_modal(pg, {'name': n, 'kcal': round(4*(20+i) + 4*(5+i) + 9*(3+i)), 'protein': 20 + i, 'fat': 3 + i, 'carbs': 5 + i, 'amount': '100g'})
    lib = pg.evaluate(LIB)
    print('stored names:', [x['name'] for x in lib])
    chk(len(lib) == 5, f'expected 5 library items after adding 5, got {len(lib)}')
    pg.evaluate("renderLibrary()"); pg.wait_for_timeout(300)
    # edit one: give it fibre + polyols + a category through the real edit functions
    idx = next((i for i, x in enumerate(lib) if x['name'] == 'Oats'), 0)
    pg.evaluate(f"openLibraryEdit({idx})"); pg.wait_for_timeout(300)
    pg.fill(f'#lib-edit-kcal-{idx}', '370'); pg.fill(f'#lib-edit-prot-{idx}', '13'); pg.fill(f'#lib-edit-carb-{idx}', '60')
    for fid, v in (('fibre', '10'), ('polyols', '2')):
        try: pg.evaluate(f"(v)=>{{document.getElementById('lib-edit-{fid}-{idx}').value=v}}", v)
        except Exception as e: f.add('BUG', f'edit form lacks {fid}: {str(e)[:60]}')
    pg.evaluate(f"saveLibraryEdit({idx})"); pg.wait_for_timeout(500)
    o = pg.evaluate(LIB)[idx]
    chk(o['kcal'] == 370 and o['protein'] == 13 and o['carbs'] == 60, f'edit not saved: {o}')
    chk(o.get('fibre') == 10 and o.get('polyols') == 2, f'fibre/polyols not saved by edit: {o.get("fibre")}/{o.get("polyols")}')
    # an edit with a blank kcal must NOT wipe the item
    pg.evaluate(f"openLibraryEdit({idx})"); pg.fill(f'#lib-edit-kcal-{idx}', ''); pg.evaluate(f"saveLibraryEdit({idx})"); pg.wait_for_timeout(300)
    chk(pg.evaluate(LIB)[idx]['kcal'] == 370, 'blank-kcal edit changed the stored value')
    # search through the real input
    pg.fill('#libSearch' if pg.query_selector('#libSearch') else 'input[oninput^="filterLibrary"]', 'chick'); pg.wait_for_timeout(500)
    vis = pg.inner_text('body')
    chk('Chicken' in vis and 'Oats' not in vis, 'search for "chick" should show Chicken and hide Oats')
    pg.fill('input[oninput^="filterLibrary"]', ''); pg.wait_for_timeout(400)
    # log a portion: item is 100g based; 50g must log half the macros, exactly once
    cidx = next(i for i, x in enumerate(pg.evaluate(LIB)) if x['name'] == 'Greek Yoghurt 0%')
    base = pg.evaluate(LIB)[cidx]
    pg.evaluate(f"quickLogFromLibrary({cidx})"); pg.wait_for_timeout(300)
    pg.fill('#libPortionInput', '50'); pg.evaluate(f"logLibraryWithPortion({cidx})"); pg.wait_for_timeout(500)
    tl = pg.evaluate("state.todayLog")
    chk(len(tl) == 1, f'logging one portion made {len(tl)} log entries')
    if tl:
        it = (tl[0].get('items') or [tl[0]])[0]
        chk(abs(it['kcal'] - round(base['kcal'] / 2)) <= 1, f'50g of a 100g item logged {it["kcal"]} kcal, expected {round(base["kcal"]/2)}')
        chk(abs(it['protein'] - base['protein'] / 2) < 0.2, f'50g protein {it["protein"]} vs {base["protein"]/2}')
    chk(pg.evaluate(LIB)[cidx].get('useCount') == 1, 'useCount not incremented once')
    # a nonsense portion must not log NaN
    pg.evaluate(f"quickLogFromLibrary({cidx})"); pg.fill('#libPortionInput', ''); pg.evaluate(f"logLibraryWithPortion({cidx})"); pg.wait_for_timeout(300)
    bad = json.dumps(pg.evaluate("state.todayLog"))
    chk('NaN' not in bad and 'null' not in bad.replace('"_origAmount"', ''), 'blank portion logged NaN/null')
    # the server copy: written, and what comes back after a wipe
    pg.wait_for_timeout(800)
    csvp = os.path.join(root, 'data', 'tables', 'library.csv')
    chk(os.path.exists(csvp), 'library.csv never reached the server')
    before = pg.evaluate(LIB)
    pg2, errs2 = boot(b); pg2.evaluate("localStorage.clear()"); pg2.reload(); pg2.wait_for_timeout(2500)
    after = pg2.evaluate(LIB)
    chk(len(after) == len(before), f'after a browser wipe {len(after)} of {len(before)} library items came back')
    ob = {x['name']: x for x in before}; oa = {x['name']: x for x in after}
    for n, x in ob.items():
        y = oa.get(n)
        if not y: f.add('BUG', f'item lost in server round trip: {n!r}'); continue
        for k in ('kcal', 'protein', 'carbs', 'fat'):
            if abs((x.get(k) or 0) - (y.get(k) or 0)) > 0.05: f.add('BUG', f'{n!r}: {k} {x.get(k)} -> {y.get(k)} after restore')
        for k in ('fibre', 'polyols', 'useCount'):
            if x.get(k) and not y.get(k): f.add('BUG', f'{n!r}: {k}={x.get(k)} lost after a browser wipe (server CSV has no such column)')
    # delete all, one by one, via the real delete function; the library must end empty and stay empty
    for _ in range(10):
        if not pg.evaluate(LIB): break
        pg.evaluate("_doDeleteLibraryItem(0)"); pg.wait_for_timeout(120)
    chk(pg.evaluate(LIB) == [], 'library not empty after deleting every item')
    pg.reload(); pg.wait_for_timeout(2000)
    chk(pg.evaluate("loadLibrary().length") == 0, 'deleted items came back after reload (backup keys / server restore)')
    # a big library: 800 items render without errors and in reasonable time
    pg.evaluate("localStorage.setItem('maxhealth_foods', JSON.stringify(Array.from({length:800},(_,i)=>({id:'t'+i,name:'Food '+i,kcal:100+i%50,protein:5,carbs:10,fat:2,portion:'100g',per100g:true}))))")
    pg.reload(); pg.wait_for_timeout(1500); open_library(pg)
    t = pg.evaluate("(()=>{const s=performance.now(); renderLibrary(); return performance.now()-s})()")
    chk(t < 3000, f'rendering 800 library items took {t:.0f} ms')
    chk(not errs and not errs2, f'JS errors: {errs + errs2}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
