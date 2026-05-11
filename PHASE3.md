# MaxHealth Phase 3 Specification

Status: Planning
Live app: pete-maxhealth.github.io/maxhealth/maxhealth.html

## Theme: Data Intelligence + Onboarding Excellence

---

## 1. Data Pipeline

### 1.1 Source Precedence
When multiple devices report the same metric, configurable precedence determines which is used. Secondary fills in if primary has no value.

Default order:
- Weight: Withings > manual > RingConn
- HRV: RingConn > Withings > Garmin
- Sleep: RingConn > Withings > Garmin > Oura
- Steps: Garmin > Withings > RingConn
- SpO2: RingConn > Withings

User-configurable in Import tab.

### 1.2 Data Source Tracking
Every row in combined.csv gains a source column (e.g. withings+ringconn).
Visible in Trends when hovering a data point.

### 1.3 File Versioning
Before any pipeline write, current combined.csv and nutrition.csv copied to
/data/backup/ with timestamp. Max 7 backups retained. Restore via Import tab.

### 1.4 Data Validation
- Date format and value range checks (weight 30-300kg, HRV 0-300ms etc)
- Duplicate date detection with conflict resolution
- Structured error log at /MaxHealth/pipeline.log

### 1.5 Amazfit / Zepp Integration
Sample zip is in inbox. Build extractors/amazfit.py, add to pipeline and
Import tab device selector. Test with real export data.

---

## 2. Onboarding Excellence

### 2.1 First-Time Journey Audit
Full walkthrough from story page to first logged meal. Target: under 3 minutes
for a non-technical user arriving cold.

### 2.2 Contextual Tips (one-time, dismissable)
- First Trends visit: "Import wearable data to populate these charts"
- First Library visit: "Save regular foods here for instant logging"
- First Reports visit: "Generate your first brief after 14 days of data"
- First carb ceiling hit: explanation of what happens next

### 2.3 Condition-Specific Onboarding Paths
After main wizard, optional condition path:
- GBM / Therapeutic Ketosis: 50g carb ceiling, patient guide link, ketosis explanation
- Type 2 Diabetes: appropriate carb ceiling, blood sugar context
- Body Recomposition: protein target focus, lean mass tracking
- General Health: standard defaults

### 2.4 Demo Mode
Read-only mode pre-populated with 30 days of sample data.
Accessible from story page as "Try a demo". Nothing saved.

---

## 3. Reporting and Error Tracking

### 3.1 Pipeline Error Log
Structured logging: timestamp, device, operation, status, error message.
Last 50 lines viewable in Import tab. Errors surfaced in UI not silently dropped.

### 3.2 Specific AI Error Messages
- Network error: "Check your connection and try again"
- Proxy error: "AI temporarily unavailable - try again in a moment"
- Parse error: "Try describing the meal differently"

### 3.3 Data Integrity Checks
On app load: detect duplicate dates, detect corrupted entries,
flag to user with option to review and clean.

---

## 4. Documentation

- README: reflect current architecture (GitHub Pages + proxy, no localhost)
- Story page: "no API key needed" prominent, install tracks accurate
- Pipeline setup guide: add Amazfit/Zepp, precedence config, backup/restore, error log
- In-app help: collapsible per-tab help sections, consistent and concise
- TECHNICAL.md: architecture, proxy setup, pipeline structure, data schema, adding extractors

---

## 5. Additional Items

- PWA push notifications: EOD reminder, carb ceiling warning, weekly summary
- Nutrition CSV auto-export to pipeline (eliminate manual export step)
- Reports: selectable date range and query builder
- Multi-user / carer view: read-only shared view via encrypted export link
- Offline-first: proper queued AI requests when connectivity returns

---

## Priority Order

1  Amazfit/Zepp extractor (sample in inbox, real user need)
2  Documentation pass (README, story, pipeline guide)
3  Condition-specific onboarding paths (GBM path especially)
4  Contextual onboarding tips
5  Source precedence + data source tracking
6  File versioning / backup
7  Pipeline error logging
8  Data integrity checks
9  PWA push notifications
10 Reports date range + query builder
11 Demo mode
12 Multi-user / carer view
13 Nutrition CSV auto-export

---

## Phase 2 Complete

- GitHub Pages distribution
- Cloudflare proxy - AI built in, no user key needed
- PWA manifest + service worker
- Onboarding wizard with TDEE calculator
- Assistant tab (formerly Log Meal)
- Health context in Settings
- Food library with edit, save from AI, duplicate prevention
- EOD save to history
- Reports tab with GBM monthly brief
- Body composition overlays on weight chart
- Nutrition/wearable correlation
- Data import/export (JSON + nutrition CSV)
- Pipeline setup guide
- Story page with install instructions
- Patient guide linked from Reports and Settings
- TDEE recalculator in Settings
- Dynamic targets - no hardcoded values
- Floating point rounding fixed
