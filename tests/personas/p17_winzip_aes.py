"""Persona 17: Zepp's AES-encrypted export zip. Public test vector for the pure-Python AES, a full
encrypt->decrypt round trip through the reader's own primitives, and a wrong-password refusal."""
import sys, os, hmac, hashlib, struct; sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'extractors'))
import _winzip_aes as w
f = []
bad = lambda m: (f.append(m), print('  [BUG]', m))
# FIPS-197 appendix C.1 (AES-128) and C.3 (AES-256)
for key, want in (('000102030405060708090a0b0c0d0e0f', '69c4e0d86a7b0430d8cdb78070b4c55a'),
                  ('000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f', '8ea2b7ca516745bfeafc49904b496089')):
    rk, nr = w._expand_key(bytes.fromhex(key))
    got = w._enc_block(bytes.fromhex('00112233445566778899aabbccddeeff'), rk, nr).hex()
    if got != want: bad(f'AES-{len(key)*4} test vector: {got} != {want}')
# round trip: encrypt like WinZip does, then decrypt with the reader
pw = b'correct horse'; data = os.urandom(5000) + b'ABC'
for strength, keylen in ((1, 16), (3, 32)):
    salt = os.urandom(keylen // 2); dk = hashlib.pbkdf2_hmac('sha1', pw, salt, 1000, 2 * keylen + 2)
    ks = w._keystream(dk[:keylen], (len(data) + 15) // 16)
    ct = bytes(a ^ b for a, b in zip(data, ks))
    raw = salt + dk[2*keylen:] + ct + hmac.new(dk[keylen:2*keylen], ct, hashlib.sha1).digest()[:10]
    if w._decrypt_entry(raw, pw, strength) != data: bad(f'round trip failed for strength {strength}')
    try: w._decrypt_entry(raw, b'wrong', strength); bad('wrong password was accepted')
    except RuntimeError as e:
        if 'Bad password' not in str(e): bad(f'wrong-password message: {e}')
    tampered = raw[:-20] + bytes([raw[-20] ^ 1]) + raw[-19:]
    try: w._decrypt_entry(tampered, pw, strength); bad('tampered data was accepted')
    except RuntimeError: pass
# the same keystream must come out of the pure-Python path and the `cryptography` path
try:
    import cryptography
    k = bytes(range(32)); a = w._keystream(k, 40)
    rk, nr = w._expand_key(k)
    b = b''.join(w._enc_block(struct.pack('<Q', i) + b'\0' * 8, rk, nr) for i in range(1, 41))
    if a != b: bad('pure-Python and cryptography keystreams differ')
except ImportError: pass
print('findings', len(f)); sys.exit(1 if f else 0)
