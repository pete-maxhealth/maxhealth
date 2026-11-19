"""Clip: choosing what a carer, coach or clinician sees (Settings > Carer & Clinician): role chips, tick items, make link, preview. Sam demo persona (sample data only). Alba narration. Output: /home/claude/voice/clip/out_carer/c_carer_view.mp4"""
import sys, re, time, wave, os, json, subprocess, glob
sys.path.insert(0, '/home/claude/maxhealth/tests/personas')
from harness import fresh_server
from playwright.sync_api import sync_playwright
from piper import PiperVoice
OUT = '/home/claude/voice/clip/out_carer'; os.makedirs(OUT, exist_ok=True)
VOICE = PiperVoice.load('/home/claude/voice/en_GB-alba-medium.onnx')
def say(i, text):
    p = f'{OUT}/n{i}.wav'
    with wave.open(p, 'wb') as w: VOICE.synthesize_wav(text, w)
    with wave.open(p) as w: return p, w.getnframes() / w.getframerate()
LINES = [
 "Sam wants his coach to see how he is eating, without sharing everything. Open Settings, then Carer and Clinician.",
 "Tap who the link is for, and MaxedHealth starts from a sensible set. A coach gets his grams by time of day, but not his food names.",
 "Then switch anything on or off yourself. Weight, exercise and sleep are one tap each.",
 "Make the link. Nothing leaves his phone until he sends it himself.",
 "Preview shows exactly what they will see, so there are no surprises.",
 "The link lasts seven days. Sample data shown. Not medical advice.",
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
    def seg(i, action=None):
        starts.append(time.time() - t0)
        if action: action()
        left = segs[i][1] + 0.5 - (time.time() - t0 - starts[-1])
        if left > 0: page.wait_for_timeout(int(left * 1000))
    def tap(sel, pause=0.5):
        el = page.locator(sel).first; el.scroll_into_view_if_needed(); b = el.bounding_box()
        page.evaluate(RING, [b['x'] + b['width'] / 2, b['y'] + b['height'] / 2]); page.wait_for_timeout(350); el.click(); page.wait_for_timeout(int(pause * 1000))
    def smooth(sel, block='start'):
        page.evaluate(f"document.querySelector('{sel}').scrollIntoView({{behavior:'smooth',block:'{block}'}})"); page.wait_for_timeout(1400)
    page.goto('http://localhost:5757/?demo=sam'); page.wait_for_timeout(3500)
    page.evaluate("var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'")
    page.click('#maintab-settings'); page.wait_for_timeout(800); page.click('#settingstab-manage'); page.wait_for_timeout(800)
    page.evaluate("var w=document.getElementById('set-carer-wrap'); if(w.style.display==='none') toggleSection('set-carer','set-carer-wrap','set-carer-icon')")
    page.evaluate("window.scrollTo(0,0); document.querySelectorAll('.view, #view-manage').forEach(e=>e.scrollTop=0)")
    seg(0, lambda: (page.wait_for_timeout(500), smooth('#title-set-carer'), page.wait_for_timeout(800)))
    seg(1, lambda: tap('#shareRoles >> text=PT or coach', 1.2))
    seg(2, lambda: (tap('#shareItems >> text=Sleep', 0.9), tap('#shareItems >> text=Weight', 0.9), tap('#shareItems >> text=Weight', 0.9)))
    seg(3, lambda: tap('button:has-text("GENERATE CARER VIEW LINK")', 1.5))
    seg(4, lambda: tap('#carerPreviewBtn', 3.5))
    seg(5)
    page.wait_for_timeout(600)
    ctx.close(); br.close()
json.dump({'starts': starts, 'durs': [s[1] for s in segs]}, open(f'{OUT}/timing.json', 'w'))
vid = sorted(glob.glob(f'{OUT}/vid/*.webm'), key=os.path.getmtime)[-1]
cmd = ['ffmpeg', '-y', '-i', vid] + sum([['-i', segs[i][0]] for i in range(len(segs))], [])
fc = ''.join(f'[{i+1}:a]adelay={int(starts[i]*1000)}|{int(starts[i]*1000)}[a{i}];' for i in range(len(segs)))
fc += ''.join(f'[a{i}]' for i in range(len(segs))) + f'amix=inputs={len(segs)}:normalize=0,loudnorm=I=-16:TP=-1.5[aout];[0:v]scale=1080:1920:flags=lanczos[vout]'
subprocess.run(cmd + ['-filter_complex', fc, '-map', '[vout]', '-map', '[aout]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-shortest', f'{OUT}/c_carer_view.mp4'], check=True, capture_output=True)
print('DONE', starts)
