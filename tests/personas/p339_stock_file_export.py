"""Persona 339: Cupboards & stock and Shopping list appear in the Settings > Data export/import list. Export gives one json file;
importing it on another phone opens the same preview as the QR codes (nothing added until confirmed), merge not replace."""
import sys, re, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
bad = []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n + (f'  {info}' if info and not ok else ''))
    if not ok: bad.append(n)
SHOT = '/tmp/claude-0/-home-claude/c032a46b-68f2-5aea-a854-98f1a5b7657c/scratchpad/xfer/'
T0 = 1790000000000
def phone(br):
    ctx = br.new_context(viewport={'width': 430, 'height': 900}, service_workers='block', accept_downloads=True); p = ctx.new_page()
    errs = []; p.on('pageerror', lambda e: errs.append(str(e)[:200])); p.on('dialog', lambda d: d.accept())
    p.route(re.compile(r'^https?://(?!localhost)'), lambda r: r.abort())
    p.goto('http://localhost:5757/'); p.wait_for_timeout(1200); p.evaluate("state.onboarded=true; saveState()"); p.reload(); p.wait_for_timeout(1500)
    return p, errs
with fresh_server() as root, sync_playwright() as pw:
    br = pw.chromium.launch(); A, ea = phone(br); B, eb = phone(br)
    A.evaluate("""(()=>{mhStockTrack('Eggs',{base:'each',pack:6});let o=mhStockLoad();o.items.eggs.level=6;o.items.eggs.since=%d+5000;o.enabled=true;mhStockSave(o);
      const s=mhShopLoad();s.items.push({id:'a1',key:'oats',name:'Oats',shop:s.def,checked:false,src:'manual'});mhShopSave(s);})()""" % T0)
    B.evaluate("""(()=>{mhStockTrack('Milk',{base:'ml',pack:1000});let o=mhStockLoad();o.items.milk.level=500;o.enabled=true;mhStockSave(o);})()""")
    A.evaluate("showView && showView('import')") if A.evaluate("typeof showView==='function'") else None
    A.wait_for_timeout(600)
    html = A.evaluate("buildBulkDataActionsCard()")
    check('list has Cupboards & stock', 'value="stock"' in html and 'Cupboards & stock' in html)
    check('list has Shopping list', 'value="shoplist"' in html)
    # put the real card on screen for a rendered look
    A.evaluate("(h)=>{let d=document.createElement('div');d.id='tmpBulk';d.style.cssText='position:fixed;inset:0;z-index:9000;background:var(--bg);overflow:auto;padding:16px';d.innerHTML=h;document.body.appendChild(d)}", html)
    A.wait_for_timeout(300); A.screenshot(path=SHOT + 'bulk_list.png')
    A.evaluate("mhBulkSelect(false); document.querySelectorAll('#bulkDsList .bulkDs').forEach(c=>{if(c.value==='stock'||c.value==='shoplist')c.checked=true}); document.querySelector('input[name=bulkFmt][value=separate]').checked=true")
    with A.expect_download() as dl: A.evaluate("mhExportSelected(false)")
    d = dl.value; path = d.path(); txt = open(path).read(); obj = json.loads(txt)
    check('one stock file named maxedhealth_stock_<date>.json', re.match(r'maxedhealth_stock_.*\.json$', d.suggested_filename) is not None, d.suggested_filename)
    check('file holds eggs and the Oats list item', 'eggs' in obj['scopes']['stock']['items'] and len(obj['scopes']['list']['items']) == 1)
    # B imports it through the Settings import path
    before = B.evaluate("localStorage.getItem(MH_STOCK_KEY)+localStorage.getItem(MH_SHOP_KEY)")
    B.evaluate("(t)=>{mhImportFiles([new File([t],'maxedhealth_stock_x.json')])}", txt); B.wait_for_timeout(800)
    check('preview opens, nothing saved yet', B.evaluate("document.getElementById('mhXferOverlay').style.display==='block'") and B.evaluate("localStorage.getItem(MH_STOCK_KEY)+localStorage.getItem(MH_SHOP_KEY)") == before)
    B.screenshot(path=SHOT + 'bulk_import_review.png')
    check('preview mentions stock and shopping list', all(w in B.inner_text('#mhXferOverlay') for w in ['Stock', 'Shopping list']))
    B.evaluate("mhxDoApply()"); B.wait_for_timeout(600)
    st = B.evaluate("(()=>{const o=mhStockLoad();return {e:o.items.eggs&&o.items.eggs.level,m:o.items.milk.level,l:mhShopLoad().items.map(i=>i.key)}})()")
    check('merged: eggs arrive, milk kept, Oats on list', st == {'e': 6, 'm': 500, 'l': ['oats']}, str(st))
    B.evaluate("mhxUndo && mhxUndo()"); B.wait_for_timeout(500)
    check('undo puts B back', B.evaluate("!mhStockLoad().items.eggs && mhShopLoad().items.length===0"))
    # junk json still refused, and unrelated backups unaffected
    B.evaluate("mhxClose()"); B.evaluate("(t)=>{mhImportFiles([new File(['{\"v\":1,\"scopes\":{\"stock\":5}}'],'x.json')])}", ''); B.wait_for_timeout(500)
    check('a junk transfer file is refused', B.evaluate("document.getElementById('mhXferOverlay').style.display!=='block'"))
    check('no page errors', not ea and not eb, str(ea + eb))
    br.close()
print('FAILED: ' + ', '.join(bad) if bad else 'ALL PASS'); sys.exit(1 if bad else 0)
