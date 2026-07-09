# MaxedHealth

**Personal health intelligence PWA** — AI-powered nutrition tracking, wearable data integration, and metabolic analytics. Built for a strict therapeutic ketogenic protocol post-GBM diagnosis.

**Live:** [pete-maxhealth.github.io/maxhealth/maxhealth.html](https://pete-maxhealth.github.io/maxhealth/maxhealth.html)
**Local:** `http://localhost:5757` (via Termux + server.py)
**Version:** v3.10.133

---

## What it does

- **Suggested Targets calculator** ⭐ — the app's most powerful feature. Enter height, age, sex, weight, condition and goal → it calculates personalised TDEE (Mifflin-St Jeor × activity from real step data), phase-adjusted calories, protein (1.8g/kg for GBM/Epilepsy, 1.6g/kg otherwise), and fat to fill remaining calories. Condition overlay checks ketogenic ratio for GBM/Epilepsy. One tap applies all targets. Works on day one with no history, and improves as wearable data accumulates.
- **Library-aware meal suggestions** — "📚 From my library" proposes real combinations of saved ingredients and Recipes (proper per-serving math) against today's actual remaining macros, never inventing values. One-tap logging straight from the suggestion.
- **Ingredient substitution** — if a described food doesn't exactly match your library (wrong brand, etc.), offers real alternatives from what you actually have instead of a silent fresh AI guess. Includes a "save as new item" path for when a flagged duplicate turns out to be a genuinely different product.
- **Recipes vs Meals** — Recipes support proper servings math for anything batch-cooked (log 1, 2, or half a portion correctly); Meals are simpler single-instance saves for anything eaten in one sitting. Each section explains which fits which use case.
- **Dashboard & tab reordering** — every section on Today, the Library tab's Recipes/Food Library split, and Reports/Manage/Import can be reordered via ▲▼ buttons, with preferences persisted.
- **Ketosis streak milestones** — one-time celebration at 7/14/30/50/100/200/365 consecutive days.
- **Nutrition logging sanity checks** — beyond the original meat-carbs and pure-fat plausibility checks: Atwater kcal-consistency, implausible low-carb-on-fruit, implausible portion size, and macro-mass-exceeds-food-weight. Flags rather than silently logging bad data; an explicit "are you sure?" gate for genuinely unusual (but real, e.g. batch-cooked) amounts rather than blocking them outright.
- **Weight Phase History** — log intentional weight phases (loss/maintain/gain) with dates. Automatically updated when you change goal. Used by all AI reports to correctly interpret weight trends — deliberate loss is never flagged as a concern.
- **⭐ Full Summary** — one-tap comprehensive 9-section health analysis: nutrition, weight phases, ketosis quality, sleep, HRV, activity, best periods, areas to improve, protocol verdict. Phase-aware, condition-specific, nil days excluded.
- **AI meal logging** — type, paste, photo, barcode or voice. Step 0 photo classification (label vs meal), ambiguity detection (asks before logging uncertain items), sanity-checked portion estimation, per-component delete and inline edit in preview.
- **Food library** — Meals, Recipes, and Ingredients. Search, A-Z nav (ingredients only), long-press to log, recently scanned items.
- **Condition/Protocol** — Settings dropdown (GBM, Epilepsy, Strict Ketosis, Type 1 Diabetes, Type 2 Diabetes, General Health). All AI reports adapt framing, evidence categorisation and thresholds.
- **Activity card** — Walking, Resistance + custom exercises. Distance-aware effort auto-calculation. All macro targets adjust dynamically. Strength Training log and Routine Templates for saved exercise groupings.
- **Occasion tags** — Chemotherapy, Hospital day, Illness, Social event, Travel, Fasting. Multi-select, retroactively editable.
- **Reports** — condition-aware, day-type aware (holiday/occasion days evaluated against their own ceilings), nil days excluded from all calculations and AI context.
- **Boot survival** — Termux:Boot + wake-lock + watchdog cron. Server auto-restarts after reboots, zero user interaction required.
- **Offline fallback** — when AI is unreachable (flight mode etc.), a manual macro entry form appears automatically.
- **Weight carry-forward** — dashboard shows last known weight when today has no reading, labelled "last known".
- **Wearable integration** — Withings, RingConn, Amazfit via `update_health.py`. AES-encrypted Zepp exports via `pyzipper`. Device precedence is user-configurable per metric, including custom devices beyond the built-in list.
- **Demo mode** — "Try a demo first" seeds realistic sample data across nutrition history, Library, Recipes, Routines, and Strength Training, without ever touching real user data.

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

These are user-configured in Settings (`mh_target_kcal`, `mh_target_protein`, etc.) and read fresh via `getTargets()` — not hardcoded. The figures below reflect Pete's current settings, corrected this session after a height-entry error (188cm, not 178cm) had inflated the TDEE calculation.

| Metric | Target |
|--------|--------|
| Calories | 3,223 kcal base gain-phase (+ activity) |
| Protein | 166g (1.8g/kg) |
| Carbs | ≤50g standard / ≤75g occasion / ≤75g holiday |
| Fat | ≥240g (≥65% of calories, GBM therapeutic floor) |
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
