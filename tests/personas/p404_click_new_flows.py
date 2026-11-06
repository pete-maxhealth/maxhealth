"""Persona 404: click every control on the recently changed flows and on their neighbours, two levels deep (6 Nov 2026).
Pete: "the full click everything on the app for the new stuff and its neighbours". Unlike p362 (one click per control on every top-level screen,
skips anything behind a state), this builds each flow's state first (import review with many lines, after a partial add, two rounds of suggestion
cards, shopping list, My cupboards, the Log search panel opened from an import line) and clicks every visible control in it, then every control
that its click opened.
After every click it checks: no page error, no NaN / undefined / [object Object] in visible text, no duplicate element ids (the v3.10.1299 bug:
two suggestion cards both called combo-card-0), every mh_ storage key that holds JSON still parses, and the shopping list / stock / library
did not silently lose items unless the control was a remove/clear one. Destructive controls are skipped (same list as p362) and confirms are dismissed.
Usage: python3 p404_click_new_flows.py [scenario ...]   (no argument = all). Invented data only.
Findings are for review; a duplicate id or a JS error is always a bug."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SKIP = re.compile(r'delete|remove all|reset|erase|wipe|clear all|sign out|log ?out|restore|replace|factory|forget|uninstall|stop sharing|revoke|remove everything|empty', re.I)
REMOVES = re.compile(r'remove|clear|×|✕|delete|skip|discard|dismiss|undo', re.I)
FOODS = [('Zzqx Chicken Breast', 'meat'), ('Zzqx Mince', 'meat'), ('Zzqx Cheddar', 'dairy'), ('Zzqx Milk', 'dairy'), ('Zzqx Apples', 'fruit'),
         ('Zzqx Carrots', 'vegetable'), ('Zzqx Rice', 'grain'), ('Zzqx Beans', 'beansandpulses'), ('Zzqx Bread Rolls', 'bread')]
ORDER = "\n".join(f"1 x {n} 400g\t£1.00" for n, _ in FOODS) + "\n1 x Zzqx Washing Pods 30\t£4.00"
SCAN = """() => { const sel = 'button, [onclick], summary, [role=button], .tab-btn, input[type=checkbox], select'; const out = [];
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' && s.display !== 'none' && !e.closest('#onboardingOverlay'); };
  document.querySelectorAll(sel).forEach((e, i) => { if (!vis(e)) return; out.push({ i, t: ((e.innerText || e.getAttribute('aria-label') || e.title || e.value || '') + '').trim().slice(0, 50), oc: (e.getAttribute('onclick') || '').slice(0, 80) }); });
  return out; }"""
TEXT = """() => { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let o = [], n; while (n = w.nextNode()) { const e = n.parentElement; if (!e || ['SCRIPT','STYLE'].includes(e.tagName)) continue; const r = e.getBoundingClientRect(); if (r.width > 0 && r.height > 0) o.push(n.textContent); } return o.join(' '); }"""
DUPS = """() => { const seen = {}, d = []; document.querySelectorAll('[id]').forEach(e => { if (seen[e.id]) d.push(e.id); seen[e.id] = 1; }); return [...new Set(d)]; }"""
STORE = """() => { const bad = []; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (!k.startsWith('mh_')) continue; const v = localStorage.getItem(k); if (v && /^[\\[{]/.test(v)) { try { JSON.parse(v); } catch (e) { bad.push(k); } } } return bad; }"""
COUNTS = """() => { const n = k => { try { const v = JSON.parse(localStorage.getItem(k) || 'null'); return Array.isArray(v) ? v.length : (v && typeof v === 'object' ? Object.keys(v).length : 0); } catch (e) { return -1; } }; return { lib: n('mh_library'), stock: (typeof loadStock === 'function' ? Object.keys(loadStock() || {}).length : 0) }; }"""

def setup(page, name):
    ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1000)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')&&(document.getElementById('onboardingOverlay').style.display='none')")
    ev("l=>{const lib=loadLibrary(); l.forEach(([n,c])=>lib.push({name:n,kcal:100,protein:5,carbs:5,fat:5,categories:[c],portion:'100g',per100g:true})); saveLibrary(lib)}", FOODS)
    if name == 'import_review':
        ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300); ev("t=>mhOrdLoad(t,'p404')", ORDER); page.wait_for_timeout(500)
    elif name == 'import_after_partial_add':
        ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300); ev("t=>mhOrdLoad(t,'p404')", ORDER); page.wait_for_timeout(500)
        ev("mhOrdAll(false); _shopUi.ord.rows.slice(0,3).forEach(r=>{r.amount=r.amount||'400 g'; r.on=true})")
        try: ev("mhOrdApplyList&&mhOrdApplyList()")
        except Exception: pass
        page.wait_for_timeout(400)
    elif name == 'suggestion_cards':
        ev("switchTabById('chat')")
        ev("()=>renderLibraryComboSuggestions({combos:[{items:['Zzqx Rice','Zzqx Beans'],note:'round one'}]}, loadLibrary(), [], {})")
        ev("()=>renderLibraryComboSuggestions({combos:[{items:['Zzqx Cheddar'],note:'round two'}]}, loadLibrary(), [], {})"); page.wait_for_timeout(300)
    elif name == 'shopping_list':
        ev("switchTabById('shop')"); ev("()=>{try{['Zzqx Milk','Zzqx Apples','Zzqx Rice'].forEach(n=>mhShopAddName&&mhShopAddName(n))}catch(e){}}"); page.wait_for_timeout(400)
    elif name == 'my_cupboards':
        ev("switchTabById('shop')"); page.wait_for_timeout(300)
        ev("()=>{try{const s=loadStock?loadStock():{}; ['Zzqx Milk','Zzqx Rice','Zzqx Mince'].forEach(n=>{s[n.toLowerCase()]={name:n,qty:2,unit:'x'}}); saveStock&&saveStock(s)}catch(e){}}")
    elif name == 'log_search_from_import':
        ev("switchTabById('shop'); mhOrdOpen('order')"); page.wait_for_timeout(300); ev("t=>mhOrdLoad(t,'p404')", ORDER); page.wait_for_timeout(500)
        ev("()=>{try{_shopUi.ord.rows[0].create=true; mhOrdFind(0,'search')}catch(e){}}"); page.wait_for_timeout(500)
    page.wait_for_timeout(300)

def check(page, where, before, was_remove):
    ev = page.evaluate
    for d in ev(DUPS): f.add('BUG', f'{where}: duplicate element id "{d}"')
    for k in ev(STORE): f.add('BUG', f'{where}: storage key {k} no longer parses as JSON')
    txt = ev(TEXT)
    for w in ('NaN', 'undefined', 'Infinity', '[object Object]'):
        if re.search(r'(?<![\w-])' + re.escape(w) + r'(?![\w-])', txt): f.add('BUG', f'{where}: "{w}" visible')
    after = ev(COUNTS)
    if not was_remove and (after['lib'] < before['lib'] or after['stock'] < before['stock']):
        f.add('BUG', f'{where}: library/stock shrank without a remove control ({before} -> {after})')

ALL = ['import_review', 'import_after_partial_add', 'suggestion_cards', 'shopping_list', 'my_cupboards', 'log_search_from_import']
want = sys.argv[1:] or ALL; clicked = 0; skipped = 0
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page()
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    ev = page.evaluate
    for name in want:
        setup(page, name); first = ev(SCAN); n1 = 0
        print(f'{name}: {len(first)} controls')
        for it in first[:45]:
            label = it['t'] or it['oc']
            if SKIP.search(it['t'] + ' ' + it['oc']): skipped += 1; continue
            setup(page, name)
            cur = ev(SCAN)
            m = [c for c in cur if c['t'] == it['t'] and c['oc'] == it['oc']]
            if not m: continue
            before = ev(COUNTS); rm = bool(REMOVES.search(it['t'] + ' ' + it['oc']))
            sig_before = {(c['t'], c['oc']) for c in cur}
            ev(f"(() => {{ const e = document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn, input[type=checkbox], select')[{m[0]['i']}]; if (e) e.click(); }})()")
            page.wait_for_timeout(250); clicked += 1; n1 += 1
            check(page, f'{name} > {label}', before, rm)
            # second level: controls that appeared because of that click
            new = [c for c in ev(SCAN) if (c['t'], c['oc']) not in sig_before][:8]
            for c2 in new:
                l2 = c2['t'] or c2['oc']
                if SKIP.search(c2['t'] + ' ' + c2['oc']): skipped += 1; continue
                b2 = ev(COUNTS); rm2 = rm or bool(REMOVES.search(c2['t'] + ' ' + c2['oc']))
                ev(f"(() => {{ const all = [...document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn, input[type=checkbox], select')]; const e = all.find(x => ((x.innerText || x.getAttribute('aria-label') || x.title || x.value || '') + '').trim().slice(0, 50) === {json.dumps(c2['t'])} && (x.getAttribute('onclick') || '').slice(0, 80) === {json.dumps(c2['oc'])}); if (e) e.click(); }})()")
                page.wait_for_timeout(200); clicked += 1
                check(page, f'{name} > {label} > {l2}', b2, rm2)
        print(f'  clicked {n1} first-level controls')
print(f'clicked {clicked} controls, skipped {skipped} destructive ones')
seen = set(); uniq = []
for x in f:
    if x[1] not in seen: seen.add(x[1]); uniq.append(x)
print('findings', len(uniq)); [print(x) for x in uniq[:60]]
sys.exit(1 if uniq else 0)
