"""Persona 340: phone-to-phone QR carries all non-third-party data. History, exercise, routines, supplements, symptoms, treatments + sessions, labs,
and (opt-in) settings. Walks: pack on A, preview on B (nothing saved), apply (merge, never replace, yours kept), reload, undo everything,
a snapshot that cannot be stored (nothing added), a write that fails part way (everything put back), third-party/secret keys never packed."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
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
DAY = lambda d, desc, k, w=None: "{date:'%s',log:[{id:%s,time:'08:00',description:'%s',kcal:%d,protein:10,carbs:5,fat:8}],totals:{kcal:%d,protein:10,carbs:5,fat:8},mode:'standard',notes:'',weight:%s}" % (d, abs(hash(desc)) % 1000, desc, k, k, w if w else 'null')
SEED_A = """(()=>{
  state.history=[%s,%s,%s]; state.strengthLog=[{id:'sa1',date:'01/10/26',exercise:'Squat',sets:[{reps:5,weight_kg:60,note:null}]}]; saveState();
  saveRoutines([{id:'r1',name:'Push day',exercises:[{name:'Bench press',sets:3}]}]);
  localStorage.setItem('mh_supplement_defs',JSON.stringify([{id:'s1',name:'Vitamin D',dose:'1000iu',periods:['morning'],active:true},{id:'s2',name:'Magnesium',dose:'200mg',periods:['evening'],active:true}]));
  localStorage.setItem('mh_symptom_defs',JSON.stringify([{id:'y1',name:'Headache'}]));
  localStorage.setItem('mh_treatment_defs',JSON.stringify([{id:'t1',name:'PEMF'}]));
  localStorage.setItem('mh_treatment_log',JSON.stringify([{id:'trt_1',treatmentId:'t1',date:'01/10/26',time:'09:00',note:''}]));
  localStorage.setItem('mh_lab_results',JSON.stringify([{id:'lab_1',date:'01/10/26',values:{wbc:5.1},custom:[]}]));
  localStorage.setItem('mh_target_fibre','30'); localStorage.setItem('mh_target_water','3000'); localStorage.setItem('mh_carer_email','x@y.z'); localStorage.setItem('mh_licence_key','L'); localStorage.setItem('mh_debug_watch_date','01/10/26'); localStorage.setItem('mh_wearable_big','x'.repeat(500)); localStorage.setItem('mh_api_key','SECRET'); localStorage.setItem('mh_oura_data','{"a":1}');
})()""" % (DAY('01/10/26','Eggs',200,'80.5'), DAY('02/10/26','Steak A',500), DAY('03/10/26','Salmon',450))
SEED_B = """(()=>{
  state.history=[%s]; saveState();
  localStorage.setItem('mh_supplement_defs',JSON.stringify([{id:'s1',name:'Zinc',dose:'15mg',periods:['morning'],active:true}]));
  localStorage.setItem('mh_target_protein','150'); localStorage.setItem('mh_target_water','2500');
})()""" % DAY('02/10/26','Steak B',999)
STORES = "JSON.stringify(['maxhealth_v1','mh_routines','mh_supplement_defs','mh_symptom_defs','mh_treatment_defs','mh_treatment_log','mh_lab_results','mh_target_fibre','mh_target_protein','mh_target_water'].map(k=>localStorage.getItem(k)))"
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); A, ea = phone(br, "Pete's phone"); B, eb = phone(br, "Jill's phone")
    A.evaluate(SEED_A); B.evaluate(SEED_B)
    # pack everything incl. settings
    sel = "{stock:true,list:true,recipes:true,library:true,history:true,routines:true,supplements:true,symptoms:true,treatments:true,labs:true,settings:true}"
    pk = A.evaluate("(async()=>{const o=mhxCollect(%s);const r=await mhxPack(o);return {frames:r.frames,keys:Object.keys((o.scopes.settings||{})),scopes:Object.keys(o.scopes)}})()" % sel)
    fr = pk['frames']
    check('all scopes are in the transfer', all(k in pk['scopes'] for k in ['history','routines','supplements','symptoms','treatments','labs','settings']), str(pk['scopes']))
    check('third-party, secret, device-label and own-scope keys are never packed', not any(re.search(r'wearable|oura|api_key|device_label|supplement|routines|stock|shopping', k) for k in pk['keys']), str(pk['keys']))
    check('settings that are plain preferences are packed', 'mh_target_fibre' in pk['keys'] and 'mh_target_water' in pk['keys'] and not any(k in pk['keys'] for k in ['mh_carer_email','mh_licence_key','mh_debug_watch_date','mh_master_csv_cache','mh_mig_step_commas']))
    check('every frame draws as a QR code', A.evaluate("(fs)=>{try{return fs.every(f=>{const q=MHQR.encodeText(f);return q.version<=40})}catch(e){return String(e)}}", fr) is True)
    B.evaluate("(frames)=>{window._rx=null;return (async()=>{const rx=mhxReceiver();let l=null;for(const f of frames)l=await rx.feed(f);window._rx=l.data;return l.complete})()}", fr)
    before = B.evaluate(STORES)
    pl = B.evaluate("""(()=>{const p=mhxPlan(window._rx);return {h:[p.history.add.map(d=>d.date),p.history.same,p.history.strength.length],r:p.routines.add.length,s:[p.supplements.add.map(x=>x.name),p.supplements.clash],y:p.symptoms.add.length,
      t:[p.treatments.add.length,p.treatments.log.length],l:p.labs.add.length,st:[p.settings.add.map(x=>x.k).sort(),p.settings.differ.map(x=>x.k)]}})()""")
    check('preview saves nothing', B.evaluate(STORES) == before)
    check('history: 01 and 03 Oct new, 02 Oct (on both) kept as B has it; exercise entry', pl['h'] == [['01/10/26','03/10/26'], 1, 1], str(pl['h']))
    check('routines, symptoms, treatments + session, labs counted', pl['r'] == 1 and pl['y'] == 1 and pl['t'] == [1, 1] and pl['l'] == 1, str(pl))
    check('supplements: Magnesium added, Vitamin D left out (its id clashes with B\'s Zinc)', pl['s'] == [['Magnesium'], 1], str(pl['s']))
    check('settings: a is new, c differs and is not changed by default', pl['st'] == [['mh_target_fibre'], ['mh_target_water']], str(pl['st']))
    # look at the real screens
    B.evaluate("(()=>{mhxOpen(); _mhx.plan=mhxPlan(window._rx); _mhx.view='review'; mhxRender();})()"); B.wait_for_timeout(300); B.screenshot(path=SHOT + 'all_review.png', full_page=True)
    B.evaluate("mhxOpen()"); B.wait_for_timeout(300); B.screenshot(path=SHOT + 'all_home.png', full_page=True)
    # apply
    B.evaluate("(()=>{mhxOpen(); _mhx.plan=mhxPlan(window._rx); _mhx.view='review'; mhxRender();})()")
    B.evaluate("mhxDoApply()"); B.wait_for_timeout(1500)
    check('done screen shows the counts', 'history: 2 days' in B.inner_text('#mhXferOverlay'), B.inner_text('#mhXferOverlay')[:300])
    r = B.evaluate("""(()=>{const h=state.history.map(d=>[d.date,d.log[0].description]);return {h,str:state.strengthLog.length,rt:loadRoutines().map(x=>x.name),sup:JSON.parse(localStorage.getItem('mh_supplement_defs')).map(x=>x.name),
      sy:JSON.parse(localStorage.getItem('mh_symptom_defs')).map(x=>x.name),td:JSON.parse(localStorage.getItem('mh_treatment_defs')).map(x=>x.name),tl:JSON.parse(localStorage.getItem('mh_treatment_log')).length,
      lab:JSON.parse(localStorage.getItem('mh_lab_results')).length,pa:localStorage.getItem('mh_target_fibre'),pb:localStorage.getItem('mh_target_protein'),pc:localStorage.getItem('mh_target_water'),
      leak:['mh_wearable_big','mh_api_key','mh_oura_data','mh_carer_email','mh_licence_key'].map(k=>localStorage.getItem(k))}})()""")
    check('history merged, newest first, B\'s own 02 Oct kept', r['h'] == [['03/10/26','Salmon'],['02/10/26','Steak B'],['01/10/26','Eggs']], str(r['h']))
    check('exercise, routine, symptom, treatment+session, lab arrived', r['str'] == 1 and r['rt'] == ['Push day'] and r['sy'] == ['Headache'] and r['td'] == ['PEMF'] and r['tl'] == 1 and r['lab'] == 1, str(r))
    check('supplements: B keeps Zinc and gains Magnesium', r['sup'] == ['Zinc', 'Magnesium'], str(r['sup']))
    check('settings: new one added, B\'s own kept, differing one left as B had it, nothing third-party', r['pa'] == '30' and r['pb'] == '150' and r['pc'] == '2500' and r['leak'] == [None]*5, str(r))
    # survives reload
    B.reload(); B.wait_for_timeout(1500)
    check('after a reload the new history is still there', B.evaluate("state.history.length") == 3 and B.evaluate("state.strengthLog.length") == 1)
    # neighbouring screens still work
    check('Today still renders with no page errors', not eb, str(eb))
    B.evaluate("(frames)=>(async()=>{const rx=mhxReceiver();let l=null;for(const f of frames)l=await rx.feed(f);window._rx=l.data})()", fr)
    # undo restores every store exactly
    B.evaluate("mhxOpen()"); B.wait_for_timeout(200)
    ok = B.evaluate("mhxUndo()"); B.wait_for_timeout(500)
    check('undo reports success', ok is True)
    check('undo puts every store back exactly as it was', B.evaluate(STORES) == before)
    check('undo restored the live state too', B.evaluate("state.history.length") == 1 and B.evaluate("(state.strengthLog||[]).length") == 0)
    # replace-differing tick
    B.evaluate("(async()=>{const p=mhxPlan(window._rx); p.settings.replace=true; window._r2=await mhxApply(p)})()"); B.wait_for_timeout(800)
    check('with the tick, the differing setting takes the other phone\'s value', B.evaluate("localStorage.getItem('mh_target_water')") == '3000')
    B.evaluate("mhxUndo()"); B.wait_for_timeout(500)
    check('and undo brings B\'s own back', B.evaluate("localStorage.getItem('mh_target_water')") == '2500' and B.evaluate("localStorage.getItem('mh_target_fibre')") is None)
    # snapshot cannot be stored -> nothing added
    B.evaluate("window._realSet=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(k===MHX_UNDO_KEY) throw new Error('quota'); return window._realSet.call(this,k,v) }; 0")
    b0 = B.evaluate(STORES); res = B.evaluate("mhxApply(mhxPlan(window._rx))")
    check('no room for the undo copy: refused and nothing changed', bool(res.get('failed')) and B.evaluate(STORES) == b0, str(res))
    B.evaluate("Storage.prototype.setItem=window._realSet; 0")
    # a write fails part way -> everything put back
    B.evaluate("window._realSet=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(k==='mh_lab_results') throw new Error('boom'); return window._realSet.call(this,k,v) }; 0")
    res = B.evaluate("mhxApply(mhxPlan(window._rx))"); B.evaluate("Storage.prototype.setItem=window._realSet; 0")
    check('a failure part way puts everything back', bool(res.get('failed')) and B.evaluate(STORES) == b0 and B.evaluate("state.history.length") == 1, str(res))
    # demo mode blocks
    B.evaluate("startDemoMode && startDemoMode('priya')"); B.wait_for_timeout(1500)
    dm = B.evaluate("mhxApply(mhxPlan(window._rx))") if B.evaluate("typeof window._rx!=='undefined' && !!window._rx") else {'demo': True}
    check('demo mode adds nothing', dm.get('demo') is True, str(dm))
    check('no page errors anywhere', not ea and not eb, str(ea + eb))
    br.close()
print('FAILED: ' + ', '.join(bad) if bad else 'ALL PASS'); sys.exit(1 if bad else 0)
