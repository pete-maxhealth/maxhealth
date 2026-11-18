"""Clip: log a meal by typing the start of a name and picking from the library. Doris demo persona (sample data only). Alba narration (Piper en_GB-alba-medium)."""
import sys, re, time, wave, os, json, subprocess, glob
sys.path.insert(0, '/home/claude/maxhealth/tests/personas')
from harness import fresh_server
from playwright.sync_api import sync_playwright
from piper import PiperVoice
OUT = '/home/claude/voice/clip/out'; os.makedirs(OUT, exist_ok=True)
VOICE = PiperVoice.load('/home/claude/voice/en_GB-alba-medium.onnx')
def say(i, text):
    p = f'{OUT}/n{i}.wav'
    with wave.open(p, 'wb') as w: VOICE.synthesize_wav(text, w)
    with wave.open(p) as w: return p, w.getnframes() / w.getframerate()
LINES = [
 "This is Doris. She is about to log her lunch, and she will not type a single number.",
 "Tap Log, then tap the magnifier.",
 "Type just the start of a name. Three letters is enough, and her own library answers first.",
 "Pick the food, then tap a portion. The calories and macros come from her library, not from guesswork.",
 "Tap Log, and it lands on today's page, with her totals updated.",
 "New foods get into the library from a barcode, a label photo or an AI search, so typing numbers is a last resort. Sample data shown. Not medical advice.",
]
segs = [say(i, t) for i, t in enumerate(LINES)]
RING = """(xy)=>{const d=document.createElement('div');d.style.cssText='position:fixed;z-index:99999;pointer-events:none;width:46px;height:46px;border-radius:50%;border:4px solid #0ea875;background:rgba(14,168,117,.25);left:'+(xy[0]-23)+'px;top:'+(xy[1]-23)+'px;transition:all .45s ease-out;opacity:1';document.body.appendChild(d);requestAnimationFrame(()=>{d.style.transform='scale(1.7)';d.style.opacity='0'});setTimeout(()=>d.remove(),600)}"""
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch()
    ctx = br.new_context(viewport={'width': 540, 'height': 960}, service_workers='block', record_video_dir=f'{OUT}/vid', record_video_size={'width': 540, 'height': 960})
    ctx.add_init_script("Object.defineProperty(navigator,'onLine',{get:()=>true})")
    t0 = time.time(); page = ctx.new_page()
    ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.fulfill(status=200, content_type='application/json', body='{"products":[],"count":0}'))
    starts = []
    def seg(i, action=None, min_after=0.4):
        starts.append(time.time() - t0)
        if action: action()
        left = segs[i][1] + 0.5 - (time.time() - t0 - starts[-1])
        if left > 0: page.wait_for_timeout(int(left * 1000))
    def tap(sel, pause=0.5):
        el = page.locator(sel).first; el.scroll_into_view_if_needed(); b = el.bounding_box()
        page.evaluate(RING, [b['x'] + b['width'] / 2, b['y'] + b['height'] / 2]); page.wait_for_timeout(350); el.click(); page.wait_for_timeout(int(pause * 1000))
    page.goto('http://localhost:5757/?demo=doris'); page.wait_for_timeout(3500)
    seg(0)
    seg(1, lambda: (tap('#maintab-log', 1.0), tap('#searchBtn', 0.8)))
    seg(2, lambda: (page.wait_for_timeout(900), page.type('#foodSearchInput', 'pep', delay=450), page.wait_for_timeout(600)))
    seg(3, lambda: (tap('#foodSearchPanel >> text=Peppers', 1.0), tap('button:has-text("150g")', 0.9)))
    def log_it():
        tap('button:has-text("LOG →")', 1.2); page.evaluate("document.getElementById('foodSearchOverlay') && closeFoodSearch && closeFoodSearch()") if False else None
        tap('#maintab-today', 0.8)
        print('LOGGED', page.evaluate("JSON.stringify((state.todayLog||[]).map(e=>[e.name||e.description,e.kcal]))"))
        try:
            el = page.locator('text=Peppers').first; el.scroll_into_view_if_needed(timeout=3000); page.wait_for_timeout(800)
        except Exception as e: print('no scroll', str(e)[:80])
    seg(4, log_it)
    seg(5)
    page.wait_for_timeout(600)
    ctx.close(); br.close()
json.dump({'starts': starts, 'durs': [s[1] for s in segs]}, open(f'{OUT}/timing.json', 'w'))
print(starts)
