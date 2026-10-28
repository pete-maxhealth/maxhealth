import socket,fcntl,struct,os
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ifr=struct.pack('16sH14s',b'lo',0,b'')
fl=struct.unpack('16sH14s',fcntl.ioctl(s,0x8913,ifr))[1]
fcntl.ioctl(s,0x8914,struct.pack('16sH14s',b'lo',fl|1,b''))
# Relay: the sandbox's HTTP proxy lives on the parent's loopback, which a private namespace cannot reach.
# Listen on the same loopback port here and forward over a unix socket (filesystem sockets cross namespaces).
import os, threading, urllib.parse
_u = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy'); _us = os.environ.get('MH_PROXY_SOCK')
if _u and _us:
    def _pipe(a, b):
        try:
            while (d := a.recv(65536)): b.sendall(d)
        except OSError: pass
        for s in (a, b):
            try: s.shutdown(socket.SHUT_RDWR)
            except OSError: pass
    def _srv():
        l = socket.socket(); l.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        l.bind(('127.0.0.1', urllib.parse.urlparse(_u).port)); l.listen(64)
        while True:
            c, _ = l.accept(); u = socket.socket(socket.AF_UNIX); u.connect(_us)
            threading.Thread(target=_pipe, args=(c, u), daemon=True).start(); threading.Thread(target=_pipe, args=(u, c), daemon=True).start()
    threading.Thread(target=_srv, daemon=True).start()

# Give Chromium a non-loopback "online" interface (else navigator.onLine is false and the app shows its offline screens).
# A tun device is created by ioctl alone (no netlink library needed); the fd must stay open for the device to exist.
try:
    _tun = os.open('/dev/net/tun', os.O_RDWR)
    fcntl.ioctl(_tun, 0x400454ca, struct.pack('16sH14s', b'mh0', 0x1002, b''))   # TUNSETIFF, IFF_TUN|IFF_NO_PI
    _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _sa = lambda ip: struct.pack('H2s4s8s', socket.AF_INET, b'\0\0', socket.inet_aton(ip), b'')
    fcntl.ioctl(_s, 0x8916, struct.pack('16s', b'mh0') + _sa('10.200.0.2'))        # SIOCSIFADDR
    fcntl.ioctl(_s, 0x891c, struct.pack('16s', b'mh0') + _sa('255.255.255.0'))     # SIOCSIFNETMASK
    _fl = struct.unpack('16sH14s', fcntl.ioctl(_s, 0x8913, struct.pack('16sH14s', b'mh0', 0, b'')))[1]
    fcntl.ioctl(_s, 0x8914, struct.pack('16sH14s', b'mh0', _fl | 1 | 0x40, b''))   # UP|RUNNING
    _rt = struct.pack('L', 0) + _sa('0.0.0.0') + _sa('10.200.0.1') + _sa('0.0.0.0') + struct.pack('HLLHHL', 3, 0, 0, 0, 0, 0) + b'\0' * 24
    fcntl.ioctl(_s, 0x890B, _rt)                                                    # SIOCADDRT default via 10.200.0.1
except Exception as _e:
    print('namespace online-interface setup failed:', _e)
