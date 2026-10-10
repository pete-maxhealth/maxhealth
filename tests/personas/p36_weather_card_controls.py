"""Persona 36: weather card has show / hide / reorder like the other Today cards, a help tip explaining what the weather affects,
a saved custom order survives the card being added, and the Formulas card documents the water/effort rules."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
OLD = ['weight','daymode','ketosis','macros','macroratio','goalcheck','steps','symptoms','treatment','activity','water','log','guides']
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Pete'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '56'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '82'); page.fill('#onboardTarget', '78')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('gbm')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    # a person with a custom order saved BEFORE the weather card existed
    custom = list(reversed(OLD))
    page.evaluate("o=>localStorage.setItem('mh_dashboard_order',JSON.stringify(o))", custom)
    page.evaluate("d=>{localStorage.setItem('mh_wx_loc',JSON.stringify({lat:38.42,lon:27.14,name:'Izmir'}));localStorage.setItem('mh_wx_cache',JSON.stringify({lat:38.42,lon:27.14,at:Date.now(),date:todayStr(),temp:30,feelsNow:32,code:0,feelsMax:33,hi:31,lo:22,uv:8,rainPct:5}))}")
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(2500)
    order = page.evaluate("getDashboardOrder()")
    exp = list(custom); exp.insert(exp.index('water'), 'weather'); exp.insert(exp.index('water'), 'fasting')  # fasting (v3.10.930) also slots in just above water
    if order != exp: f.add('BUG', f'custom order not preserved with weather slotted before water: {order}')
    idx = lambda: page.evaluate("(()=>{const p=document.getElementById('mhWxCard').parentNode;const k=[...p.children];return [k.indexOf(document.getElementById('mhWxCard')),k.indexOf(document.getElementById('dashSection-water'))]})()")
    a, w = idx()
    if not a < w: f.add('BUG', f'weather card not placed before the water card in the page {a},{w}')
    # controls present on the card
    if page.evaluate("document.querySelectorAll('#mhWxCard [onclick*=\"moveDashboardSection(\\'weather\\'\"]').length") != 2: f.add('BUG', 'weather card is missing its up/down arrows')
    if not page.evaluate("!!document.querySelector('#mhWxCard [onclick*=\"toggleDashboardSectionHidden(\\'weather\\'\"]')"): f.add('BUG', 'weather card has no hide (eye) button')
    # reorder
    before = page.evaluate("getDashboardOrder().indexOf('weather')")
    page.evaluate("moveDashboardSection('weather','up')"); page.wait_for_timeout(300)
    if page.evaluate("getDashboardOrder().indexOf('weather')") != before - 1: f.add('BUG', 'weather did not move up')
    a2, w2 = idx()
    if a2 == a: f.add('BUG', 'weather card did not move in the page')
    # hide, restore strip, persistence, show
    page.evaluate("toggleDashboardSectionHidden('weather')"); page.wait_for_timeout(300)
    if page.evaluate("getComputedStyle(document.getElementById('mhWxCard')).display") != 'none': f.add('BUG', 'weather card not hidden')
    if 'Weather' not in page.evaluate("document.getElementById('dashboardRestoreStrip').textContent"): f.add('BUG', 'no Weather pill in the hidden strip')
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(2500)
    if page.evaluate("getComputedStyle(document.getElementById('mhWxCard')).display") != 'none': f.add('BUG', 'hidden weather card came back after reload')
    page.evaluate("toggleDashboardSectionHidden('weather')"); page.wait_for_timeout(300)
    if page.evaluate("getComputedStyle(document.getElementById('mhWxCard')).display") == 'none': f.add('BUG', 'weather card not restored')
    # help tip
    page.evaluate("document.querySelector('#mhWxCard span[onclick*=\"help-wxfactors\"]').click()"); page.wait_for_timeout(200)
    ht = page.evaluate("document.getElementById('help-wxfactors').innerText")
    if 'What it does not change' not in ht or '+500ml' not in ht or 'override' not in ht.lower() and 'your say wins' not in ht.lower(): f.add('BUG', 'help tip missing content: ' + ht[:200])
    if page.evaluate("getComputedStyle(document.getElementById('help-wxfactors')).display") == 'none': f.add('BUG', 'help tip did not open')
    # also available before weather is set up (not-set-up state keeps the controls)
    page.evaluate("mhWxRemove()"); page.wait_for_timeout(300)
    if not page.evaluate("!!document.querySelector('#mhWxCard [onclick*=\"toggleDashboardSectionHidden(\\'weather\\'\"]')"): f.add('BUG', 'hide button missing before weather is set up')
    # formulas card
    page.evaluate("switchTabById('manage')"); page.wait_for_timeout(500)
    ft = page.evaluate("document.getElementById('set-formulas-wrap').innerText")
    if 'Water Target & Weather' not in ft or '+500ml' not in ft or 'Suggested exercise effort' not in ft: f.add('BUG', 'Formulas card does not document the weather rules')
    if errs: f.add('JS-exception', str(errs[:3]))
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
