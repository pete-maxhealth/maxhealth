"""
_winzip_aes.py - read WinZip-AES encrypted zips (compression method 99) with the standard library.

Python's zipfile cannot open these ("That compression method is not supported"), and Zepp/Amazfit
"Export your data" zips use this encryption, so the extractor's password option never worked on a
real export - people had to extract with ZArchiver first. This adds a small ZipFile-like wrapper:
  z = open_aes_zip(path, password)   ->  z.namelist(), z.read(name), z.close(), context manager
Plain (unencrypted / ZipCrypto) entries are passed through to zipfile.
Uses the `cryptography` package for AES when present (fast); otherwise a built-in pure-Python AES
(slower, ~seconds per MB) so nothing extra has to be installed.
"""
import hashlib, hmac, struct, zlib, zipfile

# ── minimal pure-Python AES (encrypt only; CTR needs nothing else) ──────────────
_SBOX = None
def _init_sbox():
    global _SBOX
    if _SBOX: return
    p = q = 1; sbox = [0] * 256
    while True:
        p = p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)
        q ^= q << 1; q ^= q << 2; q ^= q << 4; q &= 0xFF
        if q & 0x80: q ^= 0x09
        x = q ^ ((q << 1) | (q >> 7)) & 0xFF ^ ((q << 2) | (q >> 6)) & 0xFF ^ ((q << 3) | (q >> 5)) & 0xFF ^ ((q << 4) | (q >> 4)) & 0xFF
        sbox[p] = (x ^ 0x63) & 0xFF
        if p == 1: break
    sbox[0] = 0x63
    _SBOX = sbox

def _xt(a): return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else a << 1

def _expand_key(key):
    _init_sbox(); nk = len(key) // 4; nr = nk + 6
    w = [list(key[4*i:4*i+4]) for i in range(nk)]; rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i-1])
        if i % nk == 0:
            t = t[1:] + t[:1]; t = [_SBOX[b] for b in t]; t[0] ^= rcon; rcon = _xt(rcon)
        elif nk > 6 and i % nk == 4:
            t = [_SBOX[b] for b in t]
        w.append([w[i-nk][j] ^ t[j] for j in range(4)])
    return [sum(w[4*r:4*r+4], []) for r in range(nr + 1)], nr

def _enc_block(block, rk, nr):
    s = [b ^ k for b, k in zip(block, rk[0])]
    for r in range(1, nr + 1):
        s = [_SBOX[b] for b in s]
        s = [s[0], s[5], s[10], s[15], s[4], s[9], s[14], s[3], s[8], s[13], s[2], s[7], s[12], s[1], s[6], s[11]]
        if r != nr:
            o = []
            for c in range(4):
                a0, a1, a2, a3 = s[4*c:4*c+4]
                o += [_xt(a0) ^ (_xt(a1) ^ a1) ^ a2 ^ a3, a0 ^ _xt(a1) ^ (_xt(a2) ^ a2) ^ a3,
                      a0 ^ a1 ^ _xt(a2) ^ (_xt(a3) ^ a3), (_xt(a0) ^ a0) ^ a1 ^ a2 ^ _xt(a3)]
            s = o
        s = [b ^ k for b, k in zip(s, rk[r])]
    return bytes(s)

def _keystream(key, nblocks):
    """WinZip AES uses AES-CTR with a LITTLE-endian counter starting at 1."""
    counters = b''.join(struct.pack('<Q', i) + b'\0' * 8 for i in range(1, nblocks + 1))
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        e = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
        return e.update(counters) + e.finalize()
    except ImportError:
        rk, nr = _expand_key(key)
        return b''.join(_enc_block(counters[i:i+16], rk, nr) for i in range(0, len(counters), 16))

def _xor(a, b):
    return (int.from_bytes(a, 'big') ^ int.from_bytes(b, 'big')).to_bytes(len(a), 'big') if a else b''

def _decrypt_entry(raw, password, strength):
    keylen = {1: 16, 2: 24, 3: 32}[strength]; saltlen = keylen // 2
    salt, verifier, body, auth = raw[:saltlen], raw[saltlen:saltlen+2], raw[saltlen+2:-10], raw[-10:]
    dk = hashlib.pbkdf2_hmac('sha1', password, salt, 1000, 2 * keylen + 2)
    if dk[2*keylen:] != verifier:
        raise RuntimeError('Bad password')
    if hmac.new(dk[keylen:2*keylen], body, hashlib.sha1).digest()[:10] != auth:
        raise RuntimeError('Encrypted data failed its integrity check')
    ks = _keystream(dk[:keylen], (len(body) + 15) // 16)
    return _xor(body, ks[:len(body)])


class AESZip:
    def __init__(self, path, password=None):
        self._zf = zipfile.ZipFile(path, 'r'); self._path = path
        self._pw = password.encode('utf-8') if isinstance(password, str) else password
    def setpassword(self, pw): self._pw = pw.encode('utf-8') if isinstance(pw, str) else pw
    def namelist(self): return self._zf.namelist()
    def infolist(self): return self._zf.infolist()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def close(self): self._zf.close()
    def read(self, name):
        info = self._zf.getinfo(name)          # KeyError if missing, like zipfile
        if info.compress_type != 99:
            return self._zf.read(info, pwd=self._pw)
        if not self._pw:
            raise RuntimeError('File is encrypted, password required')
        with open(self._path, 'rb') as f:
            f.seek(info.header_offset)
            hdr = f.read(30)
            nlen, elen = struct.unpack('<HH', hdr[26:30])
            f.seek(info.header_offset + 30 + nlen)
            extra = f.read(elen)
            f.seek(info.header_offset + 30 + nlen + elen)
            raw = f.read(info.compress_size)
        strength = method = None; i = 0
        while i + 4 <= len(extra):
            tag, size = struct.unpack('<HH', extra[i:i+4])
            if tag == 0x9901:
                _ver, _vendor, strength, method = struct.unpack('<H2sBH', extra[i+4:i+11]); break
            i += 4 + size
        if strength is None:
            raise RuntimeError('Unrecognised encryption header')
        data = _decrypt_entry(raw, self._pw, strength)
        return zlib.decompress(data, -15) if method == 8 else data


def has_aes(path):
    try:
        with zipfile.ZipFile(path) as z:
            return any(i.compress_type == 99 for i in z.infolist())
    except Exception:
        return False


def open_aes_zip(path, password=None):
    return AESZip(path, password)
