"""Persona 2: people who type heights/weights the way people actually write them."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
from playwright.sync_api import sync_playwright
CASES = [  # (unit, typed, expected value, tolerance)
  ('ft','5.6',167.6),('ft','5.06',167.6),('ft','5.11',180.3),('ft','5.10',177.8),('ft','5.1',154.9),('ft','6',182.9),
  ('st','12.7',79.8),('st','12.10',81.2),('st','12.07',79.8),('st','13',82.6),
  ('lbs','160',72.6),('kg','80.5',80.5),
]
bad = 0
with fresh_server() as root, sync_playwright() as pw:
    b = pw.chromium.launch(); page = b.new_page(); page.goto('http://localhost:5757/'); page.wait_for_timeout(1500); page.evaluate('onboardNext(2)'); page.evaluate('onboardNext(3)')
    for unit, typed, exp in CASES:
        if unit in ('ft',):
            page.evaluate(f"setHeightUnit('ft')"); page.fill('#onboardHeight', typed)
            got = page.evaluate("getHeightInCm(parseFloat(document.getElementById('onboardHeight').value))")
        else:
            page.evaluate(f"setWeightUnit('{unit}')"); page.fill('#onboardWeight', typed)
            got = page.evaluate("getWeightInKg(parseFloat(document.getElementById('onboardWeight').value))")
        ok = abs(got-exp) < 0.6
        bad += not ok
        print(('ok  ' if ok else 'FAIL'), unit, typed, '->', got, 'expected ~', exp)
    b.close()
print('FAILURES:', bad)
