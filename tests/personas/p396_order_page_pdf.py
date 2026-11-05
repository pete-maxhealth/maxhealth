"""Persona 396: an order page saved as a PDF reads as an order (v3.10.1290). Pete (5 Nov): a delivered Asda order came in with "Rate your driver", "Your order" and
"Substitutes & unavailable" as items, "1 x" left in the names ("X Asda Vine Tomatoes") and weight lines as foods. The PDF reader puts each item's price in a second
tab-separated column, which looked like a table. Covers: tab-separated order text (invented), plain order text, a real table still read as a table, accents in names.
Invented data only."""
import re, sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from harness import *
from playwright.sync_api import sync_playwright
f = Findings()
PAGE = "\n".join([
 "Thu 05 Nov 2026 10:30 AM to 11:30 AM", "Rate your driver\tZZ1 1ZZ", "How would you rate your experience?", "£50.00 (estimated)", "Order again\tProblem with my order",
 "Your order\tPrint order", "Substitutes & unavailable\tHide", "1 x ZZQX VINE TOMATOES 250G\t£0.97", "Rest of order\tHide", "Dairy (3 items)",
 "2 x Zzqx Ready Salted Crisps 6 x 25g (150g)\t£2", "0.3kg\t£2", "1 x Zzqx Smooth Brussels Pâté 175g\t£0.69", "3 x Zzqx Chicken Breast Strips 500g\t£14.88", "1.5kg\t£14.88",
 "1 x Zzqx Toilet Tissue 24 Rolls\t£11.74", "Shopping total\t£267.80", "Delivery cost\t£4.50", "Total\t£261.12", "•••• 0000\t£261.12"])
with fresh_server() as root, sync_playwright() as pw:
    page = pw.chromium.launch().new_context(viewport={'width': 390, 'height': 900}, service_workers='block').new_page(); errs = []
    page.on('pageerror', lambda e: errs.append(str(e)[:200])); page.on('dialog', lambda d: d.accept())
    page.goto('http://localhost:5757/'); page.wait_for_timeout(1200); ev = page.evaluate
    ev("state.onboarded=true; saveState()"); ev("document.getElementById('onboardingOverlay').style.display='none'")
    ev("switchTabById('shop'); mhOrdOpen('receipt')"); page.wait_for_timeout(400)
    def load(text):
        ev("t=>mhOrdLoad(t,'test')", text); page.wait_for_timeout(400)
        return ev("(_shopUi.ord&&_shopUi.ord.rows||[]).map(r=>({n:r.name,t:r.track,a:r.amount,q:r.qty}))")
    rows = load(PAGE); names = ' | '.join(r['n'] for r in rows)
    if len(rows) != 5: f.add('BUG', f'1: five items from the order page, got {len(rows)}: {names}')
    for bad in ('Rate your', 'Your order', 'Substitutes', 'Shopping total', 'Delivery', '0.3kg', '1.5kg', 'Rest of order', 'Order again', 'Dairy'):
        if any(bad.lower() in r['n'].lower() or bad.lower() in r['t'].lower() for r in rows): f.add('BUG', f'2: page furniture is not an item ({bad}): {names}')
    if any(r['t'].lower().startswith('x ') or re.match(r'^\d+\s*x\b', r['n'], re.I) for r in rows): f.add('BUG', f'3: "1 x" never stays in a name: {rows}')
    by = {r['n'].split(' ')[0] + r['n'].split(' ')[1]: r for r in rows if len(r['n'].split(' ')) > 1}
    am = {r['n']: r['a'] for r in rows}
    if am.get('ZZQX VINE TOMATOES 250G') != '250 g': f.add('BUG', f'4: tomatoes 250 g: {am}')
    if am.get('Zzqx Ready Salted Crisps 6 x 25g (150g)') != '300 g': f.add('BUG', f'5: 2 x 150 g = 300 g: {am}')
    if am.get('Zzqx Chicken Breast Strips 500g') != '1500 g': f.add('BUG', f'6: 3 x 500 g = 1500 g: {am}')
    if not any('Pâté' in r['t'] and 'PâTé' not in r['t'] for r in rows): f.add('BUG', f'7: accented letters keep their case: {[r["t"] for r in rows]}')
    # the same page without tabs and prices on their own lines still reads as before
    plain = load("\n".join(l.split('\t')[0] for l in PAGE.split('\n')))
    if len(plain) != 5: f.add('BUG', f'8: the same page as plain text gives five items: {len(plain)}')
    # a genuine table is still a table
    tb = load("Item\tQty\tPrice\nZzqx Cheddar 400g\t2\t£3.50\nZzqx Milk 2L\t1\t£1.50")
    if len(tb) != 2 or not any('Cheddar' in r['n'] and r['q'] == 2 for r in tb): f.add('BUG', f'9: a real table is still read as a table: {tb}')
    if errs: f.add('BUG', f'page errors: {errs}')
print('findings', len(f)); [print(v) for v in f] if f else None; sys.exit(1 if f else 0)
