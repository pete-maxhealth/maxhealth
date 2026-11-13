"""Persona 404: click every control on the recently changed flows and on their neighbours, two levels deep (6 Nov 2026).
Pete: "the full click everything on the app for the new stuff and its neighbours". Unlike p362 (one click per control on every top-level screen,
skips anything behind a state), this builds each flow's state first (import review with many lines, after a partial add, two rounds of suggestion
cards, shopping list, My cupboards, the Log search panel opened from an import line) and clicks every visible control in it, then every control
that its click opened.
After every click it checks: no page error, no NaN / undefined / [object Object] in visible text, no duplicate element ids (the v3.10.1299 bug:
two suggestion cards both called combo-card-0), every mh_ storage key that holds JSON still parses, and the shopping list / stock / library
did not silently lose items unless the control was a remove/clear one. Destructive controls (delete / clear / reset / erase ...) ARE clicked, but only inside the demo persona (Pete, 6 Nov), with the app's own confirm answered yes; outside demo they are skipped.
Also: a section must not open/shut by itself when something else is done (collapse), and any full-screen panel a click opens must have a way out (navigation).
Takes 15-25 minutes for all scenarios (every click rebuilds its flow from scratch); it is not hung while it prints progress.
Usage: python3 p404_click_new_flows.py [scenario ...]   (no argument = all). Invented data only.
Findings are for review; a duplicate id or a JS error is always a bug."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SKIP = re.compile(r'delete|remove all|reset|erase|wipe|clear all|sign out|log ?out|restore|replace|factory|forget|uninstall|stop sharing|revoke|remove everything|empty', re.I)
REMOVES = re.compile(r'remove|clear|×|✕|delete|skip|discard|dismiss|undo', re.I)
from flows import *

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

# Stay-put (Pete 9 Nov 2026: removing a cupboard food brought up the Next meal idea picker): a control that is not a navigator must leave you on the same screen.
SCREEN = "[...document.querySelectorAll('[id^=maintab-].active,[id^=logtab-].active,[id^=shoptab-].active')].map(e=>e.id).join(',') + '|' + (document.querySelector('.mh-mealpicker-live') ? 'picker' : '')"
GOES = re.compile(r'idea|suggest|meal|log|today|insights|settings|history|library|shopping|back|open|go to|view|show|edit|add|import|search|barcode|scan|photo|recipe|plan|share|help|tour|switchTab|nav|startNext|mhUseUpIdea|mhSoonGo|mhShopView|mhShopOpen|Fold|Tab|Pane', re.I)
ALL = ['import_review', 'import_after_partial_add', 'suggestion_cards', 'shopping_list', 'my_cupboards', 'log_search_from_import', 'compare_metrics_foods']
want = sys.argv[1:] or ALL; clicked = 0; skipped = 0; destructive = 0
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page()
    page.on('pageerror', lambda e: f.add('JS-exception', str(e)[:200])); page.on('dialog', lambda d: d.dismiss())
    ev = page.evaluate
    for name in want:
        setup(page, name); first = ev(SCAN); n1 = 0
        print(f'{name}: {len(first)} controls')
        for it in first[:45]:
            label = it['t'] or it['oc']
            if n1 and n1 % 10 == 0: print(f'  {name}: {n1} of {min(len(first),45)} clicked', flush=True)   # each click rebuilds the flow (about 5 s), so a scenario takes minutes: show it is alive
            dest = bool(SKIP.search(it['t'] + ' ' + it['oc']))
            setup(page, name)
            if dest and not ev("typeof _demoMode !== 'undefined' && !!_demoMode"): skipped += 1; continue   # destructive controls only ever run inside the demo persona
            cur = ev(SCAN)
            m = [c for c in cur if c['t'] == it['t'] and c['oc'] == it['oc']]
            if not m: continue
            before = ev(COUNTS); rm = dest or bool(REMOVES.search(it['t'] + ' ' + it['oc'])); fold0 = ev(FOLD); ov0 = ev(OVERLAYS); scr0 = ev(SCREEN)
            if dest: ev("window.appConfirm = (m, ok) => { ok && ok(); }"); destructive += 1   # say yes to the app's own confirm
            sig_before = {(c['t'], c['oc']) for c in cur}
            ev(f"(() => {{ const e = document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn, input[type=checkbox], select')[{m[0]['i']}]; if (e) e.click(); }})()")
            page.wait_for_timeout(250); clicked += 1; n1 += 1
            check(page, f'{name} > {label}', before, rm)
            if rm and not GOES.search(it['t'] + ' ' + it['oc']) and ev(SCREEN) != scr0: f.add('stay-put', f'{name} > {label}: a remove/clear control moved you to another screen or opened the meal-idea picker ({scr0} -> {ev(SCREEN)})')
            if ev(FOLD) != fold0 and not TOGGLE.search(it['t'] + ' ' + it['oc']) and 'mhShopBackArrow' not in it['oc']: f.add('collapse', f'{name} > {label}: a section opened or shut by itself (Pete 4 Nov: adding or editing must not open or reset sections)')
            if ev(OVERLAYS) > ov0:
                if not ev(CLOSER): page.keyboard.press('Escape')
                page.wait_for_timeout(250)
                if ev(OVERLAYS) > ov0: ev("()=>{const o=[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e);const r=e.getBoundingClientRect();return s.position==='fixed'&&r.width>innerWidth*.6&&r.height>innerHeight*.4&&s.display!=='none'}).pop(); if(o){const b=[...o.querySelectorAll('button,[onclick]')].find(e=>/close|dismiss|hide|cancel/i.test((e.getAttribute('onclick')||'')+(e.getAttribute('aria-label')||'')+(e.innerText||'')+(e.title||''))); (b||o).click();}}"); page.wait_for_timeout(250)   # tap-to-dismiss panels and x buttons count as a way out
                if ev(OVERLAYS) > ov0: f.add('navigation', f'{name} > {label}: opened a full-screen panel that has no visible close/back and does not close on Escape')
            # second level: controls that appeared because of that click
            new = [c for c in ev(SCAN) if (c['t'], c['oc']) not in sig_before][:8]
            for c2 in new:
                l2 = c2['t'] or c2['oc']
                d2 = bool(SKIP.search(c2['t'] + ' ' + c2['oc']))
                if d2 and not ev("typeof _demoMode !== 'undefined' && !!_demoMode"): skipped += 1; continue
                b2 = ev(COUNTS); rm2 = rm or d2 or bool(REMOVES.search(c2['t'] + ' ' + c2['oc']))
                if d2: ev("window.appConfirm = (m, ok) => { ok && ok(); }"); destructive += 1
                ev(f"(() => {{ const all = [...document.querySelectorAll('button, [onclick], summary, [role=button], .tab-btn, input[type=checkbox], select')]; const e = all.find(x => ((x.innerText || x.getAttribute('aria-label') || x.title || x.value || '') + '').trim().slice(0, 50) === {json.dumps(c2['t'])} && (x.getAttribute('onclick') || '').slice(0, 80) === {json.dumps(c2['oc'])}); if (e) e.click(); }})()")
                page.wait_for_timeout(200); clicked += 1
                check(page, f'{name} > {label} > {l2}', b2, rm2)
        print(f'  clicked {n1} first-level controls')
print(f'clicked {clicked} controls ({destructive} of them destructive, run inside the demo persona), skipped {skipped}')
seen = set(); uniq = []
for x in f:
    if x[1] not in seen: seen.add(x[1]); uniq.append(x)
print('findings', len(uniq)); [print(x) for x in uniq[:60]]
sys.exit(1 if uniq else 0)
