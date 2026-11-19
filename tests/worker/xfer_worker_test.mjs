// Code transfer on the licence Worker: node tests/worker/xfer_worker_test.mjs
import worker from '../../licence-worker.js';
import assert from 'node:assert/strict';
const store = new Map();
const env = { LICENCE_SECRET: 's'.repeat(40), ADMIN_SECRET: 'admin-secret-1234', LICENCE_KV: {
  async get(k, t) { const v = store.get(k); if (v === undefined) return null; return t === 'arrayBuffer' ? new TextEncoder().encode(v).buffer : v; },
  async put(k, v) { store.set(k, typeof v === 'string' ? v : new TextDecoder().decode(v)); },
  async delete(k) { store.delete(k); } } };
let ipn = 1;
const post = async (o, ip) => { const r = await worker.fetch(new Request('https://w.test/', { method: 'POST', headers: { 'CF-Connecting-IP': ip || '10.0.0.' + ipn }, body: JSON.stringify(o) }), env); return { status: r.status, j: await r.json() }; };
const dev = 'device-aaaaaaaaaaaaaaaaaaaa';
const issued = await post({ action: 'issue', admin: env.ADMIN_SECRET, tier: 'premium', max_devices: 5 });
assert.equal(issued.j.ok, true); assert.equal(issued.j.max_devices, 5);
const act = await post({ action: 'activate', key: issued.j.key, device: dev, label: 'test' });
assert.equal(act.j.ok, true); const token = act.j.token;
const blob = Buffer.from('ciphertext-pretend-0123456789').toString('base64');
// no licence: cannot send
assert.equal((await post({ action: 'xfer_put', blob, device: dev })).status, 403);
assert.equal((await post({ action: 'xfer_put', token: 'junk', blob, device: dev })).status, 403);
// bad payloads
assert.equal((await post({ action: 'xfer_put', token, device: dev, blob: 'short' })).status, 400);
assert.equal((await post({ action: 'xfer_put', token, device: dev, blob: 'A'.repeat(4000001) })).status, 413);
// send, then receive WITHOUT a licence (free user), once only
const put = await post({ action: 'xfer_put', token, device: dev, blob }); assert.equal(put.status, 200); assert.match(put.j.code, /^[ABCDEFGHJKMNPQRSTUVWXYZ2-9]{8}$/);
const got = await post({ action: 'xfer_get', code: put.j.code.slice(0, 4).toLowerCase() + '-' + put.j.code.slice(4) }); assert.equal(got.status, 200); assert.equal(got.j.blob, blob);
assert.equal((await post({ action: 'xfer_get', code: put.j.code })).status, 404, 'second download must fail');
assert.equal([...store.keys()].some(k => k.startsWith('x:')), false, 'nothing left stored');
// malformed code
assert.equal((await post({ action: 'xfer_get', code: 'ABC' })).status, 400);
// wrong guesses are limited (10 then locked), real codes from that address are then refused too
ipn = 77; let last;
for (let i = 0; i < 10; i++) last = await post({ action: 'xfer_get', code: 'ZZZZZZZZ' }, '10.9.9.9'); assert.equal(last.status, 404);
const locked = await post({ action: 'xfer_get', code: 'ZZZZZZZZ' }, '10.9.9.9'); assert.equal(locked.status, 429);
// sends are limited per address (20 an hour)
let n = 0, st = 200; while (st === 200 && n < 30) { st = (await post({ action: 'xfer_put', token, device: dev, blob }, '10.8.8.8')).status; if (st === 200) n++; }
assert.equal(n, 20); assert.equal(st, 429);
console.log('xfer worker: all passed');
