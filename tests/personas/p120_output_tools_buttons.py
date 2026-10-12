"""Persona 120: every output area gets Select all + Copy (not on empty/idle ones); copy puts exactly the output text on the clipboard; rectangular buttons share a 12px radius; plan-card buttons never clip their labels at large text."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 320, 'height': 780}, service_workers='block'); ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev = page.evaluate
    ev("document.body.insertAdjacentHTML('beforeend','<div id=\"t1\" class=\"output-box\">Result line one\\nResult line two with data</div><div id=\"t2\" class=\"output-box idle\">No file loaded yet.</div>')")
    page.wait_for_timeout(1200)
    if not ev("!!document.querySelector('#t1 + .mh-outtools')"): f.add('BUG', 'no tools under a filled output')
    if ev("!!document.querySelector('#t2 + .mh-outtools') && document.querySelector('#t2 + .mh-outtools').style.display!=='none'"): f.add('BUG', 'tools shown on an idle placeholder')
    page.click('#t1 + .mh-outtools [data-a=copy]'); page.wait_for_timeout(300)
    if ev("navigator.clipboard.readText()") != 'Result line one\nResult line two with data': f.add('BUG', 'clipboard text wrong: ' + repr(ev("navigator.clipboard.readText()")))
    page.click('#t1 + .mh-outtools [data-a=sel]')
    if 'Result line one' not in ev("String(getSelection())"): f.add('BUG', 'select all did not select the output')
    ev("document.getElementById('t1').textContent='Changed output text here'"); page.wait_for_timeout(900)
    if ev("document.querySelectorAll('#t1 + .mh-outtools').length") != 1: f.add('BUG', 'duplicate bars after update')
    if ev("document.querySelectorAll('.mh-outtools').length") > 3: f.add('BUG', 'bars multiplying')
    # button radii
    for sel in ['.copy-btn', '.run-btn', '.modal-btn', '.btn-neutral']:
        ev(f"document.body.insertAdjacentHTML('beforeend','<button class=\"{sel[1:]}\" id=\"zb\" style=\"border-radius:6px\">x</button>')")
        r = ev("parseFloat(getComputedStyle(document.getElementById('zb')).borderTopLeftRadius)"); ev("document.getElementById('zb').remove()")
        if r < 12: f.add('BUG', f'{sel} radius {r}')
    # plan card at large text
    ev("""(()=>{ const t=new Date(), d=localISODate(t); const p=n=>String(n).padStart(2,'0'); mhPlanSave([{id:'a',text:'Nicks Chocolate Waffles',date:d,time:'00:01',foods:[{name:'w',kcal:165,protein:3.2,carbs:2.7,fat:12.6}]}]); switchTab('today'); mhPlanRender(); })()""")
    page.wait_for_timeout(400)
    ev("document.querySelectorAll('#mhPlanBlock *').forEach(e=>{e.style.fontSize=(parseFloat(getComputedStyle(e).fontSize)*1.6)+'px'})")
    bad = ev("[...document.querySelectorAll('#mhPlanBlock button')].filter(b=>b.scrollWidth>b.clientWidth+1).map(b=>b.textContent.trim())")
    if bad: f.add('BUG', f'plan buttons clip their labels: {bad}')
    if ev("document.documentElement.scrollWidth") > 321: f.add('BUG', 'page wider than screen with plan card')
    if errs: f.add('BUG', f'page errors {errs[:2]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
