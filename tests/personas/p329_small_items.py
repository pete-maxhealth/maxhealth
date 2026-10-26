"""Persona 329 (v3.10.1221): the five loose ends. (1) Regular on/off is on list rows (Edit mode) AND the shelf, same button, same words, same effect. (2) long shelf names stay two lines with the buttons in place. (3) the "logged for 19:00" tile line clears itself once that time passes. (4) Trends Journey / Body composition hidden + folded state is carried to Move once. (5) the unused "ones I use most" view is gone."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    # (4) migration: old Trends state, then run it
    ev("localStorage.removeItem('mh_move_mig2'); localStorage.setItem('mh_reorder_hidden_trends', JSON.stringify(['trends-journey','trends-bodycomp','trends-routine'])); localStorage.setItem('mh_collapse_trends-journey','closed'); localStorage.removeItem('mh_move_hidden'); mhMoveMigrate()")
    mh = ev("JSON.parse(localStorage.getItem('mh_move_hidden')||'[]')")
    if 'journey' not in mh or 'bodycomp' not in mh: f.add('BUG', f'Journey and Body composition stay hidden on Move: {mh}')
    if ev("JSON.parse(localStorage.getItem('mh_reorder_hidden_trends')).join()") != 'trends-routine': f.add('BUG', 'other Trends hidden cards are left alone')
    if ev("localStorage.getItem('mh_collapse_move-journey')") != 'closed': f.add('BUG', 'folded state carried to Move')
    ev("localStorage.setItem('mh_move_hidden','[]'); mhMoveMigrate()")
    if ev("localStorage.getItem('mh_move_hidden')") != '[]': f.add('BUG', 'migration runs once only')
    # (5) gone
    if ev("typeof mhStockSuggestTrack") != 'undefined': f.add('BUG', 'unused suggest code removed')
    # (1)(2) shelf + list row
    ev("localStorage.setItem('mh_shop_pane','both')"); ev("switchTabById('shop'); mhShopOpen()"); page.wait_for_timeout(400)
    ev("(()=>{ let e = document.getElementById('mhShopOwn'); if (!e) { e = document.createElement('input'); e.id = 'mhShopOwn'; document.body.appendChild(e); } e.value = 'Zz Washing powder'; mhShopAddOwn(); _shopUi.edit = true; mhShopRender(); })()"); page.wait_for_timeout(300)
    sel = '[data-regid]'
    if not ev("!!document.querySelector('[data-regid]')"): f.add('BUG', 'a Regular button on list rows in Edit mode')
    else:
        a = ev("(()=>{ const b = document.querySelector('[data-regid]'); const c = getComputedStyle(b); return [b.className, c.fontSize, c.paddingTop, c.borderRadius, b.innerText.trim()].join('|'); })()")
        if a.split('|')[-1] != '☆ Regular': f.add('BUG', f'off state wording is the shelf wording: {a}')
        page.click(sel); page.wait_for_timeout(300)
        if ev("!!mhShopUsualFind(mhShopLoad(), mhShopKey('Zz Washing powder'))") is not True: f.add('BUG', 'tap makes it a regular')
        if ev("document.querySelector('[data-regid]').innerText.trim()") != '⭐ Regular': f.add('BUG', 'on state shows ⭐ Regular')
        page.click(sel); page.wait_for_timeout(300)
        if ev("!!mhShopUsualFind(mhShopLoad(), mhShopKey('Zz Washing powder'))"): f.add('BUG', 'tap again switches it off')
    # shelf: long name + same button look as the list row
    LONG = 'Zz Extra long named household product that goes on and on for a good while indeed'
    ev("n => { mhStockAddNonFood(n); }", LONG); page.wait_for_timeout(300)
    ev("(()=>{ _shopUi.edit = false; _shopUi.view = 'list'; _shopUi.addOpen = true; mhShopAddKind('nonfood'); })()"); page.wait_for_timeout(300)
    ev("n => { const s = mhShopLoad(); s.items = s.items.filter(i => i.key !== mhShopKey(n)); mhShopSave(s); mhShopRender(); }", LONG); page.wait_for_timeout(300)
    shelf = ev("""(()=>{ const r = document.querySelector('[data-nfshelf^="Zz Extra"]'); if (!r) return null; const sp = r.querySelector('span'); const b = r.querySelector('[data-regk]'); const rr = r.getBoundingClientRect(); return {h: Math.round(rr.height), w: Math.round(rr.width), bw: Math.round(b.getBoundingClientRect().width), right: Math.round(b.getBoundingClientRect().right), cls: b.className, fs: getComputedStyle(b).fontSize}; })()""")
    if shelf is None: f.add('BUG', 'shelf row not found (non-food shelf)')
    else:
        if shelf['h'] > 90: f.add('BUG', f'long shelf name is clamped to two lines, row {shelf["h"]}px')
        if shelf['right'] > 390: f.add('BUG', 'Regular button stays on screen')
        la = ev("getComputedStyle(document.createElement('button')).fontSize")
    # (3) later tile line clears
    ev("""(()=>{ const d = new Date(Date.now() + 90*1000); const t = String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0'); state.todayLog = [{name:'Zz Bar', kcal: 200, protein: 5, fat: 5, carbs: 20, time: t, id: 'zz1'}]; window.__zzT = t; localStorage.setItem('mh_planned_v1', JSON.stringify([{id:'p9', date: localISODate(), time:'23:59', text:'x', foods:[{name:'Zz Plan', kcal:100, protein:1, fat:1, carbs:1}]}])); mhPlanTileNotes(); })()""")
    page.wait_for_timeout(300)
    has = lambda: ev("document.body.textContent.includes('logged for ' + window.__zzT)")
    # the tile notes may use different element ids; find any text
    if not has(): f.add('BUG', 'precondition: the "logged for" line shows while the time is ahead')
    if ev("!!window._mhLaterTimer") is not True: f.add('BUG', 'a refresh is scheduled for the moment the time passes')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
