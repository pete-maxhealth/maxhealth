// node tests/worker/licence_worker.mjs  -> exits 1 on any failure
import fs from 'fs'; import os from 'os'; import path from 'path';
const tmp = path.join(os.tmpdir(), 'mh_licence_worker.mjs'); fs.copyFileSync(new URL('../../licence-worker.js', import.meta.url), tmp);
const W = (await import(tmp)).default;
const tmp2 = path.join(os.tmpdir(), 'mh_worker_main.mjs'); fs.copyFileSync(new URL('../../worker.js', import.meta.url), tmp2);
const AI = (await import(tmp2)).default;
const store = new Map();
const KV = { get: async (k, t) => { const v = store.get(k); if (v === undefined) return null; if (t === 'arrayBuffer') return typeof v === 'string' ? new TextEncoder().encode(v).buffer : v; return typeof v === 'string' ? v : new TextDecoder().decode(v); }, put: async (k, v) => { store.set(k, v); } };
const env = { LICENCE_KV: KV, LICENCE_SECRET: 's'.repeat(40), ADMIN_SECRET: 'a'.repeat(40) };
let fails = 0; const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) fails++; };
const DEV = 'device_abcdefghijklmnop', DEV2 = 'device_bbbbbbbbbbbbbbbb', DEV3 = 'device_cccccccccccccccc';
const post = (o, ip = '1.1.1.1') => W.fetch(new Request('https://l.test/', { method: 'POST', headers: { 'CF-Connecting-IP': ip }, body: JSON.stringify(o) }), env);
const get = (p, h = {}) => W.fetch(new Request('https://l.test' + p, { headers: h }), env);
const put = (p, body, adm = env.ADMIN_SECRET) => W.fetch(new Request('https://l.test' + p, { method: 'PUT', headers: { 'X-MH-Admin': adm }, body }), env);

// issue
ok((await post({ action: 'issue', admin: 'wrong' })).status === 403, 'issue refused without admin secret');
let r = await (await post({ action: 'issue', admin: env.ADMIN_SECRET, tier: 'premium', note: 'test' })).json();
ok(r.ok && /^[A-Z2-9]{4}(-[A-Z2-9]{4}){3}$/.test(r.key), 'issue returns a key ' + r.key);
const key = r.key;
ok(![...store.keys()].some(k => k.includes(key)) && ![...store.values()].some(v => typeof v === 'string' && v.includes(key)), 'plain key is never stored');
// activate
r = await (await post({ action: 'activate', key: key.toLowerCase(), device: DEV })).json();
ok(r.ok && r.tier === 'premium' && r.token, 'activate works (case-insensitive key)');
const tok = r.token;
// token accepted by the AI worker's verifier
const aiStore = new Map(); const aiKV = { get: async k => aiStore.get(k) ?? null, put: async (k, v) => { aiStore.set(k, v); } };
globalThis.fetch = async () => new Response(JSON.stringify({ content: [{ type: 'text', text: 'ok' }] }));
const ai = await AI.fetch(new Request('https://w.test/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-MH-Device': DEV, 'X-MH-Licence': tok }, body: '{"messages":[]}' }), { RATE_LIMIT_KV: aiKV, ANTHROPIC_API_KEY: 'k', LICENCE_SECRET: env.LICENCE_SECRET });
ok(ai.headers.get('X-MH-Tier') === 'premium', 'AI worker accepts the token as premium');
// device cap
await post({ action: 'activate', key, device: DEV2 });
ok((await post({ action: 'activate', key, device: DEV3 })).status === 409, 'third device refused');
ok((await post({ action: 'activate', key, device: DEV })).status === 200, 'known device can refresh');
// bad key + throttle
for (let i = 0; i < 8; i++) await post({ action: 'activate', key: 'NOPE-NOPE-NOPE-NOPE', device: DEV }, '9.9.9.9');
ok((await post({ action: 'activate', key: 'NOPE-NOPE-NOPE-NOPE', device: DEV }, '9.9.9.9')).status === 429, 'guessing is throttled');
// trial
r = await (await post({ action: 'trial', device: DEV3 }, '2.2.2.2')).json();
ok(r.ok && r.tier === 'trial' && r.days === 14, 'trial starts');
const trialTok = r.token;
r = await (await post({ action: 'trial', device: DEV3 }, '2.2.2.2')).json();
ok(r.ok && r.days <= 14, 'trial restarts only with remaining days');
// downloads
ok((await get('/launcher/download')).status === 403, 'launcher refused without token');
ok((await get('/launcher/download', { 'X-MH-Licence': trialTok })).status === 403, 'launcher refused for trial token');
ok((await get('/launcher/download', { 'X-MH-Licence': tok })).status === 404, 'launcher 404 before upload');
ok((await put('/admin/put/launcher:apk', 'x', 'bad')).status === 403, 'upload refused without admin');
ok((await put('/admin/put/other', 'x')).status === 400, 'upload refuses unknown name');
const apk = new Uint8Array(300000).map((_, i) => i % 251);
r = await (await put('/admin/put/launcher:apk', apk)).json();
ok(r.ok && r.bytes === 300000 && r.sha256.length === 64, 'APK upload returns size + sha256');
let d = await get('/launcher/download?t=' + encodeURIComponent(tok));
const body = new Uint8Array(await d.arrayBuffer());
ok(d.status === 200 && body.length === 300000 && body[1000] === 1000 % 251 && /android/.test(d.headers.get('Content-Type')), 'premium token downloads identical APK (?t=)');
d = await get('/launcher/download', { 'X-MH-Licence': tok });
ok(d.status === 200, 'premium token downloads via header');
ok((await put('/admin/put/launcher:version', '{"nope":1}')).status === 400, 'bad version.json refused');
ok((await get('/launcher/version.json')).status === 404, 'version 404 before upload');
await put('/admin/put/launcher:version', '{"versionCode":15,"versionName":"1.5.1"}');
const v = await (await get('/launcher/version.json')).json();
ok(v.versionCode === 15 && !JSON.stringify(v).includes('http'), 'version.json public, no download link');
const pg=await get('/launcher/get'); const pgt=await pg.text();
ok(pg.status===200&&/text\/html/.test(pg.headers.get('Content-Type'))&&pgt.includes('/launcher/download?t='), 'download page served');
// premium payload
await put('/admin/put/payload:zip', 'PKzip');
ok((await post({ action: 'download', token: trialTok })).status === 200, 'payload downloads with any valid token');
ok((await post({ action: 'download', token: 'junk.junk' })).status === 403, 'payload refused for bad token');
// revoke
ok((await post({ action: 'revoke', admin: env.ADMIN_SECRET, key })).status === 200, 'revoke works');
ok((await post({ action: 'activate', key, device: DEV })).status === 403, 'revoked key cannot activate');
// expired token
const [p] = tok.split('.'); const pl = JSON.parse(Buffer.from(p, 'base64url').toString()); pl.exp = 1;
const p2 = Buffer.from(JSON.stringify(pl)).toString('base64url');
ok((await get('/launcher/download', { 'X-MH-Licence': p2 + '.' + tok.split('.')[1] })).status === 403, 'tampered/expired token refused');
console.log(fails ? fails + ' FAILED' : 'ALL PASSED'); process.exit(fails ? 1 : 0);
