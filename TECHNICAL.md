# MaxedHealth Technical Reference

## Architecture

Single-file PWA (`maxhealth.html`, ~900KB) served by a Python HTTP server (`server.py`) running locally on Android via Termux. All data stored in localStorage and flat files on device.

```
Browser (Chrome/Android)
    ↕ localhost:5757
Python HTTP Server (server.py)
    ↕ filesystem
Data tables (master.csv, combined.csv, library.csv)
    ↕ pipeline
Wearable exports (Withings, RingConn, Amazfit)
```

AI requests route through a Cloudflare Worker proxy (`maxhealth-ai.bogginsuk.workers.dev`) which holds the Anthropic API key. The app sends model and max_tokens — the Worker passes them through.

---

## File locations

| File | Path |
|------|------|
| App | `/storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html` |
| Server | `/storage/emulated/0/maxhealth/app/maxhealth/server.py` |
| Pipeline | `/storage/emulated/0/maxhealth/app/maxhealth/update_health.py` |
| Setup | `/storage/emulated/0/maxhealth/app/maxhealth/setup.sh` |
| master.csv | `/storage/emulated/0/maxhealth/data/tables/master.csv` |
| combined.csv | `/storage/emulated/0/maxhealth/data/tables/combined.csv` |
| library.csv | `/storage/emulated/0/maxhealth/data/tables/library.csv` |
| Boot script | `~/.termux/boot/maxhealth.sh` |

---

## master.csv format

Pipe-delimited. Notes field may contain commas — pipes are reserved as delimiters.

```
date|kcal|protein|carbs|fat|notes
16/06/26|3506|188|42|274.5|Chemotherapy, 45min Resistance, 76min Walking
```

**Notes field values:**
- `standard` — normal day, no tags
- `holiday` — holiday day mode
- Occasion tags: `Chemotherapy`, `Hospital day`, `Illness`, `Social event`, `Travel`, `Fasting`
- Activity: `45min Resistance`, `76min Walking`, `60min Swimming` etc
- Multiple values comma-separated

---

## localStorage keys

| Key | Description |
|-----|-------------|
| `maxhealth_v1` | Main state JSON (todayLog, history, dayMode, notes, weight, waterToday, lastDate) |
| `mh_today_notes` | Today's occasion tags — persists across Termux restarts |
| `mh_activities` | Activity card state (types, duration, effort, enabled) |
| `mh_target_kcal` | Calorie target |
| `mh_target_protein` | Protein target |
| `mh_target_fat` | Fat target |
| `mh_target_water` | Water target (base, before exercise adjustment) |
| `mh_target_carbs` | Carb target (synced with mh_ceil_standard) |
| `mh_ceil_standard` | Carb ceiling — standard day mode |
| `mh_ceil_occasion` | Carb ceiling — occasion day mode |
| `mh_ceil_holiday` | Carb ceiling — holiday day mode |
| `mh_weight_target_low` | Weight target lower bound |
| `mh_weight_target_high` | Weight target upper bound |
| `mh_name` | User name |
| `mh_condition` | Medical condition (gbm, t2d, general) |
| `mh_visual_theme` | Visual colour theme |
| `mh_color_scheme` | Dark/light/auto scheme |
| `mh_recent_scans` | Last 10 barcode scans |
| `mh_saved_queries` | Saved report queries |
| `mh_notif_prefs` | Notification preferences |
| `mh_steps_today` | Today's step count (cleared at midnight) |
| `mh_library` | Food library JSON |
| `mh_supplement_defs` | Supplement definitions |
| `mh_supplement_log` | Today's supplement log |

---

## State object structure

```javascript
state = {
  todayLog: [{ id, name, amount, kcal, protein, fat, carbs, time, _fromLibrary, _portionPct }],
  history:  [{ date, log, totals, mode, notes, weight, water_ml }],
  dayMode:  'standard' | 'occasion' | 'holiday',
  notes:    'Chemotherapy, 45min Resistance',  // occasion tags + activity
  lastDate: '16/06/26',
  weight:   92.5,
  waterToday: 1500,
}
```

---

## MET calorie calculation

```
kcal = MET × weight(kg) × duration(hours)
```

| Activity | Easy | Moderate | Hard |
|----------|------|----------|------|
| Walking | 2.8 | 3.5 | 4.5 |
| Resistance | 3.0 | 5.0 | 6.0 |
| Custom exercise | 3.5 | 5.0 | 7.0 |

Dynamic target adjustments:
- **Calories**: base + Σ(MET × weight × hours) per activity
- **Protein**: base + 15g when resistance enabled
- **Water**: base + 500ml per hour of any activity

---

## Rollover logic

Fires in `updateDashboard()` when `state.lastDate !== todayStr()`.

```
1. Capture: log, notes, mode, weight, water, lastDate
2. Set state.lastDate = today (immediately prevents re-trigger)
3. Clear: todayLog, notes, dayMode, waterToday, steps, activities duration
4. saveState() — persists today's date
5. If captured log non-empty AND date not already in history:
   a. Write history entry
   b. Build notes from captured occasion tags + activity state
   c. setTimeout(saveNutritionToServer, 1000)
   d. saveState()
```

---

## Cloudflare Worker

```javascript
// worker.js — passes model and max_tokens through from app
body: JSON.stringify({
  model: body.model || 'claude-sonnet-4-6',
  max_tokens: body.max_tokens || 1024,
  system: body.system,
  messages: body.messages
})
```

Update via Cloudflare dashboard → Workers & Pages → maxhealth-ai → Edit code.
Cannot be deployed from Android (Wrangler requires x86_64).

---

## Version history summary

| Version | Phase | Key features |
|---------|-------|-------------|
| v1.0.0 | 1 | Initial build — dashboard, AI logging, pipeline |
| v1.9.0 | 5 | Editable grid, long meal split |
| v2.0.0 | 6 | 4-tab nav, fat tracking, supplements, barcode |
| v2.7.x | 8 | Library split, recipe scaling, A-Z nav |
| v2.9.x | 8 | Occasion tags, streak, weight trend, swipe delete |
| v3.0.x | 9 | Treatment analysis, weekly export, oncology view |
| v3.1.x | 9 | Activity card, MET calc, notes in query builder |
| v3.2.x | 9 | Model fix, GBM summary, dynamic targets |
| v3.3.x | 9 | Activity layout, water dynamic, rollover guard |
| v3.4.x | 9 | Custom modals, intelligence analysis, rollover rewrite |

---

## Common operations

**Deploy after update:**
```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html
cd /storage/emulated/0/maxhealth/app/maxhealth
git add -A && git commit -m "vX.X.X — description" && git push
```

**Full backup:**
```bash
pkg install zip -y
cd /storage/emulated/0/maxhealth
zip -r "/storage/emulated/0/Download/maxhealth_backup_$(date +%Y%m%d).zip" app/maxhealth/ data/tables/
```

**Rollback:**
```bash
cd /storage/emulated/0/maxhealth/app/maxhealth
git log --oneline -10
git reset --hard COMMIT_HASH
git push --force
```

**Sync wearable data:**
```bash
cd /storage/emulated/0/maxhealth/app
python update_health.py
```

**Check server:**
```bash
curl http://localhost:5757/ping
```

---

## Known issues

- Tab bleeding — occasional, cosmetic only
- Cloudflare Worker cannot be updated from Android (use dashboard or laptop)
- GitHub Pages service worker can interfere with localhost — clear site data if this occurs

---

*Built with Claude by Anthropic*
