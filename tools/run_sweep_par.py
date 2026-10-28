"""Parallel persona sweep. Each test runs in its own network namespace (own loopback), so every test
can keep using port 5757 without clashing. Usage: python3 -u tools/run_sweep_par.py <logfile> [workers] [timeout_s]
Log lines match run_sweep.py: 'PASS|FAIL name Ns', ending with 'DONE'. Needs root (unshare -n)."""
import glob, os, re, subprocess, sys, time, signal
from concurrent.futures import ThreadPoolExecutor
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1]; workers = int(sys.argv[2]) if len(sys.argv) > 2 else 3; tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 240
files = sorted(glob.glob(R + '/tests/personas/p[0-9]*.py'), key=lambda f: int(re.match(r'p(\d+)', os.path.basename(f)).group(1)))
od = os.environ.get('SWEEP_OUT', '/tmp/claude-0/sweep_out'); os.makedirs(od, exist_ok=True)
LO = os.path.join(R, 'tools', '_lo_up.py')
import socket, threading, urllib.parse, tempfile
SOCK = os.path.join(tempfile.mkdtemp(prefix='mh_sweep_'), 'proxy.sock')
_pu = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
def _pipe(a, b):
    try:
        while (d := a.recv(65536)): b.sendall(d)
    except OSError: pass
    for s in (a, b):
        try: s.shutdown(socket.SHUT_RDWR)
        except OSError: pass
if _pu:
    _l = socket.socket(socket.AF_UNIX); _l.bind(SOCK); _l.listen(64); _pp = urllib.parse.urlparse(_pu)
    def _accept():
        while True:
            c, _ = _l.accept(); u = socket.create_connection((_pp.hostname, _pp.port))
            threading.Thread(target=_pipe, args=(c, u), daemon=True).start(); threading.Thread(target=_pipe, args=(u, c), daemon=True).start()
    threading.Thread(target=_accept, daemon=True).start()
def run(f):
    n = os.path.basename(f)[:-3]; t = time.time()
    p = subprocess.Popen(['unshare', '-n', sys.executable, '-I', '-c',
        f"exec(open({LO!r}).read()); import runpy,sys; sys.argv=[{f!r}]; runpy.run_path({f!r}, run_name='__main__')"],
        cwd=R, env={**os.environ, 'MH_PROXY_SOCK': SOCK}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try: txt, _ = p.communicate(timeout=tmo); rc = p.returncode
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL); txt = (p.communicate()[0] or '') + '\nTIMEOUT'; rc = -9
    open(f'{od}/{n}.txt', 'w').write(txt)
    open(out, 'a').write(f"{'PASS' if rc == 0 else 'FAIL'} {n} {time.time()-t:.0f}s\n")
with ThreadPoolExecutor(workers) as ex: list(ex.map(run, files))
subprocess.run("find /tmp -maxdepth 1 -name 'mh_persona_*' -exec rm -rf {} + 2>/dev/null", shell=True)
open(out, 'a').write('DONE\n')
