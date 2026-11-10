"""Persona 446 (v3.10.1363): the weather card's default readout is the headline, the hour strip and the green Best time line, nothing else; the text advice, suggested effort, water line, detailed seven days and the explanation sit behind the "?" (Pete, 10 Nov: "like it used to be")."""
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
    page.evaluate("window.__mhWxHour = 12; localStorage.setItem('mh_wx_loc', JSON.stringify({lat:38.42,lon:27.14,name:'Izmir'}))")
    page.evaluate("mhWxRefresh(true)"); page.wait_for_timeout(1500)
    SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p446_%s.png'
    page.evaluate("window.__mhWxHour = 12; mhWxRender()"); page.wait_for_timeout(300)
    page.evaluate("switchTab('today', document.getElementById('maintab-today'))"); page.wait_for_timeout(400)
    ORDER = """()=>{const box=document.querySelector('#mhWxCard .mhwx-box'); const top=e=>e?e.getBoundingClientRect().top:null;
      const strip=document.getElementById('mhWxHours'); const help=document.getElementById('help-wxfactors');
      const best=[...box.querySelectorAll('div')].find(d=>/Best time left|No comfortable window|Nothing suitable/.test(d.textContent)&&d.children.length===0);
      const head=box.firstElementChild; return {head:head.getBoundingClientRect().bottom, strip:top(strip), best:top(best), help:top(help), helpShown:help?getComputedStyle(help).display!=='none':false, stripBottom:strip?strip.getBoundingClientRect().bottom:null}}"""
    R = page.evaluate(ORDER)
    if R['strip'] is None or R['best'] is None: f.add('BUG', f'1: the strip and the Best time line both show by default: {R}')
    else:
        if R['strip'] < R['head'] - 1 or R['strip'] - R['head'] > 40: f.add('BUG', f'2: the strip sits right under the headline: {R}')
        if not (R['best'] >= R['stripBottom'] - 1 and R['best'] - R['stripBottom'] < 40): f.add('BUG', f'3: the Best time line sits right under the strip: {R}')
    T0 = page.evaluate("document.getElementById('mhWxCard').innerText")
    for w in ['Suggested effort', 'Next 7 days', 'What the weather changes', 'Water target +']:
        if w in T0: f.add('BUG', f'8: "{w}" is behind the ?, not in the default readout')
    if 'Best time left' not in T0 or 'Not right? Adjust' not in T0: f.add('BUG', '9: default readout keeps Best time and the Adjust/Refresh links: ' + T0[:300])
    page.evaluate("document.getElementById('mhWxCard').scrollIntoView({block:'start'})"); page.wait_for_timeout(200); page.screenshot(path=SHOT % 'closed')
    page.evaluate("[...document.querySelectorAll('#mhWxCard span')].find(s=>s.textContent.trim()==='?').click()"); page.wait_for_timeout(300)
    R2 = page.evaluate(ORDER)
    if not R2['helpShown']: f.add('BUG', '4: the ? opens the explanation')
    else:
        if R2['help'] < R2['best']: f.add('BUG', f'5: the explanation opens below the strip and the Best time line, not above them: {R2}')
        if abs((R2['strip'] - R2['head']) - (R['strip'] - R['head'])) > 2 or abs((R2['best'] - R2['head']) - (R['best'] - R['head'])) > 2: f.add('BUG', f'6: opening the ? does not move the strip or the Best time line: {R} {R2}')
    T1 = page.evaluate("document.getElementById('mhWxCard').innerText")
    for w in ['Suggested effort', 'Next 7 days', 'What the weather changes', 'Water target +', 'Hot: do outdoor exercise']:
        if w not in T1: f.add('BUG', f'10: the ? opens "{w}"')
    if T1.find('Suggested effort') > T1.find('What the weather changes'): f.add('BUG', '11: advice and effort come before the explanation: ' + T1[:900])
    page.screenshot(path=SHOT % 'open')
    page.evaluate("document.documentElement.setAttribute('data-theme','light')"); page.wait_for_timeout(300); page.screenshot(path=SHOT % 'open_light')
    page.evaluate("[...document.querySelectorAll('#mhWxCard span')].find(s=>s.textContent.trim()==='?').click()"); page.wait_for_timeout(200)
    if page.evaluate("getComputedStyle(document.getElementById('help-wxfactors')).display") != 'none': f.add('BUG', '7: the ? closes it again')
    if errs: f.add('BUG', f'page errors {errs}')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
