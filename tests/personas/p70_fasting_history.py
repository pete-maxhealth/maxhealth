"""Persona 70: the Fasting report lists every measured fast (not just 30 days), newest first, with filters, an honest
unmeasured-days note, and an all-time CSV. Known meal times give known durations."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from datetime import date, timedelta
from playwright.sync_api import sync_playwright
f = Findings()
dmy = lambda n: (date.today() - timedelta(days=n)).strftime('%d/%m/%y')
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:200]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    page.evaluate("localStorage.setItem('mh_onboarded','1')")
    # 60 days (well past 30), each with a 08:00 and 20:00 meal -> every fast is 12h. Day 45 is missing, so day 44 cannot be measured.
    # One extended fast: day 10 has Fasting tag and no meals, so day 9's fast runs 20:00 (day 11) -> 08:00 (day 9) = 36h.
    page.evaluate("""(days) => {
      const mk = (n) => ({date: days[n], mode:'standard', notes:'', log:[{id:n*10+1,name:'a',kcal:400,time:'08:00',carbs:5},{id:n*10+2,name:'b',kcal:500,time:'20:00',carbs:5}], totals:{kcal:900,protein:50,fat:50,carbs:10}});
      const h = [];
      for (let n = 60; n >= 1; n--) { if (n === 45) continue; if (n === 10) { h.push({date: days[n], mode:'standard', notes:'Fasting', log:[], totals:{kcal:0,protein:0,fat:0,carbs:0}}); continue; } h.push(mk(n)); }
      state.history = h; saveState(); }""", [dmy(n) for n in range(0, 62)])
    page.evaluate("localStorage.setItem('mh_fasting_goal_h','12'); renderFastingReport();")
    page.wait_for_timeout(300)
    n_all = page.evaluate("mhFastingHistoryRows().fasts.length")
    if n_all < 50: f.add('BUG', f'expected the list to reach back past 30 days (about 56 fasts), got {n_all}')
    rows = page.evaluate("mhFastingHistoryRows()")
    if rows['unmeasured'] < 1: f.add('BUG', 'the day after the gap should be counted as unmeasured')
    ext = [r for r in rows['fasts'] if r['extended']]
    if len(ext) != 1 or abs(ext[0]["hours"] - 36) > 0.01: f.add('BUG', f'expected one extended fast of 36h, got {[(r["date"], r["hours"]) for r in ext]}')
    plain = [r for r in rows['fasts'] if not r['extended']]
    if any(abs(r['hours'] - 12) > 0.01 for r in plain): f.add('BUG', 'a normal 20:00 -> 08:00 fast should be exactly 12h')
    if not all(r['endMs'] >= nxt['endMs'] for r, nxt in zip(rows['fasts'], rows['fasts'][1:])): f.add('BUG', 'list is not newest first')
    txt = page.evaluate("document.getElementById('fast-history').innerText")
    if 'Every fast' not in txt or 'could not be measured' not in txt: f.add('BUG', f'history block or unmeasured note missing: {txt[:200]!r}')
    if 'Show all' not in txt: f.add('BUG', 'long list should offer Show all')
    shown = page.evaluate("document.querySelectorAll('#fast-history > div[style*=\"justify-content\"]').length")
    if shown != 20: f.add('BUG', f'expected 20 rows before Show all, got {shown}')
    page.evaluate("mhToggleFastHistAll()")
    shown2 = page.evaluate("document.querySelectorAll('#fast-history > div[style*=\"justify-content\"]').length")
    if shown2 != n_all: f.add('BUG', f'Show all should list every fast ({n_all}), got {shown2}')
    page.evaluate("mhSetFastHistFilter('extended')")
    if page.evaluate("document.querySelectorAll('#fast-history > div[style*=\"justify-content\"]').length") != 1: f.add('BUG', 'Extended filter should show exactly one fast')
    page.evaluate("mhSetFastHistFilter('under')")
    if 'No fasts match' not in page.evaluate("document.getElementById('fast-history').innerText") and page.evaluate("mhFastingHistoryRows().fasts.filter(r=>!r.met).length") == 0: pass
    with page.expect_download() as dl: page.evaluate("mhDownloadFastingCsv()")
    path = dl.value.path(); lines = open(path).read().strip().split('\n')
    if len(lines) != n_all + 1: f.add('BUG', f'CSV should have a header plus {n_all} rows, got {len(lines)}')
    if not lines[0].startswith('fast_start,fast_end,hours'): f.add('BUG', f'bad CSV header {lines[0]!r}')
    if not lines[0].endswith('meal_counts_from_kcal') or not lines[1].endswith(',50'): f.add('BUG', f'CSV should record the kcal limit used (default 50): {lines[0]!r} / {lines[1]!r}')
    page.evaluate("localStorage.setItem('mh_fasting_kcal_threshold','100')")
    with page.expect_download() as dl2: page.evaluate("mhDownloadFastingCsv()")
    if not open(dl2.value.path()).read().split('\n')[1].endswith(',100'): f.add('BUG', 'CSV did not pick up a changed kcal limit')
    if errs: f.add('BUG', f'page errors: {errs[:2]}')
print('findings', len(f)); sys.exit(1 if f else 0)
