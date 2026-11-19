"""Persona 506 (v3.10.1431): Non-HDL cholesterol (total - HDL) is calculated for any panel with both, shown as a trend chip and in the drill chart, never an input in the panel form, never stored, and reaches the AI summary. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(3000); ev = page.evaluate
    ev("state.onboarded=true; saveState(); var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'")
    ev("saveLabResults([{id:'a',date:'01/09/26',labName:'T',values:{total_chol:5.8,hdl:1.4,ldl:3.6},custom:[]},{id:'b',date:'01/11/26',labName:'T',values:{total_chol:5.1,hdl:1.5},custom:[]},{id:'c',date:'05/11/26',labName:'T',values:{ldl:2.9},custom:[]}])")
    tr = ev("getLabMarkerTrend('non_hdl').map(x=>x.value).join(',')")
    tr == '4.4,3.6' or f.add('FAIL', 'non-HDL trend wrong (expect 4.4,3.6 and skip panel without HDL): ' + tr)
    ev("JSON.stringify(loadLabResults()).indexOf('non_hdl')") == -1 or f.add('FAIL', 'non_hdl was stored')
    page.click('#maintab-settings'); page.wait_for_timeout(500); page.click('#settingstab-manage'); page.wait_for_timeout(400)
    ev("renderLabResultsSettings()")
    'Non-HDL' in ev("document.getElementById('labTrendChips').innerText") or f.add('FAIL', 'no Non-HDL trend chip')
    ev("openLabPanelModal(null); document.getElementById('labMarker_non_hdl') === null") or f.add('FAIL', 'non-HDL shows as an input in the panel form')
    ev("closeLabPanelModal()")
    ev("openChartLightbox('lab_non_hdl')"); page.wait_for_timeout(800)
    ev("document.body.innerText.indexOf('Non-HDL') > -1") or f.add('FAIL', 'drill chart did not open')
    errs and f.add('JS-exception', errs[0])
print('findings', len(f))
