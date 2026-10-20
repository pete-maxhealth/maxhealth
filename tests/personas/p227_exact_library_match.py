"""Persona 227: an AI-suggested ingredient lands on the library food of the same name (v3.10.1125). Found while recording the tour: "Olive oil" was
matched to "Sardines in olive oil, drained" because that food came first in the library and both scored 100%. Covers: an exact name wins whatever the
library order (also with different case / spacing); on a tie the closest name (fewest extra words) wins; a fuzzy match is still found when there is no
exact one; a brand or meat mismatch still blocks a match. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    def food(n): return {'name': n, 'kcal': 100, 'protein': 5, 'fat': 3, 'carbs': 10, 'portion': '100g'}
    ev("l=>saveLibrary(l)", [food('Sardines in olive oil, drained'), food('Extra virgin olive oil bottle'), food('Olive oil'), food('Chicken thigh, roasted'), food('Beef mince, cooked')])
    find = lambda n: (ev("(n)=>fuzzyFindInLibrary(n)?.name || null", n) or "").lower() or None
    if find('Olive oil') != 'olive oil': f.add('BUG', f'exact name wins over an earlier longer name: {find("Olive oil")}')
    if find('  olive OIL ') != 'olive oil': f.add('BUG', f'exact name ignores case and spacing: {find("  olive OIL ")}')
    ev("l=>saveLibrary(l)", [food('Sardines in olive oil, drained'), food('Olive oil spray'), food('Chicken thigh, roasted')])
    if find('Olive oil') != 'olive oil spray': f.add('BUG', f'with no exact name, the closest (fewest extra words) wins: {find("Olive oil")}')
    ev("l=>saveLibrary(l)", [food('Oil olive'), food('Olive oil')])
    if find('Olive oil') != 'olive oil': f.add('BUG', f'an exact name beats an equally close one that came first: {find("Olive oil")}')
    ev("l=>saveLibrary(l)", [food('Sardines in olive oil, drained'), food('Olive oil spray'), food('Chicken thigh, roasted')])
    if find('Chicken thigh') != 'chicken thigh, roasted': f.add('BUG', f'a fuzzy match is still found: {find("Chicken thigh")}')
    if find('Beef thigh') is not None: f.add('BUG', 'a meat mismatch still blocks a match')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
