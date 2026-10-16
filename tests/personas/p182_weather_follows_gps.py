"""Persona 182 (v3.10.1080): a weather location set from GPS follows the phone when it moves."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad=[]
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ')+n+(f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
with fresh_server() as root, sync_playwright() as pw:
    br=pw.chromium.launch(); ctx=br.new_context(viewport={'width':430,'height':900},service_workers='block',geolocation={'latitude':51.51,'longitude':-0.13},permissions=['geolocation']); page=ctx.new_page()
    errs=[]; page.on('pageerror',lambda e:errs.append(str(e)[:200])); page.on('dialog',lambda d:d.dismiss())
    page.route(re.compile(r'^https?://(?!localhost)'),lambda r:r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); page.evaluate("state.onboarded=true; saveState()"); page.reload(); page.wait_for_timeout(1500)
    ev=page.evaluate
    ev("mhWxUseGPS()"); page.wait_for_timeout(1500)
    loc=ev("JSON.parse(localStorage.getItem('mh_wx_loc'))")
    check('GPS location saved and flagged', loc and loc['lat']==51.51 and loc.get('gps'), str(loc))
    ctx.set_geolocation({'latitude':53.48,'longitude':-2.24})
    ev("mhWxRefresh(true)"); page.wait_for_timeout(2500)
    loc=ev("JSON.parse(localStorage.getItem('mh_wx_loc'))")
    check('Refresh follows the phone to the new place', loc['lat']==53.48 and loc['lon']==-2.24, str(loc))
    ctx.set_geolocation({'latitude':53.481,'longitude':-2.241})
    ev("mhWxRefresh(true)"); page.wait_for_timeout(1500)
    check('a tiny move does not reset the cache', ev("JSON.parse(localStorage.getItem('mh_wx_loc')).lat")==53.48)
    ev("localStorage.setItem('mh_wx_loc',JSON.stringify({lat:10,lon:10,name:'Somewhere'}))"); ctx.set_geolocation({'latitude':40,'longitude':40})
    ev("mhWxRefresh(true)"); page.wait_for_timeout(1500)
    check('a place you typed is never overridden by GPS', ev("JSON.parse(localStorage.getItem('mh_wx_loc')).lat")==10)
    check('no JS errors', not errs, str(errs[:2]))
print('p182:', 'ALL PASS' if not bad else f'{len(bad)} FAIL: {bad}'); sys.exit(1 if bad else 0)
