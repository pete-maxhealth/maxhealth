// Run with: node tests/worker/worker_allowance.mjs   (copies worker.js to a temp .mjs first)
import fs from 'fs'; import os from 'os'; import path from 'path'; import crypto from 'crypto';
const tmp = path.join(os.tmpdir(), 'mh_worker_test.mjs'); fs.copyFileSync(new URL('../../worker.js', import.meta.url), tmp);
const worker = (await import(tmp)).default;
let fails = 0; const bad = (m) => { fails++; console.log('FAIL', m); };
const store = new Map();
const KV = { get: async k => store.has(k) ? store.get(k) : null, put: async (k, v) => { store.set(k, v); } };
let upstream = [];
globalThis.fetch = async (url, init) => { upstream.push({ url, body: JSON.parse(init.body) }); return new Response(JSON.stringify({ content: [{ type: 'text', text: 'ok' }] }), { headers: { 'Content-Type': 'application/json' } }); };
const env = { RATE_LIMIT_KV: KV, ANTHROPIC_API_KEY: 'k', LICENCE_SECRET: 'sekrit' };
const call = (headers = {}, body = { messages: [{ role: 'user', content: 'hi' }] }) =>
  worker.fetch(new Request('https://w.test/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.1.1.1', ...headers }, body: JSON.stringify(body) }), env);
const dev = 'device_abcdefghijklmnop';
// 1. starter counts down
let r = await call({ 'X-MH-Device': dev });
if (r.status !== 200 || r.headers.get('X-MH-Remaining') !== '59' || r.headers.get('X-MH-Tier') !== 'starter') bad('first starter call ' + r.status + ' ' + r.headers.get('X-MH-Remaining'));
for (let i = 0; i < 59; i++) r = await call({ 'X-MH-Device': dev });
if (r.headers.get('X-MH-Remaining') !== '0') bad('after 60 calls remaining=' + r.headers.get('X-MH-Remaining'));
// 2. top-up of 5 then block
let ok = 0; for (let i = 0; i < 7; i++) { r = await call({ 'X-MH-Device': dev }); if (r.status === 200) ok++; }
if (ok !== 5 || r.status !== 429) bad(`top-up gave ${ok} ok, last ${r.status}`);
if (!(await r.json()).error.message.includes('starter')) bad('block message not friendly');
// 3. old app (no device header) still works, no allowance headers
r = await call({}); if (r.status !== 200 || r.headers.get('X-MH-Remaining') !== null) bad('tokenless call changed behaviour');
// 4. junk device id ignored (treated like an old app)
r = await call({ 'X-MH-Device': 'x' }); if (r.status !== 200 || r.headers.get('X-MH-Remaining') !== null) bad('short device id not ignored');
// 5. licence token
const mk = (payload, secret = 'sekrit') => { const p = Buffer.from(JSON.stringify(payload)).toString('base64url'); return p + '.' + crypto.createHmac('sha256', secret).update(p).digest('base64url'); };
const good = mk({ id: 'L1', tier: 'premium', exp: Math.floor(Date.now() / 1000) + 3600 });
r = await call({ 'X-MH-Device': dev, 'X-MH-Licence': good }); if (r.status !== 200 || r.headers.get('X-MH-Tier') !== 'premium' || r.headers.get('X-MH-Remaining') !== '29') bad('valid licence not honoured ' + r.status + r.headers.get('X-MH-Tier'));
r = await call({ 'X-MH-Device': dev, 'X-MH-Licence': mk({ id: 'L1', exp: 1 }) }); if (r.headers.get('X-MH-Tier') === 'premium') bad('expired licence accepted');
r = await call({ 'X-MH-Device': dev, 'X-MH-Licence': mk({ id: 'L1' }, 'wrong') }); if (r.headers.get('X-MH-Tier') === 'premium') bad('forged licence accepted');
r = await call({ 'X-MH-Device': dev, 'X-MH-Licence': good.slice(0, -3) + 'abc' }); if (r.headers.get('X-MH-Tier') === 'premium') bad('tampered licence accepted');
// 5b. licence: daily cap 30, not stopped by the 80-per-connection cap, own monthly pool
const lic2 = mk({ id: 'L2', tier: 'premium', exp: Math.floor(Date.now() / 1000) + 3600 });
let okL = 0; for (let i = 0; i < 33; i++) { r = await call({ 'X-MH-Licence': lic2 }); if (r.status === 200) okL++; }
if (okL !== 30 || r.status !== 429) bad(`licence daily gave ${okL} ok, last ${r.status}`);
for (const k of [...store.keys()]) if (k.startsWith('calls:day:')) store.delete(k);
const before = [...store.keys()].filter(k => k.startsWith('calls:day:')).length;
r = await call({ 'X-MH-Licence': mk({ id: 'L3', tier: 'founder', exp: Math.floor(Date.now() / 1000) + 3600 }) });
if (r.status !== 200 || [...store.keys()].filter(k => k.startsWith('calls:day:')).length !== before) bad('licensed call used the per-connection cap');
const lm = [...store.keys()].find(k => k.startsWith('calls:month-lic:')); if (!lm) bad('no licensed monthly pool key');
store.set(lm, '10000'); r = await call({ 'X-MH-Licence': lic2 }); if (r.status !== 429) bad('licensed monthly cap not enforced ' + r.status);
store.set(lm, '0');
// free pool unaffected by licensed use, and full free pool does not block licensed users
const fm = [...store.keys()].find(k => k.startsWith('calls:month:') && !k.includes('lic')); store.set(fm, '5000');
r = await call({ 'X-MH-Licence': mk({ id: 'L4', tier: 'premium', exp: Math.floor(Date.now() / 1000) + 3600 }) }); if (r.status !== 200) bad('full free pool blocked a licensed user ' + r.status);
r = await call({}); if (r.status !== 429) bad('full free pool did not block a free user'); store.set(fm, '0');
// 6. model / tokens / tools hardening
upstream = [];
await call({}, { model: 'claude-opus-9', max_tokens: 99999, messages: [], tools: [{ type: 'bash_20250124', name: 'x' }, { type: 'web_search_20250305', name: 'web_search', max_uses: 500 }] });
const u = upstream[0].body; if (u.model !== 'claude-sonnet-4-6') bad('model not allow-listed ' + u.model); if (u.max_tokens !== 2500) bad('max_tokens uncapped ' + u.max_tokens);
if (!u.tools || u.tools.length !== 1 || u.tools[0].max_uses !== 3 || u.tools[0].type !== 'web_search_20250305') bad('tools not restricted ' + JSON.stringify(u.tools));
// 7. preflight exposes headers
r = await worker.fetch(new Request('https://w.test/', { method: 'OPTIONS' })); if (!/X-MH-Device/.test(r.headers.get('Access-Control-Allow-Headers') || '')) bad('preflight missing X-MH-Device');
console.log('worker findings', fails); process.exit(fails ? 1 : 0);
