#!/usr/bin/env python3
"""Builds start/*.html (one start page per goal, plus start/index.html) from start/pages.json.
Each page: the person's problem, one demo persona (opens the app's demo), an optional video link, a QR code that opens the app set up for that goal,
and the install steps. The QR is drawn with the app's own encoder (MHQR in maxhealth.html), so nothing is downloaded.
Usage: python3 tools/build_start_pages.py    (run from the repo root; set "video" in start/pages.json to a YouTube link and rerun)"""
import json, os, re, subprocess, html, tempfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(R, 'start', 'pages.json'), encoding='utf-8')); BASE = cfg['base']
src = open(os.path.join(R, 'maxhealth.html'), encoding='utf-8').read().split('\n')
a = next(i for i, l in enumerate(src) if l.startswith('(function (root) {') and any('MHQR' in x for x in src[i:i+170]))
b = next(i for i in range(a, a + 200) if src[i].startswith("  if (typeof module !== 'undefined') module.exports = root.MHQR;"))
js = '\n'.join(src[a:b + 2])
def qr_svg(url):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as t:
        t.write('const root = globalThis; ' + js.replace("})(typeof window !== 'undefined' ? window : globalThis);", "})(globalThis);") + f"\nconst q = globalThis.MHQR.encodeText({json.dumps(url)}); console.log(JSON.stringify({{n: q.size, m: q.modules.map(r => r.map(c => c ? 1 : 0).join(''))}}));")
    out = subprocess.check_output(['node', t.name], text=True); os.unlink(t.name); d = json.loads(out); n = d['n']; q = 4
    path = ''.join(f'M{x + q} {y + q}h1v1h-1z' for y, row in enumerate(d['m']) for x, c in enumerate(row) if c == '1')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n + 2 * q} {n + 2 * q}" role="img" aria-label="QR code that opens MaxedHealth on your phone" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fff"/><path d="{path}" fill="#000"/></svg>'
E_ = html.escape
CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#080a0d;--surface:#0f1318;--surface2:#161b22;--border:rgba(255,255,255,.1);--text:#f0f2f7;--text2:#a8b0c0;--text3:#7a8298;--accent:#2deb8f;--accent-dim:rgba(45,235,143,.1)}
@media (prefers-color-scheme: light){:root{--bg:#f6f8fa;--surface:#fff;--surface2:#eef1f5;--border:rgba(0,0,0,.12);--text:#14181f;--text2:#3d4655;--text3:#5b6577;--accent:#0a8f55;--accent-dim:rgba(10,143,85,.1)}}
html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:0 max(18px,env(safe-area-inset-left)) 40px max(18px,env(safe-area-inset-right))}
.wrap{max-width:720px;margin:0 auto}
nav{display:flex;justify-content:space-between;align-items:center;padding:18px 0;border-bottom:1px solid var(--border);margin-bottom:28px;font-family:'Space Mono',ui-monospace,monospace;font-size:12px}
nav a{color:var(--text2);text-decoration:none}nav .logo{color:var(--accent);font-weight:700;letter-spacing:.08em}
h1{font-size:clamp(28px,7vw,42px);line-height:1.15;letter-spacing:-.02em;margin-bottom:14px;text-wrap:balance}
.lead{color:var(--text2);font-size:18px;margin-bottom:24px}
.btn{display:inline-block;background:var(--accent);color:#06130c;font:700 14px 'Space Mono',ui-monospace,monospace;padding:14px 24px;border-radius:8px;text-decoration:none;letter-spacing:.03em}
.btn.alt{background:var(--surface2);color:var(--text);border:1px solid var(--border)}
.row{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin:18px 0}
.card h2{font-size:13px;font-family:'Space Mono',ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:10px;font-weight:700}
ul{padding-left:20px}li{margin:8px 0;color:var(--text2)}
ol{padding-left:22px}ol li{margin:10px 0}
.who{color:var(--text2);margin-bottom:14px}
.ondesk{display:none}.qrbox{display:none;align-items:center;gap:20px;margin-top:14px}
.qrbox svg{width:180px;height:180px;border-radius:8px;flex:0 0 auto}
@media (min-width:700px){.qrbox{display:flex}.ondesk{display:list-item}.onphone{display:none}}
.small{font-size:13px;color:var(--text3);margin-top:22px;line-height:1.6}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:22px 0}
.tile{display:block;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px 18px;text-decoration:none;color:var(--text)}
.tile:hover{border-color:var(--accent)}.tile b{display:block;margin-bottom:4px}.tile span{color:var(--text2);font-size:14px}
.video{position:relative;padding-top:56.25%;margin:18px 0;border-radius:12px;overflow:hidden;background:#000}.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}"""
HEAD = lambda t, d, canon: f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{E_(t)}</title><meta name="description" content="{E_(d)}"><meta property="og:title" content="{E_(t)}"><meta property="og:description" content="{E_(d)}"><meta property="og:type" content="website"><link rel="canonical" href="{canon}"><style>{CSS}</style></head><body><div class="wrap"><nav><a class="logo" href="../index.html">MAXEDHEALTH</a><a href="index.html">All starting points</a></nav>'
NOTE = '<p class="small">Free, with no account and no ads. Your data stays on your phone. MaxedHealth gives sourced, labelled information; it is not a medical device and does not diagnose or treat anything. Talk to your doctor before changing your treatment. <a href="../docs/legal.html#privacy" style="color:inherit">Privacy</a></p>'
def video_html(u):
    m = re.search(r'(?:youtu\.be/|youtube\.com/(?:shorts/|watch\?v=|embed/))([\w-]{11})', u or '')
    if not m: return ''
    return f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{m.group(1)}" title="Video" loading="lazy" allow="accelerometer; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>'
os.makedirs(os.path.join(R, 'start'), exist_ok=True)
for p in cfg['pages']:
    app = f"{BASE}maxhealth.html?start={p['start']}"; demo = f"../maxhealth.html?demo={p['demo']}"
    pts = ''.join(f'<li>{E_(x)}</li>' for x in p['points'])
    page = HEAD(p['title'] + ' | MaxedHealth', p['lead'], f"{BASE}start/{p['slug']}.html") + f'''
<h1>{E_(p['title'])}</h1><p class="lead">{E_(p['lead'])}</p>
<div class="row"><a class="btn" href="../maxhealth.html?start={p['start']}">Open it on this phone</a><a class="btn alt" href="{demo}">Look around first</a></div>
{video_html(p.get('video'))}
<div class="card"><h2>What it does for you</h2><ul>{pts}</ul></div>
<div class="card"><h2>See it as someone like you</h2><p class="who">{E_(p['who'])} A made-up person with 30 days of sample data; nothing you do in the demo is saved.</p><a class="btn alt" href="{demo}">Open the demo</a></div>
<div class="card"><h2>Put it on your phone</h2>
<ol><li class="onphone">Tap <b>Open it on this phone</b> above.</li><li class="ondesk">Scan this code with your phone camera. It opens the app already set up for this goal.</li><li><b>Android (Chrome):</b> tap <b>Install app</b> when it appears, or use <b>Add to home screen</b> in Settings, About. <b>iPhone (Safari):</b> tap Share, then <b>Add to Home Screen</b>.</li><li>Answer a few questions and log your first meal. Nothing to sign up for.</li></ol>
<div class="qrbox">{qr_svg(app)}<p class="who">Scan with your phone camera.<br>Free. No account.</p></div></div>
{NOTE}</div></body></html>'''
    open(os.path.join(R, 'start', p['slug'] + '.html'), 'w', encoding='utf-8').write(page)
tiles = ''.join(f"<a class=\"tile\" href=\"{p['slug']}.html\"><b>{E_(p['title'])}</b><span>{E_(p['who'].split(',')[0])}'s story and a one-scan set-up</span></a>" for p in cfg['pages'])
idx = HEAD('Choose your starting point | MaxedHealth', 'Pick what you want help with and open MaxedHealth already set up for it. Free, no account.', f'{BASE}start/') + f'''
<h1>What do you want help with?</h1><p class="lead">Pick one. You can change it, add to it, or hide what you do not need at any time.</p>
<div class="tiles">{tiles}</div>
<p class="small">Something else, such as epilepsy, migraine or cancer care? <a href="../maxhealth.html" style="color:var(--accent)">Open the app</a>; setup asks what you want to track, and the demo people cover many conditions.</p>
{NOTE}</div></body></html>'''
open(os.path.join(R, 'start', 'index.html'), 'w', encoding='utf-8').write(idx)
# landing page tiles (between the START-TILES markers in index.html)
ip = os.path.join(R, 'index.html'); t = open(ip, encoding='utf-8').read()
short = {'lose': 'Lose weight', 'lowcarb': 'Keep carbs low', 'muscle': 'Build muscle', 't2d': 'Type 2 diabetes', 'simple': 'Just see how I am doing'}
tl = ''.join(f"<a href=\"start/{p['slug']}.html\">{E_(short.get(p['start'], p['title']))}<span>See it as {E_(p['who'].split(',')[0])}</span></a>" for p in cfg['pages'])
t = re.sub(r'<!-- START-TILES:START -->.*?<!-- START-TILES:END -->', lambda m: '<!-- START-TILES:START --><div class="goal-tiles">' + tl + '</div><!-- START-TILES:END -->', t, flags=re.S)
open(ip, 'w', encoding='utf-8').write(t)
print('built', len(cfg['pages']) + 1, 'pages')
