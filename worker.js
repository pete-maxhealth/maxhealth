
// Tune these two to whatever worst-case monthly spend you're actually willing
// to risk. Rough cost reference at claude-sonnet-4-6 rates ($3/$15 per
// million input/output tokens): a typical text call is ~$0.004, a
// photo/label call ~$0.015. MONTHLY_CALL_CAP x ~$0.006 (blended average) is
// roughly your true worst-case monthly ceiling - e.g. 5000 calls ≈ £24-30/mo.
const PER_IP_DAILY_CAP = 80;
const MONTHLY_CALL_CAP = 5000;

export default {
	async fetch(request, env) {
		if (request.method === 'OPTIONS') {
			return new Response(null, {
				headers: {
					'Access-Control-Allow-Origin': '*',
					'Access-Control-Allow-Methods': 'POST, OPTIONS',
					'Access-Control-Allow-Headers': 'Content-Type',
				}
			});
		}

		if (request.method !== 'POST') {
			return new Response('Method not allowed', { status: 405 });
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

			if (env.RATE_LIMIT_KV) {
				const [dayCount, monthCount] = await Promise.all([
					env.RATE_LIMIT_KV.get(dayKey),
					env.RATE_LIMIT_KV.get(monthKey)
				]);
				const dayN = parseInt(dayCount || '0', 10);
				const monthN = parseInt(monthCount || '0', 10);

				if (monthN + weight > MONTHLY_CALL_CAP) {
					return new Response(JSON.stringify({
						error: { message: `Monthly AI usage cap reached (${MONTHLY_CALL_CAP} calls) - this protects against runaway cost across all users. Resets at the start of next month.` }
					}), { status: 429, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } });
				}
				if (dayN + weight > PER_IP_DAILY_CAP) {
					return new Response(JSON.stringify({
						error: { message: `Daily AI usage cap reached for this connection (${PER_IP_DAILY_CAP} calls) - try again tomorrow, or add your own API key in Settings to bypass the shared account entirely.` }
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
			const model = body.model || 'claude-sonnet-4-6';
			const maxTokens = body.max_tokens || 800;

			const anthropicBody = {
				model,
				max_tokens: maxTokens,
				system: body.system,
				messages: body.messages
			};
			// Forward tool use (e.g. web search) if the client requested it -
			// previously dropped silently, same as model/max_tokens.
			if (body.tools) anthropicBody.tools = body.tools;

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
