"""p369: nutrient x route grid. Every nutrient (kcal, protein, carbs, fat, fibre, polyols) goes in through every route a meal takes into the log, and
the totals must match what went in. A route that cannot take a nutrient at all is a GAP; the set of gaps is pinned in EXPECTED_GAPS (known, in BACKLOG.md),
so a NEW gap fails and a gap that has been closed also fails until the list is updated. Also checks that every day's stored totals equal the sum of its lines.
Invented data."""
import sys; sys.path.insert(0, 'tests/personas')
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def chk(c, m):
    if not c: f.add('BUG', m)
N = ['kcal', 'protein', 'carbs', 'fat', 'fibre', 'polyols']
V = {'kcal': 335, 'protein': 20.0, 'carbs': 30.0, 'fat': 15.0, 'fibre': 8.2, 'polyols': 6.3}
EXPECTED_GAPS = set()   # all closed (v3.10.1288: polyols boxes in Manual entry and Missed day)
gaps = set()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); page.reload(); page.wait_for_timeout(1200)
    ev("window.__clip=''; Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__clip=t;return Promise.resolve()},readText:()=>Promise.resolve(window.__clip)},configurable:true})")
    ev("window.appConfirm = (m, ok) => { ok && ok(); }")
    missing = set()   # input boxes that do not exist on a form: that route cannot take the nutrient
    NID = {'Fibre': 'fibre', 'Polyols': 'polyols', 'meFibre': 'fibre', 'missedFibre': 'fibre'}
    def setv(i, v):
        ok = ev("(a => { const e = document.getElementById(a[0]); if (!e) return false; e.value = a[1]; e.dispatchEvent(new Event('input')); return true; })", [i, v])
        if not ok and i in ('pasteMealFibre', 'pasteMealPolyols', 'meFibre', 'missedFibre'): missing.add(NID.get(i) or NID[i[len('pasteMeal'):]])
    ISO = "(() => { const d = new Date(Date.now() - 864e5); const p = n => String(n).padStart(2,'0'); return p(d.getDate()) + '/' + p(d.getMonth()+1) + '/' + String(d.getFullYear()).slice(2); })()"
    Y = ev(ISO)
    ENTRY = "{ id: 8800001, description: 'Grid meal', kcal: 335, protein: 20, carbs: 30, fat: 15, fibre: 8.2, polyols: 6.3, time: '09:00' }"
    def reset():
        ev(f"state.todayLog = []; state.history = [{{ date: '{Y}', log: [{ENTRY}], totals: {{ kcal: 335, protein: 20, carbs: 30, fat: 15, fibre: 8.2, polyols: 6.3 }} }}]; saveState()")
        ev("closePasteMealModal && closePasteMealModal()")
    today = lambda: ev("(() => { const t = calcTotals(state.todayLog); return { kcal: t.kcal, protein: t.protein, carbs: t.carbs, fat: t.fat, fibre: t.fibre, polyols: t.polyols }; })()")
    yday = lambda: ev(f"(() => {{ const d = state.history.find(h => h.date === '{Y}'); const t = d.totals; return {{ kcal: t.kcal, protein: t.protein, carbs: t.carbs, fat: t.fat, fibre: t.fibre || 0, polyols: t.polyols || 0 }}; }})()")
    def check(route, got, base, accepts, extra=None):
        accepts = set(accepts) - missing; missing.clear()
        for n in N:
            if n not in accepts:
                gaps.add((route, n)); continue
            want = (extra or V)[n] if not base else base[n] + V[n]
            if abs((got.get(n) or 0) - want) > 0.06: f.add('BUG', f'{route}: {n} should be {want}, got {got.get(n)}')
    ALL = set(N)
    # 1 the common sink (AI, library, recipe preview all end here)
    reset(); ev("logFoods([{ name: 'Grid meal', amount: '100g', kcal: 335, protein: 20, carbs: 30, fat: 15, fibre: 8.2, polyols: 6.3 }], 'Grid meal')"); page.wait_for_timeout(300); check('log foods (AI/library/preview)', today(), None, ALL)
    # 2 paste form, typed
    reset(); ev("openPasteMealModal()"); page.wait_for_timeout(300)
    for i, k in [('pasteMealDesc', 'Grid meal'), ('pasteMealKcal', '335'), ('pasteMealProtein', '20'), ('pasteMealCarbs', '30'), ('pasteMealFat', '15'), ('pasteMealFibre', '8.2'), ('pasteMealPolyols', '6.3')]: setv(i, k)
    ev("document.getElementById('pasteMealDate').value = todayStr(); confirmPasteMeal()"); page.wait_for_timeout(300); check('paste form (typed)', today(), None, ALL)
    # 3 copy a Today line, paste it
    reset(); ev(f"state.todayLog = [{ENTRY}]; saveState()"); ev("copyLogEntryLine(8800001)"); ev("state.todayLog = []"); ev("openPasteMealModal()"); page.wait_for_timeout(300); ev("pasteMealFromClipboard(true)"); page.wait_for_timeout(300)
    ev("document.getElementById('pasteMealDate').value = todayStr(); confirmPasteMeal()"); page.wait_for_timeout(300); check('copy Today line, paste', today(), None, ALL)
    # 4 copy a History line, paste it to today
    reset(); ev(f"copyHistEntryLine('{Y}', 0)"); ev("openPasteMealModal()"); page.wait_for_timeout(300); ev("pasteMealFromClipboard(true)"); page.wait_for_timeout(300)
    ev("document.getElementById('pasteMealDate').value = todayStr(); confirmPasteMeal()"); page.wait_for_timeout(300); check('copy History line, paste', today(), None, ALL)
    # 4b ... and paste it into a past day
    reset(); ev(f"copyHistEntryLine('{Y}', 0)"); ev("openPasteMealModal()"); page.wait_for_timeout(300); ev("pasteMealFromClipboard(true)"); page.wait_for_timeout(300)
    ev(f"document.getElementById('pasteMealDate').value = '{Y}'; confirmPasteMeal()"); page.wait_for_timeout(300); check('paste into a past day', yday(), {n: V[n] for n in N}, ALL)
    # 5 History multi-select, add to Today
    reset(); ev("switchTabById('hist')"); page.wait_for_timeout(400); ev("renderHistory()"); ev("document.getElementById('histBody0').classList.add('open')"); ev("toggleHistSelectMode(); histSelectDay(0); histAddSelectedToToday()"); page.wait_for_timeout(400); check('History multi-select to Today', today(), None, ALL)
    # 6 manual entry (polyols box since v3.10.1288)
    reset(); ev("switchTabById('chat')"); page.wait_for_timeout(300); ev("showManualEntryForm('Grid meal')"); page.wait_for_timeout(300)
    for i, k in [('meKcal', '335'), ('meProt', '20'), ('meCarbs', '30'), ('meFat', '15'), ('meFibre', '8.2'), ('mePolyols', '6.3')]: setv(i, k)
    ev("confirmManualEntry()"); page.wait_for_timeout(300); check('manual entry', today(), None, {'kcal', 'protein', 'carbs', 'fat', 'fibre', 'polyols'})
    # 7 Missed day, typed totals, into a day not yet in history
    reset(); ev("state.history = []; saveState()"); ev("openMissedDayModal('28/10/26')"); page.wait_for_timeout(300); ev("_missedMode = 'manual'")
    for i, k in [('missedKcal', '335'), ('missedProtein', '20'), ('missedCarbs', '30'), ('missedFat', '15'), ('missedFibre', '8.2'), ('missedPolyols', '6.3')]: setv(i, k)
    ev("document.getElementById('missedDayDate').value = '28/10/26'; saveMissedDay()"); page.wait_for_timeout(400)
    t = ev("(state.history.find(h => h.date === '28/10/26') || { totals: {} }).totals"); t = {n: (t.get(n) or 0) for n in N}; check('missed day (typed)', t, None, {'kcal', 'protein', 'carbs', 'fat', 'fibre', 'polyols'})
    # 8 planned meal eaten today
    reset(); ev("mhPlanSave([{ id: 'pg', date: localISODate(), time: '07:00', text: 'Grid meal', foods: [{ name: 'Grid meal', amount: '100g', kcal: 335, protein: 20, carbs: 30, fat: 15, fibre: 8.2, polyols: 6.3 }], createdAt: 1 }]); mhPlanEat('pg')"); page.wait_for_timeout(400); check('planned meal eaten', today(), None, ALL)
    # 9 recipe logged
    reset(); ev("saveRecipes([{ id: 'rg', name: 'Grid recipe', servings: 1, ingredients: [{ name: 'Grid meal', amount: '100', kcal: 335, protein: 20, carbs: 30, fat: 15, fibre: 8.2, polyols: 6.3 }] }])"); ev("logRecipe('rg', 1)"); page.wait_for_timeout(400); check('recipe logged', today(), None, ALL)
    # whole-app invariant: every day's stored totals are the sum of its lines, for every nutrient
    ev("state.history.push({ date: '27/10/26', log: [{ id: 8800002, description: 'a', kcal: 100, protein: 5, carbs: 10, fat: 2, fibre: 1.5, time: '08:00' }, { id: 8800003, description: 'b', kcal: 50, protein: 1, carbs: 5, fat: 1, polyols: 2, time: '09:00' }], totals: { kcal: 150, protein: 6, carbs: 15, fat: 3, fibre: 1.5, polyols: 2 } })")
    for d in ev("state.history"):
        lg = d.get('log') or []
        if not lg: continue
        for n in N:
            s = sum((e.get(n) or 0) for e in lg); tt = (d.get('totals') or {}).get(n) or 0
            if abs(s - tt) > 0.06: f.add('BUG', f"history {d['date']}: stored {n} total {tt} differs from the sum of its lines {round(s, 2)}")
new = gaps - EXPECTED_GAPS; closed = EXPECTED_GAPS - gaps
for g in sorted(new): f.add('BUG', f'NEW GAP: {g[0]} cannot take {g[1]}')
for g in sorted(closed): f.add('BUG', f'gap closed, update EXPECTED_GAPS: {g[0]} now takes {g[1]}')
print('routes x nutrients checked; known gaps:', sorted(gaps))
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs:', len(bugs)); [print(x) for x in bugs]; sys.exit(1 if bugs else 0)
