# MaxedHealth — Technical Documentation

**Architecture, proxy setup, pipeline structure, data schema, and adding new extractors.**

---

## Architecture Overview

MaxedHealth is a static single-page web application with no server-side component.

```
┌─────────────────────────────────────────┐
│  Browser (Chrome on Android)            │
│                                         │
│  maxhealth.html                         │
│  ├── Nutrition tracker (localStorage)   │
│  ├── Trends / Reports / Library         │
│  ├── Import tab (CSV file picker)       │
│  └── Assistant tab (AI meal logging)    │
│              │                          │
│              │ fetch (text only)        │
└──────────────┼──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Cloudflare Workers Proxy                │
│  maxhealth-ai.bogginsuk.workers.dev      │
│                                          │
│  Adds API key, forwards to Anthropic     │
│  Rate-limited, no user data stored       │
└──────────────┬───────────────────────────┘
               │
               ▼
        Anthropic API (Claude)
```

**Key design decisions:**

- No backend means no server to maintain, no accounts, no database
- GitHub Pages hosting is free, reliable, and requires no deployment pipeline beyond `git push`
- The Cloudflare proxy keeps the API key out of client-side code while keeping AI free for users
- All health data stays on the device — only meal descriptions (text/photo) leave the device for AI processing

---

## GitHub Pages Hosting

**Repo:** `github.com/pete-maxhealth/maxhealth`  
**Live URL:** `pete-maxhealth.github.io/maxhealth/maxhealth.html`

Deployment is a `git push` to `main`. GitHub Pages serves the repo root automatically.

Docs live at `docs/` and are accessible as:
- `pete-maxhealth.github.io/maxhealth/docs/story.html`
- `pete-maxhealth.github.io/maxhealth/docs/pipeline-setup.html`
- `pete-maxhealth.github.io/maxhealth/docs/gbm_patient_guide.html`

---

## Cloudflare Workers Proxy

**Worker URL:** `maxhealth-ai.bogginsuk.workers.dev`  
**Purpose:** Relay AI requests from the app to the Anthropic API without exposing the API key in client-side code.

The worker:
1. Receives POST requests from the app containing only the meal description (text) or image
2. Injects the `x-api-key` header from a Worker secret
3. Forwards to `https://api.anthropic.com/v1/messages`
4. Returns the response

No user health data is ever sent to the proxy — only the meal logging prompt and any food photo.

**Worker secret setup (one-time):**
```bash
wrangler secret put ANTHROPIC_API_KEY
```

**Rate limiting:** configured in the Cloudflare dashboard to prevent abuse.

---

## Local Data Pipeline

The pipeline is an optional Python-based system that runs on Android via Termux. It processes wearable device exports and produces `combined.csv` for import into the app.

### Directory structure (on-device)

```
/storage/emulated/0/MaxHealth/
├── app/
│   ├── maxhealth/              # Git repo (web app + docs)
│   │   ├── maxhealth.html
│   │   ├── distribute.sh       # Run after every git pull
│   │   ├── pipeline/
│   │   │   └── auto.py         # Thin trigger → app/update_health.py
│   │   └── docs/
│   ├── extractors/             # Pipeline extractors (outside repo)
│   │   ├── withings.py
│   │   ├── ringconn.py
│   │   └── amazfit.py
│   ├── update_health.py        # Pipeline entry point
│   ├── server.py
│   └── utils.py
├── data/
│   ├── inbox/                  # Drop wearable exports here
│   ├── tables/
│   │   ├── combined.csv        # Merged wearable data
│   │   └── nutrition.csv       # Exported from app
│   └── backup/                 # Auto-backups (7 max)
└── logs/
    └── pipeline.log            # Structured error log
```

### Running the pipeline

```bash
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

Default order (configurable in Import tab → Source Precedence):

| Metric  | Priority order                          |
|---------|-----------------------------------------|
| Weight  | Withings > manual > RingConn > Amazfit  |
| HRV     | RingConn > Withings > Garmin            |
| Sleep   | RingConn > Withings > Garmin > Amazfit  |
| Steps   | Garmin > Withings > RingConn > Amazfit  |
| SpO2    | RingConn > Withings                     |
| HR      | RingConn > Amazfit > Withings > Garmin  |

### File versioning and backup

Before every pipeline write, `combined.csv` and `nutrition.csv` are automatically copied to `data/backup/` with a timestamp suffix. A maximum of 7 backups are retained (oldest deleted automatically).

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
| notes       | string | Optional daily notes            |

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

## PWA (Progressive Web App)

`maxhealth.html` includes a Web App Manifest and Service Worker registration enabling:

- **Add to Home Screen** — installs as a standalone app icon on Android
- **Offline access** — cached assets work without connectivity
- **Background sync** — AI requests queued when offline, sent when connectivity returns (Phase 3)

The Service Worker caches the app shell on first load. Nutrition data is stored in localStorage (survives app closure, cleared only by explicit data export or browser data clear).

---

## Termux:Boot Auto-Start

`setup.sh` installs a boot script at `~/.termux/boot/start-maxedhealth.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth — runs on every device boot
# The app is hosted on GitHub Pages — no local server needed.
# This script auto-runs the pipeline if new inbox files are present.
cd /storage/emulated/0/MaxHealth/app
cd /storage/emulated/0/MaxHealth/app && python update_health.py 2>> /storage/emulated/0/MaxHealth/logs/pipeline.log
```

Termux:Boot runs this on every reboot. The app needs no local server — it runs entirely from GitHub Pages. The boot script processes any wearable exports left in the inbox overnight.

---

## Security Notes

- The Cloudflare proxy API key is stored as a Worker secret — never in the codebase
- No health data transits the proxy — only meal descriptions and food photos
- localStorage data is scoped to the origin and not accessible to other sites
- The pipeline runs entirely on-device with no network calls
- The GitHub repo contains no credentials, keys, or personal data
