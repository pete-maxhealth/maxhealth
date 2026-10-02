#!/data/data/com.termux/files/usr/bin/bash
APP_DIR="/storage/emulated/0/maxhealth/app/maxhealth"
LOG="$HOME/mh_autoupdate.log"

cd "$APP_DIR" || { echo "$(date): FAILED — could not cd to $APP_DIR" >> "$LOG"; exit 1; }

timeout 60 git fetch origin main --quiet 2>>"$LOG"
if [ $? -ne 0 ]; then
  echo "$(date): git fetch failed (offline, or network unavailable) — skipping this check" >> "$LOG"
  exit 0
fi

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "$(date): up to date ($LOCAL)" >> "$LOG"
  exit 0
fi

echo "$(date): update found — local $LOCAL, remote $REMOTE — resetting" >> "$LOG"
git reset --hard origin/main >> "$LOG" 2>&1

NEW_LOCAL=$(git rev-parse HEAD)
if [ "$NEW_LOCAL" = "$REMOTE" ]; then
  echo "$(date): reset succeeded, now at $NEW_LOCAL" >> "$LOG"
else
  echo "$(date): WARNING — reset ran but HEAD ($NEW_LOCAL) still doesn't match origin/main ($REMOTE)" >> "$LOG"
fi

PIDS=$(pgrep -f "python.*server.py")
if [ -n "$PIDS" ]; then
  echo "$(date): killing running server (PID(s): $PIDS) so the watchdog restarts it on the new code" >> "$LOG"
  kill $PIDS
else
  echo "$(date): no running server found to kill — watchdog will start it fresh within a minute" >> "$LOG"
fi
