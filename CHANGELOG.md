# MaxedHealth Changelog

## v3.10.23 — Phase 9 (5 Jul 2026)
- **Added:** Condition/Protocol dropdown in Settings → Profile (GBM, Epilepsy, Strict Ketosis, Type 1 Diabetes, Type 2 Diabetes, General Health). All AI reports now adapt framing, evidence categorisation and thresholds to the user's actual condition — not hardcoded GBM assumptions.
- **Added:** `CONDITION_META` table with per-condition protocol label, evidence note, and carb concern framing. `patientContextBlock()` builds appropriate context for each condition.
- **Fixed:** `buildPatientContext` and `patientContextBlock` were hardcoded to GBM gaining phase. Now reads `mh_condition` and `mh_goal` from localStorage and generates condition-appropriate prompts.

## v3.10.22 — Phase 9 (5 Jul 2026)
- **Fixed:** Meal/Label toggle was hardcoded to Label as the active state in HTML despite JS defaulting to Meal. Corrected to Meal as default — Label requires explicit user selection.

## v3.10.21 — Phase 9 (4 Jul 2026)
- **Fixed:** Step 0 photo classification prompt was too broad — meal photos were being misclassified as nutrition labels. Tightened to binary yes/no question: "does this photo show a printed nutrition panel with actual numbers in table/list format?" Added explicit rule: food on a plate is always MEAL PATH.

## v3.10.20 — Phase 9 (2 Jul 2026)
- **Added:** Delete button (✕) per component row in multi-item meal preview. Tap to remove an individual ingredient/item from the "Ready to Log" list before logging. Cancels cleanly if all items are removed.
- **Added:** Step 0 photo classification — AI now explicitly classifies photo as label or meal before any other reasoning fires, routing to the correct analysis path.

## v3.10.19 — Phase 9 (2 Jul 2026)
- **Fixed:** When AI asks a clarification question about an ambiguous photo item (e.g. "pasta or vegetables?"), the next user reply is now correctly treated as the answer to that question rather than a fresh log entry. Stored as `window._pendingClarification` with image + AI question; replayed as full context on next send.
- **Fixed:** Sauce double-counting — when a protein is logged "in sauce/curry", sauce is no longer also added as a separate line item.

## v3.10.18 — Phase 9 (2 Jul 2026)
- **Added:** Termux:Boot boot survival — `start-watchdog.sh` runs `termux-wake-lock` and immediately launches `mh_watchdog.sh` on boot, preventing Android Doze from suspending the server between cron ticks.
- **Fixed:** GitHub Pages → localhost auto-redirect blocked by Chrome's Local Network Access (LNA) policy (enforced ~Chrome 142–149). Removed dead WebSocket probe (`tryLocalhostRedirect`) and silent fetch redirect. Replaced with one-time toast pointing to localhost:5757 shortcut.
- **Fixed:** setup.sh (v3.2) now auto-installs `termux-api`, detects Termux:Boot/API via `pm list packages`, and prompts only when missing (opens F-Droid page directly).
- **Added:** `buildPatientContext` + `patientContextBlock` shared functions — all three report types (Monthly Summary, Ask AI, Full Summary) now receive full patient context: day-type aware carb compliance, weight target, gaining phase, activity factors.
- **Fixed:** Monthly summary section 2 now evaluates calorie adequacy for the gaining phase, not just protein.
- **Fixed:** A-Z library nav now draws letters from ingredients only, excluding meals.
- **Added:** Meal photo ambiguity rule — if any component could plausibly be two different foods (pasta vs cooked vegetables, rice vs cauliflower etc.), AI flags it and asks before logging. Prevents phantom carb entries.

## v3.10.17 — Phase 9 (27 Jun 2026)
- **Added:** Meal photo Step 4 calibration sanity check — sum of component weights verified against expected plate size before calculating macros.
- **Fixed:** Meal photo prompt removed directional bias ("estimate higher"). Replaced with neutral plate-weight anchor.

## v3.10.16 — Phase 9 (27 Jun 2026)
- **Added:** `showLocalhostHint()` — one-time per-session toast when local server detected but user still on public GitHub Pages URL.
- **Added:** `maybeShowHomeScreenTip()` — one-time persistent localStorage reminder to pin localhost:5757 shortcut when landing on localhost for the first time.
- **Added:** `offerLocalSwitchIfAvailable()` — post-onboarding banner offering one-tap switch to localhost if local server is running and user is still on public URL. User-gesture navigation so Chrome LNA permission prompt fires correctly.

## v3.10.15 — Phase 9 (27 Jun 2026)
- **Fixed:** `amazfit.py` now uses `pyzipper.AESZipFile` for AES-encrypted Zepp exports. stdlib `zipfile` cannot decrypt these even with the correct password ("That compression method is not supported").
- **Added:** `AMAZFIT_EXCLUSIVE` field set (`steps`, `distance_m`, `calories_active`) — these fields always overwrite on re-sync rather than fill-only, so partial/stale daily totals from early syncs get corrected by later exports.
- **Added:** `fix_amazfit_steps.py` — one-off retroactive correction script. Reads latest Zepp export, identifies steps/distance/calories discrepancies in combined.csv, previews all changes, applies after y/N confirmation. Backup written automatically.

## v3.10.14 — Phase 9 (26 Jun 2026)
- **Added:** `offerLocalSwitchIfAvailable()` post-onboarding prompt.
- **Fixed:** `start-watchdog.sh` boot script filename (previously saved without `.sh` extension in some environments).

## v3.10.13 — Phase 9 (26 Jun 2026)
- **Fixed:** GitHub Pages → localhost auto-redirect (first pass — WebSocket probe removed; full LNA fix completed in v3.10.18).
- **Added:** setup.sh v3.2 — Termux:Boot/API auto-detection.

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
