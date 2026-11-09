"""Persona 437: the suggested-fix box in the meal preview is laid out properly on a phone: the text is a readable line, the Apply button is its own size and never covers the text (v3.10.1335).
Pete (9 Nov 2026, screenshot): "Format issue" - the text ran one word per line and Apply stretched across it. Cause: .copy-btn is width:100%. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/p437_%s.png'
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 360, 'height': 800}, service_workers='block', device_scale_factor=2).new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = page.evaluate
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200)
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'"); ev("switchTab('log', document.getElementById('maintab-log')); switchSubTab('log','log', document.getElementById('logtab-log'))"); page.wait_for_timeout(600)
    LAY = """(()=>{const box=document.querySelector('#previewFixes'); if(!box) return null; const row=box.querySelector('button').parentElement, sp=row.querySelector('span'), bt=box.querySelector('button');
      const r=e=>e.getBoundingClientRect(), a=r(sp), b=r(bt), bx=r(box);
      const lines=Math.round(a.height/parseFloat(getComputedStyle(sp).lineHeight||18));
      return {textW:Math.round(a.width), textH:Math.round(a.height), btnW:Math.round(b.width), boxW:Math.round(bx.width), boxH:Math.round(bx.height), overlap: !(b.right<=a.left||b.left>=a.right||b.bottom<=a.top||b.top>=a.bottom), inside: b.left>=bx.left-1&&b.right<=bx.right+1&&b.bottom<=bx.bottom+1}})()"""
    # Pete's case: whey protein 25g with per-100g figures; also two foods flagged at once
    for name, foods in [('one', "[{name:'Banana Diet Whey Protein (Applied Nutrition)', amount:'25g', kcal:100, protein:20, fat:2, carbs:1.2, _source:'ai'}]"),
                        ('two', "[{name:'Banana Diet Whey Protein (Applied Nutrition)', amount:'25g', kcal:100, protein:20, fat:2, carbs:1.2, _source:'ai'},{name:'Double cream', amount:'100g', kcal:60, protein:2, fat:5, carbs:3, _source:'ai'}]")]:
        ev(f"window._pendingMealFoods={foods}; renderMealPreview()"); page.wait_for_timeout(400)
        L = ev(LAY)
        if not L: f.add('BUG', f'{name}: no suggestion box shown'); continue
        if L['textW'] < 150: f.add('BUG', f'{name}: the text is squeezed to {L["textW"]}px wide: {L}')
        if L['btnW'] > 140: f.add('BUG', f'{name}: Apply is stretched to {L["btnW"]}px: {L}')
        if L['overlap']: f.add('BUG', f'{name}: Apply covers the text: {L}')
        if not L['inside']: f.add('BUG', f'{name}: Apply sticks out of the box: {L}')
        if L['boxH'] > 260 * (2 if name == 'two' else 1): f.add('BUG', f'{name}: the box is {L["boxH"]}px tall, far too much for a couple of lines: {L}')
        page.locator('#previewFixes').scroll_into_view_if_needed(); page.locator('#previewFixes').screenshot(path=SHOT % (name + '_dark'))
    ev("document.documentElement.setAttribute('data-theme','light')"); page.wait_for_timeout(300); page.locator('#previewFixes').screenshot(path=SHOT % 'two_light')
    # Apply still works from the new layout
    ev("document.documentElement.removeAttribute('data-theme')")
    page.locator('#previewFixes button').first.click(); page.wait_for_timeout(300)
    if ev("window._pendingMealFoods[0].protein") != 5: f.add('BUG', f'Apply still scales the whey to 25g: {ev("window._pendingMealFoods[0].protein")}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f]; sys.exit(1 if f else 0)
