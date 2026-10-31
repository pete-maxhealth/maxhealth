"""Persona 363: a standard General Health user (not clinical) sets up through the real onboarding, then uses the app for 8 weeks.
Usage: p363_general_journey.py improving|maintenance|struggling
improving   = eats to target, loses weight steadily, sleep/steps improve.
maintenance = holds weight, steady habits.
struggling  = eats far under target, loses weight fast without meaning to, poor sleep, resting heart rate climbing:
              the app should say something sensible (this is where a person needs a clinician, not more tracking).
Seeded days use the same history format the app writes. Test data only. Writes screen text to /tmp/claude-0/crawl/p363_<name>.json"""
import sys, re, json, random; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
T = sys.argv[1] if len(sys.argv) > 1 else 'improving'
SETUP = {'improving': dict(w=92, tgt=82, goal='lose'), 'maintenance': dict(w=82, tgt=82, goal='maintain'), 'struggling': dict(w=80, tgt=80, goal='maintain')}[T]
DAYS = 56; random.seed({'improving': 1, 'maintenance': 2, 'struggling': 3}[T])
CLIN = re.compile(r'ketone|ketosis|ketogenic|\bGKI\b|glioma|\bGBM\b|glioblastoma|seizure|epilep|migraine|cluster headache|insulin|hypoglyc|\bMRI\b|chemo|temozolomide|oncolog|diabet', re.I)
f = Findings(); out = {}
CLICK = """(labels) => { const o=document.getElementById('onboardingOverlay'); const vis=e=>{const r=e.getBoundingClientRect();return r.width>2&&r.height>2&&getComputedStyle(e).display!=='none'};
  const els=[...o.querySelectorAll('button,[onclick]')].filter(vis); for (const l of labels){ const b=els.find(e=>(e.innerText||'').trim().toUpperCase().startsWith(l)); if(b){b.click(); return l;} } return null; }"""
def body_text(page):
    return page.evaluate("""() => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let o = [], n; while (n = w.nextNode()) { const e = n.parentElement; if (!e || ['SCRIPT','STYLE'].includes(e.tagName)) continue; const r = e.getBoundingClientRect(), s = getComputedStyle(e); if (r.width > 2 && r.height > 2 && s.display !== 'none' && s.visibility !== 'hidden') o.push(n.nodeValue.trim()); } return o.filter(Boolean).join(' | '); }""")
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); ev = page.evaluate
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1800)
    # ---- real onboarding ----
    for step in range(12):
        if ev("getComputedStyle(document.getElementById('onboardingOverlay')).display") == 'none': break
        for k, v in {'onboardName': 'Test ' + T, 'onboardAge': '42', 'onboardHeight': '175', 'onboardWeight': str(SETUP['w']), 'onboardTarget': str(SETUP['tgt'])}.items():
            if page.query_selector('#' + k) and page.is_visible('#' + k): page.fill('#' + k, v)
        for sel in ('#ob-sexBtn-male', '#ob-actBtn-light', '#ob-goalBtn-' + SETUP['goal'], '#ob-condBtn-general', '#ob-startBtn-simple'):
            if page.query_selector(sel) and page.is_visible(sel): page.click(sel)
        if 'No set pattern' in (ev("document.getElementById('onboardingOverlay').innerText") or ''):
            ev("(() => { const b = [...document.querySelectorAll('#onboardingOverlay button,#onboardingOverlay [onclick]')].find(e => /^No set pattern/.test(e.innerText.trim())); if (b) b.click(); })()")
        ev(CLICK, ['NEXT', 'GET STARTED', 'START TRACKING']); page.wait_for_timeout(500)
    else: f.add('BUG', 'onboarding never closed')
    cond, goal = ev("localStorage.getItem('mh_condition')"), ev("localStorage.getItem('mh_goal')")
    tk, tp, tc = (int(ev(f"localStorage.getItem('mh_target_{k}')") or 0) for k in ('kcal', 'protein', 'carbs'))
    print('   goal-ish keys after onboarding:', ev("Object.keys(localStorage).filter(k=>/goal/i.test(k)).map(k=>k+'='+localStorage.getItem(k))"), ev("typeof state.goal!=='undefined'?state.goal:'(no state.goal)'"))
    print(f'{T}: condition={cond} goal={goal} targets kcal={tk} protein={tp} carbs={tc}'); out['setup'] = dict(cond=cond, goal=goal, kcal=tk, protein=tp, carbs=tc)
    if cond != 'general': f.add('BUG', f'condition {cond}')
    # ---- 8 weeks of use ----
    hist = []
    for i in range(DAYS - 1, 0, -1):
        p = 1 - i / (DAYS - 1); d = ev(f"(() => {{ const x = new Date(); x.setDate(x.getDate() - {i}); return x.getDate().toString().padStart(2,'0') + '/' + (x.getMonth()+1).toString().padStart(2,'0') + '/' + String(x.getFullYear()).slice(2); }})()")
        fr = {'improving': random.uniform(.93, 1.04), 'maintenance': random.uniform(.96, 1.06), 'struggling': random.uniform(.45, .62)}[T]
        kc = round(tk * fr); pr = round(kc * (0.25 if T != 'struggling' else 0.18) / 4); ca = round(kc * 0.30 / 4); fa = round((kc - pr * 4 - ca * 4) / 9)
        log = [dict(name=n, description=n, kcal=round(kc * s), protein=round(pr * s), carbs=round(ca * s), fat=round(fa * s), time=t, id=f'p363_{i}_{k}') for k, (n, s, t) in enumerate([('Breakfast', .28, '08:00'), ('Lunch', .34, '13:00'), ('Dinner', .38, '19:00')])]
        e = dict(date=d, log=log, totals=dict(kcal=sum(x['kcal'] for x in log), protein=sum(x['protein'] for x in log), carbs=sum(x['carbs'] for x in log), fat=sum(x['fat'] for x in log)))
        w = {'improving': SETUP['w'] - (SETUP['w'] - 84.5) * p, 'maintenance': 82 + random.uniform(-.5, .5), 'struggling': 80 - 9 * p}[T] + random.uniform(-.25, .25)
        if i % 2 == 0: e['weight'] = round(w, 1)
        e['steps'] = round({'improving': 5000 + 4200 * p, 'maintenance': 8000, 'struggling': 4200 - 1500 * p}[T] * random.uniform(.85, 1.15))
        sl = {'improving': 6.3 + 1.2 * p, 'maintenance': 7.2, 'struggling': 5.4 - 0.9 * p}[T] * 60 * random.uniform(.93, 1.07); sl = round(sl)
        e.update(sleep_duration=sl, sleep_deep=round(sl * .16), sleep_rem=round(sl * .2), sleep_light=sl - round(sl * .36), sleep_wake=20, sleep_efficiency=90, hr_resting=round({'improving': 66 - 6 * p, 'maintenance': 62, 'struggling': 64 + 14 * p}[T] + random.uniform(-1.5, 1.5)), water_ml=round({'struggling': 900}.get(T, 2200) * random.uniform(.8, 1.2)))
        if i % 7 in (1, 3, 5) and T != 'struggling': e['exercises'] = [dict(type='walking', name='🚶 Walking', duration='35', effort='Moderate', kcal=140)]
        if i % 7 == 0:   # weekly body-composition reading (scales/wearable): maintenance only wobbles by ~0.1 kg
            fm = {'improving': 24.0 - 6.0 * p, 'maintenance': 18.0 + random.uniform(-.15, .15), 'struggling': 17.0 - 3.0 * p}[T]
            mm = {'improving': 60.0 - 0.3 * p, 'maintenance': 61.0 + random.uniform(-.15, .15), 'struggling': 59.0 - 2.4 * p}[T]
            e['fat_mass_kg'] = round(fm, 1); e['muscle_mass_kg'] = round(mm, 1)
        hist.append(e)
    ev("(h => { state.history = h; state.weight = h.filter(x => x.weight).slice(-1)[0].weight; saveState(); })", ) if False else ev("h => { state.history = h; state.weight = h.filter(x => x.weight).slice(-1)[0].weight; saveState(); }", hist)
    rows = ['date,weight,fat_mass_kg,muscle_mass_kg,steps,hr_resting']
    for e in hist:
        dd, mm, yy = e['date'].split('/')
        if 'fat_mass_kg' in e or 'weight' in e: rows.append(f"20{yy}-{mm}-{dd},{e.get('weight','')},{e.get('fat_mass_kg','')},{e.get('muscle_mass_kg','')},{e['steps']},{e['hr_resting']}")
    ev("t => { localStorage.setItem('mh_combined_csv_cache', t); localStorage.setItem('mh_combined_csv_meta', JSON.stringify({date: new Date().toLocaleDateString('en-GB'), rows: 99})); }", '\n'.join(rows))
    page.reload(); page.wait_for_timeout(1500)
    print('history days:', ev("state.history.length"), 'weight now:', ev("state.weight"))
    import os; os.makedirs(f'/tmp/claude-0/crawl/p363_{T}', exist_ok=True)
    for scr in ('dash', 'move', 'hist', 'trends', 'stats', 'reports'):
        try: ev(f"switchTabById('{scr}')")
        except Exception as ex: f.add('JS-exception', f'{scr}: {str(ex)[:100]}'); continue
        page.wait_for_timeout(1400); txt = body_text(page); out[scr] = txt[:6000]
        page.screenshot(path=f'/tmp/claude-0/crawl/p363_{T}/{scr}.png', full_page=False)
        for w in ('NaN', 'undefined', 'Infinity', '[object Object]'):
            if re.search(r'(?<![\w-])' + re.escape(w) + r'(?![\w-])', txt): f.add('BUG', f'{scr}: {w} visible')
        for m in CLIN.finditer(txt): f.add('clinical-wording', f'{scr}: …{txt[max(0, m.start() - 40):m.end() + 40]}…')
        print(f'  {scr}: {len(txt)} chars of text')
    allt = ' || '.join(out[k] for k in ('move', 'trends', 'stats', 'reports') if k in out)
    verdicts = sorted(set(re.findall(r'(Gaining fat[a-z ,]*|Losing fat[a-z ,]*|Losing muscle|Gaining muscle|Holding steady)', allt)))
    print('  body-composition verdict text:', verdicts)
    if T == 'maintenance' and any(v.startswith(('Gaining fat', 'Losing fat', 'Losing muscle')) for v in verdicts): f.add('BUG', f'noise reported as a change: {verdicts}')
    if T == 'improving' and not any(v.startswith('Losing fat') for v in verdicts): f.add('check', f'improving user: no "Losing fat" verdict ({verdicts})')
    for m in re.finditer(r'(?i)(gain\w*|lost|loss|losing|up|down|increase\w*|decrease\w*|[+−-])\s*0\.[0-2]\d?\s*kg', allt): f.add('review', f'tiny change worded as movement: …{allt[max(0, m.start() - 40):m.end() + 40]}…')
    json.dump(dict(out=out, findings=[list(x) for x in f]), open(f'/tmp/claude-0/crawl/p363_{T}.json', 'w'), indent=1)
bugs = [x for x in f if x[0] in ('BUG', 'JS-exception')]
print('findings:', len(f), 'bugs:', len(bugs)); sys.exit(1 if bugs else 0)
