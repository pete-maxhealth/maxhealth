**Home checklist (Premium, licensing, GitHub, Android Studio, prices): see `premium/HOME_CHECKLIST.md`.**

# MaxedHealth backlog (bookmarked 11 Oct 2026)

Raised by Pete Spence while simplifying. Tick off as released (see CHANGELOG.md).

## Data tab (Settings → Data)
- [x] v3.10.949 One Export / Import card: Select all / Unselect all, one zip or separate files, share sheet.
- [x] v3.10.949 Duplicate "Export All Data" removed (the reminder banners still offer it).
- [x] v3.10.949 Data Management and Nutrition History import/backup folded into that card.
- [x] v3.10.949 Restore from backup is its own card (server daily backups, or a backup file).
- [x] v3.10.949 Advanced / Manual Pipeline is a hideable section inside Sync Wearable Data.
- [x] v3.10.949 Data Preview & Validator = coverage across history; now inside Missing Data & Coverage.
- [x] v3.10.951 Filter pill: just "Filter", closes itself after a choice, Open all / Close all never touch hidden cards.

## Layout, packs and nudges (v3.10.967 - 975)
- [x] v3.10.967 Every Today card folds to a one-line bar; v3.10.968 live values on bars and ↺ Default.
- [x] v3.10.971 Starter packs carry a screen layout; Default returns to the pack layout.
- [x] v3.10.972 First-run "What would you like to start with?" step.
- [x] v3.10.973-974 One Filter panel holding chips and Hidden pills; toolbar always first; one pill size.
- [x] v3.10.975 Optional nudges; epilepsy, type 2 diabetes and migraine starter packs.
- [ ] **Launcher plan (needs the laptop; not reachable from the cloud session on 12 Oct).** The launcher source is not in this repo.
  1. *Back up first:* zip `C:\Users\jill.spence\AndroidStudioProjects\MaxedHealth` (leave out `build/` and `.gradle/`), copy the 2 Oct APK, **and copy `%USERPROFILE%\.android\debug.keystore`**: an update only installs over an existing app if it is signed with the same key, so losing that file means everyone has to uninstall first. Keep a copy off the laptop (cloud drive or USB).
  2. *Health Connect step doubling (inference, to confirm in code):* `HealthConnectBridge.kt` (~lines 194-231) probably sums raw `StepsRecord`s, so phone and watch both count. Switch steps to `HealthConnectClient.aggregate(AggregateRequest(setOf(StepsRecord.COUNT_TOTAL), TimeRangeFilter.between(start, end)))`, which de-duplicates using the user's Health Connect app priority (Zepp above phone). Check against Zepp's own number for the same day. In the same change, export the last 2-3 days, not just today.
  3. *Moving the APK off public GitHub:* host `version.json` and the APK on your own site (the GoDaddy host), change `versionCheckUrl` (and the download URL) in launcher 1.6, build, upload. Keep the GitHub copy until installed launchers are on 1.6+, then replace it with a one-line note. Deleting the file does not remove it from git history (old commits stay downloadable); only a history rewrite (`git filter-repo` plus a force push, then re-cloning both phones) does, which is probably not worth it. Check the APK holds no secrets first (`apkanalyzer` or `strings`); it is debug-signed.
- [x] v3.10.998 Score a past day (14 days).
- [x] v3.10.997 Header fit at large text, localised date, language card translated.
- [x] v3.10.996 Food-less days keep scores/tags; analyst prompt gets scores/tags/treatments. Idea: back-fill a past day's How-are-you scores from History.
- [x] v3.10.995 AI 'Translate this screen' (✨) with consent, cached per phrase.
- [x] v3.10.994 SVG flags + header language button; number-aware translation; ~240 more strings. Still English by design: Formulas reference, device hints. Next: native-speaker review; crawl more states (modals, toasts) for leftovers.
- [x] v3.10.993 Plan card buttons standardised, fat goal in plan totals. Full suite green at 992.
- [x] v3.10.992 Flags, report profiles on tags/conditions, planner fasting heads-up. Dropped: demo applying pack layout (cosmetic, restore risk).
- [x] v3.10.991 Language packs (en/es/de/fr/tr), machine-assisted. Next: native-speaker + clinician review, translate remaining dynamic strings, report profiles on tags/conditions.
- [x] v3.10.990 Six new demo personas with day tags. Idea: demo applies pack layout + labels. Next: report profiles on tags/conditions, language packs.
- [x] v3.10.989 Tag manager. Next: report profiles on tags/conditions, demo personas for newer packs, language packs.
- [x] v3.10.988 Condition labels/filter + Add another focus. Next: tag manager, report profiles on tags/conditions, demo personas for newer packs, language packs.
- [x] v3.10.987 Tags as before/after anchors + Compare Metrics tag pills. Next: condition labels + filter, Add another focus, tag manager, report profiles on tags; then more demo personas; then language packs.
- [x] v3.10.986 Treatment tags from own list + duplicate strip fix. Idea: per-pack occasion chip sets; demo personas for the newer packs.
- [x] v3.10.985 Meal planner. Ideas: fasting-window warning, fill-the-gap suggestions for the plan. Next: language packs (EN default, ES, DE, FR, TR).
- [x] v3.10.984 Seventeen more packs + disclaimer on every pack screen. Idea: embed all packs for offline focus switching; clinician review of symptom lists.
- [x] v3.10.983 Type 3c diabetes pack.
- [x] v3.10.982 Change my focus + muscle growth pack. Idea: embed all packs for offline focus switching.
- [x] v3.10.981 Library chip icons; Food Library category filter.
- [x] v3.10.980 Close all on Trends folds the metric cards.
- [x] v3.10.979 Library 👁 hide per section (uniform with the other pages).
- [x] v3.10.978 Mark app errors as fixed on System health.
- [x] v3.10.977 Filter toolbar on History/Library/Customise; strict keto, type 1 diabetes, cluster headache packs; test plan + p98/p99.
- [x] v3.10.976 Layout by voice; AI check no longer sends guessed grams; half-written page guard.
- [ ] Filter row on Supplements, Log, History, Library and Customise (they have no hide/reorder system today).
- [ ] Starter packs per remaining condition (strict keto, type 1 diabetes, cluster headache).

## Ideas register (compiled 16 Oct 2026 from this phase, the repo, memory and the earlier phase chats)

Built in the Move / Sleep / Statistics phase (v3.10.1071 - 1081), see CHANGELOG:
- [x] Live Health Connect steps trump planned steps; exercise planner (Plan ahead) and In/Out strip.
- [x] Catalogue of 55+ known exercises (indoor/outdoor, racket, water...), per-kind watch calibration, scroll-hold fix on Resistance.
- [x] Exercise and sleep as full citizens: History, chart, Reports, AI, summaries, clinician view, carer page, backup.
- [x] What seems to move what (Early Stage): habits against next-night sleep, HRV, symptoms; short nights against the same day's eating and movement; treatment sessions as a habit.
- [x] Statistics tab: build, save, group, search, hide, reorder, library, colours, compare with previous period, CSV, copy, export/import of definitions, pin to Today, share into summaries/clinician/AI.
- [x] Speed-based MET (2011 Compendium) and exercise energy net of resting; weather location follows GPS.

Open, this phase:
- [ ] Re-record the tour videos with Move, Sleep and Statistics chapters (and the "general health and muscle gain" framing).
- [x] Story page and docs/changelog.html updated 16 Oct.
- [x] DROPPED (Pete, 4 Nov): phone checks for v3.10.1081; overtaken by daily use on the phone.
- [x] v1083 Drag-reorder on Statistics; light-theme checked for the Statistics tab and the sleep and outcomes reports (high-contrast theme not checked).
- [x] v1082/1084 Colour and chart type per statistic and per Trends chart.
- [x] v1085 What-moves-what: bedtime, next-morning weight change, treatment-session windows. (Whole treatment cycles as a unit are not modelled.)
- [ ] Remaining personas through `alex_deep.py`. (Exported PDFs, reminders, language files offline and device import were already covered by p190, v3.10.1086; this line was stale, corrected 30 Oct 2026.)

Older ideas, found in earlier phase chats and NOT confirmed built (check the code before starting):
- [ ] Watch companion (square and round layouts): quick water / supplement / ketosis status, a daily touchpoint that drives people into the app.
- [x] (already in code, 16 Oct) Meal suggestions: recipe-aware (use saved recipes), avoid repeating recent meals, "nearly there" mode for small gaps, "save this combo as a recipe?" (grep shows some of these may exist: verify).
- [ ] Micronutrients: iron, potassium and magnesium are tracked. Vitamin D and omega-3 left out: no trustworthy food data source to fill them.
- [x] Voice logging exists on the main log (🎤 button) as well as add-food, water and batch library build.
- [ ] Elevation from Zepp per-activity files (needs per-activity parsing).
- [ ] Vascular age: needs PWV readings, which stopped in June 2025; revisit only if measuring resumes.
- [ ] Decided against: protocol adherence view (risk of confusion), Simple/Full view switch.

Business and launch (from memory, see `premium/HOME_CHECKLIST.md`):
- [ ] Register-interest page live on pspence.co.uk before any ad links to it; Premium "coming soon" in demo personas, Ko-fi gallery and videos.
- [ ] Move the APK off public GitHub, secure Premium code; launcher plan above.
- [x] Worker already has a per-device starter allowance, licence tokens, per-IP daily cap, global monthly cap, model allowlist and token cap (worker.js). Residual: a fresh device id gets a new 60-call starter, bounded by the IP and monthly caps. Needs checking that the DEPLOYED worker matches this file (home job).

## Other
- [x] v3.10.950 Incidental Steps Baseline automatic; Activity Level reads real weekly steps.
- [x] Strength Log CSV import merges by (date, exercise) (checked in code 16 Oct).

## Deferred until home
- ICO fee check, launcher items. (GoDaddy upload of premium-site/ is OBSOLETE: the licence service runs on the Cloudflare Worker since v3.10.1249; the GoDaddy plan is the website builder only.)

## Pattern signals (`pattern_detector.py`, `/pattern-signals`): tested 13 Oct; v2 rewrite fixes the issues below (test p135)
Original findings, all addressed in v2 (own-baseline comparisons, whole-history meals, no universal grades):
Works mechanically, but the app never calls it and several outputs are not trustworthy enough to sell:
- Meal windows use only today's log, despite "learns from 2-4 days".
- "Regular exercise detected" fires if one day is 30% above the average (one 9,000-step day in a week of ~6,000).
- HRV "Excellent / Good / Fair / Low" uses fixed millisecond cut-offs; HRV is personal and age-dependent, so a label like that can mislead.
- Sleep "quality" is graded from the wearable's deep-sleep percentage alone; regularity uses duration spread, not bedtime.
- No tests. The app's own SPC early-warning checks already cover the useful ground.
v2 status: done and promoted (card on Trends, demo sample, Premium page; tests p135, p136). Still wanted: a real-phone check with a few days of real data.

## From the 20 Oct 2026 cupboard session
- [ ] Retire the old CSV import screen (`mhCsvPlan`, view `csvimport`, `mhShopCsvPick`) now that Import covers it; move the CSV-only checks in p213 and p223 onto the Import screen first. Nothing in the UI opens it any more.
- [x] v3.10.1131 Fridge life by type of food, typed by Pete (rules by name words). Was: Fridge life of 3 days for everything makes every fridge food "use soon". Consider letting Pete set a default per category himself (never a built-in guess).
- [ ] Custom storage places ("garage freezer", "utility") if three places (fridge, freezer, cupboard) prove too few.
- [ ] Videos: short tour "idea to plate", 45 s knockout reel, then the clip series (see scratchpad storyboard); record the Import scene last, it changed.
- [x] Whole-journey tests, v3.10.1248: p358 (fresh install, a week, backup, restore on a second device, switch off and on) and p359 (real-life mess). Still to build from his real-phone checklist: a longer shopping week with receipts and use-by dates.
- [ ] Reservations-switch test gap; Surprise sweet/savoury pair with a real web search untested; five stale branches (feat/quick-list, quick-list2, shopping-list, stock-suggest, stock-switch, move-tab, v1095-language-button, fix/p61-tally-link) to delete only with Pete's OK.
- [ ] Video series (Pete: "I want everything", each clip hooks to the others, one every 2-3 days, short tour first as the hub): everyday user; treatment/symptoms with an invented person; plan/history/library; monitoring/analysis; connected; how safe is my data; accuracy settings tour; Make it yours; Simple please; stock clips (cupboard, receipts, off switch); meals by time of day; history and analysis with Proven/Early Stage/Speculative; "how it differs from a chatbot" (no competitors named, only on-screen claims). Vertical 1080x1920, captions only, hook on a moving screen, no web address burnt in (end card "Link in the description"), no Premium page link (Tally register-interest only), keep "Sample data shown. Not medical advice." Per-clip upload pack: title, description, tags, hashtags, SRT, thumbnail, pinned comment. promo.py line 35 burns in the GitHub URL: change.
- [ ] Generated voice-over: set up a GitHub-hosted voice (Hugging Face is blocked, pip has no piper-tts/kokoro-onnx), send Pete a short sample for approval before touching any video.
- [ ] Other open: optional pspence.co.uk redirect to GitHub Pages (GoDaddy is no longer needed for hosting), monthly competitor sweep on the 1st, Premium pricing decision, re-record tours with Move/Sleep/Statistics chapters.

- [ ] (v3.10.1125) Guide and README: mention that a recipe leaves off foods already in the cupboards.
- [x] v3.10.1246 fixed (fruit words added, pear/peach/peanut moved ahead of 'pea', spear guard). Left for later: other everyday foods that may still fall to Other (check the Library 'Other' chip). Was: The category sorter files Apple, Banana, Grape, Lemon as Other (and Pears as vegetable). It is global (aisles, nutrition groups), so extend CATEGORY_MAP deliberately and run the full sweep. Found 21 Oct 2026 while adding section rules for fridge life.

## Data and Reports tidy-up (raised by Pete 27 Oct 2026; agreed plan, do after v3.10.1226)
- [x] (v3.10.1303, chips + default order; no chooser card, see CHANGELOG) Data tab: group by intent ("Bring data in", "Move or back up my data", "Check it's complete"). One "Move & back up" card with a "what do you want to do?" chooser holding QR, export/import, setup share, starter packs and restore. Fold the wearable cards (Sync, History, Advanced pipeline, Add device) into one.
- [x] DONE in v3.10.1230 (checked 4 Nov): Reports: merge Sleep into Sleep & Ketosis; merge Treatment Analysis with Sessions; one "Ask about this period" card (Ask AI + Query Builder); rename Export & Share to "Make a report to hand to someone" and point to Data for raw files.
- [ ] Keep show/hide and reorder on every merged card, long text behind "?", rendered side-by-side screenshot check, targeted persona tests (no sweep unless asked).

## Pre-existing test failures found 28 Oct 2026 (identical on v3.10.1225, not caused by 1226)
- [x] p42 (Clear-Site-Data header guard): retired 28 Oct 2026 at Pete's call; it hung every run. The warning comment in server.py (around line 1801) stays. Do not add Clear-Site-Data back without testing on the phone.
- [x] p63, p70 (fasting): v3.10.1246 pinned to UTC. Cause was the UK clock change on 25 Oct (that night is 13h of real fasting); the app counts real elapsed hours and is right.
- [x] p306, p307 (ate-out history): fixed 28 Oct 2026. The tests hard-coded 20/10/26, which fell outside History's default period; they now use a day relative to today. No app bug.

## Steps: plan vs actual in one box (Pete, 28 Oct 2026) - PARKED, NOT NEEDED (Pete, 31 Oct 2026)
- Pete's decision 31 Oct: the planner works as it is. He books food and exercise in the morning as a forecast of how the day will play out, then deletes or adjusts portions and adds a snack before the end of the day to close the macros; his weight stability shows it works. Do NOT build the box or change how plans affect the fast timer unless he asks. The notes below are kept only in case he returns to it.
- [ ] One Daily Steps box that knows if the number is a plan (intention) or an actual. A plan is replaced by the first device figure even if lower; an actual stays a floor (today's rule). Plan ahead becomes how a plan is entered. Card says "planned, waiting for your watch". Steps become the one metric where a device beats a manual entry; everything else keeps manual wins. Whole-day test: plan, device lower, device higher, midnight, reload, History.
- [ ] No in-app step counter (a web page cannot count in the background). Phone steps come from Health Connect via the launcher; fix the phone+watch double count there (needs the laptop).

## Moving off GitHub: CLOSED 31 Oct 2026 (Pete): only the Premium payload and the APK needed to leave public GitHub (done, Cloudflare Worker). The free app, `lang/`, `starter_packs/`, docs and README stay on GitHub. v3.10.1251 made starter packs load from the app's own copy first (offline works, testable offline). The items below are kept as history; do not build them unless that decision changes. (Pete and Jill, 29 Oct 2026). v3.10.1246 put the app's own addresses in one `MH_HOME` block; what is left
- [x] SUPERSEDED (Pete, 4 Nov): the free app, `starter_packs/`, `lang/` and README stay on GitHub, so nothing needs hosting elsewhere or editing in `MH_HOME`. (Original note: host them as plain files and edit `MH_HOME.raw`.)
- [x] SUPERSEDED (Pete, 4 Nov): the free app stays on GitHub Pages (pete-maxhealth.github.io), so story page, docs, guide, privacy pages and carer.html stay where they are.
- [x] SUPERSEDED (Pete, 4 Nov): scripts and docs that name GitHub for the free app are correct as they are. Only the Premium payload and the APK left GitHub (done).
- [x] **Launcher (laptop):** done 30 Oct. Launcher 1.6.1 (build 17, source `MaxedHealth-launcher-1.6.1-source.zip`, not in this repo) reads `version.json` from the Cloudflare licence Worker; its banner opens `/launcher/get` (paste key, APK downloads). Proven on Pete's phone, update banner, key, download. Worker, KV and secrets are set up (see LICENCE_WORKER_SETUP.md; the Cloudflare dashboard route replaced wrangler).
- [x] **Licence address:** app v3.10.1249 sends keys/trial to the Worker (`MH_LICENCE_URL`), not GoDaddy.
- [x] p131 (split_premium): fixed 31 Oct 2026. Cause: three new files (`LICENCE_WORKER_SETUP.md`, `licence-worker.js`, `wrangler.licence.toml`) were unclassified, so the split stopped before writing the free tree. They are now PRIVATE in `tools/split_premium.py` (not published). Check that is what you want for `licence-worker.js`.
- [x] 30 Oct: `apk/` removed from the repo tree (README and TECHNICAL.md updated). The 1.5.1 and older APKs stay in git history until history is rewritten. Release asset `launcher-v1.0.0` (MaxedHealth-launcher-v1.0.0.apk) still public: Pete to delete on GitHub.
- [x] 31 Oct: signed release build done. Launcher 1.7.0 (build 18), release key `maxedhealth-release.jks` (Pete's laptop, backed up by him), installed and checked on Pete's phone, stored on the Worker (6,781,030 bytes, sha256 ceb02080...abf35) with version.json = 18. Phones on the debug-signed 1.6.x must uninstall the launcher once before installing it. Project source: MaxedHealth-launcher-1.7.0-source.zip (not in this repo; includes RELEASE_BUILD.md).
- [x] DONE (Pete, 4 Nov: "we did this yesterday when we brought the launcher up to 1.7.0"): AI limits adjustable from Termux; new worker.js pasted and ADMIN_SECRET added on the maxhealth-ai Worker.
- [ ] **GO-LIVE TRIGGER (Pete, 31 Oct 2026): go live with Premium when 50 people have registered interest on the Tally form.** Until then Premium stays "coming soon" and nothing public links to the Premium page. First step on hitting 50: move Cloudflare to Workers Paid (below), then publish the Premium page, then link it from ads and pages.
- [x] **DONE 2 Nov 2026 (Pete): Cloudflare account is on Workers Paid.** The 1,000-writes-a-day ceiling no longer applies, so a busy day can no longer switch AI off for everyone. Original note: move the Cloudflare account to Workers Paid (about $5/month) before any ad goes live or other paying users are added.** Free plan = 1,000 KV writes a day for the whole account (both Workers). worker.js now fails closed with a clear 503 if KV is unavailable (31 Oct), but that would still stop the AI for everyone. Add $5/month to the cost model.
- [ ] **Still to do for the APK (updated 4 Nov):** the GitHub release `launcher-v1.0.0` is GONE (checked 4 Nov: the only release left is MaxedHealth_v3_10_552 with no files; a plain git tag `launcher-v1.0.0` remains, harmless, delete only if wanted); git history: NO rewrite needed (Pete, 4 Nov: the old APKs were checked that morning and are no danger; the removal commits of 08:45 on 4 Nov took `apk/` out of every branch; one old debug-build blob remains in old commits). Jill's phone is DONE (Pete, 4 Nov). Check the KV write budget is no longer a concern now the account is on Workers Paid (2 Nov). Older notes kept in git history of this file.
- [x] (v3.10.1250, 31 Oct) **Bug reports:** with no GitHub issues, `MH_HOME.issues` = '' makes the report copy its text; the settings card text still says "Opens a GitHub report", so reword it at the same time.
- [x] SUPERSEDED (Pete, 4 Nov): ads, videos, YouTube descriptions and the Ko-fi gallery link to the free app on github.io, which is staying, so no link changes are needed. The only link rule that matters: nothing public links to the Premium page until it is live (Tally register-interest link until then).

## Nightly sweep, night of 29-30 Oct 2026 (triaged 30 Oct)
- [x] p325: stale test, fixed. The Move tab now has planCard (the exercise planner) after activityCard; the expected order list in the test was missing it. Not an app bug.
- [x] p308: made steadier 31 Oct 2026 (test now waits for fonts and the screen to finish drawing before measuring); passes. Was: intermittent. Failed in the sweep and once on a lone run straight after another test, then passed twice. The odd persona reported Arial instead of Space Mono, so a Reports button was measured before it was styled or redrawn. Leave for now; if it keeps appearing, make the test wait for Reports to settle.

- [x] (v3.10.1250, 31 Oct; blank counts as 0, a typed figure is kept) Manual "Missed day" has no fat box and stores fat as 0 (not "not entered"). Decide whether to add the box, or store nothing.

- [x] p26 (more screens): failed once in the 30-31 Oct sweep ("free-text question never reached the AI"), passed alone 4 times. Test waited a fixed 3s; now waits up to 10s. Not an app bug.

## Known gaps pinned by tests (p369, nutrient x route grid)
- [x] (DONE v3.10.1288) Polyols has no box in Manual entry or the Missed day form (it travels through copy/paste, the Paste form, planned meals, recipes and the AI/library route). The Save-to-library dialog also has no Polyols box. p369 lists these in EXPECTED_GAPS; closing one makes p369 fail until the list is updated.
- Test p370 types into every box that saves itself (35 today) and checks each keeps its value after the sync round trip and a reload; settingKcalTarget rejects an implausible 53 kcal by design.

## From the 3-4 Nov 2026 session
- [x] v3.10.1260-1267 (4 Nov): cupboard sections stay put; ON LIST tap takes an item off; own default shop; open/shut state kept everywhere; trolley on every cupboard food and on Filtered foods; wrapped cupboard rows; qty -/+ on every list row; Possible duplicates in My cupboards. Full sweep green at 1267 (377 pass).
- [x] 4 Nov: YouTube "Start here" playlist rebuilt (3 public 3 Nov videos; 10 deleted placeholders and 3 old entries removed). Old 29 Oct "What shall I eat?" set Private. Other 9 playlists checked: no deleted or private entries. Facebook post tested by Pete.
- [x] (DONE v3.10.1268-1269) **Duplicate check rethink (Pete, 4 Nov).** Today the Possible duplicates tile only appears when a pair exists, only compares cupboard foods with each other, and needs near-identical words. Adds that match a Filtered (held) item do nothing and say nothing. Plan: one shared "does this already exist?" check on every add route (cupboard food, non-food, shopping list, receipt), searching cupboards, list, Filtered and library with fuzzy wording; say where the match is; offer use-existing (bringing it back off Filtered) or add anyway; make the tile always visible ("none found"). One persona test across all routes.
- [ ] **When you eat (Pete, 4 Nov), step 1:** Statistics card showing protein, fat and carbs by time of day and protein spread per meal, from logged meal times (ignore backfilled entries). Show/hide, reorder, standard date range, "?" for long text.
- [ ] **Timing coach (step 2):** goal-based guidance (muscle gain, conditions) using age, sex, weight, goal and the step-1 data; every suggestion labelled Proven / Early Stage / Speculative; a suggestion, never a target; optional AI commentary and a version for third parties.
- [~] **Clinician/carer view and nutrition (Pete, 4 Nov) - first slice DONE v3.10.1277 (choose what a link shows, roles as starting points, time of day, meals, treatment sessions). Supplements item DONE v3.10.1287. Still open: preview of the carer page before sending, the clinician report (Full Report Package) following the same choices.** Original note: the shared view is totals only, no food log details, by design. Consider an opt-in section (macro totals plus timing summary, no food names). Pete's steer (4 Nov): what they see depends on what the clinician does. Diabetes: foods and carbs by time of day. Oncology: intake around treatment sessions and supplements. Build on Report Profiles with a per-role preset of sections, preview before sharing, nothing shared by default. DECIDED (Pete, 4 Nov): the user governs what is shared, in Settings; it is not our call. Presets are only starting points the user can change.
- [ ] Videos still wanted: a short clip on typing part of a name (like "pep" or "nick") and picking from the library; more low-typing demos (Pete's 3 Nov priority).
- [ ] Meal-timing series (v3.10.1278) are Compare Metrics overlays only. Trends card DONE v3.10.1282. Still to check: demo-persona coverage, videos.
- [ ] Timing features (v3.10.1277 to 1285): demos, user guide and search are done. Still to do: a tour floor and a short or two (When you eat card with the adviser; choosing what a carer sees), playlist entries, then set any replaced versions Private.

- Recipe steps follow ingredients (v3.10.1286): not yet covered - the AI recipe bubble method text, placeholder resolution and fuzzy re-match do not rewrite steps; tour floor/clip for this feature still to do.

- Videos (4 Nov, evening): DONE. Three clips approved, uploaded and published Public: c_meal_times https://youtube.com/shorts/Rf_cX_wKyBQ (playlist Insights), c_share_choices https://youtube.com/shorts/h3dAIhwTWmM (Health and sharing), c_recipe_follows https://youtube.com/shorts/goEEw4c2MJ4 (Recipes and cooking). Pinned comment on each (links the other clips and the app). Scripts in ytbuild. Still to do: a tour floor for timing, sharing and recipe features; set any replaced version Private (none replaced by these three).
- [x] Share-with role row no longer shows Oncology team on a standard profile (v3.10.1292, 5 Nov); one shared check (mhOncContext) with the adviser chips; p398. Diabetes team still shows for everyone (generic role, left as is). Summary line still says "treatment sessions" for everyone (left as is).
- [x] Import "Create new" goes down the Log routes (search online, AI, barcode) with typing last; saves to library only and returns to the list (v3.10.1293, 5 Nov); p399. Label photo (📸 Read a label) and the scanner message toast added in v3.10.1294. Still to test on the phone: real barcode scan and real label photo from the import.
- [x] Adding part of an import no longer discards the rest (v3.10.1296, 5 Nov); p400.
- [x] Undo for an import (v3.10.1297, 5 Nov); p401. Bulk 'remove all non-nutritional items' in My cupboards done in v3.10.1302 (p407).
- [x] Full tour v5 live (5 Nov, youtu.be/AlyKWSBYoGI, 1:14:35, Public, description with 70 YouTube-safe chapters: every chapter >=10 s apart, so title cards 2-7 s ahead of their first clip are dropped; file MaxedHealth_full_tour_v5_youtube_chapters.txt). Old v4 tour (1Pz6iZaAgA0) set to Private, not deleted. v4 was in no playlists, so v5 is in none. Custom thumbnail not set (thumb_full_tour.png exists); chapters/title/description set by hand in Studio.
- [x] Sleep overstated (v3.10.1291, 5 Nov): launcher <=1.7.0 sent time-in-bed as sleep (6h29 shown as 7h42, efficiency 100%). Pipeline guard in extractors/health_connect.py; p397. Launcher 1.7.1 (versionCode 19) built and release-signed 6 Nov with a NEW key (cert CN=Pete Spence, valid to 2051; old maxedhealth-release.jks passwords were not found and that key is kept only in case they turn up). Installed on Pete's phone by uninstall + reinstall (launcher only; Health Connect permissions re-granted). Old nights keep the old figure. Open: confirm a new night's sleep total on the phone; do the same uninstall/reinstall on Jill's phone; copy the new .jks off the laptop with both passwords in the password manager.
- [x] Order-page PDF import fixed (v3.10.1290, 5 Nov): headings no longer become items, "N x" stripped. Seen rendered on Pete's real Asda PDF (not committed: has address/order no.). Full sweep not re-run.
- [x] Docs brought up to v3.10.1289 (5 Nov): public changelog pages (new 1257-1289 block), README, user guide (duplicate check, polyols boxes, oncology adviser wording). Premium full guide gets the adviser wording only; it has no shopping section. Still to do: tour floor for timing, sharing, recipes and the duplicate check (the three published shorts become its clips).

## PC browser use (Pete, 5 Nov)
- [ ] Notice for PC/browser users: data stays in that browser, backups and security of the device are the user's own responsibility (plain wording, in Settings and the user guide).
- [ ] Watch/sleep/activity data on a PC: a CSV import and export routine (same shape both ways) so people can add data by hand or move it by downloads; no launcher or pipeline needed. Check what the app already imports first; this is NOT the old shopping CSV screen listed for retirement above.
- [x] Desktop layout, step 1 (v3.10.1306, 6 Nov): 880 px centred column from 900 px up, phones untouched (p410). Still to do: look at every sub-tab, picker and pop-up at desktop width; a two-pane layout is optional later.
- [ ] Camera features on desktop: left as they are (best effort, not our problem); say so in the guide.
- [ ] PC: default folder paths configurable (inbox, backups, exports), with sensible per-platform defaults.
- [ ] PC: anything that does not apply on a PC (launcher, Health Connect, Termux, camera-only features) is hidden or marked "phone only" with a "?" explaining why.
- [ ] Carer/clinician share defaults (6 Nov check, Claude): a fresh install shares totals, weight, exercise minutes and sleep by default once a link is made; time of day, meals and food names, treatment sessions and supplements are OFF (p386, p398 pass). If "nothing shared by default" should cover weight/exercise/sleep too, that is a one-line default change plus the text on the share card. Pete's call.
- [ ] Retiring the old CSV import screen is bigger than it reads: p213, p223, p233 and p385 test things only that screen has (Accept all suggestions, remembered answers, the Check this / Matched / New food badge, the "already have" note on CSV rows). Each needs an Import-screen equivalent built, not just a test moved. The pure matching passes (mhVariantMatch, mhClassify) stay either way. Left alone until you say it is worth it.
- [x] Long text behind "?" (6 Nov, v3.10.1301): all 23 audit items done (p406). Left as they are, on purpose: formula lines in Settings → Formulas, two Trends insight sentences, supplement "Edit / On" listed once per period. Seven explainers had no translation before and still have none (es de fr tr pt it pl nl).
- [ ] p405 audit tuning: the "Log vs History log tab are 100% the same" item is the History sub-tab button opening the Log screen (test artefact); the two Trends insight sentences could take a "?" if you want them hidden too.
- [x] PC audit (6 Nov, Claude): opened the demo at 1440x900 in desktop Chromium. It runs with no page errors, but shows as one centred 480 px phone column with empty margins either side, so the desktop layout item above is real work, not a tweak. Browser features present in desktop Chromium: camera/getUserMedia, speech synthesis, speech recognition, vibrate. Missing: Web Share and BarcodeDetector, so any barcode or share route needs a PC fallback (a file or paste route). Screens not yet checked at desktop width: the Insights/Settings sub-tabs (my probe only reached Today), pickers and modals, the Library tab.
- [ ] PC: persona tests at desktop size (wide viewport, mouse and keyboard, no touch), including the CSV routine and configurable paths.
- [ ] PC: support by donations (a donate link on its own page; the no-Premium-links rule still applies until Premium is live). Advertising can add a "works on your PC too" angle.
- [ ] Phone and PC sync: decide free vs Premium. Options: (a) manual backup or QR (already free), (b) encrypted file the user keeps in their own cloud folder, no MaxedHealth server, (c) a hosted sync service (Premium, costs money, brings ICO and data-protection duties). Recommend (a) free, (b) as the Premium candidate.
- [x] (v3.10.1304: per-row Add this one now removed; the rest kept, see CHANGELOG) Shopping: too many buttons doing the same job (Pete, 5 Nov). Review and propose: the per-row "✓ Add this one now" vs the bottom add button; Match… / Ask AI (my foods) / Create new; Tick all vs section Tick all; Import / Check the cupboards / Add a food. Keep one clear route for each job, hide the rest behind a "?" or remove.
