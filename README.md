# MaxedHealth

**Personal health intelligence — nutrition tracking, wearable data, AI meal logging.**

> Built by a GBM patient who needed it. Given freely to everyone who does.

[Read the full story →](https://pete-maxhealth.github.io/maxhealth/docs/story.html) &nbsp;·&nbsp; [Why free? →](https://pete-maxhealth.github.io/maxhealth/docs/story.html#sec-free)

---

## Open the app

MaxedHealth runs in your browser. No installation required. **No API key needed.**

**Open Chrome on your Android phone and go to:**

```
pete-maxhealth.github.io/maxhealth/maxhealth.html
```

Bookmark it, or tap Chrome's menu → **Add to Home Screen** to install it like an app. A setup wizard walks you through everything in about 2 minutes.

---

## What it does

- **AI meal logging** — log meals by text or photo. AI identifies macros instantly. No API key required
- **Personal food library** — locked macro values for your regular foods
- **Daily targets** — calories, protein, carbs, ketosis zone indicator
- **Trends** — weight, sleep, HRV, SpO2, steps, activity — all connected to nutrition
- **Wearable data** — import from Withings, RingConn, Garmin, Oura, Amazfit/Zepp, or any CSV export
- **Reports** — GBM monthly brief, correlation analysis, date-range queries
- **End of day logging** — one tap generates your daily nutrition row
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

Full pipeline documentation: [Pipeline Setup Guide](https://pete-maxhealth.github.io/maxhealth/docs/pipeline-setup.html)

---

## Repository structure

```
# Web app (served via GitHub Pages)
maxhealth.html          # The app — single file
sw.js                   # Service worker (PWA/offline)
manifest.json           # PWA manifest
docs/story.html         # Full story including why free
carer.html              # Read-only carer view
setup.sh                # One-command Termux setup
distribute.sh           # Post-pull file distribution + inbox automation
pipeline/
  auto.py               # Thin trigger → app/update_health.py
docs/
  story.html            # Why it exists
  pipeline-setup.html   # Wearable setup guide
  gbm_patient_guide.html
README.md
TECHNICAL.md

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

## Licence

MIT — do what you want with it.

---

*Built by Pete. Software architect, Oracle DBA, RPA developer — and GBM patient in remission.*

*YOUR DATA. YOUR HEALTH. YOUR RULES.*
