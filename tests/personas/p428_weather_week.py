"""Persona 428: "Next 7 days" under the weather card (tucked away, stays as left): feels-like high per day, best stretch or why not, hot and windy days, old cache refreshes."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
import datetime
dates = [(datetime.date(2026,11,8)+datetime.timedelta(days=k)).isoformat() for k in range(8)]
def day_f(k): return 14 if k != 3 else 31          # day 3 is hot
def day_w(k, h): return 30 if k == 2 else (8 if h < 20 else 14)   # day 2 is windy all day
def day_g(k, h): return 45 if k == 2 else 14
hourly = {'time': [f'{dates[k]}T{h:02d}:00' for k in range(8) for h in range(24)],
          'temperature_2m': [day_f(k)-2 for k in range(8) for h in range(24)],
          'apparent_temperature': [day_f(k) for k in range(8) for h in range(24)],
          'weather_code': [0]*192, 'precipitation_probability': [0]*192, 'uv_index': [2]*192,
          'wind_speed_10m': [day_w(k,h) for k in range(8) for h in range(24)], 'wind_gusts_10m': [day_g(k,h) for k in range(8) for h in range(24)]}
seen = []
body = {'current': {'temperature_2m': 14, 'apparent_temperature': 14, 'weather_code': 0},
        'daily': {'time': dates, 'apparent_temperature_max': [day_f(k) for k in range(8)], 'temperature_2m_max': [day_f(k)+1 for k in range(8)], 'temperature_2m_min': [8]*8,
                  'uv_index_max': [3]*8, 'precipitation_probability_max': [0]*8, 'weather_code': [0]*8,
                  'wind_speed_10m_max': [day_w(k,12) for k in range(8)], 'wind_gusts_10m_max': [day_g(k,12) for k in range(8)]}, 'hourly': hourly}
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
    if 'forecast_days=8' not in seen[-1]: f.add('BUG', 'asks for eight days (today + 7)')
    if page.evaluate("!!document.getElementById('mhWxWeek')") is False: f.add('BUG', 'week line exists')
    if page.evaluate("document.querySelectorAll('#mhWxWeek > div').length") != 1: f.add('BUG', 'closed by default: only the one line')
    if 'Next 7 days' not in txt(): f.add('BUG', 'line says Next 7 days')
    page.evaluate("mhWxWeekToggle()"); page.wait_for_timeout(300)
    rows = page.evaluate("[...document.querySelectorAll('#mhWxWeek > div:nth-child(2) > div')].map(d=>d.innerText.replace(/\\s+/g,' '))")
    if len(rows) != 7: f.add('BUG', f'seven rows, got {len(rows)}: {rows}')
    else:
        if 'feels 14°' not in rows[0] or '🟢 06:00-22:00' not in rows[0]: f.add('BUG', 'day 1 calm: feels 14 and a window: ' + rows[0])
        if 'windy' not in rows[1] or '💨45' not in rows[1] or '🟡' not in rows[1]: f.add('BUG', 'day 2 windy: ' + rows[1])
        if 'feels 31°' not in rows[2] or '🟡' not in rows[2]: f.add('BUG', 'day 3 hot, no window: ' + rows[2])
    if not txt().count('Next 7 days'): f.add('BUG', 'still shown open')
    # stays open through re-renders and a reload
    page.evaluate("mhWxRender()"); page.wait_for_timeout(200)
    if page.evaluate("document.querySelectorAll('#mhWxWeek > div:nth-child(2) > div').length") != 7: f.add('BUG', 'stays open after a redraw')
    page.reload(); page.wait_for_timeout(2500)
    if page.evaluate("document.querySelectorAll('#mhWxWeek > div:nth-child(2) > div').length") != 7: f.add('BUG', 'stays open after reload')
    page.evaluate("window.__mhWxHour = 5; mhWxRender()"); page.wait_for_timeout(300)
    if '06:00-22:00' not in txt() and '06:00' not in txt(): f.add('BUG', "today's own window still there: " + txt()[:300])
    page.locator('#mhWxCard').scroll_into_view_if_needed(); page.locator('#mhWxCard').screenshot(path='/tmp/claude-0/p428_week_open.png')
    page.evaluate("mhWxWeekToggle()"); page.wait_for_timeout(300)
    if page.evaluate("document.querySelectorAll('#mhWxWeek > div').length") != 1: f.add('BUG', 'tap again tucks it away')
    page.reload(); page.wait_for_timeout(2500)
    if page.evaluate("document.querySelectorAll('#mhWxWeek > div').length") != 1: f.add('BUG', 'stays shut after reload')
    # a cache from before the week existed refreshes itself
    page.evaluate("const c=JSON.parse(localStorage.getItem('mh_wx_cache')); c.v=2; delete c.days; localStorage.setItem('mh_wx_cache', JSON.stringify(c)); mhWxRender()"); page.wait_for_timeout(300)
    n = len(seen); page.evaluate("mhWxRefresh(false)"); page.wait_for_timeout(1500)
    if len(seen) <= n or not page.evaluate("!!document.getElementById('mhWxWeek')"): f.add('BUG', 'old cache refreshes and brings the week back')
    # offline: no week data, nothing breaks
    page.evaluate("const c=JSON.parse(localStorage.getItem('mh_wx_cache')); delete c.days; localStorage.setItem('mh_wx_cache', JSON.stringify(c)); mhWxRender()")
    if page.evaluate("!!document.getElementById('mhWxWeek')"): f.add('BUG', 'no week line without week data')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
