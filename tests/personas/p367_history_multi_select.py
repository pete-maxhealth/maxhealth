# p367: History multi-select. Tick several lines of a past day, add them to Today in one go (leftovers next day).
import sys; sys.path.insert(0, 'tests/personas')
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def chk(c, m):
    if not c: f.add('BUG', m)
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); page.reload(); page.wait_for_timeout(1200)
    y = "(() => { const d = new Date(Date.now() - 864e5); const p = n => String(n).padStart(2,'0'); return p(d.getDate()) + '/' + p(d.getMonth()+1) + '/' + String(d.getFullYear()).slice(2); })()"
    ev(f"""(() => {{ const date = {y}; const log = [
      {{ id: 7000001, description: 'Chicken', amount: '150g', kcal: 204, protein: 39, carbs: 0, fat: 5.3, time: '17:44' }},
      {{ id: 7000002, description: 'Seeded bread', amount: '120g', kcal: 276, protein: 30.8, carbs: 1.2, fat: 12.8, fibre: 6.4, polyols: 2.1, time: '10:12', missedDay: true }},
      {{ id: 7000003, description: 'Double cream', amount: '38g', kcal: 177, protein: 0.6, carbs: 0.6, fat: 19.4, time: '17:45' }}];
      state.history = [{{ date, log, totals: {{ kcal: 657, protein: 70.4, carbs: 1.8, fat: 37.5, fibre: 6.4 }} }}]; state.todayLog = []; saveState(); }})()""")
    ev("switchTabById('hist')"); page.wait_for_timeout(500)
    ev("renderHistory()"); page.wait_for_timeout(300)
    chk(ev("document.getElementById('histSelectRow').textContent.includes('Select')"), 'no Select link above History')
    ev("document.getElementById('histBody0').classList.add('open')")
    ev("toggleHistSelectMode()"); page.wait_for_timeout(200)
    chk(ev("document.getElementById('histBody0').classList.contains('open')"), 'day folded when select mode started')
    chk(ev("[...document.querySelectorAll('.hist-act')].every(e => getComputedStyle(e).display === 'none')"), 'row icons still visible in select mode')
    chk(ev("getComputedStyle(document.querySelector('.hist-sel-cb')).display") != 'none', 'tick boxes not shown in select mode')
    chk(ev("document.querySelector('#histSelectRow button').disabled"), 'Add button should be off with nothing ticked')
    ev("document.querySelectorAll('.hist-entry > div > span:nth-of-type(1)')[0].click()")   # tapping the name ticks, never opens the editor
    chk(ev("document.querySelectorAll('.hist-sel-cb:checked').length") == 1, 'tapping a name did not tick it')
    chk(not ev("!!document.querySelector('.hist-edit-form, #histEditModal, .edit-entry-panel')"), 'tapping a name in select mode opened the editor')
    ev("histSelectDay(0)"); chk(ev("document.querySelectorAll('.hist-sel-cb:checked').length") == 3, 'Select whole day did not tick all three')
    ev("histSelectDay(0)"); chk(ev("document.querySelectorAll('.hist-sel-cb:checked').length") == 0, 'Select whole day did not untick on second tap')
    ev("document.querySelectorAll('.hist-sel-cb')[1].click(); document.querySelectorAll('.hist-sel-cb')[0].click()"); page.wait_for_timeout(150)
    ev("document.getElementById('histBody0').scrollIntoView({block:'center'})"); page.wait_for_timeout(300); page.screenshot(path='/tmp/claude-0/shots/hist_select.png')
    chk('(2)' in ev("document.querySelector('#histSelectRow button').textContent"), 'Add button does not show the count')
    # Cancel on the confirm adds nothing
    ev("window.__ans = null; const _c = window.appConfirm; window.appConfirm = (m, ok, cancel) => { window.__msg = m; window.__ok = ok; }"); ev("histAddSelectedToToday()")
    chk('Add 2 lines' in (ev("window.__msg") or ''), 'confirm text wrong: ' + str(ev("window.__msg"))[:120]); chk(ev("state.todayLog.length") == 0, 'added before confirming')
    ev("window.__ok()"); page.wait_for_timeout(300)
    t = ev("state.todayLog")
    chk(len(t) == 2, f'expected 2 entries on Today, got {len(t)}')
    sb = next((e for e in t if e['description'] == 'Seeded bread'), {}); ch = next((e for e in t if e['description'] == 'Chicken'), {})
    chk(sb.get('fibre') == 6.4 and sb.get('polyols') == 2.1 and sb.get('amount') == '120g' and sb.get('kcal') == 276, f'copy lost figures: {sb}')
    chk('fibre' not in ch, 'fibre invented for a food that never had any')
    chk(len({e['id'] for e in t}) == 2 and all(e['id'] not in (7000001, 7000002) for e in t), 'new entries must have their own ids')
    chk(not sb.get('missedDay') and sb.get('time') != '10:12', 'copy kept the old time or the missed-day flag')
    chk(abs(ev("calcTotals(state.todayLog).fibre") - 6.4) < .01 and abs(ev("calcTotals(state.todayLog).kcal") - 480) < .01, 'Today totals wrong after adding')
    chk(ev("state.history[0].log.length") == 3, 'the original day was changed')
    chk(not ev("_histSelMode") and ev("document.querySelectorAll('.hist-sel-cb:checked').length") == 0, 'select mode did not end after adding')
    chk(ev("!document.getElementById('histEntries').classList.contains('hist-selecting')"), 'list still looks like select mode')
    # reload: entries survive, history untouched
    page.reload(); page.wait_for_timeout(1200)
    chk(ev("state.todayLog.length") == 2 and ev("state.history[0].log.length") == 3, 'after reload Today/History differ')
    # re-render and Cancel both clear the mode
    ev("renderHistory(); toggleHistSelectMode(); toggleHistSelectMode()"); chk(not ev("_histSelMode"), 'Cancel did not leave select mode')
    ev("toggleHistSelectMode(); renderHistory()"); chk(not ev("_histSelMode"), 'a re-render left select mode on')
    # normal buttons still work outside select mode
    ev("document.getElementById('histBody0').classList.add('open')"); chk(ev("[...document.querySelectorAll('.hist-act')].every(e => getComputedStyle(e).display !== 'none')"), 'row icons gone outside select mode')
    ev("copyHistEntryLine(" + y + ", 1)")
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs:', len(bugs)); [print(x) for x in bugs]; sys.exit(1 if bugs else 0)
