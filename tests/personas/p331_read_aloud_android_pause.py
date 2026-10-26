"""Persona 331 (v3.10.1224): read-aloud must not be killed by the keep-alive pause/resume nudge. Pete (26/10, real Android phone): Ask AI read "Over the last 30 days ..., your HRV has been quite" and stopped mid-sentence. On Android pause() ends the speech silently. The fake engine here behaves that way: a pause() while speaking kills the utterance with no event. Also checks the Cook Mode style speak() (not a read-aloud button) still gets its nudge, and the button returns to its idle icon."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
FAKE = """
window.__spoken = []; window.__pauses = 0; window.__cur = null;
SpeechSynthesis.prototype.speak = function(u){ window.__spoken.push(u.text); const me = {u, dead:false}; window.__cur = me;
  setTimeout(() => { u.onstart && u.onstart({}); }, 30);
  setTimeout(() => { if (!me.dead) { window.__cur = null; u.onend && u.onend({}); } }, 30 + u.text.length * 70); };
SpeechSynthesis.prototype.cancel = function(){ if (window.__cur) window.__cur.dead = true; window.__cur = null; };
SpeechSynthesis.prototype.pause = function(){ window.__pauses++; if (window.__cur) window.__cur.dead = true; };
SpeechSynthesis.prototype.resume = function(){};
Object.defineProperty(SpeechSynthesis.prototype, 'speaking', {get(){return !!window.__cur}});
"""
with fresh_server() as root, sync_playwright() as pw:
    ctx = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block'); ctx.add_init_script(FAKE)
    page = ctx.new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("startDemoMode('alex')"); page.wait_for_timeout(2000)
    txt = ("Over the last 30 days (roughly 27 September to 26 October 2026), your HRV has been quite variable and generally on the lower end. "
           "Looking at the actual readings in the data: you started the period with some relatively stronger values, 38ms on 27 September and 40ms on 29 September, but those higher readings did not persist. "
           "Through most of October the numbers have sat in the mid-to-upper 20s and low 30s, with several days at 24 to 28ms. Your most recent readings cluster around 28 to 35ms.")
    ev("window.__b = document.createElement('span'); document.body.appendChild(window.__b); toggleSpeakText(window.__b, %r); 0" % txt)
    page.wait_for_timeout(2000)
    mid = ev("window.__b.textContent")
    if mid != '⏹': f.add('BUG', f'button shows stop while reading, got {mid!r}')
    page.wait_for_timeout(50000)
    allt = ev("window.__spoken.join(' ')")
    if ev("window.__pauses") > 0: f.add('BUG', f"read-aloud was paused/resumed {ev('window.__pauses')} time(s): on Android that ends the speech")
    if 'Your most recent readings' not in allt: f.add('BUG', f'the whole answer is read to the end, got: ...{allt[-80:]}')
    if ev("window.__b.textContent") != '🔊': f.add('BUG', 'the speaker button returns to idle when finished')
    # neighbour: a plain speak() (Cook Mode narration) still gets the nudge
    ev("window.__pauses = 0; speechSynthesis.speak(new SpeechSynthesisUtterance('x'.repeat(220))); 0"); page.wait_for_timeout(10500)
    if ev("window.__pauses") < 1: f.add('BUG', 'Cook Mode style narration lost its keep-alive nudge')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
