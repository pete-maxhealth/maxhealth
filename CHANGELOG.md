# MaxHealth — Changelog

> Built by a GBM patient who needed it. Given freely to everyone who does.
> YOUR DATA. YOUR HEALTH. YOUR RULES.

---

## v1.9 — Phase 5 (May 2026)

### New Features
- **Carer & Clinician portal** — `carer.html` standalone read-only view. Generates a shareable 7-day link from Settings. Shows daily nutrition history, weekly summaries with adherence bars, sparkline trends, and colour-coded target compliance. Zero-day filtering so carers only see logged days.
- **iOS / Safari support** — PWA installable from Safari. Apple touch icon, safe area insets for iPhone notch, input zoom prevention, overscroll-behavior on all scroll containers.
- **Water target celebration** — Water card pulses with animated blue glow when daily target is reached. Matches ketosis badge animation style.
- **Dedicated Carer & Clinician section in Settings** — moved from buried inside Data & Backup to its own clearly labelled section.
- **Nutrition input redesign** — Icon buttons (camera, gallery, search, barcode) moved to their own row above the text input, giving the input field full width.
- **Shorter welcome message** — Nutrition tab welcome bubble condensed to one line so the input area is immediately accessible.

### Bug Fixes
- **AI food logging proxy fix** — Cloudflare proxy path now inlines system prompt into user message, matching the pattern used by the working Reports path. Fixes "Failed to fetch" for users without a personal API key.
- **Drill-down overlay scroll** (Android Chrome) — Fixed.
- **Daily view tappable rows** (Android Chrome) — Fixed.

### Demo Mode
- Demo data updated with full Phase 4+ fields: water_ml, fibre, fat, steps, heart_rate, hrv, spo2, sleep_hours, occasion days, richer meal log entries.

---

## v1.8 — Phase 4 (April–May 2026)

### New Features
- **Barcode scanner** — Scan product barcodes directly from the Nutrition tab. Looks up Open Food Facts database. Logs with exact nutritional values.
- **Fibre tracking** — Daily fibre target (default 25g, configurable in Settings). Tracked from food database and barcode scans. Shown on dashboard and in history.
- **Water tracking** — Dashboard water card with one-tap logging (Glass 250ml, Can 330ml, Bottle 500ml, Custom). Daily target configurable in Settings. Resets at midnight.
- **Recipe builder** — Create multi-ingredient recipes, save to library, log as single entries. Barcode scanning supported within recipe builder.
- **History editing** — Tap any entry in Today's Log to edit calories, protein or carbs inline. 5-second undo on deletion. Previous days editable via History tab.
- **Missed day logging** — Log a day you forgot via AI (describe what you ate) or enter macros directly. Accessible from History tab.
- **Nutrient deep-dive** — Expanded macro tracking including fat and fibre alongside existing kcal/protein/carbs.
- **Carer view link generator** — Generates shareable read-only snapshot URL (carer.html — completed in Phase 5).
- **One-tap pipeline sync** — Streamlined sync flow in Import tab.
- **GBM guide timetable page** — Dedicated treatment schedule reference.
- **Cloud mode banner** — Visible indicator when running from GitHub Pages vs localhost.
- **GitHub → localhost auto-redirect** — Dev workflow improvement.
- **Merged setup / user guide** — Single unified documentation page.

### Pipeline (Python / Termux)
- **Source precedence config** — Per-metric device priority (RingConn, Withings, Zepp/Amazfit). Downloadable config file. Applied on next sync.
- **Universal device extractor** — Import tab AI column mapper handles non-standard CSV formats.
- **mhstart alias** — Single command to start local server from Termux.

### Bug Fixes
- Contextual tips system — dismissable per-tab tips, reset via Settings.
- Data integrity check on init — flags duplicate dates, missing dates, suspicious values.
- Floating point rounding fixes across all macro displays.

---

## v1.7 — Phase 3 (Early 2026)

### New Features
- **Condition-specific onboarding** — 4 condition cards in setup wizard:
  - 🧠 GBM / Therapeutic Ketosis → 50g carb ceiling, patient guide
  - 🩸 Type 2 Diabetes → 100g carb ceiling
  - ⚖️ Body Recomposition → protein focus
  - ❤️ General Health → standard defaults
- **Health context AI injection** — Free-text field in Settings injected into every AI system prompt. Enables context-aware responses (e.g. chemotherapy cycle, fatigue, water retention).
- **Food library editing** — Tap any saved food to edit name or macros inline.
- **GBM Patient Protocol Guide** — Linked from Reports, Settings and Story page.
- **Body composition drill-downs** — Weight, HRV, SpO₂, sleep, steps — full chart overlays with stats.
- **Contextual onboarding tips** — Dismissable first-visit tips on each tab.
- **Push notifications** — EOD reminder, carb ceiling warning, permission flow.
- **Day mode selector** — Standard / Occasion / Holiday with dynamic carb ceilings (50g / 75g / 100g).
- **Phase logic** — Auto-switches Gain ↔ Maintenance at 92kg sustained.
- **Seasonal compare** — Reports tab Period A vs Period B date comparison with AI analysis.
- **Reports Query Builder** — Metric + operator + value selector runs against full history.
- **Trends tab** — Today / 30 / 60 / All filters. Daily view with day navigation. Chart drill-downs.
- **Import tab** — combined.csv import, device extractor UI, AI column mapper, pipeline commands.
- **Count-up animation** — Dashboard macros animate on load.
- **Demo mode** — Full 30-day sample data, read-only, enter/exit without affecting real data.

### Pipeline
- Withings extractor — body comp scale (weight, fat%, muscle%, water%, bone%, visceral fat, BMR).
- RingConn extractor — smart ring (HRV RMSSD+SDNN, sleep staging, SpO₂, heart rate, steps).
- merge.py — builds combined.csv from all tables, left-join on date.
- utils.py — logging, CSV helpers, config, date normalisation.
- setup.py — first-run wizard.
- server.py — local HTTP server (Termux).

---

## v1.6 — Phase 2 (Late 2025)

### New Features
- **Claude AI via Cloudflare proxy** — No user API key required. Meal logging and questions answered by Claude (Anthropic). Proxy at `maxhealth-ai.bogginsuk.workers.dev`.
- **Photo meal logging** — Photograph a meal or nutrition label. Label mode: switch to 🏷, type product name and amount.
- **Food library** — Save foods from AI responses. Edit, delete, duplicate prevention.
- **Reports tab** — Date range selection, summary cards, GBM monthly brief, AI insights.
- **End-of-day save to history** — Daily log saves automatically at midnight rollover.
- **Onboarding wizard** — TDEE calculator with activity level and goal selection.
- **Body comp chart overlays** — Weight chart with fat%, muscle%, hydration overlays.
- **Nutrition/wearable correlation** — Cross-reference nutrition with wearable metrics in Reports.
- **Data import/export** — JSON backup, nutrition CSV, combined CSV export.
- **PWA + service worker** — Network-first caching, auto-updates, installable on Android.
- **AI provider selector** — Claude (default), OpenAI, or Local only.

---

## v1.0–v1.5 — Phase 1 (2025)

### Foundation
- Single-file mobile-first HTML app. All CSS and JS inline. Zero build tools.
- GitHub Pages hosting. `localStorage` persistence.
- Dashboard tab — weight card, phase banner, macro progress bars, ketosis badge.
- Nutrition tab (originally "Log Meal") — free-text AI meal logging.
- History tab — week/month/all filter, expandable day entries.
- Strict low-carb protocol — 50g standard, 75g occasion, 100g holiday.
- Therapeutic ketosis tracking for GBM management.
- Dark theme — deliberate, permanent.
- Chart.js integration (cdnjs, no npm).
- Multiple themes — Midnight, Aurora, Carbon, Slate, Light.
- Custom accent colour picker.

---

## Roadmap (Phase 5+)

- Supplement tracker (omega-3, Vitamin D, magnesium)
- Carer portal expansion — live sync, PIN access, notification alerts
- Meal templates — one-tap logging for frequent meals
- Native wearable sync APIs
- Zepp/Amazfit Python extractor
- Pipeline rolling backups

---

*MaxHealth is built and maintained by Pete — retired Oracle DBA, retired RPA developer, GBM patient.*
*Developed with Claude (Anthropic). May it be useful to someone else too.*
