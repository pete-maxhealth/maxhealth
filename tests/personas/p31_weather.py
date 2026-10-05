"""Persona 31: local weather - set up by city search, forecast shown, water target rises on a hot day,
user override wins, cached forecast survives going offline, removal clears it."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
state = {'down': False, 'feels': 33.0}
def S(page): return page.evaluate("JSON.parse(localStorage.getItem('maxhealth_v1')||'{}')")
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []; hits = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    def route(r):
        u = r.request.url
        if u.startswith('http://localhost'): return r.continue_()
        if 'geocoding-api.open-meteo.com' in u:
            hits.append(u); return r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'},
                body=json.dumps({'results': [{'name': 'Izmir', 'admin1': 'Izmir', 'country': 'Turkey', 'latitude': 38.42, 'longitude': 27.14}]}))
        if 'api.open-meteo.com' in u:
            if state['down']: return r.abort()
            hits.append(u); return r.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'},
                body=json.dumps({'current': {'temperature_2m': 30, 'apparent_temperature': 32, 'weather_code': 0},
                  'daily': {'apparent_temperature_max': [state['feels']], 'temperature_2m_max': [31], 'temperature_2m_min': [22], 'uv_index_max': [8], 'precipitation_probability_max': [5]}}))
        r.fulfill(status=200, body='')
    ctx.route(re.compile(r'^https?://'), route)
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/', wait_until='domcontentloaded'); page.wait_for_timeout(800)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    txt = lambda: page.evaluate("document.getElementById('mhWxCard').innerText")
    wt = lambda: page.evaluate("document.getElementById('waterTarget').innerText")
    if 'Add local weather' not in txt(): f.add('BUG', 'no add-weather prompt: ' + txt()[:120])
    base = wt()
    page.evaluate("mhWxOpenSetup()"); page.fill('#mhWxCity', 'Izmir'); page.evaluate("mhWxSearch()"); page.wait_for_timeout(600)
    page.evaluate("mhWxPick(0)"); page.wait_for_timeout(1200)
    t = txt()
    if 'Izmir' not in t or 'high 31' not in t: f.add('BUG', 'forecast not shown: ' + t[:200])
    if 'Hot' not in t and 'hot' not in t: f.add('BUG', 'no hot-day exercise tip: ' + t[:300])
    if 'UV 8' not in t: f.add('BUG', 'UV missing')
    if '+500ml heat' not in wt(): f.add('BUG', 'water target not raised for 33° day: ' + wt())
    # override to a cool day wins
    page.evaluate("mhWxOpenOverride()"); page.fill('#mhWxFeels', '20'); page.evaluate("mhWxSaveOverride()"); page.wait_for_timeout(500)
    if 'heat' in wt(): f.add('BUG', 'override did not remove heat water: ' + wt())
    if 'Using your adjustment' not in txt(): f.add('BUG', 'override not indicated')
    page.evaluate("mhWxClearOverride()"); page.wait_for_timeout(300)
    if '+500ml heat' not in wt(): f.add('BUG', 'back-to-forecast did not restore')
    # offline: service down, refresh keeps the cached forecast
    state['down'] = True
    page.evaluate("mhWxRefresh(true)"); page.wait_for_timeout(1500)
    if 'high 31' not in txt(): f.add('BUG', 'cached forecast lost when offline: ' + txt()[:150])
    # reload keeps location
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(2500)
    if 'Izmir' not in txt(): f.add('BUG', 'location not remembered after reload')
    page.evaluate("mhWxRemove()"); page.wait_for_timeout(300)
    if 'Add local weather' not in txt(): f.add('BUG', 'remove did not clear')
    if 'heat' in wt(): f.add('BUG', 'heat extra stays after removal')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
