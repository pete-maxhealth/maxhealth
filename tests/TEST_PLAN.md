# MaxedHealth test plan (written 12 Oct 2026, v3.10.977)

A release is ready when every layer below passes. Layers 1 and 2 are automatic and run in the sandbox; layer 3 is the short list Pete runs on his own phone.

## Layer 1: automated persona suite (every release)

Run from the repo, one command, about 15 to 25 minutes:

```
python3 -I tests/personas/run_all.py
```

Each `pNN_*.py` starts its own fresh server and a headless Chromium at phone size (390 px wide), drives the real page, and exits non-zero on any finding. Rules:

- Never run two suites at once (they share port 5757).
- Run with `python3 -I` or from the repo, so a stray `bisect.py` or similar cannot shadow the standard library.
- A failure that passes on a straight re-run and on a stash of the change is flaky (p44 under load is the known one); anything else is a real bug.
- Console errors about fonts or GitHub are sandbox network noise, not findings.

What the suite covers, by area:

| Area | Personas |
| --- | --- |
| First run, setup, packs, nudges | p01, p75, p91, p92, p94, p99 |
| Logging meals, library, recipes, portions | p09, p11, p22, p29, p39, p40, p44, p48, p53, p54, p68 |
| Screens, Filter toolbar, fold bars, reset | p49, p50, p71, p73, p78, p80, p88, p89, p90, p93, p98 |
| Charts, trends, reports | p03, p13, p51, p82 |
| Wearables, sync, data gaps | p04, p05, p07, p10, p20, p56, p57, p58, p66, p67, p84, p86, p87 |
| Backup, offline, network failure | p25, p27, p28, p43, p62, p96 |
| AI safety (no guessed grams, prompt rules) | p60, p95 |
| Health tracking (symptoms, fasting, ketosis, weight, bodycomp) | p23, p41, p45, p46, p63, p70 |
| Voice and chat commands | p97 |

## Layer 2: targeted checks for each new feature

For every new feature the suite gets one new persona that tests:

1. the happy path;
2. the "nothing there" case (empty data, no filter, first run);
3. persistence across a page reload;
4. that Default / reset puts things back;
5. that no page error fires.

Examples added for v3.10.977: `p98` (toolbar on History, Library, Customise; none on Supplements or Log; Library chips filter, persist, and reset) and `p99` (every shipped starter pack: listed, unique ids, real layout keys, applies cleanly, embedded first-run packs equal the JSON files).

Pack rules, enforced by p99: a pack may only carry symptoms, treatments and layout; layout keys are limited to Today fold keys, hidden Today cards and hidden Trends cards; every card it names must exist; a pack never contains advice or personal data.

## Layer 3: Pete's phone checklist (about 10 minutes, after `bash ~/mh_autoupdate.sh`)

Do this once at large text and once at small text.

1. **Toolbar on every page.** Today, Log > History, Log > Library, Insights > Trends and Reports, Settings > Manage, Customise and Import. The first row is always Filter (where the page has anything to filter), Open all, Close all, Default, in that order. Supplements and Log (chat) have no toolbar by design.
2. **Library chips and 👁.** Tap the 👁 on a section: it disappears and is listed under Filter as Hidden, with the count on the button; tap its name to bring it back.
2b. **Library chips.** Open Filter on Library, tap Tools: only Library Tools shows. Close the app and reopen: the filter is still there. Tap Default and confirm: everything is back.
3. **History.** This Week, Month and All sit inside the Filter panel and still change the list.
4. **Packs.** Settings → Data → Starter packs lists all 27 packs A–Z, with a "not medical advice" line at the top. Preview one: it should list symptoms and a screen layout and change nothing until you apply it.
4d. **Change my focus.** Settings > Manage > Setup > Change my focus: choose Muscle growth, read the preview, Switch. Today now hides Ketosis and Fasting; your own symptoms are still there; Show me everything brings it all back.
4c. **Food Library category.** In Log > Library > Food Library pick a category from the third dropdown: only those foods show, with a warning banner; Show everything resets it.
4e. **Meal planner.** In chat type "I'm planning on eating 2 eggs at 1pm": the preview says Ready to plan for 13:00; Add to plan. Under the Today bars the plan shows with eaten + planned totals. At the time it asks Did you eat this? Yes moves it into the log.
4f. **Languages.** Settings > Profile > Language: choose Español; screens switch; tap the 🌐 button, Back to English: everything returns. Same picker on first-run onboarding.
4g. **Report on a tag.** Settings > Manage > Report Profiles > New: step 2 lists your tags (🏷) and, with 2+ conditions, the condition chips; pick one, finish, generate: the report names that tag.
4h. **Translate this screen.** In French, open a screen with leftover English, tap ✨ next to the flag, confirm: the English becomes French and stays so after reopening; Forget my AI translations undoes it.
4i. **Score on a no-food day.** Score a symptom and add a tag today without logging food; next day History/Compare Metrics still show that day. In Reports, ask the analyst about a symptom: the answer can mention your scores.
4j. **Score a past day.** Under How are you today?, tap ＋ Score a past day, pick 3 days ago, score, Save; Compare Metrics shows that day.
4k. **Share vs Save.** Settings > Data, tick one thing, tap Share…: the phone's share menu opens (or a 'Ready to share' box appears first; tap Share… in it). Save to Downloads puts the file in Downloads and does not open a menu.
4l. **Copy and buttons.** Run any import or ask the AI a question: under the result there is Select all and Copy; Copy then paste elsewhere gives exactly the result. Make the phone's text size large: the Meal plan card's buttons wrap and nothing is cut off. Buttons across the app have rounded corners and a clear outline.
4m. **Demo is AI-free.** Start any demo and use the meal AI, a recipe, or the AI check: each answers with "Sample answer: live AI is switched off in demo mode", and your own AI allowance does not move. Tap "See Premium" in the banner: a locked preview opens with a Register interest button. The picker lists 28 people, one for each of the 27 starter packs.
4n. **Starter allowance.** After the Worker is redeployed, Settings > AI Provider shows "Free AI answers left: N" and it counts down as you use meal AI. At 10 and 3 left a toast suggests your own key or Premium. With your own AI key set, the line is hidden.
4o. **Licence.** Settings > AI Provider > Premium licence: a wrong key says it was not recognised; a good key shows "Premium licence"; "Start 14-day trial" shows days left; Remove clears it. (Needs the licence service uploaded first.)
4p. **Premium awareness.** Start any demo: a "Premium: your ring and watch, synced for you" card sits at the top of Today. Tap it for a labelled example day (Health Connect snapshots, ring and watch, ranking, self-check). It disappears when you exit the demo.
4q. **Four more languages.** Settings → Language lists nine languages with flags. Pick Portuguese, Italian, Polish and Dutch in turn: the tabs and buttons translate, nothing shows a stray {1}, and voice entry uses that language. Return to English with the 🌐 button.
4r. **Your routine.** Start any demo and open Insights → Trends: a "Your routine" card with a clear EXAMPLE ONLY label sits under the Premium chart; it disappears on exit. On Premium (phone with the local server and a few days of data) the card shows your own meal times, sleep, steps and HRV, and says "Still learning" until it has enough days. On the free web app nothing appears.
4b. **Close all really closes.** On Trends (7 Days) tap Close all: the Weight, Heart rate and other metric cards fold to one-line bars (tap a bar to open just that one); Open all opens them. Same on Today and the Library.
5. **No regressions.** Log a meal by typing, run the 3-AI check (the grams must not be echoed unless you typed them), tap a Trends chart, use the Next meal idea buttons (each tapped pill stays highlighted).
6. **Jill's phone.** Fresh install of the web version: the first-run "what do you want to track?" choice appears once, then the chosen layout.

## Release gate

1. `run_all.py` is all PASS (a flaky one must pass on re-run).
2. CHANGELOG, TECHNICAL, README, BACKLOG and the guide mention the change.
3. `APP_VERSION` bumped and starter pack versions not newer than it.
4. Commit with a descriptive message, push to main, then run layer 3.
