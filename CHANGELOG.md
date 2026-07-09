# MaxedHealth Changelog — Phase 10 continued (v3.10.99 – v3.10.133)

## New Features

**Library-aware meal suggestions ("📚 From my library")**
- Proposes real combinations of saved library items and Recipes (with proper per-serving math) against today's actual remaining macros — never invents values, only ever uses locked/stored data
- Shows each item's real portion size, not just names
- One-tap logging directly from the suggestion card
- Recipe suggestions reuse the exact same servings-scaling formula as the Recipe Builder itself

**Ingredient substitution flow**
- If a described food doesn't exactly match your library (e.g. wrong brand), offers real alternatives from what you actually have instead of silently falling through to a fresh AI guess
- Works both when no match is found at all, and when you explicitly decline a suggested match
- "Save as new item" option added to the duplicate-comparison screen, for when comparison reveals two genuinely different products rather than a real duplicate

**Ketosis streak milestones**
- One-time celebration messages at 7/14/30/50/100/200/365 consecutive days, shown as both a chat message and a toast (visible regardless of active tab)

**Dashboard & Library section reordering**
- Every section on the Today dashboard (Weight, Day Mode, Ketosis, Macros, Remaining, Macro Ratio, Goal Check, Steps, Activity, Water, Log, Guides & Docs) can be reordered via ▲▼ buttons
- Recipes vs Food Library sections in the Library tab reorderable the same way
- Reports, Manage, and Import tabs also fully reorderable — built as one generic, self-discovering system rather than hand-wiring dozens of sections individually

**Demo mode overhaul**
- "Try a demo first" now seeds realistic sample data across Library, Recipes, Routines, and Strength Training history — previously these sections were completely empty in demo mode, hiding most of what the app actually does
- Built via safe read/write redirection rather than temporarily overwriting real user data

**Library-only ingredient saving**
- New "📚 Just add to library (haven't eaten this)" option when reading a label, for cataloging an ingredient without logging it as eaten today

## Nutrition Logging Accuracy

**Four new sanity checks added to the existing meat-carbs and pure-fat plausibility checks:**
- Atwater kcal-consistency (a food's stated calories must roughly match protein×4 + carbs×4 + fat×9), with an explicit exception for alcohol
- Implausibly low carbs on fruit-named items (the inverse of the meat-carbs check)
- Implausible portion size (under 1g or over 2000g)
- Macro-mass plausibility — protein + fat + carbs in grams cannot physically exceed the food's own stated weight

**Fuzzy-match accuracy (library duplicate detection and substitution)**
- Brand names (Asda, Tesco, Sainsbury's, Lidl, etc.) now correctly disqualify a match when they genuinely differ between query and candidate — previously "double cream is Asda" and "double cream is Lidl" scored identically
- Meat/protein type (chicken vs beef vs pork etc.) now works the same way — previously a single shared generic word like "mince" could match two completely different meats
- Short 2-word queries now require both words to match, not just one — closes the gap where a single generic shared word inflated the match score

**Meal-photo reasoning text**
- AI no longer states its own rough sanity-check total in the message field — previously this could show a different number from the actual, more carefully-calculated logged total, creating a confusing self-contradiction

**Long-meal parsing safety net**
- A named item with every macro at zero is now excluded rather than silently logged — this pattern almost never represents a real food and more likely indicates a parsing failure somewhere in the AI response chain

**Today's summary — fixed missing fat**
- The "show today summary" conversational response was missing fat entirely from its output; now included alongside calories, protein, and carbs

## Data Safety

- "Export All Data" now includes recipes and routines in the JSON backup — previously silently missing
- Corrected misleading "downloads one zip" wording to accurately describe the several separate files actually produced
- Recipe deletion now requires confirmation — previously deleted instantly with no warning

## UX & Organization

- Settings grouped into clear categories (Your Targets, Data & Devices, App Info), with debug/diagnostic tools (Body Comp Debug, Rollover Debug Log) visually and functionally separated from everyday settings via a distinct "⚠ Advanced" warning box
- Recipes vs Meals naming confusion addressed with cross-referencing subtitles in each section, rather than a rename
- Fixed a focus-destroying bug where the reorder system's own render logic was silently kicking users out of text inputs (search box, Daily Steps, custom water amount) on every keystroke

## Donation / Fundraising Page

- Story, cover photo, and donation copy finalized for the JustGiving crowdfunding page and app-linked story page
- Subsequently removed personal fundraising link and photo from the app entirely per decision to direct support toward charity rather than personal fundraising

## Known Outstanding Items
- Documentation (this file, README.md, TECHNICAL.md, user-guide.html) needs the above folded in properly
- Garmin data quality comparison against RingConn/Withings not yet completed
- Server auto-restart reliability — occasional manual restart needed, root cause (battery optimization vs boot-script failure) not yet confirmed
# MaxedHealth Changelog

## v3.10.39 — Phase 9 (6 Jul 2026)
- **Added:** Goal change (Lose/Maintain/Gain) now automatically appends a timestamped entry to Weight Phase History. No manual entry needed except for historical backdating.

## v3.10.38 — Phase 9 (6 Jul 2026)
- **Added:** ⭐ Full Summary — dedicated one-tap button in Ask AI generating a comprehensive 9-section health analysis (nutrition, weight phases, ketosis quality, sleep, HRV, activity, best periods, areas to improve, protocol verdict). Phase-aware, condition-specific, nil days excluded.
- **Fixed:** Ask AI section title updated with ⭐ star status indicator.

## v3.10.37 — Phase 9 (6 Jul 2026)
- **Added:** Suggested Targets calculator in Settings → Profile. Calculates personalised TDEE (Mifflin-St Jeor × activity multiplier from real avg step count), phase-adjusted calories, protein (1.8g/kg GBM/Epilepsy, 1.6g/kg otherwise), and fat to fill remaining calories. Condition overlay checks ketogenic ratio for GBM/Epilepsy. "Apply these targets →" button applies in one tap. Recalculates when Settings opens or weight updates.

## v3.10.36 — Phase 9 (6 Jul 2026)
- **Added:** Weight Phase History field in Settings. Log intentional weight phases (loss/maintain/gain) with ISO dates, one per line. Used by all AI reports to correctly interpret weight trends — deliberate loss is never flagged as a concern.
- **Fixed:** `savePhaseHistory()` now calls `renderSuggestedTargets()` after saving.

## v3.10.35 — Phase 9 (6 Jul 2026)
- **Fixed:** Nil nutrition days (<100 kcal) now filtered from Ask AI raw data table, Monthly Summary calculations, and `buildPatientContext`. Gap days reported as "tracking gaps, not zero intake" in AI context.

## v3.10.34 — Phase 9 (6 Jul 2026)
- **Fixed:** Report streak now uses `calcKetosisStreak()` which includes today's logged data. Previously the report showed 0 streak even when today was compliant because today's log wasn't included in the history array.
- **Fixed:** Nil nutrition days excluded from protein misses, fat misses and best carbs calculations in report summary.

## v3.10.33 — Phase 9 (6 Jul 2026)
- **Fixed:** JS syntax error — `const trackedCarbs` declaration placed inside a chained expression, breaking all JavaScript. Node syntax check now run on every build before deploy.

## v3.10.32 — Phase 9 (5–6 Jul 2026)
- **Fixed:** File header comment corrected from stale "v2.1.9 Phase 7" to "v3.10.32 Phase 9". The comment was misleading but the file was always Phase 9.
- **Added:** Offline manual entry fallback — when AI is unreachable (flight mode, no network), a manual kcal/protein/fat/carbs form appears automatically instead of an error.
- **Added:** Weight carry-forward — dashboard shows last known weight when today has no reading, labelled "last known". Never writes to data.
- **Fixed:** Watchdog (`mh_watchdog.sh`) was starting server.py from wrong directory, causing `combined_exists: false`. Fixed `cd` path from `app/maxhealth` to `app`.

## v3.10.31 — Phase 9 (5 Jul 2026)
- **Fixed:** Tesco Double Cream fat=0 bug. Three-layer fix: (1) label-locked values (467kcal/50.5g F/1.5g P/1.6g C per 100g), (2) FAT_FLOOR_DB updated with label-confirmed 50.5g, added lamb/pork/single cream, (3) high-kcal backstop — any item >200kcal with 0g fat has fat back-calculated from `(kcal - protein×4 - carbs×4) ÷ 9`.
- **Fixed:** AI fat prompt updated with label-confirmed Tesco double cream values and explicit rule: never return 0g fat for cream/oil/dairy/nuts/eggs.

## v3.10.30 — Phase 9 (5 Jul 2026)
- **Fixed:** Report summary stats (best carbs, protein misses, fat misses) now exclude days with <100 kcal logged, preventing untracked days from skewing statistics.

## v3.10.29 — Phase 9 (2 Jul 2026)
- **Added:** Inline edit (✏) per component row in meal preview. Tap to edit name and gram amount; macros recalculate live from original per-100g base values. Save updates the preview; Cancel reverts.

## v3.10.28 — Phase 9 (2 Jul 2026)
- **Fixed:** story.html links in app used absolute GitHub Pages URL — now works correctly from both localhost and GitHub Pages.

## v3.10.27 — Phase 9 (2 Jul 2026)
- **Fixed:** story.html link path was `docs/story.html` (non-existent subfolder). Corrected to `story.html`.
- **Fixed:** History render — log entries whose description is a mode word ("standard", "holiday", "occasion") now filtered from display. These ghost entries were created by an old rollover bug.
- **Added:** HOL/OCC badge next to date in history header for holiday/occasion days.

## v3.10.26 — Phase 9 (2 Jul 2026)
- **Fixed:** Ghost mode-word log entries filtered from history display.
- **Added:** Day mode badge (HOL/OCC) in history header.

## v3.10.25 — Phase 9 (5 Jul 2026)
- **Fixed:** Carb zone gaps — dropdown labels now use contiguous ceiling values (≤20g / ≤50g / ≤100g / ≤150g). No gaps between zones.
- **Updated:** `CONDITION_META` protocol labels and carb ceilings hint text to match.

## v3.10.24 — Phase 9 (5 Jul 2026)
- **Fixed:** `carer.html` — title and all brand references corrected to "MaxedHealth". Hardcoded carb ceilings replaced with `data.ceilings` from payload. `generateCarerLink()` now embeds actual ceiling values from localStorage.

## v3.10.23 — Phase 9 (5 Jul 2026)
- **Added:** Condition/Protocol dropdown in Settings → Profile (GBM, Epilepsy, Strict Ketosis, Type 1 Diabetes, Type 2 Diabetes, General Health). All AI reports now adapt framing, evidence categorisation and thresholds to the user's condition.
- **Added:** `CONDITION_META` table with per-condition protocol label, evidence note and report framing.
- **Fixed:** `buildPatientContext` and `patientContextBlock` were hardcoded to GBM gaining phase. Now reads `mh_condition` and `mh_goal`.

## v3.10.22 — Phase 9 (5 Jul 2026)
- **Fixed:** Meal/Label toggle was hardcoded to Label as the active state in HTML despite JS defaulting to Meal.

## v3.10.21 — Phase 9 (4 Jul 2026)
- **Fixed:** Step 0 photo classification prompt was too broad. Tightened to binary yes/no: "does this photo show a printed nutrition panel with actual numbers?" Food on a plate is always MEAL PATH.

## v3.10.20 — Phase 9 (2 Jul 2026)
- **Added:** Delete button (✕) per component row in multi-item meal preview.
- **Added:** Step 0 photo classification — AI classifies photo as label or meal before any other reasoning fires.

## v3.10.19 — Phase 9 (2 Jul 2026)
- **Fixed:** When AI asks a clarification question about an ambiguous photo item, the next user reply is now correctly treated as the answer. Stored as `window._pendingClarification`.
- **Fixed:** Sauce double-counting — when a protein is logged "in sauce/curry", sauce is no longer also added as a separate line item.

## v3.10.18 — Phase 9 (2 Jul 2026)
- **Added:** Termux:Boot boot survival — `start-watchdog.sh` runs `termux-wake-lock` and immediately launches `mh_watchdog.sh` on boot.
- **Fixed:** GitHub Pages → localhost auto-redirect blocked by Chrome LNA policy. Removed dead WebSocket probe. Replaced with one-time toast pointing to localhost:5757 shortcut.
- **Fixed:** setup.sh (v3.2) now auto-installs `termux-api`, detects Termux:Boot/API, prompts only when missing.
- **Added:** `buildPatientContext` + `patientContextBlock` — all three report types receive full patient context.
- **Added:** Meal photo ambiguity rule — flags uncertain items and asks before logging.

## v3.10.17 — Phase 9 (27 Jun 2026)
- **Fixed:** Meal photo prompt — removed directional bias. Added Step 4 plate-weight sanity check.

## v3.10.16 — Phase 9 (27 Jun 2026)
- **Added:** `showLocalhostHint()`, `maybeShowHomeScreenTip()`, `offerLocalSwitchIfAvailable()` for post-LNA localhost shortcut guidance.

## v3.10.15 — Phase 9 (27 Jun 2026)
- **Fixed:** `amazfit.py` now uses `pyzipper.AESZipFile` for AES-encrypted Zepp exports.
- **Added:** `AMAZFIT_EXCLUSIVE` fields always overwrite on re-sync. `fix_amazfit_steps.py` one-off retroactive correction script.

## v3.10.14 — Phase 9 (26 Jun 2026)
- **Added:** Post-onboarding local server switch banner.

## v3.10.13 — Phase 9 (26 Jun 2026)
- **Fixed:** GitHub Pages → localhost redirect (first pass). setup.sh v3.2 Termux:Boot/API auto-detection.

- **Fixed:** GitHub Pages → localhost auto-redirect no longer works due to Chrome's
  Local Network Access (LNA) policy (enforced from Chrome ~142–149), which blocks
  cross-origin fetch/WebSocket requests from public HTTPS pages to localhost.
  Removed the now-dead `tryLocalhostRedirect()` WebSocket probe and the
  `checkServer()` auto-redirect; replaced with a one-time toast pointing users to
  their localhost:5757 shortcut instead.
- **Added:** setup.sh (v3.2) now auto-installs `termux-api`, detects whether
  Termux:Boot and Termux:API are already installed, and prompts for the one-time
  manual install only when missing (links open directly). New boot script
  (`start-watchdog.sh`) holds a wake-lock and launches the watchdog immediately
  on boot, alongside the existing cron-based boot script, to prevent Doze
  suspending background checks overnight.
- **Action required (existing installs):** re-pin your home screen shortcut to
  `http://localhost:5757` directly — the old shortcut pointing at the GitHub
  Pages URL will no longer auto-jump to local mode.

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
