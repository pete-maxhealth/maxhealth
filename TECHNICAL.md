# MaxedHealth — Technical Documentation

**Architecture, proxy setup, pipeline structure, data schema, and adding new extractors.**

*Last updated: June 2026 — v2.0 (Phase 7)*

---

## Architecture Overview

MaxedHealth is a static single-page web application backed by an optional local Python server for wearable data sync.

```
┌──────────────────────────────────────────────────┐
│  Browser (Chrome / Safari)                       │
│                                                  │
│  maxhealth.html                                  │
│  ├── Today tab (dashboard, macros, water, log)   │
│  ├── Log tab (AI chat, library, recipes)         │
│  │   ├── Chat sub-tab  (AI meal logging)         │
│  │   ├── Library sub-tab (saved foods)           │
│  │   └── Recipes sub-tab (recipe builder)        │
│  ├── Insights tab (history, trends, reports)     │
│  │   ├── History sub-tab                         │
│  │   ├── Trends sub-tab                          │
│  │   └── Reports sub-tab (query builder)         │
│  └── Settings tab                                │
│      ├── Profile, targets, notifications         │
│      ├── Supplements tracker (19 supplements)    │
│      ├── Devices & import                        │
│      └── Appearance & accessibility              │
│              │                                   │
│              │ fetch (text / image)              │
└──────────────┼───────────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────────┐  ┌─────────────────────────┐
│  Anthropic   │  │  Cloudflare Workers      │
│  API (direct)│  │  Proxy (no-key users)    │
│              │  │  bogginsuk.workers.dev   │
│  User's own  │  │  Adds API key, forwards  │
│  API key     │  │  to Anthropic            │
└──────────────┘  └─────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Local Python server         │
│  server.py (localhost:5757)  │
│  Termux on Android           │
│                              │
│  Serves & persists:          │
│  ├── library.csv             │
│  ├── supplements.csv         │
│  ├── master.csv              │
│  └── combined.csv            │
└──────────────────────────────┘
```

**Key design decisions:**

- No backend means no server to maintain, no accounts, no database
- GitHub Pages hosting is free, reliable, and requires no deployment pipeline beyond `git push`
- The Cloudflare proxy keeps the API key out of client-side code while keeping AI free for users with no personal key
- Users with their own Claude or OpenAI key bypass the proxy entirely — direct API calls only
- All health data stays on the device — only meal descriptions (text/photo) leave the device for AI processing
- The local server (`server.py`) is optional — the app works fully from GitHub Pages without it, but loses wearable sync and CSV persistence for library/supplements

---

## GitHub Pages Hosting

**Repo:** `github.com/pete-maxhealth/maxhealth`  
**Live URL:** `pete-maxhealth.github.io/maxhealth/maxhealth.html`  
**Install page:** `pete-maxhealth.github.io/maxhealth/` (index.html with MacroDroid guide)

Deployment is a `git push` to `main`. GitHub Pages serves the repo root automatically.

Docs live at `docs/` and are accessible as:
- `pete-maxhealth.github.io/maxhealth/docs/user-guide.html`
- `pete-maxhealth.github.io/maxhealth/docs/gbm_patient_guide.html`
- `pete-maxhealth.github.io/maxhealth/docs/story.html`
- `pete-maxhealth.github.io/maxhealth/carer.html` (read-only carer portal)

---

## Cloudflare Workers Proxy

**Worker URL:** `maxhealth-ai.bogginsuk.workers.dev`  
**Purpose:** Relay AI requests from the app to the Anthropic API without exposing the API key in client-side code. Used only when the user has no personal API key configured.

The worker:
1. Receives POST requests containing a `messages` array (no `system` field)
2. Injects the `x-api-key` header from a Worker secret
3. Forwards to `https://api.anthropic.com/v1/messages`
4. Returns the response

**Important:** The proxy does not support a top-level `system` field. The app inlines the system prompt as the first entry in the `messages` array when using the proxy path. The direct API path (user's own key) sends `system` as a separate field as normal.

Meals with 6+ items are split into two parallel AI requests to avoid token truncation on the proxy path.

No user health data is ever sent to the proxy — only the meal logging prompt and any food photo.

**Worker secret setup (one-time):**
```bash
wrangler secret put ANTHROPIC_API_KEY
```

**Rate limiting:** configured in the Cloudflare dashboard to prevent abuse.

---

## Local Server (server.py)

`server.py` runs on Android via Termux and serves `localhost:5757`. It handles:

- Static file serving (fallback to GitHub Pages URL when offline)
- CSV read/write endpoints for `library.csv`, `supplements.csv`, `master.csv`, `combined.csv`
- WebSocket probe endpoint (`ws://localhost:5757/ws-probe`) — used by the app to detect whether the local server is running and switch between local and GitHub Pages modes automatically

**Auto-start:** Termux:Boot runs the boot script at `~/.termux/boot/start-maxedhealth.sh` on every device reboot.

**mhstart:** A script at `~/bin/mhstart` (on `$PATH`) restarts the server from any Termux session. Created automatically by `setup.sh`.

**Deploy command:**
```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html
```

**Standard push** (always copies server.py and update_health.py into repo before committing):
```bash
cd /storage/emulated/0/maxhealth/app/maxhealth && git add -A && git commit -m "vX.X" && git push
```

---

## Carer & Clinician Portal

`carer.html` is a standalone read-only HTML file in the repo root.

When a user taps **Generate Carer View Link** in Settings, the app encodes a snapshot of the last 30 days of nutrition history as base64 JSON in the URL hash:

```
pete-maxhealth.github.io/maxhealth/carer.html#<base64-payload>
```

**Payload structure:**
```json
{
  "name": "Pete",
  "generated": "2026-05-19T07:50:54.870Z",
  "expires": "2026-05-26T07:50:54.874Z",
  "targets": {
    "standard": { "kcal": 3500, "protein": 164, "carbs": 50 },
    "occasion": { "kcal": 3500, "protein": 164, "carbs": 75 },
    "holiday":  { "kcal": 3500, "protein": 164, "carbs": 100 }
  },
  "history": [
    { "date": "DD/MM/YY", "totals": { "kcal": 0, "protein": 0, "carbs": 0 }, "weight": null, "mode": "standard" }
  ]
}
```

The link is valid for 7 days. No data is stored server-side — everything is in the URL hash.

---

## Local Data Pipeline

The pipeline is an optional Python-based system that runs on Android via Termux. It processes wearable device exports and produces `combined.csv` for import into the app.

### Directory structure (on-device)

```
/storage/emulated/0/maxhealth/
├── app/
│   ├── maxhealth/              # Git repo (web app + docs)
│   │   ├── maxhealth.html
│   │   ├── carer.html
│   │   ├── index.html          # Install page with MacroDroid guide
│   │   ├── manifest.json       # PWA manifest
│   │   ├── icons/              # PWA icons (96, 192, 512px)
│   │   ├── CHANGELOG.md
│   │   ├── TECHNICAL.md
│   │   ├── README.md
│   │   └── docs/
│   │       ├── user-guide.html
│   │       ├── gbm_patient_guide.html
│   │       └── story.html
│   ├── extractors/
│   │   ├── withings.py
│   │   ├── ringconn.py
│   │   └── amazfit.py
│   ├── update_health.py        # Pipeline entry point
│   ├── server.py               # Local HTTP + WebSocket server
│   ├── merge.py                # Builds combined.csv
│   └── utils.py                # Logging, CSV helpers, backup
├── data/
│   ├── inbox/                  # Drop wearable exports here
│   ├── tables/
│   │   ├── combined.csv        # Merged wearable data (39 fields)
│   │   ├── nutrition.csv       # Exported from app
│   │   ├── master.csv          # Full merged health + nutrition master
│   │   ├── library.csv         # Saved food library (persisted by server.py)
│   │   └── supplements.csv     # Supplement log (persisted by server.py)
│   └── backup/                 # Auto-backups (7 max per file)
└── logs/
    └── pipeline.log            # Structured error log
```

### Running the pipeline

```bash
# Quick alias (configured by setup.sh)
mhstart

# Process all devices with files in inbox/
cd /storage/emulated/0/maxhealth/app && python update_health.py

# Specific device only
cd /storage/emulated/0/maxhealth/app && python update_health.py --device withings
cd /storage/emulated/0/maxhealth/app && python update_health.py --device ringconn
cd /storage/emulated/0/maxhealth/app && python update_health.py --device amazfit --password YOUR_ZEPP_PASSWORD

# Preview without writing
cd /storage/emulated/0/maxhealth/app && python update_health.py --dry-run
```

### Source precedence

| Metric  | Priority order                          |
|---------|-----------------------------------------|
| Weight  | Withings > manual > RingConn > Amazfit  |
| HRV     | RingConn > Withings > Garmin            |
| Sleep   | RingConn > Withings > Garmin > Amazfit  |
| Steps   | Garmin > Withings > RingConn > Amazfit  |
| SpO2    | RingConn > Withings                     |
| HR      | RingConn > Amazfit > Withings > Garmin  |

### File versioning and backup

Before every pipeline write, `combined.csv` and `nutrition.csv` are automatically copied to `data/backup/` with a timestamp suffix. A maximum of 7 backups are retained per file (oldest deleted automatically).

To restore a backup: open the app → Import tab → Restore Backup.

### Error logging

```
2026-05-11 14:30:22 | amazfit   | extract  | ok      | 2 days processed
2026-05-11 14:30:22 | withings  | extract  | error   | No files found in inbox/
2026-05-11 14:30:22 | pipeline  | write    | ok      | combined.csv written (847 rows)
```

Format: `timestamp | device | operation | status | message`

The last 50 lines are viewable in the app at Import tab → View Pipeline Log.

---

## Data Schema

### combined.csv

One row per date. All wearable data merged by date according to source precedence. 39 fields total.

| Column           | Type    | Description                                      |
|------------------|---------|--------------------------------------------------|
| date             | string  | YYYY-MM-DD                                       |
| steps            | int     | Total daily steps                                |
| distance_m       | int     | Distance in metres                               |
| calories_active  | int     | Active calories burned                           |
| sleep_duration   | int     | Total sleep in minutes (excl. wake periods)      |
| sleep_deep       | int     | Deep sleep in minutes                            |
| sleep_light      | int     | Light/shallow sleep in minutes                   |
| sleep_rem        | int     | REM sleep in minutes                             |
| sleep_wake       | int     | Wake time during sleep window in minutes         |
| hr_avg           | int     | Average heart rate for the day                   |
| hr_min           | int     | Minimum heart rate                               |
| hr_max           | int     | Maximum heart rate                               |
| hrv              | float   | Heart rate variability (ms)                      |
| spo2             | float   | Blood oxygen saturation (%)                      |
| weight           | float   | Weight in kg                                     |
| bmi              | float   | BMI                                              |
| fat_pct          | float   | Body fat percentage                              |
| muscle_pct       | float   | Muscle mass percentage                           |
| source           | string  | Pipe-joined source tags e.g. `withings+ringconn` |

Empty string = no data for that field on that date.

### nutrition.csv

Exported from the app. One row per day.

| Column      | Type   | Description                     |
|-------------|--------|---------------------------------|
| date        | string | YYYY-MM-DD                      |
| calories    | float  | Total kcal                      |
| protein     | float  | Protein in grams                |
| carbs       | float  | Net carbohydrates in grams      |
| fat         | float  | Fat in grams                    |
| fibre       | float  | Fibre in grams                  |
| water_ml    | int    | Water intake in ml              |
| mode        | string | standard / occasion / holiday   |
| notes       | string | Optional daily notes            |

### master.csv

Full merged dataset combining wearable data and nutrition. Built by `merge.py` after each pipeline run. Used by the Reports query builder for cross-domain analysis (e.g. "days where sleep > 7h AND carbs < 50g").

### library.csv

Saved food library. Persisted by `server.py` at `/data/tables/library.csv`. Mirrors `localStorage['maxhealth_foods']` — synced on load and on every save. One row per food item.

| Column   | Type   | Description                              |
|----------|--------|------------------------------------------|
| name     | string | Food name                                |
| kcal     | float  | Calories per base portion                |
| protein  | float  | Protein per base portion (g)             |
| fat      | float  | Fat per base portion (g)                 |
| carbs    | float  | Carbs per base portion (g)               |
| portion  | string | Base portion label (e.g. "30g", "1 tbsp")|
| per100g  | bool   | True if values are per 100g              |
| locked   | bool   | True if locked (prevents accidental edit)|
| fibre    | float  | Fibre per base portion (g), optional     |

### supplements.csv

Supplement log. Persisted by `server.py` at `/data/tables/supplements.csv`. One row per supplement per day taken.

| Column     | Type   | Description                          |
|------------|--------|--------------------------------------|
| date       | string | YYYY-MM-DD                           |
| name       | string | Supplement name                      |
| dose       | string | Dose taken (e.g. "500mg", "2 caps")  |
| period     | string | Morning / Afternoon / Evening / Night|
| taken      | bool   | Whether taken that period            |

### localStorage keys (app state)

| Key                    | Description                                      |
|------------------------|--------------------------------------------------|
| `maxhealth_v1`         | Full app state (history, today's log, weight)    |
| `mh_target_kcal`       | Daily calorie target                             |
| `mh_target_protein`    | Daily protein target                             |
| `mh_target_carbs`      | Daily carb ceiling                               |
| `mh_target_fat`        | Daily fat target                                 |
| `mh_name`              | User's name                                      |
| `mh_provider`          | AI provider: claude / openai / local             |
| `mh_api_key`           | Encrypted API key (if set)                       |
| `mh_health_context`    | Free-text health context injected into AI        |
| `mh_condition`         | Selected condition (gbm / t2d / recomp / general)|
| `mh_water_target`      | Daily water target in ml                         |
| `mh_fibre_target`      | Daily fibre target in grams                      |
| `maxhealth_foods`      | Saved food library (also persisted to library.csv)|
| `mh_supplements`       | Supplement definitions and log                   |
| `mh_tips_seen`         | Dismissed contextual tips per tab                |
| `mh_visual_theme`      | Active visual theme                              |
| `mh_icon_pack`         | Active icon pack                                 |
| `mh_theme`             | Colour palette                                   |
| `mh_custom_accent`     | Custom accent hex colour override                |
| `mh_text_size`         | Text size preference (normal/large/larger)       |

---

## Supplements Tracker

The supplements tracker (Settings → Supplements) manages a configurable stack of up to 20+ supplements across four daily periods: Morning, Afternoon, Evening, Night.

Each supplement has:
- Name, dose, notes
- Active periods (which times of day it's taken)
- Per-period toggle (mark taken/not taken each period independently)

Resets at midnight. Persisted to `supplements.csv` via server.py when local server is running; falls back to localStorage only when on GitHub Pages.

---

## Adding a New Extractor

Extractors live in `extractors/`. Each is a self-contained Python module.

### Required interface

```python
# extractors/mydevice.py

def run(inbox_path, output_path, dry_run=False):
    """
    inbox_path: str — path to /data/inbox/
    output_path: str — path to /data/tables/ (for reference only)
    dry_run: bool — if True, return data without side effects

    Returns: list of dicts, one per date
    """
    rows = []
    rows.append({
        'date': '2026-05-11',
        'steps': 10234,
        'sleep_duration': 420,
        'source': 'mydevice',
    })
    return rows
```

### Registering the extractor

```python
EXTRACTORS = {
    'withings': extractors.withings,
    'ringconn': extractors.ringconn,
    'amazfit':  extractors.amazfit,
    'mydevice': extractors.mydevice,   # add here
}
```

### Amazfit / Zepp specifics

The Amazfit extractor handles AES-256 encrypted zip exports using `pyzipper`. Pass the password via:

```bash
cd /storage/emulated/0/maxhealth/app && python update_health.py --device amazfit --password YOUR_PASSWORD
# or
export ZEPP_PASSWORD=YOUR_PASSWORD && python update_health.py --device amazfit
```

The password is displayed in the Zepp app at export time and is often the numeric user ID at the start of the export filename.

---

## Visual Theme System

### Visual Style (`mh_visual_theme`)

Values: `none` (Classic), `vital`, `pulse`, `forge`. Applied via `data-visual-theme` on `<html>`.

| Theme   | Palette              | Radius   | Typography       | Card style        |
|---------|----------------------|----------|------------------|-------------------|
| Classic | Green accent, dark   | 12px     | DM Sans          | Border + surface  |
| Vital   | Blue (#38bdf8)       | 6px      | Space Mono heads | Left border accent|
| Pulse   | Green (#2deb8f)      | 18-20px  | DM Sans rounded  | Gradient fill     |
| Forge   | Amber (#f97316)      | 2-4px    | Syne bold        | Top border accent |

### Icon Pack (`mh_icon_pack`)

Values: `classic`, `outline`, `organic`, `bold`, `neon`, `mono`. Auto-selected by visual theme, overridable independently.

---

## PWA & Service Worker

`maxhealth.html` includes a Web App Manifest (`manifest.json`) and Service Worker registration enabling:

- **Add to Home Screen** — installs as a standalone app icon on Android and iOS
- **Offline access** — cached assets work without connectivity
- **iOS Safari support** — Apple touch icon, safe area insets, input zoom prevention

The Service Worker caches the app shell on first load. All nutrition data is stored in localStorage.

---

## Termux:Boot Auto-Start

`setup.sh` installs a boot script at `~/.termux/boot/start-maxedhealth.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth — runs on every device boot
cd /storage/emulated/0/maxhealth/app && python update_health.py 2>> /storage/emulated/0/maxhealth/logs/pipeline.log
```

`setup.sh` also installs `mhstart` as a script at `~/bin/mhstart` (on `$PATH`), so it works regardless of how Termux is launched — not as a `.bashrc` alias.

---

## Security Notes

- The Cloudflare proxy API key is stored as a Worker secret — never in the codebase
- No health data transits the proxy — only meal descriptions and food photos
- Users with their own API key communicate directly with Anthropic — the proxy is never involved
- localStorage data is scoped to the origin and not accessible to other sites
- The pipeline runs entirely on-device with no network calls
- The GitHub repo contains no credentials, keys, or personal data
- The carer view URL contains only nutrition totals and weight — no food log details, no personal notes
