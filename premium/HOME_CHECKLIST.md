# When Pete is home: everything outstanding (private: do not publish)

Last updated 13 Oct 2026, app v3.10.1011. Order matters where marked.

## A. Do first (no laptop needed, mostly from the phone)
1. **Spend limits.** Set a monthly spend limit and alerts on each AI provider dashboard (Anthropic, OpenAI, Google). Protects you today, whatever else changes.
2. **Deploy `worker.js`** in the Cloudflare dashboard (Workers > maxhealth-ai > Edit code > paste > Deploy). This switches on the 60-answer starter allowance, the daily top-up of 5, the model allow-list and the response cap. Check Settings > AI Provider shows "Free AI answers left".
3. **Rotate the provider keys** (Worker secrets) once the new Worker is live, because the old Worker has been open to anyone.
4. **Check GitHub Pages** shows v3.10.1011 in Settings.

## B. Licence service (needs GoDaddy Linux/cPanel hosting; the current GoDaddy plan is the website builder and cannot run PHP)
0. Register-interest is now a Tally form (https://tally.so/r/Dq2AQ5), set by `MH_PREMIUM_URL`; check its Submissions tab. Move it to a pspence.co.uk page when hosting is added.
1. Upload `premium-site/` (index.html, register.php, setup.html, icons) and `licence.php`.
2. Create `maxedhealth_licence/config.php` one level ABOVE public_html: `signing_secret` (long random) and `admin_secret` (another). Steps in `premium-site/README.md`.
3. In Cloudflare add the Worker secret `LICENCE_SECRET` with exactly the same value as `signing_secret`.
4. Issue founder keys for Pete and Jill (5 devices each). Activate in Settings > AI Provider > Premium licence.
5. Hide the "Start 14-day trial" button until a trial actually unlocks something (see C).
6. ICO registration fee question (you are collecting email addresses).

## C. Making Premium really Premium (needs the laptop and both phones)
1. Phone side (then un-hide the trial button `#licenceTrialBtn`): make `mh_autoupdate.sh` and the launcher fetch `premium_payload.zip` with the stored licence token (`action: download`) instead of pulling from GitHub. The server needs a small endpoint to receive the token from the app. Test on Pete's phone first, then Jill's.
2. Build the payload: `python3 tools/split_premium.py --out /tmp/split`; put `premium_payload.zip` in `maxedhealth_licence/`.
3. Only then: create the private repo (full history), recreate the public repo from `split/free/` (new history, same name). Old commits stay visible in a public repo's history unless it is recreated.
4. Remove the launcher APK from public GitHub Releases. Keep `debug.keystore` and a backup of the 2 Oct APK safe offline first.
5. Public README is `premium/public_README.md`.

## D. Android Studio / launcher (Jill's laptop)
1. Health Connect step doubling fix in the launcher (the app and server rules are already done).
2. Back up the 2 Oct APK and `debug.keystore`.
3. Launcher source is not in the repo: decide where it lives (private repo).
4. Jill's phone: `crond` line and Termux battery set to Unrestricted.
5. iPhone tester: Safari load, Add to Home Screen, data persistence, camera/voice/barcode.

## E. Prices and offer (decide, then update the Premium page)
1. Price for Premium: one-off vs yearly vs monthly; an early-bird figure for the register-interest list.
2. Who it is for: Android users with a ring or watch who log daily. iPhone users stay on the free web app.
3. Add a before-and-after screenshot (typed week vs synced week) to the Premium page and a locked wearable-trends sample in the demo.
4. Starter allowance numbers can be changed in `worker.js`: `STARTER_TOTAL` 60, `STARTER_TOPUP` 5, `LICENCE_DAILY` 200.
5. Payment: nothing built, by design, until interest is proven.

## F. PEMFiT (parked)
Organisation licence tier: seats plus automatic branding on activation, a monthly AI budget per organisation, customers send their own reports (no central collection, so no data-controller role for you). Pilot idea: one hand-issued key. Draft a one-page pilot offer when you want to approach them. Wording note: the company name is "PEMFiT".

## G. Review needed from real people
1. Clinician review of the 27 starter packs and the 11 newest demo personas (their lab values and stories).
2. Native-speaker review of each language pack (Spanish, German, French, Turkish, and the newer Portuguese-BR, Italian, Polish, Dutch). All are machine translations; corrections go in `lang/<code>.json` as English → translation.
3. Decide whether any condition should get real formulas (heart: sodium and saturated fat; PCOS: lower-carb defaults). Only with solid evidence, clearly labelled.
4. Read the 28-card demo picker on a real phone; decide if it needs search or groups.
5. Public docs: read the new Free vs Premium wording in the guide and story pages.

## H. Smaller items still open
0. Ko-fi is live (ko-fi.com/maxedhealth). The old JustGiving button is removed from `docs/why-free.html`; its header photo is still hosted on images.justgiving.com, so copy it into the repo before that page is ever taken down. Check the tax treatment of tips.
Garmin extractor verification; old HTML changelog gaps; GitHub Releases cleanup; multi-category meal picker.
