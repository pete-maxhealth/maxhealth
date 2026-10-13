"""Persona 144: Treatment Sessions 'Compare against' shows grouped chips for metrics with data only; Show all restores the full wall."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev("startDemoMode('bill')"); page.wait_for_timeout(1200)
    ev("renderTreatmentSessionsPicker()")
    sel = "#treatment-sessions-content button"
    names = ev(f"[...document.querySelectorAll('{sel}')].map(b=>b.textContent.trim())")
    if len(names) > 22: f.add('BUG', f'still a wall of chips: {len(names)}')
    if 'Weight' not in names: f.add('BUG', 'Weight chip missing although the persona has weight data')
    if 'Total Cholesterol' in names or 'GKI (Glucose Ketone Index)' in names: f.add('BUG', 'no-data metric chips still shown')
    heads = ev("document.getElementById('treatment-sessions-content').textContent")
    if 'Body' not in heads or 'Nutrition' not in heads: f.add('BUG', 'groups missing')
    ev("toggleTsShowAll()")
    n2 = ev(f"document.querySelectorAll('{sel}').length")
    if n2 <= len(names) + 5: f.add('BUG', f'Show all did not expand ({len(names)} -> {n2})')
    ev("toggleTsShowAll()")
    ev("toggleTreatmentMetricPill('lab_total_chol')")
    if 'Total Cholesterol' not in ev("document.getElementById('treatment-sessions-content').textContent") and 'marker' not in ev("document.getElementById('treatment-sessions-content').textContent"): f.add('BUG', 'selected metric vanished')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
