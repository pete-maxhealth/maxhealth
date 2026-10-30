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
- [ ] Phone checks for v3.10.1081 (Today statistics card, Statistics tab on light theme, net exercise energy figures, weather follow).
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
- GoDaddy upload of premium-site/, ICO fee check, move APK off public GitHub, launcher items.

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
- [ ] Other open: GoDaddy redirect to GitHub Pages, monthly competitor sweep on the 1st, Premium pricing decision, re-record tours with Move/Sleep/Statistics chapters.

- [ ] (v3.10.1125) Guide and README: mention that a recipe leaves off foods already in the cupboards.
- [x] v3.10.1246 fixed (fruit words added, pear/peach/peanut moved ahead of 'pea', spear guard). Left for later: other everyday foods that may still fall to Other (check the Library 'Other' chip). Was: The category sorter files Apple, Banana, Grape, Lemon as Other (and Pears as vegetable). It is global (aisles, nutrition groups), so extend CATEGORY_MAP deliberately and run the full sweep. Found 21 Oct 2026 while adding section rules for fridge life.

## Data and Reports tidy-up (raised by Pete 27 Oct 2026; agreed plan, do after v3.10.1226)
- [ ] Data tab: group by intent ("Bring data in", "Move or back up my data", "Check it's complete"). One "Move & back up" card with a "what do you want to do?" chooser holding QR, export/import, setup share, starter packs and restore. Fold the wearable cards (Sync, History, Advanced pipeline, Add device) into one.
- [ ] Reports: merge Sleep into Sleep & Ketosis; merge Treatment Analysis with Sessions; one "Ask about this period" card (Ask AI + Query Builder); rename Export & Share to "Make a report to hand to someone" and point to Data for raw files.
- [ ] Keep show/hide and reorder on every merged card, long text behind "?", rendered side-by-side screenshot check, targeted persona tests (no sweep unless asked).

## Pre-existing test failures found 28 Oct 2026 (identical on v3.10.1225, not caused by 1226)
- [x] p42 (Clear-Site-Data header guard): retired 28 Oct 2026 at Pete's call; it hung every run. The warning comment in server.py (around line 1801) stays. Do not add Clear-Site-Data back without testing on the phone.
- [x] p63, p70 (fasting): v3.10.1246 pinned to UTC. Cause was the UK clock change on 25 Oct (that night is 13h of real fasting); the app counts real elapsed hours and is right.
- [x] p306, p307 (ate-out history): fixed 28 Oct 2026. The tests hard-coded 20/10/26, which fell outside History's default period; they now use a day relative to today. No app bug.

## Steps: plan vs actual in one box (Pete, 28 Oct 2026; build only after the videos, not needed for them)
- [ ] One Daily Steps box that knows if the number is a plan (intention) or an actual. A plan is replaced by the first device figure even if lower; an actual stays a floor (today's rule). Plan ahead becomes how a plan is entered. Card says "planned, waiting for your watch". Steps become the one metric where a device beats a manual entry; everything else keeps manual wins. Whole-day test: plan, device lower, device higher, midnight, reload, History.
- [ ] No in-app step counter (a web page cannot count in the background). Phone steps come from Health Connect via the launcher; fix the phone+watch double count there (needs the laptop).

## Moving off GitHub (Pete and Jill, 29 Oct 2026). v3.10.1246 put the app's own addresses in one `MH_HOME` block; what is left
- [ ] **App:** host `starter_packs/`, `lang/` and `README.md` (the version check reads its `**Version:**` line) as plain files, with CORS allowing the app's origin; then edit `MH_HOME.raw` (and `site`, `issues`) in maxhealth.html. Keep the GitHub copy until every installed copy is on a version that has the new addresses.
- [ ] **Where the app itself is served from** (today pete-maxhealth.github.io): story page, docs, user guide, privacy pages, carer.html. The phone app runs from the Termux server, so the launcher/`mh_autoupdate.sh` (`git fetch origin`) also needs a new remote or a download-and-unpack route.
- [ ] **Scripts and docs that name GitHub:** `setup.sh` (REPO, the curl line), `deploy_docs.sh` (printed URLs), README.md (Live link, clone line), `premium/public_README.md`, `premium/user-guide-full.html` (launcher download, setup curl, GitHub link), `premium-site/setup.html` (curl line), `docs/story.html` and `docs/why-free.html`, `gbm_patient_guide.html` (links to the app).
- [x] **Launcher (laptop):** done 30 Oct. Launcher 1.6.1 (build 17, source `MaxedHealth-launcher-1.6.1-source.zip`, not in this repo) reads `version.json` from the Cloudflare licence Worker; its banner opens `/launcher/get` (paste key, APK downloads). Proven on Pete's phone, update banner, key, download. Worker, KV and secrets are set up (see LICENCE_WORKER_SETUP.md; the Cloudflare dashboard route replaced wrangler).
- [x] **Licence address:** app v3.10.1249 sends keys/trial to the Worker (`MH_LICENCE_URL`), not GoDaddy.
- [ ] p131 (split_premium) fails on a clean checkout: it opens `free/README.md` in the split output and the file is not there. Failed the same before the APK removal (30 Oct), so not caused by it. Look at `tools/split_premium.py` / `premium/public_README.md`.
- [x] 30 Oct: `apk/` removed from the repo tree (README and TECHNICAL.md updated). The 1.5.1 and older APKs stay in git history until history is rewritten. Release asset `launcher-v1.0.0` (MaxedHealth-launcher-v1.0.0.apk) still public: Pete to delete on GitHub.
- [ ] **Still to do for the APK:** (1) install 1.6.1 by hand on Jill's phone (she is on 1.5.1, which still checks GitHub); (2) with Pete's OK, remove `apk/` and the GitHub Release assets from the public repo (old files stay in git history unless history is rewritten, which needs his say-so); (3) keep an offline copy of `debug.keystore` and the 1.6.1 APK first; (4) a sold APK should be a signed release build, not a debug build; (5) the banner-tap on 3-button navigation was fixed in 1.6.1, check a gesture-navigation phone too.
- [ ] **Bug reports:** with no GitHub issues, `MH_HOME.issues` = '' makes the report copy its text; the settings card text still says "Opens a GitHub report", so reword it at the same time.
- [ ] **Ads, videos and descriptions** that link to the github.io address (YouTube descriptions, the Ko-fi gallery, the register-interest page) need the new address before the old one goes dark; consider a redirect from the old address first.

## Nightly sweep, night of 29-30 Oct 2026 (triaged 30 Oct)
- [x] p325: stale test, fixed. The Move tab now has planCard (the exercise planner) after activityCard; the expected order list in the test was missing it. Not an app bug.
- [ ] p308 (two users uniform, Reports "btn-neutral" font): intermittent. Failed in the sweep and once on a lone run straight after another test, then passed twice. The odd persona reported Arial instead of Space Mono, so a Reports button was measured before it was styled or redrawn. Leave for now; if it keeps appearing, make the test wait for Reports to settle.

- [ ] Manual "Missed day" has no fat box and stores fat as 0 (not "not entered"). Decide whether to add the box, or store nothing.
