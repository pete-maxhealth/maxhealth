"""Persona 443 (v3.10.1344): the weather card's "?" explanation opens at the full width of the card, under the header row, not squeezed into the
narrow title cell beside the show/hide and reorder controls (Pete, 10 Nov screenshot). The "?" and the controls stay on the header row."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p443_%s.png'
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', device_scale_factor=2); errs = []
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("""()=>{localStorage.setItem('mh_wx_loc',JSON.stringify({lat:51.5,lon:-0.1,name:'Your location'}));localStorage.setItem('mh_wx_cache',JSON.stringify({lat:51.5,lon:-0.1,at:Date.now(),date:todayStr(),temp:5,feelsNow:3,code:3,feelsMax:6,hi:8,lo:2,rainPct:10,uv:1,hours:[]}))}""")
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(2500)
    ev("switchTab('today', document.getElementById('maintab-today'))"); page.wait_for_timeout(500)
    ev("document.getElementById('mhWxCard').scrollIntoView({block:'start'})"); page.wait_for_timeout(300)
    ev("[...document.querySelectorAll('#mhWxCard span')].find(s=>s.textContent.trim()==='?').click()"); page.wait_for_timeout(300)
    R = ev("""()=>{const box=document.querySelector('#mhWxCard .mhwx-box').getBoundingClientRect(); const h=document.getElementById('help-wxfactors'); const hr=h.getBoundingClientRect();
      const q=[...document.querySelectorAll('#mhWxCard span')].find(s=>s.textContent.trim()==='?').getBoundingClientRect(); const up=[...document.querySelectorAll('#mhWxCard span')].find(s=>s.textContent==='▲').getBoundingClientRect();
      return {boxW:box.width, helpW:hr.width, shown:getComputedStyle(h).display!=='none', qTop:q.top, upTop:up.top, helpTop:hr.top, qBottom:q.bottom}}""")
    if not R['shown']: f.add('BUG', '1: the ? opens the explanation')
    if R['helpW'] < R['boxW'] * 0.8: f.add('BUG', f'2: the explanation spans the card, not a narrow column: {R}')
    if R['helpTop'] < R['qBottom']: f.add('BUG', f'3: the explanation sits under the header row: {R}')
    if abs(R['qTop'] - R['upTop']) > 40: f.add('BUG', f'4: the ? and the controls stay on the header row: {R}')
    page.screenshot(path=SHOT % 'dark')
    ev("document.documentElement.setAttribute('data-theme','light')"); page.wait_for_timeout(300); page.screenshot(path=SHOT % 'light')
    ev("[...document.querySelectorAll('#mhWxCard span')].find(s=>s.textContent.trim()==='?').click()"); page.wait_for_timeout(200)
    if ev("getComputedStyle(document.getElementById('help-wxfactors')).display") != 'none': f.add('BUG', '5: the ? closes it again')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
