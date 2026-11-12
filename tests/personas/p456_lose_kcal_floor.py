"""Persona 456: the weight-loss calorie suggestion never goes below 1,200 kcal (women) / 1,500 kcal (men) or above maintenance (Pete, 12 Nov 2026: Jill's friends are starting a diet).
Set-up: a small woman is raised to 1,200 and told why; an ordinary case keeps TDEE-500 and shows no floor note; a small man gets 1,500; maintain/gain unchanged.
Settings/Suggested-targets paths use the same helper and a typed or confirmed target is never rewritten. Invented people only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
CASES = [  # name, sex, age, h cm, w kg, target, activity, goal, expected kcal, floor note expected
 ('Tiny', 'female', '30', '160', '52', '45', 'light', 'lose', 1200, True),
 ('Sam', 'female', '33', '165', '75', '60', 'light', 'lose', 1501, False),
 ('Alex', 'male', '40', '175', '95', '80', 'sedentary', 'lose', 1719, False),
 ('Wee', 'male', '60', '160', '55', '50', 'sedentary', 'lose', 1500, True),
 ('Sam2', 'female', '33', '165', '75', '70', 'light', 'maintain', 2001, False),
]
with fresh_server() as root, sync_playwright() as pw:
    for (n, sx, age, h, w, t, act, goal, want, note) in CASES:
        ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); page = ctx.new_page(); ev = page.evaluate
        page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:300])); page.on('dialog', lambda d: d.dismiss())
        page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
        ev('onboardNext(2)'); page.fill('#onboardName', n); ev('onboardNext(3)'); ev(f"obSetSex('{sx}')"); page.fill('#onboardAge', age)
        ev("setHeightUnit('cm')"); page.fill('#onboardHeight', h); ev("setWeightUnit('kg')"); page.fill('#onboardWeight', w); page.fill('#onboardTarget', t)
        ev('onboardNext(4)'); ev(f"obSetActivity('{act}')"); ev(f"obSetGoal('{goal}')")
        got = int(page.input_value('#onboardKcal')); br = ev("document.getElementById('tdeeBreakdown').textContent")
        if got != want: f.add('BUG', f'1: {n}: suggested {got} kcal, expected {want} ({br})')
        if note != ('lowest we suggest' in br): f.add('BUG', f'2: {n}: floor note {"missing" if note else "shown when not needed"}: {br}')
        ev('onboardNext(5)'); ev("obSetCondition('general')"); ev("obSetStart('everything')"); ev('onboardNext(6)'); ev('onboardFinish()'); page.wait_for_timeout(1500)
        saved = ev("parseInt(localStorage.getItem('mh_target_kcal'))")
        if saved != want: f.add('BUG', f'3: {n}: saved target {saved}, expected {want}')
        if goal == 'lose':
            # Settings paths: re-derive without crashing; a confirmed (typed) target is left alone
            ev("localStorage.setItem('mh_target_kcal','1100'); try{ switchTabById('manage') }catch(e){}"); page.wait_for_timeout(600)
            if ev("parseInt(localStorage.getItem('mh_target_kcal'))") != 1100: f.add('BUG', f'4: {n}: a typed target was rewritten by opening Settings')
            if ev("typeof mhLoseKcal") != 'function' or ev("mhLoseKcal(1662,'female')") != 1200 or ev("mhLoseKcal(2219,'male')") != 1719 or ev("mhLoseKcal(1300,'female')") != 1200 or ev("mhLoseKcal(1100,'female')") != 1100:
                f.add('BUG', '5: helper gives wrong values')
        ctx.close()
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
