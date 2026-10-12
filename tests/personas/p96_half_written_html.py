"""Persona 96: the server never serves a half-written maxhealth.html (the auto-update rewrites it in place). A file that does not end with </html> is retried, then the last complete copy is served."""
import sys, os, tempfile, importlib.util, time
f_findings = []
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
spec = importlib.util.spec_from_file_location('mh_server_under_test', os.path.join(root, 'server.py'))
srv = importlib.util.module_from_spec(spec); spec.loader.exec_module(srv)
good = b'<html><body>ok</body>\n</html>\n'
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'maxhealth.html'); srv.TRACKER = p; srv.time.sleep = lambda s: None
    open(p, 'wb').write(good)
    if srv.read_complete_app_html() != good: f_findings.append('complete file not served as is')
    open(p, 'wb').write(good[:12])            # half written
    if srv.read_complete_app_html() != good: f_findings.append('half-written file was served instead of the last complete copy')
    srv._LAST_GOOD_HTML = None
    if srv.read_complete_app_html() != good[:12]: f_findings.append('with no good copy, the partial file should still be returned (not an exception)')
print('findings', len(f_findings)); [print('  [BUG]', x) for x in f_findings]; sys.exit(1 if f_findings else 0)
