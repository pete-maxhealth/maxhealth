# MaxedHealth

**Personal health intelligence PWA** — AI-powered nutrition tracking, wearable data integration, and metabolic analytics. Built for a strict therapeutic ketogenic protocol post-GBM diagnosis.

**Live:** [pete-maxhealth.github.io/maxhealth/maxhealth.html](https://pete-maxhealth.github.io/maxhealth/maxhealth.html)
**Local:** `http://localhost:5757` (via Termux + server.py)
**Version:** v3.10.23

---

## What it does

- **AI meal logging** — type, paste, photo, barcode or voice. 10+ item lists split automatically. Photo path uses Step 0 classification (label vs meal), ambiguity detection (asks before logging uncertain items), and sanity-checked portion estimation.
- **Food library** — Meals and Ingredients. Search box filters both by name as you type, with a live match count. Long-press for instant log. Recently scanned items for quick re-log. A-Z nav (ingredients only).
- **Meal preview** — per-component delete button (✕) to remove individual items before logging.
- **Condition/Protocol** — Settings dropdown (GBM, Epilepsy, Strict Ketosis, Type 1 Diabetes, Type 2 Diabetes, General Health). All AI reports adapt framing, evidence categorisation and thresholds to the user's condition.
- **Activity card** — permanent on dashboard. Walking, Resistance + custom exercises. For Walking and any custom activity flagged as distance-based, effort (Easy/Moderate/Hard) is auto-calculated from pace and total distance — always manually overridable. All macro targets adjust dynamically — calories, protein (+15g resistance), water (+500ml/hr).
- **Occasion tags** — Chemotherapy, Hospital day, Illness, Social event, Travel, Fasting. Multi-select, removable, retroactively editable. Writes to master.csv.
- **Dashboard** — calories, protein, carbs, fat tiles. Ketosis streak. Weight trend prediction. Dynamic targets from activity.
- **History** — daily log with fat back-calculation. Exercise minutes shown separately (🏃). Edit totals and tags retrospectively. Swipe left to delete.
- **Reports** — query builder (all 39 columns + notes/tags text search), Treatment Analysis, Weekly Summary export, GBM Monthly Summary, Oncology Team View. All reports are condition-aware and day-type aware (holiday/occasion days evaluated against their own ceilings, not penalised against standard targets).
- **Boot survival** — Termux:Boot + wake-lock + watchdog cron. Server auto-restarts after reboots and Android Doze, with zero user interaction required.
- **Local server shortcut** — home screen shortcut should point to `localhost:5757` directly (not GitHub Pages). setup.sh guides new installs through this. GitHub Pages URL serves as cloud fallback for users without local Termux setup.
- **Themes** — Dark, Light, Auto. Custom modals throughout.
- **Voice input** — microphone button, Web Speech API.
- **Wearable integration** — Withings, RingConn, Amazfit via `update_health.py`. AES-encrypted Zepp exports handled via `pyzipper`.

---

## Quick start

```bash
git clone https://github.com/pete-maxhealth/maxhealth.git
cd maxhealth
bash setup.sh
mhstart
# Open http://localhost:5757
```

## Auto-start on boot — self-healing watchdog (recommended)

This is the permanent fix for local server reliability. Once set up, Termux never needs to be opened manually again — the server starts on boot and auto-restarts itself if it ever crashes or gets killed by Android.

1. Install cron: `pkg install cronie -y`
2. Create `~/mh_watchdog.sh` that checks every minute, restarts the server if down, and kills duplicate instances if more than one is running.
3. Add to crontab: `echo "* * * * * ~/mh_watchdog.sh" | crontab -`
4. Add `~/.termux/boot/start-crond.sh` to launch `crond` on every boot.

After a reboot, give it a minute, then confirm both crond and the server are running on their own — no manual Termux interaction needed. From this point on, Termux can stay closed; the server is self-healing.

Note for cloud/GitHub Pages users: none of this is required — it only applies to local Termux setups. If you switch to local mode later, this is the section to follow.

## Local server access — pin the shortcut directly

As of Chrome's Local Network Access (LNA) enforcement (rolled out across Chrome ~142–149), public HTTPS pages — including the GitHub Pages version of MaxedHealth — can no longer auto-detect or redirect to a local server at `localhost:5757`. This is a browser security restriction, not a MaxedHealth bug, and it affects every site that tries this trick, not just this one.

**What this means for you:** instead of opening the GitHub Pages link and letting the page jump to local mode automatically, open `http://localhost:5757` directly (with the local server running) and add **that** to your home screen. `setup.sh` does this for you automatically on first install.

If you already have an older shortcut pointing at the GitHub Pages URL, delete it and re-add one pointing at `localhost:5757` instead — the page itself will tell you (via a one-time toast) when it detects a local server is running but auto-redirect isn't possible.

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
