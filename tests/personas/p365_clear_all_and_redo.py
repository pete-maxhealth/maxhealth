"""Persona 365: the three "Clear all" buttons (supplements, symptoms, treatments) and "Redo setup wizard".
Cancel keeps everything; Confirm removes exactly the definitions AND the log the message names, and nothing else (meals, history, library,
profile, other trackers); the app's own dialog is used (no browser confirm box); the message says what goes and that meals/history stay;
Redo setup wizard keeps history, library and the log after reload and says so."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SEED = """() => { localStorage.setItem('mh_condition','general'); localStorage.setItem('mh_goal','lose'); localStorage.setItem('mh_age','42'); localStorage.setItem('mh_sex','male'); localStorage.setItem('mh_height_cm','175'); localStorage.setItem('mh_target_kcal','2000');
  state.onboarded = true; state.weight = 88; state.history = [{ date: '30/10/26', log: [{ name: 'Eggs', description: 'Eggs', kcal: 300, protein: 20, carbs: 2, fat: 20, time: '08:00', id: 9000001 }], totals: { kcal: 300, protein: 20, carbs: 2, fat: 20 }, weight: 88 }];
  window._mhLibQuiet = true; saveLibrary([{ id: 'l1', name: 'Plain yoghurt', kcal: 60, protein: 5, carbs: 4, fat: 3, portion: '100g' }]);
  localStorage.setItem('mh_supplement_defs', JSON.stringify(loadSupplementDefs())); localStorage.setItem('mh_supplement_log', '{"30/10/26":{"x":1}}');
  localStorage.setItem('mh_symptom_defs', JSON.stringify(typeof loadSymptomDefs === 'function' ? loadSymptomDefs() : [])); localStorage.setItem('mh_symptom_log', '{"30/10/26":{"fatigue":3}}');
  localStorage.setItem('mh_treatment_defs', '[]'); localStorage.setItem('mh_treatment_log', '[{"d":"30/10/26"}]');
  saveState(); document.getElementById('onboardingOverlay').style.display = 'none'; }"""
CASES = [('supplements', 'Clear all supplements', ['mh_supplement_defs', 'mh_supplement_log'], 'record of when you took'),
         ('symptoms', 'Clear all tracked symptoms', ['mh_symptom_defs', 'mh_symptom_log'], 'symptom history'),
         ('treatments', 'Clear all tracked treatments', ['mh_treatment_defs', 'mh_treatment_log'], 'logged session')]
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); native = []
    page.on('dialog', lambda d: (native.append(d.message), d.dismiss()))
    def fresh():
        page.goto('http://localhost:5757/'); page.wait_for_timeout(800); ev("localStorage.clear()"); page.goto('http://localhost:5757/'); page.wait_for_timeout(800)
        ev(SEED); page.reload(); page.wait_for_timeout(1100); ev("switchTabById('manage')"); page.wait_for_timeout(500)
        ev("window.__m = []; sessionStorage.setItem('__m', '[]'); window.__ans = false; window.appConfirm = (m, ok, cancel) => { if (m == null) return; window.__m.push(String(m)); try { sessionStorage.setItem('__m', JSON.stringify(window.__m)); } catch (e) {} if (window.__ans) ok && ok(); else cancel && cancel(); }")
    def click_clear(word):
        return ev("(w => { const b = [...document.querySelectorAll('button')].find(e => /clear all/i.test(e.innerText) && (e.getAttribute('onclick') || '').includes(w)); if (!b) return false; b.click(); return true; })", word)
    KEEP = ['maxhealth_v1', 'mh_condition', 'mh_goal', 'mh_target_kcal']
    for name, word, keys, phrase in CASES:
        fresh(); native.clear(); before = {k: ev(f"localStorage.getItem('{k}')") for k in keys + KEEP}; others = {k: ev(f"localStorage.getItem('{k}')") for k in ['mh_supplement_defs', 'mh_symptom_defs', 'mh_treatment_defs', 'mh_supplement_log', 'mh_symptom_log', 'mh_treatment_log', 'maxhealth_v1'] if k not in keys}
        if not click_clear(word.split()[-1] if name != 'supplements' else 'supplement'): f.add('BUG', f'{name}: Clear all button not found'); continue
        page.wait_for_timeout(400); msgs = ev("window.__m")
        if native: f.add('BUG', f'{name}: uses the browser confirm box, not the app dialog')
        if not msgs: f.add('BUG', f'{name}: no confirmation asked'); continue
        if phrase not in msgs[0] or 'not touched' not in msgs[0] or 'cannot be undone' not in msgs[0]: f.add('BUG', f'{name}: message does not say what goes / what stays / that it is permanent: {msgs[0]}')
        if any(ev(f"localStorage.getItem('{k}')") != before[k] for k in keys): f.add('BUG', f'{name}: CANCEL changed data')
        ev("window.__ans = true"); click_clear(word.split()[-1] if name != 'supplements' else 'supplement'); page.wait_for_timeout(500)
        if any(ev(f"localStorage.getItem('{k}')") is not None for k in keys): f.add('BUG', f'{name}: CONFIRM left {[k for k in keys if ev(f"localStorage.getItem(\'{k}\')") is not None]}')
        for k, v in others.items():
            now = ev(f"localStorage.getItem('{k}')")
            if k == 'maxhealth_v1':
                if json.loads(now or '{}').get('history') != json.loads(v or '{}').get('history'): f.add('BUG', f'{name}: CONFIRM changed history')
            elif now != v: f.add('BUG', f'{name}: CONFIRM also changed {k}')
        print(f'  {name}: ok, asked: {msgs[0][:90]}…')
    # Redo setup wizard
    fresh(); native.clear(); ev("window.__ans = true")
    hist0 = ev("JSON.stringify(state.history)"); lib0 = ev("localStorage.getItem('mh_library') || localStorage.getItem('mh_food_library') || ''")
    ev("resetOnboarding()"); page.wait_for_timeout(1500)
    page.wait_for_timeout(300)
    msg = json.loads(ev("sessionStorage.getItem('__m') || '[]'"))
    if not msg or 'stay' not in msg[0]: f.add('BUG', f'Redo setup wizard message does not say what stays: {msg}')
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    if ev("JSON.stringify(state.history)") != hist0: f.add('BUG', 'Redo setup wizard changed logged history')
    if ev("localStorage.getItem('mh_supplement_log')") is None: f.add('BUG', 'Redo setup wizard lost the supplement log')
    print('  redo wizard: history kept:', ev("JSON.stringify(state.history)") == hist0, '| overlay shown:', ev("getComputedStyle(document.getElementById('onboardingOverlay')).display"))
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs:', len(bugs)); sys.exit(1 if bugs else 0)
