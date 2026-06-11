# MaxedHealth

**Personal health intelligence PWA** — AI-powered nutrition tracking, wearable data integration, and metabolic analytics. Built for a strict therapeutic ketogenic protocol.

**Live:** [pete-maxhealth.github.io/maxhealth/maxhealth.html](https://pete-maxhealth.github.io/maxhealth/maxhealth.html)  
**Local:** `http://localhost:5757` (via Termux + server.py)  
**Version:** v2.7.8

---

## What it does

- **AI meal logging** — type a meal, paste an ingredient list, snap a photo, or scan a barcode. Claude identifies foods and calculates macros automatically.
- **Food library** — Meals and Ingredients in separate sections with A-Z nav, search, category filter and sort. Inline portion scaler on LOG. Meals show ingredient list.
- **Dashboard** — calories, protein, carbs, fat tiles with progress bars. Macro ratio bar with ketogenic target marker. Remaining targets. Water tracker.
- **Recipes** — templates with adjustable ingredient amounts. Live macro scaling per ingredient.
- **Supplement tracker** — 19 supplements across morning/midday/evening/bedtime periods. Auto-resets at midnight.
- **History** — daily nutrition log with fat back-calculation for pre-tracking entries.
- **Reports** — query builder, ketogenic adherence, GBM monthly summary.
- **Wearable integration** — Withings, RingConn, Amazfit via `update_health.py` pipeline.

---

## Quick start

```bash
# Clone
git clone https://github.com/pete-maxhealth/maxhealth.git
cd maxhealth

# Run setup (first time)
bash setup.sh

# Start server
mhstart

# Open in Chrome
# Navigate to http://localhost:5757
```

---

## Deploy after update

```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html
cd /storage/emulated/0/maxhealth/app/maxhealth
git add -A
git commit -m "vX.X.X — description"
git push
```

---

## File structure

```
maxhealth/
├── maxhealth.html      # Complete PWA (single file)
├── why-free.html       # Why MaxedHealth is free
├── server.py           # Local HTTP server (Termux)
├── update_health.py    # Wearable data pipeline
├── setup.sh            # First-time install script
├── TECHNICAL.md        # Full technical reference
├── CHANGELOG.md        # Version history
└── data/
    └── tables/
        ├── master.csv      # Daily nutrition log
        ├── combined.csv    # Wearable data
        ├── library.csv     # Food library
        └── supplements.csv # Supplement stack
```

---

## Nutrition targets (current)

| Metric | Target |
|--------|--------|
| Calories | 3,300 kcal |
| Protein | 165g |
| Carbs | ≤50g (standard) / ≤75g (holiday) |
| Fat | ~247g |

---

## Why it exists

Built by Pete following a GBM diagnosis in April 2023. See [why-free.html](why-free.html) for the full story.

---

## Tech stack

- Single-file HTML/CSS/JS PWA
- Claude (Anthropic) via Cloudflare Worker proxy
- Open Food Facts API (barcode lookup)
- Python HTTP server (Termux on Android)
- GitHub Pages (hosting)
