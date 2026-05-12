#!/usr/bin/env python3
"""
pipeline/auto.py
MaxedHealth — Pipeline trigger (repo copy)

This file lives in the git repo at:
  /storage/emulated/0/MaxHealth/app/maxhealth/pipeline/auto.py

The real pipeline entry point lives at:
  /storage/emulated/0/MaxHealth/app/update_health.py

This script just forwards to it, so you can trigger the pipeline
from the repo directory without knowing the exact path.

Usage (from anywhere in the repo):
  python pipeline/auto.py
  python pipeline/auto.py --device amazfit --password YOUR_PASSWORD
  python pipeline/auto.py --dry-run
  python pipeline/auto.py --check
  python pipeline/auto.py --restore path/to/backup.csv

All arguments are passed straight through to update_health.py.
"""

import os
import sys
import subprocess

# Real pipeline location — one level up from the repo
REPO_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR      = os.path.dirname(REPO_DIR)
PIPELINE     = os.path.join(APP_DIR, 'update_health.py')

if not os.path.exists(PIPELINE):
    print(f"Error: Cannot find pipeline at {PIPELINE}", file=sys.stderr)
    print(f"Expected structure:", file=sys.stderr)
    print(f"  {APP_DIR}/", file=sys.stderr)
    print(f"  ├── update_health.py   ← pipeline entry point", file=sys.stderr)
    print(f"  ├── extractors/", file=sys.stderr)
    print(f"  └── maxhealth/         ← this repo", file=sys.stderr)
    print(f"      └── pipeline/", file=sys.stderr)
    print(f"          └── auto.py    ← you are here", file=sys.stderr)
    sys.exit(1)

# Forward all arguments to the real pipeline
result = subprocess.run(
    [sys.executable, PIPELINE] + sys.argv[1:],
    cwd=APP_DIR
)
sys.exit(result.returncode)
