"""Persona 222: (a) cupboards & stock starts OFF until something is counted (and says so), (b) Surprise sweet / savoury gives two ideas: one made
from what is in the library (stock-filtered when on), then one new idea that searches the web for inspiration; a failed web search falls back
to a plain idea; a typed request is unchanged (one idea, no web). AI is stubbed. Invented data only."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    ev("localStorage.setItem('mh_shop_pane','both')")   # these tests look at the list and the cupboards together (v3.10.1177)
    # a: default off
    if ev("mhStockOn()"): f.add('BUG', 'a: a user who has counted nothing starts with it OFF')
    ev("mhShopOpen()"); card = ev("mhStockCardHtml(mhShopLoad())")
    if 'Switched off' not in card or 'Turn cupboards' not in card or 'only suggests meals you can make' not in card: f.add('BUG', 'a: the off card says it is off and what switching it on does')
    if ev("mhSuggestMode()") != 'off': f.add('BUG', 'a: off by default means meal ideas are not filtered')
    ev("mhStockTrack('Honey',{base:'g',pack:340})")
    if not ev("mhStockOn()"): f.add('BUG', 'a: counting something turns it on')
    ev("localStorage.removeItem(MH_STOCK_KEY)"); ev("""()=>{ const o={items:{x:{name:'Old thing',key:'old thing',base:'g',level:5,reorder:null}},ledger:[],rev:1}; localStorage.setItem(MH_STOCK_KEY, JSON.stringify(o)); }""")
    if not ev("mhStockOn()"): f.add('BUG', 'a: someone who already counted foods keeps it ON')
    ev("localStorage.removeItem(MH_STOCK_KEY)")
    # b: surprise pair
    ev("""saveLibrary([
      {id:'l1',name:'Greek Yoghurt',kcal:97,protein:9,carbs:4,fat:5,portion:'100g',useCount:9},
      {id:'l2',name:'Raspberries',kcal:52,protein:1.2,carbs:5,fat:0.7,portion:'100g',useCount:5},
      {id:'l3',name:'Cheddar',kcal:410,protein:25,carbs:0.1,fat:34,portion:'100g',useCount:5}])""")
    ev("""()=>{ window._calls=[]; window._bubbles=[]; window._failWeb=false;
      window.callHealthAI = async (p,o)=>{ window._calls.push({p, web:!!(o&&o.webSearch)}); if (o && o.webSearch && window._failWeb) return {ok:false,error:'no web'};
        const lib = p.includes('AVAILABLE INGREDIENTS'); return {ok:true,text: JSON.stringify(lib ? {title:'Yoghurt Berry Pot',intro:'quick',servings:1,ingredients:[{name:'Greek Yoghurt',amount:150,unit:'g'},{name:'Raspberries',amount:80,unit:'g'}],method:['Mix.']} : {title:'Web Tart',intro:'Inspired by Example Tart from example.com',servings:2,ingredients:[{name:'flour',amount:100,unit:'g'}],method:['Bake.']})}; };
      const orig = window.addRecipeBubble; window.addRecipeBubble = r => { window._bubbles.push(r.title); };
      return 0; }""")
    run = lambda kind: ev("async k=>{ window._calls=[]; window._bubbles=[]; _recipeDiscoverKind=k; document.getElementById('recipeDiscoverInput').value=''; await submitRecipeDiscover(); return 1 }", kind)
    run('sweet')
    calls = ev("window._calls"); bub = ev("window._bubbles")
    if len(calls) != 2: f.add('BUG', f'b: surprise sweet makes two ideas (two AI calls): {len(calls)}')
    else:
        if 'AVAILABLE INGREDIENTS' not in calls[0]['p'] or 'sweet dish' not in calls[0]['p'] or calls[0]['web']: f.add('BUG', 'b: the first idea is built from the library, sweet, no web')
        if not calls[1]['web'] or 'Inspired by' not in calls[1]['p'] or 'sweet' not in calls[1]['p'] or 'own words' not in calls[1]['p']: f.add('BUG', 'b: the second idea searches the web and is written in its own words with an Inspired by line')
    if bub != ['Yoghurt Berry Pot', 'Web Tart']: f.add('BUG', f'b: both ideas are shown, local first: {bub}')
    run('savoury'); c2 = ev("window._calls")
    if not c2 or 'savoury dish' not in c2[0]['p']: f.add('BUG', 'b: savoury is passed to the library idea')
    # web fails: falls back plain
    ev("window._failWeb=true"); run('sweet'); c3 = ev("window._calls"); b3 = ev("window._bubbles")
    if [c['web'] for c in c3] != [False, True, False] or b3 != ['Yoghurt Berry Pot', 'Web Tart']: f.add('BUG', f'b: a failed web search falls back to a plain idea: {[c["web"] for c in c3]} {b3}')
    ev("window._failWeb=false")
    # typed request: unchanged
    ev("async()=>{ window._calls=[]; window._bubbles=[]; _recipeDiscoverKind=null; document.getElementById('recipeDiscoverInput').value='chicken curry'; await submitRecipeDiscover(); return 1 }")
    c4 = ev("window._calls")
    if len(c4) != 1 or c4[0]['web'] or 'chicken curry' not in c4[0]['p']: f.add('BUG', f'b: a typed request is one idea, no web: {c4}')
    # stock on: the local idea only uses what is counted
    ev("""()=>{ mhStockTrack('Greek Yoghurt',{base:'g',pack:500}); mhStockSetLevel(mhShopKey('Greek Yoghurt'),400); mhStockTrack('Raspberries',{base:'g',pack:150}); mhStockSetLevel(mhShopKey('Raspberries'),0); mhStockSetSuggestMode && 0; }""") if False else None
    ev("()=>{ mhStockTrack('Greek Yoghurt',{base:'g',pack:500}); mhStockSetLevel(mhShopKey('Greek Yoghurt'),400); mhStockTrack('Raspberries',{base:'g',pack:150}); mhStockSetLevel(mhShopKey('Raspberries'),0); }")
    run('sweet'); c5 = ev("window._calls")
    if c5 and 'Raspberries' in c5[0]['p']: f.add('BUG', 'b: with stock on, a food that is used up is not offered for the local idea')
    if c5 and 'Greek Yoghurt' not in c5[0]['p']: f.add('BUG', 'b: with stock on, a food that is in stock is offered')
    if errs: f.add('JS-exception', errs[0])
print('\n'.join(f'{a}: {b}' for a, b in f) or 'PASS')
sys.exit(1 if f else 0)
