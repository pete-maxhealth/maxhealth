# MaxedHealth Changelog — Phase 17 (v3.10.466 – v3.10.471)

Continuation of the same session, spanning three threads: a genuinely useful debugging tool built specifically to solve a real, previously stuck device (Jill's), a long-standing structural bug finally caught by that same tool, and a substantial two-part feature (personalised walking effort, then real trend-based auto-adjustment) that grew out of what started as a simple question about pace classification.

## Remote Diagnostics — App Health Check + `/system-status`

- New server endpoint (`/system-status`) surfaces the real auto-update log, crontab contents, and whether `crond`/`server.py` are actually running — added specifically so a stuck device could be debugged **remotely**, without needing Termux command-line access on the affected phone at all.
- Wired into the existing "🩺 Run health check" button — one tap, then "📋 Copy all text" to send the output to whoever's helping debug.
- **This is what actually solved Jill's device.** Confirmed, end-to-end, on a real device that had been stuck for days: the health check first correctly showed `crond` wasn't running at all (root cause, not yet fixed at that point), then — after `crond` was restarted — showed the real log entries proving auto-update genuinely worked on its own at the very next scheduled tick, jumping five versions in one clean, unattended update.

## Long-Standing Div Balance Bug — Found by the Tool Above

- Building the health check's own version-sync check surfaced a real, pre-existing structural bug: a duplicate, prematurely-placed `</div><!-- /app-wrapper -->` closing the app's outermost wrapper in the *middle* of the document, with the correct matching close already existing at the true end. Different comment styles between the two suggest this had been sitting there for a while, silently — not something introduced this session.
- Found via a proper stack-based HTML parser after simpler counting methods (including the crude raw-text `grep` this project had been relying on) proved unreliable — a raw count happened to look "balanced" for a long time purely because HTML-shaped text sitting inside JS strings was being counted alongside real markup.
- **`bump_and_deploy.sh`'s own safety check had the identical blind spot** — it used the same unreliable raw-count method, meaning it could produce both false-positive aborts (blocking a genuinely correct fix, which is what actually happened) and, more concerningly, false-negative passes if JS-string content ever happened to mask a real imbalance. Fixed to use the same script-stripping method as the in-app Health Check, so the two can never disagree with each other again.
- Also fixed the exact two-places version drift `bump_and_deploy.sh`'s own header comment already warned about — the `APP_VERSION` const had gone stale independently of the display text it's supposed to stay in sync with, for reasons unrelated to the script (a file was shared before a manual edit was made).

## Setup Wizard & Advanced Tools Reorder Bug

- "Redo Setup Wizard" made hideable and reorderable, matching every other settings section — previously a standalone block using different, ad-hoc markup.
- **Found a real bug affecting three existing sections**: Log Mutation Debug, Save Debug Trace, and Settings Change Log were all genuinely, correctly positioned inside the fixed "⚠ Advanced — Troubleshooting Tools" box in the source HTML, but were missing from that box's reorder-exclusion list. The generic reorder system was picking them up and physically moving them out of Advanced Tools via `appendChild` — not hidden, just relocated somewhere nobody would think to look for a debug tool. All three now correctly excluded, matching their siblings.

## Personalised Walking Effort & Activity Level

- **Real research first**: confirmed there's no single correct universal walking-pace threshold for "brisk"/moderate effort — even the AHA (≥2.5mph) and CDC (≥3.5mph) officially disagree, explicitly because it depends on individual fitness. Multiple peer-reviewed studies warn fixed thresholds "may misclassify" intensity for exactly this reason.
- **Activity Level is now a genuine, persistent Profile setting** — previously it was asked once during onboarding, used for a single TDEE calculation, and then discarded entirely with no way to view or change it afterward.
- **New fitness-adjusted walking pace bands**, four tiers anchored on the real AHA/CDC figures rather than arbitrary numbers, replacing a single fixed scale that had the same "brisk" pace meaning completely different things depending who was walking.
- **Found and fixed a real internal inconsistency**: two separate, independently-maintained pace-classification systems existed in the code (one for auto-suggesting an effort label from a logged pace, one for the reverse) and had drifted to disagree with each other even before personalisation was added. Both — plus two further consumers found along the way — now read from one shared source.
- **Full Formulas & Technical Reference documentation** added, including an honest flag about one related thing *not* yet fixed: MET calorie values for walking aren't pace-adjusted the same way yet, so calorie estimates outside the "moderately active" tier may be very slightly off until that's addressed too.

## Activity Level Auto-Switch

- Directly building on the above: the app now detects **sustained, genuine change** in real step-count data and adjusts Activity Level automatically, rather than requiring it to be manually kept up to date as someone's real fitness changes.
- Reuses the app's own existing TDEE step-count thresholds (already closely aligned with the real, widely-cited Tudor-Locke & Bassett 2004 classification, independently confirmed via research) — one consistent definition of each tier, not a second one invented separately.
- **Deliberately more noise-resistant than the existing weight/goal auto-switch it's modelled on**: rather than requiring every single day in the check window to individually match (which a single low-step rest day would break even during genuine sustained improvement), it checks whether the smoothed 30-day rolling average, computed as of each of the last N days, has consistently agreed on a different tier throughout. Proven with real simulated tests: a genuinely noisy but sustained improvement correctly triggers; a stable match correctly doesn't; a short vacation-week spike correctly gets recognised as not sustained rather than falsely triggering a permanent change.
- Improvement gets a real celebration (matching the existing ketosis-streak-milestone pattern); a decline gets a plain, factual notification only — informed either way, celebrated only when it's genuinely something to celebrate, as specifically requested.
- New Activity Level History, mirroring the existing Condition History pattern exactly, so a later auto-switch (or manual change) never retroactively distorts how older logged days get interpreted by AI reports.
- **Two genuine pre-existing bugs found and fixed along the way**, unrelated to what was being built: `mh_notif_autoswitch` was being included in backups but never actually restored from one, and Condition History's own textarea was never populated when Settings first loaded — only ever got filled in as a side effect of something else happening first, meaning a fresh visit could show blank even with real history genuinely stored.

## Known Outstanding Items
- Health Connect bridge app (Kotlin) written but not yet built/run in Android Studio — first build pending
- Heylo crackerbread camera/photo logging reported as "hit and miss" — not yet investigated
- MET calorie values for walking are not yet pace-adjusted the same way the effort-label bands now are (see above)
- Phase 13 and 14 changelog entries were never written up in detail — the live version history has real gaps this file doesn't cover
- Garmin data quality comparison against RingConn/Withings not yet completed
- Coeliac disease and iron deficiency conditions researched and evidence-graded, but deliberately not added — would need ingredient-level allergen flagging and nutrient-timing features respectively, not just another dropdown entry

# MaxedHealth Changelog — Phase 16 (v3.10.451 – v3.10.465)

A single very long session covering three distinct threads: real bug fixes found through direct use (recipe substitution, the polyols/net-carbs feature end-to-end, several condition-aware calculation gaps), a genuinely new feature (site-wide search), and the start of Health Connect integration (server-side complete, native Android bridge app written and pending its first build).

## Recipe & Substitution Fixes

- **Substitute picker pre-fill bug** — tapping the swap icon on a flagged, unmatched ingredient pre-filled the search box with the entire raw label ("⚠️ mascarpone cheese — add nutrition") instead of just the food name, finding poor or no matches until manually retyped. Fixed, scoped specifically to flagged rows so ordinary resolved ingredients with their own parenthetical text aren't mangled by the same stripping.
- **Missing "+ add ingredient" button** — the recipe builder had no way to add a new ingredient to an already-created recipe, only during initial creation. Added, reusing the existing library-add mechanism.
- **Recipe ingredients/steps could silently blank out entirely** — a single malformed ingredient (missing its name field) threw an uncaught exception mid-render, and since the list only gets assigned to the page after the whole render completes, one bad item took the other eleven down with it with no visible error at all. Now wrapped so a broken item shows as a specific, diagnosable red error row while the rest of the list renders correctly — this is what actually caught and fixed the real corrupted ingredient (mascarpone) once deployed.
- **Library/substitute picker had no reachable way to cancel** — the Cancel button existed but sat below a potentially long, scrollable list with nothing visible above it. Added a sticky close button pinned to the top regardless of scroll position, plus tap-outside-to-close.

## Net Carbs & Polyols (UK/EU labelling)

- **Polyols now genuinely subtracted from net carbs**, not just fibre — matching UK/EU convention and directly relevant given how often ketogenic recipes lean on erythritol and similar sweeteners. Sourced only from real barcode/OpenFoodFacts data (`polyols_100g`), never AI-estimated from photos or descriptions, matching the same accuracy principle fibre already followed.
- Threaded through the full chain: barcode extraction → recipe ingredients → the actual logged entry (found and fixed a pre-existing gap here too — fibre itself was missing from the final logged object at one specific step).
- **Found eight separate places checking raw carbs directly** instead of the net-aware calculation once this was built out properly — most visibly the ketosis status badge itself, which could show "BORDERLINE" in gross mode and "DEEP KETOSIS" in net mode for the exact same day. Also fixed: the "Ketosis check" and "What's remaining?" saved prompts, the carb-ceiling-hit warning, a second separate remaining-carbs calculation, History tab's per-day compliance indicator, and two internal streak/pattern-compliance checks.
- Made polyols clearly visible at the moments that matter — barcode scan screen, save-to-library confirmation, logging confirmation, and a small icon on recipe ingredients that carry them — rather than buried as one more number in a long stats string.

## New Conditions: Migraine & Cluster Headache

- Added as full conditions alongside GBM/Epilepsy/Strict Ketosis, following real research: genuine RCT evidence for migraine (including a 74% vs 6% responder-rate trial), earlier-stage but real published evidence for cluster headache (open-label trials, a formal Italian expert consensus statement). Both explicitly framed as promising rather than established standard-of-care, unlike GBM/epilepsy's more settled evidence base.
- This required going well beyond the Settings dropdown — found and fixed **8 separate places** where GBM/epilepsy get special treatment for the shared "≥65% fat therapeutic ratio" trait, updating all consistently. One related spot was deliberately left untouched: an Insights panel that mixes the shared fat-ratio trait with claims specifically about *GBM tumour-outcome research*, which doesn't transfer to a headache condition and would have been actively misleading to extend.
- **Found `CONDITION_META` (the table that actually drives the AI's condition-awareness across Ask AI, AI Reports, and trends) was missing migraine, cluster headache, *and* `recomp`** — meaning AI advice was silently generic for all three despite the UI looking condition-aware. Fixed with real evidence citations for each.
- **Found a second, independently-hardcoded condition→ceiling mapping in onboarding** that only covered 2 of what are now 9 conditions — same class of drift bug as `CONDITION_META`, fixed by routing through the same shared function instead of a second copy.
- **Onboarding expanded from 4 to all 9 conditions** — previously only offered GBM, T2 Diabetes, Recomp, and General, meaning Epilepsy, Strict Keto, T1 Diabetes, Migraine, and Cluster Headache were only reachable by switching later via Settings, with no indication that was needed.
- Added `recomp` (Body Recomposition) to `CONDITION_META`, `strict_keto` and `recomp` to a few other spots — pre-existing gaps found while doing this work, not new to this session.

## Condition History & Period-Aware AI Reports

- New "Condition History" tracking, following the exact same proven pattern as the existing Weight Phase History feature — auto-logs on every genuine condition change (Settings and onboarding both), so a later condition change can't retroactively distort how old, already-logged days get judged.
- `buildPatientContext()` can now filter to a specific condition's real period(s) and judge those days against that period's own actual carb ceiling, rather than whatever's set today — while the default (no filter) behaviour stays exactly as it was, since that's the right choice for a whole-history report.
- Rather than a dropdown selector, **Ask AI and Full Summary are now period-aware automatically** — whenever more than one condition has genuinely been used, a real date-ranged "Condition Periods" block gets included in the prompt (silently absent otherwise), and the AI does its own grouping/comparison from the day-level data it already receives. Supports genuinely natural questions like "compare my general and migraine periods" without needing an explicit filter UI at all.
- Fixed a same-day correction bug (mis-clicking a condition and correcting it moments later created two spurious log entries for a period that never really existed) and a `NaN%` compliance bug that would have appeared for a condition-filtered period with zero logged days.

## Site-Wide Search

- New 🔍 icon in the header, always accessible, opens one search box covering Library, Recipes (the same underlying view, so genuinely one search), Saved Prompts, and a curated list of every real Settings section across all three sub-tabs (Manage/Customise/Import).
- First version missed the entire Import sub-tab and had two mislabelled settings entries, found and fixed once real search terms (Withings, Zepp, android) came back empty — added keyword synonyms for device/brand names so those terms correctly surface the right settings section even though the section's own display label doesn't contain them.
- Fixed collapsed sections being unreachable from search results — `scrollIntoView` on a `display:none` element does nothing, so a search result for a currently-collapsed section would silently appear to do nothing at all. Now expands the section first if needed.

## Health Connect (Android) — server-side complete, native app pending first build

- Researched and confirmed the real current Health Connect SDK (`androidx.health.connect:connect-client:1.2.0-alpha05`) — this only exists as a compiled native Android API, no web or shell-accessible path at all, confirmed before writing any code rather than assumed.
- **Server-side fully built and tested**: new `extractors/health_connect.py` (parses the bridge app's JSON export, same conventions as every other extractor), a `server.py` branch recognising the export filename with matching diagnostics for near-misses, and full registration in `update_health.py`'s device list and precedence tables — deliberately lowest priority in every list, since it's an aggregate of whatever a device's own more detailed export would already provide directly.
- **Native bridge app written** (Kotlin) — minimal by design per the explicit "invisible, no overhead" requirement: request Health Connect permission once, then a WorkManager background job syncs hourly with no further interaction needed. Reads steps (via aggregate, avoiding phone+watch double-counting), sleep, HRV, and weight; writes to the public Downloads folder via MediaStore, landing exactly where Termux's existing pipeline already looks.
- Confirmed (researched properly, not assumed): phone-based step counting flows into Health Connect automatically on Android 14+ with zero extra work, so this covers phone-only users for activity tracking without a separate code path. Sleep/HRV/SpO2 remain a genuine hardware limitation — no software approach changes that.
- **Not yet done**: the actual Android Studio build — written but never compiled, same status the Wear OS project reached before being discontinued. This needs laptop access to progress further.

## Other

- **Wear OS watchapp discontinued** — decided against building a second, separate watch interface given the existing Zepp/Amazfit one already does the job well. Kept as accurate historical record in this changelog rather than removed, since the work and its lessons (the same field-shape bug caught before being repeated) are still genuinely useful reference. GitHub repo archived, local project folder cleaned up.
- Investigated (properly researched, not guessed) nutritional evidence for four other candidate conditions — coeliac disease and iron deficiency both have very strong evidence but need a genuinely different kind of feature (allergen flagging, nutrient-timing) rather than fitting the carb-ceiling model, so both stay parked rather than force-fitted in.

## Known Outstanding Items
*(See the Phase 17 entry at the top of this file for the current list — the items below were carried forward there during this documentation pass, rather than duplicated in two places.)*

# MaxedHealth Changelog — Phase 15 (v3.10.273 – v3.10.450)

Phase 13 and 14's detailed entries were never written up (see Known Outstanding Items below) - this entry starts from where the live version history resumes. A genuinely large session spanning wearable development, several rounds of real-device bug hunting on both Pete's and Jill's phones, and a fair amount of infrastructure most of which won't be visible as a feature but fixes something that was quietly wrong underneath.

## Wearable Development

**Zepp OS watchapp — first real working build**
- Found and corrected a run of wrong assumptions from earlier, undocumented sessions: a phantom `@zeppos/router` package that was never real, `@zeppos/ui` used instead of the actual runtime module `@zos/ui`, an `app.json` written against the wrong schema version, and a TypeScript codebase built against Zeus CLI, which only compiles plain JavaScript
- Converted the whole watchapp to plain JS, corrected `app.json` against the real v2 schema and the Amazfit Active 2's actual device data, and got a genuine first successful `.zab` build
- The `/pattern-signals` field shape assumed while building this (flat fields like `breakfastStart`) didn't match the real server response at all — corrected against a live `curl` test of the actual endpoint

**Wear OS data layer — same field-shape bug caught before it was repeated**
- Room database, repository, and sync manager built for the Galaxy Watch companion, then found to have the identical wrong-field-shape assumption as the Zepp side above
- Rebuilt to store the real response as a single JSON blob rather than modelling nested objects across flat SQL columns, since this cache is always read/written as a whole and never queried field-by-field
- Configurable phone IP added rather than hardcoded `127.0.0.1` — a watch and phone are separate devices, so localhost can never reach the phone's own server no matter how the earlier Zepp build had assumed it would
- UI (Compose, Material3, `TransformingLazyColumn`) built against verified current API samples rather than trained-memory assumptions, given how much the Wear Compose library has moved since
- **Subsequently discontinued** — decided against building a second, separate watch interface when the existing Zepp/Amazfit one already does the job well. This section is kept as an accurate record of the work and its lessons, not as a sign it's still planned.

**Pattern-learning backend actually deployed for the first time**
- `pattern_detector.py` and the `/pattern-signals` endpoint had been built and tested in prior chat sessions but never actually copied to the live device or wired into `server.py` — every real call had been silently returning "unknown endpoint" this whole time
- Deployed properly, confirmed live against real logged data
- Its hardcoded "Day 2" / "Day 5" framing replaced with honest reporting of what's actually available — a `signals_available` breakdown and a real day count computed from the real data span, rather than an assumption baked into the response regardless of how much history genuinely exists

## Nutrition & Recipe Accuracy

**Recipe totals — a million-kcal chicken breast**
- A library entry with `portion: "1g"` (should have been `"100g"`) caused a 1000× scaling error for any recipe using it — root cause was the portion-scaling math faithfully doing what it was told against a mislabelled portion, not a logic bug
- Fixed with a plausibility check (nothing real exceeds ~900 kcal per gram) that falls back to 100g and warns, and the scaling logic itself consolidated into one shared helper — previously triplicated across three separate save paths, which is exactly how a bug like this can exist in one place, get "fixed," and still be live in the other two

**Portion sizes missing from logged history**
- Multi-item meal entries never saved a portion size at the top level even though each individual food item carried its own — fixed at the source for new entries, and the history display now falls back to the item's own amount for anything logged before the fix, so old entries get portions too

**Ingredient substitution — built, then redesigned after a real near-miss**
- Full substitute system built across the recipe builder, Cook Mode, and suggested-meal combos, sharing one picker flow rather than three separate implementations
- First version auto-matched the closest library item and asked for confirmation — a fuzzy match suggested peanut butter as a substitute for dairy butter (100g vs 2,200+ kcal worth of fat, sharing only the word "butter"), which is a category of mistake a human choosing from a real list can't make regardless of how good the matching heuristic is
- Redesigned to open a genuine searchable picker instead of auto-matching, with an online-search fallback when nothing in the library fits
- Nut butters (peanut/almond/cashew) now correctly cross-match each other as reasonable substitutes, while cocoa butter and shea butter stay excluded — grouping every "___ butter" together would have just been a different flavour of the same mistake

**Save-to-library silent overwrite**
- Checking a box meant to save a new item could silently overwrite a completely different, differently-named existing item if it fuzzy-matched — the box defaulted unchecked with a small warning line, but ticking it without noticing the warning meant an unrelated library entry's real data got quietly replaced
- Routed through the same careful compare-and-choose modal the manual Add Food form already used (real side-by-side values, an explicit "same thing, overwrite" vs "different product, save separately" choice) rather than patching the separate, less careful mechanism that had grown up around meal logging specifically

## Data Import

**Withings import — the same hardcoded name existed in two separate files**
- `server.py`'s Download-folder scan and `extractors/withings.py`'s own detection both independently checked for the literal filename fragment `data_pet_` — Pete's own name, from testing only ever against his own export
- Real Withings exports are named `data_{account name}_{timestamp}.zip`, so this silently rejected every other family member's genuinely correctly-formatted export
- Both fixed to match the real filename shape rather than any specific name; the in-app Sync log now also reports exactly what it found and why when nothing matches (name, size, whether it opens, whether it looks like a genuine export the pattern just missed) rather than a bare "nothing found"

## Auto-Update Infrastructure

**Devices could silently run stale code indefinitely**
- No mechanism existed for an installed device to ever catch up with GitHub on its own — every fix required someone to manually `git pull` on that specific device, which is exactly how one real device ended up running code from before several rounds of fixes without anyone realising until symptoms stopped making sense against what was supposedly already fixed
- New `mh_autoupdate.sh` checks GitHub every 30 minutes via cron, and once immediately on every boot — converges via `git reset --hard` rather than attempting a merge, appropriate for a pure end-user device that should never carry real local edits
- `mhstart` itself had a path bug — `cd`'d one directory too shallow, which silently failed and fell through to running from whatever directory the caller happened to already be in, rather than failing loudly. Fixed, and properly installed to `$PREFIX/bin` so it works from anywhere rather than only when someone happens to already be in the right folder
- All of the above folded into `setup.sh` itself, so every future fresh install gets working auto-update and a correct `mhstart` automatically, not just the devices patched by hand this session

## Accuracy & Consistency Fixes

**Vitals score contradicted the pattern-learning backend on the same data**
- Scored HRV against a fixed 80ms population target while the pattern-learning backend elsewhere correctly judged the same HRV reading as "Excellent" relative to the person's own baseline — the same number was being called both "Low" and "Excellent" in different parts of the same app
- Fixed to score HRV against the person's own recent baseline (last 30 readings), consistent with how the backend already treats it

**AI Reports — a fabricated fat target and a missing "today"**
- A hardcoded `247` was presented as a real personal fat target any time the actual target was missing — the combination it produced (247g fat, 1550kcal total) was internally impossible on its own, since 247g of fat alone is over 2,200kcal. Now reports honestly that the target isn't set rather than inventing a number
- Separately, this app only folds "today" into tracked history via a nightly rollover — so a question asked mid-afternoon about "today" had no way to see today's real entries at all, and silently answered using a multi-day average (or the most recent *completed* day) mislabelled as if it were today's actual total. Fixed with an explicit, clearly-labelled block pulled live from the same in-progress log the dashboard itself reads from

**Diabetes condition silently did nothing to nutrition targets**
- Onboarding saved the diabetes condition as `'t2d'` while every other check in the app looked for `'t2_diabetes'` — anyone selecting diabetes at onboarding got none of the diabetes-specific behaviour anywhere, permanently, from a string that simply never matched
- Separately, changing condition later via Settings never cascaded to update the carb ceiling at all, despite the dropdown's own label text explicitly promising a specific number ("Type 2 Diabetes — Low carb ≤100g")
- Both fixed; the ceiling-defaults mapping extracted into one shared function used by both onboarding and the Settings change handler, so the two can't drift apart from each other again the way they just had

**Patterns card's "not enough history" message was actively misleading**
- Fired regardless of *why* nothing was found, including against a 790-day total history — which said nothing about how many of those days also had paired wearable sync (sleep, steps), which is what these specific comparisons actually need
- Now reports the real counts for each requirement separately, so the actual bottleneck (usually wearable sync coverage, not total logging history) is visible rather than a generic message that looked wrong against a large total day count

## Saved Prompts Library

- Replaced two separate sets of hardcoded quick-question pills (the Log-tab chat bar and the Reports-tab Ask AI panel) with one unified, searchable, editable library — add, edit, delete, all shared between both locations rather than two systems that could drift apart
- Voice dictation added for typing new prompts, reusing the existing water-logging voice pattern rather than a new implementation
- Real usage tracking added — prompts sort by how often they're actually run, with visible sort controls (Most used / A–Z / Recently added) rather than an invisible default
- Went through a few rounds of direct revision based on real use: a pin/unpin mechanism was built, then replaced entirely by a single "Browse" entry point once it became clear that showing several pills in a row just competed for attention with everything else on screen — sometimes the simpler version is the right one, not the more configurable one

## Known Outstanding Items
*(See the Phase 16 entry at the top of this file for the current list — the items below were resolved or carried forward there during this documentation pass, rather than duplicated in two places.)*

# MaxedHealth Changelog — Phase 12 (v3.10.202 – v3.10.272)

The biggest single session in the app's history — roughly 70 versions. Most of it was infrastructure and reliability work that doesn't show up as a visible feature, but fixes a genuine, sometimes months-old bug underneath something that looked fine on the surface.

## New Features

**Log food to a past day**
- History → any day → "🍽 + Add food to this day" routes into the exact same AI-parsing pipeline used for today's logging (text, photo, barcode, library — all of it), with a persistent yellow banner making clear which day is being targeted
- Recalculates that day's totals from its full log automatically — no manual arithmetic
- Solves the recurring problem of a missed or mis-logged item on a previous day requiring the day's totals to be hand-adjusted

**Multi-AI consensus check**
- "🔍 Verify across 3 AIs" on any logged item — Claude, Gemini, and ChatGPT independently estimate the same food in parallel via the Cloudflare Worker, one round-trip
- Deliberately does not average or pick a winner by default — three estimates agreeing closely is a genuine reassurance signal; disagreeing by more than 25% on calories is flagged as "find a real label, don't trust any of these"
- Each provider's own numbers are checked for internal consistency (protein×4 + fat×9 + carbs×4 against its own stated kcal) — catches an estimate that's internally sloppy even before comparing it to the others
- Per-provider checkboxes let you exclude an outlier before applying an average to a single item; works per-item within a multi-item meal, not just on a whole plate at once
- Requires Gemini and OpenAI API keys configured as Worker secrets in addition to the existing Anthropic one — genuinely free on Gemini's tier for occasional use, small real cost on OpenAI (no persistent free tier)

**Activity Credit Balance**
- New card in Insights → Trends: rolling-window (default 14 days, adjustable) tracking of exercise calorie credit earned vs actually eaten back, built from real stored history (`day.exercises`, already precomputed), not an estimate
- Goal-aware interpretation — under 25% unclaimed is treated as noise regardless of goal; above that, framed differently for maintain (a real compounding deficit), gain (quietly eating into the intended surplus), and lose (expected in moderation, flagged if it's grown larger than intended)
- Exists because a single day running under an exercise-boosted target is genuinely harmless, but the same pattern repeating often compounds into something real without ever tripping a single day's warning

**Phase-aware calorie context**
- Remaining Today now distinguishes being under the exercise-boosted target (harmless unclaimed activity credit) from genuinely being under the base target (real under-eating) — the two were previously indistinguishable from the headline number alone
- Worded differently depending on the actual Goal/Phase setting (maintain/gain/lose), since "under the boosted number" means something different for each

**440ml Pint water preset**
- Added alongside Glass/Can/Bottle/Custom on the hydration bar

**find_orphans.py**
- Standalone maintenance script (not part of the app) — flags functions/variables that appear only at their own declaration and never anywhere else, plus duplicate function names, as a manual review checklist
- Deliberately a heuristic, not an auto-delete tool — a name showing up here can still be genuinely needed (a reserved feature, something called in a way static text-matching can't see)

## AI Infrastructure — found this session, most of it long-standing

**Cloudflare Worker was silently overriding every request**
- Hardcoded `claude-haiku-4-5` and `max_tokens: 500` regardless of what the app actually requested, for every proxy-routed call — meaning anyone without their own API key (the cloud version's default) had been running on a smaller model with a harder token cap than any individual feature was ever designed around
- Fixed to forward `model`/`max_tokens`/`tools` from the actual request, falling back to sensible defaults only if the client omits them

**Direct-API-key path was structurally broken since it was built**
- Missing the `anthropic-dangerous-direct-browser-access` header required for any direct browser call to Anthropic's API — without it, every direct-key request was silently blocked as a CORS violation, surfacing only as a generic, unhelpful "Failed to fetch"
- Separately, `callHealthAI()`'s direct-Claude branch had **no request body at all** in the fetch call — sending Anthropic a genuinely empty request every time a direct key was configured, which Anthropic reported back as "zero-length, empty document"
- Both fixed; this was likely the actual cause of "Check what fits from my library" failing intermittently for weeks, previously misdiagnosed as an exposed/invalid key several times over

**Wrong localStorage key bypassing the shared AI helper**
- Two functions (`suggestMealFromLibrary`, `_processLabelEstimate`) read `mh_api_key` (with an underscore) instead of the actual key name `mh_apikey`, so they always behaved as if no direct key was configured regardless of what was actually set — consolidated onto the same shared `callHealthAI()` helper every other AI call already used correctly

**App Health Check now tests the real function**
- The AI-connection live test was previously a separately hand-built request that happened to be constructed correctly — meaning it could never have caught the missing-body bug above, since it never actually exercised the buggy code path
- Now calls `callHealthAI()` directly, plus a new live multi-AI test section

**Gemini model — settled after two wrong guesses**
- First attempt (`gemini-3.5-flash`) hit genuine "high demand" 503s; switched to `gemini-2.5-flash` believing an older model would be more stable — turned out Google was actively restricting 2.5-flash for new API keys ahead of its official shutdown date
- Reverted to `gemini-3.5-flash` (confirmed current GA flagship, Google's own recommended replacement), with one automatic retry on a 503 after a short delay, matching Google's own documented guidance for this error class

## Data Pipeline

**Sleep data stalled at a fixed date for over a week**
- A folder restructure moved `server.py`/`maxhealth.html` a level deeper without updating the extractors path inside the copy of `update_health.py` that Sync Now actually calls — every sync silently found zero extractors and reported "no data" without ever touching the real ones
- A second, older, disconnected copy of `update_health.py` existed one level up, resolving `BASE` to a completely different (non-existent) data folder — deleted; one canonical script remains
- Amazfit/Zepp AES-256 decryption fixed — `zipfile` cannot decrypt AES regardless of password; `pyzipper` required. Password flows correctly through the existing CLI arg / `ZEPP_PASSWORD` env var plumbing once the decryption library itself was correct

**Cloud deployment found ~100 versions behind**
- `git push` had been silently failing with no error surfaced for an extended period — added explicit push verification to `bump_and_deploy.sh` (confirms local HEAD matches `origin/main` after pushing, not just that the command ran without throwing)
- `.gitignore` added for `__pycache__/`, backup files, and trash artifacts, which had been accumulating as noise in every `git status`

## Logging & Library

**Whole-item scaling bug**
- A food with a non-numeric amount (e.g. "1 can") defaulted its scaling baseline to 100g — correcting the displayed amount to the item's true size (e.g. 440ml) multiplied already-correct total values by the wrong factor instead of leaving them alone
- Fixed to also check the food's name for an embedded size before falling back to a guess, and to warn explicitly when no real size can be found anywhere rather than silently assuming one
- Live auto-scaling added to the per-ingredient edit modal separately — previously had zero connection between the amount field and the macro fields at all

**Fuzzy-match false positives, two distinct causes found**
- An unrecognized brand on one side let generic word overlap alone trigger a false match ("turkey sausage Asda" matched "Turkey Sausages x2 Oakhahen" on 2 of 3 words, missing only the brand) — now requires every word to match when one side's brand can't be identified at all, rather than falling back to a partial threshold
- Apostrophes broke matching entirely as raw text — "Tennents" (typed) never matched "Tennent's" (library) since the apostrophe interrupts the character sequence; affects any possessive brand name (McDonald's, Cadbury's, etc.), fixed by normalizing apostrophes out of both sides before comparing

**Fuzzy-match confirmation UI was hiding its own real choices**
- Both actual options ("Overwrite" and "save separately") existed in the code but sat behind an unlabeled tap-to-reveal step with nothing signalling it was interactive — looked exactly like only one action existed. Now shows both choices and the value comparison immediately

**Carb auto-correction wrongly zeroing processed meat products**
- Sausage, chorizo, black pudding, pâté and similar were being treated as "plain meat" (definitionally zero carbs) when they're compound products with real fillers/binders that do carry carbs — a turkey sausage's genuine 8.6g label carbs were being zeroed to 0g
- Added these to the exclusion list the correction already used for breaded/battered/sauced items

**"Haven't eaten this" wasn't actually being honoured**
- Tapping "Just add to library (haven't eaten this)" showed a toast reminder but still presented the normal Log It / Save / Cancel choice, relying on a second correct tap — one wrong tap logged food that was never eaten as if it had been
- Fixed: once that intent is declared, Log It is no longer offered at all for that preview, with a note explaining why

**Silent failure saving to library with no pending item**
- A completely silent early exit if the item hadn't finished loading when "save to library" was tapped — now shows a real message, plus diagnostic logging throughout the whole save path for any future case

**Impossible-mass warning now suggests a number**
- Previously flagged that protein+fat+carbs exceeded a food's stated weight without saying what the weight should actually be — now states the real minimum plausible weight, calculated from the same numbers already on screen

**Photo portion-estimation prompt rewritten**
- Now prioritises visible cutlery/glassware as a size reference over the plate itself (a fork is ~18-20cm almost universally; plates vary 23-32cm+ across venues)
- Explicit guidance to account for stacked/overlapping food (sliced meat, piled sides) rather than judging only the visible top-down area
- Asks the AI to flag its own estimates as approximate (~±20%) instead of stating them with false precision

**Raw JSON leaking into chat on AI self-correction**
- When the AI second-guessed itself mid-response (e.g. logging something as water, then catching that it has real calories and correcting to food), the existing JSON-recovery regex was greedy — it swallowed both JSON blocks *and* the English commentary between them into one invalid blob, which failed every repair attempt and fell back to dumping the raw text as-is
- Fixed with proper brace-depth-counted extraction of each complete JSON object individually, preferring the last valid one (since a self-correction means that one is the real answer)

## Dashboard & Activity

**Exercise credit banner disconnected from the real calculation**
- The "+Xkcal from activity" banner was a flat-rate guess based on tag text alone (+150 for any "cardio" tag, whether it represented a 10-minute walk or 3 hours) — completely different from the proper MET-based calculation (`MET × weight × hours`) already powering the dashboard's own total, which could show a wildly different, larger number for the same day
- Unified onto the same real calculation the dashboard already used, so the banner and the dashboard can no longer disagree

**Misleading "below baseline" headline**
- On a day with a substantial logged walk, the headline compared only the *incidental* (non-walk) step remainder against the daily baseline and phrased it as if it were a verdict on the whole day's activity — reworded to make clear it's only describing steps outside the logged walk when one exists

## Settings & Dashboard Polish

**Manage screen defaulting every section open**
- A collapse-by-default mechanism already existed but had every section wired to default open regardless — defeating the entire purpose and making Manage a wall of expanded cards on every visit
- Fixed to default closed except Profile; also found 3 sections missing from the list entirely, meaning they could never even remember a manually-collapsed state

**Dismissible dashboard warnings**
- Goal Check and the Ketosis Zone alert can now be dismissed — deliberately session-only (not persisted to localStorage), so a genuinely ongoing issue reappears next reload/day rather than being silenced forever by one dismissal

**Reset button text bleeding**
- Adding a 6th button (Pint) to the hydration row caused Reset's text to overflow past its own container — added overflow/ellipsis safety to the button style so this can't recur regardless of button count

**Demo Mode reachable from Settings**
- Previously only offered on first-run onboarding; added a link under Settings → About, confirmed safe to trigger mid-session (snapshots real state in memory, never touches localStorage during the swap)

## Website

**Donation messaging corrected to be actually honest**
- "It cost nothing to make it free" was simply false — real API and Claude subscription costs land on Pete, not end users; corrected across `story.html`, and the donation ask on `why-free.html` reframed from "support my costs" to "keep the project running"

**Third-person self-reference converted to first person**
- Across `story.html` and the patient guide's narrative prose — structural elements (bylines, signatures, section headings, table-of-contents entries) deliberately left as-is, since those function as attribution/navigation rather than narrative voice

**Wearables list clarified**
- Was worded like a hard requirement list; now states these are the *tested* devices specifically, and the underlying pipeline works with any export giving one row per day

## Process

**Div-balance validation methodology corrected**
- Had been stripping `<script>` content before counting balance, which misses the vast majority of this app's actual HTML (built dynamically inside JavaScript template literals) — now validates the full file, matching what the deploy script itself checks, after this exact gap let a real deploy-blocking imbalance go undetected for one release

---



## New Features

**Ketosis impact preview**
- Every "Ready to log" screen now shows the actual effect of logging: calories/protein/fat as before → after against today's real targets, and a clear carb ceiling check — still within it, over by how much, and whether it would end a current streak
- Updates live as the portion amount is adjusted, without losing input focus

**Exercise Offset for carb overage**
- Off by default (Settings). Distinguishes a carb overage meaningfully addressed by that day's logged exercise from one left unaddressed
- Never hides or replaces the raw over-ceiling fact — a genuinely additional layer, not a replacement

**Dashboard traffic-light status dots**
- Small coloured indicators on Calories/Protein/Carbs/Fat
- Carbs uses ceiling logic (green under, red over); the other three use gaining-phase logic by default — under-eating is the real risk on a surplus protocol, not exceeding target

**Weight intention status**
- Derives intention from the actual Goal/Phase setting (not a separate, potentially-conflicting setting) and colours the 14-day trend by whether it's serving that goal
- No-consequence preview mode in Settings — see how the status would read under a different goal, using real weight/trend data, without changing anything real

**Your Journey (full-history view)**
- Weight across the entire tracked history, always, independent of the Today/30/60/All filter
- Points coloured by ketosis status; treatment days marked separately; third colour for exercise-addressed overage when that setting is enabled

**Treatment Analysis (merged with the former Chemo Cycle Analysis)**
- Nutrition, ketosis adherence, and weight compared on treatment days vs standard days
- Detected treatment cycles and a specific comparison against the immediate 7-day recovery window folded in from the old standalone section — same information, one coherent story instead of two overlapping ones

**Carb Pattern breakdown**
- % of days at Strict Keto / Keto / Low Carb — or neutral equivalent tiers for non-keto conditions, since "keto" framing isn't meaningful for diabetes management or general health goals
- Encouragement keyed to adherence against the user's own chosen ceiling, not a ranking against strict keto specifically

**GBM Research Digest**
- Persistent, dated, condition-gated home for real research findings, colour-coded Proven / Early Stage / Speculative matching Monthly Summary
- A "Research Now" live-search attempt was built, tested, and found unreliable (the app's AI calls have no real web search) — replaced with "Copy Research Request", a one-tap prompt to paste into a real chat conversation instead

**Formulas & Technical Reference**
- Every calculation the app uses — BMR, TDEE, MET-based exercise calories, macro ratios, carb ceiling logic — documented in plain language, in-app

**Voice logging, finished**
- One-tap "Log it" directly on the transcript rather than needing to find the separate send button
- Real, actionable error messages instead of raw error codes
- Subtle mic highlight on treatment-tagged days

**why-free.html reinstated**
- Rebuilt with the real JustGiving crowdfunding link, generic (non-itemised) donation framing, and a second option (Headcase Cancer Trust)

**Demo mode seeded with real anonymised data**
- Previously generic placeholder data; now a genuinely rich dataset built from real history — full 151-item library, 30 real days of nutrition/wearable history, real recipes/routines/strength sessions
- Sensitive specifics (weight, supplement names/doses, condition tags) fictionalised; food/exercise/recipe data kept as-is since it isn't personally sensitive
- Found and fixed: supplements had no demo-mode protection at all (no guard on load or save) — now matches the same safe pattern as every other dataset

**ℹ️ info-icon pattern**
- Reusable tap-to-reveal explanation component for features that could be confused with a similar one, without cluttering the screen by default

## AI Reliability

**Unified AI calling — one function instead of nine separate copies**
- Every AI call site (Ask AI, Full Summary, GBM Summary, Oncology narrative, portion estimation, health-context queries, both missed-day calculators, barcode reading) now shares one function
- Real errors surfaced (HTTP status, actual message) instead of a generic swallowed "Could not generate" — this is what made it possible to actually diagnose an Anthropic billing/credit issue instead of guessing at 9 separately "broken" features
- Image support added for vision calls (barcode reading), so that path could join the same shared function too
- Several paths previously always hit the shared proxy regardless of a configured personal API key — now correctly respect a configured key first

## Bug Fixes

**Flat carb-ceiling comparison — found in 8 separate places**
- Weekly Summary, Oncology Report, Report Summary, the ketosis streak counter, Treatment Analysis, GBM Stats, the AI Brief generator, and Sleep & Ketosis correlation were all comparing every day against a flat standard-only ceiling, regardless of that day's actual logged mode (occasion/holiday days incorrectly counted as failures)
- Each now judges a day against its own mode's ceiling
- The AI Brief generator specifically had a worse variant: `getTargets().carbs` doesn't exist on the object returned (it returns `{standard, occasion, holiday}`), so the comparison was always `undefined` and adherence was being reported as 0% unconditionally, every time, regardless of actual data

**Library fuzzy-matching — category-mismatch, found in 4 separate functions**
- Generic descriptor words ("white", "slices") were scoring as match evidence with no regard for whether the actual food category matched — "Warburtons white bread" could surface "white cheese" as a match purely on coincidental word overlap
- Fixed in the strict duplicate-check finder first; found the identical bug, unfixed, in three sibling functions (substitute suggestions, Add Food comparison, the duplicate scanner) — all four now share the same food-category disqualification check

**Onboarding: height/age/sex collected but never saved**
- Used for a live TDEE preview during setup but never actually written to the persistent profile keys anywhere in onboarding — a new user would enter this data, see it work, then have it silently discarded on completion
- Fixed at the step where it's collected, plus a defensive re-save in the final "Start Tracking" button

**Print/PDF silently failing in standalone PWA mode**
- `window.open()`-based printing has nowhere to open a new window into once the app is an installed standalone PWA — failed with zero visible error
- Replaced with a hidden-iframe approach that works identically in a normal browser tab or the installed app

**Clinical report buttons never appearing**
- The Clinical export mode was rendering into an old "backwards compatibility" placeholder div, not the real shared output container — Print/Copy/AI-summary buttons were never actually reachable, not just visually broken

**Multi-match library picker going dead after first selection**
- Picking any item cleared the state backing the whole picker before the resulting preview was even confirmed — cancelling that preview left a list that looked interactive but did nothing

**Dashboard/History layout overflow**
- Progress tiles and History day-summary rows switched from cramped single-row layouts to proper 2-column grids after longer text (added target comparisons, percentage figures) no longer fit

**History: no target comparison**
- Added actual/target for every macro on every day, using that day's own mode-aware ceiling — not previously visible at all, only raw totals

## Refactoring

- `updateDashboard`: 413 → 263 lines (4 self-contained blocks extracted, animation logic deduplicated)
- `renderTrends`: 563 → 477 lines (gap-detection extracted, two canvas helpers hoisted out of per-render redefinition, one genuinely dead function removed)
- `processMessage`: 603 → 543 lines (6 keyword-query handlers extracted to named functions)
- Deliberately did not touch the rollover logic, AI-parsing core, or library-matching core during any of the above — extracted only what was clearly safe and self-contained, left the delicate/central logic exactly as it was

## Documentation

- User guide updated with all of the above — two new sections (Dashboard intelligence, Smarter logging), Reports section extended, Demo Mode note added to Setup
- README and this changelog brought current
- Fixed a genuine pre-existing bug in the patient guide (a missing closing `</div>` on the opening-letter container, present since whenever that section was first written) while checking documentation more broadly

---

## New Features

**Library-aware meal suggestions ("📚 From my library")**
- Proposes real combinations of saved library items and Recipes (with proper per-serving math) against today's actual remaining macros — never invents values, only ever uses locked/stored data
- Shows each item's real portion size, not just names
- One-tap logging directly from the suggestion card
- Recipe suggestions reuse the exact same servings-scaling formula as the Recipe Builder itself

**Ingredient substitution flow**
- If a described food doesn't exactly match your library (e.g. wrong brand), offers real alternatives from what you actually have instead of silently falling through to a fresh AI guess
- Works both when no match is found at all, and when you explicitly decline a suggested match
- "Save as new item" option added to the duplicate-comparison screen, for when comparison reveals two genuinely different products rather than a real duplicate

**Ketosis streak milestones**
- One-time celebration messages at 7/14/30/50/100/200/365 consecutive days, shown as both a chat message and a toast (visible regardless of active tab)

**Dashboard & Library section reordering**
- Every section on the Today dashboard (Weight, Day Mode, Ketosis, Macros, Remaining, Macro Ratio, Goal Check, Steps, Activity, Water, Log, Guides & Docs) can be reordered via ▲▼ buttons
- Recipes vs Food Library sections in the Library tab reorderable the same way
- Reports, Manage, and Import tabs also fully reorderable — built as one generic, self-discovering system rather than hand-wiring dozens of sections individually

**Demo mode overhaul**
- "Try a demo first" now seeds realistic sample data across Library, Recipes, Routines, and Strength Training history — previously these sections were completely empty in demo mode, hiding most of what the app actually does
- Built via safe read/write redirection rather than temporarily overwriting real user data

**Library-only ingredient saving**
- New "📚 Just add to library (haven't eaten this)" option when reading a label, for cataloging an ingredient without logging it as eaten today

## Nutrition Logging Accuracy

**Four new sanity checks added to the existing meat-carbs and pure-fat plausibility checks:**
- Atwater kcal-consistency (a food's stated calories must roughly match protein×4 + carbs×4 + fat×9), with an explicit exception for alcohol
- Implausibly low carbs on fruit-named items (the inverse of the meat-carbs check)
- Implausible portion size (under 1g or over 2000g)
- Macro-mass plausibility — protein + fat + carbs in grams cannot physically exceed the food's own stated weight

**Fuzzy-match accuracy (library duplicate detection and substitution)**
- Brand names (Asda, Tesco, Sainsbury's, Lidl, etc.) now correctly disqualify a match when they genuinely differ between query and candidate — previously "double cream is Asda" and "double cream is Lidl" scored identically
- Meat/protein type (chicken vs beef vs pork etc.) now works the same way — previously a single shared generic word like "mince" could match two completely different meats
- Short 2-word queries now require both words to match, not just one — closes the gap where a single generic shared word inflated the match score

**Meal-photo reasoning text**
- AI no longer states its own rough sanity-check total in the message field — previously this could show a different number from the actual, more carefully-calculated logged total, creating a confusing self-contradiction

**Long-meal parsing safety net**
- A named item with every macro at zero is now excluded rather than silently logged — this pattern almost never represents a real food and more likely indicates a parsing failure somewhere in the AI response chain

**Today's summary — fixed missing fat**
- The "show today summary" conversational response was missing fat entirely from its output; now included alongside calories, protein, and carbs

## Data Safety

- "Export All Data" now includes recipes and routines in the JSON backup — previously silently missing
- Corrected misleading "downloads one zip" wording to accurately describe the several separate files actually produced
- Recipe deletion now requires confirmation — previously deleted instantly with no warning

## UX & Organization

- Settings grouped into clear categories (Your Targets, Data & Devices, App Info), with debug/diagnostic tools (Body Comp Debug, Rollover Debug Log) visually and functionally separated from everyday settings via a distinct "⚠ Advanced" warning box
- Recipes vs Meals naming confusion addressed with cross-referencing subtitles in each section, rather than a rename
- Fixed a focus-destroying bug where the reorder system's own render logic was silently kicking users out of text inputs (search box, Daily Steps, custom water amount) on every keystroke

## Donation / Fundraising Page

- Story, cover photo, and donation copy finalized for the JustGiving crowdfunding page and app-linked story page
- Subsequently removed personal fundraising link and photo from the app entirely per decision to direct support toward charity rather than personal fundraising

## Known Outstanding Items
*(See the Phase 15 entry at the top of this file for the current list — the items below were resolved or carried forward there during this documentation pass, rather than duplicated in two places.)*

# MaxedHealth Changelog

## v3.10.39 — Phase 9 (6 Jul 2026)
- **Added:** Goal change (Lose/Maintain/Gain) now automatically appends a timestamped entry to Weight Phase History. No manual entry needed except for historical backdating.

## v3.10.38 — Phase 9 (6 Jul 2026)
- **Added:** ⭐ Full Summary — dedicated one-tap button in Ask AI generating a comprehensive 9-section health analysis (nutrition, weight phases, ketosis quality, sleep, HRV, activity, best periods, areas to improve, protocol verdict). Phase-aware, condition-specific, nil days excluded.
- **Fixed:** Ask AI section title updated with ⭐ star status indicator.

## v3.10.37 — Phase 9 (6 Jul 2026)
- **Added:** Suggested Targets calculator in Settings → Profile. Calculates personalised TDEE (Mifflin-St Jeor × activity multiplier from real avg step count), phase-adjusted calories, protein (1.8g/kg GBM/Epilepsy, 1.6g/kg otherwise), and fat to fill remaining calories. Condition overlay checks ketogenic ratio for GBM/Epilepsy. "Apply these targets →" button applies in one tap. Recalculates when Settings opens or weight updates.

## v3.10.36 — Phase 9 (6 Jul 2026)
- **Added:** Weight Phase History field in Settings. Log intentional weight phases (loss/maintain/gain) with ISO dates, one per line. Used by all AI reports to correctly interpret weight trends — deliberate loss is never flagged as a concern.
- **Fixed:** `savePhaseHistory()` now calls `renderSuggestedTargets()` after saving.

## v3.10.35 — Phase 9 (6 Jul 2026)
- **Fixed:** Nil nutrition days (<100 kcal) now filtered from Ask AI raw data table, Monthly Summary calculations, and `buildPatientContext`. Gap days reported as "tracking gaps, not zero intake" in AI context.

## v3.10.34 — Phase 9 (6 Jul 2026)
- **Fixed:** Report streak now uses `calcKetosisStreak()` which includes today's logged data. Previously the report showed 0 streak even when today was compliant because today's log wasn't included in the history array.
- **Fixed:** Nil nutrition days excluded from protein misses, fat misses and best carbs calculations in report summary.

## v3.10.33 — Phase 9 (6 Jul 2026)
- **Fixed:** JS syntax error — `const trackedCarbs` declaration placed inside a chained expression, breaking all JavaScript. Node syntax check now run on every build before deploy.

## v3.10.32 — Phase 9 (5–6 Jul 2026)
- **Fixed:** File header comment corrected from stale "v2.1.9 Phase 7" to "v3.10.32 Phase 9". The comment was misleading but the file was always Phase 9.
- **Added:** Offline manual entry fallback — when AI is unreachable (flight mode, no network), a manual kcal/protein/fat/carbs form appears automatically instead of an error.
- **Added:** Weight carry-forward — dashboard shows last known weight when today has no reading, labelled "last known". Never writes to data.
- **Fixed:** Watchdog (`mh_watchdog.sh`) was starting server.py from wrong directory, causing `combined_exists: false`. Fixed `cd` path from `app/maxhealth` to `app`.

## v3.10.31 — Phase 9 (5 Jul 2026)
- **Fixed:** Tesco Double Cream fat=0 bug. Three-layer fix: (1) label-locked values (467kcal/50.5g F/1.5g P/1.6g C per 100g), (2) FAT_FLOOR_DB updated with label-confirmed 50.5g, added lamb/pork/single cream, (3) high-kcal backstop — any item >200kcal with 0g fat has fat back-calculated from `(kcal - protein×4 - carbs×4) ÷ 9`.
- **Fixed:** AI fat prompt updated with label-confirmed Tesco double cream values and explicit rule: never return 0g fat for cream/oil/dairy/nuts/eggs.

## v3.10.30 — Phase 9 (5 Jul 2026)
- **Fixed:** Report summary stats (best carbs, protein misses, fat misses) now exclude days with <100 kcal logged, preventing untracked days from skewing statistics.

## v3.10.29 — Phase 9 (2 Jul 2026)
- **Added:** Inline edit (✏) per component row in meal preview. Tap to edit name and gram amount; macros recalculate live from original per-100g base values. Save updates the preview; Cancel reverts.

## v3.10.28 — Phase 9 (2 Jul 2026)
- **Fixed:** story.html links in app used absolute GitHub Pages URL — now works correctly from both localhost and GitHub Pages.

## v3.10.27 — Phase 9 (2 Jul 2026)
- **Fixed:** story.html link path was `docs/story.html` (non-existent subfolder). Corrected to `story.html`.
- **Fixed:** History render — log entries whose description is a mode word ("standard", "holiday", "occasion") now filtered from display. These ghost entries were created by an old rollover bug.
- **Added:** HOL/OCC badge next to date in history header for holiday/occasion days.

## v3.10.26 — Phase 9 (2 Jul 2026)
- **Fixed:** Ghost mode-word log entries filtered from history display.
- **Added:** Day mode badge (HOL/OCC) in history header.

## v3.10.25 — Phase 9 (5 Jul 2026)
- **Fixed:** Carb zone gaps — dropdown labels now use contiguous ceiling values (≤20g / ≤50g / ≤100g / ≤150g). No gaps between zones.
- **Updated:** `CONDITION_META` protocol labels and carb ceilings hint text to match.

## v3.10.24 — Phase 9 (5 Jul 2026)
- **Fixed:** `carer.html` — title and all brand references corrected to "MaxedHealth". Hardcoded carb ceilings replaced with `data.ceilings` from payload. `generateCarerLink()` now embeds actual ceiling values from localStorage.

## v3.10.23 — Phase 9 (5 Jul 2026)
- **Added:** Condition/Protocol dropdown in Settings → Profile (GBM, Epilepsy, Strict Ketosis, Type 1 Diabetes, Type 2 Diabetes, General Health). All AI reports now adapt framing, evidence categorisation and thresholds to the user's condition.
- **Added:** `CONDITION_META` table with per-condition protocol label, evidence note and report framing.
- **Fixed:** `buildPatientContext` and `patientContextBlock` were hardcoded to GBM gaining phase. Now reads `mh_condition` and `mh_goal`.

## v3.10.22 — Phase 9 (5 Jul 2026)
- **Fixed:** Meal/Label toggle was hardcoded to Label as the active state in HTML despite JS defaulting to Meal.

## v3.10.21 — Phase 9 (4 Jul 2026)
- **Fixed:** Step 0 photo classification prompt was too broad. Tightened to binary yes/no: "does this photo show a printed nutrition panel with actual numbers?" Food on a plate is always MEAL PATH.

## v3.10.20 — Phase 9 (2 Jul 2026)
- **Added:** Delete button (✕) per component row in multi-item meal preview.
- **Added:** Step 0 photo classification — AI classifies photo as label or meal before any other reasoning fires.

## v3.10.19 — Phase 9 (2 Jul 2026)
- **Fixed:** When AI asks a clarification question about an ambiguous photo item, the next user reply is now correctly treated as the answer. Stored as `window._pendingClarification`.
- **Fixed:** Sauce double-counting — when a protein is logged "in sauce/curry", sauce is no longer also added as a separate line item.

## v3.10.18 — Phase 9 (2 Jul 2026)
- **Added:** Termux:Boot boot survival — `start-watchdog.sh` runs `termux-wake-lock` and immediately launches `mh_watchdog.sh` on boot.
- **Fixed:** GitHub Pages → localhost auto-redirect blocked by Chrome LNA policy. Removed dead WebSocket probe. Replaced with one-time toast pointing to localhost:5757 shortcut.
- **Fixed:** setup.sh (v3.2) now auto-installs `termux-api`, detects Termux:Boot/API, prompts only when missing.
- **Added:** `buildPatientContext` + `patientContextBlock` — all three report types receive full patient context.
- **Added:** Meal photo ambiguity rule — flags uncertain items and asks before logging.

## v3.10.17 — Phase 9 (27 Jun 2026)
- **Fixed:** Meal photo prompt — removed directional bias. Added Step 4 plate-weight sanity check.

## v3.10.16 — Phase 9 (27 Jun 2026)
- **Added:** `showLocalhostHint()`, `maybeShowHomeScreenTip()`, `offerLocalSwitchIfAvailable()` for post-LNA localhost shortcut guidance.

## v3.10.15 — Phase 9 (27 Jun 2026)
- **Fixed:** `amazfit.py` now uses `pyzipper.AESZipFile` for AES-encrypted Zepp exports.
- **Added:** `AMAZFIT_EXCLUSIVE` fields always overwrite on re-sync. `fix_amazfit_steps.py` one-off retroactive correction script.

## v3.10.14 — Phase 9 (26 Jun 2026)
- **Added:** Post-onboarding local server switch banner.

## v3.10.13 — Phase 9 (26 Jun 2026)
- **Fixed:** GitHub Pages → localhost redirect (first pass). setup.sh v3.2 Termux:Boot/API auto-detection.

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
