#!/usr/bin/env python3
"""
find_orphans.py — flags potentially unused functions and top-level variables
in maxhealth.html for manual review.

This is a HEURISTIC, not a guarantee. It works by counting how many times
each declared name appears elsewhere in the file — including inside
onclick="..." strings in the HTML, since that's how most functions in this
app actually get called. A name with zero other occurrences is *likely*
dead code, but false positives are possible: a function referenced only via
string construction (e.g. window[dynamicName]()), or kept deliberately for
a reason not visible from static text, would still get flagged here.

Nothing is deleted automatically. This only prints a list for a human to
look at and decide on, one at a time.

Usage:
    python3 find_orphans.py maxhealth.html
"""

import re
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_orphans.py <path-to-maxhealth.html>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Top-level function declarations: function name(...)
    func_pattern = re.compile(r'^\s*(?:async\s+)?function\s+([a-zA-Z_$][\w$]*)\s*\(', re.MULTILINE)
    functions = {}
    for m in func_pattern.finditer(content):
        name = m.group(1)
        functions.setdefault(name, []).append(m.start())

    # Top-level const/let declarations (single-name only, skips destructuring
    # like `const { a, b } = ...` since those are near-impossible to track
    # reliably with a simple regex, and skips anything inside a function body
    # by only matching lines with minimal leading whitespace - a heuristic,
    # not a full scope parser).
    var_pattern = re.compile(r'^(?:const|let|var)\s+([a-zA-Z_$][\w$]*)\s*=', re.MULTILINE)
    variables = {}
    for m in var_pattern.finditer(content):
        name = m.group(1)
        variables.setdefault(name, []).append(m.start())

    def count_all_occurrences(name):
        # Word-boundary match for the bare name, counted across the WHOLE
        # file - this deliberately includes onclick="name(...)" strings in
        # the HTML, since that's how this app wires up most of its UI.
        return len(re.findall(r'\b' + re.escape(name) + r'\b', content))

    print(f"Scanning {path} ({len(content):,} characters)...\n")

    print("=" * 70)
    print("POSSIBLY ORPHANED FUNCTIONS")
    print("(declared once, name never appears again anywhere else in the file)")
    print("=" * 70)
    orphan_funcs = []
    for name in sorted(functions.keys()):
        total = count_all_occurrences(name)
        declarations = len(functions[name])
        # If the name appears exactly as many times as it's declared, it's
        # never referenced anywhere else - onclick strings, other function
        # bodies, nothing.
        if total <= declarations:
            orphan_funcs.append(name)
            print(f"  function {name}()  — appears {total}x total ({declarations}x as declaration)")

    if not orphan_funcs:
        print("  None found.")

    print()
    print("=" * 70)
    print("POSSIBLY ORPHANED TOP-LEVEL VARIABLES")
    print("(declared once, name never appears again anywhere else in the file)")
    print("=" * 70)
    orphan_vars = []
    for name in sorted(variables.keys()):
        total = count_all_occurrences(name)
        declarations = len(variables[name])
        if total <= declarations:
            orphan_vars.append(name)
            print(f"  {name}  — appears {total}x total ({declarations}x as declaration)")

    if not orphan_vars:
        print("  None found.")

    print()
    print("=" * 70)
    print("DUPLICATE FUNCTION NAMES")
    print("(same function name declared more than once - the second silently")
    print(" overwrites the first in JS; this is usually a real bug, not just")
    print(" clutter, and worth checking regardless of whether either is used)")
    print("=" * 70)
    dupes = {name: locs for name, locs in functions.items() if len(locs) > 1}
    if dupes:
        for name, locs in sorted(dupes.items()):
            lines = [content[:pos].count('\n') + 1 for pos in locs]
            print(f"  function {name}()  — declared {len(locs)}x, at lines: {lines}")
    else:
        print("  None found.")

    print()
    print("-" * 70)
    print(f"Summary: {len(orphan_funcs)} possibly orphaned function(s), "
          f"{len(orphan_vars)} possibly orphaned variable(s), "
          f"{len(dupes)} duplicate function name(s).")
    print()
    print("Reminder: review each one individually before removing anything.")
    print("A function/variable can legitimately show up here and still be")
    print("needed - e.g. reserved for a feature you're mid-way through, or")
    print("called in a way this script's simple text-matching can't see.")


if __name__ == "__main__":
    main()
