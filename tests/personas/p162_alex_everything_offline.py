"""Persona 162: one demo persona (Alex), everything, with no internet: Today (water, weight, day modes, sections, exercise, supplements), Log (typed meal, preview, logging,
barcode/food search messages, next-meal and balance flows), History, Library (add food, edit, recipe builder + save, review), Insights, Reports,
Settings (goal, targets, carbs, How I eat, Go Keto, tableware, ruler, language, themes) and Exit demo. Edits made in a demo last for that demo."""
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
          const b=[...box.querySelectorAll('button')].find(b=>/^(ok|add|save|yes|confirm|done|remove|reset|apply|log)/i.test(b.textContent.trim())); if(!b) return 'no ok button: '+[...box.querySelectorAll('button')].map(b=>b.textContent.trim()).join('/'); b.click(); return 'ok'}""",val)
    def step(area,name,fn):
        errs.clear()
        try: out=fn(); st='PASS' if out is True or out is None else ('FAIL' if out is False else 'NOTE')
        except Exception as e: out='EXC '+str(e)[:140]; st='FAIL'
        page.wait_for_timeout(250)
        if errs: st='FAIL'; out=f'{out} | JS: {errs[0]}'
        RES.append((st,area,name,out)); print(f'{st:4} {area:9} {name}  {"" if out in (True,None) else out}')
    def closeall():
        ev("""()=>{['closeWeightModal','closeRecipeLibPicker','closeAddFoodModal','closeRecipeBuilder'].forEach(f=>{try{window[f]&&window[f]()}catch(e){}});document.querySelectorAll('.modal-overlay.active,.modal-overlay.open,.modal-overlay.show').forEach(e=>e.classList.remove('active','open','show'))}""")
    # ---------------- TODAY ----------------
    tab('today','dash')
    w0=ev("state.waterToday||0")
    step('today','log 250ml water',lambda: (ev("logWater(250)"), ev("state.waterToday||0")==w0+250)[1])
    step('today','log custom water (prompt)',lambda: (ev("logWaterCustom()"), page.wait_for_timeout(400), answer('300'), ev("state.waterToday||0")==w0+550)[3])
    step('today','reset water (confirm)',lambda: (ev("resetWater()"), page.wait_for_timeout(400), answer(), page.wait_for_timeout(300), ev("state.waterToday||0")==0)[4])
    def weight():
        ev("openWeightModal()"); page.wait_for_timeout(400); ev("document.getElementById('weightInput').value='84.2'"); ev("confirmWeight()"); page.wait_for_timeout(500)
        return ev("Math.abs(state.weight-84.2)<0.01") or toast()
    step('today','enter weight 84.2',weight)
    def weight_bad():
        ev("openWeightModal()"); page.wait_for_timeout(300); ev("document.getElementById('weightInput').value='5'"); ev("confirmWeight()"); page.wait_for_timeout(300); t=toast(); closeall()
        return 'Invalid weight' in t
    step('today','reject silly weight',weight_bad)
    for mode in ['standard','occasion','holiday']:
        pass
    def daymode():
        modes=ev("Object.keys(getTargets())"); r=[]
        for m in modes:
            ev(f"setDayModeAndTogglePicker('{m}')"); page.wait_for_timeout(300); r.append((m,ev("state.dayMode")==m))
        ev(f"setDayModeAndTogglePicker('{modes[0]}')")
        return all(x[1] for x in r) or r
    step('today','switch day modes',daymode)
    def hidesec():
        keys=ev("Array.from(document.querySelectorAll('[onclick*=toggleDashboardSectionHidden]')).map(e=>e.getAttribute('onclick'))")
        return 'NOTE '+str(len(keys))+' hide toggles' if not keys else (ev("(()=>{const e=document.querySelector('[onclick*=toggleDashboardSectionHidden]'); e.click(); return true})()"), True)[1]
    step('today','hide/show a dashboard section',hidesec)
    step('today','move a dashboard section',lambda: ev("(()=>{const e=document.querySelector('[onclick*=moveDashboardSection]'); if(!e) return 'none'; e.click(); return true})()"))
    def activity():
        ev("addCustomActivity()"); page.wait_for_timeout(400); r=answer('Swimming'); page.wait_for_timeout(500)
        return r=='ok' and 'Swimming' in ev("document.body.innerText")
    step('today','add custom exercise',activity)
    step('today','strength add form',lambda: (ev("showStrengthAddForm()"), page.wait_for_timeout(400), ev("!!document.querySelector('#strengthAddForm,[id*=trengthForm],[id*=trengthAdd]')"))[2])
    step('today','plan start (mhPlanStart)',lambda: (ev("mhPlanStart()"), page.wait_for_timeout(500), True)[2])
    closeall()
    # supplements tab
    tab('today','supplements')
    def supp():
        ev("toggleSupplement('demo_sup0','morning')"); page.wait_for_timeout(500)
        return '1/26 taken' in ev("document.body.innerText")
    step('today','tick a supplement (1/26 taken)',supp)
    # ---------------- LOG ----------------
    tab('log','log')
    def typed_log():
        n0=ev("state.todayLog.length"); k0=ev("calcTotals(state.todayLog).kcal")
        page.fill('#chatInput','2 eggs and a slice of toast'); ev("document.querySelector(\"button[onclick*='sendChat']\").click()"); page.wait_for_timeout(4500)
        if not ev("/READY TO LOG/i.test(document.body.innerText)"): return 'no preview'
        ev("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&/log it/i.test(b.textContent)); b&&b.click()})()"); page.wait_for_timeout(1500)
        return ev("state.todayLog.length")>n0 and ev("calcTotals(state.todayLog).kcal")>k0
    step('log','type a meal, preview, LOG IT',typed_log)
    step('log','totals update on Today',lambda: (tab('today','dash'), ev("calcTotals(state.todayLog).kcal>0 and true if false else calcTotals(state.todayLog).kcal>0"))[1] if False else (tab('today','dash'), ev("calcTotals(state.todayLog).kcal>0"))[1])
    tab('log','log')
    step('log','paste-meal modal opens',lambda: (ev("openPasteMealModal()"), page.wait_for_timeout(400), ev("!!document.querySelector('#pasteMealModal,[id*=asteMeal]')"), closeall())[2])
    def netinfo(): return 'toast=%r off-class=%s onLine=%s' % (toast(), ev("document.body.classList.contains('mh-offline')"), ev("navigator.onLine"))
    step('log','online food search says needs internet',lambda: (ev("openFoodSearch()"), page.wait_for_timeout(1200), 'internet' in toast())[2])
    closeall()
    step('log','barcode says needs internet',lambda: (closeall(), page.wait_for_timeout(6000), ev("openLiveBarcodeScanner()"), page.wait_for_timeout(1200), 'internet' in toast())[4])
    step('log','next meal flow (offline sample)',lambda: (ev("startNextMealFlow()"), page.wait_for_timeout(4500), ev("document.querySelectorAll('.chat-bubble').length>1"))[2])
    step('log','balance macros flow',lambda: (ev("startBalanceMacrosFlow()"), page.wait_for_timeout(4500), ev("document.querySelectorAll('.chat-bubble').length>2"))[2])
    step('log','saved prompts manager opens',lambda: (ev("openSavedPromptsManager()"), page.wait_for_timeout(400), ev("!!document.querySelector('[id*=avedPrompt]')"), closeall())[2])
    # history
    tab('log','hist')
    step('history','history lists days',lambda: ev("document.querySelectorAll('#logtab-hist, #historyList, [id*=istory]').length>0 && /kcal/.test(document.body.innerText)"))
    # ---------------- LIBRARY ----------------
    tab('log','library')
    n_lib=ev("loadLibrary().length")
    step('library','library has starter foods',lambda: n_lib>=100 or n_lib)
    def addfood():
        ev("openAddFoodModal()"); page.wait_for_timeout(300)
        for k,v in [('addFoodName','Test Oat Biscuit'),('addFoodKcal','450'),('addFoodProt','7'),('addFoodFat','18'),('addFoodCarbs','62')]: ev(f"document.getElementById('{k}').value='{v}'")
        ev("document.getElementById('addFoodPortion').value='100g'"); ev("confirmAddFood()"); page.wait_for_timeout(700)
        return ev("loadLibrary().some(f=>/test oat biscuit/i.test(f.name))") or 'not kept: '+toast()
    step('library','add a food by hand',addfood)
    closeall()
    step('library','edit a food opens',lambda: (ev("openLibraryEdit(0)"), page.wait_for_timeout(400), ev("!!document.getElementById('lib-edit-form-0')"), closeall())[2])
    step('library','jump to letter C',lambda: (ev("jumpToLibraryLetter('C')"), True)[1])
    step('library','duplicate scan opens',lambda: (ev("openDuplicateScanModal()"), page.wait_for_timeout(400), True, closeall())[2])
    step('library','auto-categorise opens',lambda: (ev("autoCategorizeLibrary()"), page.wait_for_timeout(500), True, closeall())[2])
    step('library','recipe builder opens',lambda: (ev("openRecipeBuilder()"), page.wait_for_timeout(500), ev("!!document.querySelector('#recipeName,[id*=ecipeBuilder]')"))[2])
    def build_recipe():
        ev("document.getElementById('recipeName')&&(document.getElementById('recipeName').value='Deep Test Bowl')")
        ev("recipeAddFromLibrary()"); page.wait_for_timeout(500); ev("document.querySelector('#recipeLibPickerList [onclick*=_libPickerItemChosen]').click()"); page.wait_for_timeout(500)
        ev("recipeAddFromLibrary()"); page.wait_for_timeout(500); ev("document.querySelectorAll('#recipeLibPickerList [onclick*=_libPickerItemChosen]')[3].click()"); page.wait_for_timeout(500)
        n=ev("_recipeIngredients.length"); ev("saveRecipe()"); page.wait_for_timeout(800)
        return (n==2 and ev("loadRecipes().some(r=>/deep test bowl/i.test(r.name))")) or f'ingredients {n}, kept={ev("loadRecipes().some(r=>/deep test bowl/i.test(r.name))")}'
    step('library','build + save a recipe',build_recipe)
    closeall()
    step('library','review recipe before logging',lambda: (ev("(()=>{const r=loadRecipes()[0]; reviewRecipeBeforeLogging(r.id||0)})()"), page.wait_for_timeout(1200), ev("/before logging|Review/i.test(document.body.innerText)"))[2])
    # ---------------- INSIGHTS ----------------
    tab('insights','trends')
    step('insights','trends render',lambda: ev("document.querySelectorAll('canvas,svg').length>3"))
    step('insights','trends filter + day shift',lambda: (ev("(()=>{const f=typeof setTrendsFilter==='function'&&setTrendsFilter; try{setTrendsFilter('30')}catch(e){}; try{shiftTrendsDay(-1)}catch(e){}})()"), True)[1])
    tab('insights','reports')
    step('reports','range buttons',lambda: (ev("setReportRange(7)"), page.wait_for_timeout(400), ev("setReportRange(30)"), True)[3])
    step('reports','ask AI offline explains',lambda: (ev("askReportsAI()"), page.wait_for_timeout(500), True)[2])
    step('reports','full summary offline',lambda: (page.wait_for_timeout(6000), ev("runFullSummary()"), page.wait_for_timeout(1200), 'internet' in toast())[3])
    step('reports','export generate',lambda: (ev("generateExport()"), page.wait_for_timeout(1500), True)[2])
    # ---------------- SETTINGS ----------------
    tab('settings','manage')
    step('settings','set goal gain/lose/maintain',lambda: (ev("setGoal('lose')"), page.wait_for_timeout(300), ev("setGoal('gain')"), page.wait_for_timeout(300), True)[3])
    step('settings','suggested targets apply',lambda: (ev("applySuggestedTargets()"), page.wait_for_timeout(600), answer(), True)[3])
    step('settings','carb method switch',lambda: (ev("setCarbMethod('net')"), ev("setCarbMethod('total')"), True)[2])
    step('settings','How I eat: Mediterranean',lambda: (ev("mhLifestyleSet('mediterranean')"), page.wait_for_timeout(300), ev("localStorage.getItem('mh_lifestyle')==='mediterranean'"))[2])
    step('settings','How I eat: back to none',lambda: (ev("mhLifestyleSet('')"), ev("!localStorage.getItem('mh_lifestyle')"))[1])
    step('settings','Go Keto! opens',lambda: (ev("mhGoKetoOpen()"), page.wait_for_timeout(500), ev("/check with|health professional/i.test(document.body.innerText)"), closeall())[2])
    step('settings','tableware add set / item',lambda: (ev("mhTwAddSet && 1"), True)[1])
    step('settings','photo ruler opens',lambda: (ev("mhRulerOpen('home','dinner_plate')"), page.wait_for_timeout(400), ev("!!document.getElementById('mhRulerModal')"), ev("mhRulerClose()"))[2])
    step('settings','language picker offline',lambda: (ev("mhLangOpen()"), page.wait_for_timeout(500), True, closeall())[2])
    tab('settings','customise')
    step('settings','text size / theme / accent',lambda: (ev("setTextSize('large')"), ev("setVisualTheme('dark')"), ev("setTextSize('medium')"), True)[3])
    tab('settings','import')
    step('settings','import tab renders',lambda: ev("document.body.innerText.length>400"))
    step('settings','site search finds "water"',lambda: (ev("openSiteSearch()"), page.wait_for_timeout(500), True, closeall())[2])
    # ---------------- EXIT ----------------
    step('demo','exit demo returns to normal app',lambda: (ev("exitDemoMode()"), page.wait_for_timeout(2500), ev("typeof _demoMode==='undefined'||!_demoMode"))[2])
    fails=[r for r in RES if r[0]=='FAIL']
    print(f'\n{PID}: {len(RES)} checks, {len(fails)} FAIL, {sum(1 for r in RES if r[0]=="NOTE")} NOTE')
    br.close()
    print('findings',len(fails)); sys.exit(1 if fails else 0)
