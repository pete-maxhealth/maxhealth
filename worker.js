
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
					let res = await doFetch();
					if (res.status === 503) {
						// "High demand" is documented as typically transient within seconds -
						// one retry after a short wait, rather than failing immediately.
						await new Promise(r => setTimeout(r, 1500));
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
