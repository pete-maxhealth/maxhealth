"""Persona 13: the Reports/Insights screens for someone with no data, 45 days of data, and a GBM user -
every range button, the query builder, the report summary, and a treatment progress report."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
U = 'http://localhost:5757'
f = Findings()
VISIBLE = """() => { const out=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(w.nextNode()){const n=w.currentNode; const el=n.parentElement; if(!el||el.closest('script,style')) continue;
    let hidden=false; for(let p=el;p;p=p.parentElement){ const cs=getComputedStyle(p); if(cs.display==='none'||cs.visibility==='hidden'){hidden=true;break;} }
    if(hidden) continue; const t=n.textContent.trim(); if(t.length>1) out.push(t);} return out.join('\\n'); }"""
def boot(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.goto(U + '/'); pg.wait_for_timeout(1500); return pg, errs
def onboard(pg, cond):
    pg.evaluate("onboardNext(2)"); pg.fill('#onboardName', 'Test'); pg.evaluate("onboardNext(3)")
    pg.evaluate("obSetSex('male')"); pg.fill('#onboardAge', '52'); pg.fill('#onboardHeight', '180')
    pg.fill('#onboardWeight', '82'); pg.fill('#onboardTarget', '78')
    pg.evaluate("onboardNext(4)"); pg.evaluate("obSetActivity('light')"); pg.evaluate("obSetGoal('lose')")
    pg.evaluate("onboardNext(5)"); pg.evaluate(f"obSetCondition('{cond}')")
    pg.evaluate("onboardNext(6)"); pg.evaluate("onboardFinish()"); pg.wait_for_timeout(1500)
def tap(pg, tab, sub):
    pg.click(f"[onclick^=\"switchTab('{tab}'\"]"); pg.click(f"[onclick^=\"switchSubTab('{tab}','{sub}'\"]"); pg.wait_for_timeout(700)
BAD = re.compile(r'\b(NaN|undefined|Infinity|\[object Object\])\b|-0\b')
PERSONAL = re.compile(r'92-93|\bPete\b|Beyond the Diagnosis', re.I)

for label, cond, ndays in (('no-data', 'general', 0), ('45-days', 'general', 45), ('gbm-45-days', 'gbm', 45)):
    print('persona', label)
    with fresh_server() as root, sync_playwright() as pw:
        if ndays:
            write_hc_export(root, [dict(date=d, steps=5000 + (i * 137) % 4000, distance_m=4000, calories_active=300, sleep_duration=380 + (i * 7) % 90,
                sleep_deep=70, sleep_light=250, sleep_rem=60, sleep_wake=20, hr_avg=64 + i % 6, hr_resting=55, hrv=40 + i % 15, spo2=95 + (i % 3) * 0.5,
                weight=round(82 - i * 0.05, 1)) for i, d in enumerate(days(ndays))])
            rc, out = run_pipeline(root)
            if rc: f.add('BUG', f'{label}: pipeline failed')
        b = pw.chromium.launch(); pg, errs = boot(b); onboard(pg, cond)
        chk = lambda ok, msg: None if ok else f.add('BUG', f'{label}: {msg}')
        screens = {}
        for tab, sub in (('insights', 'reports'), ('insights', 'trends')):
            tap(pg, tab, sub)
            screens[f'{tab}/{sub}'] = pg.evaluate(VISIBLE)
        # every range button the person can press on Reports
        tap(pg, 'insights', 'reports')
        for d in (7, 30, 90, 365, -1):
            try:
                if d == -1:
                    pg.evaluate("setReportRange(-1)"); pg.evaluate("document.getElementById('rptDateFrom').value='%s'" % days(30)[0]); pg.evaluate("document.getElementById('rptDateTo').value='%s'" % days(1)[0])
                else: pg.evaluate(f"setReportRange({d})")
                pg.evaluate("runReportQuery()"); pg.wait_for_timeout(250)
            except Exception as e: f.add('BUG', f'{label}: range {d}: {str(e)[:100]}')
            screens[f'range{d}'] = pg.evaluate(VISIBLE)
        # compare periods, report summary, insights, performance report
        for call in ("renderReportSummary()", "renderReportInsights()", "generatePerformanceReport()", "renderTreatmentAnalysis()", "renderWeightProtocol()", "renderSleepKetosisCorrelation()"):
            try: pg.evaluate(call)
            except Exception as e: f.add('BUG', f'{label}: {call} threw: {str(e)[:100]}')
        screens['after-calls'] = pg.evaluate(VISIBLE)
        # report profile wizard: open, walk all steps, close
        try:
            pg.evaluate("openReportProfileWizard()"); pg.wait_for_timeout(300)
            for _ in range(6):
                pg.evaluate("reportWizardNext()"); pg.wait_for_timeout(150)
            screens['wizard'] = pg.evaluate(VISIBLE); pg.evaluate("closeReportProfileWizard()")
        except Exception as e: f.add('BUG', f'{label}: report wizard: {str(e)[:120]}')
        # a treatment progress report with sessions + an org branding line
        if ndays:
            pg.evaluate("saveTreatmentDefs([{id:'t1', name:'Test therapy', icon:'💡', color:'#2deb8f'}])"); pg.evaluate("renderReports()")
            tid = 't1'
            if tid:
                hist = pg.evaluate("state.history.slice(0,12).map(h => h.date)")
                pg.evaluate("(a) => saveTreatmentLog(a[1].map(d => ({id:'s'+d, treatmentId:a[0], date:d, ts:Date.now()})))", [tid, hist[::2]])
                keys = pg.evaluate("getAllOverlayableMetrics().slice(0,4).map(m => m.key)")
                pg.evaluate("(a) => saveReportProfiles([{id:'rp1', name:'Test report', orgName:'', orgColor:'#2deb8f', treatmentId:a[0], metrics:a[1], includeSymptoms:false, symptomIds:[], schedule:{frequency:'none',dayOfWeek:0}, lastSent:null}])", [tid, keys])
                dl = []; dlp = []; pg.on('download', lambda d: (dl.append(d.suggested_filename), dlp.append(d.path())))
                try: pg.evaluate("generateProfileReport('rp1')"); pg.wait_for_timeout(1500)
                except Exception as e: f.add('BUG', f'{label}: generateProfileReport threw: {str(e)[:120]}')
                print('   report downloads:', dl)
                chk(bool(dl), 'treatment report produced no file')
                if dlp:
                    txt = open(dlp[0], encoding='utf-8').read(); print('   ', txt.replace(chr(10), ' | ')[:200])
                    chk(not BAD.search(txt) and txt.count(chr(10)) >= 2, f'report CSV has bad/empty content: {txt[:150]!r}')
        screens['final'] = pg.evaluate(VISIBLE)
        for k, t in screens.items():
            m = BAD.search(t)
            if m: f.add('BUG', f'{label}/{k}: "{m.group(0)}" visible -> ...{t[max(0, m.start()-60):m.end()+30]!r}'.replace('\\n', ' '))
            m = PERSONAL.search(t)
            if m: f.add('BUG', f'{label}/{k}: someone else\'s personal text shows: {m.group(0)!r}')
        if cond != 'gbm':
            for k, t in screens.items():
                if re.search(r'GBM Monthly|Research Digest', t): f.add('BUG', f'{label}/{k}: GBM-only section visible to a {cond} user')
        chk(not errs, f'JS errors: {errs}')
        b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
