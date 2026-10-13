"""Persona 128: the Cloudflare Worker's starter allowance, daily top-up, licence-token check and request hardening behave (runs tests/worker/worker_allowance.mjs under node with a fake KV store and fake upstream)."""
import sys, subprocess, os
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
r = subprocess.run(['node', os.path.join(root, 'tests/worker/worker_allowance.mjs')], capture_output=True, text=True, timeout=60)
print(r.stdout.strip()); print(r.stderr.strip()[:500])
sys.exit(r.returncode)
