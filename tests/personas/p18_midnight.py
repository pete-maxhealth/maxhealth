"""Persona 18: midnight rollover. Day changes while the app is closed, a multi-day gap, and the app left open across midnight."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
f = Findings()

def fmt(d): return d.strftime('%d/%m/%y')

def setup(page):
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Mo'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '50'); page.fill('#onboardHeight', '178')
    page.fill('#onboardWeight', '80'); page.fill('#onboardTarget', '75')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('maintain')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1200)

MEAL = {"name": "Porridge", "kcal": 300, "protein": 10, "carbs": 50, "fat": 6, "time": "08:00", "items": []}
BLOCK = re.compile(r'^https?://(?!localhost)')

def state(page): return page.evaluate("JSON.parse(localStorage.getItem('maxhealth_v1')||'{}')")
def put(page, fn):
    s = state(page); fn(s); page.evaluate("s=>localStorage.setItem('maxhealth_v1',JSON.stringify(s))", s)

with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch()
    for gap in (1, 5, 40):
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
        ctx.route(BLOCK, lambda r: r.abort())
        page = ctx.new_page(); errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:150]))
        setup(page)
        old = fmt(datetime.now() - timedelta(days=gap))
        def mk(s):
            s['lastDate'] = old; s['todayLog'] = [dict(MEAL)]; s['history'] = []
        put(page, mk)
        page.reload(); page.wait_for_timeout(2000)
        s = state(page); tag = f'gap {gap}d'
        if s.get('todayLog'): f.add('BUG', f'{tag}: yesterday\'s meal still on Today after rollover')
        h = [x for x in s.get('history', []) if x.get('date') == old]
        if len(h) != 1: f.add('BUG', f'{tag}: expected exactly one history entry for {old}, found {len(h)}')
        elif round(h[0].get('totals', {}).get('kcal', 0)) != 300: f.add('BUG', f'{tag}: history kcal {h[0].get("totals")}')
        if s.get('lastDate') != fmt(datetime.now()): f.add('BUG', f'{tag}: lastDate not advanced ({s.get("lastDate")})')
        # reload again: must not duplicate
        page.reload(); page.wait_for_timeout(1500)
        s2 = state(page)
        if len([x for x in s2.get('history', []) if x.get('date') == old]) != 1: f.add('BUG', f'{tag}: second reload duplicated/changed history')
        # empty day must not create a junk history entry
        def empty(s): s['lastDate'] = old; s['todayLog'] = []; s['history'] = []
        put(page, empty); page.reload(); page.wait_for_timeout(1800)
        if state(page).get('history'): f.add('BUG', f'{tag}: empty day wrote a history entry')
        # Today tab renders and shows zero
        page.click("[onclick^=\"switchTab('today'\"]"); page.wait_for_timeout(500)
        if errs: f.add('JS-exception', f'{tag}: {errs[:2]}')
        print(f'  {tag}: done'); ctx.close()

    # App left open across midnight: fake clock, meal logged at 23:58, wait past midnight, bring app back to foreground
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(BLOCK, lambda r: r.abort())
    page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:150]))
    now = datetime.now().replace(hour=23, minute=57, second=0, microsecond=0)
    page.clock.install(time=now)
    setup(page)
    put(page, lambda s: s.__setitem__('todayLog', [dict(MEAL)]))
    page.reload(); page.wait_for_timeout(1500)
    day1 = fmt(now)
    page.clock.fast_forward('05:00')   # to 00:02
    page.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); page.wait_for_timeout(1500)
    live = page.evaluate("(typeof state!=='undefined'&&state.todayLog||[]).length")
    if live: f.add('BUG', 'app left open across midnight: yesterday\'s meal still live on Today without a reload')
    page.reload(); page.wait_for_timeout(2000)
    s = state(page)
    if s.get('todayLog'): f.add('BUG', 'open across midnight: meal still on the new day after returning to the app')
    if not [x for x in s.get('history', []) if x.get('date') == day1]: f.add('BUG', f'open across midnight: {day1} missing from history')
    if errs: f.add('JS-exception', f'open across midnight: {errs[:2]}')
    ctx.close(); b.close()
print('findings', len(f)); [print(' ', x) for x in f]; sys.exit(1 if f else 0)
