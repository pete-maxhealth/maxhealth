"""Persona 259: adding a food to the cupboards from the cupboard search or from the library (v3.10.1155). Cupboard: the shop is already known. Library: the shop is taken from the
title if it names one, otherwise asked (an existing shop or a new one). Portions and pack size are filled from what is known and asked otherwise. You come back to where you were.
With stock off the food goes on that shop's list. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("""(()=>{const l=loadLibrary(); l.push({name:'Zzqx Plain Wrap',portion:'60 g',kcal:150,protein:5,fat:3,carbs:25},{name:'Zzqhey Seeded Loaf',portion:'40 g',kcal:100,protein:4,fat:1,carbs:15}); localStorage.setItem(LIBRARY_KEY, JSON.stringify(l));
      const s=mhShopLoad(); if(!s.shops.includes('Zzqhey')) s.shops.push('Zzqhey'); mhShopSave(s);})()""")
    # stock OFF first: the food goes on the shop's list
    ev("mhStockAddFood({name:'Zzqx Off Food', origin:'library', shop:'Zzqhey'})"); page.wait_for_timeout(200)
    on = ev("mhShopLoad().items.map(i=>[i.name,i.shop])")
    if on != [['Zzqx Off Food', 'Zzqhey']]: f.add('BUG', f'1: with stock off the food goes on that shop\'s list: {on}')
    ev("(()=>{const s=mhShopLoad(); s.items=[]; mhShopSave(s);})()")
    ev("mhStockTrack('Zzqx Seed',{base:'g'})")
    # pure helper
    if ev("mhShopFromTitle('Zzqhey Seeded Loaf', ['Asda','Zzqhey'])") != 'Zzqhey' or ev("mhShopFromTitle('Zzqx Plain Wrap', ['Asda','Zzqhey'])") != '': f.add('BUG', '2: a shop named in the title is recognised, others are not')
    if ev("mhShopFromTitle('Heyloaf bread', ['Heylo'])") != '': f.add('BUG', '2b: only whole words count')
    # library origin, shop NOT in title: asked; portion filled from the library; back to the library afterwards
    ev("switchTab('log', document.getElementById('maintab-log')); switchSubTab('log','library', document.getElementById('logtab-library'))"); page.wait_for_timeout(500)
    i = ev("loadLibrary().findIndex(x=>x.name==='Zzqx Plain Wrap')")
    page.locator('#lib-item-%d [title="Add to my cupboards"]' % i).first.click(); page.wait_for_timeout(500)
    d = ev("({v:_shopUi.view, n:_shopUi.stk&&_shopUi.stk.name, sh:_shopUi.stk&&_shopUi.stk.shop, ask:_shopUi.stk&&_shopUi.stk.shopAsk, b:_shopUi.stk&&_shopUi.stk.base, sv:_shopUi.stk&&_shopUi.stk.serv, nw:_shopUi.stk&&_shopUi.stk.isNew})")
    if d['v'] != 'stockedit' or d['n'] != 'Zzqx Plain Wrap' or not d['nw']: f.add('BUG', f'3: the library button opens the stock form: {d}')
    if d['sh'] != '' or not d['ask'] or 'Which shop?' not in page.inner_text('#mhStkShop'): f.add('BUG', f'4: no shop in the title, so it asks which: {d}')
    if d['b'] != 'g' or d['sv'] != '60': f.add('BUG', f'5: the library portion fills the serving: {d}')
    if '＋ New shop' not in page.inner_text('#mhStkShop'): f.add('BUG', '6: a new shop can be chosen')
    ev("mhStockFormSave()"); page.wait_for_timeout(200)
    if 'shop' not in (ev("_shopUi.stk&&_shopUi.stk.err||''") or '').lower(): f.add('BUG', '7: it will not add until a shop is chosen')
    ev("mhStkShopPick('__new')"); page.wait_for_timeout(300)
    page.fill('.app-modal-overlay input', 'Zzqnew'); page.click('#appModalConfirm'); page.wait_for_timeout(300)
    if 'Zzqnew' not in ev("mhShopLoad().shops") or ev("_shopUi.stk.shop") != 'Zzqnew': f.add('BUG', '8: a new shop is created and chosen')
    ev("mhStockFormSave()"); page.wait_for_timeout(600)
    it = ev("mhStockLoad().items[mhShopKey('Zzqx Plain Wrap')]")
    if not it or it['shop'] != 'Zzqnew' or it['serving'] != 60: f.add('BUG', f'9: added under the new shop with the serving: {it}')
    sub = ev("document.getElementById('logtab-library').classList.contains('active')")
    if not sub: f.add('BUG', '10: afterwards you are back in the Library')
    # library origin, shop in the title: not asked
    ev("mhStockAddFood({name:'Zzqhey Seeded Loaf', origin:'library'})"); page.wait_for_timeout(300)
    if ev("_shopUi.stk.shop") != 'Zzqhey' or ev("_shopUi.stk.shopAsk"): f.add('BUG', '11: a shop named in the title is not asked for')
    ev("mhStkBack()"); page.wait_for_timeout(300)
    if ev("_shopUi.stk") is not None: f.add('BUG', '12: Back closes the form')
    if not ev("document.getElementById('logtab-library') ? true : false"): f.add('BUG', '12b')
    # cupboard origin: the highlighted shop, back to the search
    ev("(()=>{const st=mhSlState(); st.q='Zzqx Brand New'; st.f='all'; st.shop='Zzqhey'; mhShopView('stocklist');})()"); page.wait_for_timeout(400)
    page.click('#mhSlNew button'); page.wait_for_timeout(400)
    if ev("_shopUi.stk.shop") != 'Zzqhey' or ev("_shopUi.stk.shopAsk"): f.add('BUG', '13: from the cupboard the shop is already known')
    ev("mhStkBase('g')"); ev("mhStockFormSave()"); page.wait_for_timeout(500)
    if ev("_shopUi.view") != 'stocklist' or ev("mhSlState().q") != 'Zzqx Brand New': f.add('BUG', '14: you come back to the search as you left it')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
