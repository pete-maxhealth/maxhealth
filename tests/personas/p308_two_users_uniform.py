"""Persona 308: two different demo users (Alex recomp, Frank general) on the SAME theme: every screen has the same structure,
card controls and button styles (differences only where data decides), no page errors/overflow, and the shopping + stock flows
behave identically for both. Usage: python3 -I p308_two_users_uniform.py [idA idB]"""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
A, B = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('alex', 'frank')
SCREENS = ['dash', 'supplements', 'move', 'chat', 'hist', 'library', 'shop', 'trends', 'stats', 'reports', 'manage', 'customise', 'import']
DATA_BTN = "setSymptomScore|openChartLightbox|mhExplainOutcomes|togglePatternScatter"
SIG = """(DATA) => { const vis = e => e.offsetParent !== null && e.getBoundingClientRect().width > 0; const re = new RegExp(DATA);
  const cards = [...document.querySelectorAll('.water-card')].filter(vis).map(c => { const t = c.querySelector('.water-title'), ctl = c.querySelector('.mh-ctl');
    return { title: t ? t.innerText.replace(/\\s+/g,' ').trim() : '(no title)', ctl: ctl ? [...ctl.children].map(x => x.innerText.replace(/\\s+/g,' ').trim().replace(/[0-9]+\\/[0-9]+/,'n/n').replace(/[▾▸].*$/,'')).join('|') : 'NONE' }; });
  const btn = {}; document.querySelectorAll('button, .copy-btn, .hist-filter-btn, .run-btn').forEach(b => { if (!vis(b) || re.test(b.getAttribute('onclick')||'')) return; const cs = getComputedStyle(b);
    const k = (b.className||'').toString().split(' ').filter(x => /btn|tile|chip/.test(x)).join('.') || 'plain'; (btn[k] = btn[k] || new Set()).add([cs.fontSize, cs.borderRadius, cs.fontFamily.split(',')[0]].join('/')); });
  const b2 = {}; Object.keys(btn).forEach(k => b2[k] = [...btn[k]].sort().join(' ; '));
  const ac = {}; [...document.querySelectorAll('[class*=card]')].filter(vis).forEach(c => { const cs = getComputedStyle(c); ac[[c.className.toString().split(' ').filter(x => /card/.test(x)).join('.'), cs.borderRadius, cs.fontSize].join('/')] = 1; });
  return { cards, btn: b2, ac: Object.keys(ac).sort(), over: document.documentElement.scrollWidth > window.innerWidth + 2 }; }"""
FLOW = """() => { const out = {}; const k = mhShopKey('Zzqx Beans');
  mhStockTrack('Zzqx Beans', {base:'g', shop:'Asda'}); mhStockSetLevel(k, 400); mhStockSetReorder(k, 200); mhStockSetLevel(k, 100); mhStockSweep();
  out.onList = mhShopLoad().items.filter(i => /Zzqx Beans/.test(i.name)).length;
  mhShopHold(mhShopLoad().items.find(i => /Zzqx Beans/.test(i.name)).id || 0); mhStockSweep();
  out.held = !!mhStockLoad().items[k].held; out.afterHold = mhShopLoad().items.filter(i => /Zzqx Beans/.test(i.name)).length;
  _shopUi.heldSel = {[k]: true}; mhShopHeldRelease(); mhStockSweep();
  out.released = !mhStockLoad().items[k].held; out.backOnList = mhShopLoad().items.filter(i => /Zzqx Beans/.test(i.name)).length;
  return out; }"""
res = {}; f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 800}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()")
    for pid in (A, B):
        ev("startDemoMode(%r)" % pid); page.wait_for_timeout(2500)
        ev("applyTheme('midnight');setVisualTheme('vital');applyCustomAccent('#14b8a6')")
        ev("localStorage.setItem('mh_shop_pane','both'); window.appConfirm=(m,ok)=>{ok&&ok()}; window._mhLibQuiet=true")
        res[pid] = {}
        for sc in SCREENS:
            ev("switchTabById(%r)" % sc); page.wait_for_timeout(450); page.evaluate("document.fonts.ready.then(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))))"); page.wait_for_timeout(300)   # let fonts load and the screen finish drawing before measuring
            if sc == 'shop': ev("_shopUi.addOpen=true; mhShopRender()"); page.wait_for_timeout(200)   # 'Add to the list' opens by itself only while the list is empty (by design)
            res[pid][sc] = page.evaluate(SIG, DATA_BTN)
            if res[pid][sc]['over']: f.add('BUG', f'{pid}/{sc}: horizontal overflow')
        ev("switchTabById('shop')"); page.wait_for_timeout(400)
        try: res[pid]['flow'] = page.evaluate(FLOW)
        except Exception as e: f.add('BUG', f'{pid}: shopping flow threw {str(e)[:160]}')
        ev("exitDemoMode()"); page.wait_for_timeout(900)
    if errs: f.add('BUG', f'page errors: {errs}')
if A in res and B in res:
    for sc in SCREENS:
        x, y = res[A][sc], res[B][sc]
        for k in set(x['btn']) | set(y['btn']):
            if k not in x['btn'] or k not in y['btn']: print('note:', sc, 'button kind only for one user (data decides):', k); continue
            if k == 'plain': continue   # unclassed buttons: the set legitimately varies with the data shown
            if x['btn'].get(k) != y['btn'].get(k): f.add('BUG', f'{sc}: button style [{k}] differs: {A}={x["btn"].get(k)} {B}={y["btn"].get(k)}')
        for k in set(x['ac']) ^ set(y['ac']): print('note:', sc, 'card kind only for one user (condition or data decides):', k)
        tx = {c['title']: c['ctl'] for c in x['cards']}; ty = {c['title']: c['ctl'] for c in y['cards']}
        for t in set(tx) & set(ty):
            if tx[t] != ty[t]: f.add('BUG', f'{sc}: card "{t[:40]}" controls differ: {tx[t]} / {ty[t]}')
        for t in tx:
            if tx[t] == 'NONE' and sc in ('dash', 'shop') : f.add('BUG', f'{A}/{sc}: card "{t[:40]}" has no show/hide-reorder controls')
        for t in ty:
            if ty[t] == 'NONE' and sc in ('dash', 'shop') : f.add('BUG', f'{B}/{sc}: card "{t[:40]}" has no show/hide-reorder controls')
    if res[A].get('flow') != res[B].get('flow'): f.add('BUG', f'shopping flow differs: {res[A].get("flow")} vs {res[B].get("flow")}')
    else: print('flow', res[A].get('flow'))
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
