# MaxedHealth Sync — launcher APK

This folder holds the current build of the native Android launcher
("MaxedHealth Sync"), the small companion app that runs the Health Connect
background sync for the main MaxedHealth web app.

- **MaxedHealth-launcher.apk** — the current build. Download it and install
  it on your Android phone (you'll need to allow installs from this source
  the first time).
- **version.json** — what the installed app checks against. If a newer build
  is here than the one you have installed, MaxedHealth Sync shows a banner
  on its loading screen linking back to this folder.

To update: download `MaxedHealth-launcher.apk` again and install it over
the existing app — your settings and Health Connect permissions aren't
affected.

This folder always holds the single current build (the old one is replaced,
not kept) — version.json's `versionCode` is what the app compares against,
so bumping it is what actually triggers the in-app update banner for
everyone already running the app.

## Updating from v1.3 to v1.4

Install the new APK over the old one (v1.4.1 or later; v1.4's grant screen never offered the new permissions). Then open MaxedHealth Sync and use
"Grant permission & sync now" once so Health Connect can offer the three new
permissions (distance, resting heart rate, total calories). Syncing keeps
working in the meantime.

The Health Connect extractor now ships inside the repo (`extractors/health_connect.py`)
and the pipeline prefers it, so a plain `git pull` is all that's needed. No hand-copy.
