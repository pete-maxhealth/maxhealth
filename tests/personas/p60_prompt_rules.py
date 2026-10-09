"""Persona 60: guard the AI meal-logging prompt rules that protect accuracy and the "never add what I did not list" rule."""
import sys, os; sys.path.insert(0, __file__.rsplit('/',1)[0])
from harness import *
f = Findings()
h = open(os.path.join(REPO, 'maxhealth.html'), encoding='utf-8').read()
need = [
  ('COOKING FAT NOTE', 'hidden-fat note rule missing'),
  ('do NOT add any and do NOT invent an amount', 'cooking-fat rule must forbid inventing fat'),
  ("tell me what you used and how much and I'll add it", 'cooking-fat note wording missing'),
  ("do not add ingredients they haven't mentioned", 'text-description-overrides rule missing'),
  ('NO SAUCE DOUBLE-COUNTING', 'sauce double-count rule missing'),
  ('AMBIGUITY RULE', 'ambiguity rule missing'),
]
for k, msg in need:
    if k not in h: f.add('BUG', msg)
print('findings', len(f)); sys.exit(1 if f else 0)
