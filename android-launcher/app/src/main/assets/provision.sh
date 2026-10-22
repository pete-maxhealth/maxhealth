#!/data/data/com.termux/files/usr/bin/bash
# Fired headless via RUN_COMMAND — never seen by the user.
#
# The folder-creation section below is now CONFIRMED against your real
# setup.sh (you shared it — it only does mkdir -p on five folders, nothing
# else). Everything after that — package installs, git clone, mhstart, boot
# scripts, crontab — is NOT in setup.sh at all, despite README.md and
# TECHNICAL.md describing it as if it were. That part of this script is still
# my best guess at what needs to happen, written from the docs, not verified
# against how you actually do it. Please tell me the real process for that
# part (a second script? typed from memory?) before trusting this beyond the
# folder creation.
#
# Idempotent throughout on purpose — RUN_COMMAND gives no guaranteed single-shot
# semantics, and a retry after a partial failure should be safe to just run again
# rather than leaving things half-done.

set -e

STAGING="$HOME/storage/shared/maxhealth-launcher-staging"
ROOT="/storage/emulated/0/maxhealth"
APP_DIR="$ROOT/app/maxhealth"
EXTRACTORS_DIR="$ROOT/app/extractors"
DATA_DIR="$ROOT/data/tables"
INBOX_DIR="$ROOT/data/inbox"
ARCHIVE_DIR="$ROOT/data/archive"
LOGS_DIR="$ROOT/app/logs"
# Matches the live phone: logs live under app/, and maxedhealth.sh writes its
# boot log to $ROOT/app/logs/boot.log. Created here so a fresh install has it.

echo "[provision] Ensuring package list is current…"
pkg update -y >/dev/null 2>&1 || true

echo "[provision] Installing required packages…"
# pyzipper added after checking the real server.py — it's imported there
# (optional at import time, guarded by a try/except, but needed for real
# password-protected zip restores to work) and is a pip package, not a
# Termux pkg. nodejs deliberately NOT added yet — package.json/package-lock
# in this repo pull in `sharp`, a natively-compiled image library, and I
# don't yet know whether that's meant to run in Termux at all (sharp is
# often genuinely difficult to get working on Android/Termux — missing
# native deps) or whether it's a desktop-only build step. Asked rather than
# guessed — see the chat.
pkg install -y python git termux-api cronie >/dev/null 2>&1
pip install pyzipper >/dev/null 2>&1 || true

echo "[provision] Checking for a stray server.py at the old pre-restructure path…"
# Confirmed real, live bug on the existing phone install (not hypothetical):
# a leftover server.py directly under app/ (964 lines newer vs 804 older,
# genuinely different code, not just a stale comment) was silently being run
# by mhstart/maxhealth_sync.sh instead of the current app/maxhealth/ copy.
# Removing anything found here before this script does anything else, so a
# fresh native-app install can never fall into the same trap.
if [ -f "$ROOT/app/server.py" ]; then
  echo "[provision] Found one — removing it."
  rm -f "$ROOT/app/server.py"
fi

echo "[provision] Creating real app folders…"
# Matches the actual setup.sh (confirmed directly, not from the docs, which
# were missing data/inbox, data/archive, and app/extractors entirely — this
# list is now the real one).
mkdir -p "$APP_DIR"
mkdir -p "$EXTRACTORS_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$INBOX_DIR"
mkdir -p "$ARCHIVE_DIR"
mkdir -p "$LOGS_DIR"

# NEEDS VERIFYING: where the actual maxhealth.html/server.py/etc. come from at
# provisioning time. Two real options, and I don't know which fits how you
# actually want to distribute this — flagging rather than guessing:
#   (a) git clone the real repo directly here, same as the existing Quick Start
#       instructions in README.md, OR
#   (b) have the native app bundle a known-good release inside its own APK
#       assets and copy those files in during this step instead of cloning.
# (a) keeps this always in sync with GitHub with zero APK rebuilds needed;
# (b) works without needing network access or GitHub credentials on a fresh
# device. Written here as (a) since it matches the existing Quick Start flow,
# but this is the single biggest thing worth deciding before relying on this.
if [ ! -d "$APP_DIR/.git" ]; then
  echo "[provision] Cloning MaxedHealth…"
  git clone https://github.com/pete-maxhealth/maxhealth.git "$APP_DIR.tmp"
  # Clone into a temp dir then move contents in, rather than cloning directly
  # into APP_DIR — avoids "destination path already exists and is not an empty
  # directory" if this step is ever retried after partially succeeding.
  cp -r "$APP_DIR.tmp"/. "$APP_DIR"/
  rm -rf "$APP_DIR.tmp"
else
  echo "[provision] Already cloned — pulling latest…"
  (cd "$APP_DIR" && git pull) || true
fi

echo "[provision] Setting up boot survival…"
mkdir -p "$HOME/.termux/boot"

cat > "$HOME/mh_watchdog.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

PIDS=$(pgrep -f "python.*server.py")
COUNT=$(echo "$PIDS" | grep -c .)

if [ "$COUNT" -eq 0 ]; then
  cd /storage/emulated/0/maxhealth/app/maxhealth && python server.py &
  echo "$(date): Server was down, restarted" >> ~/mh_watchdog.log
elif [ "$COUNT" -gt 1 ]; then
  # Kill duplicates, keep the oldest (lowest PID)
  KEEP=$(echo "$PIDS" | sort -n | head -1)
  for PID in $PIDS; do
    if [ "$PID" != "$KEEP" ]; then
      kill "$PID"
      echo "$(date): Killed duplicate PID $PID, kept $KEEP" >> ~/mh_watchdog.log
    fi
  done
fi
EOF
chmod +x "$HOME/mh_watchdog.sh"

# mh_autoupdate.sh deliberately not written: confirmed absent on the live
# phone (22/09/2026) and nothing in crontab or the boot scripts calls it.

# Matches the live ~/bin/mhstart exactly (confirmed 22/09/2026).
mkdir -p "$HOME/bin"
cat > "$HOME/bin/mhstart" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
pkill -f server.py 2>/dev/null; sleep 1
cd /storage/emulated/0/maxhealth/app/maxhealth && python server.py &
EOF
chmod +x "$HOME/bin/mhstart"

# Real file, confirmed from what you shared — written here so it exists, but
# deliberately NOT wired into crontab below yet. Its own header comment says
# it's meant to be triggered by MacroDroid/Tasker/Automate/Termux:Tasker
# whenever a wearable export lands in Downloads — a file-watch trigger, not a
# time-based one like the watchdog/autoupdate above. Need to know: should
# this be part of the native app's automated setup at all (i.e. does it
# matter for the 5 testers, who may not have wearables), and if so, wire it
# via which mechanism — a cron job that just polls Downloads periodically
# instead of a real file-watch, or something else?
cat > "$HOME/maxhealth_sync.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth Auto-Sync Script
# Trigger this whenever a new wearable export appears in Downloads
# Works with: MacroDroid, Tasker, Automate, Termux:Tasker, cron

DOWNLOADS="/storage/emulated/0/Download"
SERVER="http://localhost:5757"

# Check if server is running
if ! curl -sf "$SERVER/ping" > /dev/null 2>&1; then
  # Start server if not running
  cd /storage/emulated/0/maxhealth/app/maxhealth
  python server.py &
  sleep 3
fi

# Trigger sync
curl -sf "$SERVER/sync" > /dev/null 2>&1

echo "MaxedHealth sync triggered at $(date)"
EOF
chmod +x "$HOME/maxhealth_sync.sh"

cat > "$HOME/.termux/boot/start-crond.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 5
crond
EOF
chmod +x "$HOME/.termux/boot/start-crond.sh"

# Real mechanism (confirmed) is genuinely different from what I'd guessed —
# not a wake-lock plus a direct call into mh_watchdog.sh. It just asks
# Android's own service manager to keep Termux's foreground service alive,
# so Android doesn't kill the whole Termux environment before crond gets a
# chance to tick. The actual watchdog logic runs entirely through the
# crontab entry (`* * * * * ~/mh_watchdog.sh`) once crond is up — this script
# and start-crond.sh above are both just keeping the environment alive long
# enough for that to happen, not invoking the watchdog themselves.
cat > "$HOME/.termux/boot/start-watchdog.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 5
am start-foreground-service --user 0 -n com.termux/com.termux.app.TermuxService
EOF
chmod +x "$HOME/.termux/boot/start-watchdog.sh"

# Named maxedhealth.sh (not maxhealth.sh) to match the real file exactly.
# Copied verbatim from the live phone (confirmed 22/09/2026): logs under
# app/logs, and the sync step calls $HOME/maxhealth_sync.sh (sync.sh never
# existed).
cat > "$HOME/.termux/boot/maxedhealth.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth auto-sync on device boot
sleep 10  # Wait for storage to mount
ROOT="/storage/emulated/0/maxhealth"
LOG="$ROOT/app/logs/boot.log"
echo "$(date) | boot sync started" >> "$LOG"
bash "$HOME/maxhealth_sync.sh" >> "$LOG" 2>&1
echo "$(date) | boot sync complete" >> "$LOG"
EOF
chmod +x "$HOME/.termux/boot/maxedhealth.sh"

echo "[provision] Setting up scheduled checks…"
# Matches your real, confirmed crontab exactly (`* * * * * ~/mh_watchdog.sh`)
# rather than the guessed `bash $HOME/...` variant this had before — cron's
# handling of `~` and of `bash script` vs a directly-executable script with
# its own shebang can behave differently between implementations, so matching
# your actual, already-working syntax beats a plausible-looking guess.
# No autoupdate line — confirmed via real crontab -l that nothing schedules
# it today; not adding it silently until that's a deliberate decision.
#
# BUG FOUND AND FIXED 24/09/26: on a genuinely empty crontab (exactly what a
# fresh Termux install has), `crontab -l` produces no output, and `grep -v`
# on empty input exits 1 (its normal "nothing matched" signal). Under this
# script's `set -e`, that was being treated as a real failure and silently
# killed the subshell BEFORE the echo below ever ran — so `crontab -`
# received empty input and set an empty crontab, with no error shown
# anywhere and the rest of provisioning completing normally regardless.
# Confirmed live on Pete's phone: provisioning reported success, sentinel
# was written, dashboard loaded fine — but crontab was empty and crond
# wasn't running at all, so mh_watchdog.sh never got a chance to catch a
# dead server. The `|| true` below is the fix: it stops "found nothing to
# remove" from ever being mistaken for a real failure again.
{ crontab -l 2>/dev/null | grep -v "mh_watchdog" || true; \
  echo "* * * * * ~/mh_watchdog.sh"; \
} | crontab -

echo "[provision] Starting the server…"
cd "$APP_DIR"
if ! pgrep -f "python.*server.py" > /dev/null; then
  nohup python server.py > /dev/null 2>&1 &
fi

echo "[provision] Waiting for the server to actually respond before declaring success…"
ATTEMPTS=0
until curl -s "http://localhost:5757/ping" > /dev/null 2>&1 || [ "$ATTEMPTS" -ge 30 ]; do
  sleep 1
  ATTEMPTS=$((ATTEMPTS + 1))
done

if curl -s "http://localhost:5757/ping" > /dev/null 2>&1; then
  echo "[provision] Server confirmed responding — done."
  touch "$STAGING/sentinel_provision-complete"
else
  echo "[provision] Server never responded to /ping after 30s — NOT writing the completion sentinel."
  echo "[provision] Check server.py directly: cd $APP_DIR && python server.py"
fi
