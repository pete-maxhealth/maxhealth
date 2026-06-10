# MaxedHealth Changelog

## v2.7.3 — Phase 8 (10 Jun 2026)

### Added
- Library split into **🍽 MEALS** and **📋 INGREDIENTS** sections with counts
- Meals show ingredient list with portions in library view
- Inline amount scaler on library LOG — type grams, macros update live
- **Save as meal / Save ingredients / ✦ Save both** buttons post-log
- Amount-first flow — type food name only, preview appears with amount field auto-focused
- Macro ratio bar with target marker, status label and guidance line
- Smart fat target in running totals line (e.g. `188/247g F`)
- Two-line log entry format — name+amount on line 1, macros on line 2
- Library delete confirm dialog
- Truncation repair — salvages complete items if AI response is cut short
- Sequential split requests (800ms delay) to prevent proxy rate limiting
- `why-free.html` page added to repo

### Fixed
- Long meal lists (10+ items) now correctly return all items via sequential split
- Library crash (`renderItems is not a function`) fixed
- Meals correctly detected in library (legacy entries via `portion: '1 serving'`)
- Fat sanitiser no longer fires incorrectly for tablespoon/tsp amounts
- Barcode portion scaling uses OFF `serving_size`/`serving_quantity`
- History storage strips log arrays >30 days old to prevent ~90 day localStorage cap
- Rollover abort caused by supplement log reset fixed
- Tab bleeding fixed (overflow hidden on .view, .subview)
- MCT oil tablespoon scaling bug fixed (parseFloat "1 tablespoon" → 1, not 14×)
- Duplicate dashboard entries on log entry name edit
- Library edit double-save guard added
- Library search debounced for large libraries

### Removed
- Fibre tile from dashboard (not used)
- Fibre target from Settings
- "Correct this" correction grid from post-log bubble (use Library edit instead)

### Changed
- Dashboard tile values rounded to integers, font size reduced
- Multi-item meal description shows "Chicken + Onions + 8 more" not full ingredient list
- Save buttons restored: Save as meal / Save ingredients / Save both

---

## v2.5.0 — Phase 8 start (10 Jun 2026)
- Barcode portion scaling from OFF serving_size
- History storage optimisation (strip old logs)
- TECHNICAL.md rewritten
- why-free.html created
- Ketogenic ratio and avg fat back-calculated for pre-fat-tracking history
- Fat column added to all master.csv write paths
- server.py updated with fat column
- Clear Today's Log button in Settings
- Rollover abort fix

---

## v2.2.2 — Phase 7 end (Jun 2026)
- Library delete/edit index bug fix (_origIdx tagging)
- Notifications interval fix (20-minute setInterval)
- parseFood fallback intercept removed
- Fat sanitiser (sanitiseFatValues) added
- Save-to-library post-logging flow
- Meal photo 3-step visual reasoning
- mhstart as ~/bin/mhstart script

---

## v2.0.0 — Phase 6 (29 May 2026)
- 4-tab navigation (Today/Log/Insights/Settings)
- Fat tracking everywhere
- Supplement tracker (19 supplements, multi-period)
- Midnight sync
- Missed day conversational flow
- Recipe builder
- Barcode scanner with Open Food Facts

---

## v1.9.0 — Phase 5 (late May 2026)
- Editable correction grid
- Long meal parallel AI requests
- History index fix
- Log/Query mode toggle
- Imperial/metric/stones weight toggles

---

## v1.8.0 — Phase 4 (mid-May 2026)
- Barcode scanner (BarcodeDetector API + AI fallback)
- Open Food Facts integration
- Recipe builder
- Comprehensive nutrient tracking
- Water tracking
- History entry editing

---

## v1.0.0 — Initial build (May 2026)
- Dashboard, AI meal logging, localStorage
- Cloudflare Worker proxy
- Python data pipeline (Withings, RingConn, Amazfit)
- combined.csv / master.csv
