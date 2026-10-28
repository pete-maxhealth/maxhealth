# Working notes for any Claude session on MaxedHealth

## Start of every session (do this BEFORE saying something does or does not exist)
1. `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`, then `git branch -a` and `git ls-remote --heads origin`. Work is often pushed on a feature branch by an earlier session; `main` alone is not the whole picture.
2. `git log --oneline -15 --all`, `git status`, `git stash list`. Read the newest CHANGELOG.md entry and BACKLOG.md.
3. If the user says work was done earlier today and you cannot find it, keep looking (other branches, `gh api repos/pete-maxhealth/maxhealth/branches`, recent events) and say plainly that you may have lost context. Never tell the user it does not exist until every branch has been checked.

## Release routine
- The version lives in one place: `const APP_VERSION` in maxhealth.html. Bump it, add a CHANGELOG.md entry, update tests that pin text.
- Release gate (Pete, 28/10/2026): test only what the change touched (its own persona test plus the neighbouring screens and every place the same thing appears), not the full sweep. Before pushing, a backup/restore path must be in place: tag the current `main` (e.g. `git tag pre-v<version> origin/main && git push origin pre-v<version>`) and say how to roll back (`git push -f origin pre-v<version>:main` only with Pete's OK, or revert the release commit). The full sweep runs overnight (scheduled task "MaxedHealth nightly tests", report-only) and is not a release gate; triage its new failures the next day. Known failures live in BACKLOG.md.
- Push with `git push -q origin HEAD:main`. Then give Pete `bash ~/mh_autoupdate.sh` in its own code block.
- Commit trailers: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` and the `Claude-Session:` line.

## Running the tests (hard-won)
- All personas share ONE port (5757): never run two at once, and never run a single test while a sweep is running.
- A leftover `server.py` from a killed run keeps serving the OLD page on 5757 and gives false failures. Before any run: `ps -eo pid,args | grep server.py | grep -v grep`, and kill strays by PID. Never `pkill -f` a pattern that also matches your own command line; it kills your shell.
- Full sweep: `python3 -u tools/run_sweep_par.py <logfile> [workers=3] [timeout=240]` (as root). Each test runs in its own network namespace, so all keep port 5757 and run 3 at a time: about 27 min instead of ~75 (28/10/2026). Logs PASS/FAIL per test and ends with DONE. The old serial `tools/run_sweep.py` still works if namespaces are unavailable.
- Background jobs die when the workspace restarts; check the log is still growing.

## Standing rules from Pete
- Every new card needs show/hide and reorder controls.
- Never guess nutrition values or portions; a missing figure stays missing until he adds it.
- No ad or public page may link to the Premium page until it is live: Premium is "coming soon" with the Tally register-interest link.
- Keep personal health details out of the public repo and the app.

## How every change is checked (Pete's standard, 24/10/2026)
- Before building: think the whole process through, including what it means retrospectively (past days, older data, other screens that show the same thing). List every place the same thing appears (Today, History, edit forms, calendar, copy/duplicate paths) and do all of them, not just the one he pointed at.
- Uniformity: a new button, chip, control or message must look and act like the existing ones that do the same job (same class, size, icon, position, wording, confirm/undo behaviour). Find the existing one first and reuse it; compare them side by side in a rendered screenshot, not from the code alone.
- Persona tests are part of building, not a later step: write a test that walks the whole process (set up, do it, undo it, reload, the neighbouring screens it touches) and run the targeted tests for everything it can affect. The full regression sweep runs overnight, not before a release (see Release routine).
- Say what was checked and what was not. Never tell Pete a change "landed" without having seen it render.
