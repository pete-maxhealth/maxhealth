# MaxedHealth — Technical Documentation

**Architecture, proxy setup, pipeline structure, data schema, and adding new extractors.**

*Last updated: May 2026 — v1.9 (Phase 5)*

---

## Architecture Overview

MaxedHealth is a static single-page web application with no server-side component.

```
┌─────────────────────────────────────────┐
│  Browser (Chrome / Safari)              │
│                                         │
│  maxhealth.html                         │
│  ├── Dashboard (weight, macros, water)  │
│  ├── Nutrition tab (AI meal logging)    │
│  ├── History / Trends / Reports         │
│  ├── Library (saved foods + recipes)    │
│  ├── Import tab (CSV + pipeline)        │
│  └── Settings                           │
│              │                          │
│              │ fetch (text / image)     │
└──────────────┼──────────────────────────┘
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
```

**Key design decisions:**

- No backend means no server to maintain, no accounts, no database
- GitHub Pages hosting is free, reliable, and requires no deployment pipeline beyond `git push`
- The Cloudflare proxy keeps the API key out of client-side code while keeping AI free for users with no personal key
- Users with their own Claude or OpenAI key bypass the proxy entirely — direct API calls only
- All health data stays on the device — only meal descriptions (text/photo) leave the device for AI processing

---

## GitHub Pages Hosting

**Repo:** `github.com/pete-maxhealth/maxhealth`  
**Live URL:** `pete-maxhealth.github.io/maxhealth/maxhealth.html`

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

No user health data is ever sent to the proxy — only the meal logging prompt and any food photo.

**Worker secret setup (one-time):**
```bash
wrangler secret put ANTHROPIC_API_KEY
```

**Rate limiting:** configured in the Cloudflare dashboard to prevent abuse.

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

The link is valid for 7 days. After expiry, carer.html shows an expired banner. No data is stored server-side — everything is in the URL hash. Zero-day entries are filtered from the display automatically.

---

## Local Data Pipeline

The pipeline is an optional Python-based system that runs on Android via Termux. It processes wearable device exports and produces `combined.csv` for import into the app.

### Directory structure (on-device)

```
/storage/emulated/0/MaxHealth/
├── app/
│   ├── maxhealth/              # Git repo (web app + docs)
│   │   ├── maxhealth.html
│   │   ├── carer.html
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
│   ├── server.py               # Local HTTP server (dev only)
│   ├── merge.py                # Builds combined.csv
│   └── utils.py                # Logging, CSV helpers, backup
├── data/
│   ├── inbox/                  # Drop wearable exports here
│   ├── tables/
│   │   ├── combined.csv        # Merged wearable data
│   │   └── nutrition.csv       # Exported from app
│   └── backup/                 # Auto-backups (7 max per file)
└── logs/
    └── pipeline.log            # Structured error log
```

### Running the pipeline

```bash
# Quick alias (configured by setup.sh)
mhstart

# Process all devices with files in inbox/
cd /storage/emulated/0/MaxHealth/app && python update_health.py

# Specific device only
cd /storage/emulated/0/MaxHealth/app && python update_health.py --device withings
cd /storage/emulated/0/MaxHealth/app && python update_health.py --device ringconn
cd /storage/emulated/0/MaxHealth/app && python update_health.py --device amazfit --password YOUR_ZEPP_PASSWORD

# Preview without writing
cd /storage/emulated/0/MaxHealth/app && python update_health.py --dry-run
```

### Source precedence

When multiple devices report the same metric for the same date, precedence determines which value is used. Secondary sources fill gaps where the primary has no value.

Default order (configurable in Import tab → Device Precedence):

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

The pipeline writes structured logs to `/storage/emulated/0/MaxHealth/logs/pipeline.log`:

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

One row per date. All wearable data merged by date according to source precedence.

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

### localStorage keys (app state)

| Key                    | Description                                      |
|------------------------|--------------------------------------------------|
| `maxhealth_v1`         | Full app state (history, today's log, weight)    |
| `mh_target_kcal`       | Daily calorie target                             |
| `mh_target_protein`    | Daily protein target                             |
| `mh_target_carbs`      | Daily carb ceiling                               |
| `mh_name`              | User's name                                      |
| `mh_provider`          | AI provider: claude / openai / local             |
| `mh_api_key`           | Encrypted API key (if set)                       |
| `mh_health_context`    | Free-text health context injected into AI        |
| `mh_condition`         | Selected condition (gbm / t2d / recomp / general)|
| `mh_water_target`      | Daily water target in ml                         |
| `mh_fibre_target`      | Daily fibre target in grams                      |
| `maxhealth_foods`      | Saved food library                               |
| `mh_tips_seen`         | Dismissed contextual tips per tab                |

---

## Adding a New Extractor

Extractors live in `extractors/`. Each is a self-contained Python module.

### Required interface

Every extractor must expose a `run(inbox_path, output_path, dry_run=False)` function that:

1. Finds its export file(s) in `inbox_path`
2. Extracts and transforms data into the `combined.csv` schema
3. Returns a list of dicts — one per date — with keys matching the schema columns above
4. Does **not** write to disk itself — the pipeline runner handles merging and writing

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
    # ... find and parse your export file ...
    rows.append({
        'date': '2026-05-11',
        'steps': 10234,
        'sleep_duration': 420,
        # ... other fields as available ...
        'source': 'mydevice',
    })
    return rows
```

### Registering the extractor

Add it to the device registry in `update_health.py`:

```python
EXTRACTORS = {
    'withings': extractors.withings,
    'ringconn': extractors.ringconn,
    'amazfit':  extractors.amazfit,
    'mydevice': extractors.mydevice,   # add here
}
```

### Amazfit / Zepp specifics

The Amazfit extractor (`extractors/amazfit.py`) handles the AES-256 encrypted zip that Zepp exports. Pass the password via:

```bash
cd /storage/emulated/0/MaxHealth/app && python update_health.py --device amazfit --password YOUR_PASSWORD
# or
export ZEPP_PASSWORD=YOUR_PASSWORD && cd /storage/emulated/0/MaxHealth/app && python update_health.py --device amazfit
```

The password is displayed in the Zepp app at the time of export. It is also often the numeric user ID at the start of the export filename.

---

## Visual Theme System

MaxHealth has two independent appearance layers, both stored in localStorage.

### Visual Style (`mh_visual_theme`)

Controls the full design language of the app. Values: `none` (Classic), `vital`, `pulse`, `forge`.

Applied via `data-visual-theme` attribute on `<html>`. All theme CSS uses attribute selectors (`[data-visual-theme="vital"] .card { ... }`) so existing styles are never overridden — only supplemented.

| Theme | Palette | Radius | Typography | Card style |
|-------|---------|--------|------------|------------|
| Classic | Green accent, dark bg | 12px | DM Sans | Border + surface |
| Vital | Blue (#38bdf8) | 6px | Space Mono headers | Left border accent |
| Pulse | Green (#2deb8f) | 18-20px | DM Sans rounded | Gradient fill |
| Forge | Amber (#f97316) | 2-4px | Syne bold | Top border accent |

When a visual theme is active, colour swatches only update `--accent` (not the full palette).

### Icon Pack (`mh_icon_pack`)

Controls SVG icons for tab bar and input buttons. Values: `classic`, `outline`, `organic`, `bold`, `neon`, `mono`.

Stored in `ICON_SETS` (tab icons) and `INPUT_ICONS` (button icons) JS objects. Applied via `applyTabIcons()` and `applyInputIcons()` on theme change and page load.

Selecting a visual theme auto-selects its matching icon pack, but the user can override independently.

| Pack | Style | Auto-selected by |
|------|-------|-----------------|
| Classic | Emoji + original SVGs | Classic theme |
| Outline | Thin-line SVG | Vital |
| Organic | Rounded filled SVG | Pulse |
| Bold | Solid chunky SVG | Forge |
| Neon | Outline + accent glow | Manual only |
| Mono | Greyscale solid | Manual only |

### localStorage keys

| Key | Description |
|-----|-------------|
| `mh_visual_theme` | Active visual theme (`none`/`vital`/`pulse`/`forge`) |
| `mh_icon_pack` | Active icon pack (`classic`/`outline`/`organic`/`bold`/`neon`/`mono`) |
| `mh_theme` | Colour palette (`midnight`/`aurora`/`carbon`/`slate`/`light`) |
| `mh_custom_accent` | Custom accent hex colour override |

---

## Chart Lightbox

A full-screen chart overlay (`#chartLightbox`) separate from the metric drill-down overlay (`#metricDrillOverlay`).

Triggered by tapping any chart card in the Trends → Full Charts view. Renders the selected metric's data on a large canvas with period selector (30D/90D/All). A "Deep Dive →" button closes the lightbox and opens the drill overlay for stats/insights.

Attempts `screen.orientation.lock('landscape')` on open where supported (Android Chrome). Falls back to a "rotate for wider view" hint.

---

`maxhealth.html` includes a Web App Manifest and Service Worker registration enabling:

- **Add to Home Screen** — installs as a standalone app icon on Android and iOS
- **Offline access** — cached assets work without connectivity
- **iOS Safari support** — Apple touch icon, safe area insets, input zoom prevention (Phase 5)

The Service Worker caches the app shell on first load. All nutrition data is stored in localStorage (survives app closure, cleared only by explicit export or browser data clear).

**iOS-specific meta tags (Phase 5):**
```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="MaxedHealth">
<link rel="apple-touch-icon" href="icons/icon-192.png">
```

All `<input>` and `<textarea>` elements use `font-size: 16px` minimum to prevent iOS Safari auto-zoom.

---

## Termux:Boot Auto-Start

`setup.sh` installs a boot script at `~/.termux/boot/start-maxedhealth.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth — runs on every device boot
cd /storage/emulated/0/MaxHealth/app && python update_health.py 2>> /storage/emulated/0/MaxHealth/logs/pipeline.log
```

Termux:Boot runs this on every reboot. The app itself runs entirely from GitHub Pages — no local server needed for normal use. The `mhstart` alias launches the local dev server when needed.

---

## Security Notes

- The Cloudflare proxy API key is stored as a Worker secret — never in the codebase
- No health data transits the proxy — only meal descriptions and food photos
- Users with their own API key communicate directly with Anthropic — the proxy is never involved
- localStorage data is scoped to the origin and not accessible to other sites
- The pipeline runs entirely on-device with no network calls
- The GitHub repo contains no credentials, keys, or personal data
- The carer view URL contains only nutrition totals and weight — no food log details, no personal notes
