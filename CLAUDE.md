# Working notes for any Claude session on MaxedHealth

## Start of every session (do this BEFORE saying something does or does not exist)
1. `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`, then `git branch -a` and `git ls-remote --heads origin`. Work is often pushed on a feature branch by an earlier session; `main` alone is not the whole picture.
2. `git log --oneline -15 --all`, `git status`, `git stash list`. Read the newest CHANGELOG.md entry and BACKLOG.md.
3. If the user says work was done earlier today and you cannot find it, keep looking (other branches, `gh api repos/pete-maxhealth/maxhealth/branches`, recent events) and say plainly that you may have lost context. Never tell the user it does not exist until every branch has been checked.

## Release routine
- The version lives in one place: `const APP_VERSION` in maxhealth.html. Bump it, add a CHANGELOG.md entry, update tests that pin text.
- Merge to `main` only after the FULL regression sweep passes on the final code; push with `git push -q origin HEAD:main`. Then give Pete `bash ~/mh_autoupdate.sh` in its own code block.
- Commit trailers: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` and the `Claude-Session:` line.

## Running the tests (hard-won)
- All personas share ONE port (5757): never run two at once, and never run a single test while a sweep is running.
- A leftover `server.py` from a killed run keeps serving the OLD page on 5757 and gives false failures. Before any run: `ps -eo pid,args | grep server.py | grep -v grep`, and kill strays by PID. Never `pkill -f` a pattern that also matches your own command line; it kills your shell.
- Use `python3 -u tools/run_sweep.py <logfile>`: it logs each persona (PASS/FAIL, seconds) as it finishes and cleans up stray servers, whereas `run_all.py` prints only at the very end. A full sweep takes about an hour.
- Background jobs die when the workspace restarts; check the log is still growing.

## Standing rules from Pete
- Every new card needs show/hide and reorder controls.
- Never guess nutrition values or portions; a missing figure stays missing until he adds it.
- No ad or public page may link to the Premium page until it is live: Premium is "coming soon" with the Tally register-interest link.
- Keep personal health details out of the public repo and the app.

## How every change is checked (Pete's standard, 24/10/2026)
- Before building: think the whole process through, including what it means retrospectively (past days, older data, other screens that show the same thing). List every place the same thing appears (Today, History, edit forms, calendar, copy/duplicate paths) and do all of them, not just the one he pointed at.
- Uniformity: a new button, chip, control or message must look and act like the existing ones that do the same job (same class, size, icon, position, wording, confirm/undo behaviour). Find the existing one first and reuse it; compare them side by side in a rendered screenshot, not from the code alone.
- Persona tests are part of building, not a later step: write a test that walks the whole process (set up, do it, undo it, reload, the neighbouring screens it touches) and run the targeted tests for everything it can affect. The full regression sweep is still only run when Pete asks.
- Say what was checked and what was not. Never tell Pete a change "landed" without having seen it render.
