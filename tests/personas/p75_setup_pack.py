"""Persona 75: a setup pack carries definitions only (no logs, name, send dates), previews before importing, merges without overwriting, unlocks shared foods, remaps ids, and rejects non-packs."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def mk(pw):
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    return b, page, errs
with fresh_server() as root, sync_playwright() as pw:
    # --- Sender
    b, page, errs = mk(pw)
    page.evaluate("""() => {
      localStorage.setItem('mh_name','Secret Person');
      saveLibrary([{id:'l1',name:'Greek yoghurt',kcal:100,protein:10,carbs:4,fat:5,portion:'100g',locked:true,source:'label'},{id:'l2',name:'Almonds',kcal:600,protein:21,carbs:9,fat:50,portion:'30g',locked:false,source:'label'}]);
      saveSupplementDefs([{id:'s1',name:'Vitamin D',dose:'1000iu',tablets:'1',periods:['morning'],active:true}]);
      saveSymptomDefs([{id:'sy1',name:'Headache',active:true},{id:'sy2',name:'Fatigue',active:true}]);
      saveTreatmentDefs([{id:'t1',name:'PEMF'}]);
      localStorage.setItem('mh_symptom_log', JSON.stringify([{date:'01/10/26',id:'sy1',sev:3}]));
      saveReportProfiles([{id:'rp1',name:'Clinic',metrics:['kcal'],symptomIds:['sy2'],treatmentId:'t1',lastSent:'2026-10-01',schedule:{frequency:'none',dayOfWeek:0}}]);
      localStorage.setItem('mh_tableware', JSON.stringify({activeId:'home',revertOn:null,sets:[{id:'home',name:'Home',vals:{dinner_plate:{diam:25}}},{id:'hol',name:'Holiday',vals:{bowl:{cap:400}}}],custom:[{id:'c1',name:'Egg cup',kind:'cup',cap:60}]}));
    }""")
    pack = page.evaluate("mhPackBuild(['library','supplements','symptoms','treatments','reports','tableware','strength','fullstate'])")
    txt = json.dumps(pack)
    if 'Secret Person' in txt: f.add('BUG', 'pack leaked the name')
    if '2026-10-01' in txt or 'sev' in txt: f.add('BUG', 'pack leaked a send date or a symptom entry')
    if set(pack['sets']) != {'library','supplements','symptoms','treatments','reports','tableware'}: f.add('BUG', f"unexpected pack sections {sorted(pack['sets'])}")
    if not all(not x['locked'] for x in pack['sets']['library']['data']): f.add('BUG', 'locked foods must be exported unlocked')
    b.close()
    # --- Receiver (own storage), already has overlapping data
    b, page, errs = mk(pw)
    page.evaluate("""() => {
      saveLibrary([{id:'l1',name:'Greek yoghurt',kcal:999,protein:1,carbs:1,fat:1,portion:'x',locked:true,source:'mine'}]);
      saveSymptomDefs([{id:'sy2',name:'Nausea',active:true}]);
      saveTreatmentDefs([]);
      localStorage.setItem('mh_tableware', JSON.stringify({activeId:'home',revertOn:null,sets:[{id:'home',name:'Home',vals:{dinner_plate:{diam:30}}}],custom:[]}));
    }""")
    page.evaluate("p => mhPackPreview(p)", pack); page.wait_for_timeout(300)
    if not page.query_selector('#mhPackModal'): f.add('BUG', 'no preview shown')
    prev = page.inner_text('#mhPackModal')
    if '1 new, 1 already there' not in prev: f.add('BUG', f'library preview counts wrong: {prev[:300]}')
    page.click('#mhPackGo'); page.wait_for_timeout(400)
    lib = page.evaluate("loadLibrary()")
    yo = [x for x in lib if x['name'].lower().startswith('greek')]
    if len(yo) != 1 or yo[0]['kcal'] != 999 or not yo[0]['locked']: f.add('BUG', f'merge overwrote or duplicated an existing food: {yo}')
    al = [x for x in lib if x['name'].lower().startswith('almond')]
    if len(al) != 1 or al[0].get('locked') or al[0].get('source') != 'from pack': f.add('BUG', f'new food should arrive unlocked and marked: {al}')
    sy = page.evaluate("loadSymptomDefs()")
    if sorted(x['name'] for x in sy) != ['Fatigue', 'Headache', 'Nausea']: f.add('BUG', f'symptoms merge wrong: {sy}')
    ids = [x['id'] for x in sy]
    if len(set(ids)) != len(ids): f.add('BUG', 'duplicate symptom ids after merge')
    fat = [x for x in sy if x['name'] == 'Fatigue'][0]['id']
    rp = page.evaluate("loadReportProfiles()")
    if not rp or rp[0].get('lastSent') or rp[0]['symptomIds'] != [fat]: f.add('BUG', f'report profile ids not remapped / lastSent kept: {rp}')
    if rp and rp[0]['treatmentId'] != page.evaluate("loadTreatmentDefs()[0].id"): f.add('BUG', 'report profile treatment id not remapped')
    tw = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware'))")
    if tw['sets'][0]['vals']['dinner_plate']['diam'] != 30: f.add('BUG', 'merge overwrote my Home plate size')
    if not any(s['name'] == 'Holiday' for s in tw['sets']) or not tw['custom']: f.add('BUG', 'tableware set/item not merged in')
    # Replace path
    page.evaluate("window.confirm = () => true; document.getElementById('mhPackModal')?.remove();")
    page.evaluate("p => mhPackPreview(p)", pack); page.wait_for_timeout(200)
    page.evaluate("document.querySelector('input[name=mhPackMode][value=replace]').click(); document.querySelectorAll('.mhPackPick').forEach(i => { if (i.value !== 'library') i.checked = false; })")
    page.click('#mhPackGo'); page.wait_for_timeout(300)
    lib = page.evaluate("loadLibrary()")
    if sorted(x['name'] for x in lib) != ['Almonds', 'Greek Yoghurt'] or any(x['locked'] for x in lib): f.add('BUG', f'replace result wrong: {lib}')
    # Reject non-pack
    page.evaluate("document.getElementById('mhPackModal')?.remove()")
    page.evaluate("""() => { const dt = new DataTransfer(); dt.items.add(new File(['{"hello":1}'], 'x.json', {type:'application/json'})); mhPackImportFile(dt.files[0]); }"""); page.wait_for_timeout(300)
    if page.query_selector('#mhPackModal'): f.add('BUG', 'a non-pack JSON opened the preview')
    # Picker lists the new sets
    page.evaluate("switchTab('import')"); page.wait_for_timeout(500)
    opts = page.evaluate("[...document.querySelectorAll('#bulkDatasetSelect option')].map(o => o.value)")
    for k in ('symptoms', 'treatments', 'reports', 'tableware'):
        if k not in opts: f.add('BUG', f'picker missing {k}')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
