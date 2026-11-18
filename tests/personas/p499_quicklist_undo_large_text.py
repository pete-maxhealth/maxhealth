"""Persona 499 (v3.10.1419): Quick list taps (not this time, never, bring back) and deleting a saved list carry an Undo that puts things back exactly;
Needs details rows (single food and several) stay readable at large text: name never under the 'counted in' box, nothing wider than the screen. Invented data."""
import sys, re; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept()); page.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()"); page.wait_for_timeout(300)
    has_undo = lambda: ev("!!document.querySelector('#toast .toast-undo')")
    undo = lambda: (ev("document.querySelector('#toast .toast-undo').click()"), page.wait_for_timeout(400))
    st = lambda: ev("JSON.stringify([mhShopLoad().skip, mhShopLoad().never, mhShopLoad().usuals, mhShopListsLoad().lists])")
    # Quick list: not this time / never / bring back
    for name, call in (('not this time', "mhShopSuggestSkip('zzqx apple')"), ('never', "mhShopSuggestNever('zzqx pear')")):
        s0 = st(); ev(call); page.wait_for_timeout(300)
        if st() == s0: f.add('BUG', f'{name}: nothing changed'); continue
        if not has_undo(): f.add('BUG', f'{name}: no Undo in the toast'); continue
        undo()
        if st() != s0: f.add('BUG', f'{name}: Undo did not put it back')
    ev("mhShopSuggestNever('zzqx pear')"); page.wait_for_timeout(300); s1 = st()
    ev("mhShopSuggestRestore('zzqx pear')"); page.wait_for_timeout(300)
    if not has_undo(): f.add('BUG', 'bring back: no Undo')
    else:
        undo()
        if st() != s1: f.add('BUG', 'bring back: Undo did not put it back')
    # saved list delete
    ev("mhShopListsSave({lists:[{id:'zl1',name:'Zzqx weekly',items:[{name:'Zzqx Rice',qty:1}]}]})"); s2 = st()
    ev("mhShopListDelete('zl1')"); page.wait_for_timeout(300)
    try: page.click('#appModalConfirm', timeout=2000)
    except Exception: pass
    page.wait_for_timeout(400)
    if ev("mhShopListsLoad().lists.length") != 0: f.add('BUG', 'saved list was not deleted')
    elif not has_undo(): f.add('BUG', 'saved list delete: no Undo')
    else:
        undo()
        if st() != s2: f.add('BUG', 'saved list delete: Undo did not restore the list')
    # large text: Needs details rows
    ev("(()=>{['Zzqx Tomato','Zzqx A very long food name for a narrow screen'].forEach(n=>mhStockTrack(n,{base:'g',shop:'Asda'}));})()")
    ev("switchTabById('shop')"); ev("mhSlOpen()"); page.wait_for_timeout(400); ev("mhSlF('gaps')"); page.wait_for_timeout(400)
    ev("document.querySelectorAll('#mhSlRows *').forEach(e=>{e.style.fontSize=(parseFloat(getComputedStyle(e).fontSize)*2.3)+'px'})"); page.wait_for_timeout(300)
    bad = ev("""(()=>{const o=[];document.querySelectorAll('#mhSlRows [data-sl]').forEach(r=>{
      const sel=r.querySelector('select[data-f="unitset"],select[data-f="unit"]'), nm=sel&&sel.previousElementSibling; if(!nm||!sel){o.push('missing parts');return}
      if(nm.scrollWidth>nm.clientWidth+1) o.push('name text spills out of its box: '+r.dataset.n+' '+nm.scrollWidth+'>'+nm.clientWidth); const a=nm.getBoundingClientRect(), b=sel.getBoundingClientRect(); if(a.right>b.left+1 && a.bottom>b.top+1 && a.top<b.bottom-1 && a.left<b.right-1) o.push('name under the counted-in box: '+r.dataset.n);
      const rr=r.getBoundingClientRect(); r.querySelectorAll('input,select,button').forEach(c=>{const q=c.getBoundingClientRect(); if(q.width&&(q.right>innerWidth+1||q.left<-1)) o.push('off screen: '+(c.dataset.f||c.dataset.dest||c.tagName))});});
      if(document.documentElement.scrollWidth>innerWidth+1) o.push('page scrolls sideways '+document.documentElement.scrollWidth); return o})()""")
    for b in bad: f.add('BUG', b)
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
