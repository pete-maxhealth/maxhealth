"""Shared recorder for the demo clips (19 Nov 2026). run_clip(name, lines, steps, url, setup=None):
 lines = narration (Alba, Piper en_GB-alba-medium); steps = one function(h) per line, h has .page .tap .smooth .wait.
 Output /home/claude/voice/clip/out_<name>/c_<name>.mp4 (1080x1920). Sample data only (demo persona in url)."""
import sys, re, time, wave, os, json, subprocess, glob
sys.path.insert(0, '/home/claude/maxhealth/tests/personas')
from harness import fresh_server
from playwright.sync_api import sync_playwright
from piper import PiperVoice
RING = """(xy)=>{const d=document.createElement('div');d.style.cssText='position:fixed;z-index:99999;pointer-events:none;width:46px;height:46px;border-radius:50%;border:4px solid #0ea875;background:rgba(14,168,117,.25);left:'+(xy[0]-23)+'px;top:'+(xy[1]-23)+'px;transition:all .45s ease-out;opacity:1';document.body.appendChild(d);requestAnimationFrame(()=>{d.style.transform='scale(1.7)';d.style.opacity='0'});setTimeout(()=>d.remove(),600)}"""
class H: pass
def run_clip(name, lines, steps, url, setup=None, viewport=(540, 960)):
    assert len(lines) == len(steps)
    OUT = f'/home/claude/voice/clip/out_{name}'; os.makedirs(OUT, exist_ok=True)
    voice = PiperVoice.load('/home/claude/voice/en_GB-alba-medium.onnx'); segs = []
    for i, t in enumerate(lines):
        p = f'{OUT}/n{i}.wav'
        with wave.open(p, 'wb') as w: voice.synthesize_wav(t, w)
        with wave.open(p) as w: segs.append((p, w.getnframes() / w.getframerate()))
    with fresh_server() as root, sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={'width': viewport[0], 'height': viewport[1]}, service_workers='block', record_video_dir=f'{OUT}/vid', record_video_size={'width': viewport[0], 'height': viewport[1]})
        ctx.add_init_script("Object.defineProperty(navigator,'onLine',{get:()=>true})")
        t0 = time.time(); page = ctx.new_page()
        ctx.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.fulfill(status=200, content_type='application/json', body='{"products":[],"count":0}'))
        h = H(); h.page = page; starts = []
        def tap(sel, pause=0.5):
            el = page.locator(sel).first; el.scroll_into_view_if_needed(); b = el.bounding_box()
            page.evaluate(RING, [b['x'] + b['width'] / 2, b['y'] + b['height'] / 2]); page.wait_for_timeout(350); el.click(); page.wait_for_timeout(int(pause * 1000))
        def smooth(sel, block='start'):
            page.evaluate(f"document.querySelector('{sel}').scrollIntoView({{behavior:'smooth',block:'{block}'}})"); page.wait_for_timeout(1400)
        h.tap = tap; h.smooth = smooth; h.wait = lambda s: page.wait_for_timeout(int(s * 1000))
        page.goto(url); page.wait_for_timeout(3500)
        page.evaluate("var o=document.getElementById('onboardingOverlay'); if(o) o.style.display='none'")
        if setup: setup(h)
        for i, st in enumerate(steps):
            starts.append(time.time() - t0); st(h)
            left = segs[i][1] + 0.5 - (time.time() - t0 - starts[-1])
            if left > 0: page.wait_for_timeout(int(left * 1000))
        page.wait_for_timeout(600); ctx.close(); br.close()
    vid = sorted(glob.glob(f'{OUT}/vid/*.webm'), key=os.path.getmtime)[-1]
    cmd = ['ffmpeg', '-y', '-i', vid] + sum([['-i', s[0]] for s in segs], [])
    fc = ''.join(f'[{i+1}:a]adelay={int(starts[i]*1000)}|{int(starts[i]*1000)}[a{i}];' for i in range(len(segs)))
    fc += ''.join(f'[a{i}]' for i in range(len(segs))) + f'amix=inputs={len(segs)}:normalize=0,loudnorm=I=-16:TP=-1.5[aout];[0:v]scale={min(viewport[0]*2,1920)}:{min(viewport[0]*2,1920)*viewport[1]//viewport[0]//2*2}:flags=lanczos[vout]'
    subprocess.run(cmd + ['-filter_complex', fc, '-map', '[vout]', '-map', '[aout]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-shortest', f'{OUT}/c_{name}.mp4'], check=True, capture_output=True)
    print('DONE', f'{OUT}/c_{name}.mp4', [round(s, 1) for s in starts])
def sheet(name, times):
    OUT = f'/home/claude/voice/clip/out_{name}'
    for t in times: subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(t), '-i', f'{OUT}/c_{name}.mp4', '-frames:v', '1', '-vf', 'scale=270:480', f'{OUT}/s{t}.png'])
    subprocess.run(['ffmpeg', '-y', '-v', 'error'] + sum([['-i', f'{OUT}/s{t}.png'] for t in times], []) + ['-filter_complex', f'hstack=inputs={len(times)}', f'{OUT}/sheet.png'])
