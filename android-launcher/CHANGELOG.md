# Changelog — MaxedHealth launcher

Native Android companion app (`com.maxedhealth.launcher`). See `README.md` for what this project is and how it relates to the main `maxhealth` PWA repo.

This file starts here (29 September 2026) — earlier work wasn't tracked in a dedicated changelog for this project, only informally in code comments and the main repo's `docs/changelog.html`. Notable prior milestones, reconstructed from those comments where dated:

- **23 September 2026** — Health Connect integration started: permission handling, availability checks (`HealthConnectBridge.kt`), first working manual read-and-sync proven end to end on a real device.
- **24–25 September 2026** — `findInstalledWebApk()` added so the launcher opens whichever WebAPK is actually installed (found per-device via PackageManager) rather than one hardcoded package name; `HealthConnectTestActivity`'s on/off switch added.
- **26 September 2026** — Fixed Health Connect's Android 14+ `ViewPermissionUsageActivity` requirement (permission screen was silently refusing to appear without it); settings-gear button repositioned clear of the edge-to-edge status bar; root-page-readiness check added to `MainActivity` (avoids a brief "page not found" flash right after a fresh Termux start).
- **27 September 2026** — First attempt at automatic background sync via WorkManager (`HealthConnectSyncWorker.kt`, `HealthConnectBridge.schedulePeriodicSync()`). Built successfully, but never actually confirmed firing on-device before this was superseded — see 29 September below.

## 29 September 2026 — Background sync actually working

### Fixed — Health Connect background sync wasn't running at all

The manual "Grant permission & sync now" screen always worked, but nothing was scheduling it automatically. Investigated and confirmed on-device (via Android Studio's Logcat, watching WorkManager's own `WM-WorkerWrapper` log tag) that the WorkManager periodic job scheduled on 27 September had never fired even once, in nearly an hour of testing, while other apps' periodic WorkManager jobs on the same phone fired normally in that same window. Battery saver for this app was already off, ruling out the most common cause.

Replaced WorkManager entirely with a foreground service on a 30-minute repeating alarm:

- `HealthConnectSyncService.kt` (new) — foreground `Service`, shows a low-priority "Syncing…" notification only while actively running (a few seconds at a time), does one sync, then stops itself.
- `AlarmReceiver.kt` (new) — `BroadcastReceiver` that re-arms the next run via `AlarmManager.setExactAndAllowWhileIdle()` (Doze-resistant), fired both by the previous run and on device boot (`RECEIVE_BOOT_COMPLETED`), so the chain survives a reboot without the app needing to be reopened.
- `MainActivity.onCreate()` now calls `HealthConnectSyncService.startNow()` instead of `HealthConnectBridge.schedulePeriodicSync()`. The old WorkManager code (`HealthConnectSyncWorker.kt`, `schedulePeriodicSync()`) is kept in place, unused, rather than deleted, in case a future HyperOS/MIUI update makes WorkManager reliable again.

Two Android 14+ foreground-service-type issues were found and fixed along the way, both confirmed via a new on-device debug log (`sync_service_debug.log`, added specifically to diagnose this — Logcat access from a remote session proved unreliable to search):

1. **`MissingForegroundServiceTypeException`** — the manifest declared `android:foregroundServiceType="health"` but the code's `startForeground()` call didn't pass a matching `ServiceInfo.FOREGROUND_SERVICE_TYPE_*` flag. Android 14+ requires both to agree.
2. **`SecurityException` on the "health" type itself** — even once matched, `FOREGROUND_SERVICE_TYPE_HEALTH` additionally requires `ACTIVITY_RECOGNITION`, `BODY_SENSORS`, or `HIGH_SAMPLING_RATE_SENSORS` (none of which this app declares or needs — it reads from Health Connect, not live sensors directly). Switched to `FOREGROUND_SERVICE_TYPE_DATA_SYNC` — the correct type for "read some data, write it somewhere" work, no extra sensor permissions required.

Confirmed fixed via the debug log showing a clean, unattended run:

```
[...] onCreate
[...] onStartCommand — calling startForeground()
[...] startForeground() succeeded
[...] gating: enabled=true available=true permitted=true
[...] sync complete: steps=2526
[...] onDestroy
```

### Manifest changes

- Added `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_DATA_SYNC`, `SCHEDULE_EXACT_ALARM`, `RECEIVE_BOOT_COMPLETED` permissions.
- Added `<service android:name=".HealthConnectSyncService" android:foregroundServiceType="dataSync" />` and `<receiver android:name=".AlarmReceiver">` (boot-completed intent filter).

## 1 October 2026 — v9/v10: in-app update checks, Health Connect settings button fix, sleep double-counting fixed

### v9 — Added: update-check banner, Health Connect button timing

- `versionCode`/`versionName` bumped for the first time since project creation (had been stuck at 1 through v3–v8) — needed so the new version-check below has a real number to compare against. `buildFeatures { buildConfig = true }` also enabled in `app/build.gradle.kts` (AGP 8+ turns off `BuildConfig` generation by default; the version check reads `BuildConfig.VERSION_CODE`).
- `checkForNewerApk()`/`showApkUpdateBanner()` (`MainActivity.kt`) — fire-and-forget check against `apk/version.json` in the main `maxhealth` repo (raw GitHub content, no auth needed) on every open; shows a banner linking to the `apk/` folder if a newer build is available. This app has no store to push updates through, so previously the only way to know a newer build existed was being told directly.
- The loading screen's Health Connect button: was a timed gear icon (900ms minimum display, added so it's at least tappable) that Pete reported "still vanished too fast on reload... I missed it the first time." 900ms genuinely isn't enough time for a human to see, register, and tap a button on a warm launch. Changed to a permanent labelled "Health Connect settings" button at 6000ms minimum display.
- Distribution itself moved to a `apk/` folder in the main repo (APK + `version.json` + README), replacing "handed to testers directly" — Pete's own call when asked how to handle distribution.

### v10 — Sleep query window fix (real edge case, but NOT what caused the 13h32m — see v11)

Pete, from a screenshot: "Looks like the sleeping health connect issue is still apparent" — Trends showing 13h32m total sleep at 11:15am, which isn't possible for a day barely a third through.

**Correction, added after v11:** this diagnosis was wrong about the cause. Pete went to bed at ~02:00, so no session straddled midnight and last night wasn't leaking in. The window fix below is still correct for a session that does straddle midnight, but the 13h32m had a different cause (v11). Original reasoning left as written:

Not a reorder or a resolveSleepHours bug — that overlap-detection logic (added 30/09, see its own doc comment in `HealthConnectBridge.kt`) was working correctly on whatever it was given. The actual bug: `getDailySummary()`'s sleep query used the same `TimeRangeFilter.between(todayMidnight, now)` as steps/heart-rate/weight. Health Connect's filter matches any session that *overlaps* that window at all — so last night's real sleep session (started ~22:00 yesterday, ended this morning) was being pulled into *today*'s query too, on top of anything else. `resolveSleepHours` then correctly saw two genuinely non-overlapping periods and summed them — it was just summing last night's sleep plus itself: counted once for yesterday, counted again in full for today.

Fixed by giving sleep its own, separately-queried, backward-extended window (yesterday noon onward — comfortably before any realistic bedtime), then keeping only sessions that actually *ended* today. That's attribution by wake-up day, which is what "today's sleep" means to someone checking Trends in the morning — not attribution by whether a session happens to overlap a midnight-to-now timestamp.

### v11 — Fixed: two devices recording one night were being added together

Pete's 02:00 bedtime disproved v10's theory (9h15 elapsed since bed, yet 13h32m shown), so he sent screenshots of both apps. Zepp and RingConn each said **5h17m asleep**. The raw Health Connect sessions — RingConn 01:23–06:13, RingConn nap 08:03–09:11, Zepp 01:56–09:16 — are spans that include awake time, and add to 13h18m (within 14 min of the 13h32m shown). The overlap-conflict card in the web app offered "Both genuinely happened — add them" across all three raw spans.

`resolveSleep()` (`HealthConnectBridge.kt`) replaces the old span-based logic:
1. Sleep is measured in **asleep time** — the union of each record's non-awake stage intervals (whole span only if a record has no stages).
2. One total per **source** — a device's nap and main sleep are one device's story, not two sources.
3. One source → its total. Several sources not overlapping in time → sum. Several overlapping (same night) → compare totals: within 20 minutes they **agree** and the preferred device (RingConn, then Zepp) is used with no prompt; only a real disagreement is queued for the comparison card, one entry per source, with asleep minutes.
Pete's morning now resolves to 5h17m with no card. The web app's card lost its "add them" button in v3.10.841. Checked against Pete's real numbers plus single-source, separate-periods and genuine-disagreement cases in a throwaway simulation; not yet confirmed on-device.

### v1.4 (versionCode 12) — Reads far more from Health Connect

Pete: "Health connect users only would want as much information as possible." The launcher read seven record types; this adds the rest worth having.

- New reads: distance, resting heart rate, total calories (sent as `calories_passive` = total − active); min/max heart rate; min/max HRV and SpO2; and sleep detail — deep/light/REM/awake minutes, bedtime, wake time, sleep efficiency — for the night `resolveSleep()` settled on. Stage totals follow the same source choice as the sleep total so they always agree with it (`buildSleepDetail`).
- Safe upgrade: `corePermissions` (the original seven) still gate the sync; the three new permissions (`READ_DISTANCE`, `READ_RESTING_HEART_RATE`, `READ_TOTAL_CALORIES_BURNED`) are optional, each read is skipped unless granted and wrapped in try/catch. Manifest declares the three new permissions.
- Left out on purpose: exercise sessions (need their own design), basal metabolic rate (the app calculates it itself).
- Note for future builds: `device_commit_files` appears to cache files by `stagedPath`; reusing a previously used output filename wrote stale content to the laptop (manifest regressed once, caught by a size check and fixed). Use a fresh filename per write and always verify sizes afterwards.
