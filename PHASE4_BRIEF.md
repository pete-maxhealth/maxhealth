# MaxHealth Phase 4 — Handoff Brief
## For Claude — Read This First

---

## Who Pete Is

Pete is a 56-year-old male, 188cm, currently ~90.5kg (target 92–93kg, gain phase).
MGMT-methylated GBM (glioblastoma), March 2023 diagnosis, currently in remission.
Strict therapeutic ketosis protocol: <50g carbs/day standard, <75g occasion, ~100g holiday.
Nutrition targets: 3,000 kcal | 145g protein | 50g carbs (standard day).
Oracle DBA and RPA developer. Strong architectural instincts. Precise about data.

**Tone:** Warm, direct, funny when casual. No medical disclaimers — acknowledged once, never repeat.

---

## What MaxHealth Is

A personal health intelligence system with two components:

**1. Data Pipeline** — Python scripts (stdlib only, no pip) on Android via Termux.
Processes wearable export zips into clean master tables → combined.csv.

**2. Nutrition Tracker** — Single mobile-first HTML file. GitHub Pages hosted.
AI meal logging via Cloudflare proxy (no user API key needed).
PWA. Full localStorage persistence.

---

## Live System

- **App URL:** https://pete-maxhealth.github.io/maxhealth/maxhealth.html
- **GitHub repo:** pete-maxhealth/maxhealth
- **Local repo:** /storage/emulated/0/MaxHealth/app/maxhealth
- **App file:** maxhealth.html (root of repo)
- **Cloudflare proxy:** https://maxhealth-ai.bogginsuk.workers.dev
- **Current version:** v1.8

### Push command (standard)
```bash
cd /storage/emulated/0/maxhealth/app/maxhealth
cp /storage/emulated/0/Download/maxhealth_v1.x.html maxhealth.html
git add .
git commit -m "description"
git push
```

---

## What Is Fully Built (v1.7)

Do not re-implement or alter any of these unless Pete explicitly asks.

| Feature | Status | Notes |
|---------|--------|-------|
| Dashboard tab | ✅ Complete | Weight card, phase banner, progress bars, ketosis badge, log, CSV row |
| Assistant tab | ✅ Complete | Renamed from Log Meal. Chat-style, photo support, quick actions |
| History tab | ✅ Complete | Week/month/all filter, expandable day entries |
| Trends tab | ✅ Complete | Today/30/60/All filters, daily view, day nav, chart drill-downs |
| Reports tab | ✅ Complete | Date range, summary cards, Insights, Seasonal Compare, Ask AI starters, Query Builder, AI Brief |
| Library tab | ✅ Complete | Save/edit/delete food items, duplicate prevention |
| Import tab | ✅ Complete | combined.csv import, universal device extractor, AI column mapper, pipeline commands |
| Settings tab | ✅ Complete | AI provider, health context, condition, profile, notifications, carer link, export |
| Condition onboarding | ✅ Complete | 4 condition cards in wizard (GBM/T2D/Recomp/General), CONDITION_CONFIG object |
| Health context AI injection | ✅ Complete | Free-text field → injected into every AI system prompt |
| Food library | ✅ Complete | localStorage key: maxhealth_foods |
| AI via Cloudflare proxy | ✅ Complete | No user API key needed. Falls back gracefully. |
| PWA + service worker | ✅ Complete | Network-first, auto-updates, push notifications |
| Push notifications | ✅ Complete | EOD reminder, carb ceiling warning, permission flow |
| Body comp drill-downs | ✅ Complete | Weight, HRV, SpO2, sleep, steps — full chart overlays |
| Contextual onboarding tips | ✅ Complete | Dismissable tab tips + welcome banner (mh_new_user_dismissed) |
| Data integrity check | ✅ Complete | On init — duplicate dates, missing dates, suspicious values |
| Demo mode | ✅ Complete | Full _demoMode system, 30-day sample data, read-only, enter/exit |
| Carer view link | ✅ Complete | Generates URL pointing to carer.html (see Known Gap below) |
| Nutrition CSV auto-export | ✅ Complete | exportNutritionForPipeline() — exports history as pipeline-ready CSV |
| Source precedence config | ✅ Complete | Per-metric device dropdowns in Import tab, KNOWN_DEVICES array |
| Amazfit/Zepp (app side) | ✅ Complete | UI, commands, device selector all present |
| Seasonal Compare | ✅ Complete | Period A vs Period B date pickers, AI comparison |
| Reports Query Builder | ✅ Complete | Metric + operator + value selector, runs against history |
| Theme system | ✅ Complete | Dark theme only — deliberate, do not lighten |
| Count-up animation | ✅ Complete | Dashboard macros animate on load |
| Day mode selector | ✅ Complete | Standard / Occasion / Holiday — dynamic carb ceiling |
| Phase logic | ✅ Complete | Auto-switches Gain ↔ Maintenance at 92kg sustained |

---

## Locked Nutrition Values — Do Not Change

| Item | Value |
|------|-------|
| TDEE | 3,420 kcal/day |
| Gain target | 3,000 kcal (current active target) |
| Protein target | 145g/day |
| Carb ceiling (standard) | 50g |
| Carb ceiling (occasion) | 75g |
| Carb ceiling (holiday) | 100g |
| Target weight | 92–93kg |
| Height | 188cm |
| Age | 56 |

**ASDA Roasted & Salted Mixed Nuts** (locked, never recalculate):
- Per 100g: 658kcal / 19g P / 11g C / 58g F

**Tesco Double Cream 150g** (daily shake, non-negotiable):
- 675kcal / 3g P / 4.5g C

---

## Key Technical Details

- **Single HTML file** — all CSS and JS inline. No build tools, no npm, no frameworks.
- **localStorage key:** `maxhealth_v1` — do not change
- **State schema:** `{ weight, dayMode, todayLog, history, notes, lastDate, onboarded }`
- **History entries:** `{ date(DD/MM/YY), log[], totals{}, mode, notes, weight, steps, sleep_min, hrv_rmssd, spo2_avg, ... }`
- **All tracker dates:** DD/MM/YY format
- **Wearable tables:** YYYY-MM-DD format (normalised by utils.py)
- **AI provider:** `mh_provider` localStorage ('claude' default)
- **Health context:** `mh_health_context` localStorage
- **Condition:** `mh_condition` localStorage
- **Food library:** `maxhealth_foods` localStorage
- **Chart library:** Chart.js from cdnjs only — no other external dependencies
- **AI model:** claude-sonnet-4-20250514
- **AI calls:** All must be JSON-only responses, 10-second timeout, failure message on error

### Pipeline structure
```
/storage/emulated/0/MaxHealth/app/
├── update_health.py      # Single entry point — CLI with --device and --dry-run
├── merge.py              # Builds combined.csv from all tables, left-join on date
├── utils.py              # Logging, CSV helpers, config, date normalisation
├── setup.py              # First-run wizard
├── server.py             # Local HTTP server
├── extractors/
│   ├── withings.py       # ✅ Complete
│   ├── ringconn.py       # ✅ Complete
│   └── amazfit.py        # 🔧 Stub — see Phase 4 tasks below
└── data/
    ├── inbox/            # Drop wearable export zips here
    ├── tables/           # Individual CSV tables per metric
    │   ├── combined.csv  # Master joined table — never edit directly
    │   └── ...
    └── backup/           # (Phase 4) Rolling backups — not yet implemented
```

### Device setup
- **Withings** — body comp scale. Primary for weight, fat%, muscle%, water%, bone%, visceral fat, BMR, hydration.
- **RingConn** — smart ring. Primary for HRV (RMSSD+SDNN), sleep staging, SpO2, heart rate, steps.
- **Zepp (Amazfit)** — smart watch. Primary for elevation, steps, activity. Fills gaps from others.

---

## Design Principles — Never Break These

- **Mobile-first always** — test on small screen mentally before suggesting anything
- **Precision over convenience** — locked values stay locked, zero drift
- **Ask before guessing** — if unclear, stop and ask Pete
- **Local first** — library → local DB → AI, always in that order
- **Evidence-based** — label anything speculative clearly
- **Zero extra dependencies** — stdlib Python, vanilla JS, Chart.js only
- **Dark theme is deliberate** — do not lighten it
- **One consistent method for maths** — never switch approach mid-calculation
- **If a value is unclear or missing** — STOP and ask, never estimate silently

---

## Phase 4 — What Needs Building

These are the genuine outstanding items: two bugs from v1.3, two pipeline items never implemented, and one missing file that renders an existing feature non-functional.

---

### BUG 1 — Drill-down overlay scroll broken on Android

**Where:** Metric drill-down overlay (opens when tapping chart cards in Trends/daily view).

**The HTML structure:**
```html
<div id="metricDrillOverlay"
     style="display:none;position:fixed;inset:0;z-index:400;background:var(--bg);overflow:hidden;">
  <div id="metricDrillScroll"
       style="height:100vh;overflow-y:scroll;-webkit-overflow-scrolling:touch;">
    ...content...
  </div>
</div>
```

**The symptom:** On Android Chrome, the overlay opens but the inner div won't scroll. The user can see the top of the content but can't reach the chart or stats below.

**What was tried:** `document.body.style.overflow = 'hidden'` was removed (commented out in both `openMetricDrill()` and `closeMetricDrill()`) because it was itself preventing scroll. That comment is still in the code: `// removed — prevents overlay scroll on Android`. The removal didn't fix it.

**Root cause:** On Android Chrome, a `position:fixed` outer container with `overflow:hidden` traps touch scroll events and prevents the inner scrollable div from receiving them. The fix is to change the outer div to `overflow:auto` or `overflow-y:auto` (not `hidden`), and ensure the inner scroll container is structured correctly. Alternatively, the outer overlay can be made the scroll container itself (removing the inner wrapper), with the sticky header handled via a separate fixed-position child inside it.

**Recommended fix:** Change outer `overflow:hidden` → `overflow-y:auto`. Make `metricDrillScroll` `min-height:100%` rather than `height:100vh`. Test that the sticky header (back button + period buttons) still sticks correctly after the change.

---

### BUG 2 — Daily view tappable rows not firing on Android

**Where:** Trends tab → Today view → daily summary rows (Activity & Vitals section). Each row is supposed to tap through to the metric drill-down chart.

**How they're built:** `renderDailyView()` uses `makeRow()` which creates divs and sets `div.onclick = () => openMetricDrill(drillMetric)` via JavaScript (not inline HTML). The cursor style is set to `pointer` via `div.style.cssText`.

**The symptom:** Rows show the arrow indicator and pointer cursor, but tapping them on Android does nothing. The `onclick` handler never fires.

**Root cause:** Android Chrome sometimes fails to fire `click` events on non-interactive elements (divs) that don't have an explicit `role` or are inside a scrollable container. The scroll container captures the touch gesture before it can resolve into a click. This is a well-known Android Chrome quirk.

**Recommended fix:** Either (a) add `cursor:pointer` and `touch-action:manipulation` to the row's style, plus ensure the tap target is at least 44px tall, or (b) replace `div.onclick = fn` with `div.addEventListener('touchend', fn)` for mobile compatibility, with a fallback `click` listener. Option (b) is more reliable. Also verify `openMetricDrill` is in scope from within `renderDailyView` — it's defined in the same file so scope shouldn't be the issue, but worth confirming no naming conflict exists.

---

### TASK 3 — Amazfit Python extractor (amazfit.py)

**Where:** `/storage/emulated/0/MaxHealth/app/extractors/amazfit.py`

**Status:** Stub only. The app-side UI is complete (Import tab has Amazfit commands, source precedence includes Zepp/Amazfit). The Python extractor that actually processes the Zepp export zip has never been implemented.

**What's needed:**
The extractor needs to follow the same pattern as `withings.py` and `ringconn.py`. It should:
- Accept a zip file path (Zepp/Amazfit export format)
- Extract the relevant CSVs from inside the zip
- Parse: steps, calories, elevation/altitude, activity minutes, heart rate where available
- Write to `data/tables/activity.csv` (or relevant table) in the standard schema
- Follow source precedence: Zepp is primary for elevation and activity; fills gaps for steps/HR from Withings and RingConn

**Before implementing:** Pete needs to provide a sample Zepp export zip so the actual file structure can be inspected. Do not guess the Zepp CSV structure — ask Pete to drop a sample in `/storage/emulated/0/MaxHealth/data/inbox/` and describe the file layout, or share the zip directly.

**Action required from Pete before this can proceed:** Provide a sample Amazfit/Zepp export zip or describe its contents.

---

### TASK 4 — Pipeline rolling backups (backup/ directory)

**Where:** `/storage/emulated/0/MaxHealth/app/` — likely in `utils.py` or as a wrapper around write operations.

**Status:** The `data/backup/` directory exists in the folder structure. The backup logic was never implemented.

**What's needed:**
Before any pipeline write to `data/tables/` (i.e. before any extractor writes its output CSV, and before `merge.py` writes `combined.csv`), a rolling backup of the affected file should be taken:
- Copy the existing file to `data/backup/<filename>_<YYYY-MM-DD_HHMMSS>.csv`
- Keep a maximum of 7 backups per file — delete the oldest when the cap is exceeded
- Implement as a utility function in `utils.py`: `def backup_file(path, backup_dir, keep=7)`
- Call it from `update_health.py` before each extractor runs, and from `merge.py` before writing combined.csv
- Failures to back up should log a warning but not abort the pipeline run (non-fatal)

---

### TASK 5 — carer.html (missing file)

**Where:** GitHub Pages repo root — needs to be a new file `carer.html` alongside `maxhealth.html`.

**Status:** The `generateCarerLink()` function in `maxhealth.html` is fully implemented and generates a correct URL pointing to `carer.html#<base64-encoded-snapshot>`. The snapshot contains: name, generated timestamp, expires timestamp, targets, and 30 days of history (date, totals, weight, mode only — no food log details, no personal notes). However, `carer.html` does not exist, so the link 404s.

**What's needed:**
A standalone read-only HTML page that:
- Reads the base64 payload from `window.location.hash`
- Decodes and parses the JSON snapshot
- Displays: patient name, generated/expires dates, nutrition targets, and a simple day-by-day history table (date, calories, protein, carbs, weight, day mode)
- Shows a clear "EXPIRED" banner if current date > expires date
- Matches MaxHealth's visual style (dark theme, same CSS variables, same fonts: Syne + DM Sans from Google Fonts)
- Is read-only — no inputs, no editing, no localStorage access
- Works as a single standalone HTML file — no server, no dependencies beyond Google Fonts

**Data passed in the hash (structure):**
```json
{
  "name": "string",
  "generated": "ISO8601",
  "expires": "ISO8601",
  "targets": { "kcal": 3000, "protein": 145, "carbs": 50 },
  "history": [
    { "date": "DD/MM/YY", "totals": { "kcal": 0, "protein": 0, "carbs": 0 }, "weight": 0, "mode": "standard" }
  ]
}
```

---

## Documentation Pass (TASK 6 — Lower Priority)

The following docs are out of date. Update after the above tasks are complete.

| File | What needs updating |
|------|---------------------|
| `README.md` | Remove any localhost references. Reflect GitHub Pages + Cloudflare proxy architecture. Mention Amazfit once extractor is done. |
| `story.html` | Add prominent "no API key needed" note for the Cloudflare proxy. |
| `pipeline-setup.html` | Add Amazfit/Zepp setup instructions once extractor is done. Add source precedence explanation. Add backup/restore instructions once Task 4 is done. |
| `TECHNICAL.md` | New file. Cover: architecture overview, data schema, how to add a new extractor, localStorage keys, AI integration. |

---

## Phase 4 — Completion Summary (May 2026)

All tasks complete.

| Task | Status | Notes |
|------|--------|-------|
| BUG 1 — Drill overlay scroll | ✅ Fixed | `overflow:hidden` → `overflow-y:auto` on outer div |
| BUG 2 — Daily view tappable rows | ✅ Fixed | Added `touchend` listener + `touch-action:manipulation` |
| TASK 3 — Amazfit extractor | ✅ Already complete | Was never a stub — confirmed working, 64 days extracted |
| TASK 4 — Pipeline rolling backups | ✅ Already complete | Confirmed in pipeline output |
| TASK 5 — carer.html | ✅ Built | Read-only clinician view, matches app theme, expiry support |
| TASK 6 — Docs | ✅ Done | pipeline-setup.html updated — one-tap sync as primary flow |
| BONUS — Assistant AI routing | ✅ Fixed | Was silently failing for all proxy users (no API key path) |
| BONUS — Local server + one-tap sync | ✅ Built | server.py on port 5757, Termux:Boot auto-starts, zero Termux for normal use |

---

MaxHealth Phase 4 Brief · Built with Claude (Anthropic) · May 2026
YOUR DATA. YOUR HEALTH. YOUR RULES.
