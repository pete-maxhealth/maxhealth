"""Persona 366: fibre must survive every route a meal takes into the log, the same way fat does.
Routes: copy a line (Today and History) then paste it; the paste form typed by hand (today and a past day); the manual entry form;
the Missed day form (manual); the save-to-library dialog; a planned meal eaten (today and from an earlier day).
A figure that was never recorded stays 'not recorded' (shown as a dash when copied, left blank when pasted): never guessed.
Invented data."""
import sys, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def setv(i, v): ev("(a => { const e = document.getElementById(a[0]); e.value = a[1]; e.dispatchEvent(new Event('input')); })", [i, v])
def chk(cond, msg):
    if not cond: f.add('BUG', msg)
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); page.reload(); page.wait_for_timeout(1200)
    ev("window.__clip = ''; Object.defineProperty(navigator, 'clipboard', { value: { writeText: t => { window.__clip = t; return Promise.resolve(); }, readText: () => Promise.resolve(window.__clip) }, configurable: true })")
    ev("window.appConfirm = (m, ok) => { ok && ok(); }")
    # an earlier day exists so past-day routes have somewhere to go
    ev("state.history = [{ date: '30/10/26', log: [{ id: 8000001, description: 'Yesterday oats', kcal: 300, protein: 10, carbs: 40, fat: 8, fibre: 6.5, time: '08:00' }, { id: 8000002, description: 'Yesterday toast', kcal: 120, protein: 4, carbs: 20, fat: 2, time: '09:00' }], totals: { kcal: 420, protein: 14, carbs: 60, fat: 10, fibre: 6.5 } }]; state.todayLog = []; saveState()")
    # 1. copy a Today line with fibre, round-trip through the paste form
    ev("state.todayLog = [{ id: 9100001, description: 'Chia pudding', kcal: 250, protein: 8, carbs: 20, fat: 15, fibre: 11.2, time: '08:00' }, { id: 9100002, description: 'Plain egg', kcal: 80, protein: 6, carbs: 0.5, fat: 5, time: '09:00' }]; saveState()")
    ev("copyLogEntryLine(9100001)"); line = ev("window.__clip"); chk('11.2g fibre' in line, f'Today copy line has no fibre: {line}')
    ev("openPasteMealModal()"); page.wait_for_timeout(500)
    chk(ev("document.getElementById('pasteMealFibre').value") == '11.2', 'paste form did not pick up fibre from the copied line: ' + str(ev("document.getElementById('pasteMealFibre').value")))
    ev("document.getElementById('pasteMealDate').value = todayStr(); confirmPasteMeal()"); page.wait_for_timeout(300)
    chk(abs(ev("calcTotals(state.todayLog).fibre") - 22.4) < 0.01, f"Today fibre after paste should be 22.4, got {ev('calcTotals(state.todayLog).fibre')}")
    # 2. a line that never had fibre: dash when copied, blank when pasted, nothing guessed
    ev("copyLogEntryLine(9100002)"); line2 = ev("window.__clip"); chk('— g fibre'.replace(' ', '') in line2.replace(' ', '') or '—g fibre' in line2, f'no-fibre copy line should show a dash: {line2}')
    ev("openPasteMealModal()"); page.wait_for_timeout(400)
    chk(ev("document.getElementById('pasteMealFibre').value") == '', 'pasted a dash as a fibre figure')
    before = ev("calcTotals(state.todayLog).fibre"); ev("document.getElementById('pasteMealDate').value = todayStr(); confirmPasteMeal()"); page.wait_for_timeout(300)
    chk(ev("calcTotals(state.todayLog).fibre") == before and ev("state.todayLog.slice(-1)[0].fibre") is None, 'fibre was invented for a food that never had any')
    # 3. an older copied line (written before fibre was added) still pastes
    ev("window.__clip = 'Old toast (2 slices) — 150kcal, 5g protein, 2g fat, 25g carbs'; openPasteMealModal()"); page.wait_for_timeout(400)
    chk(ev("document.getElementById('pasteMealDesc').value") == 'Old toast' and ev("document.getElementById('pasteMealFibre').value") == '', 'an older copied line no longer pastes')
    ev("closePasteMealModal()")
    # 4. History copy line, then paste into a past day
    ev("copyHistEntryLine('30/10/26', 0)"); hl = ev("window.__clip"); chk('6.5g fibre' in hl, f'History copy line has no fibre: {hl}')
    ev("openPasteMealModal()"); page.wait_for_timeout(400); ev("document.getElementById('pasteMealDate').value = '30/10/26'; confirmPasteMeal()"); page.wait_for_timeout(300)
    chk(abs(ev("state.history.find(h => h.date === '30/10/26').totals.fibre") - 13.0) < 0.01, "past-day fibre total should be 13.0")
    # 5. paste form typed by hand
    ev("openPasteMealModal()"); setv('pasteMealDesc', 'Typed lentils'); setv('pasteMealKcal', '200'); setv('pasteMealFibre', '7.5'); ev("document.getElementById('pasteMealDate').value = todayStr()"); ev("confirmPasteMeal()"); page.wait_for_timeout(300)
    chk(any(e.get('fibre') == 7.5 for e in ev("state.todayLog")), 'hand-typed fibre in the paste form was not stored')
    # 6. manual entry form
    ev("switchTabById('chat')"); page.wait_for_timeout(300); ev("showManualEntryForm('Manual beans')"); page.wait_for_timeout(300); setv('meKcal', '120'); setv('meFibre', '5.2'); ev("confirmManualEntry()"); page.wait_for_timeout(300)
    chk(any(e.get('source') == 'manual' and e.get('fibre') == 5.2 for e in ev("state.todayLog")), 'manual entry fibre not stored')
    # 7. Missed day form (manual)
    ev("openMissedDayModal('29/10/26')"); page.wait_for_timeout(300); ev("setMissedMode && setMissedMode('manual')") if ev("typeof setMissedMode") == 'function' else None
    if ev("_missedMode") != 'manual': ev("_missedMode = 'manual'")
    setv('missedKcal', '1800'); setv('missedProtein', '120'); setv('missedCarbs', '90'); setv('missedFibre', '18.5'); ev("document.getElementById('missedDayDate').value = '29/10/26'; saveMissedDay()"); page.wait_for_timeout(400)
    d = ev("state.history.find(h => h.date === '29/10/26')"); chk(d and d['totals'].get('fibre') == 18.5 and d['log'][0].get('fibre') == 18.5, f'Missed day fibre not stored: {d and d["totals"]}')
    ev("openMissedDayModal('28/10/26')"); page.wait_for_timeout(300); ev("_missedMode = 'manual'"); setv('missedKcal', '1500'); setv('missedProtein', '100'); setv('missedCarbs', '80'); ev("document.getElementById('missedDayDate').value = '28/10/26'; saveMissedDay()"); page.wait_for_timeout(400)
    d2 = ev("state.history.find(h => h.date === '28/10/26')"); chk(d2 and d2['totals'].get('fibre') == 0, 'Missed day with no fibre typed should count 0')
    # 8. save-to-library dialog keeps fibre
    ev("promptSaveToLibrary({ name: 'Fibre bar', kcal: 180, protein: 5, fat: 6, carbs: 22, fibre: 8.4, amount: '1 bar' })"); page.wait_for_timeout(300)
    chk(ev("document.getElementById('saveModalFibreEdit').value") == '8.4', 'save dialog did not show the meal fibre')
    ev("confirmSaveToLibrary()"); page.wait_for_timeout(500)
    lib = ev("(typeof loadLibrary === 'function' ? loadLibrary() : []).find(x => x.name.toLowerCase() === 'fibre bar')"); chk(lib and lib.get('fibre') == 8.4, f'library entry lost fibre: {lib}')
    # 9. planned meals: eaten today, and eaten from an earlier day
    plan = "[{ id: 'pa', date: localISODate(), time: '07:00', text: 'Bran flakes', foods: [{ name: 'Bran flakes', amount: '40g', kcal: 130, protein: 4, carbs: 24, fat: 1, fibre: 7.9 }], createdAt: 1 }, { id: 'pb', date: '2026-10-30', time: '12:00', text: 'Yesterday lentils', foods: [{ name: 'Lentils', amount: '100g', kcal: 116, protein: 9, carbs: 20, fat: 0.4, fibre: 7.9 }], createdAt: 2 }]"
    ev(f"mhPlanSave({plan})"); b0 = ev("calcTotals(state.todayLog).fibre"); ev("mhPlanEat('pa')"); page.wait_for_timeout(500)
    chk(abs(ev("calcTotals(state.todayLog).fibre") - b0 - 7.9) < 0.01, f"planned meal eaten today lost its fibre ({b0} -> {ev('calcTotals(state.todayLog).fibre')})")
    ev("mhPlanEat('pb')"); page.wait_for_timeout(500)
    chk(abs(ev("state.history.find(h => h.date === '30/10/26').totals.fibre") - 20.9) < 0.01, "overdue planned meal logged to its own day lost fibre (expected 20.9)")
    # 10. polyols travel with the copied line (only when the meal has them) and the planned-fibre tile note
    ev("state.todayLog.push({ id: 9100050, description: 'Keto bar', kcal: 200, protein: 12, carbs: 18, fat: 10, fibre: 3.1, polyols: 9.4, time: '10:00' }); saveState()")
    ev("copyLogEntryLine(9100050)"); lp = ev("window.__clip"); chk(lp.endswith('3.1g fibre, 9.4g polyols'), f'copy line lost polyols: {lp}')
    ev("copyLogEntryLine(9100002)"); chk('polyols' not in ev("window.__clip"), 'a food with no polyols got a polyols figure in its copy line')
    ev("copyLogEntryLine(9100050)"); ev("openPasteMealModal()"); page.wait_for_timeout(400)
    chk(ev("document.getElementById('pasteMealPolyols').value") == '9.4', 'paste form did not pick up polyols')
    pb = ev("calcTotals(state.todayLog).polyols"); ev("document.getElementById('pasteMealDate').value = todayStr(); confirmPasteMeal()"); page.wait_for_timeout(300)
    chk(abs(ev("calcTotals(state.todayLog).polyols") - pb - 9.4) < 0.01, 'pasted polyols not counted in the day total')
    ev("mhPlanSave([{ id: 'pz', date: localISODate(), time: '23:00', text: 'Oats', foods: [{ name: 'Oats', amount: '50g', kcal: 180, protein: 6, carbs: 30, fat: 3, fibre: 5.0 }], createdAt: 2 }]); mhPlanTileNotes()")
    tn = ev("(document.getElementById('fibrePlanned') || {}).textContent || ''"); chk('+5g planned' in tn, f'fibre tile has no planned note: {tn!r}')
    ev("mhPlanSave([]); mhPlanTileNotes()"); chk(ev("document.getElementById('fibrePlanned').style.display") == 'none', 'fibre planned note stays after plan cleared')
    print('routes checked: copy/paste (today, history, old line, no-fibre), typed paste, manual, missed day x2, save dialog, plan today, plan overdue')
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs:', len(bugs)); sys.exit(1 if bugs else 0)
