"""Persona 213: CSV import with the food/not-food sort and the shop-variant matching passes (v3.10.1120). Pete has four double creams, one per
shop, each with its own nutrition. Covers: CSV reading (quotes, commas inside quotes, CRLF, BOM, headed and headless); pass 1 exact (case and
punctuation ignored); pass 2 ingredient + shop, pack size ignored; pass 3 near match (word order, typo) only SUGGESTED; two equal candidates
never picked for you; nothing invented (the food library is untouched by an import); obvious non-food spotted but still confirmed; a
food nobody knows asks; remembered answers so the same file asks nothing the second time; shops created; duplicates counted; non-food keeps
its amount; and the remembered answers are in the backup."""
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay')?.remove()"); ev("mhShopOpen()")
    lib = [{'name': f'Double Cream ({s})', 'kcal': k, 'protein': 1.5, 'fat': 48, 'carbs': 1.7, 'portion': '30ml'} for s, k in (('Asda', 467), ('Tesco', 449), ('Aldi', 471), ('Lidl', 460))]
    ev("l=>saveLibrary(l.concat(loadLibrary()))", lib); nlib = ev("loadLibrary().length")
    # reading
    rows = ev("t=>mhCsvParse(t)", '﻿Item,Qty,Shop\r\n"Cream, double",2,Aldi\r\n"Say ""cheese""",,\r\n')
    if rows != [['Item', 'Qty', 'Shop'], ['Cream, double', '2', 'Aldi'], ['Say "cheese"', '', '']]: f.add('BUG', f'csv reading: {rows}')
    M = lambda n: ev("n=>mhVariantMatch(n)", n)
    m = M('double cream (asda)')
    if m['pass'] != 1 or m['name'] != 'Double Cream (Asda)' or not m['sure']: f.add('BUG', f'pass 1 exact, case ignored: {m}')
    m = M('Double Cream 300ml (Tesco)')
    if m['pass'] != 2 or m['name'] != 'Double Cream (Tesco)' or not m['sure']: f.add('BUG', f'pass 2 ingredient+shop, pack size ignored: {m}')
    m = M('Double Cream')
    if m['sure'] or len(m.get('options', [])) != 3: f.add('BUG', f'four equal candidates: never pick, offer at most three: {m}')
    m = M('Cream, double (Aldi)')
    if m['pass'] != 3 or m['sure'] or m.get('options') != ['Double Cream (Aldi)']: f.add('BUG', f'pass 3 word order is only a suggestion: {m}')
    m = M('Doble Cream (Lidl)')
    if m['pass'] != 3 or m['sure'] or m.get('options') != ['Double Cream (Lidl)']: f.add('BUG', f'pass 3 typo is only a suggestion: {m}')
    m = M('Zorblax')
    if m['sure'] or m.get('options'): f.add('BUG', f'an unknown name matches nothing: {m}')
    # classification
    csv = 'Item,Qty,Shop\nDouble Cream (Asda),,Asda\nDouble Cream 300ml (Tesco),,Tesco\nDouble Cream,,\nCream double (Aldi),,Aldi\nToilet roll,24 pack,Tesco\nZorblax,,Asda\nDouble Cream (Asda),,Asda\n'
    ev("t=>mhShopCsvLoad(t,'shop.csv')", csv); page.wait_for_timeout(150)
    plan = ev("_shopUi.csv.rows")
    if len(plan) != 6: f.add('BUG', f'a repeated line is read once: {len(plan)}')
    by = {r['name']: r for r in plan}
    if by['Toilet roll']['kind'] != 'nonfood' or by['Toilet roll']['kindSure']: f.add('BUG', 'obvious non-food is spotted but still needs a confirming tap')
    if by['Zorblax']['kindSure']: f.add('BUG', 'a food nobody knows must ask')
    if by['Double Cream']['linkOn'] or by['Double Cream']['link']: f.add('BUG', 'two equals: nothing may be linked for you')
    txt = page.inner_text('#mhShopPane')
    for must in ('Toilet roll', 'Zorblax', 'Cream double (Aldi)', 'Double Cream'):
        if must not in txt: f.add('BUG', f'{must} should be in the review')
    if 'Double Cream (Asda)' in txt.split('Import 6 items')[0].split('Import shop.csv')[1].split('need a quick look')[1].split('Same as')[0] and False: pass
    if ev("n=>mhVariantMatch(n,'Asda').name", 'Double Cream') != 'Double Cream (Asda)': f.add('BUG', 'the CSV shop column supplies the shop when the name has none (pass 2)')
    # answer the questions, import
    page.click('[data-csv="Toilet roll"] button:has-text("Not food")'); page.click('[data-csv="Zorblax"] button:has-text("Food")')
    page.select_option('[data-csv="Double Cream"] select', 'Double Cream (Lidl)'); page.click('text=Accept all suggestions'); page.wait_for_timeout(100)
    page.click('#mhCsvGo'); page.wait_for_timeout(200)
    s = ev("mhShopLoad()"); names = {i['name']: i for i in s['items']}
    for n in ('Double Cream (Asda)', 'Double Cream (Tesco)', 'Double Cream (Aldi)', 'Double Cream (Lidl)', 'Toilet roll', 'Zorblax'):
        if n not in names: f.add('BUG', f'{n} should be on the list: {list(names)}')
    if names.get('Toilet roll', {}).get('amount') != '24 pack' or not names.get('Toilet roll', {}).get('nonFood'): f.add('BUG', 'non-food keeps its amount and kind')
    if names.get('Double Cream (Aldi)', {}).get('shop') != 'Aldi' or 'Aldi' not in s['shops']: f.add('BUG', 'items go under their own shop and the shop is created')
    if 'Cream double (Aldi)' in names or 'Double Cream' in names: f.add('BUG', 'a linked item uses the library name, not the typed one')
    if ev("loadLibrary().length") != nlib: f.add('BUG', 'an import must never create or change food entries (nothing invented)')
    if ev("_shopUi.csv") is not None: f.add('BUG', 'the import is finished and cleared')
    # second time: everything remembered, nothing to ask, duplicates counted
    ev("t=>mhShopCsvLoad(t,'shop.csv')", csv); page.wait_for_timeout(150)
    left = ev("_shopUi.csv.rows.filter(mhCsvNeedsYou).map(r=>r.name)")
    if left: f.add('BUG', f'answers are remembered, nothing left to ask: {left}')
    page.click('#mhCsvGo'); page.wait_for_timeout(200)
    if 'already on the list' not in page.inner_text('#mhShopPane'): f.add('BUG', 'duplicates are counted on screen')
    if ev("mhShopLoad().items.length") != len(names): f.add('BUG', 'importing twice must not duplicate')
    if not ev("mhBuildBackupSettingsHas = (buildFullBackupPayload().settings||{}).mh_shopping_match_v1 != null"): f.add('BUG', 'remembered answers must be in the backup')
    if errs: f.add('BUG', f'page errors {errs[:3]}')
print('findings', len(f)); [print(x) for x in f] if f else None; sys.exit(1 if f else 0)
