"""Persona 353 (v3.10.1244): tapping a meal name in History opens that meal's editor, for every day shown and every meal, even when the list's
order differs from the stored order (newest first on screen) and when a day has an empty 'Standard' ghost entry before the real meals.
Delete by tap removes the entry shown, not a neighbour. Demo data (invented)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    ev("document.getElementById('maintab-log').click()"); p.wait_for_timeout(450); ev("document.getElementById('logtab-hist').click()"); p.wait_for_timeout(700)
    # put a ghost entry in front of the real meals on the first shown day
    ev("""(()=>{const dt=document.querySelector('.hist-day-date').textContent.trim(); const d=state.history.find(x=>x.date===dt);
        d.log.unshift({id:'ghost1',description:'Standard',name:'Standard',kcal:0,protein:0,carbs:0,fat:0}); saveState(); renderHistory();})()""")
    p.wait_for_timeout(400)
    differs = ev("(()=>{const shown=[...document.querySelectorAll('.hist-day-date')].map(e=>e.textContent.trim()); return shown.slice(0,5).some((d,i)=>state.history.findIndex(x=>x.date===d)!==i)})()")
    if not differs: f.add('NOTE', 'demo data happens to be in display order; the mismatch case is not exercised')
    checked = 0
    for d in range(3):
        ev(f"document.querySelectorAll('.hist-day')[{d}].querySelector('.hist-day-body').classList.add('open')")
        n = ev(f"document.querySelectorAll('.hist-day')[{d}].querySelectorAll('.hist-entry').length")
        for j in range(n):
            ev("document.querySelectorAll('.hist-edit-form').forEach(x=>x.remove())")
            nm = ev(f"document.querySelectorAll('.hist-day')[{d}].querySelectorAll('.hist-entry')[{j}].querySelector('span[onclick*=editHistEntryByDate]').innerText")
            p.locator('.hist-day').nth(d).locator('.hist-entry').nth(j).locator('span[onclick*=editHistEntryByDate]').click(); p.wait_for_timeout(250)
            forms = ev(f"document.querySelectorAll('.hist-day')[{d}].querySelectorAll('.hist-entry')[{j}].querySelectorAll('.hist-edit-form').length")
            if forms != 1: f.add('BUG', f'day {d} meal {j} ("{nm[:30]}"): tapping the name should open its editor, forms inside it: {forms}')
            checked += 1
    if checked < 6: f.add('BUG', f'only {checked} meals checked')
    # the editor that opens is for the meal tapped (description box matches the entry), not a neighbour
    ev("document.querySelectorAll('.hist-edit-form').forEach(x=>x.remove())")
    p.locator('.hist-day').nth(0).locator('.hist-entry').nth(1).locator('span[onclick*=editHistEntryByDate]').click(); p.wait_for_timeout(300)
    shown = ev("document.querySelectorAll('.hist-day')[0].querySelectorAll('.hist-entry')[1].querySelector('.hist-edit-form input')?.value || document.querySelectorAll('.hist-day')[0].querySelectorAll('.hist-entry')[1].querySelector('.hist-edit-form')?.innerText || ''")
    want = ev("(()=>{const dt=document.querySelector('.hist-day-date').textContent.trim(); const d=state.history.find(x=>x.date===dt); const clean=d.log.filter(e=>(e.description||'').trim()&&!['standard','occasion','holiday','missed day entry','missed day'].includes(e.description.trim().toLowerCase())); return clean[1].description})()")
    if want[:12] not in shown: f.add('BUG', f'editor opened for the wrong meal: wanted "{want[:30]}", saw "{shown[:60]}"')
    # delete by tap removes the shown entry
    ev("document.querySelectorAll('.hist-edit-form').forEach(x=>x.remove()); window.appConfirm=(m,yes)=>yes(); 0")
    before = ev("(()=>{const dt=document.querySelector('.hist-day-date').textContent.trim(); const d=state.history.find(x=>x.date===dt); return d.log.map(e=>e.description)})()")
    date0 = ev("document.querySelector('.hist-day-date').textContent.trim()")
    ev(f"deleteHistEntryByDate('{date0}',1)"); p.wait_for_timeout(300)
    after = ev("(()=>{const dt=document.querySelector('.hist-day-date').textContent.trim(); const d=state.history.find(x=>x.date===dt); return d.log.map(e=>e.description)})()")
    gone = [x for x in before if x not in after]
    if gone != [want]: f.add('BUG', f'delete-by-tap on the second shown meal removed {gone}, wanted [{want}]')
    if 'Standard' not in after: f.add('BUG', 'the ghost entry should be untouched')
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
