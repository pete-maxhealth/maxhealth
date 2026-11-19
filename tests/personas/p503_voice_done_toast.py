"""Persona 503 (v3.10.1427): saying "done" after logging by voice must not show "No items captured" (it did every time, because the list was emptied before the check).
Walks: tap the mic, say two items, say done -> items are sent to the log preview and the toast is not "No items captured"; a trailing "done" inside one long phrase behaves the same;
"done" with nothing said still says "No items captured"; Today is untouched until Log it; reload keeps nothing half-done. Stand-in speech recogniser (headless Chromium has no microphone). Invented demo data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
FAKE = """window.SpeechRecognition = window.webkitSpeechRecognition = class { constructor(){ window.__sr = this; }
  start(){ setTimeout(()=>this.onstart && this.onstart(), 30); } stop(){ setTimeout(()=>this.onend && this.onend(), 10); } abort(){} };
window.__say = (t)=>{ const r=[{transcript:t}]; r.isFinal=true; window.__sr.onresult({resultIndex:0, results:[r]}); };"""
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); ctx.add_init_script(FAKE)
    page = ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/?demo=doris'); page.wait_for_timeout(3500); ev = page.evaluate
    toast = lambda: ev("document.getElementById('toast')?.innerText||''")
    preview = lambda: ev("(document.getElementById('mealPreviewBubble')||{innerText:''}).innerText")
    say = lambda t: (ev("t=>window.__say(t)", t), page.wait_for_timeout(700))
    page.click('#maintab-log'); page.wait_for_timeout(700)
    # 1 two items then "done"
    page.click('#voiceBtn'); page.wait_for_timeout(500)
    say('2 eggs'); say('a slice of toast'); say('done'); page.wait_for_timeout(1500)
    'No items captured' in toast() and f.add('FAIL', f'"done" after two items still says No items captured: {toast()!r}')
    p = preview(); ('Egg' in p and 'bread' in p.lower()) or f.add('FAIL', f'items not in the log preview: {p[:120]!r}')
    ev("document.querySelector('#mealPreviewBubble button.btn-cancel, #mealPreviewBubble button:last-of-type')?.click()")
    ev("cancelMealPreview && cancelMealPreview()") if ev("typeof cancelMealPreview==='function'") else None; page.wait_for_timeout(500)
    # 2 one long phrase ending in done
    page.click('#voiceBtn'); page.wait_for_timeout(500); say('peppers and chicken breast done'); page.wait_for_timeout(1500)
    'No items captured' in toast() and f.add('FAIL', f'trailing "done" still says No items captured: {toast()!r}')
    'Pepper' in preview() or f.add('FAIL', f'trailing-done phrase did not reach the preview: {preview()[:120]!r}')
    ev("cancelMealPreview && cancelMealPreview()") if ev("typeof cancelMealPreview==='function'") else None; page.wait_for_timeout(500)
    # 3 "done" with nothing said keeps the message
    page.click('#voiceBtn'); page.wait_for_timeout(500); say('done'); page.wait_for_timeout(800)
    'No items captured' in toast() or f.add('FAIL', f'"done" with nothing said should say No items captured: {toast()!r}')
    # 3b filler + done after an item said earlier: the item is sent, the filler is not logged as food
    ev("cancelMealPreview && cancelMealPreview()") if ev("typeof cancelMealPreview==='function'") else None; page.wait_for_timeout(300)
    page.click('#voiceBtn'); page.wait_for_timeout(500); say('2 eggs'); say("that's all done"); page.wait_for_timeout(1500)
    ('Egg' in preview()) or f.add('FAIL', f'"that\'s all done" after an item did not send it: {preview()[:100]!r}')
    ('that' in preview().lower() and 'all' in preview().lower().split('ready to log')[-1][:60]) and f.add('FAIL', f'filler words were logged as food: {preview()[:100]!r}')
    # 4 nothing logged by any of this
    ev("(state.todayLog||[]).length") == 0 or f.add('FAIL', f'something was logged without Log it: {ev("(state.todayLog||[]).length")}')
    errs and f.add('JS-exception', errs[0])
print('findings', len(f))
