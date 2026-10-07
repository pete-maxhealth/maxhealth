"""Persona 47: slow waits use the same pulsing border as the chat thinking bubble - report/AI/sync buttons show a box while disabled and drop it when re-enabled; compare-AI placeholder uses the same class."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    # watcher: disable a report button -> box appears with the animation; enable -> gone
    for bid in ['rptAskBtn', 'gbmSummaryBtn', 'rptFullSummaryBtn']:
        if not page.evaluate(f"!!document.getElementById('{bid}')"): f.add('BUG', f'{bid} missing'); continue
        page.evaluate(f"document.getElementById('{bid}').disabled = true"); page.wait_for_timeout(700)
        anim = page.evaluate(f"(()=>{{const x=document.querySelector('.mh-wait-box[data-mhwait=\"{bid}\"]');return x?getComputedStyle(x).animationName:null}})()")
        if anim != 'thinkingPulse': f.add('BUG', f'{bid}: wait box not pulsing while disabled: {anim}')
        page.evaluate(f"document.getElementById('{bid}').disabled = false"); page.wait_for_timeout(700)
        if page.evaluate(f"!!document.querySelector('.mh-wait-box[data-mhwait=\"{bid}\"]')"): f.add('BUG', f'{bid}: box stuck after re-enable')
    # compare-AI placeholder markup
    h = page.evaluate("mhWaitHTML('x')")
    if 'mh-wait-box' not in h: f.add('BUG', 'mhWaitHTML wrong')
    n = page.evaluate("document.documentElement.innerHTML.split('mhWaitHTML(').length - 1")
    if n < 5: f.add('BUG', f'compare placeholders not converted ({n} refs)')
    src = page.content()
    if "independently about: ${desc}…`, 'system', 'thinking')" not in src: f.add('BUG', 'log-chat compare AI bubble is not a pulsing thinking bubble')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
    b.close()
print('findings', len(f)); sys.exit(1 if f else 0)
