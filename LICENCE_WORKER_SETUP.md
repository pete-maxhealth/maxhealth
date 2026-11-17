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

## Copy protection and households (v3.10.1408)
- **Device-bound tokens.** Each activation issues a token that names the phone it was issued to (a hash of its device code). The AI Worker only treats the token as licensed on that phone, so copying the token to another phone does nothing. Tokens issued before this change have no such claim and work until they expire (30 days at most).
- **One key, a set number of phones** (premium 2, founder 5, or `max_devices` when you issue it, up to 10: use that for a household pack). Each key is separate, and nothing is ever compared between keys or between internet connections, so a household with several keys, or several people on one wifi, is never flagged. Each person's trial is their own too (8 per connection per day).
- **Changing phone needs no help.** Settings, AI Provider, Premium licence, **Devices** lists the phones (by the name each gave itself) and frees one. A key that is full shows the same list with "Replace with this phone". Freeing is limited to 3 times in 30 days, so a key cannot be passed round. A freed phone keeps working until its current token expires (30 days at most) and is not renewed.
- **See a key's devices** (developer): `curl -d '{"action":"inspect","admin":"'$ADMIN'","key":"XXXX-XXXX-XXXX-XXXX"}' https://<addr>/` shows devices, labels, last use and moves in 30 days. Keys are still stored only as hashes, so you need the key text.
- **Deploy order:** the AI Worker (`worker.js`) first, then the licence Worker (`npx wrangler deploy -c wrangler.licence.toml`). Tests: `node tests/worker/licence_worker.mjs` and `node tests/worker/licence_devices.mjs`.
- **What cannot be stopped:** someone who copies a phone's whole stored data (not just the key) looks like that phone. The licence only gates AI use (a daily and monthly cap per licence, whatever the number of phones) and the launcher download, so the cost of that is bounded.
