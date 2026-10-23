"""Persona 285: the clear ✕ sits inside the search box, which fits its row and does not cover the Add button (v3.10.1182). Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("switchTabById('shop')"); page.wait_for_timeout(500)
    for id_ in ['mhShopOwn']:
        r = ev("(()=>{const i=document.getElementById('mhShopOwn'),b=i.parentNode.parentNode.querySelector('button.copy-btn,button');const a=i.getBoundingClientRect(),c=b?b.getBoundingClientRect():null;return {ir:a.right,bl:c?c.left:null,w:a.width}})()")
        if r['bl'] is not None and r['ir'] > r['bl'] + 1: f.add('BUG', f'the box covers the Add button: {r}')
        if r['w'] < 150: f.add('BUG', f'the box is a sensible width: {r}')
    # one look everywhere: same size, border and radius as the Log box's clear
    std = ev("(()=>{const l=document.querySelector('span[onclick=\"clearChatInput()\"]');const c=getComputedStyle(l);return {w:c.width,b:c.borderTopWidth,r:c.borderTopLeftRadius,fs:c.fontSize}})()")
    for id_ in ['mhShopOwn']:
        got = ev("(()=>{const x=document.querySelector('[data-clear-for=%s]');const c=getComputedStyle(x);return {w:c.width,b:c.borderTopWidth,r:c.borderTopLeftRadius,fs:c.fontSize}})()" % id_)
        if got != std: f.add('BUG', f'{id_} clear looks like the Log one: {got} vs {std}')
    page.fill('#mhShopOwn', 'abc')
    vis = ev("(()=>{const x=document.querySelector('[data-clear-for=mhShopOwn]');if(!x)return null;const r=x.getBoundingClientRect(),i=document.getElementById('mhShopOwn').getBoundingClientRect();return {shown:getComputedStyle(x).display!=='none',inside:r.left>=i.left&&r.left<=i.left+10&&r.right<=i.right,st:getComputedStyle(x),w:r.width,h:r.height}})()")
    if not vis or not vis['shown'] or not vis['inside']: f.add('BUG', f'a ✕ shows inside the box once text is typed: {vis}')
    page.click('[data-clear-for=mhShopOwn]'); page.wait_for_timeout(200)
    if ev("document.getElementById('mhShopOwn').value") != '': f.add('BUG', 'tapping ✕ clears the text')
    if ev("document.documentElement.scrollWidth > window.innerWidth + 1"): f.add('BUG', 'the page does not scroll sideways')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
