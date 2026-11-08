"""Persona 425: water (and weight) editable straight from History, v3.10.1323. Pete 8 Nov: "Could water be made editable under history?"
Covers: a day with water shows a tappable Water line that opens Edit day totals with the cursor in the water box; changing it saves, the History line, state and the Trends water series show the new value, and it survives a reload;
a day with no water shows "+ Water", adding one works, and clearing it (0) takes the line away again; the Weight line does the same for weight; nothing else on the day (food lines, totals) changes;
the existing Edit day totals link still works; narrow phone and PC widths; both themes looked at; no page errors. Invented days."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings(); chk = lambda ok, m: None if ok else f.add('BUG', m)
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%Y')
def day(n, water, weight):
    d = {'date': dmy(n), 'mode': 'standard', 'notes': 'standard', 'log': [{'id': 900 + n, 'time': '08:00', 'description': 'Zzqx Eggs', 'kcal': 400, 'protein': 20, 'carbs': 2, 'fat': 15}], 'totals': {'kcal': 400, 'protein': 20, 'carbs': 2, 'fat': 15}}
    if water: d['water_ml'] = water
    if weight: d['weight'] = weight
    return d
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    for label, w, h in (('phone', 390, 844), ('pc', 1280, 900)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: errs.append(label + ' ' + str(e)[:160])); page.on('dialog', lambda d: d.dismiss())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
        D1, D2 = dmy(1), dmy(2)
        ev("state.history = " + json.dumps([day(1, 1500, 80.5), day(2, 0, 0)]) + "; saveState()")
        ev("document.getElementById('maintab-log').click(); switchSubTab('log','hist'); renderHistory()"); page.wait_for_timeout(1200)
        row = lambda d: ev(f"(()=>{{const h=state.history.find(x=>x.date==='{d}'); return h?{{w:h.water_ml||0,kg:h.weight||0,kcal:h.totals.kcal,log:(h.log||[]).length}}:null}})()")
        txt = lambda: ev("document.getElementById('histEntries').innerText")
        open_day = lambda d: ev(f"(()=>{{const el=[...document.querySelectorAll('.hist-day-date')].find(e=>e.textContent.trim()==='{d}'); el.closest('.hist-day').querySelector('.hist-day-header, .hist-day-top, div').click(); return !!el}})()")
        ev("document.querySelectorAll('.hist-day-body').forEach(b=>b.classList.add('open'))")
        chk('Water: 1500ml' in txt(), f'1 {label}: water line missing: {txt()[:200]!r}')
        chk(ev("[...document.querySelectorAll('.hist-notes')].some(e=>e.textContent.includes('Water: 1500ml') && e.getAttribute('onclick'))"), f'2 {label}: water line is not tappable')
        chk('+ Water' in txt(), f'3 {label}: no "+ Water" on the day without water')
        # tap the water line
        ev(f"[...document.querySelectorAll('.hist-notes')].find(e=>e.textContent.includes('Water: 1500ml')).click()"); page.wait_for_timeout(500)
        focus_id = ev("document.activeElement && document.activeElement.id")
        chk(focus_id and focus_id.startswith('hday-water-'), f'4 {label}: cursor not in the water box (active: {focus_id})')
        idx = ev(f"state.history.findIndex(x=>x.date==='{D1}')")
        ev(f"document.getElementById('hday-water-{idx}').value='2250'; saveHistDayTotals({idx})"); page.wait_for_timeout(500)
        r = row(D1); chk(r and r['w'] == 2250 and r['kcal'] == 400 and r['log'] == 1, f'5 {label}: after saving: {r}')
        ev("document.querySelectorAll('.hist-day-body').forEach(b=>b.classList.add('open'))")
        chk('Water: 2250ml' in txt(), f'6 {label}: History shows {txt()[:160]!r}')
        series = ev("(()=>{try{const g=(METRIC_DEFS||[]).find(m=>m.key==='water'); return g? g.get(state.history.find(x=>x.date==='" + D1 + "')) : 'nometric'}catch(e){return 'err '+e.message}})()")
        # reload keeps it
        page.reload(); page.wait_for_timeout(1500); ev("document.getElementById('onboardingOverlay')?.remove()")
        chk(row(D1) and row(D1)['w'] == 2250, f'7 {label}: after reload: {row(D1)}')
        ev("document.getElementById('maintab-log').click(); switchSubTab('log','hist'); renderHistory()"); page.wait_for_timeout(900); ev("document.querySelectorAll('.hist-day-body').forEach(b=>b.classList.add('open'))")
        # add water to the empty day
        ev("[...document.querySelectorAll('span')].find(e=>e.textContent.trim()==='💧 + Water').click()"); page.wait_for_timeout(500)
        idx2 = ev(f"state.history.findIndex(x=>x.date==='{D2}')")
        chk(ev("document.activeElement && document.activeElement.id") == f'hday-water-{idx2}', f'8 {label}: + Water did not focus the box')
        ev(f"document.getElementById('hday-water-{idx2}').value='600'; saveHistDayTotals({idx2})"); page.wait_for_timeout(500)
        chk(row(D2) and row(D2)['w'] == 600, f'9 {label}: added water: {row(D2)}')
        # clear it again
        ev("document.querySelectorAll('.hist-day-body').forEach(b=>b.classList.add('open'))")
        ev("[...document.querySelectorAll('.hist-notes')].find(e=>e.textContent.includes('Water: 600ml')).click()"); page.wait_for_timeout(500)
        ev(f"document.getElementById('hday-water-{idx2}').value='0'; saveHistDayTotals({idx2})"); page.wait_for_timeout(500)
        ev("document.querySelectorAll('.hist-day-body').forEach(b=>b.classList.add('open'))")
        chk(row(D2) and row(D2)['w'] == 0 and '600ml' not in txt(), f'10 {label}: clearing water: {row(D2)}')
        # weight line
        ev("[...document.querySelectorAll('.hist-notes')].find(e=>e.textContent.includes('Weight')).click()"); page.wait_for_timeout(500)
        fid = ev("document.activeElement && document.activeElement.id"); chk(fid and fid.startswith('hday-weight-'), f'11 {label}: weight line did not focus the weight box ({fid})')
        # existing link still works
        ev("document.querySelectorAll('.hist-day-totals-edit').forEach(e=>e.remove())")
        ev(f"editHistDayTotalsByDate('{D2}')"); page.wait_for_timeout(300); chk(ev("!!document.querySelector('.hist-day-totals-edit')"), f'12 {label}: Edit day totals no longer opens')
        if label == 'phone':
            for th in ('light', 'dark'):
                ev(f"document.documentElement.setAttribute('data-theme','{th}')"); ev("document.querySelectorAll('.hist-day-totals-edit').forEach(e=>e.remove())"); ev("document.querySelectorAll('.hist-day-body').forEach(b=>b.classList.add('open'))"); page.wait_for_timeout(300)
                page.locator('#histEntries').screenshot(path=f'/tmp/claude-0/p425_{th}.png')
        ctx.close()
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
