# MaxedHealth launcher

Native Android companion app for [MaxedHealth](https://pete-maxhealth.github.io/maxhealth/maxhealth.html), the health-tracking PWA. Package: `com.maxedhealth.launcher`.

This is a small, separate Android Studio project — it is **not** the PWA itself (`maxhealth.html`, in the main `maxhealth` repo). It exists to handle things a web page can't do on its own: launching the PWA reliably, ensuring the Termux-hosted server is running, and reading Health Connect data in the background.

## What it does

- **Launches MaxedHealth** — opens the PWA in the user's own installed WebAPK if one exists (so existing data/storage is used, not a fresh empty Chrome tab), falling back to a Chrome Custom Tab otherwise. Waits for the Termux server to actually be ready (not just "process started") before handing off, with a retry screen if it's taking unusually long.
- **Keeps the Termux server alive** — actively nudges `mhstart` on each launch rather than passively hoping it's already running (`TermuxBridge.kt`).
- **Health Connect integration** — reads steps, heart rate, weight, and sleep from Android's Health Connect and writes them into the same pipeline inbox every other device export uses (`HealthConnectBridge.kt`, `extractors/health_connect.py` on the server side). Manual sync via a settings screen (⚙ button, or long-press the home screen icon), plus automatic background sync — see below.
- **Onboarding** — `ProvisioningActivity` walks through the one-time setup Termux itself requires (permissions, `allow-external-apps`) before handing off to `MainActivity` for normal use.

## Background Health Connect sync

As of 29 September 2026, this runs via a **foreground service on a repeating alarm** (`HealthConnectSyncService.kt` + `AlarmReceiver.kt`), not WorkManager. WorkManager's periodic job was tried first and never fired reliably on real hardware (HyperOS/MIUI) — confirmed via on-device logging that it simply never started, with battery optimization already ruled out. A foreground service is much harder for a manufacturer's battery manager to silently kill outright.

Two Android 14+ specifics worth knowing if this ever needs touching again:
- A service using a foreground-service *type* must declare it in **both** the manifest (`android:foregroundServiceType`) and in code (`startForeground(..., ServiceInfo.FOREGROUND_SERVICE_TYPE_*)`) — a mismatch throws at runtime.
- The type must be `dataSync`, not `health` — `health` additionally requires `ACTIVITY_RECOGNITION`/`BODY_SENSORS`/`HIGH_SAMPLING_RATE_SENSORS` permissions (for apps reading live sensors directly), which this app doesn't need since it only reads from Health Connect, itself already permission-gated separately.

A small debug log (`/storage/emulated/0/maxhealth/app/data/sync_service_debug.log`, plain text, on-device) records each sync attempt — useful for confirming background sync is actually firing without needing to reconnect a debugger, since that's genuinely hard to arrange for a phone that isn't physically at hand.

## Building

Standard Android Studio project — open the `MaxedHealth` folder, let Gradle sync, Run onto a connected/USB-debugging device. `minSdk = 26`, `targetSdk = 37`.

## See also

- `CHANGELOG.md` in this project — history specific to the launcher app.
- The main `maxhealth` repo's `docs/changelog.html` — the PWA's own changelog, which also links back to major launcher milestones like this one.
