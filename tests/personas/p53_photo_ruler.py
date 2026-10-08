"""Persona 53: photo ruler in Settings > Tableware: card-calibrated measurement lands in the item's Across (cm) box."""
import sys, re; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
import tempfile, os
from PIL import Image, ImageDraw
# 1100x900: card long edge 342px = 85.6mm (4 px/mm); bowl 600px across = 15.0cm
IMG = os.path.join(tempfile.mkdtemp(), 'ruler.png')
_im = Image.new('RGB', (1100, 900), (120, 100, 80)); _d = ImageDraw.Draw(_im)
_d.rectangle([100, 100, 442, 316], fill=(30, 60, 160)); _d.ellipse([350, 200, 950, 800], fill=(240, 240, 240)); _im.save(IMG)
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); errs = []
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route(re.compile(r'https://(cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|fonts\.(googleapis|gstatic)\.com)/.*'), lambda r: r.abort())
    page = ctx.new_page(); page.on('pageerror', lambda e: errs.append(str(e)[:160]))
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1500)
    # pure maths
    if page.evaluate("mhRulerCalc(342, 85.6, 600)") != 15.0: f.add('BUG', 'calc wrong')
    if page.evaluate("mhRulerCalc(0, 85.6, 600)") is not None or page.evaluate("mhRulerCalc(342, 0, 600)") is not None: f.add('BUG', 'calc accepted bad input')
    page.evaluate("switchTabById('settings')"); page.wait_for_timeout(500)
    page.evaluate("mhTwRender()")
    if page.evaluate("document.querySelectorAll('#mhTwCard [onclick^=\"mhRulerOpen\"]').length") != 8: f.add('BUG', '📏 should sit on every tableware item')
    page.evaluate("mhRulerOpen('home','bowl')")
    page.set_input_files('#mhRulerModal input[type=file]', IMG); page.wait_for_selector('#mhRulerCanvas', timeout=5000)
    def tap(x, y):
        box = page.evaluate("(()=>{const r=document.getElementById('mhRulerCanvas').getBoundingClientRect();return [r.left,r.top,r.width,r.height]})()")
        page.mouse.click(box[0] + x * box[2] / 1100, box[1] + y * box[3] / 900); page.wait_for_timeout(80)
    if 'Step 1 of 2' not in page.evaluate("document.getElementById('mhRulerBody').textContent"): f.add('BUG', 'no readable step hint before reference is set')
    if page.evaluate("[...document.querySelectorAll('#mhRulerBody button')].some(b => b.textContent.includes('Next') && getComputedStyle(b).opacity < 1)"): f.add('BUG', 'faded Next button')
    tap(100, 208); tap(442, 208)                    # card long edge
    page.evaluate("mhRulerNext()")
    tap(350, 500); tap(950, 500)                    # across the bowl
    txt = page.evaluate("document.getElementById('mhRulerBody').textContent")
    m = re.search(r'([\d.]+) cm across', txt)
    if not m or abs(float(m.group(1)) - 15.0) > 0.4: f.add('BUG', f'measured {m and m.group(1)} cm, expected ~15.0')
    page.evaluate("mhRulerUse()"); page.wait_for_timeout(300)
    v = page.evaluate("JSON.parse(localStorage.getItem('mh_tableware')).sets[0].vals.bowl")
    if not v or abs(v.get('diam', 0) - 15.0) > 0.4 or v.get('diam') == 15 and False: pass
    if page.evaluate("!!document.getElementById('mhRulerModal')"): f.add('BUG', 'modal stayed open after Use')
    # default bowl is 15 so equal-to-default removes the override; measure something different to prove the write
    page.evaluate("mhRulerOpen('home','dinner_plate')")
    page.set_input_files('#mhRulerModal input[type=file]', IMG); page.wait_for_selector('#mhRulerCanvas', timeout=5000)
    tap(100, 208); tap(442, 208); page.evaluate("mhRulerNext()"); tap(350, 500); tap(800, 500)
    page.evaluate("mhRulerUse()"); page.wait_for_timeout(300)
    d = page.evaluate("(JSON.parse(localStorage.getItem('mh_tableware')).sets[0].vals.dinner_plate||{}).diam")
    if not d or abs(d - 11.2) > 0.4: f.add('BUG', f'plate diam not saved from ruler: {d}')
    # a smaller card: type its length and it is remembered
    page.evaluate("mhRulerOpen('home','mug')")
    page.set_input_files('#mhRulerModal input[type=file]', IMG); page.wait_for_selector('#mhRulerCanvas', timeout=5000)
    page.evaluate("mhRulerRef('custom'); mhRulerCustom('64')")
    page.evaluate("mhRulerClose(); mhRulerOpen('home','mug')")
    if page.evaluate("JSON.parse(localStorage.getItem('mh_ruler_ref')).customMm") != 64: f.add('BUG', 'typed reference length not remembered')
    page.evaluate("mhRulerClose()")
    # absurd result is refused
    page.evaluate("localStorage.removeItem('mh_ruler_ref'); mhRulerOpen('home','dinner_plate')")
    page.set_input_files('#mhRulerModal input[type=file]', IMG); page.wait_for_selector('#mhRulerCanvas', timeout=5000)
    tap(100, 208); tap(110, 208); page.evaluate("mhRulerNext()"); tap(100, 500); tap(1000, 500); page.evaluate("mhRulerUse()")
    if not page.evaluate("!!document.getElementById('mhRulerModal')"): f.add('BUG', 'absurd measurement (>60cm) was accepted')
    if errs: f.add('BUG', f'page errors: {errs[:3]}')
    b.close()
print("findings", len(f)); sys.exit(1 if f else 0)
