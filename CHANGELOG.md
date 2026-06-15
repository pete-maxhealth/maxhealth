# MaxedHealth Changelog

## v3.4.0 — Phase 9 (15 Jun 2026)
- Custom themed modals replace all browser confirm/alert/prompt dialogs
- Styled with app design system — dark/light theme aware, danger styling for deletions

## v3.3.9 — Phase 9 (15 Jun 2026)
- All activities deletable including Walking and Resistance
- Confirm dialog before deletion
- Activity types persist permanently — only duration/enabled clears at midnight

## v3.3.8 — Phase 9 (15 Jun 2026)
- Rollover guard prevents ghost duplicate lines in master.csv
- Each date can only roll over once — flag stored in localStorage

## v3.3.7 — Phase 9 (15 Jun 2026)
- Midnight rollover rebuilds full notes from occasion tags + activity state
- Chemotherapy, resistance bands etc now correctly written to master.csv

## v3.3.6 — Phase 9 (14 Jun 2026)
- Rollover date captured before state.lastDate changes — correct date in master.csv
- Water progress bar uses adjusted target (base + exercise)

## v3.3.5 — Phase 9 (14 Jun 2026)
- Duration input uses onchange/onblur — no more focus loss while typing
- dash-scroll overflow fix

## v3.3.4 — Phase 9 (14 Jun 2026)
- Activity row two-line layout — name+kcal on top, duration+effort below
- No more horizontal overflow on small screens

## v3.3.3 — Phase 9 (14 Jun 2026)
- Resistance bands → Resistance (shorter label)
- dash-scroll min-height fix

## v3.3.2 — Phase 9 (14 Jun 2026)
- overflow:hidden on views, subviews and app wrapper (bleeding fix attempt)

## v3.3.1 — Phase 9 (14 Jun 2026)
- Custom activity delete button fixed — uses index >= 2 check

## v3.3.0 — Phase 9 (14 Jun 2026)
- Smart emoji for custom exercises (🏊 swimming, 🚴 cycling, 🏃 running etc)
- Custom activity delete button fixed using custom_ ID prefix

## v3.2.9 — Phase 9 (14 Jun 2026)
- Descriptive effort labels per activity type
- Walking: Easy (<2mph) / Moderate (3–4mph) / Hard (4–5mph+)
- Resistance: Easy — light / Moderate — working hard / Hard — near max

## v3.2.8 — Phase 9 (14 Jun 2026)
### Added
- All macro targets adjust dynamically with exercise:
  - Calories — MET × weight × duration
  - Protein — +15g on resistance days
  - Water — +500ml per hour of activity
  - Carbs — stays fixed (therapeutic ceiling unchanged)
- Activity summary auto-saves to notes/history (e.g. "76min Walking, 45min Resistance")
- History shows exercise minutes as separate 🏃 line in accent colour
- Steps removed from Remaining Today (wearable is authoritative)

## v3.2.7 — Phase 9 (14 Jun 2026)
- GBM summary tokens 6000, concise prompt instruction

## v3.2.6 — Phase 9 (14 Jun 2026)
- Fixed wrong model name across all 15 AI calls (claude-sonnet-4-20250514 → claude-sonnet-4-6)
- This was breaking all AI features including meal logging

## v3.2.5 — Phase 9 (14 Jun 2026)
- GBM summary better error reporting (shows actual API error)

## v3.2.4 — Phase 9 (14 Jun 2026)
- Calorie tile updates dynamically when activities ticked
- Remaining calories recalculates against adjusted target

## v3.2.3 — Phase 9 (13 Jun 2026)
- Daily carb target removed — superseded by Carb Ceilings
- Carb Ceilings section has reference ranges in description
- saveCarbCeilings syncs mh_target_carbs for backwards compatibility

## v3.2.2 — Phase 9 (13 Jun 2026)
- GBM carb adherence fixed (getTargets().standard not getTargets())
- updateGBMStats fixed same way

## v3.2.1 — Phase 9 (13 Jun 2026)
- GBM summary tokens increased 900→4000

## v3.2.0 — Phase 9 (12 Jun 2026)
### Fixed
- Phase banner removed from dashboard
- Protein tile reads from settings (165g), updates dynamically
- Activity card moved just above water section
- Occasion tags preserved when switching to Standard
- History tag × delete fixed — uses data-tag attribute, deletes only tapped tag
- Carer link generates self-contained HTML blob (no missing carer.html)
- Carb ceilings set at onboarding (GBM: 50/75/100g, T2D: 100/150/200g)

## v3.1.9 — Phase 9 (12 Jun 2026)
### Added
- 🏃 Activity card — permanent on dashboard, any day mode
- Walking + Resistance defaults with duration and effort (Easy/Moderate/Hard)
- MET-based calorie calculation (MET × weight × hours)
- + Add exercise for custom activities with smart emoji detection
- Notes/Tags column in Reports query builder with text search
- Occasion tags cleaned — removed Walking/Resistance/Exercise/Birthday/Rest day
  (these moved to activity card)

## v3.1.8 — Phase 9 (11 Jun 2026)
- Steps field visible in Remaining Today
- Occasion button stays highlighted after selecting tags (dayMode sync fix)

## v3.1.7 — Phase 9 (11 Jun 2026)
- Steps labelled as informational — wearable takes precedence
- Walking tag confirmed present in occasion picker

## v3.1.6 — Phase 9 (11 Jun 2026)
- Steps moved to Remaining Today section — visible on any day mode

## v3.1.5 — Phase 9 (12 Jun 2026)
- Occasion button stays highlighted (updateDashboard syncs button state)
- Activity calorie nudge — ⚡ banner shows extra kcal from exercise tags
- Steps field in occasion picker

## v3.1.4 — Phase 9 (11 Jun 2026)
- 😴 Rest day added to occasion tags

## v3.1.3 — Phase 9 (12 Jun 2026)
- Occasion tags write correctly to master.csv
- Legacy values filtered, real tags pass through
- EOD, midnight rollover, sync all, backup all fixed

## v3.1.2 — Phase 9 (11 Jun 2026)
- Saved query card name now visible (accent colour, fallback text)

## v3.1.1 — Phase 9 (11 Jun 2026)
- Saved query card layout fixed — single row, ellipsis on long names

## v3.1.0 — Phase 9 milestone (11 Jun 2026)
- Removable tag pills in history edit — × button per tag
- Docs updated

## v3.0.9 — Phase 9 (11 Jun 2026)
### Added
- 🎤 Voice input — microphone button, Web Speech API
- 📷 Recently scanned — last 10 barcode items for quick re-log
- 📋 Oncology Team View — clinical PDF/text report (30/14/90/7 day periods)
- Custom occasion tag Add button fixed (settings-input class)

## v3.0.8 — Phase 9 (11 Jun 2026)
- Carb ceilings editable per day mode (Standard/Occasion/Holiday)
- Saved to localStorage, used in all adherence calculations

## v3.0.7 — Phase 9 (11 Jun 2026)
- Dark/Light/Auto theme fixed — body attribute, separate from visual theme
- Light theme correctly overrides all colour variables

## v3.0.6 — Phase 9 (11 Jun 2026)
- Weekly summary print — portrait A4, CSS variables resolved for PDF

## v3.0.5 — Phase 9 (11 Jun 2026)
- Dark/Light/Auto theme toggle in Settings → Customise → Appearance
- Weekly summary try/catch

## v3.0.4 — Phase 9 (11 Jun 2026)
### Added
- 📊 Weekly Summary export — day-by-day, print/copy
- Chemo days highlighted purple, treatment days called out

## v3.0.3 — Phase 9 (11 Jun 2026)
- Treatment Analysis in Reports — auto-detects chemo/treatment tags
- Compares calories, protein, fat, carbs on treatment vs standard days

## v3.0.2 — Phase 9 (11 Jun 2026)
- Long-press library card for instant log (600ms, vibrate)

## v3.0.1 — Phase 9 (11 Jun 2026)
- Long-press rebuilt — index from onclick, prevents browser context menu

## v3.0.0 — Phase 9 milestone (11 Jun 2026)
- Legacy notes filtered from tag display
- History shows only real occasion tags

## v2.9.x — Phase 8 (11 Jun 2026)
- Occasion picker multi-tag system
- Ketosis streak counter
- Weight trend prediction
- Swipe left to delete log entries
- Long-press library for instant log
- Save changes closes form
- GBM tile text cutoff fixed

## v2.8.x — Phase 8 (11 Jun 2026)
- Portion badge (↑200%/↓50%) on log entries
- Fat in history edit
- Midnight rollover fix
- History layout, weight card overflow

## v2.7.x — Phase 8 (10–11 Jun 2026)
- Recipe ingredient live scaling
- A-Z library nav, category filter
- Meal ingredients in library view
- 10+ item lists fixed

## v2.6.x — Phase 8 (10 Jun 2026)
- Library split Meals/Ingredients
- Inline amount scaler on LOG
- Fat in running totals

## v2.0.0 — Phase 6 (29 May 2026)
- 4-tab navigation, fat tracking, supplements
- Recipe builder, barcode scanner, missed day flow

## v1.9.0 — Phase 5 (late May 2026)
- Editable correction grid, long meal parallel requests

## v1.0.0 — Initial build (May 2026)
- Dashboard, AI meal logging, Cloudflare Worker proxy
- Python pipeline (Withings, RingConn, Amazfit)
