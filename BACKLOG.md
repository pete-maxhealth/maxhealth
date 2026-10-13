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

## Other
- [x] v3.10.950 Incidental Steps Baseline automatic; Activity Level reads real weekly steps.
- [ ] Strength Log CSV import still replaces (now asks first).

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
