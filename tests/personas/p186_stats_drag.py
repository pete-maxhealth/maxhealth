"""Persona 186 (v3.10.1083): drag a statistic card by its handle to reorder; light theme renders the Statistics tab, sleep and exercise reports."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad=[]
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ')+n+(f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':2400},service_workers='block',has_touch=False); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.accept())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev=page.evaluate
    ev("switchTabById('stats')"); ev("mhStatsOpen()"); page.wait_for_timeout(300)
    ids=ev("mhStatLoad().map(x=>x.id)")
    check('every card has a drag handle', ev("document.querySelectorAll('.mh-stdrag').length")==len(ids))
    ev("mhStatMoveTo('%s','%s',true)"%(ids[0],ids[-1]))
    now=ev("mhStatLoad().map(x=>x.id)")
    check('moveTo puts the first card after the last', now[-1]==ids[0] and len(now)==len(ids))
    before=ev("mhStatLoad().map(x=>x.id)")
    # real pointer drag: last card's handle onto the first card's top half
    first=ev("mhStatLoad()[0].id"); last=ev("mhStatLoad().slice(-1)[0].id")
    ev("document.getElementById('stcard-%s').scrollIntoView({block:'center'})"%last); page.wait_for_timeout(300)
    hb=page.locator('#stcard-%s .mh-stdrag'%last).bounding_box()
    page.evaluate("document.getElementById('stcard-%s').scrollIntoView({block:'start'})"%first); page.wait_for_timeout(200)
    page.evaluate("document.getElementById('stcard-%s').scrollIntoView({block:'start'})"%last); page.wait_for_timeout(200)
    hb=page.locator('#stcard-%s .mh-stdrag'%last).bounding_box()
    first_b=page.locator('#stcard-%s'%before[0]).bounding_box()
    page.mouse.move(hb['x']+5,hb['y']+5); page.mouse.down()
    page.mouse.move(hb['x']+40,first_b['y']+8,steps=8)
    page.mouse.up(); page.wait_for_timeout(300)
    after=ev("mhStatLoad().map(x=>x.id)")
    check('pointer drag actually reorders', after.index(last)<before.index(last), str(before)+str(after))
    check('pointer drag runs without errors and keeps all cards', ev("mhStatLoad().length")==len(ids) and not errs, str(errs[:2]))
    # light theme
    ev("document.documentElement.setAttribute('data-theme','light'); document.body.classList.add('light')")
    ev("mhStatsOpen()"); page.wait_for_timeout(300)
    cols=ev("(()=>{const c=document.querySelector('#statsList .metric-card'); const cs=getComputedStyle(c); return [cs.backgroundColor, getComputedStyle(c.querySelector('div div')).color]})()")
    check('light theme: card text differs from card background', cols[0]!=cols[1], str(cols))
    check('no JS errors', not errs, str(errs[:2]))
print('p186: ALL PASS' if not bad else 'p186 FAILED: '+', '.join(bad))
