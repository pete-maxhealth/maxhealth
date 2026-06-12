# MaxedHealth Changelog

## v3.1.0 — Phase 8/9 (12 Jun 2026)
- Removable tag pills in history edit — × button on each active tag

## v3.0.9 — Phase 9 (12 Jun 2026)
### Added
- 🎤 Voice input — microphone button next to barcode, speak your meal
- 📷 Recently scanned — last 10 barcode/database items shown for quick re-log
- 📋 Oncology Team View — clean clinical PDF/text report for medical team
- 🐛 Custom occasion tag Add button fixed

## v3.0.8 — Phase 9 (12 Jun 2026)
- Carb ceilings editable per day mode (Standard / Occasion / Holiday)
- Custom ceilings saved to localStorage, used in all adherence calculations

## v3.0.7 — Phase 9 (12 Jun 2026)
- Dark/Light/Auto theme fixed — uses body attribute, separate from visual theme
- Light theme now correctly overrides all colour variables

## v3.0.6 — Phase 9 (12 Jun 2026)
- Weekly summary print — portrait A4, CSS variables resolved for PDF

## v3.0.5 — Phase 9 (12 Jun 2026)
- Carb target Save button added
- Dark/Light/Auto theme toggle in Settings → Customise → Appearance
- Weekly summary try/catch for error visibility

## v3.0.4 — Phase 9 (12 Jun 2026)
### Added
- 📊 Weekly Summary export — select any week, generate day-by-day breakdown
- Print to PDF (portrait A4) or copy as plain text
- Chemo days highlighted in purple, treatment days called out

## v3.0.3 — Phase 9 (12 Jun 2026)
- Treatment Analysis in Reports — auto-detects chemo/treatment tags
- Compares avg calories, protein, fat, carbs on treatment vs standard days
- Lists all treatment days with nutrition and tags
- Visible only when treatment tags exist in history

## v3.0.2 — Phase 9 (11 Jun 2026)
- Long-press library card for instant log at default portion (0.6s hold, vibrate)
- "hold card" hint under LOG button

## v3.0.1 — Phase 9 (11 Jun 2026)
- Long-press rebuilt — reads index from onclick, prevents browser context menu

## v3.0.0 — Phase 9 milestone (11 Jun 2026)
- Legacy notes filtered from tag display (missed day entry, standard, occasion etc)
- History tag display shows only real occasion tags

## v2.9.9 — Phase 8 (11 Jun 2026)
- History edit auto-opens day body when Edit day totals tapped

## v2.9.8 — Phase 8 (11 Jun 2026)
- Occasion tags in history edit — retrospectively tag past days
- Full tag picker with × to remove, custom tag input, saves to day.notes

## v2.9.7 — Phase 8 (11 Jun 2026)
- Removable tag pills in occasion banner — × button per tag
- Active tags shown in picker when open

## v2.9.6 — Phase 8 (11 Jun 2026)
### Added
- 🔥 Ketosis streak counter in badge (consecutive days within ceiling)
- 📈 Weight trend prediction below weight card (avg daily change, days to target)
- 👈 Swipe left to delete log entries with smooth animation
- 📚 Long-press library LOG button for instant log at default portion

## v2.9.5 — Phase 8 (11 Jun 2026)
- Multi-tag occasion system — tap to toggle, multiple tags combine
- Added 💪 Resistance bands and 🚶 Walking tags

## v2.9.4 — Phase 8 (11 Jun 2026)
### Added
- 🟡 Occasion picker — predefined tags with custom input
- Tags: Chemotherapy (purple), Hospital day, Illness, Social event, Travel, Fasting, Exercise, Birthday
- 📌 Banner on dashboard showing active tags
- Tags saved to state.notes, shown in history

## v2.9.3 — Phase 8 final (11 Jun 2026)
### Fixed
- History edit day totals — render index vs array index mismatch
- undefinedg ceiling/target — getTargets().standard fix
- GBM Monthly Summary date placeholder — today's date in prompt
- Save changes form close — renderDash was undefined
- Recipe dupe check — partial name matching
- Dashboard tile font clamp — 4-digit values no longer clip
- Portion edit hint text

## v2.9.x — Phase 8 (10–11 Jun 2026)
- Save changes button now closes form
- GBM tile text cutoff fixed
- Save query layout improved
- Portion badge on library logging

## v2.8.x — Phase 8 (11 Jun 2026)
- Portion percentage badge (↑200% / ↓50%) on log entries
- Fat field in Override Day Totals
- Midnight rollover check in updateDashboard
- History layout fix, fat back-calculation in history
- Weight card clamp, settings inputs stacked

## v2.7.x — Phase 8 (10–11 Jun 2026)
- Recipe ingredient amounts with live scaling
- A-Z quick nav in library
- Category filter (All/Meals/Ingredients)
- Meal ingredients shown in library
- Library search debounced
- All 10+ item lists return correctly (sequential split)
- Truncation repair

## v2.6.x — Phase 8 (10 Jun 2026)
- Library split Meals/Ingredients
- Inline amount scaler on LOG
- Save as meal / ingredients / both
- Amount-first logging flow
- Fat in running totals line

## v2.5.x — Phase 8 (10 Jun 2026)
- Fat column in master.csv
- Barcode portion scaling from OFF serving_size
- History storage optimisation

## v2.2.x — Phase 7 (Jun 2026)
- Library delete/edit index fix
- Notifications 20-minute interval
- Fat sanitiser
- Save-to-library post-logging
- Meal photo reasoning

## v2.0.0 — Phase 6 (29 May 2026)
- 4-tab navigation
- Fat tracking
- Supplement tracker
- Midnight sync, missed day flow
- Recipe builder, barcode scanner

## v1.9.0 — Phase 5 (late May 2026)
- Editable correction grid
- Long meal parallel AI requests
- History index fix

## v1.0.0 — Initial build (May 2026)
- Dashboard, AI meal logging, localStorage
- Cloudflare Worker proxy
- Python data pipeline (Withings, RingConn, Amazfit)
