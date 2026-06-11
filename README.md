# MaxedHealth

**Personal health intelligence PWA** — AI-powered nutrition tracking, wearable data integration, and metabolic analytics. Built for a strict therapeutic ketogenic protocol post-GBM diagnosis.

**Live:** [pete-maxhealth.github.io/maxhealth/maxhealth.html](https://pete-maxhealth.github.io/maxhealth/maxhealth.html)
**Local:** `http://localhost:5757` (via Termux + server.py)
**Version:** v2.9.3 — Phase 8 complete

---

## What it does

- **AI meal logging** — type a meal, paste an ingredient list, snap a photo, or scan a barcode. Claude identifies foods and calculates macros automatically. Lists of 10+ items split into batches automatically.
- **Food library** — Meals and Ingredients in separate sections. A-Z quick nav, search, category filter, sort. Tap LOG to open inline portion scaler — type grams, macros update live. Meals show their full ingredient list.
- **Recipes** — templates with adjustable ingredient amounts. Each ingredient shows its base portion; change grams and macros update live. Per-serving calculation. Different from meals: recipes are for things you cook with variations, meals are fixed snapshots.
- **Dashboard** — calories, protein, carbs, fat tiles with progress bars. Macro ratio bar with ketogenic target marker. Remaining targets. Water tracker. Portion badges on entries logged at non-standard amounts.
- **Supplement tracker** — 19 supplements across morning/midday/evening/bedtime. Auto-resets at midnight.
- **History** — daily nutrition log with fat back-calculation for pre-tracking entries. Edit day totals inline.
- **Insights** — carb adherence, protein, sleep, HRV, weight trend. All using real targets.
- **Reports** — query builder (38 columns, 6 operators), ketogenic adherence, GBM monthly summary with fat back-calculation.
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

## Full backup

```bash
cd /storage/emulated/0/maxhealth
zip -r "/storage/emulated/0/Download/maxhealth_backup_$(date +%Y%m%d).zip" app/maxhealth/ data/tables/
```

---

## File structure

```
maxhealth/
├── maxhealth.html      # Complete PWA (single file, ~700KB)
├── why-free.html       # Why MaxedHealth is free
├── user-guide.html     # User guide
├── server.py           # Local HTTP server (Termux)
├── update_health.py    # Wearable data pipeline
├── setup.sh            # First-time install
├── TECHNICAL.md        # Full technical reference
├── CHANGELOG.md        # Version history
└── data/
    └── tables/
        ├── master.csv      # Daily nutrition log
        ├── combined.csv    # Wearable data
        ├── library.csv     # Food library backup
        └── supplements.csv # Supplement stack
```

---

## Nutrition targets (current)

| Metric | Target |
|--------|--------|
| Calories | 3,500 kcal |
| Protein | 165g |
| Carbs | ≤50g (standard) / ≤75g (holiday) |
| Fat | ~247g |

---

## Tech stack

- Single-file HTML/CSS/JS PWA (~700KB)
- Claude (Anthropic) via Cloudflare Worker proxy at `maxhealth-ai.bogginsuk.workers.dev`
- Open Food Facts API (barcode lookup)
- Python HTTP server (Termux on Android)
- GitHub Pages (hosting)

---

## Why it exists

Built by Pete following a GBM diagnosis in April 2023. Therapeutic ketogenic protocol requires precise macro tracking — this is the tool that makes that possible daily. See [why-free.html](why-free.html) for the full story.
