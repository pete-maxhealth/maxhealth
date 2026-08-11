# MaxedHealth Technical Reference

## Architecture

Single-file PWA (`maxhealth.html`, ~900KB) served by a Python HTTP server (`server.py`) running locally on Android via Termux. All data stored in localStorage and flat files on device.

```
Browser (Chrome/Android)
    ↕ localhost:5757
Python HTTP Server (server.py)
    ↕ filesystem
Data tables (master.csv, combined.csv, library.csv)
    ↕ pipeline
Wearable exports (Withings, RingConn, Amazfit)
```

AI requests route through a Cloudflare Worker proxy (`maxhealth-ai.bogginsuk.workers.dev`) which holds the Anthropic API key. The app sends model and max_tokens — the Worker passes them through.

---

## File locations

| File | Path |
|------|------|
| App | `/storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html` |
| Server | `/storage/emulated/0/maxhealth/app/maxhealth/server.py` |
| Pipeline | `/storage/emulated/0/maxhealth/app/maxhealth/update_health.py` |
| Setup | `/storage/emulated/0/maxhealth/app/maxhealth/setup.sh` |
| master.csv | `/storage/emulated/0/maxhealth/data/tables/master.csv` |
| combined.csv | `/storage/emulated/0/maxhealth/data/tables/combined.csv` |
| library.csv | `/storage/emulated/0/maxhealth/data/tables/library.csv` |
| Boot script (crond) | `~/.termux/boot/start-crond.sh` |
| Boot script (watchdog) | `~/.termux/boot/start-watchdog.sh` |
| Boot script (sync) | `~/.termux/boot/maxedhealth.sh` |

---

## master.csv format

Pipe-delimited. Notes field may contain commas — pipes are reserved as delimiters.

```
date|kcal|protein|carbs|fat|notes
16/06/26|3506|188|42|274.5|Chemotherapy, 45min Resistance, 76min Walking
```

**Notes field values:**
- `standard` — normal day, no tags
- `holiday` — holiday day mode
- Occasion tags: `Chemotherapy`, `Hospital day`, `Illness`, `Social event`, `Travel`, `Fasting`
- Activity: `45min Resistance`, `76min Walking`, `60min Swimming` etc
- Multiple values comma-separated

---

## localStorage keys

| Key | Description |
|-----|-------------|
| `maxhealth_v1` | Main state JSON (todayLog, history, dayMode, notes, weight, waterToday, lastDate) |
| `mh_today_notes` | Today's occasion tags — persists across Termux restarts |
| `mh_activities` | Activity card state (types, duration, effort, enabled) |
| `mh_target_kcal` | Calorie target |
| `mh_target_protein` | Protein target |
| `mh_target_fat` | Fat target |
| `mh_target_water` | Water target (base, before exercise adjustment) |
| `mh_target_carbs` | Carb target (synced with mh_ceil_standard) |
| `mh_ceil_standard` | Carb ceiling — standard day mode |
| `mh_ceil_occasion` | Carb ceiling — occasion day mode |
| `mh_ceil_holiday` | Carb ceiling — holiday day mode |
| `mh_weight_target_low` | Weight target lower bound |
| `mh_weight_target_high` | Weight target upper bound |
| `mh_name` | User name |
| `mh_condition` | Medical condition (gbm, t2d, general) |
| `mh_visual_theme` | Visual colour theme — `none` / `vital` / `pulse` / `forge`. Independent of `mh_theme` (base) as of the Phase 14 theme rebuild — each visual theme now has its own light-mode palette too, activated via `[data-theme="light"][data-visual-theme="..."]` combined selectors |
| `mh_theme` | Base — `midnight` (default) / `light` / `auto` (follows system preference). Replaces the old `mh_color_scheme` key (removed Phase 14 — a genuine parallel system that caused a real bug, see Known Issues) |
| `mh_custom_accent` | Custom accent hex, independent of base — set via the swatch presets or the native colour picker in Customise. Re-applied automatically whenever base changes (`applyTheme()` no longer clears it on switch, a Phase 14 fix) |
| `mh_recent_scans` | Last 10 barcode scans |
| `mh_saved_queries` | Saved report queries |
| `mh_notif_prefs` | Notification preferences |
| `mh_steps_today` | Today's step count (cleared at midnight) |
| `mh_library` | Food library JSON |
| `mh_supplement_defs` | Supplement definitions |
| `mh_supplement_log` | Today's supplement log |
| `mh_dashboard_order` | Today dashboard section order (array of section keys) |
| `mh_library_section_order` | Library tab Recipes/Food Library order |
| `mh_reorder_reports` / `mh_reorder_manage` / `mh_reorder_import` | Generic reorder system order per tab (see below) |
| `mh_custom_devices` | User-added devices for the precedence list, beyond the built-in set |
| `mh_celebrated_milestones` | Ketosis streak day-counts already celebrated, so milestones fire once ever |
| `mh_recipes` | Saved Recipes JSON (servings-based, distinct from Meals in `mh_library`) |
| `mh_routines` | Saved Routine Templates (named exercise lists) |
| `mh_exercise_offset_enabled` | Exercise Offset for carb overage — on/off, off by default |
| `mh_exercise_offset_pct` | Exercise Offset threshold % (default 100 — exercise must burn at least as many calories as the excess carbs represent) |
| `mh_gbm_research_digests` | Saved GBM Research Digest entries (JSON array, dated, newest first) |
| `mh_height_cm` / `mh_age` / `mh_sex` | Profile basics — power `getCurrentTDEE()`; now correctly saved during onboarding, not just read for the live preview and then discarded |
| `mh_goal` | Goal/Phase — `lose` / `maintain` / `gain`. Drives the Suggested Targets calculator, Weight Phase History, and phase-aware calorie/activity-credit messaging |
| `mh_provider` | AI provider selection — `none` (proxy) / `claude` / `openai`. Determines whether `callHealthAI()` calls Anthropic/OpenAI directly with a personal key, or falls through to the shared Cloudflare Worker proxy |
| `mh_apikey` | Personal API key, used only when `mh_provider` is `claude` or `openai` |
| `mh_activity_credit_window` | Activity Credit Balance's rolling window size in days (default 14, adjustable 7-90 directly in the card) |
| `mh_settings_change_log` | Settings Change Log (Phase 14) — every auto-saved setting change on Manage, with old/new value and timestamp. 7-day rotation |
| `mh_last_full_backup_date` | Last date the automatic daily server backup ran (see `/save-full-backup`) — checked on startup so it only fires once per day |
| `mh_last_export_nudge` | Last date "Export All Data" was used, for the 7-day reminder banner shown after logging |

---

## State object structure

```javascript
state = {
  todayLog: [{ id, name, amount, kcal, protein, fat, carbs, time, _fromLibrary, _portionPct }],
  history:  [{ date, log, totals, mode, notes, weight, water_ml }],
  dayMode:  'standard' | 'occasion' | 'holiday',
  notes:    'Chemotherapy, 45min Resistance',  // occasion tags + activity
  lastDate: '16/06/26',
  weight:   92.5,
  waterToday: 1500,
}
```

---

## MET calorie calculation

```
kcal = MET × weight(kg) × duration(hours)
```

| Activity | Easy | Moderate | Hard |
|----------|------|----------|------|
| Walking | 2.8 | 3.5 | 4.5 |
| Resistance | 3.0 | 5.0 | 6.0 |
| Custom exercise | 3.5 | 5.0 | 7.0 |

Dynamic target adjustments:
- **Calories**: base + Σ(MET × weight × hours) per activity
- **Protein**: base + 15g when resistance enabled
- **Water**: base + 500ml per hour of any activity

---

## Rollover logic

Fires in `updateDashboard()` when `state.lastDate !== todayStr()`.

```
1. Capture: log, notes, mode, weight, water, lastDate
2. Set state.lastDate = today (immediately prevents re-trigger)
3. Clear: todayLog, notes, dayMode, waterToday, steps, activities duration
4. saveState() — persists today's date
5. If captured log non-empty AND date not already in history:
   a. Write history entry
   b. Build notes from captured occasion tags + activity state
   c. setTimeout(saveNutritionToServer, 1000)
   d. saveState()
```

---

## Voice input — continuous vs single-shot

Two distinct patterns, both built on the Web Speech API (`webkitSpeechRecognition`/`SpeechRecognition`), chosen per-feature based on whether the input is naturally one value or a list.

**Continuous** — Recipe Builder, Meal Logging, Missed-Day Logging, Library Batch-Add, Supplements. `continuous = false` on the recognizer instance, but `onend` immediately restarts listening (`setTimeout(() => _startXVoiceListening(), 300)`) as long as an active flag is still true — so from the user's perspective it never stops, one utterance rotates into the next automatically. Ends only when:
- The transcript matches `isRecipeVoiceDonePhrase()` (shared across all continuous features, not recipe-specific despite the name) — a plain-English regex (`RECIPE_VOICE_DONE_PHRASES`) covering "done", "finished", "that's it/all/everything", "stop", "I'm done", "no more", "nothing else", etc.
- The user taps the mic manually — this is always a *pause*, not a cancel: whatever's been captured so far is kept (ingredient list, water/library queue, chat text), the button/status reflects "paused", and tapping again resumes rather than restarting.

Each continuous feature routes its captured items through whatever review step already exists for that data — Recipe/Library through their own AI-parse-then-confirm flow, Meal Logging by populating `chatInput` and requiring an explicit "Log it" tap (never auto-sends), Missed-Day by auto-triggering `calculateMissedDayConv()` which itself stops at a result bubble requiring Save. Supplements is the one exception to "accumulate then review" — each recognized name is a direct, immediate, idempotent action (`toggleSupplement`-equivalent that only ever sets *taken*, never un-sets), since ticking off a supplement doesn't carry the same log-to-real-totals risk a meal does.

**Single-shot** — Weight, Water. `continuous = false`, no restart on `onend`. One utterance, parsed immediately, done. Weight only fills the input field (still requires the existing manual Confirm tap); Water logs directly, matching the zero-friction directness the existing preset buttons (+Glass/+Can/+Pint/+Bottle) already have.

---

## Cloudflare Worker

Two request modes, one `worker.js` file:

**Normal path** — forwards whatever the client actually requests rather than hardcoding anything. Previously silently forced `claude-haiku-4-5` and `max_tokens: 500` regardless of the client's request, meaning every proxy-routed call (the default for anyone without their own API key, including the entire cloud version) ran on a smaller model with a harder cap than any feature was designed around. Now:

```javascript
const model = body.model || 'claude-sonnet-4-6';
const maxTokens = body.max_tokens || 800;
const anthropicBody = { model, max_tokens: maxTokens, system: body.system, messages: body.messages };
if (body.tools) anthropicBody.tools = body.tools; // web search etc. — previously dropped silently too
```

**`multiCheck` path** — triggered by `body.multiCheck === true`. Fans out the same prompt to Claude, Gemini (`gemini-3.5-flash`), and OpenAI (`gpt-5.4-mini`) via `Promise.allSettled`, so one provider failing (bad key, quota, safety block) doesn't take down the other two. Returns `{claude, gemini, openai}`, each `{ok: true, text}` or `{ok: false, error}` — no averaging or merging happens server-side, since disagreement between providers is itself the useful signal the client displays.

Requires `GEMINI_API_KEY` and `OPENAI_API_KEY` as Worker secrets (Settings → Variables and Secrets), alongside the existing `ANTHROPIC_API_KEY`. The Gemini call includes one automatic retry after a short delay specifically for 503 "high demand" errors, per Google's own documented guidance for that error class — genuinely common right after a model's release as everyone piles onto it at once.

**Cost containment (added Phase 13)** — every call that isn't using someone's own stored API key runs through this shared Worker on Pete's own account, which scales with usage: no cap meant no ceiling as adoption grows. Two independent caps, both backed by Workers KV (`RATE_LIMIT_KV` binding → namespace `maxhealth-rate-limit`, id `a7f31fea0d224ba787cd402790934827`):

```javascript
const PER_IP_DAILY_CAP = 80;    // stops one device/household running away
const MONTHLY_CALL_CAP = 5000;  // hard ceiling on total spend regardless of scale — ~£24-30/mo worst case
```

`multiCheck` requests weight 3 against both caps (three provider calls per request) rather than counting as 1. Both keys are date-scoped (`calls:day:YYYY-MM-DD:{ip}`, `calls:month:YYYY-MM`) with matching TTLs so they self-expire rather than needing manual resets. KV is eventually-consistent, not atomic — acceptable for a cost *ceiling* with headroom, not something to rely on as an exact security boundary. If `RATE_LIMIT_KV` isn't bound, caps are silently skipped rather than erroring every request.

The app itself also has a much softer, client-side-only version of the daily cap (`PROXY_DAILY_CAP` in `maxhealth.html`, `localStorage`-based) — that one protects nothing against a determined bypass (clearing localStorage resets it instantly), it just stops an honest device's runaway retry loop from being invisible. The Worker-side caps above are the ones that actually bound worst-case cost.

**Deployment — from Android, without Wrangler:**

Wrangler requires glibc (macOS/Windows/Linux); Termux uses Android's Bionic libc, so it cannot run there at all, with no workaround. The actual solution is Cloudflare's REST API directly via `curl`, which Termux already has. Uploading a new script version replaces the *entire* binding configuration in one request — it is not additive — so every existing binding (including secrets) must be listed in `metadata.bindings` every time, or it gets dropped:

```bash
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/ACCOUNT_ID/workers/scripts/maxhealth-ai" \
  -H "Authorization: Bearer API_TOKEN" \
  -F "metadata=@metadata.json;type=application/json" \
  -F "worker.js=@worker.js;type=application/javascript+module"
```

Where `metadata.json` lists every binding, secrets included with their real `text` value each time (Cloudflare requires re-supplying secret values on every script upload — it does not accept "keep existing" by name alone):

```json
{
  "main_module": "worker.js",
  "compatibility_date": "2024-01-01",
  "bindings": [
    {"name": "ANTHROPIC_API_KEY", "type": "secret_text", "text": "..."},
    {"name": "GEMINI_API_KEY", "type": "secret_text", "text": "..."},
    {"name": "OPENAI_API_KEY", "type": "secret_text", "text": "..."},
    {"name": "RATE_LIMIT_KV", "type": "kv_namespace", "namespace_id": "a7f31fea0d224ba787cd402790934827"}
  ]
}
```

Better as a real file than an inline `-F` string — a giant one-line JSON blob typed into a phone keyboard is exactly the kind of thing that produces a stray-comma syntax error at 2am. Validate with `python3 -m json.tool metadata.json` before uploading, and delete the file straight after (`rm metadata.json`) since it briefly holds real key values in plaintext. Confirm success with a settings GET (shows binding *names*, never values) and then an actual live AI call in the app — the settings check alone doesn't prove the secret *values* survived, only that the names did.

The API Token needs the "Edit Cloudflare Workers" template, or a custom token with Workers Scripts + Workers KV Storage edit permissions (they're separate scopes — a token created only for KV namespace creation will fail Workers Scripts calls with a 400, not a helpful "wrong scope" message). The `metadata`/`type=application/javascript+module` combination matters — a plain `Content-Type: application/javascript` PUT only works for the legacy "service worker" syntax (`addEventListener('fetch', ...)`), not the ES module syntax (`export default { async fetch... }`) this worker actually uses.

---

## Version history summary

| Version | Phase | Key features |
|---------|-------|-------------|
| v1.0.0 | 1 | Initial build — dashboard, AI logging, pipeline |
| v1.9.0 | 5 | Editable grid, long meal split |
| v2.0.0 | 6 | 4-tab nav, fat tracking, supplements, barcode |
| v2.7.x | 8 | Library split, recipe scaling, A-Z nav |
| v2.9.x | 8 | Occasion tags, streak, weight trend, swipe delete |
| v3.0.x | 9 | Treatment analysis, weekly export, oncology view |
| v3.1.x | 9 | Activity card, MET calc, notes in query builder |
| v3.2.x | 9 | Model fix, GBM summary, dynamic targets |
| v3.3.x | 9 | Activity layout, water dynamic, rollover guard |
| v3.4.x | 9 | Custom modals, intelligence analysis, rollover rewrite |
| v3.10.x | 10 | Library-aware meal suggestions, ingredient substitution, recipe-aware suggestions, dashboard/tab reordering, ketosis milestones, four new nutrition sanity checks, demo mode overhaul, corrected TDEE (height fix: 188cm not 178cm) |
| v3.10.202-272 | 12 | Multi-AI consensus check (Claude/Gemini/OpenAI), log food to a past day, Activity Credit Balance, phase-aware calorie context — plus a large infrastructure/reliability pass: Worker request-forwarding, direct-API-key path (missing body, missing CORS header), sleep pipeline extractors-path bug, cloud deploy silently ~100 versions behind, fuzzy-match apostrophe/brand fixes, activity-credit duplicate-calculation unification |
| v3.10.289-296 | 13 | Continuous voice input extended across meal logging, missed-day, library batch-add, and supplements (plus single-shot voice for weight/water); fixed a meal-voice pause dead-end (manual mic-tap now offers Log-it, not just resume); Cloudflare Worker server-side rate limiting (per-IP daily cap + hard monthly cost ceiling via Workers KV) to bound shared-proxy cost regardless of user scale |
| v3.10.297-417 | 14 | Condition-scoping audit (11 fixes); 3-pronged ingredient search (Library → OFF → AI); History target snapshots (fixes retroactive rewriting from live TARGETS proxy); Ketosis Adherence as a genuine Trends chart; found and fixed a real silent-data-loss bug (broken DD/MM/YY string date-sort scrambled history's true chronological order, causing the 30-day localStorage-size logic to silently strip recent days' items); full theme system rebuild (Base/Accent fully independent, was 5 fixed bundles); found and fixed a second root-cause bug (leftover dead code setting `data-theme` on `document.body` silently overrode the correct accent for everything visible); Settings auto-save + Change Log (removed 10 explicit Save buttons); real server-side full backup (`/save-full-backup`, 7-day rotation, automatic daily trigger) — `data/backup/` finally gets used, having existed unused since the folder structure was first created; tap-to-reveal help text across Import/Manage/Insights (several dozen instances) |

---

## Common operations

**Deploy after update:**
```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html
cd /storage/emulated/0/maxhealth/app/maxhealth
bash bump_and_deploy.sh X.X.X "description"
```
Handles version bump (both references), div-balance check, commit, push, and push verification (confirms `origin/main` actually matches local HEAD after pushing — this was silently failing for ~100 versions before the verification step existed). For anything other than `maxhealth.html` (worker.js, docs), commit manually and selectively; avoid `git add -A`, which stages pycache/backup noise alongside real changes.

**Full backup:**
```bash
pkg install zip -y
cd /storage/emulated/0/maxhealth
zip -r "/storage/emulated/0/Download/maxhealth_backup_$(date +%Y%m%d).zip" app/maxhealth/ data/tables/
```

**Rollback:**
```bash
cd /storage/emulated/0/maxhealth/app/maxhealth
git log --oneline -10
git reset --hard COMMIT_HASH
git push --force
```

**Sync wearable data:**
```bash
cd /storage/emulated/0/maxhealth/app
python update_health.py
```

**Check server:**
```bash
curl http://localhost:5757/ping
```

---

## Full server-side backup (Phase 14)

`BACKUP_DIR` (`data/backup/`) existed since the folder structure was first set up — created on every server startup — but nothing ever wrote to it until this. The 5 CSV tables had their own server persistence via `/save-library-csv` etc. and `saveLibrary()`'s "always try, silent fail if unavailable" pattern; the full JSON state (today's log, complete history, everything `buildFullBackupPayload()` builds client-side) had no server-side home at all, only ever a local browser download.

**Endpoint:** `POST /save-full-backup` (server.py) — accepts the same JSON `exportAll()` already builds, writes to `data/backup/maxhealth_backup_YYYY-MM-DD.json`, one file per calendar day. 7-day rotation on every write (deletes anything beyond the most recent 7 files, sorted by filename).

**Client-side trigger (maxhealth.html):**
- `buildFullBackupPayload()` — the shared payload builder, used by both the local download and the server POST, so they can never drift apart
- `saveFullBackupToServer(silent)` — checks `_serverOnline` before attempting (unlike the older CSV pattern, which attempts-and-silently-fails); posts to `/save-full-backup`; updates `mh_last_full_backup_date` on success
- `autoBackupIfNeeded()` — called from `checkServer()`'s confirmed-local success path (both the immediate hostname-based one and the async ping-confirmed one — there are two, see below). Checks `mh_last_full_backup_date` against today; if not yet done today, backs up silently. Not a true scheduled job — it's "first app-open of the day," which covers the real goal (a recent server copy always exists) for anyone who opens the app daily, which logging itself already requires

**Cloud users:** `_serverOnline` is false (no local server reachable), so `saveFullBackupToServer()` returns early without attempting anything — local download via `exportAll()` still works exactly as before, just without the server half. This is correct, not a gap — cloud users have never had a server to back up to.

**Gotcha worth knowing:** the badge showing "⬡ LOCAL" and the backup/warning text updating are two separate code paths — one fires immediately on hostname alone (before any server ping resolves), the other fires later inside `checkServer()`'s async success callback. Both now call `updateDataBackupWarningForMode()` / `autoBackupIfNeeded()`, but if either one is extended in future, check both call sites, not just one — this exact gap caused the backup-status text to visibly lag behind the badge for a moment on a previous version.

---

## Boot survival (Termux)

Three boot scripts in `~/.termux/boot/` fire after any phone reboot:

| Script | Purpose |
|--------|---------|
| `start-crond.sh` | Starts crond after 5s delay (allows storage to mount) |
| `start-watchdog.sh` | Acquires wake-lock via `termux-wake-lock`, immediately runs `mh_watchdog.sh` |
| `maxedhealth.sh` | Runs `sync.sh` to restore data after reboot |

`mh_watchdog.sh` runs via cron every minute — checks if `server.py` is alive, restarts it if not, kills duplicate processes. `termux-wake-lock` prevents Android Doze from suspending the check between cron ticks.

Requires: **Termux:Boot** and **Termux:API** from F-Droid (same signing key as Termux). `setup.sh` (v3.2+) auto-detects whether these are installed and prompts the one-time manual install only when missing.

---

## Local Network Access (Chrome LNA)

Chrome ~142–149 enforced the Local Network Access (LNA) policy, which blocks cross-origin requests — including WebSocket — from public HTTPS pages (GitHub Pages) to localhost. The old auto-redirect from `pete-maxhealth.github.io` to `localhost:5757` no longer works.

**Current behaviour:**
- GitHub Pages URL is for cloud-only users (no local server)
- Local server users should pin `localhost:5757` directly as their home screen shortcut
- setup.sh explicitly instructs this in its closing screen
- If a local server is detected while on the public URL, a one-time banner offers a user-gesture tap to switch (user-gesture navigation is permitted by LNA, silent fetch/WebSocket is not)

---

## Amazfit/Zepp data pipeline

Zepp exports are AES-encrypted zip files. Python's stdlib `zipfile` cannot decrypt these — `pyzipper` is required (`pip install pyzipper --break-system-packages`). `amazfit.py` uses `pyzipper.AESZipFile` when a password is supplied.

**Field precedence:**
- `AMAZFIT_EXCLUSIVE` fields (`steps`, `distance_m`, `calories_active`) always overwrite on re-sync — Zepp's daily totals can be partial on first export and correct themselves later. These fields have no other source in the pipeline, so fill-only merge would permanently lock in stale values.
- All other fields follow fill-only merge — Withings owns weight/body comp, RingConn owns HRV/sleep/SpO2/HR.

`fix_amazfit_steps.py` — one-off retroactive correction tool. Run manually after fixing the pipeline to backfill historical data.

**Extractors-path bug — sleep data stalled at a fixed date for over a week.** A folder restructure moved `server.py`/`maxhealth.html` a level deeper (`app/` → `app/maxhealth/`) without updating the extractors path inside the *copy* of `update_health.py` that the in-app Sync Now button actually calls. That path was computed relative to the script's own file location (`os.path.dirname(__file__)`), so after the restructure it silently pointed at a folder that didn't exist — every sync reported "no extractor found" for every device and returned zero new data, with nothing visibly wrong from the UI. A second, older, disconnected copy of `update_health.py` also existed one level up, resolving its `BASE` constant to a completely different (non-existent) data folder if ever run manually. Fixed by deleting the stray copy and correcting the extractors path in the one canonical script to resolve from `BASE` (which was already correct) rather than the script's own directory. Worth checking for this same class of bug — a path computed relative to `__file__` rather than a shared, correct base constant — anywhere else a folder restructure might have silently broken.

---

## Condition/Protocol system

`localStorage('mh_condition')` stores the user's selected condition:

| Key | Condition | Carb target | Report framing |
|-----|-----------|-------------|----------------|
| `gbm` | GBM — therapeutic ketogenic | 20–30g | Evidence-categorised ([Proven]/[Early Stage]/[Speculative]), gaining phase context |
| `epilepsy` | Epilepsy — therapeutic ketogenic | 20–30g | Seizure control focus, strict compliance |
| `strict_keto` | Strict Ketosis | 20–50g | Metabolic health, weight focus |
| `t1_diabetes` | Type 1 Diabetes | Carb-aware | Insulin management, flag dosing implications |
| `t2_diabetes` | Type 2 Diabetes | 50–100g | Glucose stability, HbA1c framing |
| `general` | General Health / Weight Loss | 100–150g | Calorie deficit, balanced approach |

`buildPatientContext()` and `patientContextBlock()` in `maxhealth.html` build all AI report prompts from this value. The `CONDITION_META` table maps conditions to protocol labels, evidence notes and report framing. Carb ceilings themselves are set separately in Settings → Carb Ceilings and are independent of this selection.

---

## Suggested Targets calculator

`renderSuggestedTargets()` in `maxhealth.html`. Called on Settings open and when weight updates.

**Inputs:** `mh_height_cm`, `mh_age`, `mh_sex`, `state.weight` (or `getLastKnownWeight()`), `mh_goal`, `mh_condition`, `mh_ceil_standard`, last 30 days avg steps from `state.history`.

**Calculation:**
1. BMR via Mifflin-St Jeor (sex-adjusted)
2. Activity multiplier from avg steps: >12k=1.725, >8k=1.55, >5k=1.375, else 1.2
3. TDEE = BMR × multiplier
4. Calories = TDEE −500 (lose) / ±0 (maintain) / +400 (gain)
5. Protein = 1.8g/kg (GBM/Epilepsy), 1.6g/kg (all others)
6. Fat = (calories − protein×4 − carbCeiling×4) ÷ 9
7. Carbs = untouched (from existing ceiling)

**Condition overlay:** GBM/Epilepsy shows fat% vs ≥65% therapeutic threshold with ✓/⚠. T1D flags insulin dosing warning. T2D flags carb ceiling dependency.

`applySuggestedTargets()` pushes values into Settings fields and calls `saveMacroTargets()`.

---

## Weight Phase History

Stored in `localStorage('mh_phase_history')` as newline-separated `YYYY-MM-DD goal` entries (goal = loss/maintain/gain), sorted earliest first.

`getPhaseHistory()` parses and returns sorted array. `getPhaseForDate(isoDate)` walks the array to find the active phase for any given date.

`setGoal()` automatically appends a new timestamped entry when the goal changes — only if the goal actually changed from the previous entry (deduplication). The textarea in Settings is for historical backdating only.

All AI reports receive the full phase history via `patientContextBlock()` with explicit instruction not to treat intentional loss as a concern.

---

## ⭐ Full Summary

`runFullSummary()` — pre-built 9-section comprehensive analysis prompt fed directly into `askReportsAI()`. Covers: nutrition overview, weight & body composition, ketosis quality, sleep, HRV & recovery, activity, best performing period, areas needing attention, protocol verdict. Phase-aware and condition-specific via `patientContextBlock()`. Nil days excluded.

---

## Nil day filtering

Days with <100 kcal logged are excluded from:
- `buildPatientContext()` — AI reports context and averages
- `askReportsAI()` raw data table
- Monthly summary local stats
- Report summary cards (best carbs, protein misses, fat misses)

Gap days are reported to the AI as "X day(s) had no nutrition logged (tracking gaps, not zero intake)" so it can acknowledge gaps without treating them as nutritional data points.

---

## Generic section reordering (Reports / Manage / Import)

Rather than hand-wire reorder buttons into ~25+ individual sections, `makeContainerReorderable(containerEl, scopeKey)` discovers sections automatically at runtime by scanning for existing `onclick="toggleSection(key, wrapId, ...)"` attributes — every collapsible section already has one, so no HTML changes were needed per section. Injects ▲▼ buttons directly into each title, tracks order in `localStorage['mh_reorder_' + scopeKey]`, and moves title+wrap element pairs together via `appendChild`.

**Critical safety detail:** `applyGenericOrder()` checks whether the DOM already matches the stored order before doing anything — `appendChild` on an element already in the correct position still forces a real remove+reinsert, which destroys focus on any input inside it (this was found and fixed after it silently broke a search box on every keystroke). Never call the move logic unconditionally on every render.

Debug/troubleshooting sections (`set-bodycompdebug`, `set-rollover`) are explicitly excluded from the reorderable set — they live inside a fixed "⚠ Advanced" warning box, and reordering them would eventually orphan that box from the sections it's meant to mark.

The Today dashboard (`applyDashboardOrder`) and Library tab (`applyLibraryOrder`) use separate, similar-but-not-shared implementations of the same pattern, built earlier and kept independent to avoid risk when the generic version was added later.

---

## Nutrition logging sanity checks

`sanitiseFatValues(items)` runs on every logging path (fresh log, edit, library quick-log) and applies, in order:

1. **Meat/fish carb correction** — plain meat or fish claiming carbs gets auto-corrected to 0g, with kcal recalculated from protein+fat alone.
2. **Pure-fat under-scaling correction** — oils/butter/lard etc. with fat% too low for the stated amount get corrected to ~90-100% fat by weight.
3. **Atwater consistency** — kcal must roughly equal protein×4 + carbs×4 + fat×9 (tolerance: greater of 30kcal or 15%). Auto-corrects kcal to match the macros. Explicitly excludes alcohol (beer/wine/spirits etc.), since alcohol carries real calories this formula can't see.
4. **Low-carb-fruit warning** — a fruit-named item claiming under 2g carbs gets flagged (not auto-corrected, since there's no reliable universal fruit-carb table to correct to).
5. **Implausible portion size** — under 1g or over 2000g gets flagged.
6. **Macro-mass plausibility** — protein+fat+carbs (grams) cannot exceed the food's own stated weight; this is a hard physical constraint, not a judgement call, so it's flagged prominently (🔴) rather than as a routine warning.

Checks 1-2 auto-correct silently with a visible explanation; checks 3-6 either auto-correct (3) or warn (4-6). `confirmMealLog()` re-runs these checks immediately before the actual log commit and shows an explicit "are you sure?" gate for anything flagged by checks 5-6, rather than blocking outright — accommodates genuine large-batch cooking while still surfacing the issue.

---

## Fuzzy library matching

`fuzzyFindInLibrary(name)` — used for both "did you mean X?" confirmation and duplicate-detection before saving. Strips stopwords, then requires word-overlap ≥50% (≥99% for 2-word queries, to prevent a single shared generic word like "mince" or "chicken" from false-matching completely different products — found via a real case: "chicken mince" matching "beef mince" on the shared word "mince" alone).

**Brand, meat-type, and food-category disqualification:** if the query names a specific supermarket brand, meat/protein type, or food category (bread, cheese, milk, rice, pasta, etc.) that genuinely differs from a candidate's, that candidate is disqualified outright regardless of overall word-overlap score. Food-category disqualification was added after a real case: "Warburtons white bread" matched "white cheese (triangular slices)" purely because two generic descriptor words ("white", "slices") happened to overlap, while the words that actually identify the food ("bread" vs "cheese") shared nothing. `canonicalBrand()`/`canonicalMeatType()`/`canonicalCategory()` normalize spelling/plural variants to the same identity before comparing.

This same category-mismatch check exists in **four** separate matching functions — `fuzzyFindInLibrary` (strict duplicate check), `findLibrarySubstitutes` (loose substitution flow), `findComparableLibraryItems` (Add Food comparison), and the duplicate scanner's `nameScore`. All four were found to have the identical underlying vulnerability; fixing one and assuming the others were safe was itself a mistake caught mid-session — check all matching functions together when fixing this class of bug, not just the one that happened to surface first.

`findLibrarySubstitutes(name, excludeName, limit)` is the looser cousin used for the substitution flow — deliberately allows brand differences (that's the point: offering a real Lidl alternative when the query asks for Asda), returning up to 3 candidates from the same broad food category.

**Two further false-positive causes found this session, both in the same class of bug:**

1. **Unrecognized brand on one side.** The existing brand-mismatch protection only works when *both* names have a brand recognized from `LIBRARY_KNOWN_BRANDS`. If the query names a real, recognized brand but the candidate's own brand isn't in that list at all (an unusual or misspelled name), the protection silently doesn't apply — the match falls through to generic word-overlap scoring. This let "turkey sausage Asda" match "Turkey Sausages x2 Oakhahen" on 2 of 3 words, missing only the brand itself, since "Oakhahen" wasn't a recognized brand and so couldn't be flagged as a mismatch. Fix: when the query names a real brand but the candidate's brand can't be identified at all, require every query word to match rather than the normal partial threshold, since the one disqualifying signal (brand) is precisely the one that can't be verified either way.
2. **Apostrophes break substring matching entirely.** As raw text, `"tennent's".includes("tennents")` is false — the apostrophe interrupts the character sequence, so a query typed without it ("Tennents") never matches a library name that has it ("Tennent's"), regardless of how similar they otherwise are. Affects any possessive brand name (McDonald's, Cadbury's, Warburton's). Fixed by stripping both straight and curly apostrophes (`/['\u2019]/g`) from both the query and item words before splitting into comparison tokens, in both `fuzzyFindInLibrary` and `findLibrarySubstitutes`.

---

## Unified AI calling — callHealthAI()

Every AI call in the app (Ask AI, Full Summary, GBM Summary, Oncology narrative, portion estimation, health-context queries, both missed-day calculators, barcode reading) routes through one shared function, `callHealthAI(prompt, {maxTokens, system, image, webSearch})`, instead of each maintaining its own copy of the fetch/parse logic.

**Why this mattered in practice:** the previous per-call-site copies each had their own fallback of the form `text = response.content?.[0]?.text || 'Could not generate X.'` — meaning any unexpected response (a proxy error, a rate limit, an empty completion) was silently swallowed into an identical generic message everywhere, with zero indication of the actual cause. When the Anthropic account backing the shared proxy ran out of credit, every AI feature appeared to fail identically and independently — the unified function's real error surfacing (HTTP status, actual error body) is what made it possible to diagnose this as one external billing issue in a single step, rather than investigating 9 separately "broken" features.

Returns `{ok: true, text}` or `{ok: false, error}` — callers check `.ok` and show `.error` directly rather than a canned message. Provider selection (configured Claude/OpenAI key vs shared default proxy) happens once, inside the function, so a configured personal API key is now correctly respected by every call site — several previously always hit the shared proxy regardless.

`webSearch: true` adds the Messages API's native `web_search_20250305` tool to the request. Tried for the GBM Research Digest specifically — the model correctly refused to fabricate results rather than inventing plausible-sounding citations when it turned out the proxy doesn't reliably forward this through, which is the right failure mode, just not a useful one. Replaced with a "Copy Research Request" button instead: copies a ready-made prompt for pasting into a real chat conversation, where genuine web search exists.

**Two structural bugs found this session, specific to the direct-API-key path** (provider set to Claude/OpenAI with a personal key configured, rather than the shared proxy):

1. **Missing request body entirely.** The direct-Claude branch's `fetch()` call had no `body:` field at all — sending Anthropic a genuinely empty request every time. Surfaced as "The request body is not valid JSON: zero-length, empty document" once the API key itself was confirmed valid, which is what made it identifiable rather than looking like another key/connectivity issue.
2. **Missing CORS header.** Direct browser calls to Anthropic's API require `anthropic-dangerous-direct-browser-access: true` — without it, the browser silently blocks the response as a CORS violation, surfacing only as a generic `TypeError: Failed to fetch` with no other detail. This meant the direct-key path had likely never worked from a browser context since it was first built, masked because an invalid key failed at a different, more informative stage before ever reaching the CORS check.

Both fixed in `callHealthAI()`. Two other functions (`suggestMealFromLibrary`, `_processLabelEstimate`) had their own separate, older request-building code instead of using this shared helper, and read the API key from the wrong localStorage key (`mh_api_key` instead of `mh_apikey`) — always behaving as if no direct key was configured. Consolidated onto `callHealthAI()`, closing both the wrong-key bug and the two structural ones above for these paths at the same time.

---

## Day-mode-aware ceiling comparison (recurring bug pattern)

`getTargets()` returns `{standard, occasion, holiday}` — carb ceilings differ by day mode. A day should always be judged against **its own logged mode's** ceiling, not a flat standard-only one, or an occasion/holiday day within its own (wider) ceiling gets wrongly counted as a failure.

This exact bug — comparing every day against `getTargets().standard.carbs` regardless of `day.mode` — was found independently in **eight** separate places over one session: Weekly Summary, Oncology Report, Report Summary, the ketosis streak counter, Treatment Analysis, GBM Stats, the AI Brief generator, and Sleep & Ketosis correlation. The AI Brief generator had a more severe variant — `getTargets().carbs` doesn't exist at all on the object returned (no top-level `.carbs`), so the comparison was always against `undefined`, meaning adherence was reported as 0% unconditionally, regardless of actual data, every time that specific report ran.

The fix pattern used consistently: `const carbCeilFor = d => targetsAll[d.mode || 'standard']?.carbs ?? targetsAll.standard.carbs;` then compare each day against `carbCeilFor(day)` rather than a single flat value captured once outside the loop. Worth checking for a ninth instance if a carb-adherence percentage anywhere looks wrong on an occasion/holiday-heavy period — this was never fixed via one exhaustive sweep, only found opportunistically while working on something else each time.

---

## Duplicate activity-calorie calculations (found and unified this session)

Two genuinely separate implementations existed for "how many extra calories does today's exercise earn": `updateActivityNudge()` / `calcActivityKcal()` (a proper `MET × weight(kg) × hours` calculation, feeding the real dashboard total) and `getActivityNudge()` (an older, cruder function powering the pinned-tag banner specifically, which just checked whether any tag *text* contained a word like "cardio" or "walking" and added a flat `+150kcal` regardless of actual logged duration — a 10-minute walk and a 3-hour walk scored identically).

Because these operated on entirely different data (structured `getActivities()` duration/effort vs raw tag string matching), they could — and did — disagree by an order of magnitude for the same real day's exercise (150kcal vs 1241kcal for the same 100 minutes of walking). Fixed by rewriting `getActivityNudge()` to call `calcActivityKcal()` the same way the dashboard total does, so the banner and the dashboard can no longer show two different numbers for the same day again. Both functions also had `getTargets().standard` hardcoded regardless of the actual current day mode — fixed to read `getTargets()[state.dayMode]`, though this doesn't currently change any real output since `kcal` targets are presently identical across day modes (only the carb ceiling varies by mode).

---

## Library-aware meal suggestions

`suggestMealFromLibrary()` sends both the raw Food Library and saved Recipes (shown per-serving, not just totals) to the AI alongside today's actual remaining macros. The AI's role is limited to choosing which real items/recipes fit — it never computes final totals itself. `renderLibraryComboSuggestions()` resolves each suggestion against real library/recipe data and computes totals deterministically in JS (recipe servings math reuses the exact same formula as `logRecipe()` itself, so a suggested recipe logs identically to manually applying it).

---

## Log food to a past day

`runMultiAICheck` and past-day logging share the same underlying principle: reuse the existing pipeline rather than build a parallel one. Triggered from History's "🍽 + Add food to this day", which sets `window._logTargetDate` and switches to the normal Log tab — the exact same chat interface, AI parsing, photo/barcode/library support as logging today.

`logFoods()` — the single choke point every logging path already funnels through — checks this flag early: if set and not today, it takes a simplified path that appends the entry to that historical day's `log` array (rather than `state.todayLog`), recomputes `day.totals` by summing the full log (the same pattern already used by `editHistEntry`/`deleteHistEntry`), and skips every today-only side effect (water auto-add, weight-stamping, the "today's remaining" confirmation bubble, save-to-library prompts) since none of those make sense for a day that isn't today. A persistent yellow banner shows which day is currently targeted, cleared automatically once the log commits.

---

## Multi-AI consensus check

`runMultiAICheck(targetIndex)` — an optional index scopes the check to a single item within a larger pending meal (the common real case: verify the roast beef specifically, not the whole plate); omitted, it checks the whole pending list.

Sends a strict-format prompt (`KCAL: / PROTEIN: / FAT: / CARBS:`, nothing else) to the Worker's `multiCheck` endpoint, which fans it out to Claude/Gemini/OpenAI in parallel. Each provider's raw response is checked two ways:

1. **Cross-provider disagreement** — a >25% spread between the highest and lowest calorie estimate is flagged as worth finding a real label, not trusted as-is.
2. **Internal (Atwater) consistency** — each provider's own stated kcal is checked against what its own reported macros actually add up to (`protein×4 + fat×9 + carbs×4`). A >15% gap flags that specific estimate as internally sloppy, independent of how it compares to the others.

Averaging only applies when checking a single item (`isSingleItem`) — a whole multi-item meal has no single field a blended number could apply to. Per-provider checkboxes (rendered per result, `id="{checkId}-{providerKey}"`) let a wildly-off provider be excluded before applying the average; read at click time via `applyMultiAIAverage()`, not baked in when the results first rendered, so unchecking something genuinely excludes it. If an edit form for a different item happens to be open when a check starts, it's closed explicitly with a toast rather than silently disappearing later when the preview re-renders.

---

## Activity Credit Balance

`getUnclaimedActivityCredit(windowDays)` — reads real stored history (`day.exercises`, already precomputed per-exercise `kcal`; `day.totals.kcal` for actual intake; `day.mode` for that day's base target via `TARGETS[day.mode]`). For each day with logged exercise credit, computes how much of that credit was actually "claimed" by eating above base target (`surplusAboveBase = max(0, actual - baseTarget)`), and how much went unclaimed (`max(0, dayCredit - surplusAboveBase)`) — if intake didn't even reach base that day, none of the credit was claimed at all.

Rendered in Insights → Trends via `renderActivityCreditBalance()`, called from `renderTrends()`. Window defaults to 14 days, adjustable 7–90 via an input in the card itself (`mh_activity_credit_window` in localStorage) — deliberately kept as a simple in-card control rather than a separate Settings entry, since it's the only real "tuning" this feature needs. Interpretation text differs by `mh_goal` (maintain/gain/lose), since "25%+ of earned credit went unclaimed" means a different thing depending on which direction the user is actually trying to move.

---

## Phase-aware calorie context

Added to `updateDashboard()`'s Remaining Today section (`#calorieContextNote`), populated whenever `activityExtra > 0` for the day. Computes `vsBase = totals.kcal - targets.kcal` (surplus/deficit against the *base*, non-exercise-adjusted target) and `vsBoosted = totals.kcal - adjustedKcalTarget` (the same, against the exercise-boosted target), then picks wording based on `mh_goal`:

- **Above base already**: the gap to the boosted number is framed as unclaimed activity credit, not a real shortfall — wording differs slightly for maintain (reassuring) vs gain (still worth closing if maximising gain pace matters) vs lose (fine either way).
- **Below base**: flagged regardless of goal, since this isn't about unclaimed exercise room at all — it's genuine under-eating.

This is the single-day companion to Activity Credit Balance above — this note explains what *today's* number means; the Insights card tracks whether the same pattern is recurring often enough to matter.

---



---

## Known issues

- Water target celebration not firing
- `mh_reorder_manage` order may need re-saving after adding a new reorderable section, since new entries aren't automatically inserted into an already-saved custom order
- OpenAI has no persistent free tier (unlike Gemini's Flash tier) — multi-AI check will incur small real per-use cost on that provider specifically
- Full App State (Import tab) is export-only — no restore-from-backup function exists yet. Genuinely different, more careful feature than the other 5 tables' import (which only ever adds/updates rows); a full-state restore would overwrite everything, including today's log

**Resolved this session, previously listed here:**
- ~~Cloudflare Worker cannot be updated from Android~~ — solved via direct Cloudflare REST API calls through `curl` (see Cloudflare Worker section above)
- ~~Monthly summary may truncate if Cloudflare Worker caps `max_tokens`~~ — this was the Worker's hardcoded `max_tokens: 500`, now forwards the client's actual request
- ~~Tab bleeding — occasional, cosmetic only~~ — was specifically the Reset button's text overflowing its container once a 6th hydration button was added; fixed with overflow/ellipsis safety on the button style
- ~~History items silently disappearing while totals stayed correct~~ — genuinely difficult bug, several rounds of live tracing before finding it: `state.history` was sorted with a plain string comparison on "DD/MM/YY" dates, which is fundamentally broken (day comes first in the string, so "31/12/25" string-sorts as "greater than" "09/08/26"). This scrambled the array's true chronological order, and the 30-day localStorage-size-management logic — which strips item-level detail from anything beyond the 30 most recent, using array *position* as a proxy for recency — would then silently strip a genuinely recent day's items on every save. Fixed with a real `ddmmyySortKey()` comparator replacing the broken one in all 10 places it existed, plus a one-time corrective re-sort on load so already-scrambled history self-heals immediately
- ~~Custom accent colour not visually applying despite the CSS variable being confirmed correct~~ — a second, separate root-cause hunt. Leftover dead code from an older, already-removed parallel theme system still set `data-theme` directly on `document.body` on every startup. Since `<body>` contains the entire visible app and CSS custom properties resolve to the nearest declaration, this silently re-declared the theme's own default accent on body, overriding the correctly-set value inherited from `<html>` for everything visible — while the computed-value check on `documentElement` (where the inline style genuinely lived) kept confirming "correct," which is what made this one hard to see

---

*Built with Claude by Anthropic*
