// MaxedHealth licence + launcher download Worker (v3.10.1249).
// Replaces premium-site/licence.php (which needed PHP hosting) and moves the launcher APK off public GitHub.
//
// One Cloudflare Worker, one KV namespace (binding LICENCE_KV), two secrets:
//   LICENCE_SECRET  must be exactly the value the AI Worker (worker.js) already uses to verify tokens
//   ADMIN_SECRET    a long random value only you know; needed to issue/revoke keys and to upload files
//
// Same JSON protocol the app already speaks (POST { action: 'activate' | 'trial' | 'download' | 'issue' | 'revoke', ... }),
// so the app only needs its licence address changed. Added on top:
//   GET  /launcher/version.json   public: what the installed launcher compares against (no download link inside)
//   GET  /launcher/get            small page: paste a licence key, the APK downloads (the launcher's update banner opens this)
//   GET  /launcher/download       needs a founder or premium licence token (header X-MH-Licence or ?t=): streams the APK
//   PUT  /admin/put/<name>        needs X-MH-Admin: stores launcher:apk, launcher:version or payload:zip (each up to 25 MB, a KV limit)
// Keys are stored only as SHA-256 hashes, so a lost key cannot be looked up: revoke it and issue another.

const TOKEN_DAYS = 30;          // the app re-issues a token automatically while the key stays valid
const TRIAL_DAYS = 14;
const MAX_DEVICES = 2;          // devices one paid key may be bound to (founder keys: 5)
const APK_TIERS = ['founder', 'premium'];   // a trial token never gets the launcher
const BLOBS = {
	'launcher:apk':     { max: 25000000 },
	'launcher:version': { max: 4096 },
	'payload:zip':      { max: 25000000 },
};
const CORS = {
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
	'Access-Control-Allow-Headers': 'Content-Type, X-MH-Licence, X-MH-Admin',
};


// Plain download page the launcher's update banner opens: paste the licence key once, the APK downloads.
const GET_PAGE = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MaxedHealth launcher download</title>
<style>body{font:16px system-ui,sans-serif;background:#080a0d;color:#e8eef2;margin:0;padding:24px;max-width:460px}h1{font-size:20px}input,button{font:inherit;width:100%;box-sizing:border-box;padding:12px;margin-top:10px;border-radius:8px;border:1px solid #2debaf55}input{background:#10151b;color:inherit}button{background:#2debaf;color:#080a0d;border:0;font-weight:600}#m{margin-top:14px;min-height:1.4em}</style></head><body>
<h1>MaxedHealth Sync: download</h1><p>Enter your licence key to download the latest launcher.</p>
<input id="k" placeholder="XXXX-XXXX-XXXX-XXXX" autocomplete="off" autocapitalize="characters"><button id="b">Download</button><div id="m"></div>
<script>
const m=document.getElementById('m');let d;try{d=localStorage.getItem('mh_dev')}catch(e){}
if(!d){d='web_'+[...crypto.getRandomValues(new Uint8Array(12))].map(b=>b.toString(16).padStart(2,'0')).join('');try{localStorage.setItem('mh_dev',d)}catch(e){}}
document.getElementById('b').onclick=async()=>{m.textContent='Checking…';
try{const r=await fetch('/',{method:'POST',body:JSON.stringify({action:'activate',key:document.getElementById('k').value,device:d})});const j=await r.json();
if(!j.ok){m.textContent=j.error||'That did not work.';return}
if(j.tier!=='founder'&&j.tier!=='premium'){m.textContent='This key cannot download the launcher.';return}
m.textContent='Starting your download…';location.href='/launcher/download?t='+encodeURIComponent(j.token);setTimeout(()=>{m.textContent='Download started. Check your Downloads. You can close this page.'},2500)}catch(e){m.textContent='No connection. Please try again.'}};
</script></body></html>`;

const enc = new TextEncoder();
function reply(code, obj) { return new Response(JSON.stringify(obj), { status: code, headers: { 'Content-Type': 'application/json; charset=utf-8', 'X-Content-Type-Options': 'nosniff', ...CORS } }); }
function b64u(bytes) { let s = ''; bytes = new Uint8Array(bytes); for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]); return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
function fromB64u(s) { s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; const bin = atob(s); const o = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) o[i] = bin.charCodeAt(i); return o; }
async function sha256hex(data) { const d = await crypto.subtle.digest('SHA-256', typeof data === 'string' ? enc.encode(data) : data); return [...new Uint8Array(d)].map(b => b.toString(16).padStart(2, '0')).join(''); }
async function hmacKey(secret, usage) { return crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, usage); }

// Compare two secrets without leaking where they differ: hash both to equal length, then compare every byte.
async function sameSecret(a, b) {
	const x = await sha256hex(String(a || '')), y = await sha256hex(String(b || ''));
	let d = 0; for (let i = 0; i < x.length; i++) d |= x.charCodeAt(i) ^ y.charCodeAt(i);
	return d === 0;
}

// Token format shared with worker.js: base64url(JSON payload) + "." + base64url(HMAC-SHA256(payload, LICENCE_SECRET)).
async function makeToken(env, id, tier, days) {
	const p = b64u(enc.encode(JSON.stringify({ id, tier, exp: Math.floor(Date.now() / 1000) + days * 86400 })));
	const sig = await crypto.subtle.sign('HMAC', await hmacKey(env.LICENCE_SECRET, ['sign']), enc.encode(p));
	return p + '.' + b64u(sig);
}
async function verifyToken(env, token) {
	try {
		if (!token || !env.LICENCE_SECRET) return null;
		const [p, sig] = String(token).split('.');
		if (!p || !sig) return null;
		const ok = await crypto.subtle.verify('HMAC', await hmacKey(env.LICENCE_SECRET, ['verify']), fromB64u(sig), enc.encode(p));
		if (!ok) return null;
		const payload = JSON.parse(new TextDecoder().decode(fromB64u(p)));
		if (!payload.id || !payload.exp || payload.exp < Date.now() / 1000) return null;
		return payload;
	} catch (e) { return null; }
}

function newKey() {
	const c = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; const r = crypto.getRandomValues(new Uint8Array(16));
	let s = ''; for (let i = 0; i < 16; i++) s += c[r[i] % 32];
	return s.match(/.{4}/g).join('-');
}
async function kvJson(env, key) { try { return JSON.parse((await env.LICENCE_KV.get(key)) || 'null'); } catch (e) { return null; } }

// Wrong guesses and trial starts are counted per (hashed) address, expiring on their own.
async function throttleCount(env, name, windowSec) {
	const now = Math.floor(Date.now() / 1000); const arr = ((await kvJson(env, name)) || []).filter(t => t > now - windowSec);
	return arr;
}
async function throttleAdd(env, name, arr, windowSec) {
	arr.push(Math.floor(Date.now() / 1000));
	await env.LICENCE_KV.put(name, JSON.stringify(arr), { expirationTtl: Math.max(60, windowSec) });
}

async function handlePost(request, env) {
	let input; try { input = await request.json(); } catch (e) { return reply(400, { ok: false, error: 'Unknown action' }); }
	if (!input || typeof input !== 'object') return reply(400, { ok: false, error: 'Unknown action' });
	const action = String(input.action || ''); const device = String(input.device || '');
	const validDevice = /^[A-Za-z0-9_-]{16,64}$/.test(device);
	if (!env.LICENCE_KV || !env.LICENCE_SECRET || !env.ADMIN_SECRET) return reply(500, { ok: false, error: 'Server not configured' });
	const ip = await sha256hex((request.headers.get('CF-Connecting-IP') || '') + 'mh-lic');

	if (action === 'issue') {
		if (!(await sameSecret(env.ADMIN_SECRET, input.admin))) return reply(403, { ok: false, error: 'Not allowed' });
		const tier = ['founder', 'premium'].includes(input.tier) ? input.tier : 'premium';
		const note = String(input.note || '').replace(/[\r\n]+/g, ' ').slice(0, 80);
		const max = Math.max(1, Math.min(10, parseInt(input.max_devices) || (tier === 'founder' ? 5 : MAX_DEVICES)));
		const key = newKey();
		await env.LICENCE_KV.put('k:' + await sha256hex(key), JSON.stringify({ tier, note, max, devices: [], created: new Date().toISOString(), revoked: false }));
		return reply(200, { ok: true, key, tier, max_devices: max });
	}
	if (action === 'revoke') {
		if (!(await sameSecret(env.ADMIN_SECRET, input.admin))) return reply(403, { ok: false, error: 'Not allowed' });
		const name = 'k:' + await sha256hex(String(input.key || '').trim().toUpperCase());
		const e = await kvJson(env, name);
		if (!e) return reply(404, { ok: false });
		e.revoked = true; await env.LICENCE_KV.put(name, JSON.stringify(e));
		return reply(200, { ok: true });
	}
	if (action === 'activate') {
		if (!validDevice) return reply(400, { ok: false, error: 'Missing device id' });
		const h = await sha256hex(String(input.key || '').trim().toUpperCase());
		const tn = 'th:' + ip, tries = await throttleCount(env, tn, 600);
		if (tries.length >= 8) return reply(429, { ok: false, error: 'Too many tries. Please wait a few minutes.' });
		const e = await kvJson(env, 'k:' + h);
		if (!e || e.revoked) { await throttleAdd(env, tn, tries, 600); return reply(403, { ok: false, error: 'That key was not recognised.' }); }
		if (!e.devices.includes(device)) {
			if (e.devices.length >= e.max) return reply(409, { ok: false, error: 'This key is already in use on ' + e.max + ' devices. Contact support to move it.' });
			e.devices.push(device); await env.LICENCE_KV.put('k:' + h, JSON.stringify(e));
		}
		return reply(200, { ok: true, token: await makeToken(env, h.slice(0, 12), e.tier, TOKEN_DAYS), tier: e.tier, days: TOKEN_DAYS });
	}
	if (action === 'trial') {
		if (!validDevice) return reply(400, { ok: false, error: 'Missing device id' });
		const now = Math.floor(Date.now() / 1000), dh = await sha256hex(device);
		const started = parseInt(await env.LICENCE_KV.get('t:' + dh) || '0');
		if (started) {
			const left = started + TRIAL_DAYS * 86400 - now;
			if (left <= 0) return reply(403, { ok: false, error: 'The trial on this device has ended.' });
			const days = Math.ceil(left / 86400);
			return reply(200, { ok: true, token: await makeToken(env, 't' + dh.slice(0, 11), 'trial', Math.max(1, days)), tier: 'trial', days });
		}
		const tn = 'tt:' + ip, tries = await throttleCount(env, tn, 86400);
		if (tries.length >= 3) return reply(429, { ok: false, error: 'Too many trials from this connection today.' });
		await throttleAdd(env, tn, tries, 86400);
		await env.LICENCE_KV.put('t:' + dh, String(now), { expirationTtl: 60 * 60 * 24 * 400 });
		return reply(200, { ok: true, token: await makeToken(env, 't' + dh.slice(0, 11), 'trial', TRIAL_DAYS), tier: 'trial', days: TRIAL_DAYS });
	}
	if (action === 'download') {   // the Premium files, same as licence.php: any valid, unexpired token
		if (!(await verifyToken(env, input.token))) return reply(403, { ok: false, error: 'Licence not valid' });
		const buf = await env.LICENCE_KV.get('payload:zip', 'arrayBuffer');
		if (!buf) return reply(404, { ok: false, error: 'Premium files are not published yet' });
		return new Response(buf, { headers: { 'Content-Type': 'application/zip', 'Content-Disposition': 'attachment; filename="maxedhealth-premium.zip"', 'Cache-Control': 'private, no-store', ...CORS } });
	}
	return reply(400, { ok: false, error: 'Unknown action' });
}

export default {
	async fetch(request, env) {
		if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
		const url = new URL(request.url); const path = url.pathname.replace(/\/+$/, '') || '/';

		if (request.method === 'GET' && path === '/launcher/version.json') {
			if (!env.LICENCE_KV) return reply(500, { ok: false, error: 'Server not configured' });
			const v = await env.LICENCE_KV.get('launcher:version');
			if (!v) return reply(404, { ok: false, error: 'No launcher published yet' });
			return new Response(v, { headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'public, max-age=300', ...CORS } });
		}
		if (request.method === 'GET' && path === '/launcher/get') return new Response(GET_PAGE, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } });
		if (request.method === 'GET' && path === '/launcher/download') {
			if (!env.LICENCE_KV || !env.LICENCE_SECRET) return reply(500, { ok: false, error: 'Server not configured' });
			const lic = await verifyToken(env, request.headers.get('X-MH-Licence') || url.searchParams.get('t'));
			if (!lic || !APK_TIERS.includes(lic.tier)) return reply(403, { ok: false, error: 'The launcher is for Premium and founder licences' });
			const buf = await env.LICENCE_KV.get('launcher:apk', 'arrayBuffer');
			if (!buf) return reply(404, { ok: false, error: 'No launcher published yet' });
			return new Response(buf, { headers: { 'Content-Type': 'application/vnd.android.package-archive', 'Content-Length': String(buf.byteLength), 'Content-Disposition': 'attachment; filename="MaxedHealth-launcher.apk"', 'Cache-Control': 'private, no-store', ...CORS } });
		}
		if (request.method === 'PUT' && path.startsWith('/admin/put/')) {
			if (!env.LICENCE_KV || !env.ADMIN_SECRET) return reply(500, { ok: false, error: 'Server not configured' });
			if (!(await sameSecret(env.ADMIN_SECRET, request.headers.get('X-MH-Admin')))) return reply(403, { ok: false, error: 'Not allowed' });
			const name = decodeURIComponent(path.slice('/admin/put/'.length));
			if (!BLOBS[name]) return reply(400, { ok: false, error: 'Unknown name. Use one of: ' + Object.keys(BLOBS).join(', ') });
			const buf = await request.arrayBuffer();
			if (!buf.byteLength || buf.byteLength > BLOBS[name].max) return reply(413, { ok: false, error: 'Empty, or over the ' + BLOBS[name].max + ' byte limit' });
			if (name === 'launcher:version') {
				try { const v = JSON.parse(new TextDecoder().decode(buf)); if (!v.versionCode || !v.versionName) throw 0; } catch (e) { return reply(400, { ok: false, error: 'version.json needs versionCode and versionName' }); }
			}
			await env.LICENCE_KV.put(name, buf);
			return reply(200, { ok: true, name, bytes: buf.byteLength, sha256: await sha256hex(buf) });
		}
		if (request.method === 'POST' && (path === '/' || path === '/licence')) return handlePost(request, env);
		return reply(404, { ok: false, error: 'Not found' });
	},
};
