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

```javascript
// worker.js — passes model and max_tokens through from app
body: JSON.stringify({
  model: body.model || 'claude-sonnet-4-6',
  max_tokens: body.max_tokens || 1024,
  system: body.system,
  messages: body.messages
})
```

Update via Cloudflare dashboard → Workers & Pages → maxhealth-ai → Edit code.
Cannot be deployed from Android (Wrangler requires x86_64).

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

---

## Common operations

**Deploy after update:**
```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html
cd /storage/emulated/0/maxhealth/app/maxhealth
git add -A && git commit -m "vX.X.X — description" && git push
```

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

**Brand and meat-type disqualification:** if the query names a specific supermarket brand (Asda, Tesco, Sainsbury's, Lidl, etc.) or meat/protein type (chicken, beef, pork, etc.) that genuinely differs from a candidate's, that candidate is disqualified outright regardless of overall word-overlap score — these are treated as definitive mismatch signals, not just words to strip as noise. `canonicalBrand()`/`canonicalMeatType()` normalize spelling variants (Lidl/Lidl's, Sainsbury/Sainsburys/Sainsbury's) to the same identity before comparing, so two different spellings of the same brand never falsely register as a mismatch.

`findLibrarySubstitutes(name, excludeName, limit)` is the looser cousin used for the substitution flow — deliberately allows brand differences (that's the point: offering a real Lidl alternative when the query asks for Asda), returning up to 3 candidates from the same broad food category.

---

## Recipe-aware library suggestions

`suggestMealFromLibrary()` sends both the raw Food Library and saved Recipes (shown per-serving, not just totals) to the AI alongside today's actual remaining macros. The AI's role is limited to choosing which real items/recipes fit — it never computes final totals itself. `renderLibraryComboSuggestions()` resolves each suggestion against real library/recipe data and computes totals deterministically in JS (recipe servings math reuses the exact same formula as `logRecipe()` itself, so a suggested recipe logs identically to manually applying it).

---



- Tab bleeding — occasional, cosmetic only
- Cloudflare Worker cannot be updated from Android (use dashboard or laptop)
- Monthly summary may truncate if Cloudflare Worker caps `max_tokens` — check Worker script if this occurs
- Water target celebration not firing

---

*Built with Claude by Anthropic*
