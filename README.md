# MaxHealth

**Personal health intelligence — nutrition tracking, wearable data, AI meal logging.**

> Built by a GBM patient who needed it. Given freely to everyone who does.

---

## What it is

MaxHealth is a personal health tracking system that runs entirely on your Android device. No account. No subscription. No cloud. Your data never leaves your phone.

It has two parts:

- **maxhealth.html** — A mobile-first web app for daily nutrition tracking. Log meals by text, description, or photo. The AI identifies macros instantly. Tracks calories, protein, carbs, ketosis status, and body weight against your personal targets.

- **Python pipeline** — Processes wearable exports (Withings, RingConn, Garmin, Oura, Apple Health, or any CSV export) into a unified daily health record. Runs locally via [Termux](https://termux.dev) on Android.

Together they answer the question: **what is my eating actually doing to my body?**

---

## Who it's for

MaxHealth was originally built for therapeutic ketosis management in **Glioblastoma (GBM)** — keeping carbohydrates below 50g/day is a meaningful protocol alongside standard treatment. It has since been designed to be useful for anyone managing their health through diet and data:

- **GBM patients** — ketosis zone monitoring, carb ceiling enforcement, therapeutic protocol tracking
- **Type 2 Diabetes** — precise carbohydrate tracking, blood sugar-relevant macro targets
- **Body recomposition** — weight, lean mass, activity, and nutrition all connected
- **General health tracking** — for anyone who wants their data to work for them

[Read the full story →](https://YOUR_USERNAME.github.io/maxhealth/docs/story.html)

---

## Features

### Nutrition Tracker (maxhealth.html)
- AI meal logging via text or photo (Claude or OpenAI — uses your own API key)
- Personal food library with locked macro values
- Day mode selector — Standard / Occasion / Holiday carb ceilings
- Real-time remaining targets — calories, protein, carbs
- Ketosis zone indicator
- End-of-day CSV row generator — one tap to copy to your nutrition log
- History tab with expandable daily entries
- Trends charts — calories, protein, carbs, weight, sleep, HRV, SpO2, steps
- Import historical nutrition data from pipe-delimited CSV
- Import combined wearable data from combined.csv
- Add new devices — AI-powered column mapping for any CSV export

### Data Pipeline (Python — no external dependencies)
- Processes Withings and RingConn exports out of the box
- Universal extractor (`auto.py`) for any device via saved mapping configs
- Outputs a unified `combined.csv` joined on date
- Gap detection and duplicate priority enforcement
- Runs on Android via Termux — no PC required

---

## Getting started

### The tracker (everyone)

1. Download `maxhealth.html` from the [latest release](https://github.com/YOUR_USERNAME/maxhealth/releases/latest)
2. Copy it to your Android device
3. Open it in Chrome
4. Follow the setup wizard — takes about 60 seconds

That's it. The app runs from a single file. Nothing to install.

**Optional:** Add an API key for AI meal logging (Claude or OpenAI) in Settings. Without one, the built-in food library and manual entry work fine.

### The pipeline (wearable data)

The pipeline requires [Termux](https://termux.dev) on Android and Python 3.

```bash
# First time setup
pkg install python
cd /storage/emulated/0/MaxHealth
python pipeline/setup.py

# Run the pipeline
python pipeline/update_health.py --device withings
python pipeline/update_health.py --device ringconn
python pipeline/update_health.py  # all devices

# Add a new device
# Go to Import > Add New Device in the app, upload a sample CSV,
# confirm the AI mapping, download the JSON config,
# save it to MaxHealth/mappings/
python pipeline/auto.py --config mappings/mydevice.json --input data/inbox/export.csv
```

---

## File structure

```
MaxHealth/
├── maxhealth.html          ← The app — open this in Chrome
├── pipeline/
│   ├── update_health.py    ← Main pipeline entry point
│   ├── auto.py             ← Universal device extractor
│   ├── merge.py            ← Builds combined.csv
│   ├── utils.py            ← Shared utilities
│   ├── setup.py            ← First-run setup wizard
│   └── extractors/
│       ├── withings.py
│       ├── ringconn.py
│       └── amazfit.py      ← Stub — needs sample export
├── mappings/               ← Device mapping configs (JSON)
│   └── README.md
├── data/
│   ├── inbox/              ← Drop wearable export zips here
│   └── tables/             ← Generated data tables (CSV)
└── docs/
    └── story.html          ← Why this was built
```

---

## Privacy

Everything runs locally on your device.

- No data is ever sent to MaxHealth or any third party
- AI meal logging uses your own API key — requests go directly to Anthropic or OpenAI
- No analytics, no tracking, no advertising
- localStorage only — your history never leaves your browser

---

## Technical notes

- Single HTML file — no build tools, no npm, no framework
- Vanilla JavaScript, Chart.js for charts (loaded from cdnjs)
- Python stdlib only — no pip dependencies
- Tested on Android (Chrome) and desktop browsers
- localStorage key: `maxhealth_v1`

---

## Contributing

MaxHealth is free and open source. If you improve it, please share it back.

If you're a GBM patient, carer, clinician, or researcher and want to suggest features relevant to the therapeutic use case — please open an issue. This is the use case that matters most.

---

## Licence

MIT — do what you want with it. Attribution appreciated but not required.

---

*Built by Pete. retired Software architect, Oracle DBA, RPA developer — and GBM patient in remission.*

*YOUR DATA. YOUR HEALTH. YOUR RULES.*
