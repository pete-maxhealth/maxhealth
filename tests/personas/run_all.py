#!/usr/bin/env python3
"""Run every persona test (p*.py) in a fresh server each; print a summary; exit 1 if any fail.
Add a persona = drop a new pNN_name.py here that exits non-zero on failure."""
import glob, os, subprocess, sys, time
here = os.path.dirname(os.path.abspath(__file__))
results = []
for path in sorted(glob.glob(os.path.join(here, 'p[0-9]*.py'))):
    name = os.path.basename(path)
    t = time.time()
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=600)
    ok = r.returncode == 0
    results.append((name, ok, time.time() - t))
    if not ok:
        print(f'--- {name} output ---'); print('\n'.join(l for l in (r.stdout + r.stderr).splitlines() if 'agent-proxy' not in l)[-3000:])
print('\nPERSONA RESULTS')
for n, ok, d in results: print(f"  {'PASS' if ok else 'FAIL'}  {n}  ({d:.0f}s)")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
