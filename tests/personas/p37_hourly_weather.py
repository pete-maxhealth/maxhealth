"""Persona 37: hour-by-hour weather strip (06-22) and the best window for outdoor exercise; user override shifts the window."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
F = [18]*6 + [20,22,24,26,28,30,32,33,33,32,30,28,26,24,22,21,20,19]
assert len(F) == 24
hourly = {'time': [f'2026-10-06T{h:02d}:00' for h in range(24)], 'temperature_2m': [x-2 for x in F], 'apparent_temperature': F,
          'weather_code': [0]*24, 'precipitation_probability': [70 if h == 8 else 0 for h in range(24)], 'uv_index': [max(0, 8-abs(h-13)*1.3) for h in range(24)]}
hourly['weather_code'][8] = 61
body = {'current': {'temperature_2m': 30, 'apparent_temperature': 32, 'weather_code': 0},
        'daily': {'apparent_temperature_max': [33], 'temperature_2m_max': [31], 'temperature_2m_min': [16], 'uv_index_max': [8], 'precipitation_probability_max': [70]}, 'hourly': hourly}
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def route(r):
        u = r.request.url
        if u.startswith('http://localhost'): return r.continue_()
        if 'api.open-meteo.com' in u:
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
    cells = page.evaluate("document.querySelectorAll('#mhWxHours > div').length")
    if cells != 17: f.add('BUG', f'expected 17 hourly cells (06-22), got {cells}')
    t = txt()
    if '18:00-22:00' not in t: f.add('BUG', 'best window not 18:00-22:00: ' + t[:400])
    if page.evaluate("document.querySelectorAll('#mhWxHours > div[style*=\"var(--accent)\"]').length") != 4: f.add('BUG', 'best-window cells not outlined')
    if '70%' not in t: f.add('BUG', 'rain chance for the wet hour not shown')
    # later in the evening only the remaining hours count
    page.evaluate("window.__mhWxHour = 20; mhWxRender()"); page.wait_for_timeout(300)
    if '20:00-22:00' not in txt(): f.add('BUG', 'window did not shrink to remaining hours: ' + txt()[:300])
    # past the last hour: nothing silly
    page.evaluate("window.__mhWxHour = 23; mhWxRender()"); page.wait_for_timeout(300)
    if 'Best time left' in txt(): f.add('BUG', 'offered a best time after 22:00')
    # user says it actually feels 13 degrees cooler: the whole day shifts, so a longer window opens
    page.evaluate("window.__mhWxHour = 5; mhWxOpenOverride()"); page.fill('#mhWxFeels', '20'); page.evaluate("mhWxSaveOverride()"); page.wait_for_timeout(400)
    if '16:00-22:00' not in txt(): f.add('BUG', 'override did not shift the best window: ' + txt()[:400])
    # marked wet: no outdoor window
    page.evaluate("mhWxOpenOverride()"); page.select_option('#mhWxWet', 'wet'); page.evaluate("mhWxSaveOverride()"); page.wait_for_timeout(400)
    if 'marked today wet' not in txt(): f.add('BUG', 'wet override not reflected: ' + txt()[:300])
    # an old cache without hourly data refreshes itself and never crashes
    page.evaluate("mhWxClearOverride(); const c=JSON.parse(localStorage.getItem('mh_wx_cache')); delete c.hr; localStorage.setItem('mh_wx_cache', JSON.stringify(c)); mhWxRender()"); page.wait_for_timeout(300)
    page.evaluate("mhWxRefresh(false)"); page.wait_for_timeout(1500)
    if page.evaluate("document.querySelectorAll('#mhWxHours > div').length") != 17: f.add('BUG', 'cache without hourly data did not refresh')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
