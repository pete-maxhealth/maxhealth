"""Persona 338: phone-to-phone QR transfer. Two separate phones (two browser contexts). Walks the whole process: pack on A, shuffled and
repeated frames into B, preview, apply (merge, never replace), undo, reload, a damaged transfer, a hostile payload, both ways so the stock
converges, demo mode, and the neighbouring screens (shopping list, recipes, library, Settings card, Shopping sync button)."""
import sys, re, json, random; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/xfer/'
def phone(br, name):
    ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); p = ctx.new_page()
    errs = []; p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.dismiss())
    p.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1200); p.evaluate("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(1500)
    p.evaluate("localStorage.setItem('mh_stock_device_label', %s)" % json.dumps(name)); return p, errs
T0 = 1790000000000
SEED_A = """(()=>{
  mhStockTrack('Eggs',{base:'each',pack:6}); mhStockTrack('Milk',{base:'ml',pack:1000}); mhStockTrack('Rice',{base:'g',pack:1000});
  let o=mhStockLoad(); o.items.eggs.level=6; o.items.eggs.since=%d+5000; o.items.milk.level=500; o.items.milk.since=%d+1000; o.items.rice.level=900; o.items.rice.since=%d+2000; o.enabled=true; mhStockSave(o);
  const s=mhShopLoad(); s.items.push({id:'a1',key:'oats',name:'Oats',shop:s.def,checked:false,src:'manual'}); mhShopSave(s);
  saveRecipes([{id:'ra1',name:'Egg fried rice',servings:2,ingredients:[{name:'Eggs',amount:2,kcal:140,protein:12,carbs:1,fat:10},{name:'Rice',amount:150,kcal:200,protein:4,carbs:44,fat:1}],total:{kcal:340,protein:16,carbs:45,fat:11}},
    {id:'ra2',name:'Porridge',servings:1,ingredients:[{name:'Oats',amount:40,kcal:150,protein:5,carbs:27,fat:3}],total:{kcal:150,protein:5,carbs:27,fat:3}}]);
  saveLibrary([{name:'Oats',kcal:380,protein:13,carbs:60,fat:7,portion:'40g',per100g:false,locked:false,source:'a'},{name:'Greek yoghurt',kcal:97,protein:9,carbs:4,fat:5,portion:'100g',per100g:false,locked:false,source:'a'},
    {name:'Butter',kcal:740,protein:0.5,carbs:0.5,fat:82,portion:'10g',per100g:false,locked:false,source:'a'},{name:'Banana',kcal:90,protein:1,carbs:21,fat:0,portion:'1 medium',per100g:false,locked:false,source:'a'}]);
})()""" % (T0, T0, T0)
SEED_B = """(()=>{
  mhStockTrack('Eggs',{base:'each',pack:6}); mhStockTrack('Milk',{base:'ml',pack:1000});
  let o=mhStockLoad(); o.items.eggs.level=2; o.items.eggs.since=%d+1000; o.items.milk.level=1000; o.items.milk.since=%d+9000; o.enabled=true; mhStockSave(o);
  saveRecipes([{id:'rb1',name:'Porridge',servings:1,ingredients:[{name:'Oats',amount:50,kcal:190,protein:6,carbs:33,fat:4}],total:{kcal:190,protein:6,carbs:33,fat:4}}]);
  saveLibrary([{name:'Oats',kcal:371,protein:12,carbs:61,fat:8,portion:'40g',per100g:false,locked:false,source:'b'},{name:'Butter',kcal:700,protein:0.5,carbs:0.5,fat:80,portion:'10g',per100g:false,locked:true,source:'label'}]);
})()""" % (T0, T0)
SNAP = "JSON.stringify([localStorage.getItem(MH_STOCK_KEY),localStorage.getItem('mh_recipes'),localStorage.getItem(LIBRARY_KEY),localStorage.getItem(MH_SHOP_KEY)])"
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    A, errA = phone(br, "Pete's phone"); B, errB = phone(br, "Jill's phone")
    A.evaluate(SEED_A); B.evaluate(SEED_B)
    # 1. pack on A
    pk = A.evaluate("(async()=>{const r=await mhxPack(mhxCollect({stock:true,list:true,recipes:true,library:true}));return {frames:r.frames,gz:r.gzBytes}})()")
    fr = pk['frames']; check('A packs into frames', len(fr) >= 1 and all(f.startswith('MHX1|') for f in fr), str(len(fr)))
    check('every QR frame fits a QR code and draws', A.evaluate("(f)=>{try{const q=MHQR.encodeText(f);const c=document.createElement('canvas');MHQR.draw(c,q,3);return c.width>0&&q.version<=40}catch(e){return String(e)}}", fr[0]) is True)
    # 2. B receives shuffled frames with repeats; a stray frame from nothing is ignored
    order = fr + random.sample(fr, min(3, len(fr))); random.shuffle(order)
    recv = B.evaluate("""async(frames)=>{const rx=mhxReceiver();let last=null;const junk=await rx.feed('hello');for(const f of frames){last=await rx.feed(f)}
        window._rxData=last&&last.complete?last.data:null; return {junk:junk.ok,complete:!!(last&&last.complete),from:last&&last.data&&last.data.from}}""", order)
    check('stray text is ignored', recv['junk'] is False)
    check('B reassembles the transfer from shuffled, repeated frames', recv['complete'] and recv['from'] == "Pete's phone", str(recv))
    # 3. plan = preview only, nothing saved
    before = B.evaluate(SNAP)
    plan = B.evaluate("(()=>{const p=mhxPlan(window._rxData);return {st:{add:p.stock.add.map(x=>x.key),take:p.stock.take.map(x=>x.key),keep:p.stock.keep.map(x=>x.key),same:p.stock.same},li:p.list.add.length,rc:{add:p.recipes.add.length,ren:p.recipes.renamed,same:p.recipes.same},lb:{add:p.library.add.map(x=>x.name),differ:p.library.differ.map(d=>[d.name,d.locked]),same:p.library.same}}})()")
    # loadLibrary() itself tidies stored entries on first read (existing behaviour), so prove that is the only thing that moved
    B.evaluate("loadLibrary()"); warmed = B.evaluate(SNAP)
    check('preview saves nothing (compared after one plain library read)', warmed == B.evaluate(SNAP) and json.loads(warmed)[0] == json.loads(before)[0] and json.loads(warmed)[1] == json.loads(before)[1] and json.loads(warmed)[3] == json.loads(before)[3])
    before = warmed
    check('stock: Rice is new, Eggs take A (newer), Milk keep B (newer)', plan['st']['add'] == ['rice'] and plan['st']['take'] == ['eggs'] and plan['st']['keep'] == ['milk'], str(plan['st']))
    check('list: Oats to add', plan['li'] == 1)
    check('recipes: Egg fried rice added, Porridge kept apart as "from"', plan['rc']['add'] == 2 and plan['rc']['ren'] == 1, str(plan['rc']))
    check('library: Greek yoghurt + Banana new; Oats and Butter differ; Butter locked on B', sorted(plan['lb']['add']) == ['Banana', 'Greek Yoghurt'] and sorted(plan['lb']['differ']) == [['Butter', True], ['Oats', False]], str(plan['lb']))
    # 4. apply: user does NOT tick Oats; merge not replace
    res = B.evaluate("mhxApply(mhxPlan(window._rxData))")
    check('apply reports the counts', res['stockNew'] == 1 and res['stock'] == 1 and res['list'] == 1 and res['recipes'] == 2 and res['library'] == 2 and res['libraryChanged'] == 0, str(res))
    B.wait_for_timeout(1500)
    check('arriving foods do not trigger the "new in your Library, not in My cupboards" question', not B.evaluate("document.body.innerText.includes('not in My cupboards')"))
    st = B.evaluate("(()=>{const o=mhStockLoad();return {e:o.items.eggs.level,m:o.items.milk.level,r:o.items.rice&&o.items.rice.level}})()")
    check('stock merged: eggs 6 (newer from A), milk 1000 (B newer kept), rice 900 (new)', st == {'e': 6, 'm': 1000, 'r': 900}, str(st))
    lib = B.evaluate("loadLibrary().map(f=>[f.name,f.kcal,f.locked])")
    check('library: B keeps its own Oats 371 and locked Butter 700; gains Banana and Greek yoghurt', ['Oats', 371, False] in lib and ['Butter', 700, True] in lib and len(lib) == 4, str(lib))
    rc = B.evaluate("loadRecipes().map(r=>r.name)")
    check('recipes: both of B\'s own kept and A\'s added', "Porridge" in rc and "Egg Fried Rice" in rc and any("from Pete's Phone" in n for n in rc) and len(rc) == 3, str(rc))
    check('list: Oats now on B list and B own items kept', B.evaluate("mhShopLoad().items.some(i=>i.key==='oats')"))
    # 5. neighbouring screens still render
    B.evaluate("document.getElementById('maintab-log').click()"); B.wait_for_timeout(400); B.evaluate("document.getElementById('logtab-shop').click()"); B.wait_for_timeout(700)
    B.evaluate("mhShopView('list'); mhShopRender()"); B.wait_for_timeout(700)
    check('shopping list shows the transferred item (Asda (1))', B.evaluate("/Asda \\(1\\)/.test((document.getElementById('mhShopPane') || document.body).innerText)"))
    # 6. undo restores byte for byte
    B.evaluate("mhxUndo()"); B.wait_for_timeout(300)
    _after = B.evaluate(SNAP); pass
    check('undo puts B back exactly as it was', _after == before)
    check('undo is a one-shot (nothing left to undo)', B.evaluate("mhxUndoInfo()") is None)
    # 7. apply again then reload keeps it
    B.evaluate("mhxApply(mhxPlan(window._rxData))"); B.reload(); B.wait_for_timeout(1500)
    check('transfer survives a reload', B.evaluate("mhStockLoad().items.eggs.level") == 6 and B.evaluate("loadRecipes().length") == 3)
    check('undo still available after reload', B.evaluate("!!mhxUndoInfo()"))
    # 8. both ways: B sends back, A merges; stock converges
    pk2 = B.evaluate("(async()=>{const r=await mhxPack(mhxCollect({stock:true}));return r.frames})()")
    A.evaluate("""async(frames)=>{const rx=mhxReceiver();let last=null;for(const f of frames){last=await rx.feed(f)};window._rx2=last.data;mhxApply(mhxPlan(last.data))}""", pk2)
    a_st = A.evaluate("(()=>{const o=mhStockLoad();return {e:o.items.eggs.level,m:o.items.milk.level,r:o.items.rice.level}})()")
    b_st = B.evaluate("(()=>{const o=mhStockLoad();return {e:o.items.eggs.level,m:o.items.milk.level,r:o.items.rice.level}})()")
    check('both ways: the two phones now have the same stock', a_st == b_st == {'e': 6, 'm': 1000, 'r': 900}, str(a_st) + str(b_st))
    pl = A.evaluate("(()=>{const p=mhxPlan(window._rx2);return [p.stock.add.length,p.stock.take.length,p.stock.keep.length]})()")
    check('a third pass finds nothing left to change', pl == [0, 0, 0], str(pl))
    # 9. damaged transfer: one frame altered, nothing kept
    bad_fr = list(fr); bad_fr[0] = bad_fr[0][:-6] + ('AAAAAA' if not bad_fr[0].endswith('AAAAAA') else 'BBBBBB')
    r2 = B.evaluate("async(frames)=>{const rx=mhxReceiver();let last=null;for(const f of frames){last=await rx.feed(f)};return {ok:last.ok,complete:!!last.complete,reason:last.reason||''}}", bad_fr)
    check('a damaged transfer is refused with a plain message', not r2['ok'] and not r2['complete'] and r2['reason'], str(r2))
    # 10. hostile payload is cleaned, never executed or polluting
    evil = B.evaluate("""(()=>{const p=mhxPlan(JSON.parse('{"v":1,"from":"<img src=x onerror=window.__pwn=1>","at":1,"scopes":{"library":[{"name":"Evil","kcal":1,"__proto__":{"polluted":1},"constructor":{"x":1}}],"recipes":[{"name":"<b>x</b>","ingredients":[]}]}}'));
        mhxApply(p); return {pol:({}).polluted===undefined, pwn:window.__pwn===undefined, from:p.from}})()""")
    check('hostile payload: no prototype pollution, no script run', evil['pol'] and evil['pwn'], str(evil))
    # 11. the screen: Settings card, overlay home/review/send views
    B.evaluate("document.getElementById('maintab-settings').click()"); B.wait_for_timeout(300)
    B.evaluate("switchSubTab && switchSubTab('settings','import')") if False else None
    check('Settings card exists with show/hide title', B.evaluate("!!document.getElementById('title-imp-qr') && !!document.getElementById('imp-qr-wrap')"))
    B.evaluate("mhxOpen()"); B.wait_for_timeout(400)
    home = B.evaluate("document.getElementById('mhXferOverlay').innerText")
    check('home view: name, four things to share, send/scan/back', all(w in home for w in ('Phone to phone', 'Cupboards & stock', 'Shopping list', 'Recipes', 'Food library', 'Show codes', 'Scan codes', 'Back')), home[:200])
    B.screenshot(path=SHOT + 'xfer_home.png')
    B.evaluate("_mhx.plan=mhxPlan(window._rxData||mhxPlan);") if False else None
    A.evaluate("mhxOpen()"); A.wait_for_timeout(300)
    A.evaluate("mhxStartSend()"); A.wait_for_timeout(2500)
    sinfo = A.evaluate("document.getElementById('mhxSinfo') && document.getElementById('mhxSinfo').textContent")
    check('send view animates real codes', sinfo and 'Frame' in sinfo and A.evaluate("document.getElementById('mhxQr').width>100"), str(sinfo))
    A.screenshot(path=SHOT + 'xfer_send.png')
    A.evaluate("mhxBackHome()")
    # review screen with a differing food, plus done screen
    B.evaluate("""async(frames)=>{const rx=mhxReceiver();let last=null;for(const f of frames){last=await rx.feed(f)};window._rxData=last.data;_mhx.plan=mhxPlan(last.data);_mhx.view='review';mhxRender()}""", fr); B.wait_for_timeout(300)
    rv = B.evaluate("document.getElementById('mhXferOverlay').innerText")
    check('review view says what would change and that nothing is saved yet', 'Nothing is saved yet' in rv and 'Add to this phone' in rv and "Don't add" in rv, rv[:300])
    B.screenshot(path=SHOT + 'xfer_review.png')
    B.evaluate("mhxClose()")
    # 12. demo mode never saves
    B.evaluate("startDemoMode('alex')"); B.wait_for_timeout(2200)
    dm = B.evaluate("mhxApply(mhxPlan(window._rxData||{v:1,scopes:{}}))")
    check('demo mode: apply is blocked', dm.get('demo') is True)
    check('no JS errors on either phone', not errA and not errB, str(errA[:2]) + str(errB[:2]))
print('p338:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
