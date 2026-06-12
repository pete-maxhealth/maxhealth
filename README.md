# MaxedHealth

**Personal health intelligence PWA** — AI-powered nutrition tracking, wearable data integration, and metabolic analytics. Built for a strict therapeutic ketogenic protocol post-GBM diagnosis.

**Live:** [pete-maxhealth.github.io/maxhealth/maxhealth.html](https://pete-maxhealth.github.io/maxhealth/maxhealth.html)
**Local:** `http://localhost:5757` (via Termux + server.py)
**Version:** v3.1.0

---

## What it does

- **AI meal logging** — type, paste a list, snap a photo, scan a barcode, or speak your meal. Lists of 10+ items split automatically. Claude identifies foods and calculates macros.
- **Food library** — Meals and Ingredients in separate sections. A-Z nav, search, filter, sort. Tap LOG for portion scaler. Long-press for instant log at default portion. Recently scanned items shown for quick re-log.
- **Recipes** — templates with adjustable ingredient amounts. Live macro scaling per ingredient. Different from meals: recipes for variable dishes, meals for fixed snapshots.
- **Dashboard** — calories, protein, carbs, fat tiles. Macro ratio bar. Ketosis streak counter. Weight trend prediction. Remaining targets. Water tracker.
- **Occasion tags** — tag days with context (Chemotherapy, Hospital day, Illness, Exercise, custom). Multi-select, removable, retroactively editable in history. Shows as 📌 banner on dashboard and in history.
- **Supplement tracker** — 19 supplements across morning/midday/evening/bedtime. Auto-resets at midnight.
- **History** — daily log with fat back-calculation. Edit day totals and occasion tags retrospectively. Swipe left to delete entries.
- **Insights** — carb adherence, protein, sleep, HRV, weight trend. All using real targets.
- **Reports** — query builder, ketogenic adherence, Treatment Analysis (chemo vs standard days), Weekly Summary export, GBM Monthly Summary, Oncology Team View (clinical PDF).
- **Themes** — Dark, Light, Auto in Settings → Customise → Appearance.
- **Voice input** — tap the microphone button and speak your meal.
- **Wearable integration** — Withings, RingConn, Amazfit via `update_health.py`.

---

## Quick start

```bash
git clone https://github.com/pete-maxhealth/maxhealth.git
cd maxhealth
bash setup.sh
mhstart
# Open http://localhost:5757
```

## Auto-start on boot

```bash
mkdir -p ~/.termux/boot
echo '#!/data/data/com.termux/files/usr/bin/bash
sleep 10
mhstart' > ~/.termux/boot/start-maxhealth.sh
chmod +x ~/.termux/boot/start-maxhealth.sh
```

## Deploy after update

```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html
cd /storage/emulated/0/maxhealth/app/maxhealth
git add -A && git commit -m "vX.X.X — description" && git push
```

## Full backup

```bash
pkg install zip -y
cd /storage/emulated/0/maxhealth
zip -r "/storage/emulated/0/Download/maxhealth_backup_$(date +%Y%m%d).zip" app/maxhealth/ data/tables/
```

---

## File structure

```
maxhealth/
├── maxhealth.html      # Complete PWA (~800KB)
├── why-free.html       # Why MaxedHealth is free
├── user-guide.html     # User guide
├── server.py           # Local HTTP server (Termux)
├── update_health.py    # Wearable data pipeline
├── setup.sh            # First-time install
├── TECHNICAL.md        # Technical reference
├── CHANGELOG.md        # Version history
└── data/tables/
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
| Carbs | ≤50g standard / ≤75g occasion |
| Fat | ~247g |

---

## Tech stack

- Single-file HTML/CSS/JS PWA (~800KB)
- Claude (Anthropic) via Cloudflare Worker proxy
- Open Food Facts API (barcode)
- Web Speech API (voice input)
- Python HTTP server (Termux/Android)
- GitHub Pages (hosting)

---

## Why it exists

Built by Pete following a GBM diagnosis in April 2023. Therapeutic ketogenic protocol requires precise macro tracking — this makes that possible daily. See [why-free.html](why-free.html).
