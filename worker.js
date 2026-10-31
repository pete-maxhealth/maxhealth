
// Tune these two to whatever worst-case monthly spend you're actually willing
// to risk. Rough cost reference at claude-sonnet-4-6 rates ($3/$15 per
// million input/output tokens): a typical text call is ~$0.004, a
// photo/label call ~$0.015. MONTHLY_CALL_CAP x ~$0.006 (blended average) is
// roughly your true worst-case monthly ceiling - e.g. 5000 calls ≈ £24-30/mo.
const PER_IP_DAILY_CAP = 80;
const MONTHLY_CALL_CAP = 5000;


// ── Starter allowance and licence tokens (added v3.10.1011) ────────────────────
// Every number here can be changed in one place. All of it is backwards compatible:
// a request with no X-MH-Device header (an older copy of the app) is handled exactly as before.
const STARTER_TOTAL   = 60;   // free AI calls for a brand-new device
const STARTER_TOPUP   = 5;    // calls per day once the starter is used up
const LICENCE_DAILY   = 30;   // calls per day for a valid licence token (was 200, lowered 31/10/2026)
const LICENCE_MONTHLY_CAP = 10000; // separate shared monthly pool for licensed users: 10000 x ~$0.006 = about $60/mo worst case
const ALLOWED_MODELS  = ['claude-sonnet-4-6', 'claude-haiku-4-5'];
const MAX_TOKENS_CAP  = 2500;
const CORS_HEADERS = {
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'POST, OPTIONS',
	'Access-Control-Allow-Headers': 'Content-Type, X-MH-Device, X-MH-Licence',
	'Access-Control-Expose-Headers': 'X-MH-Remaining, X-MH-Tier',
};

// ── Adjustable limits (31/10/2026) ───────────────────────────────────────────────
// The numbers above are only the DEFAULTS. They can be changed without redeploying: store
// overrides in KV under "cfg:limits" with the admin command (POST /admin/limits, header
// X-MH-Admin = the ADMIN_SECRET secret on this Worker). If nothing is stored, or KV is
// unavailable, the defaults apply.
const LIMIT_DEFAULTS = { licenceDaily: LICENCE_DAILY, licenceMonthly: LICENCE_MONTHLY_CAP, freeMonthly: MONTHLY_CALL_CAP, perIpDaily: PER_IP_DAILY_CAP, starterTotal: STARTER_TOTAL, starterTopup: STARTER_TOPUP };
let limitCache = null;   // { t, v } kept per Worker instance for 30 seconds to save KV reads
async function getLimits(env) {
	if (limitCache && Date.now() - limitCache.t < 30000) return limitCache.v;
	let v = { ...LIMIT_DEFAULTS };
	try {
		const raw = env.RATE_LIMIT_KV ? await env.RATE_LIMIT_KV.get('cfg:limits') : null;
		if (raw) { const o = JSON.parse(raw); for (const k of Object.keys(v)) if (Number.isInteger(o[k]) && o[k] >= 0 && o[k] <= 1000000) v[k] = o[k]; }
	} catch (e) { /* fall back to defaults */ }
	limitCache = { t: Date.now(), v };
	return v;
}
async function sameSecret(a, b) {
	const enc = new TextEncoder();
	const [x, y] = await Promise.all([crypto.subtle.digest('SHA-256', enc.encode(a)), crypto.subtle.digest('SHA-256', enc.encode(b))]);
	const A = new Uint8Array(x), B = new Uint8Array(y); let d = 0;
	for (let i = 0; i < A.length; i++) d |= A[i] ^ B[i];
	return d === 0;
}
async function adminLimits(request, env) {
	const json = (o, st = 200) => new Response(JSON.stringify(o), { status: st, headers: { 'Content-Type': 'application/json' } });
	if (request.method !== 'POST') return json({ ok: false, error: 'POST only' }, 405);
	const given = request.headers.get('X-MH-Admin') || '';
	if (!env.ADMIN_SECRET || !given || !(await sameSecret(given, env.ADMIN_SECRET))) return json({ ok: false, error: 'Not allowed' }, 403);
	let body; try { body = await request.json(); } catch (e) { return json({ ok: false, error: 'Bad JSON' }, 400); }
	try {
		if (body.action === 'reset') { await env.RATE_LIMIT_KV.delete('cfg:limits'); limitCache = null; return json({ ok: true, limits: await getLimits(env) }); }
		if (body.action === 'set') {
			const cur = (await getLimits(env)), next = { ...cur };
			for (const [k, val] of Object.entries(body.limits || {})) {
				if (!(k in LIMIT_DEFAULTS)) return json({ ok: false, error: 'Unknown limit: ' + k }, 400);
				if (!Number.isInteger(val) || val < 0 || val > 1000000) return json({ ok: false, error: 'Bad value for ' + k }, 400);
				next[k] = val;
			}
			await env.RATE_LIMIT_KV.put('cfg:limits', JSON.stringify(next)); limitCache = { t: Date.now(), v: next };
			return json({ ok: true, limits: next });
		}
		if (body.action === 'get') return json({ ok: true, limits: await getLimits(env), defaults: LIMIT_DEFAULTS });
		return json({ ok: false, error: 'action must be get, set or reset' }, 400);
	} catch (e) { return json({ ok: false, error: 'KV unavailable: ' + e.message }, 503); }
}

function b64uToBytes(s) {
	s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '=';
	const bin = atob(s); const out = new Uint8Array(bin.length);
	for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
	return out;
}

// Licence token = base64url(JSON payload) + "." + base64url(HMAC-SHA256(payload, LICENCE_SECRET)).
// Payload: { id: "<licence id>", tier: "premium"|"trial"|"founder", exp: <unix seconds> }.
async function verifyLicence(token, env) {
	try {
		if (!token || !env.LICENCE_SECRET) return null;
		const [p, sig] = token.split('.');
		if (!p || !sig) return null;
		const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(env.LICENCE_SECRET), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']);
		const ok = await crypto.subtle.verify('HMAC', key, b64uToBytes(sig), new TextEncoder().encode(p));
		if (!ok) return null;
		const payload = JSON.parse(new TextDecoder().decode(b64uToBytes(p)));
		if (!payload.id || (payload.exp && payload.exp < Date.now() / 1000)) return null;
		return payload;
	} catch (e) { return null; }
}

function limited(message, remaining) {
	return new Response(JSON.stringify({ error: { message } }), {
		status: 429,
		headers: { 'Content-Type': 'application/json', ...CORS_HEADERS, 'X-MH-Remaining': String(remaining) }
	});
}

// If the usage counters (KV) are unavailable, e.g. the daily KV write limit on the free
// Cloudflare plan is used up, fail closed (no uncounted AI calls) but with a clear message.
function busy(err) {
	try { console.log('KV unavailable: ' + (err && err.message)); } catch (e) {}
	return new Response(JSON.stringify({ error: { message: 'The shared AI service is temporarily unavailable. Please try again later, or add your own API key in Settings.' } }), {
		status: 503,
		headers: { 'Content-Type': 'application/json', ...CORS_HEADERS }
	});
}

// Returns { block?: Response, remaining?: number, tier?: string }.
async function allowance(request, env, weight) {
	if (!env.RATE_LIMIT_KV) return {};
	const L = await getLimits(env);
	const today = new Date().toISOString().slice(0, 10);
	const lic = await verifyLicence(request.headers.get('X-MH-Licence'), env);
	if (lic) {
		const k = `lic:${lic.id}:${today}`;
		const used = parseInt((await env.RATE_LIMIT_KV.get(k)) || '0', 10);
		if (used + weight > L.licenceDaily) return { block: limited(`Daily AI limit for your licence reached (${L.licenceDaily}). It resets tomorrow.`, 0) };
		await env.RATE_LIMIT_KV.put(k, String(used + weight), { expirationTtl: 60 * 60 * 36 });
		return { remaining: L.licenceDaily - used - weight, tier: lic.tier || 'premium' };
	}
	const dev = request.headers.get('X-MH-Device') || '';
	if (!/^[A-Za-z0-9_-]{16,64}$/.test(dev)) return {};   // older app: existing per-IP caps still apply
	const k = `starter:${dev}`;
	let s; try { s = JSON.parse((await env.RATE_LIMIT_KV.get(k)) || 'null'); } catch (e) { s = null; }
	if (!s) s = { used: 0, day: today, dayUsed: 0 };
	if (s.day !== today) { s.day = today; s.dayUsed = 0; }
	if (s.used + weight <= L.starterTotal) {
		s.used += weight;
		await env.RATE_LIMIT_KV.put(k, JSON.stringify(s), { expirationTtl: 60 * 60 * 24 * 400 });
		return { remaining: L.starterTotal - s.used, tier: 'starter' };
	}
	if (s.dayUsed + weight <= L.starterTopup) {
		s.dayUsed += weight;
		await env.RATE_LIMIT_KV.put(k, JSON.stringify(s), { expirationTtl: 60 * 60 * 24 * 400 });
		return { remaining: L.starterTopup - s.dayUsed, tier: 'topup' };
	}
	return { block: limited(`Your free starter AI allowance is used up and today's top-up is spent. It tops up a little each day, or you can add your own API key in Settings, or look at Premium.`, 0) };
}

const handler = {
	async fetch(request, env) {
		if (request.method === 'OPTIONS') {
			return new Response(null, {
				headers: CORS_HEADERS
			});
		}

		if (request.method !== 'POST') {
			return new Response('Method not allowed', { status: 405, headers: CORS_HEADERS });
		}

		try {
			const body = await request.json();

			// ── Cost containment ────────────────────────────────────────────────
			// Two independent caps, both backed by Workers KV (so they're shared
			// across every device/user hitting this Worker — unlike the app's own
			// localStorage-based cap, which only protects one device and resets
			// the moment someone clears their browser data):
			//
			//   1. Per-IP daily cap — stops one household/device from running away
			//      (a stuck retry loop, a runaway feature) without affecting anyone
			//      else.
			//   2. Global monthly cap — a hard ceiling on total spend regardless of
			//      how many people or devices are using the app. This is the one
			//      that actually bounds worst-case cost as usage scales; the per-IP
			//      cap alone still scales linearly with device count.
			//
			// KV is eventually-consistent, not atomic — under heavy concurrent
			// traffic this can under-count slightly (a handful of requests landing
			// in the same instant might all read the same "before" count). That's
			// fine for a cost *ceiling* with headroom built in; it would NOT be
			// fine if this needed to be an exact security boundary.
			const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
			const now = new Date();
			const dayKey   = `calls:day:${now.toISOString().slice(0,10)}:${ip}`;
			const monthKey = `calls:month:${now.toISOString().slice(0,7)}`;
			// multiCheck fans out to 3 provider calls per request - weight it
			// accordingly rather than letting it count as "1" against the same
			// caps a single-provider call uses.
			const weight = body.multiCheck ? 3 : 1;
			const L = await getLimits(env);

			// Licensed users have their own pool and their own daily cap (LICENCE_DAILY,
			// applied in allowance()), so they skip the per-connection cap and do not
			// draw on the free/starter pool (and free users cannot use up theirs).
			const licensed = !!(await verifyLicence(request.headers.get('X-MH-Licence'), env));
			if (env.RATE_LIMIT_KV && licensed) {
				const lmKey = `calls:month-lic:${now.toISOString().slice(0,7)}`;
				const lmN = parseInt((await env.RATE_LIMIT_KV.get(lmKey)) || '0', 10);
				if (lmN + weight > L.licenceMonthly) {
					return new Response(JSON.stringify({
						error: { message: `Monthly AI usage cap reached for licensed users (${L.licenceMonthly} calls) - this protects against runaway cost. Resets at the start of next month.` }
					}), { status: 429, headers: { 'Content-Type': 'application/json', ...CORS_HEADERS } });
				}
				await env.RATE_LIMIT_KV.put(lmKey, String(lmN + weight), { expirationTtl: 60 * 60 * 24 * 31 });
			} else if (env.RATE_LIMIT_KV) {
				const [dayCount, monthCount] = await Promise.all([
					env.RATE_LIMIT_KV.get(dayKey),
					env.RATE_LIMIT_KV.get(monthKey)
				]);
				const dayN = parseInt(dayCount || '0', 10);
				const monthN = parseInt(monthCount || '0', 10);

				if (monthN + weight > L.freeMonthly) {
					return new Response(JSON.stringify({
						error: { message: `Monthly AI usage cap reached (${L.freeMonthly} calls) - this protects against runaway cost across all users. Resets at the start of next month.` }
					}), { status: 429, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } });
				}
				if (dayN + weight > L.perIpDaily) {
					return new Response(JSON.stringify({
						error: { message: `Daily AI usage cap reached for this connection (${L.perIpDaily} calls) - try again tomorrow, or add your own API key in Settings to bypass the shared account entirely.` }
					}), { status: 429, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } });
				}

				// Best-effort increment, not strictly atomic (see note above) - the
				// 24h/31-day TTLs mean a slightly-stale write still self-corrects
				// within one cycle rather than permanently drifting.
				await Promise.all([
					env.RATE_LIMIT_KV.put(dayKey, String(dayN + weight), { expirationTtl: 60 * 60 * 24 }),
					env.RATE_LIMIT_KV.put(monthKey, String(monthN + weight), { expirationTtl: 60 * 60 * 24 * 31 })
				]);
			}
			// If RATE_LIMIT_KV isn't bound yet, caps are simply skipped rather than
			// erroring every request - see deploy note for how to add the binding.

			// ── Multi-provider consensus check ──────────────────────────────────
			// Runs the same prompt past Claude, Gemini, and OpenAI in parallel and
			// returns all three raw results for the client to compare and display.
			// Deliberately does NOT try to merge/average them here - disagreement
			// between providers is itself the useful signal, so the client needs
			// to see each answer individually, not a single blended number.
			// Triggered by body.multiCheck === true; separate from the normal
			// single-provider path below so nothing about existing behaviour changes.
			if (body.multiCheck) {
				const prompt = body.prompt;
				if (!prompt) {
					return new Response(JSON.stringify({ error: { message: 'multiCheck requires a prompt' } }), {
						status: 400,
						headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
					});
				}

				const callClaude = async () => {
					const res = await fetch('https://api.anthropic.com/v1/messages', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
							'x-api-key': env.ANTHROPIC_API_KEY,
							'anthropic-version': '2023-06-01'
						},
						body: JSON.stringify({
							model: 'claude-sonnet-4-6',
							max_tokens: 500,
							messages: [{ role: 'user', content: prompt }]
						})
					});
					const data = await res.json();
					if (data.error) throw new Error(data.error.message || 'Claude API error');
					return data.content?.[0]?.text?.trim() || '';
				};

				const callGemini = async () => {
					if (!env.GEMINI_API_KEY) throw new Error('GEMINI_API_KEY not configured');
					// gemini-3.5-flash - confirmed current GA flagship per Google's own
					// docs. Earlier reasoning here was wrong: 2.5-flash isn't the
					// "safer, settled" choice - Google is actively restricting it for
					// new API keys ahead of its official shutdown date, while 3.5-flash
					// is the stable, officially recommended replacement.
					const doFetch = () => fetch(
						'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent',
						{
							method: 'POST',
							headers: {
								'Content-Type': 'application/json',
								'x-goog-api-key': env.GEMINI_API_KEY
							},
							body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
						}
					);
					// "High demand" is documented as typically transient within seconds,
					// but a single retry isn't always enough during a sustained spike -
					// up to 2 retries with increasing backoff (1.5s, then 3s). This runs
					// in parallel with Claude/OpenAI via Promise.allSettled, so the extra
					// time only affects Gemini's own result, never delays the other two.
					let res = await doFetch();
					let attempt = 0;
					while (res.status === 503 && attempt < 2) {
						attempt++;
						await new Promise(r => setTimeout(r, attempt * 1500));
						res = await doFetch();
					}
					const data = await res.json();
					if (data.error) throw new Error(data.error.message || 'Gemini API error');
					const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
					if (!text) throw new Error('Gemini returned no usable content (may have been blocked by safety filters)');
					return text.trim();
				};

				const callOpenAI = async () => {
					if (!env.OPENAI_API_KEY) throw new Error('OPENAI_API_KEY not configured');
					const res = await fetch('https://api.openai.com/v1/chat/completions', {
						method: 'POST',
						headers: {
							'Content-Type': 'application/json',
							'Authorization': `Bearer ${env.OPENAI_API_KEY}`
						},
						body: JSON.stringify({
							model: 'gpt-5.4-mini',
							messages: [{ role: 'user', content: prompt }],
							max_completion_tokens: 500
						})
					});
					const data = await res.json();
					if (data.error) throw new Error(data.error.message || 'OpenAI API error');
					return data.choices?.[0]?.message?.content?.trim() || '';
				};

				// allSettled, not all() - one provider failing (bad key, quota, safety
				// block) should not prevent the other two results from coming back.
				const [claudeResult, geminiResult, openaiResult] = await Promise.allSettled([
					callClaude(), callGemini(), callOpenAI()
				]);

				const toResult = (settled) => settled.status === 'fulfilled'
					? { ok: true, text: settled.value }
					: { ok: false, error: settled.reason?.message || 'Unknown error' };

				return new Response(JSON.stringify({
					claude: toResult(claudeResult),
					gemini: toResult(geminiResult),
					openai: toResult(openaiResult)
				}), {
					headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
				});
			}

			// ── Normal single-provider path (unchanged) ─────────────────────────
			// Forward what the app actually asked for, rather than silently
			// overriding it. Previously this always sent claude-haiku-4-5 and
			// max_tokens:500 regardless of what the client requested - meaning
			// every proxy-routed call (the default path for anyone without their
			// own API key, which includes the cloud version) silently ran on a
			// smaller model with a harder token cap than the app was actually
			// designed around, no matter what any individual feature needed.
			// Falls back to sensible defaults only if the client omits them.
			const model = ALLOWED_MODELS.includes(body.model) ? body.model : 'claude-sonnet-4-6';
			const maxTokens = Math.min(parseInt(body.max_tokens, 10) || 800, MAX_TOKENS_CAP);

			const anthropicBody = {
				model,
				max_tokens: maxTokens,
				system: body.system,
				messages: body.messages
			};
			// Forward tool use (e.g. web search) if the client requested it -
			// previously dropped silently, same as model/max_tokens.
			if (Array.isArray(body.tools)) {
				// Only the web-search tool is allowed, and capped at 3 searches a call.
				const ws = body.tools.filter(x => x && x.type === 'web_search_20250305').slice(0, 1).map(x => ({ type: x.type, name: 'web_search', max_uses: 3 }));
				if (ws.length) anthropicBody.tools = ws;
			}

			const response = await fetch('https://api.anthropic.com/v1/messages', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'x-api-key': env.ANTHROPIC_API_KEY,
					'anthropic-version': '2023-06-01'
				},
				body: JSON.stringify(anthropicBody)
			});

			const data = await response.json();

			return new Response(JSON.stringify(data), {
				headers: {
					'Content-Type': 'application/json',
					'Access-Control-Allow-Origin': '*'
				}
			});

		} catch (err) {
			if (/\bKV\b/i.test(String(err && err.message))) return busy(err);
			return new Response(JSON.stringify({ error: { message: err.message } }), {
				status: 500,
				headers: {
					'Content-Type': 'application/json',
					'Access-Control-Allow-Origin': '*'
				}
			});
		}
	}
};

export default {
	async fetch(request, env) {
		if (new URL(request.url).pathname === '/admin/limits') return adminLimits(request, env);
		if (request.method !== 'POST') return handler.fetch(request, env);
		let weight = 1;
		try { const b = await request.clone().json(); if (b && b.multiCheck) weight = 3; } catch (e) {}
		let a;
		try { a = await allowance(request, env, weight); } catch (e) { return busy(e); }
		if (a.block) return a.block;
		const res = await handler.fetch(request, env);
		if (a.remaining === undefined) return res;
		const out = new Response(res.body, res);
		out.headers.set('X-MH-Remaining', String(a.remaining));
		out.headers.set('X-MH-Tier', a.tier || '');
		out.headers.set('Access-Control-Expose-Headers', 'X-MH-Remaining, X-MH-Tier');
		return out;
	}
};
