"""Persona 117: score a past day from the How-are-you card: modal opens with 14 days, saves into that day's history (new food-less entry kept in date order, or merged into an existing one), tap again clears, no scores and no entry = nothing invented, no page errors."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("saveSymptomDefs([{id:'a',name:'Headache',active:true},{id:'b',name:'Fatigue',active:true}]); renderSymptomTracker()")
    if 'Score a past day' not in ev("document.getElementById('symptomTrackerContent').innerText"): f.add('BUG', 'no past-day link')
    ev("""(()=>{ const d=n=>{const x=new Date(Date.now()-n*864e5);const p=v=>String(v).padStart(2,'0');return p(x.getDate())+'/'+p(x.getMonth()+1)+'/'+String(x.getFullYear()).slice(2);};
      state.history=[{date:d(1),log:[],totals:{kcal:900},notes:'standard'},{date:d(6),log:[],totals:{kcal:900},notes:'standard'}]; window.__d=d; })()""")
    # existing entry (3 days ago does not exist -> new entry between)
    ev("mhSymBackfillOpen(__d(3))")
    if ev("document.querySelectorAll('#symBfDate option').length") != 14: f.add('BUG', 'not 14 days offered')
    page.click('#symBfModal [data-s="a"][data-n="2"]'); page.click('#symBfModal [data-s="b"][data-n="4"]'); page.click('#symBfSave'); page.wait_for_timeout(300)
    h = ev("state.history.map(h=>[h.date,h.symptoms||null])"); d3 = ev("__d(3)"); d1 = ev("__d(1)"); d6 = ev("__d(6)")
    if [x[0] for x in h] != [d1, d3, d6]: f.add('BUG', f'order {h}')
    row = [x for x in h if x[0] == d3]
    if not row or row[0][1] != {'a': 2, 'b': 4}: f.add('BUG', f'scores {row}')
    if ev("state.history.find(h=>h.date===__d(3)).totals.kcal") != 0: f.add('BUG', 'new entry should be food-less')
    # merge into existing + clear one
    ev("mhSymBackfillOpen(__d(1))"); page.click('#symBfModal [data-s="a"][data-n="5"]'); page.click('#symBfSave'); page.wait_for_timeout(300)
    if ev("state.history.find(h=>h.date===__d(1)).symptoms.a") != 5: f.add('BUG', 'merge failed')
    if ev("state.history.find(h=>h.date===__d(1)).totals.kcal") != 900: f.add('BUG', 'food data touched')
    ev("mhSymBackfillOpen(__d(3))"); page.click('#symBfModal [data-s="a"][data-n="2"]'); page.click('#symBfModal [data-s="b"][data-n="4"]'); page.click('#symBfSave'); page.wait_for_timeout(300)
    if ev("state.history.find(h=>h.date===__d(3)).symptoms"): f.add('BUG', 'tap again did not clear')
    # nothing scored on a day without entry
    n = ev("state.history.length"); ev("mhSymBackfillOpen(__d(9))"); page.click('#symBfSave'); page.wait_for_timeout(200)
    if ev("state.history.length") != n: f.add('BUG', 'empty save invented a day')
    ev("mhSymBackfillOpen(__d(2))"); page.click('#symBfX')
    if ev("!!document.getElementById('symBfModal')"): f.add('BUG', 'cancel did not close')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
