"""Persona 147: Barry's sample food log sits near his own targets (a good month); other personas keep their old behaviour."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    js = """(id)=>{const p=DEMO_PERSONAS.find(x=>x.id===id); const h=generateDemoHistoryForPersona(p); const a=k=>h.reduce((t,d)=>t+d.totals[k],0)/h.length; const ok=h.filter(d=>d.totals.carbs<=p.targets.carbs*1.0).length/h.length; return {k:a('kcal')/p.targets.kcal, p:a('protein')/p.targets.protein, ok, bad:h.filter(d=>[d.totals.kcal,d.totals.protein,d.totals.carbs,d.totals.fat].some(v=>!(v>=0)||isNaN(v))).length}}"""
    for _ in range(5):
        r = page.evaluate(js, 'barry')
        if not (0.9 <= r['k'] <= 1.08): f.add('BUG', f'Barry calories off target: {r}')
        if r['p'] < 0.95: f.add('BUG', f'Barry protein under target: {r}')
        if r['ok'] < 0.65: f.add('BUG', f'Barry carb ceiling adherence too low: {r}')
        if r['bad']: f.add('BUG', f'invalid totals {r}')
    r = page.evaluate(js, 'bill')
    if r['k'] > 0.9: f.add('BUG', f'Bill changed unexpectedly: {r}')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
