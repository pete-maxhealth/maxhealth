"""Run a named list of persona tests, one at a time (they share port 5757). usage: python3 -u tools/run_suite.py tests/suites/release_1219.txt /tmp/suite.log"""
import os, subprocess, sys, time
R = '/home/claude/maxhealth'
names = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
out = sys.argv[2]; os.makedirs('/tmp/claude-0/suite_out', exist_ok=True)
for n in names:
    f = os.path.join(R, 'tests/personas', n + '.py')
    t = time.time()
    try:
        r = subprocess.run([sys.executable, '-I', f], cwd=R, capture_output=True, text=True, timeout=600); rc = r.returncode; txt = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        rc = -9; txt = 'TIMEOUT'
    open(f'/tmp/claude-0/suite_out/{n}.txt', 'w').write(txt)
    subprocess.run("ps -eo pid,args | grep 'server.py' | grep -v grep | awk '{print $1}' | xargs -r kill", shell=True)
    open(out, 'a').write(f"{'PASS' if rc == 0 else 'FAIL'} {n} {time.time()-t:.0f}s\n")
open(out, 'a').write('DONE\n')
