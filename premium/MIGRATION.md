# Moving Premium off public GitHub (private notes: do not publish)

Why this order: both phones currently update straight from public GitHub. Pulling the Premium files out before the phones can fetch them with a licence key would stop Jill's and Pete's phones updating.

Built and tested (v3.10.1011):
1. Worker with starter allowance, licence-token check and hardening (`worker.js`).
2. Licence service (`premium-site/licence.php`): issue / activate (device-bound) / trial / revoke / download.
3. In-app licence card (Settings > AI Provider) and quiet token refresh.
4. `tools/split_premium.py`: builds the public free tree, the private Premium tree and `premium_payload.zip`.
5. Public docs rewritten to the Free web app vs Premium model.

Still to do, in this order:
A. Deploy the Worker; add the `LICENCE_SECRET` Worker secret. Set spend limits on each AI provider dashboard.
B. Upload `licence.php` and create `config.php` (see `premium-site/README.md`); build and place `premium_payload.zip`.
C. Issue founder keys for Pete and Jill; activate them in the app on each phone.
D. Phone side: make `mh_autoupdate.sh` and the launcher fetch `premium_payload.zip` with the stored licence token (`action: download`) instead of pulling from GitHub. The server needs a small endpoint to receive the token from the app. Test on Pete's phone first, then Jill's.
E. Only then: create the private repo with the full history, and replace the public repo contents with `split/free/`. Remove the launcher APK from public Releases. Note that old commits stay in the public history until the repo is recreated, so either recreate the public repo from the free tree (new history, same name) or accept that old copies exist.
F. Rotate the Worker's provider keys once the old public Worker is retired.
