# MaxedHealth

**Personal health intelligence — nutrition tracking, wearable data, AI meal logging.**

> Built by a GBM patient who needed it. Given freely to everyone who does.

[Read the full story →](https://pete-maxhealth.github.io/maxhealth/docs/story.html) &nbsp;·&nbsp; [Why free? →](https://pete-maxhealth.github.io/maxhealth/docs/story.html#sec-free)

---

## Open the app

MaxedHealth runs in your browser. No installation required. **No API key needed.**

**Open Chrome (Android) or Safari (iPhone/iPad) and go to:**

```
pete-maxhealth.github.io/maxhealth/maxhealth.html
```

Bookmark it, or use your browser's **Add to Home Screen** option to install it like an app. A setup wizard walks you through everything in about 2 minutes.

---

## What it does

- **AI meal logging** — log meals by text or photo. AI identifies macros instantly. No API key required
- **Barcode scanner** — scan any product barcode for exact nutritional values
- **Recipe builder** — create multi-ingredient recipes, save to library, log as single entries
- **Personal food library** — locked macro values for your regular foods
- **Daily targets** — calories, protein, carbs, fat, fibre, water — ketosis zone indicator
- **Water tracking** — one-tap hydration logging with daily target and celebration on completion
- **Trends** — weight, sleep, HRV, SpO₂, steps, activity — all connected to nutrition
- **Wearable data** — import from Withings, RingConn, Garmin, Oura, Amazfit/Zepp, or any CSV export
- **Reports** — GBM monthly brief, correlation analysis, date-range queries, seasonal comparison
- **Carer & clinician view** — share a read-only 7-day snapshot with family or medical team
- **No account, no cloud, no subscription** — everything stays on your device

---

## Who it's for

- **GBM patients** — therapeutic ketosis tracking, carb ceiling enforcement, ketosis zone monitoring
- **Type 2 Diabetes** — precise carbohydrate tracking, trend analysis
- **Body recomposition** — nutrition connected to weight, lean mass, activity
- **General health** — for anyone who wants their data to work for them

---

## Architecture

MaxedHealth is a static web app hosted on GitHub Pages. There is no server, no backend, and no localhost dependency.

- **App:** `pete-maxhealth.github.io/maxhealth/maxhealth.html` — single HTML file, runs entirely in the browser
- **AI:** routed through a Cloudflare Workers proxy (`maxhealth-ai.bogginsuk.workers.dev`) — no API key required from users
- **Data:** stored locally on the device using localStorage and file import/export
- **Pipeline:** optional local Python pipeline (runs in Termux on Android) for wearable data processing

See [TECHNICAL.md](TECHNICAL.md) for full architecture documentation.

---

## Wearable data (optional)

To connect wearable devices, you need the local data pipeline. This runs on Android via Termux and is a one-time setup.

> Samsung Galaxy users: go to **Settings → Security and Privacy → Auto Blocker** and turn it off before installing.

**Step 1** — Install F-Droid from f-droid.org, then install Termux and Termux:Boot from F-Droid.

**Step 2** — Open Termux and run:
```bash
curl -sSL https://raw.githubusercontent.com/pete-maxhealth/maxhealth/main/setup.sh | bash
```

**Step 3** — Export data from your wearable, run the pipeline, then import combined.csv in the app's Import tab.

Supported devices: Withings, RingConn, Amazfit/Zepp. Any device that exports CSV can be added via Import → Add New Device.

Full guide: [User Guide → Pipeline section](https://pete-maxhealth.github.io/maxhealth/docs/user-guide.html#wearables)

---

## Repository structure

```
maxhealth.html          # The app — single file
carer.html              # Read-only carer & clinician portal
sw.js                   # Service worker (PWA/offline)
manifest.json           # PWA manifest
setup.sh                # One-command Termux setup
distribute.sh           # Post-pull file distribution
CHANGELOG.md            # Full version history
TECHNICAL.md            # Architecture and data schema
README.md               # This file
icons/                  # PWA and iOS icons
pipeline/
  auto.py               # Thin trigger → app/update_health.py
docs/
  user-guide.html       # Setup, daily workflow, pipeline guide
  gbm_patient_guide.html
  story.html

# Pipeline (on-device only, outside repo)
# /storage/emulated/0/MaxHealth/app/
#   update_health.py    # Pipeline entry point
#   extractors/         # Device extractors
#   server.py
```

---

## Privacy

Everything runs locally on your device. No data sent anywhere except AI meal logging requests (text/photo descriptions only — no personal health data). No analytics. No tracking.

---

## Feedback

Found a bug or have a suggestion? [Open an issue on GitHub →](https://github.com/pete-maxhealth/maxhealth/issues/new)

---

## Licence

MIT — do what you want with it.

---

*Built by Pete. Software architect, retired Oracle DBA and RPA developer — and GBM patient in remission.*

*YOUR DATA. YOUR HEALTH. YOUR RULES.*
