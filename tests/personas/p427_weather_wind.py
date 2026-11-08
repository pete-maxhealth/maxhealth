"""Persona 427: the best time for outdoor exercise also avoids strong wind and gusts (mph), not just heat, rain and UV; windy hours are marked; a cache from before wind existed refreshes."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
F = [14]*24
assert len(F) == 24
hourly = {'time': [f'2026-10-06T{h:02d}:00' for h in range(24)], 'temperature_2m': [x-2 for x in F], 'apparent_temperature': F,
          'weather_code': [0]*24, 'precipitation_probability': [0]*24, 'uv_index': [2]*24,
          'wind_speed_10m': [30 if h < 12 else (8 if h < 18 else 14) for h in range(24)], 'wind_gusts_10m': [45 if h < 12 else (14 if h < 18 else 40) for h in range(24)]}
seen = []
body = {'current': {'temperature_2m': 30, 'apparent_temperature': 32, 'weather_code': 0},
        'daily': {'apparent_temperature_max': [33], 'temperature_2m_max': [31], 'temperature_2m_min': [16], 'uv_index_max': [8], 'precipitation_probability_max': [70]}, 'hourly': hourly}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def route(r):
        u = r.request.url
        if u.startswith('http://localhost'): return r.continue_()
        if 'api.open-meteo.com' in u:
            seen.append(u)
            return r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps(body))
        r.abort()
    ctx.route(re.compile(r'^https?://'), route)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    page.evaluate("window.__mhWxHour = 5; localStorage.setItem('mh_wx_loc', JSON.stringify({lat:38.42,lon:27.14,name:'Izmir'}))")
    page.evaluate("mhWxRefresh(true)"); page.wait_for_timeout(1500)
    txt = lambda: page.evaluate("document.getElementById('mhWxCard').innerText")
    if not seen or 'wind_gusts_10m' not in seen[-1] or 'wind_speed_unit=mph' not in seen[-1]: f.add('BUG', 'forecast asks for wind speed and gusts in mph')
    t = txt()
    if '12:00-18:00' not in t: f.add('BUG', 'best window is the calm stretch 12:00-18:00: ' + t[:400])
    if 'wind up to 8 mph' not in t: f.add('BUG', 'best window says how windy it is: ' + t[:400])
    if page.evaluate("document.querySelectorAll('#mhWxHours > div[style*=\"var(--accent)\"]').length") != 6: f.add('BUG', 'six calm hours outlined')
    if '💨' not in page.evaluate("document.getElementById('mhWxHours').innerText"): f.add('BUG', 'windy hours carry a wind marker')
    if '💨' in page.evaluate("[...document.querySelectorAll('#mhWxHours > div')].filter(d=>d.firstChild.textContent==='14')[0].innerText"): f.add('BUG', 'a calm hour is not marked windy')
    # after 18:00 the evening gusts rule it out
    page.evaluate("window.__mhWxHour = 18; mhWxRender()"); page.wait_for_timeout(300)
    t = txt()
    if 'Best time left' in t or 'windy' not in t: f.add('BUG', 'only gusty hours left: no window, and it says wind is why: ' + t[:400])
    # the user's own "dry" does not hide the wind
    page.evaluate("window.__mhWxHour = 5; mhWxOpenOverride()"); page.select_option('#mhWxWet', 'dry'); page.evaluate("mhWxSaveOverride()"); page.wait_for_timeout(300)
    if '12:00-18:00' not in txt(): f.add('BUG', 'dry override keeps the wind rule: ' + txt()[:300])
    page.evaluate("mhWxClearOverride()")
    # a cache from before wind existed refreshes itself
    page.evaluate("const c=JSON.parse(localStorage.getItem('mh_wx_cache')); delete c.v; c.hr.forEach(x=>{delete x.w; delete x.g}); localStorage.setItem('mh_wx_cache', JSON.stringify(c)); mhWxRender()"); page.wait_for_timeout(300)
    n = len(seen); page.evaluate("mhWxRefresh(false)"); page.wait_for_timeout(1500)
    if len(seen) <= n: f.add('BUG', 'an old cache without wind is refreshed')
    if '12:00-18:00' not in txt(): f.add('BUG', 'back to the wind-aware window after the refresh')
    page.evaluate("window.__mhWxHour = 5; mhWxRender()"); page.locator('#mhWxCard').scroll_into_view_if_needed(); page.locator('#mhWxCard').screenshot(path='/tmp/claude-0/p427_wind.png')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
