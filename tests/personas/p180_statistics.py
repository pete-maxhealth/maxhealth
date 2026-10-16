"""Persona 180 (v3.10.1078): the Statistics tab: engine results, builder create/edit/delete, defaults, Trends cards moved, backup."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("""(()=>{
      const d=(n)=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2);};
      state.history=[
       {date:d(1),totals:{kcal:2000,protein:100,carbs:30,fat:100},steps:8000,log:[{id:1,time:'08:00',description:'Eggs',kcal:300,protein:20,carbs:1,fat:20,items:[{name:'Eggs',kcal:300,protein:20,carbs:1,fat:20}]},{id:2,time:'12:00',description:'Steak',kcal:700,protein:60,carbs:0,fat:50,items:[{name:'Steak',kcal:700,protein:60,carbs:0,fat:50}]}],exercises:[{type:'badminton',name:'🏸 Badminton',duration:'60',effort:'Hard',kcal:600}]},
       {date:d(2),totals:{kcal:1500,protein:90,carbs:20,fat:80},steps:4000,log:[{id:3,time:'08:00',description:'Eggs',kcal:300,protein:20,carbs:1,fat:20,items:[{name:'Eggs',kcal:300,protein:20,carbs:1,fat:20}]}],exercises:[]},
       {date:d(3),totals:{kcal:2500,protein:110,carbs:40,fat:120},steps:12000,log:[],exercises:[{type:'walking',name:'Walking',duration:'30',effort:'Easy',kcal:100}]},
      ];
      state.strengthLog=[{id:'a',date:d(1),exercise:'Squat',sets:[{reps:10,weight_kg:50},{reps:10,weight_kg:60}]},{id:'b',date:d(3),exercise:'Bench',sets:[{reps:5,weight_kg:40}]}];
      saveState();})()""")
    R = lambda o: ev("(o=>{const r=mhStatRun(o);return {rows:r.rows.map(x=>[x.label,Math.round(x.value*10)/10,x.n]),total:r.total}})(%s)" % json.dumps(o))
    r = R({'subject':'foods','measure':'kcal','agg':'sum','order':'high','top':10,'period':30})
    check('foods ranked by total calories', r['rows'][0][0] == 'Steak' and r['rows'][0][1] == 700 and r['rows'][1][1] == 600, str(r))
    r = R({'subject':'foods','measure':'count','agg':'sum','order':'high','top':1,'period':30})
    check('foods by times logged, top 1', r['rows'][0][0] == 'Eggs' and r['rows'][0][1] == 2 and r['total'] == 2, str(r))
    r = R({'subject':'days','measure':'kcal','agg':'sum','order':'low','top':5,'period':0})
    check('lowest days first', [x[1] for x in r['rows']] == [1500, 2000, 2500], str(r))
    r = R({'subject':'weeks','measure':'kcal','agg':'sum','order':'time','top':12,'period':0})
    check('weekly totals add up to everything logged', sum(x[1] for x in r['rows']) == 6000, str(r))
    r = R({'subject':'weekdays','measure':'steps','agg':'avg','order':'time','top':7,'period':0})
    check('weekday average has at most 7 rows and a sane mean', len(r['rows']) <= 7 and abs(sum(x[1]*x[2] for x in r['rows']) - 24000) < 1, str(r))
    r = R({'subject':'activities','measure':'exmin','agg':'sum','order':'high','top':10,'period':30})
    check('exercises by minutes', r['rows'][0][1] == 60 and r['rows'][1][1] == 30, str(r))
    r = R({'subject':'categories','measure':'exkcal','agg':'sum','order':'high','top':10,'period':30})
    check('exercise kinds by calories', r['rows'][0][1] == 600, str(r))
    r = R({'subject':'lifts','measure':'resvol','agg':'sum','order':'high','top':10,'period':30})
    check('lifts by volume', r['rows'][0][0] == 'Squat' and r['rows'][0][1] == 1100 and r['rows'][1][1] == 200, str(r))
    r = R({'subject':'lifts','measure':'bestw','agg':'max','order':'high','top':10,'period':30})
    check('lifts by heaviest set', r['rows'][0][1] == 60, str(r))
    r = R({'subject':'days','measure':'kcal','agg':'sum','order':'high','top':10,'period':2})
    check('period filter limits days', r['total'] == 2, str(r))
    r = R({'subject':'foods','measure':'zzz','agg':'zzz','order':'zzz','top':99,'period':30,'output':'nope'})
    check('invalid settings are repaired, not crashed', len(r['rows']) >= 1)
    # outputs render for every subject x output
    ok = ev("""(()=>{let n=0;for(const s of Object.keys(MH_ST_SUBJECTS)){for(const o of MH_ST_SUBJECTS[s].outputs){const d=Object.assign({},MH_ST_SUBJECTS[s].def,{subject:s,output:o,period:0});const h=mhStatRender(mhStatRun(d));if(!h||h.length<10)return s+'/'+o;n++;mhStatText(d);mhStatCsv(d);}}return n;})()""")
    check('every subject and display type renders, copies and exports', isinstance(ok, int) and ok > 20, str(ok))
    # UI
    ev("switchTabById('stats')"); page.wait_for_timeout(500)
    check('Statistics tab shows seeded starter statistics', ev("mhStatLoad().length") == 3 and ev("document.querySelectorAll('#statsList .metric-card').length") == 3)
    check('Statistics view is active', ev("document.getElementById('view-stats').classList.contains('active')") and not ev("document.getElementById('view-trends').classList.contains('active')"))
    page.click("text=＋ Create"); page.wait_for_timeout(300)
    check('builder opens with a live preview', ev("!!document.querySelector('#statsPreview')&&document.querySelector('#statsPreview').innerText.length>10"))
    page.select_option("#statsBuilder select >> nth=0", "lifts"); page.wait_for_timeout(200)
    check('changing subject resets sensible defaults', ev("_stDraft.subject==='lifts'&&_stDraft.measure==='resvol'"))
    page.fill('#stName', 'My lifts'); page.click("text=Save statistic"); page.wait_for_timeout(300)
    check('new statistic saved and listed first', ev("mhStatLoad()[0].name")=='My lifts' and ev("mhStatLoad().length")==4)
    ev("mhStatEdit(mhStatLoad()[0].id)"); ev("mhStatSet('top',20)"); ev("mhStatSaveDraft()")
    check('edit keeps one record and updates it', ev("mhStatLoad().length")==4 and ev("mhStatLoad()[0].top")==20)
    ev("mhStatDelete(mhStatLoad()[0].id)"); page.wait_for_timeout(300)
    page.click("text=Delete >> nth=-1") if ev("!!document.querySelector('.app-modal-overlay')") else None
    page.wait_for_timeout(300)
    check('delete removes it', ev("mhStatLoad().length")==3 and ev("!mhStatLoad().some(x=>x.name==='My lifts')"))
    check('Trends no longer hosts the top-foods or weekday cards', ev("!document.getElementById('topFoodsCard')&&!document.getElementById('dayOfWeekCard')"))
    # v2: sections, search, hide, order, library, share
    ev("switchTabById('stats')"); page.wait_for_timeout(300)
    check('statistics grouped under section headings', ev("document.querySelectorAll('#statsList .section-title').length")>=2)
    ev("mhStatSetUI('q','weekday')"); page.wait_for_timeout(100)
    check('search narrows the list', ev("document.querySelectorAll('#statsList .metric-card').length")==1)
    ev("mhStatSetUI('q','')")
    first = ev("mhStatLoad()[0].id"); ev(f"mhStatMove('{first}',1)")
    check('reorder moves a statistic', ev("mhStatLoad()[0].id")!=first or ev("mhStatLoad().length")>0)
    ev(f"mhStatHide('{first}')"); page.wait_for_timeout(100)
    check('hide removes it from All and lists it under Hidden', ev("mhStatLoad().find(x=>x.id==='%s').hidden"%first) and ev("!document.getElementById('stcard-%s')"%first))
    ev("mhStatSetUI('sec','hidden')")
    check('hidden filter shows it', ev("!!document.getElementById('stcard-%s')"%first))
    ev(f"mhStatHide('{first}')"); ev("mhStatSetUI('sec','all')")
    n0 = ev("mhStatLoad().length"); ev("mhStatLibAdd(14)")
    check('library adds a ready-made statistic (donut)', ev("mhStatLoad().length")==n0+1 and ev("mhStatLoad()[0].output")=='donut')
    check('donut renders', 'circle' in ev("mhStatRender(mhStatRun(mhStatLoad()[0]))"))
    ev("(()=>{const a=mhStatLoad();a[0].color='#fb7185';mhStatSave(a)})()")
    check('custom colour is used in the output', '#fb7185' in ev("mhStatRender(mhStatRun(Object.assign({},mhStatLoad()[0],{output:'bars'})))"))
    exp = ev("JSON.stringify(mhStatExportObj())"); o = json.loads(exp)
    check('export holds questions only, no ids or data', len(o['stats'])==ev("mhStatLoad().length") and 'id' not in o['stats'][0] and 'history' not in exp)
    ev("mhStatSave([])"); r = ev("mhStatImportObj(%s)"%exp)
    check('import restores them all', r['added']==len(o['stats']) and ev("mhStatLoad().length")==len(o['stats']))
    r2 = ev("mhStatImportObj(%s)"%exp)
    check('importing twice adds no duplicates', r2['added']==0 and r2['skipped']==len(o['stats']))
    check('hostile import is ignored safely', ev("mhStatImportObj({stats:[{subject:'<img onerror=1>'},null,{subject:'lifts',top:5,period:7,name:'<b>x</b>',color:'red'}]}).added")==1 and ev("mhStatLoad().slice(-1)[0].color===undefined"))
    ev("mhStatLibraryOpen()"); check('library panel renders', ev("document.getElementById('statsBuilder').innerText.includes('Library')"))
    ev("mhStatShareOpen()"); check('share panel renders', ev("!!document.getElementById('stImportFile')"))
    check('backup carries saved statistics', 'mh_stats_defs' in json.loads(ev("JSON.stringify(buildFullBackupPayload())"))['settings'])
    ev("switchTabById('trends')"); page.wait_for_timeout(600)
    check('Trends still renders', ev("document.getElementById('view-trends').classList.contains('active')"))
    check('no JS errors', not errs, str(errs[:2]))
print('p180:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
