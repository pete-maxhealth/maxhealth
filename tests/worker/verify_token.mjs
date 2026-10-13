// usage: node verify_token.mjs <token> <secret>  -> prints the tier the Worker assigns
import fs from 'fs'; import os from 'os'; import path from 'path';
const tmp = path.join(os.tmpdir(), 'mh_worker_verify.mjs'); fs.copyFileSync(new URL('../../worker.js', import.meta.url), tmp);
const worker = (await import(tmp)).default;
const store = new Map(); const KV = { get: async k => store.get(k) ?? null, put: async (k, v) => { store.set(k, v); } };
globalThis.fetch = async () => new Response(JSON.stringify({ content: [{ type: 'text', text: 'ok' }] }));
const r = await worker.fetch(new Request('https://w.test/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-MH-Device': 'device_abcdefghijklmnop', 'X-MH-Licence': process.argv[2] }, body: '{"messages":[]}' }), { RATE_LIMIT_KV: KV, ANTHROPIC_API_KEY: 'k', LICENCE_SECRET: process.argv[3] });
console.log(r.headers.get('X-MH-Tier') || 'none');
