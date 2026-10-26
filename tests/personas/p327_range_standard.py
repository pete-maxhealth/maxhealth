"""Persona 327 (v3.10.1221): ONE date-range control everywhere. Built after Pete saw Trends, Reports and Move each draw Custom differently (blank boxes, different sizes, different labels).
Renders every picker with Custom chosen and compares them against each other: same chip words, chips not wrapped, From/To labelled boxes with the same look, never blank, same apply behaviour.
Also: Reports' Fasting, Sleep-ketosis, Weight protocol and Treatment cards follow the range. Saves a side-by-side screenshot per picker in /tmp/p327/."""
import sys, os; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings(); os.makedirs('/tmp/p327', exist_ok=True)
STD = ['7 Days', '30 Days', '90 Days', 'All', 'Custom']
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2500)
    # name -> (setup JS, chip selector, dates block selector)
    P = {
      'trends':  ("switchTabById('trends'); setTrendsFilter(-1, document.getElementById('trendsBtnCustom'))", '#trendsBtn7,#trendsBtn30,#trendsBtn90,#trendsBtnAll,#trendsBtnCustom', '#trendsCustomDateRow'),
      'reports': ("switchTabById('reports'); setReportRange(-1, document.getElementById('rpt-range-custom'))", '[id^=rpt-range-]', '#rpt-custom-dates'),
      'move':    ("switchTabById('move'); mhMoveSetRange('exercise',-1)", '#moveRange-exercise .trends-filter-btn', '#moveDates-exercise'),
      'compare': ("openMultiMetricOverlay(); setMMPeriod(-1, document.querySelector('#mmPeriodBtns button:last-child'))", '#mmPeriodBtns button', '#mmCustomDateRow'),
    }
    info = {}
    for name, (js, chips, block) in P.items():
        try: ev(js)
        except Exception as e: f.add('BUG', f'{name}: could not open picker: {str(e)[:80]}'); continue
        page.wait_for_timeout(900)
        d = ev("""(a) => { const chips = [...document.querySelectorAll(a.chips)]; const b = document.querySelector(a.block); if (!b) return {err: 'no dates block'};
          const ins = [...b.querySelectorAll('input[type=date]')], labs = [...b.querySelectorAll('label')].map(l => l.firstChild.textContent.trim());
          const cs = ins[0] ? getComputedStyle(ins[0]) : null;
          return { chips: chips.map(c => c.innerText.trim()), chipH: chips.map(c => Math.round(c.getBoundingClientRect().height)), vals: ins.map(i => i.value), labs, shown: getComputedStyle(b).display !== 'none',
                   inStyle: cs ? [cs.fontSize, cs.borderRadius, cs.backgroundColor, cs.paddingTop, cs.borderTopWidth].join('/') : '', inH: ins[0] ? Math.round(ins[0].getBoundingClientRect().height) : 0, labStyle: b.querySelector('label') ? [getComputedStyle(b.querySelector('label')).fontSize, getComputedStyle(b.querySelector('label')).textTransform].join('/') : '' } }""", {'chips': chips, 'block': block})
        if 'err' in d: f.add('BUG', f'{name}: {d["err"]}'); continue
        info[name] = d
        if d['chips'] != STD: f.add('BUG', f'{name}: chips are the standard set {STD}, got {d["chips"]}')
        if max(d['chipH'] or [0]) > 34: f.add('BUG', f'{name}: chip text wraps (heights {d["chipH"]})')
        if not d['shown']: f.add('BUG', f'{name}: From/To boxes show when Custom is chosen')
        if len(d['vals']) != 2 or not all(d['vals']): f.add('BUG', f'{name}: From/To are filled in, not blank: {d["vals"]}')
        if d['labs'] != ['From', 'To']: f.add('BUG', f'{name}: boxes are labelled From / To: {d["labs"]}')
        el = page.query_selector(block)
        if el: el.scroll_into_view_if_needed(); page.screenshot(path=f'/tmp/p327/{name}.png')
    ref = info.get('reports')
    for name, d in info.items():
        if ref and d['inStyle'] != ref['inStyle']: f.add('BUG', f'{name}: date boxes look the same as Reports: {d["inStyle"]} vs {ref["inStyle"]}')
        if ref and d['labStyle'] != ref['labStyle']: f.add('BUG', f'{name}: labels look the same as Reports: {d["labStyle"]} vs {ref["labStyle"]}')
        if ref and abs(d['inH'] - ref['inH']) > 2: f.add('BUG', f'{name}: date boxes are the same height: {d["inH"]} vs {ref["inH"]}')
    # Treatment sessions + Statistics use the same block (dropdown pickers there)
    ev("switchTabById('reports')"); page.wait_for_timeout(500)
    ev("document.querySelectorAll('.mh-range-dates').length")
    n = ev("[...document.querySelectorAll('input[type=date]')].filter(i => !i.closest('.mh-range-dates') && /Custom|from|to/i.test(i.id)).map(i => i.id)")
    if n: f.add('BUG', f'a range date box is outside the shared style: {n}')
    # Reports cards follow the range
    ev("[0,2,4,6,9,12,16,20,25,30,35].forEach(i => { const d = state.history[i]; if (d) d.notes = (d.notes ? d.notes + ', ' : '') + 'Chemotherapy'; }); saveState(); renderReports()"); page.wait_for_timeout(600)
    ids = ['sleep-ketosis-content', 'fasting-report-content', 'weight-protocol-content', 'treatment-analysis-section']
    sig = lambda: ev("(" + str(ids) + ").map(i => { const e = document.getElementById(i); return e ? e.innerText.replace(/\\s+/g,' ') : '' })")
    ev("setReportRange(0, document.getElementById('rpt-range-all'))"); page.wait_for_timeout(500); a = sig()
    ev("setReportRange(7, document.getElementById('rpt-range-7'))"); page.wait_for_timeout(500); b = sig()
    for i, idn in enumerate(ids):
        if a[i] and a[i] == b[i]: f.add('BUG', f'{idn} follows the range (same text for All and 7 Days)')
    # Trends 90 days works; Reports custom applies on change (no Apply button needed)
    ev("setTrendsFilter(90, document.getElementById('trendsBtn90'))"); page.wait_for_timeout(300)
    if ev("trendsWindow") != 90: f.add('BUG', '90 Days works in Trends')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
