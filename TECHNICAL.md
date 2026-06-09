# MaxedHealth — Technical Reference

**Version:** v2.2.x (Phase 7 / Phase 8)  
**Last updated:** June 2026  
**Repo:** `pete-maxhealth/maxhealth`  
**Live URL:** `https://pete-maxhealth.github.io/maxhealth/maxhealth.html`  
**Local URL:** `http://localhost:5757` (served by `server.py` via Termux)

---

## Architecture Overview

MaxedHealth is a **single-file PWA** (`maxhealth.html`) — all HTML, CSS, and JavaScript in one file, approximately 13,000+ lines. It runs locally on Android via Termux and a Python HTTP server, and is also accessible via GitHub Pages. There is no backend database; all user data is stored in `localStorage` and optionally persisted to CSV files on the device filesystem via the local server.

```
┌─────────────────────────────────────────────┐
│              maxhealth.html (PWA)           │
│  4-tab nav: Today / Log / Insights /        │
│             Settings                        │
│                                             │
│  AI meal logging → Cloudflare Worker proxy  │
│  Barcode scan  → Open Food Facts API        │
│  Wearable data ← combined.csv (via import)  │
│  History/logs  ↔ localStorage               │
│  Library/supps ↔ localStorage + server CSV  │
└────────────────┬────────────────────────────┘
                 │ HTTP (localhost:5757)
┌────────────────▼────────────────────────────┐
│              server.py (Termux)             │
│  Serves static files                        │
│  POST /save-nutrition   → master.csv        │
│  POST /save-library-csv → library.csv       │
│  POST /save-supplements → supplements.csv   │
│  GET  /library          → library.csv       │
│  GET  /health           → status check      │
│  WS   /ws-probe         → server detection  │
└────────────────┬────────────────────────────┘
                 │ filesystem
┌────────────────▼────────────────────────────┐
│  /storage/emulated/0/maxhealth/data/tables/ │
│    combined.csv      ← update_health.py     │
│    master.csv        ← nutrition log        │
│    library.csv       ← food library         │
│    supplements.csv   ← supplement stack     │
└─────────────────────────────────────────────┘
```

---

## Key File Paths

| File | Path |
|------|------|
| App HTML | `/storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html` |
| Server | `/storage/emulated/0/maxhealth/app/server.py` |
| Pipeline | `/storage/emulated/0/maxhealth/app/update_health.py` |
| Data dir | `/storage/emulated/0/maxhealth/data/tables/` |
| Combined CSV | `/storage/emulated/0/maxhealth/data/tables/combined.csv` |
| Master CSV | `/storage/emulated/0/maxhealth/data/tables/master.csv` |
| Library CSV | `/storage/emulated/0/maxhealth/data/tables/library.csv` |
| Supplements CSV | `/storage/emulated/0/maxhealth/data/tables/supplements.csv` |

---

## Deploy Commands

**Standard deploy (after downloading updated maxhealth.html):**
```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html \
  && cd /storage/emulated/0/maxhealth/app/maxhealth \
  && git add -A \
  && git commit -m "vX.X.X — description" \
  && git push
```

**Start server manually:**
```bash
mhstart
```
(`~/bin/mhstart` — auto-starts via Termux:Boot on device restart)

**Run pipeline:**
```bash
cd /storage/emulated/0/maxhealth/app
python update_health.py           # all devices
python update_health.py --device withings
python update_health.py --device ringconn
python update_health.py --device amazfit
python update_health.py --dry-run
```

---

## Navigation Structure (v2.0+)

4-tab navigation at the bottom of the screen:

| Tab | Sub-tabs / content |
|-----|--------------------|
| **Today** | Dashboard (weight, macros, supplements, water) |
| **Log** | AI chat input, food search, barcode scanner, library |
| **Insights** | Trends charts, body composition, drill-down |
| **Settings** | Targets, themes, import/export, notifications, data management |

Reports is accessible via the Insights tab or direct tab switch.

---

## AI Integration

**Provider:** Claude (Anthropic) via Cloudflare Worker proxy  
**Proxy URL:** `https://maxhealth-ai.bogginsuk.workers.dev`  
**Fallback:** Direct Anthropic API (requires user-supplied API key)  
**Model:** `claude-sonnet-4-20250514`

No API key is required for end users — the Cloudflare Worker handles authentication. The proxy adds CORS headers and forwards requests to `https://api.anthropic.com/v1/messages`.

**Long meal handling:** Meals with 6+ food items are split into two parallel AI requests and merged before display (prevents token truncation on the proxy).

**AI JSON response format** (meal logging):
```json
{
  "type": "meal",
  "items": [
    {
      "name": "Food name",
      "amount": "150g",
      "kcal": 280,
      "protein": 32.5,
      "carbs": 0,
      "fat": 6.2
    }
  ],
  "message": "Optional note shown to user"
}
```
Other response types: `"water"`, `"query"`, `"supplement"`.

**Fat sanitiser (`sanitiseFatValues`):** Applied to all AI responses before display. Corrects known-zero fat values using a reference database (`FAT_FLOOR_DB`) of per-100g fat values. Priority: gram amount from `amount` field → kcal-based estimation as fallback. Foods covered: oils, butter, cream, cheese, eggs, chicken, salmon, beef, bacon, nuts, peanut butter, avocado, yogurt, milk.

---

## Barcode Scanning

1. **BarcodeDetector API** (Chrome Android) — reads EAN-13, EAN-8, UPC-A, UPC-E, Code 128, Code 39, QR
2. **AI fallback** — sends image to Claude to extract barcode digits, then looks up
3. **Open Food Facts API** — `https://world.openfoodfacts.org/api/v2/product/{barcode}`
   - Fields fetched: `product_name`, `brands`, `nutriments`, `quantity`, `serving_size`, `serving_quantity`
   - Macros extracted: kcal, protein, carbs, fat, fibre, saturated fat, sugars, salt, iron (all per 100g)

**Portion suggestions** after scan are generated by `renderPortionSuggestions()`:
1. OFF `serving_quantity` → "Xg (1 serving)" or "Xg (product serving label)" — primary
2. Whole pack from `quantity` string (e.g. "200g") — secondary
3. Piece size from `quantity` (e.g. "6 x 30g") — secondary
4. Keyword-based fallbacks (cream, butter, nuts, chicken, etc.) — last resort
5. 100g always added if not already present

---

## Food Library

**localStorage key:** `maxhealth_foods`  
**Backup keys:** `mh_library_backup`, `mh_library_b2` (triple-write for resilience)  
**Server persistence:** `POST /save-library-csv` → `library.csv`

Library entry schema:
```json
{
  "name": "Product name",
  "brand": "Brand (optional)",
  "kcal": 250,
  "prot": 20.5,
  "carb": 5.2,
  "fat": 15.0,
  "fibre": 2.1,
  "satFat": 6.0,
  "sugars": 1.5,
  "salt": 0.8,
  "iron": 2.5,
  "portion": "30g",
  "servingQty": 30,
  "servingLabel": "1 biscuit",
  "added": "2026-05-01T10:30:00.000Z"
}
```

All values are per 100g except `portion`/`servingQty`/`servingLabel` which describe the default serving.

---

## Supplement Tracker

**localStorage keys:** `mh_supplement_defs`, `mh_supplement_log`  
**Server persistence:** `supplements.csv`

Supplement definition schema:
```json
{
  "id": "supp_abc123",
  "name": "Curcumin",
  "dose": "2400mg",
  "periods": ["morning", "evening"],
  "notes": "Liposomal"
}
```

`periods` is an array of: `"morning"`, `"midday"`, `"evening"`, `"bedtime"`. Supplement log resets at midnight rollover. Legacy single `period` string is migrated to `periods` array on load.

---

## Data Pipeline (update_health.py)

Processes wearable exports into a unified `combined.csv`. Supports:

| Device | Export format |
|--------|--------------|
| Withings Body+ | CSV export from Health Mate app |
| RingConn | CSV export (HRV, SpO2, sleep) |
| Amazfit (Zepp) | ZIP file — password extracted via `pyzipper` |

**Output:** `combined.csv` — 39 fields including weight, BMI, body fat %, muscle mass, bone mass, water %, HRV, SpO2, sleep duration/quality, steps, active calories, resting heart rate.

---

## History Storage

History entries are stored in `state.history[]` within `maxhealth_v1` localStorage key.

**Storage optimisation (v2.2.3+):** On save, entries older than 30 days have their `log` array stripped — only `totals`, `date`, `weight`, `mode`, `notes`, and `water_ml` are persisted. The last 30 days retain full per-item log data for editing. This prevents localStorage quota exhaustion on long-running installs (previously ~90 days before write failures).

History entry schema (full, last 30 days):
```json
{
  "date": "01/06/26",
  "log": [ /* array of food items */ ],
  "totals": { "kcal": 2950, "protein": 148, "carbs": 44, "fat": 238 },
  "mode": "standard",
  "notes": "rest day",
  "weight": 92.1,
  "water_ml": 2200
}
```

History entry schema (archived, 30+ days old):
```json
{
  "date": "01/01/26",
  "totals": { "kcal": 2800, "protein": 140, "carbs": 48, "fat": 220 },
  "mode": "standard",
  "notes": "",
  "weight": 91.0,
  "water_ml": 2000
}
```

---

## localStorage Keys Reference

| Key | Contents |
|-----|----------|
| `maxhealth_v1` | Full app state — history, today's log, weight, water, settings |
| `maxhealth_foods` | Food library (array of items per 100g) |
| `mh_library_backup` | Library backup copy #1 |
| `mh_library_b2` | Library backup copy #2 |
| `mh_supplement_defs` | Supplement definitions array |
| `mh_supplement_log` | Today's supplement tick log |
| `mh_master_csv_cache` | Cached nutrition history (pipe-delimited CSV) |
| `mh_master_csv_meta` | Cache metadata (date, row count) |
| `mh_nutrition_csv_cache` | Raw imported master.csv content |
| `mh_combined_csv_cache` | Raw imported combined.csv content |
| `mh_recipes` | Saved recipe definitions |
| `mh_saved_queries` | Saved report queries |
| `mh_notif_prefs` | Notification preferences |
| `mh_provider` | AI provider (`claude` or `openai`) |
| `mh_apikey` | User-supplied API key (if not using proxy) |
| `mh_condition` | Health condition (`general`, `gbm`, `t2d`, etc.) |
| `mh_theme` | UI colour theme |
| `mh_visual_theme` | Visual theme pack |
| `mh_text_size` | Accessibility text size |
| `mh_target_kcal` | Daily kcal target |
| `mh_target_protein` | Daily protein target (g) |
| `mh_target_carbs` | Daily carbs ceiling (g) |
| `mh_target_fat` | Daily fat target (g) |
| `mh_target_water` | Daily water target (ml) |
| `mh_target_fibre` | Daily fibre target (g) |
| `mh_weight_target_low` | Weight goal lower bound (kg) |
| `mh_weight_target_high` | Weight goal upper bound (kg) |
| `mh_name` | User's name |
| `mh_tdee` | Calculated TDEE |
| `mh_goal` | Current goal mode |

---

## Notifications

Notifications use the browser `Notification` API (requires permission grant). Three notification types:

| Type | Trigger | localStorage dedup key |
|------|---------|------------------------|
| End-of-day reminder | After 9pm if nothing logged | `mh_notif_eod_YYYY-MM-DD` |
| Weekly summary | Sunday after 8am | `mh_notif_weekly_YYYY-MM-DD` |
| Carb ceiling alert | When carbs reach 80% of target | `mh_carb_notif_YYYY-MM-DD` |

Notification check runs 3 seconds after app load, then every 20 minutes (`setInterval`).

---

## Server Endpoints (server.py)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves `maxhealth.html` |
| `GET` | `/health` | Returns `{"status":"ok"}` |
| `GET` | `/library` | Returns `library.csv` content |
| `POST` | `/save-nutrition` | Appends/updates a row in `master.csv` |
| `POST` | `/save-nutrition-bulk` | Writes multiple rows to `master.csv` |
| `POST` | `/save-library-csv` | Overwrites `library.csv` |
| `POST` | `/save-supplements` | Overwrites `supplements.csv` |
| `WS` | `/ws-probe` | WebSocket probe for server detection |

Server detection: the app sends a WebSocket handshake to `ws://localhost:5757/ws-probe` on load. If it succeeds, `_serverOnline = true` and server-dependent features (CSV sync, library persistence) are enabled.

---

## Patching Workflow

All code changes are made via Python patch scripts written to `~/fix_name.py` (not `/tmp/` — permissions issues on Android). Pattern:

```bash
cat > ~/fix_name.py << 'PYEOF'
content = open('/home/..../maxhealth.html', encoding='utf-8').read()
content = content.replace(old_str, new_str)
open('/home/..../maxhealth.html', 'w', encoding='utf-8').write(content)
PYEOF
python3 ~/fix_name.py
```

**Mandatory checks before every commit:**
1. Div balance: `<div` count must equal `</div>` count
2. JS syntax: `node -e "const fs=require('fs');new Function(fs.readFileSync('maxhealth.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1])"`
3. Version bump in `<div class="settings-value">MaxedHealth vX.X.X</div>`

---

## Version History

| Version | Phase | Key changes |
|---------|-------|-------------|
| v1.0 | 1 | Initial build — dashboard, AI logging, localStorage, Cloudflare proxy |
| v1.8 | 4 | Barcode scanner, Open Food Facts, recipe builder, nutrient tracking, water tracking, history editing |
| v1.9 | 5 | Editable correction grid, JSON parse fix for long meals (parallel requests), history index fix, Log/Query mode toggle |
| v2.0 | 6 | 4-tab navigation, fat tracking everywhere, library portion selector, macro ratio bar, supplement tracker (19 supps), midnight sync, missed day flow, install page, MacroDroid guide |
| v2.1.x | 7A–B | Library delete/edit index bug fix, notifications interval fix, `parseFood` fallback intercept fix, fat returning 0g for oils/meat |
| v2.1.x | 7C | Library LOG flow redesign, meal photo 3-step visual reasoning, label photo AI-help flow |
| v2.1.9 | 7D | Post-logging save-to-library (combined or individual), duplicate detection, 2dp macro rounding, `sanitiseFatValues`, TECHNICAL.md rewrite, user guide corrections |
| v2.2.2 | 7E | mhstart as `~/bin/mhstart` proper script |
| v2.2.3 | 8 | Barcode portion scaling from OFF `serving_size`/`serving_quantity`; history storage optimisation (strip old logs, prevent ~90-day localStorage cap) |
