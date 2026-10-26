"""Persona 326 (v3.10.1221): read-aloud plays the WHOLE text. Pete: Ask AI read-aloud read one line then stopped. A chunk that errors, or never reports back, must not end the queue. Covers every read-aloud button path (Ask AI box, GBM summary, chat bubble, recipe, research digest all go through toggleSpeakText)."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
FAKE = """
window.__spoken = [];
SpeechSynthesis.prototype.speak = function(u){ const n = window.__spoken.length; window.__spoken.push(u.text);
  setTimeout(() => { if (n === 0) { u.onerror && u.onerror({error:'interrupted'}); } else if (n === 1) { /* never reports back */ } else { u.onstart && u.onstart({}); u.onend && u.onend({}); } }, 50); };
SpeechSynthesis.prototype.cancel = function(){};
SpeechSynthesis.prototype.pause = function(){}; SpeechSynthesis.prototype.resume = function(){};
Object.defineProperty(SpeechSynthesis.prototype, 'speaking', {get(){return true}});
"""
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); ctx.add_init_script(FAKE)
    page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2000)
    pad = " and some more words to make this sentence long enough to be its own chunk in the queue of speech"
    txt = "First sentence of the answer is here" + pad + ". Second sentence follows it now" + pad + ". Third sentence carries on too" + pad + ". Fourth sentence is the last one" + pad + "."
    ev("window.__b = document.createElement('span'); document.body.appendChild(window.__b); toggleSpeakText(window.__b, %r); 0" % txt)
    page.wait_for_timeout(22000)
    n = ev("window.__spoken.length"); allt = ev("window.__spoken.join(' ')")
    if n < 2: f.add('BUG', f'read-aloud stopped after {n} chunk(s)')
    if 'Fourth sentence' not in allt: f.add('BUG', f'the whole text is read, not just the start: {allt[:120]}')
    if ev("window.__b.textContent") != '🔊': f.add('BUG', 'the speaker button returns to its idle icon when finished')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
