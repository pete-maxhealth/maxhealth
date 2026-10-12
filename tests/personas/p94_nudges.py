"""Persona 94: a gentle, optional nudge offers back a card the starter pack tucked away - only after a week, one at a time, snoozable, dismissible, and never for cards the person hid themselves."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def days_ago(n):
    import datetime; return (datetime.date.today() - datetime.timedelta(days=n)).isoformat()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')"); page.reload(); page.wait_for_timeout(1800)
    page.evaluate("document.querySelectorAll('[id*=nboard]').forEach(e=>{ if(e.style) e.style.display='none'; })")
    ev = page.evaluate
    card = lambda: ev("(()=>{const c=document.getElementById('mhNudgeCard'); return c? c.dataset.key : null})()")
    # no pack layout -> no nudge
    ev("mhNudgeRender()");
    if card(): f.add('BUG', 'nudge shown with no pack layout')
    # simple pack applied today -> still quiet
    ev("mhPackApply(MH_FIRST_RUN_PACKS.simple, ['layout'], 'merge'); mhNudgeRender()")
    if card(): f.add('BUG', 'nudge shown on day one')
    # a week later
    ev(f"localStorage.setItem('mh_layout_base_at','{days_ago(8)}'); mhNudgeRender()")
    if card() != 'macroratio': f.add('BUG', f'expected macroratio nudge, got {card()}')
    # a card the person hid themselves (not in the pack) is never offered: hide fasting-less case via pack lacking it
    ev("mhNudgeAct('later')")
    if card(): f.add('BUG', 'snooze did not hide the nudge')
    st = ev("mhNudgeState()")
    if not st.get('snoozeUntil'): f.add('BUG', 'no snooze date saved')
    # snooze expires
    ev(f"(()=>{{const s=mhNudgeState(); s.snoozeUntil='{days_ago(1)}'; mhNudgeSave(s); mhNudgeRender();}})()")
    if card() != 'macroratio': f.add('BUG', 'nudge did not return after the snooze')
    # show it: unhides, updates base so Default keeps it, next candidate waits a week
    ev("mhNudgeAct('show')")
    r = ev("({hidden: getDashboardHidden(), base: JSON.parse(mhLayoutBase().mh_dashboard_hidden||'[]'), next: (document.getElementById('mhNudgeCard')||{}).dataset})")
    if 'macroratio' in r['hidden'] or 'macroratio' in r['base']: f.add('BUG', f'show it did not unhide / update base {r}')
    if card(): f.add('BUG', 'next nudge came straight away')
    ev(f"(()=>{{const s=mhNudgeState(); s.snoozeUntil='{days_ago(1)}'; mhNudgeSave(s); mhNudgeRender();}})()")
    if card() != 'goalcheck': f.add('BUG', f'expected goalcheck next, got {card()}')
    # never
    ev("mhNudgeAct('never'); mhNudgeRender()")
    ev(f"(()=>{{const s=mhNudgeState(); s.snoozeUntil='{days_ago(1)}'; mhNudgeSave(s); mhNudgeRender();}})()")
    if card(): f.add('BUG', "nudge came back after 'Don't ask again'")
    # folded kind (brain pack)
    ev("localStorage.removeItem('mh_nudge_v1'); mhPackApply(MH_FIRST_RUN_PACKS.brain, ['layout'], 'replace'); mhDcApply()")
    ev(f"localStorage.setItem('mh_layout_base_at','{days_ago(9)}'); mhNudgeRender()")
    if card() not in ('macroratio', 'goalcheck', 'daymode', 'fasting'): f.add('BUG', f'folded nudge not offered: {card()}')
    k = card(); ev("mhNudgeAct('show')")
    if ev(f"mhDcGet('{k}')"): f.add('BUG', 'folded card not opened by Show it')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
