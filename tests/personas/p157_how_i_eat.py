"""Persona 157 (v3.10.1053): 'How I eat' lifestyle layer. A thyroid persona picks Mediterranean: profile and ceilings unchanged, the macro ratio
card judges the day against the Mediterranean ranges, the AI is told the lifestyle, no keto wording appears, a keto profile gets no picker,
and a demo never leaks the choice into a real account."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); ev = page.evaluate
    ev("state.onboarded=true; localStorage.setItem('mh_ceil_standard','150'); saveState()"); page.reload(); page.wait_for_timeout(1500)
    pid = ev("(DEMO_PERSONAS.find(p=>/thyroid/i.test(p.id+p.condition+(p.name||'')))||DEMO_PERSONAS.find(p=>p.condition==='general')).id")
    ev(f"startDemoMode('{pid}')"); page.wait_for_timeout(2500)
    cond0 = ev("localStorage.getItem('mh_condition')"); ceil0 = ev("localStorage.getItem('mh_ceil_standard')")
    ev("siteSearchOpenSettings('condition','manage','settings','')"); page.wait_for_timeout(600); ev("mhGoKetoRender()")
    if not ev("!!document.getElementById('mhLifestyleSel')"): f.add('BUG', 'no How I eat picker for a non-keto profile')
    ev("mhLifestyleSet('mediterranean')"); page.wait_for_timeout(500)
    if ev("localStorage.getItem('mh_lifestyle')") != 'mediterranean': f.add('BUG', 'lifestyle not stored')
    if ev("localStorage.getItem('mh_condition')") != cond0 or ev("localStorage.getItem('mh_ceil_standard')") != ceil0: f.add('BUG', 'profile or ceilings changed by choosing a lifestyle')
    if ev("isKetogenicCondition()"): f.add('BUG', 'a non-keto lifestyle switched keto on')
    ev("switchTab('today',document.getElementById('maintab-today'))"); page.wait_for_timeout(800)
    ev("renderMacroRatioBar({kcal:1200,protein:60,carbs:140,fat:45}, 405)"); page.wait_for_timeout(300)
    txt = ev("(document.getElementById('macroRatioCard')||{}).innerText||''")
    if 'Mediterranean' not in txt: f.add('BUG', f'ratio card does not show the Mediterranean plan: {txt[:120]!r}')
    if re.search(r'keto', txt, re.I): f.add('BUG', 'keto wording on the ratio card for Mediterranean')
    if 'Mediterranean' not in ev("mhDietWho()") or re.search('keto', ev("mhDietWho()"), re.I): f.add('BUG', f"AI phrase wrong: {ev('mhDietWho()')}")
    # plan adherence: a day inside the Mediterranean ranges counts, a day outside does not
    pa = ev("mhPlanAdherence([{totals:{kcal:2000,carbs:225,protein:80,fat:80}},{totals:{kcal:2000,carbs:60,protein:150,fat:110}}])")
    if not pa or pa['n'] != 2 or pa['ok'] != 1 or pa['pct'] != 50: f.add('BUG', f'plan adherence wrong: {pa}')
    # custom ratio: validated, stored, used with a 5 point margin
    ev("document.getElementById('mhLifestyleSel').value='custom'; mhLifestyleSet('custom')"); page.wait_for_timeout(300)
    ev("document.getElementById('mhLsC').value=40; document.getElementById('mhLsP').value=30; document.getElementById('mhLsF').value=30; mhLifestyleCustomSave()")
    ls = ev("mhLifestyle()")
    if not ls or ls['label'] != 'My own ratio' or ls['c'] != [35, 45]: f.add('BUG', f'custom ratio not applied: {ls}')
    ev("document.getElementById('mhLsC').value=90; mhLifestyleCustomSave()")
    if ev("JSON.parse(localStorage.getItem('mh_lifestyle_custom')).c") != 40: f.add('BUG', 'a ratio that does not add to 100 was saved')
    ev("mhLifestyleSet('mediterranean')")
    # keto wins if both are on, and stopping keto leaves the lifestyle
    ev("localStorage.setItem('mh_keto_opt','1')")
    if not ev("isKetogenicCondition()"): f.add('BUG', 'keto opt-in not honoured alongside a lifestyle')
    ev("localStorage.removeItem('mh_keto_opt')")
    ev("localStorage.setItem('mh_lifestyle','mediterranean')"); ev("exitDemoMode()"); page.wait_for_timeout(1500)
    if ev("localStorage.getItem('mh_lifestyle')"): f.add('BUG', 'lifestyle leaked out of the demo into the real account')
    ev("startDemoMode('raj')"); page.wait_for_timeout(2500)
    ev("siteSearchOpenSettings('condition','manage','settings','')"); page.wait_for_timeout(500); ev("mhGoKetoRender()")
    if ev("!!document.getElementById('mhLifestyleSel')"): f.add('BUG', 'keto profile (Raj) offered a lifestyle picker')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
