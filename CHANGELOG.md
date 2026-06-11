# MaxedHealth Changelog

## v2.9.3 — Phase 8 final (11 Jun 2026)

### Fixed
- History edit day totals — was using render index for DOM lookup, now correctly uses render index for DOM and array index for data
- `undefinedg ceiling` / `undefinedg target` in Insights — `getTargets()` was returning whole object, fixed to `.standard`
- GBM Monthly Summary date placeholder `[Month Day, Year]` — today's date now injected into prompt
- Portion edit form — clearer hint text "use this OR edit values below", step 50, examples shown
- Recipe save ingredients — dupe check now uses partial name matching so "Lurpak" matches "Lurpak Spreadable Slightly Salted (Lurpak)"
- Dashboard tile font — reduced to `clamp(12px, 3vw, 16px)` so 4-digit calorie values don't clip
- Save changes button — edit form now explicitly closed on save (renderDash was undefined)
- GBM tile text cutoff — `overflow:hidden` on grid container
- Save query layout — proper label, wider input, cleaner layout
- Portion badge on library logging — badge set at log time when factor ≠ 1

## v2.8.x — Phase 8 (11 Jun 2026)

### Added
- Portion percentage badge on today's log entries — green ↑200% or yellow ↓50% when portion differs from standard
- Fat field added to Override Day Totals edit form (2×2 grid)
- Midnight rollover check in updateDashboard — catches app left open past midnight

### Fixed
- History layout — macros nowrap, date flex-shrink:0, fat back-calculation in purple for old entries
- Weight card target range — clamped font, overflow hidden
- Weight target inputs — stacked From/To on separate lines, full width
- Import/pipeline command box — word-break fix, paths on separate lines
- GBM Monthly Summary — fat back-calculated for pre-tracking entries, avg fat and fat% now correct
- AI Provider buttons — flex-wrap so OpenAI doesn't overflow
- Duplicate log entries on midnight rollover — fixed

## v2.7.x — Phase 8 (10–11 Jun 2026)

### Added
- Recipe ingredient amounts with live scaling — each ingredient shows base portion, change grams and macros update live
- A-Z quick nav bar in library — tap letter to jump and highlight
- Category filter in library (All / Meals only / Ingredients only)
- Meal ingredients shown as text list in library view
- Library search debounced for large libraries

### Fixed
- All 10+ item lists now return correctly — sequential split requests with 800ms delay
- Truncation repair — salvages complete items from cut-off AI response
- Library crash (`renderItems is not a function`) — double join bug
- Meals correctly detected in library (legacy entries via `portion: '1 serving'`)
- Fat sanitiser false-positive for tablespoon/tsp amounts
- Spurious protein scaling warnings for volume amounts
- Duplicate dashboard entries guard
- Library edit double-save guard

## v2.6.x — Phase 8 (10 Jun 2026)

### Added
- Library split into 🍽 MEALS and 📋 INGREDIENTS sections with counts
- Inline amount scaler on library LOG — type grams, macros update live
- Save as meal / Save ingredients / ✦ Save both buttons post-log
- Amount-first logging flow — type food name only, preview with amount field auto-focused
- Fat target in running totals line (e.g. 188/247g F)
- Two-line log entry format — name+amount / macros

### Fixed
- Long meal split threshold — 7 items triggers split
- Library delete confirm dialog
- Library search with category filter and sort

## v2.5.x — Phase 8 start (10 Jun 2026)

### Added
- Fat column in all master.csv write paths
- Clear Today's Log button in Settings
- Ketogenic ratio back-calculation for pre-fat-tracking history
- Fat back-calculation in Reports avg fat

### Fixed
- Rollover abort caused by supplement log reset
- History storage optimisation (strip log arrays >30 days)
- Barcode portion scaling from OFF serving_size/serving_quantity
- Tab bleed CSS reverted to working state

## v2.2.x — Phase 7 (Jun 2026)
- Library delete/edit index bug (_origIdx tagging)
- Notifications 20-minute setInterval
- parseFood fallback intercept removed
- Fat sanitiser (sanitiseFatValues)
- Save-to-library post-logging
- Meal photo 3-step reasoning

## v2.0.0 — Phase 6 (29 May 2026)
- 4-tab navigation (Today/Log/Insights/Settings)
- Fat tracking throughout
- Supplement tracker (19 supplements, multi-period)
- Midnight sync, missed day flow
- Recipe builder, barcode scanner

## v1.9.0 — Phase 5 (late May 2026)
- Editable correction grid
- Long meal parallel AI requests
- History index fix
- Log/Query mode toggle

## v1.8.0 — Phase 4 (mid-May 2026)
- Barcode scanner (BarcodeDetector API + AI fallback)
- Open Food Facts integration
- Recipe builder, water tracking
- History entry editing

## v1.0.0 — Initial build (May 2026)
- Dashboard, AI meal logging, localStorage
- Cloudflare Worker proxy
- Python data pipeline (Withings, RingConn, Amazfit)
