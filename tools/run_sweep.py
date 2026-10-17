import glob,os,re,subprocess,sys,time
R='/home/claude/maxhealth'
files=sorted(glob.glob(R+'/tests/personas/p[0-9]*.py'), key=lambda f:int(re.match(r'p(\d+)',os.path.basename(f)).group(1)))
skip=set(sys.argv[2:]); out=sys.argv[1]
os.makedirs('/tmp/claude-0/sweep_out',exist_ok=True)
for f in files:
    n=os.path.basename(f)[:-3]
    if n in skip: continue
    t=time.time()
    try:
        r=subprocess.run([sys.executable,'-I',f],cwd=R,capture_output=True,text=True,timeout=600)
        rc=r.returncode; txt=r.stdout+r.stderr
    except subprocess.TimeoutExpired as e:
        rc=-9; txt='TIMEOUT'
    open(f'/tmp/claude-0/sweep_out/{n}.txt','w').write(txt)
    # clean up any stray server
    subprocess.run("ps -eo pid,args | grep 'server.py' | grep -v grep | awk '{print $1}' | xargs -r kill",shell=True)
    open(out,'a').write(f"{'PASS' if rc==0 else 'FAIL'} {n} {time.time()-t:.0f}s\n")
open(out,'a').write('DONE\n')
