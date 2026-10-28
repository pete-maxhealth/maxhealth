"""Persona 348 (v3.10.1235): every control that sends something to an AI carries the same icon, the sparkle.
Guards the source (no robot, brain, wand, star or magnifier on an AI button) and checks the rendered buttons on the screens they live on."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
src = open('maxhealth.html', encoding='utf-8').read()
want = ['✨ Try AI', '✨ Ask AI →', '✨ Generate Full Summary →', '✨ Ask AI · Full Summary', '✨ Generate Monthly Summary →', '✨ Add AI summary',
        '✨ Verify across 3 AIs', '✨ Interpret this with AI', '✨ Send to AI for interpretation', '✨ Estimate portion for me', '✨ Describe meals',
        '✨ Calculate with AI →', '✨ Read the label with AI instead', '✨ Reading barcode with AI…', '✨ Auto-classify', '✨ Create Recipe from this', '✨ Where AI is used', '✨ Full Summary']
for w in want:
    if w not in src: f.add('BUG', 'missing in source: ' + w)
bad = ['🤖 Estimate', '🤖 Describe', '🤖 Interpret', '🤖 Send to AI', '🤖 AI estimate', '🤖 Where', '🧠 Add AI', '🪄 Auto', '⭐ Ask AI', '⭐ Generate Full', '⭐ Full Summary', '🔍 Verify across', '🔍 Reading barcode', '📷 Read the label with AI']
for w in bad:
    if w in src: f.add('BUG', 'old AI icon still in source: ' + w)
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 430, 'height': 1000}, service_workers='block')
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p = ctx.new_page(); p.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = p.evaluate
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1500); ev("startDemoMode('doris')"); p.wait_for_timeout(2500)
    txt = lambda sel: (ev("(s)=>{const e=document.querySelector(s);return e?e.textContent.trim():null}", sel) or '')
    ev("switchTab('insights',document.getElementById('maintab-insights'))"); p.wait_for_timeout(600)
    ev("switchSubTab('insights','reports',document.getElementById('insightstab-reports'))"); p.wait_for_timeout(900)
    for sel in ('#rptFullSummaryBtn', '#rptAskBtn'):
        if not txt(sel).startswith('✨'): f.add('BUG', f'{sel} not sparkle: {txt(sel)[:40]!r}')
    ev("switchTab('log',document.getElementById('maintab-log'))"); p.wait_for_timeout(500)
    ev("openFoodSearch()"); p.wait_for_timeout(600)
    if '✨ Try AI' not in ev("document.getElementById('foodSearchModal') ? document.getElementById('foodSearchModal').innerText : document.body.innerText"): f.add('BUG', 'food search has no ✨ Try AI')
    ev("closeFoodSearch && closeFoodSearch()")
    ev("openMissedDayModal()"); p.wait_for_timeout(600)
    if not txt('#missedDayAIBtn').startswith('✨'): f.add('BUG', 'missed day Calculate with AI not sparkle: ' + txt('#missedDayAIBtn')[:40])
    if not txt('#missedModeAI').startswith('✨'): f.add('BUG', 'missed day Describe meals not sparkle: ' + txt('#missedModeAI')[:40])
    if errs: f.add('JS-exception', errs[0])
    b.close()
bad = any(s in ('BUG', 'JS-exception') for s, _ in f)
for s, m in f: print(s, m)
print('BUGS' if bad else 'OK', len(f)); sys.exit(1 if bad else 0)
