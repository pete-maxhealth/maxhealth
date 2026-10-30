# Licence + launcher Worker: set-up (about 15 minutes, all from Termux)

Replaces the GoDaddy/PHP licence service. Hosts the launcher APK behind a licence check, off public GitHub.
Tested: `node tests/worker/licence_worker.mjs` (26 checks, all pass).

1. Cloudflare account (free) is enough. Log in once: `npx wrangler login`.
2. Create the store: `npx wrangler kv namespace create LICENCE_KV` -> copy the id into `wrangler.licence.toml`.
3. Secrets (you type/paste them; I never see them):
   - `npx wrangler secret put LICENCE_SECRET -c wrangler.licence.toml`  (the SAME value the AI Worker uses)
   - `openssl rand -hex 32` -> `npx wrangler secret put ADMIN_SECRET -c wrangler.licence.toml`  (keep a copy in your password manager)
4. Deploy: `npx wrangler deploy -c wrangler.licence.toml`  -> note the https://…workers.dev address.
5. Upload the launcher: `curl -T apk/MaxedHealth-launcher.apk -H "X-MH-Admin: $ADMIN" https://<addr>/admin/put/launcher:apk`
   and `curl -T apk/version.json -H "X-MH-Admin: $ADMIN" https://<addr>/admin/put/launcher:version`
6. Issue a key: `curl -d '{"action":"issue","admin":"'$ADMIN'","tier":"founder","note":"Jill"}' https://<addr>/`
7. Only after steps 1-6 work do we repoint the app (`MH_LICENCE_URL`) and remove the APK from GitHub.
