// node tests/worker/licence_devices.mjs  -> exits 1 on any failure. v3.10.1408: device-bound tokens, self-service moves, households.
import fs from 'fs'; import os from 'os'; import path from 'path'; import crypto from 'crypto';
const tmp = path.join(os.tmpdir(), 'mh_licence_worker2.mjs'); fs.copyFileSync(new URL('../../licence-worker.js', import.meta.url), tmp);
const W = (await import(tmp)).default;
const tmp2 = path.join(os.tmpdir(), 'mh_worker_main2.mjs'); fs.copyFileSync(new URL('../../worker.js', import.meta.url), tmp2);
const AI = (await import(tmp2)).default;
const store = new Map();
const KV = { get: async (k, t) => { const v = store.get(k); if (v === undefined) return null; if (t === 'arrayBuffer') return typeof v === 'string' ? new TextEncoder().encode(v).buffer : v; return typeof v === 'string' ? v : new TextDecoder().decode(v); }, put: async (k, v) => { store.set(k, v); } };
const env = { LICENCE_KV: KV, LICENCE_SECRET: 's'.repeat(40), ADMIN_SECRET: 'a'.repeat(40) };
let fails = 0; const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++; };
const D = n => 'device_' + String(n).padStart(16, 'x');
const post = (o, ip = '1.1.1.1') => W.fetch(new Request('https://l.test/', { method: 'POST', headers: { 'CF-Connecting-IP': ip }, body: JSON.stringify(o) }), env);
const get = (p, h = {}) => W.fetch(new Request('https://l.test' + p, { headers: h }), env);
const aiStore = new Map(); const aiKV = { get: async k => aiStore.get(k) ?? null, put: async (k, v) => { aiStore.set(k, v); } };
globalThis.fetch = async () => new Response(JSON.stringify({ content: [{ type: 'text', text: 'ok' }] }));
const ai = (tok, dev) => AI.fetch(new Request('https://w.test/', { method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json', 'X-MH-Licence': tok }, dev ? { 'X-MH-Device': dev } : {}), body: '{"messages":[]}' }), { RATE_LIMIT_KV: aiKV, LICENCE_SECRET: env.LICENCE_SECRET, ANTHROPIC_API_KEY: 'k' }).then(r => r.headers.get('X-MH-Tier'));
const issue = async (o = {}) => (await (await post(Object.assign({ action: 'issue', admin: env.ADMIN_SECRET, tier: 'premium' }, o))).json());

const k1 = (await issue()).key;
let r = await (await post({ action: 'activate', key: k1, device: D(1), label: "Pete's phone" })).json();
const tok1 = r.token; const pl = JSON.parse(Buffer.from(tok1.split('.')[0], 'base64url').toString());
ok(r.ok && pl.dev && pl.dev.length === 12, 'token carries a device claim');
ok(pl.dev === crypto.createHash('sha256').update(D(1)).digest('hex').slice(0, 12), 'claim is the hash of this device code, not the code itself');
ok(await ai(tok1, D(1)) === 'premium', 'AI worker: right device is licensed');
ok(await ai(tok1, D(2)) !== 'premium', 'AI worker: a copied token on another device is NOT licensed');
ok(await ai(tok1, null) !== 'premium', 'AI worker: token without a device header is NOT licensed');
// old-style token (no claim) keeps working until it expires
const hm = crypto.createHmac('sha256', env.LICENCE_SECRET); const op = Buffer.from(JSON.stringify({ id: 'abc', tier: 'premium', exp: Math.floor(Date.now() / 1000) + 3600 })).toString('base64url');
const oldTok = op + '.' + hm.update(op).digest('base64url');
ok(await ai(oldTok, D(9)) === 'premium', 'AI worker: a token issued before this change still works');
// launcher download honours the device when given
await W.fetch(new Request('https://l.test/admin/put/launcher:apk', { method: 'PUT', headers: { 'X-MH-Admin': env.ADMIN_SECRET }, body: new Uint8Array(1000) }), env);
ok((await get('/launcher/download?t=' + encodeURIComponent(tok1) + '&d=' + D(1))).status === 200, 'launcher: right device downloads');
ok((await get('/launcher/download?t=' + encodeURIComponent(tok1) + '&d=' + D(2))).status === 403, 'launcher: copied token on another device refused');
ok((await get('/launcher/download?t=' + encodeURIComponent(tok1))).status === 200, 'launcher: a call with no device (the launcher app) still works');
// household: second phone on the same key and the same connection
r = await post({ action: 'activate', key: k1, device: D(2), label: 'Jill phone' }); ok(r.status === 200, 'second device on the same key and connection is fine');
r = await post({ action: 'activate', key: k1, device: D(3) }); const full = await r.json();
ok(r.status === 409 && full.code === 'devices_full', 'third device is told the key is full');
// self-service move
let L = await (await post({ action: 'devices', key: k1, device: D(3) })).json();
ok(L.ok && L.devices.length === 2 && L.max === 2 && L.moves_left === 3, 'device list shown to the key holder');
ok(L.devices.some(d => d.label === "Pete's phone") && L.devices.every(d => !d.here), 'labels shown, the asking phone is not on the list');
ok(!JSON.stringify(L).includes(D(1)), 'full device codes are never returned');
const target = L.devices.find(d => d.label === 'Jill phone').id;
r = await (await post({ action: 'release', key: k1, device: D(3), target })).json();
ok(r.ok && r.devices.length === 1 && r.moves_left === 2, 'a slot can be freed');
ok((await post({ action: 'activate', key: k1, device: D(3) })).status === 200, 'the new phone can now activate');
ok(await ai((await (await post({ action: 'activate', key: k1, device: D(3) })).json()).token, D(3)) === 'premium', 'and is licensed');
// the old phone keeps its token only until it expires; a refresh is refused
ok((await post({ action: 'activate', key: k1, device: D(2) })).status === 409, 'released phone cannot renew');
// churn limit
for (let i = 0; i < 2; i++) { const l = await (await post({ action: 'devices', key: k1, device: D(10 + i) })).json(); const t = l.devices[0].id; await post({ action: 'release', key: k1, device: D(10 + i), target: t }); await post({ action: 'activate', key: k1, device: D(10 + i) }); }
L = await (await post({ action: 'devices', key: k1, device: D(20) })).json(); ok(L.moves_left === 0, 'moves counted');
r = await post({ action: 'release', key: k1, device: D(20), target: L.devices[0].id }); const rj = await r.json();
ok(r.status === 403 && rj.code === 'moves_used', 'a key cannot be passed round: moves are limited per 30 days');
// wrong key / admin
ok((await post({ action: 'devices', key: 'NOPE-NOPE-NOPE-NOPE', device: D(3) })).status === 403, 'devices needs a real key');
ok((await post({ action: 'inspect', key: k1, admin: 'bad' })).status === 403, 'inspect needs the admin secret');
const ins = await (await post({ action: 'inspect', key: k1, admin: env.ADMIN_SECRET })).json();
ok(ins.ok && ins.moves_30d === 3 && ins.devices.length === 2, 'developer inspect shows devices and moves');
// households: several keys, one connection, each independent; several trials from one connection
const k2 = (await issue({ max_devices: 4 })).key, k3 = (await issue()).key;
ok((await post({ action: 'activate', key: k2, device: D(31) }, '5.5.5.5')).status === 200 && (await post({ action: 'activate', key: k3, device: D(32) }, '5.5.5.5')).status === 200, 'two keys from one connection both activate');
let all = true; for (let i = 0; i < 4; i++) { const t = await post({ action: 'activate', key: k2, device: D(40 + i) }, '5.5.5.5'); if (i < 3 && t.status !== 200) all = false; }
ok(all, 'a household key with 4 devices takes 4 phones (one already used above)');
let trials = 0; for (let i = 0; i < 6; i++) if ((await post({ action: 'trial', device: D(60 + i) }, '6.6.6.6')).status === 200) trials++;
ok(trials === 6, 'six people on one connection can each start a trial');
console.log(fails ? fails + ' FAILED' : 'ALL PASSED'); process.exit(fails ? 1 : 0);
