"""Clip: log a meal by voice. Doris demo persona (sample data only). Alba narrates; Alan is the person speaking to the app (mixed at 68% of Alba).
The browser here has no microphone, so a stand-in speech recogniser hands the app the exact words Alan says, at the moment he says them (see FAKE_SR)."""
import sys, re, time, wave, os, json
sys.path.insert(0, '/home/claude/maxhealth/tests/personas')
from harness import fresh_server
from playwright.sync_api import sync_playwright
from piper import PiperVoice
V = {'alba': PiperVoice.load('/home/claude/voice/en_GB-alba-medium.onnx'), 'alan': PiperVoice.load('/home/claude/voice/en_GB-alan-medium.onnx')}
OUT = '/home/claude/voice/clip/out2'; os.makedirs(OUT, exist_ok=True)
FAKE_SR = """
Object.defineProperty(navigator,'onLine',{get:()=>true});
window.SpeechRecognition = window.webkitSpeechRecognition = class { constructor(){ window.__sr = this; this.lang='en-GB'; }
  start(){ setTimeout(()=>this.onstart && this.onstart(), 50); } stop(){ setTimeout(()=>this.onend && this.onend(), 20); } abort(){} };
window.__say = (t)=>{ const r=[{transcript:t}]; r.isFinal=true; window.__sr.onresult({resultIndex:0, results:[r]}); };
"""
RING = """(xy)=>{const d=document.createElement('div');d.style.cssText='position:fixed;z-index:99999;pointer-events:none;width:46px;height:46px;border-radius:50%;border:4px solid #0ea875;background:rgba(14,168,117,.25);left:'+(xy[0]-23)+'px;top:'+(xy[1]-23)+'px;transition:all .45s ease-out;opacity:1';document.body.appendChild(d);requestAnimationFrame(()=>{d.style.transform='scale(1.7)';d.style.opacity='0'});setTimeout(()=>d.remove(),600)}"""
events = []
with fresh_server() as root, sync_playwright() as pw:
    print('pw ok',flush=True); br = pw.chromium.launch(); print('launched',flush=True)
    ctx = br.new_context(viewport={'width': 540, 'height': 960}, service_workers='block', record_video_dir=f'{OUT}/vid', record_video_size={'width': 540, 'height': 960})
    ctx.add_init_script(FAKE_SR)
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.fulfill(status=200, content_type='application/json', body='{"products":[],"count":0}'))
    print('ctx ok',flush=True); t0 = time.time(); page = ctx.new_page(); print('page ok',flush=True)
    def speak(voice, text):
        i = len(events); p = f'{OUT}/v{i}.wav'
        with wave.open(p, 'wb') as w: V[voice].synthesize_wav(text, w)
        with wave.open(p) as w: d = w.getnframes() / w.getframerate()
        events.append({'file': p, 'start': time.time() - t0, 'voice': voice, 'dur': d}); return d
    def wait(s): page.wait_for_timeout(int(s * 1000))
    def tap(sel, pause=0.5):
        el = page.locator(sel).first; el.scroll_into_view_if_needed(); b = el.bounding_box()
        page.evaluate(RING, [b['x'] + b['width'] / 2, b['y'] + b['height'] / 2]); wait(0.35); el.click(); wait(pause)
    page.set_default_timeout(15000); page.goto('http://localhost:5757/?demo=doris', wait_until='domcontentloaded'); wait(3.5); print('loaded',flush=True)
    d = speak('alba', "Doris would rather talk than type. So she taps the microphone, and just says what she ate."); wait(1.2)
    tap('#maintab-log', 0.8); tap('#voiceBtn', 0.8); wait(max(0, d - 3.4) + 0.5)
    for words in ["2 eggs", "a slice of toast"]:
        d = speak('alan', words); wait(d + 0.3); page.evaluate("t=>window.__say(t)", words); wait(1.4)
    d = speak('alan', "done"); wait(d + 0.3); page.evaluate("t=>window.__say(t)", "done"); wait(1.0)
    d = speak('alba', "The app matches each item to her own library and shows her day before and after. Nothing is logged until she says so."); wait(2.5)
    page.evaluate("document.getElementById('mealPreviewBubble')?.scrollIntoView({block:'start'})"); wait(d - 2.0)
    print('PREVIEW', page.evaluate("(document.getElementById('mealPreviewBubble')||{innerText:''}).innerText.replace(/\\n/g,' ').slice(0,260)"))
    tap('button:has-text("LOG IT")', 1.0)
    tap('#maintab-today', 0.8)
    try: page.locator('text=/Egg/').first.scroll_into_view_if_needed(timeout=3000); wait(0.8)
    except Exception as e: print('noscroll')
    print('LOGGED', page.evaluate("JSON.stringify((state.todayLog||[]).map(e=>[e.name||e.description,e.kcal]))"))
    d = speak('alba', "She can also say things like hide the water card. New foods come from a barcode, a label photo or an AI search, so typing numbers is a last resort. Sample data shown. Not medical advice."); wait(d + 0.8)
    ctx.close(); br.close()
json.dump(events, open(f'{OUT}/events.json', 'w'))
for e in events: print(round(e['start'], 1), e['voice'], round(e['dur'], 1))
