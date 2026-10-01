"""Persona 14: supplements, routines, strength log, themes and settings - used and then restored after a
browser wipe, with every theme and every settings control exercised."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
U = 'http://localhost:5757'
f = Findings()
chk = lambda ok, msg: None if ok else f.add('BUG', msg)
VISIBLE = """() => { const out=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(w.nextNode()){const n=w.currentNode; const el=n.parentElement; if(!el||el.closest('script,style')) continue;
    let hidden=false; for(let p=el;p;p=p.parentElement){ const cs=getComputedStyle(p); if(cs.display==='none'||cs.visibility==='hidden'){hidden=true;break;} }
    if(hidden) continue; const t=n.textContent.trim(); if(t.length>1) out.push(t);} return out.join('\\n'); }"""
# worst text-vs-background contrast among visible text, in the current theme
CONTRAST = """() => {
  const lum = c => { const m = c.match(/[\\d.]+/g).map(Number); const a = m.length > 3 ? m[3] : 1; const f = v => { v/=255; return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }; return {L:0.2126*f(m[0])+0.7152*f(m[1])+0.0722*f(m[2]), a}; };
  const rgba = c => { const m = c.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m.length > 3 ? m[3] : 1 }; };
  const lumRGB = (r, g, b) => { const f = v => { v/=255; return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }; return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b); };
  const bgOf = el => { const layers = []; for (let p = el; p; p = p.parentElement) { const c = rgba(getComputedStyle(p).backgroundColor); if (c.a > 0) layers.push(c); if (c.a >= 1) break; }
    let base = layers.length && layers[layers.length-1].a >= 1 ? null : rgba(getComputedStyle(document.documentElement).backgroundColor); if (!base || base.a < 1) base = base && base.a > 0 ? base : { r: 255, g: 255, b: 255, a: 1 };
    let cur = { r: base.r, g: base.g, b: base.b };
    for (let i = layers.length - 1; i >= 0; i--) { const l = layers[i]; cur = { r: l.r * l.a + cur.r * (1 - l.a), g: l.g * l.a + cur.g * (1 - l.a), b: l.b * l.a + cur.b * (1 - l.a) }; }
    return lumRGB(cur.r, cur.g, cur.b); };
  const bad = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode; const el = n.parentElement; if (!el || el.closest('script,style') || n.textContent.trim().length < 3) continue;
    const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    let hid = false; for (let p = el; p; p = p.parentElement) { const cs = getComputedStyle(p); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) { hid = true; break; } } if (hid) continue;
    const fg = lum(getComputedStyle(el).color), bg = bgOf(el); const hi = Math.max(fg.L, bg), lo = Math.min(fg.L, bg); const ratio = (hi + 0.05) / (lo + 0.05);
    if (ratio < 1.8) bad.push(n.textContent.trim().slice(0, 30)); }
  return bad.slice(0, 5); }"""
def boot(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U + '/'); pg.wait_for_timeout(1500); return pg, errs
def onboard(pg, cond='general'):
    pg.evaluate("onboardNext(2)"); pg.fill('#onboardName', 'Test'); pg.evaluate("onboardNext(3)")
    pg.evaluate("obSetSex('female')"); pg.fill('#onboardAge', '45'); pg.fill('#onboardHeight', '168')
    pg.fill('#onboardWeight', '70'); pg.fill('#onboardTarget', '65')
    pg.evaluate("onboardNext(4)"); pg.evaluate("obSetActivity('light')"); pg.evaluate("obSetGoal('lose')")
    pg.evaluate("onboardNext(5)"); pg.evaluate(f"obSetCondition('{cond}')")
    pg.evaluate("onboardNext(6)"); pg.evaluate("onboardFinish()"); pg.wait_for_timeout(1500)
def tap(pg, tab, sub=None):
    pg.click(f"[onclick^=\"switchTab('{tab}'\"]")
    if sub: pg.click(f"[onclick^=\"switchSubTab('{tab}','{sub}'\"]")
    pg.wait_for_timeout(500)
BAD = re.compile(r'\b(NaN|undefined|Infinity|\[object Object\])\b')

with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); pg, errs = boot(b); onboard(pg)
    # ---- A. themes: every base theme x every visual theme must render legibly, no errors
    tap(pg, 'today')
    worst = {}
    for base in ('midnight', 'aurora', 'carbon', 'slate', 'light'):
        for vis in ('none', 'vital', 'pulse', 'forge'):
            try:
                pg.evaluate(f"applyTheme('{base}')"); pg.evaluate(f"setVisualTheme('{vis}')"); pg.wait_for_timeout(600)
                bad = pg.evaluate(CONTRAST); txt = pg.evaluate(VISIBLE)
                if bad: worst[f'{base}/{vis}'] = bad
                if BAD.search(txt): f.add('BUG', f'theme {base}/{vis}: NaN/undefined visible')
            except Exception as e: f.add('BUG', f'theme {base}/{vis} threw: {str(e)[:100]}')
    for k, v in worst.items(): f.add('BUG', f'unreadable text (contrast < 1.8:1) in theme {k}: {v}')
    pg.evaluate("applyTheme('midnight')"); pg.evaluate("setVisualTheme('none')")

    # ---- B. supplements: add through the real modal, take, edit, delete, survive a wipe
    names = [('Vitamin D3', '2000 IU', '1', ['morning']), ('Fish oil | omega-3', '1000mg', '2', ['morning', 'evening']), ('Magnesium', '300mg', '', ['evening'])]
    for nm, dose, tabs, periods in names:
        pg.evaluate(f"addSupplement('{periods[0]}')"); pg.wait_for_timeout(200)
        pg.fill('#suppEditName', nm); pg.fill('#suppEditDose', dose)
        pg.evaluate("(p) => { document.getElementById('suppEditPeriod').value = JSON.stringify(p) }", periods)
        if tabs and pg.query_selector('#suppEditTablets'): pg.fill('#suppEditTablets', tabs)
        pg.evaluate("saveSupplementEdit()"); pg.wait_for_timeout(250)
    defs = pg.evaluate("loadSupplementDefs()")
    chk(len(defs) == 3, f'expected 3 supplements, have {len(defs)}')
    d0 = defs[0]['id']
    pg.evaluate(f"toggleSupplement('{d0}','morning')"); pg.wait_for_timeout(200)
    chk(pg.evaluate("loadSupplementLog()")[d0 + '_morning'] is True, 'taking a supplement did not record')
    pg.reload(); pg.wait_for_timeout(1500)
    chk(pg.evaluate("loadSupplementLog()").get(d0 + '_morning') is True, 'taken-today state lost on reload')
    pg.evaluate(f"editSupplement('{defs[2]['id']}')"); pg.wait_for_timeout(200); pg.fill('#suppEditDose', '400mg'); pg.evaluate("saveSupplementEdit()"); pg.wait_for_timeout(200)
    chk(pg.evaluate("loadSupplementDefs()")[2]['dose'] == '400mg', 'editing a supplement dose did not save')
    pg.evaluate(f"toggleSupplementActive('{defs[2]['id']}')"); pg.wait_for_timeout(200)
    pg.evaluate("renderSupplements()")
    pg.wait_for_timeout(800)
    before = pg.evaluate("loadSupplementDefs()")
    pg2, e2 = boot(b); pg2.evaluate("localStorage.clear()"); pg2.reload(); pg2.wait_for_timeout(2500)
    after = pg2.evaluate("loadSupplementDefs()")
    chk(len(after) == len(before), f'supplements after a wipe: {len(after)} of {len(before)} came back')
    am = {x['name']: x for x in after}
    for x in before:
        y = am.get(x['name'].replace('|', '/'))
        if not y: f.add('BUG', f'supplement lost in server round trip: {x["name"]!r} (have {list(am)})'); continue
        if sorted(x.get('periods') or []) != sorted(y.get('periods') or []): f.add('BUG', f'{x["name"]}: periods {x.get("periods")} -> {y.get("periods")}')
        if x.get('dose') != y.get('dose') or (x.get('active') is False) != (y.get('active') is False): f.add('BUG', f'{x["name"]}: dose/active changed after restore: {x} -> {y}')
    pg.evaluate(f"_doRemoveSupplement('{defs[1]['id']}')"); pg.wait_for_timeout(200)
    chk(len(pg.evaluate("loadSupplementDefs()")) == 2, 'deleting a supplement failed')

    # real flow: tap + Add under a period, type a name, press Save WITHOUT touching the period buttons
    pg.evaluate("addSupplement('midday')"); pg.wait_for_timeout(200); pg.fill('#suppEditName', 'Zinc'); pg.evaluate("saveSupplementEdit()"); pg.wait_for_timeout(300)
    z = [x for x in pg.evaluate("loadSupplementDefs()") if x['name'] == 'Zinc']
    chk(z and z[0]['periods'] == ['midday'], f'a supplement added under Midday and saved without touching the period buttons got periods {z[0]["periods"] if z else None}')
    pg.evaluate("editSupplement('%s')" % (z[0]['id'] if z else '')); pg.wait_for_timeout(200); pg.evaluate("saveSupplementEdit()"); pg.wait_for_timeout(200)
    z2 = [x for x in pg.evaluate("loadSupplementDefs()") if x['name'] == 'Zinc']
    chk(z2 and z2[0]['periods'] == ['midday'], f'opening Edit and pressing Save changed periods to {z2[0]["periods"] if z2 else None}')
    pg.evaluate("_doRemoveSupplement('%s')" % (z[0]['id'] if z else ''))
    # ---- C. routines + strength log restore after a wipe
    routines = [dict(id='r1', name='Push day', exercises=[dict(name='Bench press', sets=[dict(reps=8, weight_kg=60, note='slow')]), dict(name='Dips | weighted', sets=[dict(reps=10, weight_kg=10, note='')])]),
                dict(id='r2', name='Legs, glutes & core', exercises=[dict(name='Squat', sets=[dict(reps=5, weight_kg=80, note='')])])]
    pg.evaluate("(r) => saveRoutines(r)", routines)
    pg.evaluate("""() => { state.strengthLog = [{date: todayStr(), exercise: 'Bench press', sets: [{reps: 8, weight_kg: 60, note: ''}, {reps: 6, weight_kg: 62.5, note: 'felt heavy'}]}]; saveState(); }""")
    pg.wait_for_timeout(1200)
    pg3, e3 = boot(b); pg3.evaluate("localStorage.clear()"); pg3.reload(); pg3.wait_for_timeout(3000)
    onboard(pg3)
    r_after = pg3.evaluate("loadRoutines()")
    chk(len(r_after) == 2, f'routines after a wipe: {len(r_after)} of 2')
    sl = pg3.evaluate("(state.strengthLog || [])")
    chk(len(sl) == 1 and len(sl[0]['sets']) == 2 and sl[0]['sets'][1]['weight_kg'] == 62.5, f'strength log after a wipe: {sl}')
    if len(r_after) == 2:
        ex = [e['name'] for r in r_after for e in r['exercises']]
        chk(any('Dips' in e for e in ex), f'exercise with "|" lost from routine: {ex}')
        chk(any(r['name'].startswith('Legs, glutes') for r in r_after), f'routine name with comma changed: {[r["name"] for r in r_after]}')
    # the Routines screen itself opens
    try:
        tap(pg3, 'log'); pg3.evaluate("showRoutineList()"); pg3.wait_for_timeout(300); chk(not BAD.search(pg3.evaluate(VISIBLE)), 'NaN on routines list')
    except Exception as e: f.add('BUG', f'routine list threw: {str(e)[:100]}')

    # ---- D. settings: poke every select and checkbox on the Settings screens
    pg4, e4 = boot(b); onboard(pg4, 'gbm')
    for sub in ('customise', 'import', 'manage'):
        try: tap(pg4, 'settings', sub)
        except Exception as e: f.add('BUG', f'settings/{sub} not tappable'); continue
        sel = pg4.evaluate("""() => [...document.querySelectorAll('#maintab-content-settings select, [id^="settings"] select, select')].filter(s => s.offsetParent !== null && !s.disabled).map(s => s.id || s.name || '')""")
        for sid in [x for x in sel if x][:25]:
            opts = pg4.evaluate("(id) => [...document.getElementById(id).options].map(o => o.value)", sid)
            for v in opts[:6]:
                try: pg4.evaluate("(a) => { const s = document.getElementById(a[0]); s.value = a[1]; s.dispatchEvent(new Event('change', {bubbles:true})); }", [sid, v])
                except Exception as e: f.add('BUG', f'select #{sid}={v}: {str(e)[:80]}')
        chk_ids = pg4.evaluate("""() => [...document.querySelectorAll('input[type=checkbox]')].filter(c => c.offsetParent !== null && !c.disabled && c.id).map(c => c.id)""")
        for cid in chk_ids[:30]:
            try:
                pg4.evaluate("(id) => { const c = document.getElementById(id); c.checked = !c.checked; c.dispatchEvent(new Event('change', {bubbles:true})); c.dispatchEvent(new Event('click', {bubbles:true})); }", cid)
                pg4.evaluate("(id) => { const c = document.getElementById(id); c.checked = !c.checked; c.dispatchEvent(new Event('change', {bubbles:true})); }", cid)
            except Exception as e: f.add('BUG', f'checkbox #{cid}: {str(e)[:80]}')
        pg4.wait_for_timeout(300)
        if BAD.search(pg4.evaluate(VISIBLE)): f.add('BUG', f'settings/{sub}: NaN/undefined visible after poking controls')
        print(f'   settings/{sub}: {len(sel)} selects, {len(chk_ids)} checkboxes poked')
    pg4.reload(); pg4.wait_for_timeout(1500)
    chk(pg4.evaluate("document.body.innerText.length") > 200, 'app blank after settings were changed and reloaded')
    allerr = errs + e2 + e3 + e4
    chk(not allerr, f'JS errors: {allerr[:4]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
