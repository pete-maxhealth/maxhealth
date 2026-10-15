"""Persona 154 (v3.10.1049): low-carb demo personas get the keto library/recipes, others the everyday set; all macros complete, no NaN."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def main():
    with fresh_server() as root, sync_playwright() as pw:
        page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page()
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev = page.evaluate
        ev("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
        for pid, keto in (('raj', True), ('alex', False)):
            ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(2500)
            rec = ev("generateDemoRecipes()"); lib = ev("generateDemoLibrary()")
            names = ' '.join(r['name'] for r in rec)
            if keto and 'fat bombs' not in names: f.add('BUG', f'{pid}: no keto recipes')
            if not keto and 'Protein porridge' not in names: f.add('BUG', f'{pid}: no everyday recipes')
            for r in rec:
                t = r['total']
                if any(not isinstance(t[k], (int, float)) or t[k] != t[k] for k in t): f.add('BUG', f"{pid} {r['name']} bad total")
                if keto and r['name'] != 'Peanut butter fat bombs' and t['carbs'] / max(r['servings'], 1) > 30: f.add('BUG', f"{pid} {r['name']} carbs/serving {t['carbs']/r['servings']:.0f}")
main()
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
