# MaxedHealth

**Personal health intelligence PWA** — AI-powered nutrition tracking, wearable data integration, and metabolic analytics. Built for a strict therapeutic ketogenic protocol post-GBM diagnosis.

**Live:** [pete-maxhealth.github.io/maxhealth/maxhealth.html](https://pete-maxhealth.github.io/maxhealth/maxhealth.html)
**Local:** `http://localhost:5757` (via Termux + server.py)
**Version:** v3.6.1

---

## What it does

- **AI meal logging** — type, paste, photo, barcode or voice. 10+ item lists split automatically.
- **Food library** — Meals and Ingredients. Search box filters both by name as you type, with a live match count. Long-press for instant log. Recently scanned items for quick re-log.
- **Activity card** — permanent on dashboard. Walking, Resistance + custom exercises. For Walking and any custom activity flagged as distance-based, effort (Easy/Moderate/Hard) is auto-calculated from pace and total distance — always manually overridable. All macro targets adjust dynamically — calories, protein (+15g resistance), water (+500ml/hr).
- **Occasion tags** — Chemotherapy, Hospital day, Illness, Social event, Travel, Fasting. Multi-select, removable, retroactively editable. Writes to master.csv.
- **Dashboard** — calories, protein, carbs, fat tiles. Ketosis streak. Weight trend prediction. Dynamic targets from activity.
- **History** — daily log with fat back-calculation. Exercise minutes shown separately (🏃). Edit totals and tags retrospectively. Swipe left to delete.
- **Reports** — query builder (all 39 columns + notes/tags text search), Treatment Analysis, Weekly Summary export, GBM Monthly Summary, Oncology Team View.
- **Themes** — Dark, Light, Auto. Custom modals throughout.
- **Voice input** — microphone button, Web Speech API.
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

## Auto-start on boot (Termux:Boot)

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
├── maxhealth.html      # Complete PWA (~900KB)
├── worker.js           # Cloudflare Worker proxy
├── why-free.html       # Why MaxedHealth is free
├── user-guide.html     # User guide
├── server.py           # Local HTTP server (Termux)
├── update_health.py    # Wearable data pipeline
├── setup.sh            # First-time install
├── TECHNICAL.md        # Technical reference
├── CHANGELOG.md        # Version history
└── data/tables/
    ├── master.csv      # Daily nutrition + tags (pipe-delimited)
    ├── combined.csv    # Wearable data
    └── library.csv     # Food library backup
```

---

## master.csv format

```
date|kcal|protein|carbs|fat|notes
15/06/26|3506|188|18.4|265|Chemotherapy, 76min Walking, 45min Resistance
```

---

## Activity MET values

| Activity | Easy | Moderate | Hard |
|----------|------|----------|------|
| Walking | 2.8 | 3.5 | 4.5 |
| Resistance | 3.0 | 5.0 | 6.0 |
| Cycling | 4.0 | 6.8 | 10.0 |
| Custom exercise (generic) | 3.5 | 5.0 | 7.0 |

`kcal = MET × weight(kg) × duration(hours)`

Walking and any custom activity flagged distance-based also gets effort auto-calculated from pace + distance — see TECHNICAL.md for the full pace-band reference.

---

## Nutrition targets (current)

These are user-configured in Settings (`mh_target_kcal`, `mh_target_protein`, etc.) and read fresh via `getTargets()` — not hardcoded. The figures below reflect Pete's actual current settings, not the in-code fallback defaults (which exist only for first-time setup and currently sit at 3670kcal/170g, coincidentally close but not the same source of truth).

| Metric | Target |
|--------|--------|
| Calories | 3,670 kcal (+ activity) — raised from 3,500 after a weight plateau at the gaining-phase target; ~3,200 kcal at maintenance |
| Protein | 165g (+ 15g resistance days) |
| Carbs | ≤50g standard / ≤75g occasion |
| Fat | ~248g |
| Water | 2,000ml (+ 500ml/hr exercise) |

---

## Tech stack

- Single-file HTML/CSS/JS PWA (~900KB)
- Claude (Anthropic) via Cloudflare Worker proxy
- Open Food Facts API (barcode)
- Web Speech API (voice input)
- Python HTTP server (Termux/Android)
- GitHub Pages (hosting)

---

## Why it exists

Built by Pete following a GBM diagnosis. Therapeutic ketogenic protocol requires precise macro tracking — this makes that possible daily. See [why-free.html](why-free.html).

*Built with Claude by Anthropic.*
