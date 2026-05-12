# MaxedHealth — Installation & Structure Guide

## The definitive map of what goes where

```
/storage/emulated/0/
│
├── Download/                           ← wearable exports land here automatically
│   └── 7084918973_xxxx.zip             ← Zepp export (distribute.sh moves this)
│
└── MaxHealth/                          ← project root (NOT the git repo)
    ├── app/
    │   ├── maxhealth/                  ← GIT REPO (this zip → repo/ folder)
    │   │   ├── maxhealth.html          ← the app
    │   │   ├── sw.js                   ← service worker
    │   │   ├── manifest.json           ← PWA manifest
    │   │   ├── carer.html              ← carer view
    │   │   ├── why-free.html           ← transparency page
    │   │   ├── setup.sh                ← one-command setup
    │   │   ├── distribute.sh           ← run after every git pull
    │   │   ├── README.md
    │   │   ├── TECHNICAL.md
    │   │   ├── INSTALL.md              ← this file
    │   │   ├── icons/
    │   │   │   ├── icon-96.png
    │   │   │   ├── icon-192.png
    │   │   │   └── icon-512.png
    │   │   ├── docs/
    │   │   │   ├── story.html
    │   │   │   ├── pipeline-setup.html
    │   │   │   └── gbm_patient_guide.html
    │   │   └── pipeline/
    │   │       └── auto.py             ← thin trigger only
    │   │
    │   ├── update_health.py            ← PIPELINE (this zip → pipeline/ folder)
    │   ├── extractors/
    │   │   ├── amazfit.py
    │   │   ├── withings.py
    │   │   └── ringconn.py
    │   ├── server.py                   ← existing, keep as-is
    │   ├── merge.py                    ← existing, keep as-is
    │   └── utils.py                    ← existing, keep as-is
    │
    ├── data/
    │   ├── inbox/                      ← drop exports here (distribute.sh does this)
    │   ├── tables/
    │   │   ├── combined.csv            ← pipeline output → import into app
    │   │   └── nutrition.csv
    │   └── backup/                     ← auto-created, 7 rotating backups
    │
    └── logs/
        └── pipeline.log                ← structured pipeline log
```

---

## This zip contains two folders

### `repo/`
Everything that goes **into the git repo** at:
`/storage/emulated/0/MaxHealth/app/maxhealth/`

Copy all files from `repo/` into the repo root, preserving the subfolder structure.
Then `git add . && git commit && git push`.

### `pipeline/`
Everything that goes **outside the repo** at:
`/storage/emulated/0/MaxHealth/app/`

Copy `update_health.py` into `app/`.
Copy the `extractors/` folder into `app/extractors/`.

These files are **not committed to git** — they live on-device only.

---

## Fresh install from scratch

```bash
# 1. Install Termux and Termux:Boot from F-Droid
# 2. Open Termux and run:
curl -sSL https://raw.githubusercontent.com/pete-maxhealth/maxhealth/main/setup.sh | bash

# That's it. setup.sh handles everything else.
```

---

## After receiving this zip (updating existing install)

```bash
# 1. Copy repo/ files into the git repo
cp -r repo/* /storage/emulated/0/MaxHealth/app/maxhealth/

# 2. Copy pipeline files to app/ (outside repo)
cp pipeline/update_health.py /storage/emulated/0/MaxHealth/app/
cp -r pipeline/extractors/ /storage/emulated/0/MaxHealth/app/

# 3. Commit and push the repo changes
cd /storage/emulated/0/MaxHealth/app/maxhealth
git add .
git commit -m "Update from zip"
git push

# 4. Run distribute.sh to clean up and process any exports
bash distribute.sh
```

---

## What distribute.sh does (run after every git pull or zip update)

1. Removes orphaned duplicate files at `/storage/emulated/0/MaxHealth/` root
2. Scans `/storage/emulated/0/Download/` for wearable exports
3. Moves recognised exports to the inbox
4. Offers to run the pipeline immediately
5. Reports everything it did

```bash
cd /storage/emulated/0/MaxHealth/app/maxhealth
bash distribute.sh
```

---

## Running the pipeline manually

```bash
cd /storage/emulated/0/MaxHealth/app
python update_health.py                              # all devices
python update_health.py --device withings            # Withings only
python update_health.py --device ringconn            # RingConn only
python update_health.py --device amazfit --password YOUR_PASSWORD  # Amazfit/Zepp
python update_health.py --dry-run                    # preview, no writes
python update_health.py --check                      # integrity check only
```

Or use the thin trigger from inside the repo:
```bash
cd /storage/emulated/0/MaxHealth/app/maxhealth
python pipeline/auto.py --device amazfit --password YOUR_PASSWORD
```

---

## The live app

**URL:** pete-maxhealth.github.io/maxhealth/maxhealth.html

The app is served entirely from GitHub Pages — no local server needed.
The pipeline runs on-device in Termux and produces `combined.csv` which
you import via the Import tab.

---

## Repository access

The repo is at `github.com/pete-maxhealth/maxhealth`.
Only accounts with push access can commit — currently just Pete.
To add another contributor: GitHub → repo → Settings → Collaborators.
To protect the main branch: Settings → Branches → Add rule → Require pull request.

---

## Files that should NEVER be in the repo root at /storage/emulated/0/MaxHealth/

These are orphaned duplicates from an earlier structure. `distribute.sh` removes them automatically:

- maxhealth.html, sw.js, manifest.json, carer.html, why-free.html
- update_health.py, setup.sh, README.md, README.txt, TECHNICAL.md, INSTALL.md
- gbm_patient_guide.html, icon-512.png

If you see any of these at the MaxHealth root, run `distribute.sh` to clean up.
