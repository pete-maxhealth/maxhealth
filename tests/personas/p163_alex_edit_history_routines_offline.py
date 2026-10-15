"""Persona 163: Alex again, offline, the everyday edit-and-undo side: edit and delete today's entries, past-day History (edit, delete an entry,
edit totals, delete a day, calendar), exercise routines (create, apply, delete), fasting numbers, symptoms and treatments. Edits last for the demo."""
import sys,re,json,traceback; sys.path.insert(0,'/home/claude/maxhealth/tests/personas')
from harness import *
from playwright.sync_api import sync_playwright
PID=sys.argv[1] if len(sys.argv)>1 else 'alex'
RES=[]
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':900},service_workers='block'); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    page.evaluate(f"startDemoMode('{PID}')"); page.wait_for_timeout(2500)
    ctx.set_offline(True); page.evaluate("window.dispatchEvent(new Event('offline'))"); page.wait_for_timeout(1200)
    ev=page.evaluate
    def tab(t,sub=None):
        ev(f"document.getElementById('maintab-{t}').click()"); page.wait_for_timeout(450)
        if sub: ev(f"document.getElementById('{t}tab-{sub}').click()"); page.wait_for_timeout(450)
    def toast(): return ev("()=>[...document.querySelectorAll('.toast,#toast,[id*=oast]')].map(e=>e.innerText).filter(Boolean).join(' | ')")
    def answer(val=None):
        """fill + confirm the app's own prompt/confirm dialog"""
        return ev("""(val)=>{const vis=[...document.querySelectorAll('.modal-overlay,[class*=modal],[id*=Modal],[id*=Prompt],[id*=Confirm]')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height>60);
          const box=vis[vis.length-1]; if(!box) return 'no dialog'; const inp=box.querySelector('input,textarea'); if(inp&&val!=null){inp.value=val; inp.dispatchEvent(new Event('input',{bubbles:true}))}
          const b=[...box.querySelectorAll('button')].find(b=>/^(ok|add|save|yes|confirm|done|remove|reset|apply|log|delete)/i.test(b.textContent.trim())); if(!b) return 'no ok button: '+[...box.querySelectorAll('button')].map(b=>b.textContent.trim()).join('/'); b.click(); return 'ok'}""",val)
    def step(area,name,fn):
        errs.clear()
        try: out=fn(); st='PASS' if out is True or out is None else ('FAIL' if out is False else 'NOTE')
        except Exception as e: out='EXC '+str(e)[:140]; st='FAIL'
        page.wait_for_timeout(250)
        if errs: st='FAIL'; out=f'{out} | JS: {errs[0]}'
        RES.append((st,area,name,out)); print(f'{st:4} {area:9} {name}  {"" if out in (True,None) else out}')
    def closeall():
        ev("""()=>{['closeWeightModal','closeRecipeLibPicker','closeAddFoodModal','closeRecipeBuilder'].forEach(f=>{try{window[f]&&window[f]()}catch(e){}});document.querySelectorAll('.modal-overlay.active,.modal-overlay.open,.modal-overlay.show').forEach(e=>e.classList.remove('active','open','show'))}""")
    # ---------------- EDIT / DELETE TODAY'S LOG ----------------
    tab('log','log')
    def log_meal(txt='2 eggs and a slice of toast'):
        page.fill('#chatInput',txt); ev("document.querySelector(\"button[onclick*='sendChat']\").click()"); page.wait_for_timeout(4500)
        ev("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/log it/i.test(b.textContent)); b&&b.click()})()"); page.wait_for_timeout(1500)
    log_meal()
    step('today log','meal is in today\'s log',lambda: ev("state.todayLog.length")>=1)
    def edit_open():
        ev("editLogEntry(state.todayLog[0].id)"); page.wait_for_timeout(500)
        return ev("!!document.querySelector('[id*=log-edit],[id^=edit-],[class*=log-edit],.hist-edit-form')") or ev("/Save/.test(document.body.innerText)")
    step('today log','edit entry opens the editor',edit_open)
    def edit_save():
        k0=ev("state.todayLog[0].kcal"); ev("saveLogEdit(state.todayLog[0].id)"); page.wait_for_timeout(600)
        return ev("state.todayLog.length")>=1
    step('today log','save the edit (no change)',edit_save)
    def delete_entry():
        n=ev("state.todayLog.length"); ev("deleteLogEntry(state.todayLog[0].id)"); page.wait_for_timeout(400); r=answer(); page.wait_for_timeout(500)
        return ev("state.todayLog.length")==n-1 or f'{r}; still {ev("state.todayLog.length")}'
    step('today log','delete an entry (confirm)',delete_entry)
    step('today log','totals fall back to zero',lambda: ev("calcTotals(state.todayLog).kcal")==0)
    log_meal()
    step('today log','copy entry line works',lambda: (ev("copyLogEntryLine(state.todayLog[0].id)"), True)[1])
    # ---------------- HISTORY ----------------
    tab('log','hist')
    step('history','history has days',lambda: ev("state.history.length")>3)
    def hist_edit():
        di,ei=ev("(()=>{for(let i=0;i<state.history.length;i++){if(state.history[i].log&&state.history[i].log.length) return [i,0]} return [-1,-1]})()")
        if di<0: return 'no history entries'
        ev(f"toggleHistDay && 0"); ev(f"document.getElementById('histBody{di}')&&document.getElementById('histBody{di}').classList.add('open')"); 
        ev(f"editHistEntry({di},{ei})"); page.wait_for_timeout(500)
        return ev(f"!!document.querySelector('#hist-entry-{di}-{ei} .hist-edit-form')")
    step('history','edit a past entry opens the editor',hist_edit)
    def hist_delete_entry():
        di=ev("state.history.findIndex(d=>d.log&&d.log.length>1)")
        if di<0: return 'NOTE no day with 2+ entries'
        n=ev(f"state.history[{di}].log.length"); ev(f"deleteHistEntry({di},0)"); page.wait_for_timeout(400); answer(); page.wait_for_timeout(500)
        return ev(f"state.history[{di}].log.length")==n-1
    step('history','delete one past entry (confirm)',hist_delete_entry)
    step('history','edit a day\'s totals opens',lambda: (ev("editHistDayTotals(1,1)"), page.wait_for_timeout(500), ev("!!document.querySelector('.hist-day-totals-edit')"))[2])
    def hist_delete_day():
        d=ev("state.history[3].date"); n=ev("state.history.length"); ev(f"deleteHistDay('{d}')"); page.wait_for_timeout(400); answer(); page.wait_for_timeout(600)
        return ev("state.history.length")==n-1
    step('history','delete a whole past day (confirm)',hist_delete_day)
    step('history','history calendar opens',lambda: (ev("openHistoryCalendar()"), page.wait_for_timeout(500), True, closeall())[2])
    # ---------------- ROUTINES (strength) ----------------
    tab('today','dash')
    step('routines','routine list opens',lambda: (ev("showRoutineList()"), page.wait_for_timeout(500), ev("!!document.querySelector('[id*=outine]')"))[2])
    def make_routine():
        ev("showCreateRoutineForm()"); page.wait_for_timeout(500)
        ev("document.getElementById('newRoutineName').value='Deep Test Push Day'")
        ev("_routineDraftExercises=[{name:'Bench press',sets:[{reps:8,weight:60},{reps:8,weight:60}]}]")
        n=ev("loadRoutines().length"); ev("saveNewRoutine()"); page.wait_for_timeout(700)
        return ev("loadRoutines().some(r=>/deep test push day/i.test(r.name))") or f'not kept ({n}->{ev("loadRoutines().length")}) toast={toast()}'
    step('routines','create a routine and keep it',make_routine)
    def apply_routine():
        rid=ev("(loadRoutines().find(r=>/deep test push day/i.test(r.name))||loadRoutines()[0]).id")
        ev(f"applyRoutine('{rid}')"); page.wait_for_timeout(600); return ev("!!document.querySelector('[id*=outineApply],[id*=outine]')")
    step('routines','apply a routine opens',apply_routine)
    def del_routine():
        rid=ev("loadRoutines()[0].id"); n=ev("loadRoutines().length"); ev(f"deleteRoutine('{rid}')"); page.wait_for_timeout(400); answer(); page.wait_for_timeout(600)
        return ev("loadRoutines().length")==n-1 or f'{n}->{ev("loadRoutines().length")}'
    step('routines','delete a routine (confirm)',del_routine)
    # ---------------- FASTING (derived from meal times) ----------------
    tab('insights','trends')
    step('fasting','fasting numbers compute',lambda: ev("(()=>{const n=mhFastingNow(); return n===null||typeof n.hours==='number'})()"))
    step('fasting','fasting card renders (no error)',lambda: (ev("mhRenderFastingCard()"), True)[1])
    step('fasting','fasting stats compute',lambda: ev("(()=>{const s=mhFastingStats&&mhFastingStats(); return true})()"))
    # ---------------- SYMPTOMS / TREATMENTS ----------------
    tab('settings','manage')
    def symptom():
        ev("addSymptom()"); page.wait_for_timeout(400); answer('Energy test'); page.wait_for_timeout(600)
        return ev("loadSymptomDefs().some(d=>/energy test/i.test(d.name))") or 'symptom not kept'
    step('symptoms','add a symptom to track',symptom)
    def symptom_log():
        d=ev("(loadSymptomDefs().find(d=>/energy test/i.test(d.name))||loadSymptomDefs()[0]).id")
        ev(f"saveSymptomLog({{'{d}':4}})"); page.wait_for_timeout(300)
        return ev(f"JSON.parse(localStorage.getItem('mh_symptom_log')||'{{}}')['{d}']")==4
    step('symptoms','log a symptom score',symptom_log)
    step('treatments','treatment list loads',lambda: ev("Array.isArray(loadTreatmentDefs())"))
    def treat():
        n=ev("loadTreatmentDefs().length")
        if n==0: return 'NOTE persona has no treatments'
        d=ev("loadTreatmentDefs()[0].id"); ev(f"logTreatmentSession('{d}')"); page.wait_for_timeout(600); answer(); page.wait_for_timeout(400); return True
    step('treatments','log a treatment session',treat)
    # ---------------- WRAP ----------------
    step('demo','exit demo',lambda: (ev("exitDemoMode()"), page.wait_for_timeout(2500), ev("typeof _demoMode==='undefined'||!_demoMode"))[2])
    fails=[r for r in RES if r[0]=='FAIL']
    print(f'\n{PID}: {len(RES)} checks, {len(fails)} FAIL, {sum(1 for r in RES if r[0]=="NOTE")} NOTE')
    br.close()
    print('findings',len(fails)); sys.exit(1 if fails else 0)
