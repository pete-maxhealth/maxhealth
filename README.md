# MaxedHealth

**Personal health intelligence PWA** — AI-powered nutrition tracking, wearable data integration, and metabolic analytics. Built for a strict therapeutic ketogenic protocol post-GBM diagnosis.

**Live:** [pete-maxhealth.github.io/maxhealth/maxhealth.html](https://pete-maxhealth.github.io/maxhealth/maxhealth.html)
**Local:** `http://localhost:5757` (via Termux + server.py)
**Version:** v3.10.563

---

## What it does

- **Ketosis impact preview** — every "Ready to log" screen shows exactly what would happen if logged: calories/protein/fat as before → after against today's real targets, plus a clear ceiling check (still within it, or over by how much, including whether it would end a current streak). Updates live as the portion amount is adjusted.
- **Exercise Offset for carb overage** — off by default (Settings). Distinguishes a carb overage meaningfully addressed by logged exercise that day from one left unaddressed, without ever hiding or replacing the raw over-ceiling fact.
- **Dashboard traffic-light status** — small coloured dots on Calories/Protein/Carbs/Fat. Carbs uses ceiling logic; the other three use gaining-phase logic by default (under-eating is the real risk on a surplus protocol, not exceeding).
- **Weight intention status** — reads the actual Goal/Phase setting and colours the 14-day weight trend by whether it's serving that goal (losing during a Lose phase is green; gaining is red). No-consequence preview mode to see other goals without changing anything real.
- **Your Journey** — weight across the entire tracked history, always, independent of any date filter. Points coloured by ketosis status, treatment days marked along the bottom.
- **Treatment Analysis** — nutrition/ketosis/weight on treatment days vs standard days, plus detected treatment cycles and a comparison against the immediate post-treatment recovery window.
- **Carb Pattern breakdown** — % of days at Strict Keto/Keto/Low Carb (or neutral equivalents for non-keto conditions), framed around hitting your own chosen target, not a ranking against strict keto.
- **GBM Research Digest** — persistent, dated home for real research findings, colour-coded Proven/Early Stage/Speculative. Deliberately not automated — the app's AI calls have no live web search, so a "Research Now" attempt was tried, confirmed unreliable, and replaced with a one-tap "Copy Research Request" for pasting into a real chat conversation instead.
- **Formulas & Technical Reference** — every calculation the app uses, in plain language, in-app. No black boxes.
- **Unified AI reliability** — all 9 AI call sites (Ask AI, Full Summary, GBM Summary, Oncology narrative, meal parsing, portion estimation, barcode reading, missed-day calculators) now share one function with real error surfacing instead of generic swallowed failures, and image support for vision calls.
- **Voice logging, refined** — one-tap "Log it" directly on the transcript, real error messages instead of raw codes, subtle mic highlight on treatment-tagged days.
- **Library duplicate protection, properly consistent** — the same category-mismatch check (a food-category word like "bread" vs "cheese" disqualifies a match, regardless of incidental word overlap) now applies across all four library-matching functions, not just one — found after a generic descriptor match ("white", "slices") slipped a wrong suggestion through three sibling functions that had never been fixed.
- **Suggested Targets calculator** ⭐ — the app's most powerful feature. Enter height, age, sex, weight, condition and goal → it calculates personalised TDEE (Mifflin-St Jeor × activity from real step data), phase-adjusted calories, protein (1.8g/kg for GBM/Epilepsy/Migraine/Cluster Headache, 1.6g/kg otherwise), and fat to fill remaining calories. Condition overlay checks ketogenic ratio for the therapeutic-protocol conditions. One tap applies all targets. Works on day one with no history, and improves as wearable data accumulates.
- **Library-aware meal suggestions** — "📚 From my library" proposes real combinations of saved ingredients and Recipes (proper per-serving math) against today's actual remaining macros, never inventing values. One-tap logging straight from the suggestion.
- **Ingredient substitution** — a genuine searchable picker across recipes, Cook Mode, and suggested meals, with an online-search fallback when nothing in your library fits. Deliberately not auto-matching — an earlier automatic version once suggested peanut butter as a substitute for dairy butter, which is the kind of mistake a real search list in front of a person doesn't make regardless of how good the matching heuristic gets.
- **Saved Prompts library** — every AI question (both the Log-tab chat and the Reports Ask AI panel) draws from one shared, searchable, editable list rather than fixed buttons. Add, edit, delete, dictate new ones by voice, sorted by how often you actually use each one.
- **Recipes** — proper servings math for anything batch-cooked (log 1, 2, or half a portion correctly), with a real review step (add/remove/swap any ingredient) before it hits your log, and a "Refresh from Library" action if an ingredient's values have since been corrected. Meals as a separate concept has been retired — saving a logged combo now creates a genuine recipe directly, with real per-item ingredients.
- **Real food categories, fully in-app editable** — every library item auto-categorizes into genuine food groups (meat, fish, dairy, vegetable, fruit, fat, protein, grain, breakfast cereal, bread, sweet, savoury, herbs and spices, alcohol, salad) rather than the ingredient's own name being treated as its category. Add, edit, or remove any category mapping directly in Manage Categories, including a rename tool for fixing existing data in bulk and typo protection. Browse by Category to see and log from a group directly.
- **Structured meal requests** — a multi-select category picker (tap to select, set a count per category, Send) builds requests like "meat + 3 veg" or "protein + grain + salad" directly, or type it in chat ("protein and pasta"). Honest partial-match handling when the library can't fully cover what was asked.
- **Fibre and polyols, fully editable** — can be added or corrected directly on any library item, not just when the AI happens to read them correctly at add-time.
- **Read-aloud** — AI chat responses, the GBM Monthly Summary, and Research Digest entries can be read aloud via a speaker icon, using the browser's built-in text-to-speech, fully offline.
- **Dashboard & tab reordering** — every section on Today, the Library tab's Recipes/Food Library split, and Reports/Manage/Import can be reordered via ▲▼ buttons, with preferences persisted.
- **Ketosis streak milestones** — one-time celebration at 7/14/30/50/100/200/365 consecutive days.
- **Nutrition logging sanity checks** — Atwater kcal-consistency, implausible low-carb-on-fruit, implausible portion size, and macro-mass-exceeds-food-weight — now also checked at the point of adding a library item, not just when logging one, catching bad data at the source.
- **Itemized ingredient editors** — multi-item log entries (Today's Log and History) get a real per-ingredient editor: add, remove, or adjust any single ingredient, with amount edits auto-scaling that item's macros from a stable baseline. **Scale entire entry to X%** applies proportionally across every ingredient at once in one action — for logging a partial serving of a bigger batch without recalculating each item by hand.
- **Weight Phase History** — log intentional weight phases (loss/maintain/gain) with dates. Automatically updated when you change goal. Used by all AI reports to correctly interpret weight trends — deliberate loss is never flagged as a concern.
- **Condition History** — same pattern as Weight Phase History, for condition instead of goal. Auto-logs whenever your condition genuinely changes, so a later switch can't retroactively distort how old data gets judged. Ask AI and Full Summary become period-aware automatically once more than one condition has been used — ask naturally ("compare my general and migraine periods") and the AI handles the comparison itself, no filter or dropdown needed.
- **Activity Level, personalised and self-updating** — a real, editable Profile setting (previously asked once at onboarding and discarded). Walking effort (Easy/Moderate/Hard) is calibrated to it — real research confirmed there's no single universal "brisk" pace threshold, since even the AHA and CDC officially disagree on the number, explicitly because it depends on individual fitness. Auto-switches from sustained real step-count trends (smoothed 30-day average, resistant to single noisy or rest days), with a celebration for genuine improvement and a plain notification for decline. Full Activity Level History, same pattern as Condition History.
- **Site-wide search** — 🔍 in the header, always accessible. One box searches Library, Recipes, Saved Prompts, and every Settings section across all three sub-tabs. Tapping a result takes you straight there — opens the right picker pre-filled, runs the prompt directly, or scrolls straight to the settings section (expanding it first if collapsed).
- **⭐ Full Summary** — one-tap comprehensive 9-section health analysis: nutrition, weight phases, ketosis quality, sleep, HRV, activity, best periods, areas to improve, protocol verdict. Phase-aware, condition-specific, nil days excluded.
- **AI meal logging** — type, paste, photo, barcode or voice. Step 0 photo classification (label vs meal), ambiguity detection (asks before logging uncertain items), sanity-checked portion estimation, per-component delete and inline edit in preview.
- **Food library** — Meals, Recipes, and Ingredients. Search, A-Z nav (ingredients only), long-press to log, recently scanned items.
- **Condition/Protocol** — Settings dropdown, all 9 offered at onboarding too: GBM, Epilepsy, Strict Ketosis, Migraine, Cluster Headache, Type 1 Diabetes, Type 2 Diabetes, General Health, Body Recomposition. All AI reports adapt framing, evidence categorisation and thresholds — Migraine/Cluster Headache explicitly framed as promising, real trial evidence rather than established standard of care.
- **Activity card** — Walking, Resistance + custom exercises. Distance-aware effort auto-calculation. All macro targets adjust dynamically. Strength Training log and Routine Templates for saved exercise groupings.
- **Occasion tags** — Chemotherapy, Hospital day, Illness, Social event, Travel, Fasting. Multi-select, retroactively editable.
- **Reports** — condition-aware, day-type aware (holiday/occasion days evaluated against their own ceilings), nil days excluded from all calculations and AI context.
- **Boot survival & auto-update** — Termux:Boot + wake-lock + watchdog cron. Server auto-restarts after reboots, zero user interaction required. A separate 30-minute check also pulls any update from GitHub automatically, so a device never falls behind without someone manually running `git pull` on it.
- **Remote diagnostics** — Settings → Manage → Advanced Troubleshooting Tools → App Health Check shows the real auto-update log, crontab, and whether crond/the server are actually running, alongside the existing version-sync and div-balance checks. One tap, then copy the output — lets a stuck device get debugged by someone else entirely, without needing Termux access on the affected phone.
- **Offline fallback** — when AI is unreachable (flight mode etc.), a manual macro entry form appears automatically.
- **Weight carry-forward** — dashboard shows last known weight when today has no reading, labelled "last known".
- **Wearable integration** — Withings, RingConn, Amazfit via `update_health.py`. AES-encrypted Zepp exports via `pyzipper`. Device precedence is user-configurable per metric, including custom devices beyond the built-in list.
- **Demo mode, seeded with real data** — "Try a demo first" loads a genuinely rich, anonymised dataset (full 151-item library, 30 real days of history, real recipes/routines/strength sessions) entirely in memory — never touching real storage during a session, exiting restores real data untouched.
- **Log food to a past day** — from History, add a forgotten or mis-logged item to any previous day through the exact same AI-parsing pipeline used for today (text, photo, barcode, library). Recalculates that day's totals from its full log automatically, no manual arithmetic.
- **Multi-AI consensus check** — verify any logged item against Claude, Gemini, and ChatGPT independently, one tap. Three estimates agreeing is a genuine reassurance signal; disagreeing by more than 25% on calories is flagged as worth finding a real label rather than trusting any of them. Each provider's own numbers are checked for internal consistency before comparing. Per-provider checkboxes let you exclude an outlier before applying an average to a single item.
- **Activity Credit Balance** — rolling-window tracking (Insights → Trends) of exercise calorie credit earned vs actually eaten back, built from real stored history. A single day under an exercise-boosted target is harmless; this surfaces the pattern if it's happening often enough to compound into something real, with interpretation tailored to your actual Goal/Phase setting.
- **Phase-aware calorie context** — Remaining Today distinguishes harmless unclaimed exercise credit from genuine under-eating against your actual base target, worded differently for maintain/gain/lose goals.

---

## Quick start

```bash
git clone https://github.com/pete-maxhealth/maxhealth.git
cd maxhealth
bash setup.sh
mhstart
# Open http://localhost:5757
```

## Auto-start on boot — self-healing, fully automatic

`setup.sh` sets all of this up for you — nothing below needs doing by hand. Once installed, Termux never needs to be opened manually again:

- **Watchdog** (`~/mh_watchdog.sh`, via cron every minute) — checks the server is alive, restarts it if not, kills duplicate instances if more than one is somehow running
- **Auto-update** (`~/mh_autoupdate.sh`, via cron every 30 minutes and once on every boot) — checks GitHub for anything new and pulls it automatically, so a device never needs a manual `git pull` to stay current
- **Boot scripts** in `~/.termux/boot/` start crond, hold a wake-lock (stops Android's battery-saving Doze mode suspending the checks between cron ticks), and start the server itself

After a reboot, give it a minute, then confirm the server's running on its own (`curl http://localhost:5757/ping`) — no manual Termux interaction needed. From this point on, Termux can stay closed; the server is self-healing and self-updating.

Requires **Termux:Boot** and **Termux:API** from F-Droid (same signing key as Termux) — `setup.sh` prompts for these automatically if they're missing.

Note for cloud/GitHub Pages users: none of this is required — it only applies to local Termux setups. If you switch to local mode later, this is already set up for you the moment you run `setup.sh`.

## Local server access — pin the shortcut directly

As of Chrome's Local Network Access (LNA) enforcement (rolled out across Chrome ~142–149), public HTTPS pages — including the GitHub Pages version of MaxedHealth — can no longer auto-detect or redirect to a local server at `localhost:5757`. This is a browser security restriction, not a MaxedHealth bug, and it affects every site that tries this trick, not just this one.

**What this means for you:** instead of opening the GitHub Pages link and letting the page jump to local mode automatically, open `http://localhost:5757` directly (with the local server running) and add **that** to your home screen. `setup.sh` does this for you automatically on first install.

If you already have an older shortcut pointing at the GitHub Pages URL, delete it and re-add one pointing at `localhost:5757` instead — the page itself will tell you (via a one-time toast) when it detects a local server is running but auto-redirect isn't possible.

## Deploy after update

```bash
cp /storage/emulated/0/Download/maxhealth.html /storage/emulated/0/maxhealth/app/maxhealth/maxhealth.html
cd /storage/emulated/0/maxhealth/app/maxhealth
bash bump_and_deploy.sh X.X.X "description"
```

`bump_and_deploy.sh` bumps both version references, checks div balance, commits, pushes, and — critically — verifies the push actually landed on `origin/main` rather than trusting that `git push` printing something reassuring means it worked (this was silently failing for roughly 100 versions before the check existed). A `.gitignore` now excludes `__pycache__/`, backup files, and trash artifacts, so `git status` stays meaningful.

For anything other than `maxhealth.html` itself (worker.js, docs, scripts), commit manually and selectively — avoid `git add -A`, which will happily stage pycache and stray backup files alongside real changes.

## Full backup

```bash
pkg install zip -y
cd /storage/emulated/0/maxhealth
zip -r "/storage/emulated/0/Download/maxhealth_backup_$(date +%Y%m%d).zip" app/maxhealth/ data/tables/
```

---

## File structure

```
maxhealth/
├── maxhealth.html      # Complete PWA (~1.3MB)
├── worker.js           # Cloudflare Worker — Claude proxy + Gemini/OpenAI for multi-AI consensus
├── find_orphans.py     # Maintenance script — flags potentially unused functions/variables (manual review only)
├── why-free.html       # Why MaxedHealth is free
├── user-guide.html     # User guide
├── server.py           # Local HTTP server (Termux)
├── update_health.py    # Wearable data pipeline
├── setup.sh            # First-time install
├── TECHNICAL.md        # Technical reference
├── CHANGELOG.md        # Version history
└── data/tables/
    ├── master.csv      # Daily nutrition + tags (pipe-delimited)
    ├── combined.csv    # Wearable data
    └── library.csv     # Food library backup
```

---

## master.csv format

```
date|kcal|protein|carbs|fat|notes
15/06/26|3506|188|18.4|265|Chemotherapy, 76min Walking, 45min Resistance
```

---

## Activity MET values

| Activity | Easy | Moderate | Hard |
|----------|------|----------|------|
| Walking | 2.8 | 3.5 | 4.5 |
| Resistance | 3.0 | 5.0 | 6.0 |
| Cycling | 4.0 | 6.8 | 10.0 |
| Custom exercise (generic) | 3.5 | 5.0 | 7.0 |

`kcal = MET × weight(kg) × duration(hours)`

Walking and any custom activity flagged distance-based also gets effort auto-calculated from pace + distance — see TECHNICAL.md for the full pace-band reference.

---

## Nutrition targets (current)

These are user-configured in Settings (`mh_target_kcal`, `mh_target_protein`, etc.) and read fresh via `getTargets()` — not hardcoded.

| Metric | Target |
|--------|--------|
| Calories | 3,223 kcal base gain-phase (+ activity) |
| Protein | 166g (1.8g/kg) |
| Carbs | ≤50g standard / ≤75g occasion / ≤75g holiday |
| Fat | ≥240g (≥65% of calories, GBM therapeutic floor) |
| Water | 2,000ml (+ 500ml/hr exercise) |

---

## Tech stack

- Single-file HTML/CSS/JS PWA (~900KB)
- Claude (Anthropic), Gemini (Google), and ChatGPT (OpenAI) via a shared Cloudflare Worker proxy — Claude for all standard AI features, all three in parallel for the multi-AI consensus check
- Open Food Facts API (barcode)
- Web Speech API (voice input)
- Python HTTP server (Termux/Android)
- GitHub Pages (hosting)

---

## Why it exists

Built following a GBM diagnosis. My therapeutic ketogenic protocol requires precise macro tracking — this makes that possible daily. See [why-free.html](why-free.html).

*Built with Claude by Anthropic.*
