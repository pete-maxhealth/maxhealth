// Run with: node tests/worker/worker_ping.mjs   (anonymous install count: GET /ping and POST /admin/usage)
import fs from 'fs'; import os from 'os'; import path from 'path';
const tmp = path.join(os.tmpdir(), 'mh_worker_ping_test.mjs'); fs.copyFileSync(new URL('../../worker.js', import.meta.url), tmp);
const worker = (await import(tmp)).default;
let fails = 0; const bad = (m) => { fails++; console.log('FAIL', m); };
const store = new Map(); let puts = 0;
const KV = {
  get: async k => store.has(k) ? store.get(k).v : null,
  getWithMetadata: async k => store.has(k) ? { value: store.get(k).v, metadata: store.get(k).m } : { value: null, metadata: null },
  put: async (k, v, o) => { puts++; store.set(k, { v, m: o && o.metadata }); },
  delete: async k => { store.delete(k); },
  list: async ({ prefix }) => ({ keys: [...store.entries()].filter(([k]) => k.startsWith(prefix)).map(([name, x]) => ({ name, metadata: x.m })), list_complete: true }),
};
const env = { RATE_LIMIT_KV: KV, ADMIN_SECRET: 'adm' };
const ping = (dev, v = '3.10.1331', headers = {}) => worker.fetch(new Request('https://w.test/ping?v=' + v, { method: 'GET', headers: { 'CF-Connecting-IP': '9.9.9.9', ...(dev ? { 'X-MH-Device': dev } : {}), ...headers } }), env);
const usage = (secret) => worker.fetch(new Request('https://w.test/admin/usage', { method: 'POST', headers: secret ? { 'X-MH-Admin': secret } : {} }), env);
const iso = (n) => new Date(Date.now() - n * 86400000).toISOString().slice(0, 10);
// 1. a ping is stored, with no IP and nothing but first/last day and version
let r = await ping('device_aaaaaaaaaaaaaaaa');
if (r.status !== 204) bad('ping status ' + r.status);
const rec = store.get('act:device_aaaaaaaaaaaaaaaa');
if (!rec || rec.m.f !== iso(0) || rec.m.l !== iso(0) || rec.m.v !== '3.10.1331') bad('record wrong ' + JSON.stringify(rec));
if (JSON.stringify([...store.entries()]).includes('9.9.9.9')) bad('IP address was stored');
// 2. same install, same day, same version: no second write
const before = puts; await ping('device_aaaaaaaaaaaaaaaa'); if (puts !== before) bad('wrote again on the same day');
// 3. junk or missing code is ignored; junk version is dropped
await ping(''); await ping('x'); await ping('bad code with spaces!!!');
if ([...store.keys()].length !== 1) bad('junk device code was stored');
await ping('device_bbbbbbbbbbbbbbbb', '<script>'); if (store.get('act:device_bbbbbbbbbbbbbbbb').m.v !== '') bad('junk version stored');
// 4. usage totals: seed older installs
const seed = (dev, f, l, v) => store.set('act:' + dev, { v: '1', m: { f, l, v } });
seed('device_old30_aaaaaaaaaa', iso(25), iso(20), '3.10.1300');   // active 30d only
seed('device_old3_aaaaaaaaaaa', iso(40), iso(3), '3.10.1320');    // active 7d, not new
seed('device_ancient_aaaaaaaa', iso(90), iso(60), '3.10.1200');   // ever seen only
r = await usage('adm'); const u = await r.json();
if (u.installsEverSeen !== 5 || u.activeToday !== 2 || u.active7d !== 3 || u.active30d !== 4 || u.new7d !== 2 || u.new30d !== 3) bad('usage totals ' + JSON.stringify(u));
if (u.byVersion7d['3.10.1331'] !== 1 || u.byVersion7d['3.10.1320'] !== 1 || u.byVersion7d['unknown'] !== 1) bad('byVersion ' + JSON.stringify(u.byVersion7d));
// 5. admin is locked
r = await usage('wrong'); if (r.status !== 403) bad('wrong secret accepted ' + r.status);
r = await usage(''); if (r.status !== 403) bad('no secret accepted ' + r.status);
r = await worker.fetch(new Request('https://w.test/admin/usage', { method: 'GET' }), env); if (r.status !== 405) bad('GET usage ' + r.status);
// 6. KV missing or failing: ping still answers quietly
r = await worker.fetch(new Request('https://w.test/ping', { method: 'GET', headers: { 'X-MH-Device': 'device_cccccccccccccccc' } }), {}); if (r.status !== 204) bad('no KV: ' + r.status);
r = await worker.fetch(new Request('https://w.test/ping', { method: 'GET', headers: { 'X-MH-Device': 'device_dddddddddddddddd' } }), { RATE_LIMIT_KV: { getWithMetadata: async () => { throw new Error('KV down'); } } }); if (r.status !== 204) bad('KV error: ' + r.status);
// 7. an old app still works: POST path and other GETs are unchanged
r = await worker.fetch(new Request('https://w.test/', { method: 'GET' }), env); if (r.status !== 405) bad('plain GET changed ' + r.status);
console.log(fails ? fails + ' failed' : 'worker_ping ok'); process.exit(fails ? 1 : 0);
