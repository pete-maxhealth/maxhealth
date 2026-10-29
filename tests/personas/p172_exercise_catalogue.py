"""Persona 172 (v3.10.1072): exercise catalogue + picker. Known activities carry their own MET, indoor/outdoor, effort wording and
distance behaviour; typed names are recognised; the Plan box can use any of them."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block'); page = ctx.new_page()
    errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("startDemoMode('alex')"); page.wait_for_timeout(2200)
    ev("document.getElementById('maintab-today').click()"); page.wait_for_timeout(400)
    check('catalogue has 50+ entries', ev("MH_EX_CATALOG.length") >= 50)
    check('every catalogue MET ordered Easy<=Moderate<=Hard and sane', ev("MH_EX_CATALOG.every(r=>r[5]<=r[6]&&r[6]<=r[7]&&r[5]>=1.5&&r[7]<=13)"))
    check('every entry has 3 hints and a known category', ev("MH_EX_CATALOG.every(r=>r[10].length===3&&MH_EX_CATS[r[3]])"))
    check('MET table gained catalogue ids', ev("!!MET.badminton && MET.badminton.Moderate===5.5"))
    # picker
    ev("addCustomActivity()"); page.wait_for_timeout(300)
    n_all = ev("document.querySelectorAll('#mhPickList .mh-card').length")
    check('picker shows the whole list plus the custom line', n_all >= 55, str(n_all))
    ev("_pickWhere='in';mhRenderPickerList()")
    names_in = ev("[...document.querySelectorAll('#mhPickList .nm')].map(e=>e.textContent)")
    check('indoor filter keeps Squash, drops Kayaking', 'Squash' in names_in and 'Kayaking' not in names_in, str(names_in[:8]))
    ev("_pickWhere='all';_pickCat='racket';mhRenderPickerList()")
    names_r = ev("[...document.querySelectorAll('#mhPickList .nm')].map(e=>e.textContent)")
    check('racket category lists Badminton and Padel', any('Badminton' in n for n in names_r) and any('Padel' in n for n in names_r))
    ev("_pickCat='all';_pickQ='kayak';mhRenderPickerList()")
    check('search finds Kayaking', 'Kayaking' in ev("document.getElementById('mhPickList').textContent"))
    ev("_pickQ='zzzz';mhRenderPickerList()")
    check('no match shows the helpful message', 'Nothing matches' in ev("document.getElementById('mhPickList').textContent"))
    # add Badminton
    ev("_pickQ='';mhPickExercise('badminton')"); page.wait_for_timeout(400)
    b = ev("getActivities().find(a=>a.type==='badminton')")
    check('badminton added, enabled, no distance box', b and b['enabled'] and not b['needsDistance'], str(b))
    ev("updateActivity(getActivities().findIndex(a=>a.type==='badminton'),'duration','60',false); updateActivity(getActivities().findIndex(a=>a.type==='badminton'),'effort','Hard',false)")
    w = ev("state.weight||90")
    k = ev("calcActivityKcalRaw(getActivities().find(a=>a.type==='badminton'))")
    check('badminton kcal = 7.0 MET x kg x 1h', k == round(7.0 * w), f'{k} vs {7.0*w}')
    row = ev("document.getElementById('activityRows').innerText")
    check('row shows indoor tag', 'indoor' in row.lower())
    opt = ev("[...document.querySelectorAll('#activityRows select option')].map(o=>o.textContent).join('|')")
    check('effort options carry activity wording', 'Competitive match' in opt, opt[:200])
    # no duplicate
    ev("mhPickExercise('badminton')")
    check('adding twice does not duplicate', ev("getActivities().filter(a=>a.type==='badminton').length") == 1)
    # distance-aware catalogue item
    ev("mhPickExercise('treadmill_run')"); page.wait_for_timeout(300)
    ev("(()=>{const a=getActivities(); const i=a.findIndex(x=>x.type==='treadmill_run'); a[i].duration='30'; a[i].distance='5'; a[i].distanceUnit='km'; saveActivities(a); })()")
    eff = ev("calcSuggestedEffort(getActivities().find(a=>a.type==='treadmill_run'))")
    check('treadmill run 5km in 30 min -> effort from running bands', eff in ('Moderate', 'Hard'), str(eff))
    # free-text recognition
    ev("_doAddCustomActivity('Padel with the lads')"); page.wait_for_timeout(300)
    check('typed Padel recognised from the catalogue', ev("getActivities().some(a=>a.type==='padel')"))
    ev("mhExMatch('Squash')"); 
    check('whole-word matching: "arrow" is not rowing', ev("mhExMatch('arrow practice')") is None)
    check('longest alias wins', ev("mhExMatch('treadmill run').id") == 'treadmill_run')
    # unknown stays generic
    check('unknown name has no match', ev("mhExMatch('Basket weaving')") is None)
    # plan ahead with a catalogue item, Done adds it
    ev("localStorage.setItem('mh_plan_open','1'); mhXPlanSetType('kayak'); mhXPlanSetAmt(60)")
    ev("mhWiMore()"); page.wait_for_timeout(300); ev("mhPickExercise('kayak')"); page.wait_for_timeout(400)
    check('What if: More… picks kayaking without adding it to the list', 'Kayaking' in ev("document.getElementById('whatIf').textContent") and not ev("getActivities().some(a=>a.type==='kayak')"))
    ev("mhXPlanAdd('activity','kayak',60,'Moderate')"); pid = ev("mhXPlanItems()[0].id")
    check('planned kayak earns (5.0 - 1) MET x kg net of resting', ev("mhXPlanItemEffect(mhXPlanItems()[0]).kcal") == round(4.0 * w))
    ev(f"mhXPlanDone('{pid}')"); page.wait_for_timeout(300)
    kk = ev("getActivities().find(a=>a.type==='kayak')")
    check('Done auto-adds kayak and logs it', kk and kk['enabled'] and kk['duration'] == '60', str(kk))
    # history edit infers a catalogue type
    check('core activities still resolve (walking)', ev("MH_EX_CORE.walking.hints.length") == 3)
    check('no JS errors', not errs, str(errs[:2]))
    ev("addCustomActivity()"); page.wait_for_timeout(300)
    page.screenshot(path='/tmp/claude-0/pp/picker.png')
print('p172:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
