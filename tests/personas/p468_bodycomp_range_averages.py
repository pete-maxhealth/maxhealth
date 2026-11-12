"""Persona 468 (v3.10.1383): the Move body-composition range line gives the change in AVERAGES at each end (a week of readings), not one reading minus one reading, and shows the weight change beside it. Pete (12 Nov): Muscle -3.2 kg over a year looked wrong; a single high first reading and low last reading had made a loss. Invented data."""
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
    import datetime
    today = datetime.date.today()
    def csv2(rows): return "date,weight,muscle_mass_kg,fat_mass_kg,muscle_pct,fat_pct,bone_mass_kg\n" + "\n".join(",".join(str(x) for x in r) for r in rows) + "\n"
    rows = []
    for i in range(60):   # day 0 = oldest; stable body: muscle 70, fat 18, weight 92 (with small invented wobble)
        d = today - datetime.timedelta(days=60 - i); wob = [0.2, -0.1, 0.0, 0.15, -0.2][i % 5]
        mu, fa, w = 70 + wob, 18 - wob, 92.0
        if i == 0: mu, fa = 74.0, 15.0        # one high first reading
        if i == 59: mu, fa = 66.0, 21.0       # one low last reading
        rows.append((d.isoformat(), w, mu, fa, round(mu / w * 100, 1), round(fa / w * 100, 1), 3.7))
    page.evaluate("(t)=>localStorage.setItem('mh_combined_csv_cache',t)", csv2(rows))
    page.evaluate("mhMoveSetRange('bodycomp', 0)"); page.evaluate("renderBodyCompCard()")
    t = page.evaluate("document.getElementById('trends-bodycomp-wrap').innerText")
    m = re.search(r'Muscle\s+([+\-\u2212]?[\d.]+)', t[t.find('READINGS'):] if 'READINGS' in t else t)
    mu = float(m.group(1).replace('\u2212', '-')) if m else None
    if mu is None: f.add('BUG', f'no muscle change on the range line: {t[-300:]!r}')
    elif abs(mu) > 1.2: f.add('BUG', f'muscle change {mu} kg from a stable body: one reading at each end still drives it (old method gives -8)')
    if 'Weight' not in t[t.find('READINGS'):]: f.add('BUG', 'the weight change is missing beside muscle and fat')
    if 'averages at each end' not in t: f.add('BUG', 'the range line does not say it is averages')
    # a real, steady loss must still show: muscle falls 70 -> 67 across 60 days
    rows2 = []
    for i in range(60):
        d = today - datetime.timedelta(days=60 - i); mu = 70 - 3 * i / 59; rows2.append((d.isoformat(), 92 - 3 * i / 59, round(mu, 2), 18.0, round(mu / 92 * 100, 1), 19.5, 3.7))
    page.evaluate("(t)=>localStorage.setItem('mh_combined_csv_cache',t)", csv2(rows2)); page.evaluate("renderBodyCompCard()")
    t2 = page.evaluate("document.getElementById('trends-bodycomp-wrap').innerText"); t2 = t2[t2.find('READINGS'):]
    m2 = re.search(r'Muscle\s+([+\-\u2212]?[\d.]+)', t2); v2 = float(m2.group(1).replace('\u2212', '-')) if m2 else None
    if v2 is None or not (-3.2 < v2 < -2.0): f.add('BUG', f'a real steady loss of 3 kg shows as {v2}')
    if errs: f.add('JS-exception', errs[0])
print('findings', len(f))
for x in f: print(x)
sys.exit(1 if f else 0)
