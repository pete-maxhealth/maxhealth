"""Persona 46: Trends > Body Composition card - verdict from week-vs-week smart-scale means, share bar, change badges, unit-aware, hides with no data, reorder/hide controls present."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
def csv(rows):
    return "date,weight,muscle_mass_kg,fat_mass_kg,muscle_pct,fat_pct,bone_mass_kg\n" + "\n".join(",".join(str(x) for x in r) for r in rows) + "\n"
def days(start_iso_day, vals):  # vals: list of (w, mu, fa)
    import datetime
    d0 = datetime.date(2026, 10, 7)
    out = []
    for off, (w, mu, fa) in vals:
        d = d0 - datetime.timedelta(days=off)
        out.append((d.isoformat(), w, mu, fa, round(mu / w * 100, 1), round(fa / w * 100, 1), 3.7))
    return out
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    page.evaluate("onboardNext(2)"); page.fill('#onboardName', 'Ola'); page.evaluate("onboardNext(3)")
    page.evaluate("obSetSex('male')"); page.fill('#onboardAge', '58'); page.fill('#onboardHeight', '176')
    page.fill('#onboardWeight', '92'); page.fill('#onboardTarget', '90')
    page.evaluate("onboardNext(4)"); page.evaluate("obSetActivity('light')"); page.evaluate("obSetGoal('lose')")
    page.evaluate("onboardNext(5)"); page.evaluate("obSetCondition('general')")
    page.evaluate("onboardNext(6)"); page.evaluate("onboardFinish()"); page.wait_for_timeout(1500)
    def setcsv(rows):
        page.evaluate("(t)=>localStorage.setItem('mh_combined_csv_cache',t)", csv(rows))
    def render():
        page.evaluate("renderBodyCompCard()")
        return page.evaluate("[document.getElementById('bodyCompCard').style.display, document.getElementById('trends-bodycomp-wrap').innerText]")
    # no data -> hidden
    page.evaluate("localStorage.removeItem('mh_combined_csv_cache')")
    if render()[0] != 'none': f.add('BUG', 'card visible with no body-comp data')
    # A: weight flat, fat up, muscle down (two readings each week)
    setcsv(days(0, [(0, (92.2, 69.9, 18.6)), (2, (92.1, 70.0, 18.5)), (7, (92.2, 70.8, 17.7)), (9, (92.3, 70.9, 17.6))]))
    d, t = render()
    if d == 'none' or 'Gaining fat, losing muscle' not in t: f.add('BUG', f'verdict A wrong: {t[:200]!r}')
    if 'This week vs last week' not in t: f.add('BUG', 'basis not shown for window mode')
    if 'Weight barely moved' not in t: f.add('BUG', 'flat-weight note missing')
    if 'Muscle' not in t or 'Fat' not in t or '%' not in t: f.add('BUG', 'share bar labels missing')
    # B: fat down, muscle up
    setcsv(days(0, [(0, (91.0, 71.5, 16.9)), (2, (91.0, 71.6, 16.8)), (7, (92.0, 70.5, 18.0)), (9, (92.0, 70.4, 18.1))]))
    t = render()[1]
    if 'Losing fat, gaining muscle' not in t: f.add('BUG', f'verdict B wrong: {t[:120]!r}')
    # C: steady
    setcsv(days(0, [(0, (92.0, 70.0, 18.0)), (2, (92.0, 70.1, 18.0)), (7, (92.1, 70.0, 18.1)), (9, (92.0, 70.0, 18.0))]))
    t = render()[1]
    if 'Holding steady' not in t: f.add('BUG', f'verdict C wrong: {t[:120]!r}')
    # D: sparse -> latest vs previous reading, labelled
    setcsv(days(0, [(0, (92.2, 69.9, 18.9)), (3, (92.2, 70.9, 17.9))]))
    t = render()[1]
    if 'Latest weigh-in vs the one before' not in t or 'Gaining fat, losing muscle' not in t: f.add('BUG', f'fallback mode wrong: {t[:200]!r}')
    # E: single reading -> no verdict claim
    setcsv(days(0, [(0, (92.2, 69.9, 18.9))]))
    t = render()[1]
    if 'First reading' not in t: f.add('BUG', f'single reading: {t[:120]!r}')
    # unit-aware
    setcsv(days(0, [(0, (92.2, 69.9, 18.9)), (3, (92.2, 70.9, 17.9))]))
    page.evaluate("setGlobalWeightUnit('lbs')")
    t = render()[1]
    if ' lb' not in t or ' kg' in t.replace('kg.', ''): f.add('BUG', f'card not in lb: {t[:300]!r}')
    # appears on the Trends tab with reorder/hide controls
    page.evaluate("setGlobalWeightUnit('kg')")
    page.evaluate("switchTabById('trends')"); page.wait_for_timeout(1200)
    ttl = page.evaluate("document.getElementById('title-trends-bodycomp')?.innerText||''")
    if '▲' not in ttl and '👁' not in ttl: f.add('BUG', f'no reorder/hide controls on body comp card: {ttl!r}')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
