"""Persona 77: the incidental steps baseline follows the Activity Level, and the Activity Level follows real WEEKLY steps (2+ consistent weeks, 5+ days each)."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SEED = """(spec) => { const pad = n => String(n).padStart(2,'0'); const out = [];
  spec.forEach(([offset, steps]) => { const d = new Date(); d.setDate(d.getDate() - offset); out.push({date: pad(d.getDate())+'/'+pad(d.getMonth()+1)+'/'+String(d.getFullYear()).slice(2), steps, log: [], totals: {kcal: 0, protein: 0, carbs: 0, fat: 0}}); });
  state.history = out; saveState(); localStorage.removeItem('mh_last_auto_activity_check'); }"""
def run(page, spec, level='moderate', extra=''):
    page.evaluate("l => { localStorage.setItem('mh_activity_level', l); localStorage.removeItem('mh_activity_autoswitch_status'); localStorage.removeItem('mh_steps_baseline'); localStorage.removeItem('mh_steps_baseline_mode'); }", level)
    if extra: page.evaluate(extra)
    page.evaluate(SEED, spec); page.evaluate("checkActivityLevelAutoSwitch()")
    return page.evaluate("[localStorage.getItem('mh_activity_level'), getStepsBaseline(), localStorage.getItem('mh_activity_autoswitch_status')]")
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("localStorage.setItem('mh_onboarded','1'); localStorage.setItem('mh_notif_activity_autoswitch','off')")
    days = lambda n, v, start=1: [(start + i, v) for i in range(n)]
    # two solid weeks at 13,000 -> Very active, baseline follows to 9,500
    lvl, base, st = run(page, days(14, 13000))
    if lvl != 'active' or base != 9500: f.add('BUG', f'two weeks at 13k should move to active / 9500, got {lvl} {base}')
    # two weeks at 4,000 -> sedentary, baseline 5,000
    lvl, base, st = run(page, days(14, 4000))
    if lvl != 'sedentary' or base != 5000: f.add('BUG', f'two weeks at 4k should move to sedentary / 5000, got {lvl} {base}')
    # weeks that disagree: no change
    lvl, base, st = run(page, days(7, 13000, 1) + days(7, 4000, 8))
    if lvl != 'moderate' or 'same activity tier' not in (st or ''): f.add('BUG', f'mixed weeks must not switch: {lvl} / {st}')
    # not enough days in a week: says so, no change
    lvl, base, st = run(page, days(14, 13000)[:4] + days(7, 13000, 8))
    if lvl != 'moderate' or '5 or more days' not in (st or ''): f.add('BUG', f'a week with under 5 days must not switch: {lvl} / {st}')
    # today alone does not count, and matching steps = no change
    lvl, base, st = run(page, days(14, 9500))
    if lvl != 'moderate' or 'still match' not in (st or ''): f.add('BUG', f'steady week should say it still matches: {lvl} / {st}')
    # manual baseline survives a level change
    lvl, base, st = run(page, days(14, 13000), extra="localStorage.setItem('mh_steps_baseline','6200'); localStorage.setItem('mh_steps_baseline_mode','manual')")
    if lvl != 'active' or base != 6200: f.add('BUG', f'manual baseline must not be overridden: {lvl} {base}')
    # a baseline someone saved before this feature (no mode) stays manual
    page.evaluate("localStorage.removeItem('mh_steps_baseline_mode'); localStorage.setItem('mh_steps_baseline','8100')")
    if page.evaluate("getStepsBaseline()") != 8100 or page.evaluate("mhStepsBaselineIsAuto()"): f.add('BUG', 'an existing typed baseline should stay manual')
    # a brand-new user is automatic
    page.evaluate("localStorage.removeItem('mh_steps_baseline'); localStorage.removeItem('mh_steps_baseline_mode'); localStorage.setItem('mh_activity_level','light')")
    if page.evaluate("getStepsBaseline()") != 5000 or not page.evaluate("mhStepsBaselineIsAuto()"): f.add('BUG', 'a new user should get the automatic baseline for their level')
    # the card: toggle works both ways and hides the manual controls
    page.evaluate("switchTab('settings'); switchSubTab('settings','manage'); mhTopicSet('manage','all'); initSettings()"); page.wait_for_timeout(500)
    if page.evaluate("getComputedStyle(document.getElementById('stepsBaselineManual')).display") != 'none': f.add('BUG', 'manual controls should be hidden while automatic')
    page.evaluate("setStepsBaselineAuto(false)")
    if page.evaluate("getComputedStyle(document.getElementById('stepsBaselineManual')).display") == 'none': f.add('BUG', 'manual controls should show when automatic is off')
    if page.evaluate("localStorage.getItem('mh_steps_baseline')") != '5000': f.add('BUG', 'turning automatic off should keep the current value, not jump')
    page.evaluate("document.getElementById('settingStepsBaseline').value = '6400'; saveStepsBaseline()")
    if page.evaluate("getStepsBaseline()") != 6400 or page.evaluate("mhStepsBaselineIsAuto()"): f.add('BUG', 'typing a baseline should make it manual')
    page.evaluate("setStepsBaselineAuto(true)")
    if page.evaluate("getStepsBaseline()") != 5000: f.add('BUG', 'switching Automatic back on should use the level baseline')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
