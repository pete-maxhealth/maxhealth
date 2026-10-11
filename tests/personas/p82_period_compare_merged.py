"""Persona 82: the two period-comparison cards are one (Compare Two Periods, in Trends) and it carries weight, sleep, HRV and SpO2 as well; date inputs stay inside their cards."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    page = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block').new_page()
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    if ev("!!document.getElementById('title-seasonal') || typeof runSeasonalCompare === 'function'"): f.add('BUG', 'Seasonal Compare should be gone (merged into Compare Two Periods)')
    ev("""() => { state.history = []; const fmt = n => { const d = new Date(Date.now() - n * 86400000); return String(d.getDate()).padStart(2,'0') + '/' + String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getFullYear()).slice(2); };
      for (let i = 1; i <= 40; i++) state.history.push({ date: fmt(i), weight: 92 - i * 0.01, steps: i <= 10 ? 15000 : 8000, sleep_duration: 420, hrv: 40, spo2: 95.5, totals: { kcal: 3000, protein: 150, carbs: 30 }, log: [{ description: 'x', kcal: 3000, protein: 150, carbs: 30, time: '12:00' }] }); }""")
    ev("localStorage.removeItem('mh_pcmp'); switchTab('insights'); switchSubTab('insights','trends'); renderTrends(); renderPeriodCompareCard()"); page.wait_for_timeout(500)
    txt = ev("(document.getElementById('periodCmpCard')||document.getElementById('trends-periodcmp-wrap')||document.body).innerText")
    for want in ('Avg steps', 'Avg weight', 'Avg sleep', 'Avg HRV', 'Avg SpO2'):
        if want not in txt: f.add('BUG', f'Compare Two Periods lacks a "{want}" row')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
