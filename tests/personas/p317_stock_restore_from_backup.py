"""Persona 317 (v3.10.1216): stock can be put back from a full backup file - only the stock changes; history, list and everything else stay as they are; it asks first and warns if the backup is older. Invented data."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()")
    lv = lambda n: ev("n=>{const i=mhStockLoad().items[mhShopKey(n)]; return i ? i.level : 'missing'}", n)
    ev("""(()=>{ [['Zz Rice','g',640,300],['Zz Milk','ml',1500,500]].forEach(([n,b,l,r])=>{mhStockTrack(n,{base:b,pack:1000,shop:'Asda'}); mhStockSetLevel(mhShopKey(n),l);}); })()""")
    ev("localStorage.setItem('mh_last_full_backup_date', todayStr())")
    payload = ev("buildFullBackupPayload()")
    # the person then types wrong figures and logs a day
    ev("(()=>{mhStockSetLevel(mhShopKey('Zz Rice'),5); mhStockSetLevel(mhShopKey('Zz Milk'),9);})()")
    nHist = ev("state.history.length")
    ev("(()=>{const s=mhShopLoad(); mhShopSetAdd(s,'Zz Bread','manual'); mhShopSave(s);})()")
    ev("""async (txt)=>{ const file = new File([txt], 'maxhealth_backup_x.json', {type:'application/json'}); await mhStockImportFile({files:[file]}); }""", __import__('json').dumps(payload))
    page.wait_for_timeout(500)
    if not page.locator('#appModalConfirm').count(): f.add('BUG', 'restoring stock from a backup asks first')
    else: page.click('#appModalConfirm'); page.wait_for_timeout(500)
    if lv('Zz Rice') != 640 or lv('Zz Milk') != 1500: f.add('BUG', f'stock is back to the backup figures: {lv("Zz Rice")} {lv("Zz Milk")}')
    if ev("state.history.length") != nHist: f.add('BUG', 'history untouched')
    if not ev("mhShopLoad().items.some(i=>i.key===mhShopKey('Zz Bread'))"): f.add('BUG', 'the shopping list is untouched')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
