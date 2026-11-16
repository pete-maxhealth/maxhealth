"""Persona 488 (v3.10.1406): foods that differ only by shop (Asda / Tesco double cream) are separate bars in the Top foods card and in the Statistics rankings;
case, spacing and plurals still merge; the library match still ignores the shop. Invented data only."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("""(()=>{
      const d=(n)=>{const x=new Date();x.setDate(x.getDate()-n);return String(x.getDate()).padStart(2,'0')+'/'+String(x.getMonth()+1).padStart(2,'0')+'/'+String(x.getFullYear()).slice(2);};
      const it=(n,fat)=>({name:n,kcal:fat*9,protein:1,carbs:1,fat:fat});
      const e=(id,items)=>({id,time:'08:00',description:items[0].name,kcal:0,protein:0,carbs:0,fat:0,items});
      state.history=[
        {date:d(1),totals:{kcal:2000,protein:50,carbs:20,fat:100},steps:5000,log:[e(1,[it('Asda Double Cream',100)]),e(2,[it('Tesco Double Cream',60)])],exercises:[]},
        {date:d(2),totals:{kcal:2000,protein:50,carbs:20,fat:100},steps:5000,log:[e(3,[it('asda double  cream',50)]),e(4,[it('Eggs',10)]),e(5,[it('Egg',10)])],exercises:[]},
      ];
    })()""")
    top = ev("getTopFoodsData(30).map(x=>[x.name,x.fat,x.count])")
    names = [t[0].lower() for t in top]
    any('asda' in n for n in names) and any('tesco' in n for n in names) or f.add('FAIL', f'Top foods merged shops: {top}')
    asda = [t for t in top if 'asda' in t[0].lower()]; asda and asda[0][1] == 150 and asda[0][2] == 2 or f.add('FAIL', f'Asda total/count wrong (want 150 fat, 2): {asda}')
    tes = [t for t in top if 'tesco' in t[0].lower()]; tes and tes[0][1] == 60 or f.add('FAIL', f'Tesco total wrong: {tes}')
    egg = [t for t in top if t[0].lower().startswith('egg')]; len(egg) == 1 and egg[0][2] == 2 or f.add('FAIL', f'Egg/Eggs should still merge: {egg}')
    r = ev("mhStatRun({subject:'foods',measure:'fat',agg:'sum',order:'high',top:10,period:30,output:'bars'}).rows.map(x=>[x.label,Math.round(x.value)])")
    ls = [x[0].lower() for x in r]
    any('asda' in n for n in ls) and any('tesco' in n for n in ls) or f.add('FAIL', f'Statistics ranking merged shops: {r}')
    # the library match still ignores the shop name
    ev("""(()=>{const l=loadLibrary();l.push({name:'Tesco Double Cream',kcal:450,protein:2,fat:48,carbs:3,portion:'100g'});saveLibrary&&saveLibrary(l)})()""")
    m = ev("(()=>{const r=applyLibraryMatches([{name:'Asda Double Cream',amount:'100g'}]);return r[0]._source})()")
    m == 'library' or f.add('FAIL', f'library match no longer ignores the shop: {m}')
    # renders
    ev("switchTabById('trends')"); page.wait_for_timeout(800)
    errs and f.add('FAIL', f'page errors {errs}'); br.close()
print('findings', len(f))
