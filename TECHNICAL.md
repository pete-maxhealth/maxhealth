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
| `mhstart` command | `$PREFIX/bin/mhstart` (installed by `setup.sh`, works from any directory) |
| Auto-update script | `~/mh_autoupdate.sh` |
| Watchdog script | `~/mh_watchdog.sh` |
| Boot script (crond) | `~/.termux/boot/start-crond.sh` |
| Boot script (watchdog) | `~/.termux/boot/start-watchdog.sh` |
| Boot script (auto-update + start) | `~/.termux/boot/maxhealth.sh` |

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
| `mh_visual_theme` | Visual colour theme |
| `mh_color_scheme` | Dark/light/auto scheme |
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

**Deployment — from Android, without Wrangler:**

Wrangler requires glibc (macOS/Windows/Linux); Termux uses Android's Bionic libc, so it cannot run there at all, with no workaround. The actual solution is Cloudflare's REST API directly via `curl`, which Termux already has:

```bash
curl -X PUT "https://api.cloudflare.com/client/v4/accounts/ACCOUNT_ID/workers/scripts/maxhealth-ai" \
  -H "Authorization: Bearer API_TOKEN" \
  -F 'metadata={"main_module":"worker.js","compatibility_date":"2024-01-01"};type=application/json' \
  -F "worker.js=@worker.js;type=application/javascript+module"
```

The API Token needs the "Edit Cloudflare Workers" template (Cloudflare dashboard → profile → My Profile → API Tokens). The `metadata`/`type=application/javascript+module` combination matters — a plain `Content-Type: application/javascript` PUT only works for the legacy "service worker" syntax (`addEventListener('fetch', ...)`), not the ES module syntax (`export default { async fetch... }`) this worker actually uses.

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
| v3.10.273-450 | 15 | Wear OS/Zepp watchapp development, pattern-learning backend actually deployed live for the first time, full ingredient substitution system, unified Saved Prompts library — plus another large accuracy/reliability pass: recipe totals 1000× scaling bug, Vitals score self-contradiction, AI Reports fabricated fat target + missing "today" data, diabetes condition silently not applying, save-to-library silent overwrite, Withings import name-hardcoding (two separate files), device auto-update infrastructure, Patterns card misleading message. Phase 13-14 not individually documented here — see CHANGELOG.md's Known Outstanding Items |
| v3.10.451-465 | 16 | Site-wide search, Migraine/Cluster Headache conditions with real evidence grading, Condition History + period-aware AI reports (compare periods via free text, no dropdown), full polyols/net-carbs implementation, Health Connect server-side pipeline (native bridge app written, first build pending) — plus recipe/substitution fixes: pre-fill bug, missing add-ingredient button, single malformed ingredient silently blanking the whole list, unreachable cancel button on a long picker list. Also found CONDITION_META missing 3 conditions (AI advice was silently generic for them), and a second independently-hardcoded ceiling mapping in onboarding drifted out of sync with the shared function everywhere else uses |
| v3.10.466-471 | 17 | Remote diagnostics (`/system-status` + App Health Check) — confirmed solving a real, previously stuck device end-to-end. Personalised Activity Level (real Profile setting, research-backed fitness-adjusted walking pace bands) plus real auto-switch from sustained step-count trends, modelled on but more noise-resistant than the existing weight/goal auto-switch — plus a genuine long-standing structural div-balance bug found via the new diagnostics (stray duplicate closing tag), `bump_and_deploy.sh`'s own safety check fixed to match (it had the same blind spot), 3 debug/settings sections found being silently relocated out of Advanced Tools by the reorder system, and 2 further small pre-existing bugs (a notification setting never restored from backup, Condition History's field never populated on fresh page load) |
| v3.10.472-499 | 17 | Not individually documented — see CHANGELOG.md's Known Outstanding Items |
| v3.10.500-510 | 17 | Itemized per-ingredient editors for Today's Log and History (add/remove/edit, amount-driven auto-scale, new bulk "scale entire entry to X%"), photo/label AI pipeline unification (toggle removed, ~140 lines dead code, AI-assumed-amount detector), a critical library-meal portion misparse bug ("1 serving" read as 1 gram via a bare `parseFloat`), weight trend staleness fix, condition-aware Carb Zones tooltip, Open Food Facts text-search fibre/polyols parity with barcode scan — plus, outside `maxhealth.html`'s own versioning: a RingConn sleep date-shift bug found and fixed (affected ~half of all sleep sessions), a full historical backfill from raw export data, and an inbox retention policy added where none existed before |

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

## Boot survival (Termux)

Three boot scripts in `~/.termux/boot/` fire after any phone reboot:

| Script | Purpose |
|--------|---------|
| `start-crond.sh` | Starts crond after 5s delay (allows storage to mount) |
| `start-watchdog.sh` | Acquires wake-lock via `termux-wake-lock`, immediately runs `mh_watchdog.sh` |
| `maxhealth.sh` | Checks for an update immediately (`mh_autoupdate.sh`), then starts the server (`mhstart`) |

`mh_watchdog.sh` runs via cron every minute — checks if `server.py` is alive, restarts it if not, kills duplicate processes. `termux-wake-lock` prevents Android Doze from suspending the check between cron ticks.

Requires: **Termux:Boot** and **Termux:API** from F-Droid (same signing key as Termux). `setup.sh` (v3.2+) auto-detects whether these are installed and prompts the one-time manual install only when missing.

**`mhstart`** is installed to `$PREFIX/bin/mhstart` by `setup.sh`, so it works as a global command from any directory. An earlier version `cd`'d one level too shallow (`app/` instead of `app/maxhealth/`) — since a failed `cd` doesn't stop a bash script by default, this silently fell through to running `python server.py` from whatever directory the caller happened to already be in, rather than failing loudly. Only ever "worked" because Termux sessions here are almost always already sitting in the app folder when `mhstart` gets typed manually. Fixed to `cd` to the correct path with an explicit failure message if the app folder isn't found.

### Auto-update

`~/mh_autoupdate.sh` runs via cron every 30 minutes (`*/30 * * * *`), and once immediately on every boot via `maxhealth.sh` above:

1. `git fetch origin main --quiet`
2. Compares local `HEAD` against `origin/main`
3. If different: `git reset --hard origin/main`, then kills the running server (the watchdog above picks it back up within 60 seconds — this script deliberately doesn't restart the server itself, avoiding duplicating logic the watchdog already owns)
4. Logs every check to `~/mh_autoupdate.log`

Uses `git reset --hard` rather than a merge deliberately — these are pure end-user devices that should never carry real local code edits, so always converging to exactly what's on GitHub is safer than risking a merge conflict silently blocking every future update forever with no one watching to resolve it.

This exists because devices could otherwise run stale code indefinitely with no way to catch up on their own — every fix required someone to manually `git pull` on that specific device. Folded into `setup.sh` itself (not just patched onto existing installs by hand), so every fresh install gets this automatically.

### Remote diagnostics — `/system-status`

New `server.py` GET endpoint, wired into the existing App Health Check tool (Settings → Manage → Advanced Troubleshooting Tools). Reads (fixed, hardcoded commands only, no user input reaches `subprocess` — no injection risk despite being a live shell call):

- `~/mh_autoupdate.log` (last 15 lines + total line count)
- `crontab -l` output
- Whether `crond` is actually running (`pgrep -f crond`)
- How many `server.py` processes are running (`pgrep -f "python.*server.py"` — should be exactly 1)

Built specifically so a stuck device can be debugged **remotely**, without needing Termux command-line access on the affected phone — the person having the issue taps the button and copies the output, no terminal commands needed on their end at all. **Confirmed working on a real, previously stuck device**: first correctly showed `crond` wasn't running (the actual root cause — nothing can fire on schedule regardless of what's in crontab), then, after `crond` was restarted, showed the real log entries proving auto-update genuinely worked unattended at the next scheduled tick.

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

## RingConn sleep date-shift bug & backfill

**The bug:** `extractors/ringconn.py`'s `_parse_sleep` shifted any session with a start hour before 04:00 back to the previous calendar date, on the assumption that a post-midnight bedtime is "really" the tail end of the prior night. RingConn's own app doesn't apply this adjustment — it labels a session by the raw calendar date of `Start Time`, no adjustment at all. Confirmed directly: a session RingConn's own app displayed as "Aug 19" (bed 01:01, wake 08:13) was landing in `combined.csv` under "Aug 18."

**Scale, checked against a full year's raw export** (`Data_Export-*-2025-08-19-2026-08-19.zip`): 173 of 348 sleep sessions (essentially half) had a pre-04:00 start and were affected. 101 of those were consecutive-night pairs, creating genuine multi-day cascades rather than isolated single-date errors.

**Fix:** the `hour < 4` adjustment removed outright; the extractor now trusts `Start Time`'s own calendar date unconditionally.

**Why a plain pipeline re-run wouldn't have fixed already-wrong dates:** `merge_with_precedence()` tracks which source last set each field (`field_sources.json`) and only overwrites a field if the *new* source outranks whoever's on record for it. RingConn is already priority-1 for sleep fields. Re-running the fixed extractor against a date already attributed to `ringconn` — even with a genuinely different (correct) value — isn't a higher-priority source than "ringconn" already on record, so the merge logic silently skips writing the correction. This would have left roughly half the corrupted dates unfixed with no error or warning.

**Backfill method used instead:** a standalone script, bypassing `merge_with_precedence()` entirely for this one-off correction — read the raw export as ground truth, and for every date it covers, directly overwrite just the five sleep fields (`sleep_duration`, `sleep_deep`, `sleep_light`, `sleep_rem`, `sleep_wake`) in `combined.csv`, then update `field_sources.json`'s attribution for those same fields to match. Deliberately touched *every* date the export covers (not just the 173 flagged as shifted) rather than trying to reason about which specific dates were currently wrong — safer given 101 of the 173 formed cascades, where trying to patch pairs individually risked missing a subtler multi-date chain. 272 real dates covered, 110 with an actual correction, 162 re-confirmed already correct, row count unchanged before/after.

**A separate, pre-existing limitation surfaced along the way, not caused by or fixed by this backfill:** 73 of the 272 dates have two genuine, independent full sleep sessions on the same calendar day (not naps — two complete sessions, e.g. one starting 00:06 and ending ~06:00, a separate one starting 23:11 that same evening). `combined.csv` has one row per date; the existing (pre-bug) pipeline behaviour already silently keeps only the later-starting session and drops the earlier one — confirmed by checking `combined.csv`'s current values against known non-shifted multi-session dates before the backfill touched anything, and deliberately preserved as-is rather than changed.

**Not yet covered:** anything before the export's own range (19 Aug 2025) — an older export would be needed to extend the backfill further back.

---

## Health Connect data pipeline (Android)

Health Connect has no web or shell-accessible API at all — it's a compiled native Android SDK (`androidx.health.connect:connect-client`, confirmed current as `1.2.0-alpha05`) accessed only via a real app linking the client library. This means, unlike every other device in this pipeline, there's a genuine native Android companion app involved (`maxedhealth-healthbridge`, separate repo) rather than just an extractor parsing an export file.

**Data flow:** Health Connect (on-device) → bridge app reads via `HealthConnectClient`, WorkManager syncs hourly once permission is granted once → writes `health_connect_export_{timestamp}.json` to the public Downloads folder via `MediaStore` (not raw file I/O — required on Android 10+ scoped storage, needs no broad storage permission) → lands exactly where Termux's `~/storage/downloads` symlink already looks → `move_exports_to_inbox()` in `server.py` recognises the filename pattern → `extractors/health_connect.py` parses it into the same row shape every other extractor produces.

**Export JSON shape** (bridge app's own format, not a Health Connect native shape):
```json
{
  "source": "health_connect",
  "exported_at": "2026-08-18T09:00:00Z",
  "days": [
    {"date": "2026-08-17", "steps": 8342, "sleep_duration_minutes": 412,
     "hrv_ms": 38.2, "weight_kg": 92.1}
  ]
}
```
Any field can be absent per day — the bridge app doesn't guess or fill gaps, same as every other extractor.

**Precedence:** deliberately last in every field's precedence list (`weight`, `hrv`, `sleep`, `steps`) in `update_health.py`'s `DEFAULT_PRECEDENCE` — it's an aggregate of whatever the phone's own sensor or another app already wrote into Health Connect, so a device's own direct, more detailed export should win when both exist for the same day.

**Steps specifically use `aggregate()`, not `readRecords()`** in the bridge app, to avoid double-counting when both the phone and a connected watch report steps into Health Connect for the same period. Confirmed (Android 14+): the phone's own step sensor writes into Health Connect automatically with zero extra app involvement once any app has requested `READ_STEPS` permission, so phone-only users get activity tracking without needing a separate wearable at all. Sleep/HRV/SpO2 remain a genuine hardware limitation — no phone-only path exists for these.

**Status:** server-side (extractor, `server.py` branch, `update_health.py` registration) fully built and tested. Bridge app written in Kotlin, not yet built/run in Android Studio — first build pending, same status the (now-discontinued) Wear OS project reached before being parked.

---

## Condition/Protocol system

`localStorage('mh_condition')` stores the user's selected condition:

| Key | Condition | Carb target | Report framing |
|-----|-----------|-------------|----------------|
| `gbm` | GBM — therapeutic ketogenic | 50g standard | [Proven]/[Early Stage]/[Speculative] evidence-categorised, gaining phase context |
| `epilepsy` | Epilepsy — therapeutic ketogenic | 50g standard | Seizure control focus, [Proven] evidence base |
| `strict_keto` | Strict Ketosis | 50g standard | Metabolic health, weight focus, [Proven] evidence base |
| `migraine` | Migraine — ketogenic trial | 50g standard | [Early Stage] evidence — real RCT data, explicitly framed as promising not established standard of care |
| `cluster_headache` | Cluster Headache — ketogenic trial | 50g standard | [Early Stage] evidence, genuinely earlier-stage than migraine's own evidence base |
| `t1_diabetes` | Type 1 Diabetes | Carb-aware, no auto ceiling | Insulin management, flag dosing implications |
| `t2_diabetes` | Type 2 Diabetes | 100g standard | Glucose stability, HbA1c framing |
| `general` | General Health / Weight Loss | 150g standard | Calorie deficit, balanced approach |
| `recomp` | Body Recomposition | No carb ceiling | Protein-focused, lean mass preservation/gain |

All 9 offered at onboarding as well as Settings — onboarding previously only offered 4 (`gbm`/`t2_diabetes`/`recomp`/`general`), found and fixed alongside a second, independently-hardcoded ceiling mapping in onboarding that only covered 2 conditions and had silently drifted out of sync with `getConditionCeilingDefaults()`, the shared function everywhere else uses.

`gbm`/`epilepsy`/`migraine`/`cluster_headache` share the elevated 1.8g/kg protein multiplier and the "≥65% fat therapeutic ratio" framing (both trace back to the same therapeutic-ketogenic clinical lineage). One related spot deliberately excludes `migraine`/`cluster_headache` despite sharing the fat-ratio trait: an Insights panel that also mixes in claims specifically about *GBM tumour-outcome research*, which doesn't transfer to a headache condition.

`buildPatientContext()` and `patientContextBlock()` in `maxhealth.html` build all AI report prompts from this value. The `CONDITION_META` table maps conditions to protocol labels, evidence notes and report framing — found missing `migraine`/`cluster_headache`/`recomp` entirely in one pass, meaning AI advice was silently generic for those three despite the UI looking condition-aware. Carb ceilings themselves are set separately in Settings → Carb Ceilings and are independent of this selection.

`buildPatientContext(history, conditionFilter)` accepts an optional second parameter — when set, filters to only days that were genuinely logged during that condition's real period(s) per Condition History (below), and judges them against that period's own carb ceiling rather than today's.

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

## Condition History

Same pattern as Weight Phase History above, for condition instead of goal — stored in `localStorage('mh_condition_history')` as newline-separated `YYYY-MM-DD condition` entries, sorted earliest first.

`getConditionHistory()` parses and returns sorted array. `getConditionForDate(isoDate)` mirrors `getPhaseForDate()` exactly — a date before the earliest logged entry is treated as belonging to that first entry (extends backward), same convention for consistency between the two.

`appendConditionHistory(newCond)` fires from both `saveCondition()` (Settings) and the onboarding commit step, only on a genuine change from the previous entry. Same-day corrections (change → change back, e.g. a mis-click) collapse into the last entry rather than creating a spurious extra period — checked by comparing the new entry's date against the log's last entry, replacing in place if they match rather than appending.

`buildConditionPeriodsBlock()` builds a plain-text date-ranged summary of every period (only when 2+ distinct conditions genuinely exist — silently empty otherwise) and gets appended to `askReportsAI()`'s prompt. Deliberately doesn't pre-aggregate per-period stats — the day-level CSV data already sent to the AI has dates on every row, so the AI does its own grouping/comparison once it knows which dates belong to which period. This is what makes free-text comparison questions ("compare my general and migraine periods") work without a dropdown filter.

`patientContextBlock()` returns an explicit "no data for this period" message when `ctx.n === 0` (a condition-filtered period with zero logged days) rather than a wall of misleading zero-stats — and the compliance percentage calculation is guarded against the `0/0 = NaN` this would otherwise produce.

---

## Activity Level, Walking Pace Bands & Auto-Switch

**Persistence**: `localStorage('mh_activity_level')` — one of `sedentary`/`light`/`moderate`/`active`. Previously set once during onboarding via a transient in-memory variable (`_obActivity`) and never persisted at all; `obSetActivity()` now writes it immediately, and it's editable afterward in Settings → Profile via `saveActivityLevel()`, following the exact same pattern as `saveCondition()`.

**Walking pace bands**: `ACTIVITY_WALKING_PACE_BANDS` (four tiers, each with `easyMax`/`moderateMax`/`longBumpMiles`) replaces the single fixed `PACE_BANDS.walking` band that previously applied to everyone regardless of fitness. `getWalkingPaceBands()` is the single source of truth — reads the current activity level and returns the matching tier, falling back to the original generic band if somehow unset. Anchored on real research: the AHA (≥2.5mph) and CDC (≥3.5mph) officially disagree on what counts as "brisk," explicitly because it depends on individual fitness — `active` tier is anchored on the CDC figure, `light` on the AHA figure, `sedentary`/`moderate` interpolate between them. This specific 4-tier breakdown is a reasonable engineering synthesis of the validated underlying principle, not a literally-published clinical table.

Five separate call sites were found using pace assumptions before this fix, two of them silently disagreeing with each other (`calcSuggestedEffort()`'s auto-suggest bands vs. a separate fixed-mph reverse calculation used for calorie/step estimation when only an effort label, not exact pace, is available). All five now read from `getWalkingPaceBands()`.

**Known limitation**: `MET.walking` values (2.8/3.5/4.5 for Easy/Moderate/Hard) are not yet pace-adjusted the same way — calibrated assuming something close to the old universal scale, so calorie estimates outside the "moderately active" tier may be slightly off until this gets addressed too.

**Auto-switch**: `checkActivityLevelAutoSwitch()`, modelled closely on `checkWeightPhaseAutoSwitch()` (same file, same `mh_autoswitch_days` shared setting, default 14) but deliberately more resistant to noise — rather than requiring every single day in the window to individually match (which one low-step rest day would break even during genuine sustained improvement), it computes the smoothed 30-day trailing average *as of* each of the last N days and requires all of those to agree on one tier. Reuses the exact thresholds already used for the TDEE step-count activity multiplier (`>12000` active, `>8000` moderate, `>5000` light, else sedentary) — independently confirmed via research to closely match the widely-cited Tudor-Locke & Bassett (2004) step-count classification — so there's one consistent definition of each tier across TDEE and Activity Level, not two that could drift apart.

Same once-per-day guard pattern as its weight sibling (`mh_last_auto_activity_check`), called from the same three places: `updateDashboard()`, the guaranteed-once-per-app-open `setTimeout`, and immediately on `mh_autoswitch_days` changing (since both mechanisms share that one setting).

A move to a more active tier gets a real celebration (`addBubble` + `showToast`, matching the ketosis-streak-milestone pattern); a move to a less active tier is a plain, factual `showToast` only — informed either way, celebrated only when it's genuinely something to celebrate. Toggleable independently via `mh_notif_activity_autoswitch` (default on), separate from the weight/goal notification toggle.

**Activity Level History**: `localStorage('mh_activity_level_history')`, identical structure and functions to Condition History (`getActivityLevelHistory()`, `appendActivityLevelHistory()`, same-day-collapse guard) — logs every genuine change, whether manual or auto-switched, so a later change can't retroactively distort how older logged days get interpreted.

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

Debug/troubleshooting sections (`set-bodycompdebug`, `set-rollover`, `set-logmutation`, `set-savedebug`, `set-healthcheck`, `set-changelog`) are explicitly excluded from the reorderable set — all six live inside a fixed "⚠ Advanced" warning box, and reordering any of them would eventually orphan that box from the sections it's meant to mark. **Found and fixed a real bug**: three of these six (`set-logmutation`, `set-savedebug`, `set-changelog`) were genuinely, correctly positioned inside the Advanced Tools wrapper in the source HTML, but were missing from this exclusion list — the reorder system was picking them up and physically relocating them elsewhere via `appendChild`, not hidden, just moved somewhere nobody would think to look for a debug tool. Worth re-checking this exact list any time a new section gets added inside that same warning box.

`imp-bulk` and `imp-restore` (Import tab) are excluded for an unrelated, second reason: their HTML is wholesale regenerated by `renderDataImportCards()` every time `checkServer()` runs, independently of and often after the reorder scan. Letting the reorder system move these would orphan the moved copy while a fresh one gets built in its place on the next server check — two live copies of each, both matching the `toggleSection` scan, silently growing the section count past its real total.

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

## Itemized ingredient editors (Today's Log + History)

Multi-item log entries (`entry.items.length > 1`) get a real per-ingredient editor — `renderLogEditItemsForm`/`renderLogEditItemsList`/`updateLogEditItem`/`removeLogEditItem`/`addLogEditItem`/`updateLogEditTotalLine`/`saveLogEditItems` for Today, an intentionally parallel implementation (`renderHistEditItemsForm` etc., keyed by `${dayIdx}-${entryIdx}` rather than an id) for History. Aggregate kcal/protein/fat/carbs are *derived* from `items[]` on save, never typed separately — there's structurally nowhere for the two to drift apart.

**`_base` baseline mechanism** — each item can carry a `_base` object (`{grams, kcal, protein, fat, carbs, fibre, polyols}`) captured once, used as the stable reference point for all amount-driven scaling. Editing Amount computes `factor = newGrams / _base.grams` and scales every macro from `_base`, never from whatever's currently on screen — so repeated Amount edits scale from the same original point rather than compounding. Direct macro-field edits are treated as one-off manual overrides and do *not* reset `_base`.

**`_baseConfirmed` flag — new-ingredient baseline capture.** A fresh row from "+ Add ingredient" starts with no `_base` at all. Before this existed, typing an Amount for a new ingredient did nothing (nothing to scale yet), and once macros were typed in one at a time, whichever fields were still 0 at the moment a baseline might first get captured would freeze there permanently. Fixed by keeping `_base` continuously re-synced to the item's current state on every macro edit, for as long as `_baseConfirmed` is unset — regardless of whether Amount or a macro field gets typed first. `_baseConfirmed` only locks once a *genuine* rescale happens: a typed Amount value that actually differs from what `_base.grams` currently holds (not merely re-confirming the same value that was only just captured, which would read as `newGrams === _base.grams` and look identical to a real edit without this distinction). Pre-existing items from `editLogEntry`'s initial parse are marked `_baseConfirmed: true` immediately if a real baseline was found there, locking out this new logic for them entirely — items where no reliable size was found stay unconfirmed, so they can still pick up a baseline later if manually fixed up.

**Bulk "scale entire entry to X%"** (`scaleAllLogEditItems`/`scaleAllHistEditItems`) — scales every item in the entry simultaneously from each item's own `_base`, same non-compounding rule as above. Items without a `_base` get one lazily backfilled from current values (macro-only, `grams: null`) the first time bulk-scale runs, so an all-zero freshly-added row is a harmless no-op rather than an error; the per-row "no reliable size" note checks `_base.grams != null` specifically, not just truthy `_base`, so this lazy backfill doesn't cause it to misreport.

**Pre-log preview** (`editPreviewItem`/`scaleEditPreviewAmount`) uses the identical `_base` pattern for single/multi-item AI-parsed previews before they're logged, captured from the AI's own stated amount string (or a fallback regex against the food name, e.g. "440ml can") — kept deliberately separate from the log/history editors' baseline capture, since this one parses a *stored* AI-generated string rather than live interactive typing, and a bare number in that context must not be assumed to mean grams (same ambiguity class as the library-meal "1 serving" bug below).

**Shared strict parser, `_extractGramsFromAmount(str)`** — requires an explicit `g|ml|kg|l` unit suffix; a bare number always returns 0. Deliberately kept strict everywhere it parses *stored* strings (a saved meal's `"1 serving"`, an AI-generated amount) — loosening it caused the critical library-meal bug below. Every *live, interactive* Amount field (Today's editor, History's editor, the pre-log preview editor) instead layers a local, field-scoped bare-number-means-grams fallback on top, since in those specific contexts a bare number typed by a person unambiguously means grams.

**Library-meal portion misparse (critical, fixed):** `showSaveMealDialog` stores a saved multi-item meal's portion as the string `"1 serving"`. Re-matching it later via text search did `parseFloat(libMatch.portion)`, extracting the leading `"1"` as **1 gram** — reproduced directly: typing "creamy" matched a saved "Creamy Chicken and Veg" meal, Amount showed "1", and the resulting macros (2536kcal / 281g protein) looked like an entire day crammed into one gram, correctly triggering the impossible-mass warning. Fixed at all five call sites to use `_extractGramsFromAmount` instead of a raw `parseFloat`.

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

## Open Food Facts — text search vs. barcode field parity

Two separate OFF integration points exist: barcode scan (`handleBarcodeCapture`, single-product `/api/v2/product/{barcode}` fetch) and text search (`searchFoodOFF`, `/cgi/search.pl` results list + `selectFoodResult`). Both hit the same underlying `nutriments` object, but only the barcode path was requesting/parsing `fiber_100g`/`polyols_100g` — text search's results renderer never captured either field into the result item's `data-*` attributes, so `selectFoodResult()` had nothing to read back out, regardless of whether OFF actually had the data. Found via a real incident: a product logged by name search showed no polyols despite the label listing 17g/100g. Fixed to match field-for-field, including switching the amount screen's per-100g summary from `textContent` to `innerHTML` so the same styled 🍬 polyols callout the barcode path already shows now renders here too.

Separately, and not a code bug: OFF is a community-maintained database and can simply have incomplete or slightly-off data for a given product regardless of which path retrieves it — the existing "⚠ Values from Open Food Facts — verify against label" warning is the intended safeguard for exactly that case, not something to route around.

---

## Photo/Label AI unification & dashboard condition-awareness

The manual Meal/Label photo-mode toggle was removed — the AI's general system prompt already fully self-classifies a photo as label vs. meal, making the toggle (and a pre-flight gram-check gate that only fired if it had been manually set) redundant. That gate was the root cause of a real reported bug: forgetting to tap "Label" silently bypassed the AI's own portion-confirmation flow. An AI-assumed-amount detector (`_messageImpliesUnconfirmedAmount`) now flags when the AI filled in a gram figure while its own message was still asking a clarifying question, covering both label-path and meal-path items.

Two dashboard cards were found showing stale or incorrectly-universal content:
- **Weight trend** — computed purely from `state.history`, which excludes today's live entry until midnight rollover, while the headline weight figure above it was already live. Fixed by folding today's entry into the 14-day window when it's newer than history's newest.
- **Carb Zones tooltip** — static HTML with "GBM Protocol" and a metformin/MCT assumption hardcoded for every viewer regardless of condition. Fixed via `updateCarbZonesCondition()`, mirroring the existing `updateGBMSectionVisibility()` pattern already used to hide GBM-specific report sections from non-GBM users — swaps wording rather than hiding the card outright, since the carb-zone numbers themselves are still useful reference regardless of condition.

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
- Health Connect bridge app (Kotlin) written but not yet built/run in Android Studio — first build pending, needs verifying against the real current SDK the same way the Wear OS build needed several rounds of fixing wrong assumptions
- `MET.walking` calorie values (2.8/3.5/4.5) are not yet pace-adjusted the same way the effort-label bands now are — calibrated assuming something close to the old universal pace scale, so calorie estimates outside the "moderately active" tier may be slightly off
- Heylo crackerbread camera/photo logging reported as "hit and miss" — not yet investigated

**Resolved this session, previously listed here:**
- ~~Cloudflare Worker cannot be updated from Android~~ — solved via direct Cloudflare REST API calls through `curl` (see Cloudflare Worker section above)
- ~~Monthly summary may truncate if Cloudflare Worker caps `max_tokens`~~ — this was the Worker's hardcoded `max_tokens: 500`, now forwards the client's actual request
- ~~Tab bleeding — occasional, cosmetic only~~ — was specifically the Reset button's text overflowing its container once a 6th hydration button was added; fixed with overflow/ellipsis safety on the button style

---

*Built with Claude by Anthropic*
