"""Persona 196: Fibre card on Today (target default 30g, editable), honest 'not enough days' rule, show/hide and reorder, migration of an old saved order, and the nutrient audit (coverage, save, 'no fibre', unknown never filled in)."""
import sys, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    # an old saved order without the fibre card must be migrated, not thrown away
    old = ev("DEFAULT_DASHBOARD_ORDER.filter(k=>k!=='fibre').reverse()")
    ev("o=>localStorage.setItem('mh_dashboard_order', JSON.stringify(o))", old)
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    got = ev("getDashboardOrder()")
    if 'fibre' not in got: f.add('BUG', 'fibre not migrated into saved order')
    if got[:3] != [k for k in old if k != 'fibre'][:3] and got[0] != old[0]: f.add('BUG', f'custom order lost {got[:4]}')
    ev("localStorage.removeItem('mh_dashboard_order')")
    # empty state
    ev("state.todayLog=[]; state.history=[]; updateDashboard()")
    if '30g' not in ev("document.getElementById('fibreTarget').textContent"): f.add('BUG', 'default target not 30g')
    if 'not enough days' not in ev("document.getElementById('fibreNote').textContent"): f.add('BUG', 'no not-enough-days note')
    # today's total, only foods with a figure count
    ev("state.todayLog=[{id:1,time:'08:00',description:'Chia',name:'Chia',kcal:100,protein:3,carbs:8,fat:6,fibre:10},{id:2,time:'09:00',description:'Eggs',name:'Eggs',kcal:150,protein:12,carbs:1,fat:10,fibre:0}]; updateDashboard()")
    if ev("document.getElementById('fibreAmount').textContent") != '10g': f.add('BUG', 'today total wrong')
    if '1 of 2' not in ev("document.getElementById('fibreNote').textContent"): f.add('BUG', 'figure coverage note missing')
    # target change
    ev("document.getElementById('settingFibreTarget').value='25'; saveFibreTarget()")
    if '25g' not in ev("document.getElementById('fibreTarget').textContent"): f.add('BUG', 'target change not applied')
    # 14-day average needs 5 days
    ev("""(()=>{const h=[];for(let i=1;i<=6;i++){const d=new Date();d.setDate(d.getDate()-i);const iso=d.toISOString().slice(0,10);
      h.push({date:iso.slice(8,10)+'/'+iso.slice(5,7)+'/'+iso.slice(2,4),log:[{id:i,time:'12:00',name:'x',kcal:100,fibre:i<=4?20:0}],totals:{kcal:100}});}
      state.history=h; updateDashboard();})()""")
    note = ev("document.getElementById('fibreNote').textContent")
    if 'not enough days' not in note: f.add('BUG', f'4 days should be too few: {note}')
    ev("state.history[4].log[0].fibre=20; updateDashboard()")
    note = ev("document.getElementById('fibreNote').textContent")
    if '14-day average 20g of 25g (80%)' not in note: f.add('BUG', f'average wrong: {note}')
    # hide and reorder
    ev("toggleDashboardSectionHidden('fibre')")
    if ev("getComputedStyle(document.getElementById('dashSection-fibre')).display") != 'none': f.add('BUG', 'hide did not hide')
    ev("toggleDashboardSectionHidden('fibre')")
    before = ev("getDashboardOrder().indexOf('fibre')"); ev("moveDashboardSection('fibre','down')")
    if ev("getDashboardOrder().indexOf('fibre')") != before + 1: f.add('BUG', 'reorder down failed')
    # audit
    ev("saveLibrary([{id:'t1',name:'Spinach',kcal:20,protein:2,carbs:1,fat:0,portion:'80g'},{id:'t2',name:'Chicken',kcal:200,protein:40,carbs:0,fat:5},{id:'t3',name:'Oats',kcal:150,protein:5,carbs:25,fat:3,fibre:4}])")
    ev("mhNutrientAudit()")
    txt = ev("document.getElementById('mhAuditModal').innerText")
    if 'Spinach' not in txt or 'Chicken' not in txt or 'Oats' in txt.split('Foods with no fibre')[1]: f.add('BUG', 'audit list wrong')
    if '1 of 3' not in txt: f.add('BUG', 'coverage count wrong')
    if 'One portion = 80g' not in txt: f.add('BUG', 'audit row does not say which portion the figure is for')
    if 'Portion not set' not in txt: f.add('BUG', 'a food with no saved portion must say so, not assume 100g')
    if 'One portion = 100g' in txt: f.add('BUG', 'portion was assumed to be 100g')
    if ev("document.getElementById('mhAud-t1').getBoundingClientRect().width") < 90: f.add('BUG', 'fibre input too narrow to use')
    ev("document.getElementById('mhAud-t1').value='2.2'; mhAuditSave('t1',false)")
    ev("mhAuditSave('t2',true)")   # Chicken has no portion: "No fibre" must still succeed (v3.10.1108) — portion is irrelevant to zero
    lib = ev("loadLibrary()")
    sp = [x for x in lib if x['id'] == 't1'][0]; ch = [x for x in lib if x['id'] == 't2'][0]
    if sp.get('fibre') != 2.2 or not sp.get('fibreChecked'): f.add('BUG', f'save failed {sp}')
    if ch.get('fibre') != 0 or not ch.get('fibreChecked'): f.add('BUG', f'no-fibre failed {ch}')
    if ch.get('portion'): f.add('BUG', f'no-fibre should not invent a portion: {ch}')
    if 'Every food has a fibre figure' not in ev("document.getElementById('mhAuditModal').innerText"): f.add('BUG', 'audit did not finish')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
