#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth Setup
# Run: curl -sL https://pete-maxhealth.github.io/maxhealth/setup.sh | bash

REPO="https://github.com/pete-maxhealth/maxhealth.git"
APP_DIR="/storage/emulated/0/maxhealth"
BOOT_DIR="/data/data/com.termux/files/home/.termux/boot"
BASHRC="/data/data/com.termux/files/home/.bashrc"

clear
echo ""
echo "╔══════════════════════════════════════╗"
echo "║       MAXEDHEALTH SETUP v3.2        ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "This will take about 2-3 minutes."
echo "Keep this screen open throughout."
echo ""

# ── Step 1: Packages ──────────────────────────────────────────────────────────
echo "━━━ Step 1/6: Installing packages ━━━"
pkg update -y -q 2>/dev/null
pkg install -y -q git python openssh cronie termux-api 2>/dev/null
pip install pyzipper --break-system-packages -q 2>/dev/null
echo "  ✓ Done"
echo ""

# ── Step 1b: Companion apps (Termux:Boot / Termux:API) ───────────────────────
echo "━━━ Step 1.5/6: Checking companion apps ━━━"
BOOT_INSTALLED=$(pm list packages 2>/dev/null | grep -c "com.termux.boot")
API_INSTALLED=$(pm list packages 2>/dev/null | grep -c "com.termux.api")

if [ "$BOOT_INSTALLED" -eq 0 ] || [ "$API_INSTALLED" -eq 0 ]; then
  echo ""
  echo "  ACTION REQUIRED (one-time, ~30 seconds):"
  echo "  MaxedHealth needs two small companion apps so it"
  echo "  keeps running after your phone restarts."
  echo ""
  if [ "$BOOT_INSTALLED" -eq 0 ]; then
    echo "  1. Opening Termux:Boot page — tap INSTALL, then open it once."
    termux-open-url "https://f-droid.org/packages/com.termux.boot/" 2>/dev/null
    echo "     (If nothing opened, visit: https://f-droid.org/packages/com.termux.boot/)"
    echo ""
    read -p "  Press ENTER once Termux:Boot is installed and opened... " _
  fi
  if [ "$API_INSTALLED" -eq 0 ]; then
    echo "  2. Opening Termux:API page — tap INSTALL (no need to open it)."
    termux-open-url "https://f-droid.org/packages/com.termux.api/" 2>/dev/null
    echo "     (If nothing opened, visit: https://f-droid.org/packages/com.termux.api/)"
    echo ""
    read -p "  Press ENTER once Termux:API is installed... " _
  fi
  echo ""
  echo "  ✓ Companion apps ready"
else
  echo "  ✓ Already installed"
fi
echo ""

# ── Step 2: Storage permission ────────────────────────────────────────────────
echo "━━━ Step 2/6: Storage permission ━━━"
if [ ! -d "/storage/emulated/0/Download" ]; then
  echo ""
  echo "  ACTION REQUIRED:"
  echo "  A permission dialog will appear."
  echo "  Tap ALLOW to give Termux access to your files."
  echo ""
  termux-setup-storage
  echo "  Waiting for permission..."
  sleep 5
  if [ ! -d "/storage/emulated/0/Download" ]; then
    echo ""
    echo "  ✗ Storage permission not granted."
    echo "  Please run setup again and tap ALLOW when prompted."
    exit 1
  fi
fi
mkdir -p "$APP_DIR/data/tables" "$APP_DIR/data/inbox" "$APP_DIR/data/backup" "$APP_DIR/logs"
echo "  ✓ Storage accessible"
echo ""

# ── Step 3: Download MaxedHealth ─────────────────────────────────────────────
echo "━━━ Step 3/6: Downloading MaxedHealth ━━━"
if [ -d "$APP_DIR/app" ]; then
  echo "  Updating existing installation..."
  cd "$APP_DIR/app" && git pull -q
else
  echo "  Cloning repository..."
  git clone -q "$REPO" "$APP_DIR/app"
fi
# Git refuses to operate on a repo if the file ownership looks different from
# what the current process expects ("dubious ownership") - a real security
# feature, but one that fires as a false positive constantly on Android/
# Termux. Setting this now means it's correct from the very first run,
# rather than waiting for the first auto-update cron cycle to self-heal it
# (that self-heal exists too, in mh_autoupdate.sh below, as a second layer -
# this one silently blocked every update for over a day on one real device
# before being noticed, precisely because the failure was silent).
git config --global --add safe.directory "$APP_DIR/app/maxhealth"
echo "  ✓ MaxedHealth ready"
echo ""

# ── Step 4: Self-healing watchdog ────────────────────────────────────────────
echo "━━━ Step 4/6: Configuring self-healing server ━━━"

# Watchdog script — checks every minute, restarts if down, kills duplicates
cat > "$HOME/mh_watchdog.sh" << 'WATCHEOF'
#!/data/data/com.termux/files/usr/bin/bash
PIDS=$(pgrep -f "python.*server.py")
COUNT=$(echo "$PIDS" | grep -c .)
if [ "$COUNT" -eq 0 ]; then
  cd /storage/emulated/0/maxhealth/app/maxhealth && python server.py &
  echo "$(date): Server was down, restarted" >> ~/mh_watchdog.log
elif [ "$COUNT" -gt 1 ]; then
  KEEP=$(echo "$PIDS" | sort -n | head -1)
  for PID in $PIDS; do
    if [ "$PID" != "$KEEP" ]; then
      kill "$PID"
      echo "$(date): Killed duplicate PID $PID, kept $KEEP" >> ~/mh_watchdog.log
    fi
  done
fi
WATCHEOF
chmod +x "$HOME/mh_watchdog.sh"

# Auto-update script — checks GitHub every 30 min, applies any update, then
# lets the watchdog above (already running every minute) restart the server.
# This is a pure end-user device, never expected to carry real local code
# edits, so it always converges to exactly what's on GitHub (git reset --hard)
# rather than attempting a merge - a merge conflict here would silently block
# every future update forever with no one watching to notice or resolve it.
cat > "$HOME/mh_autoupdate.sh" << 'UPDATEEOF'
#!/data/data/com.termux/files/usr/bin/bash
REPO_DIR="/storage/emulated/0/maxhealth/app/maxhealth"
LOG="$HOME/mh_autoupdate.log"
cd "$REPO_DIR" || { echo "$(date): ERROR - can't cd to $REPO_DIR" >> "$LOG"; exit 1; }
# Git refuses to operate on a repo if the file ownership looks different from
# what the current process expects ("dubious ownership") - a real security
# feature, but one that fires as a false positive constantly on Android/
# Termux, where a fresh git clone can end up with ownership metadata that
# looks different to a cron job's execution context than to an interactive
# shell's, even though it's genuinely the same device and the same person.
# Run every single time rather than once during setup, so this can't
# silently start blocking every future update again if ownership ever shifts
# a second time for any reason - this exact thing is what took a full day's
# worth of failed update attempts to notice, since the failure was silent
# beyond this log file.
git config --global --add safe.directory "$REPO_DIR" 2>> "$LOG"
git fetch origin main --quiet 2>> "$LOG"
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" != "$REMOTE" ]; then
  echo "$(date): Update found ($LOCAL -> $REMOTE), applying..." >> "$LOG"
  git reset --hard origin/main >> "$LOG" 2>&1
  pkill -9 -f "python.*server.py"
  echo "$(date): Update applied, server stopped - watchdog will restart it within a minute." >> "$LOG"
fi
UPDATEEOF
chmod +x "$HOME/mh_autoupdate.sh"

# mhstart command — installed globally so it works from any directory, not
# just when the caller already happens to be sitting in the app folder.
# (An earlier version cd'd one level too high, which silently no-op'd rather
# than failing loudly - it only ever "worked" because Termux sessions here
# are almost always already inside the app folder when this gets typed.)
mkdir -p "$PREFIX/bin"
cat > "$PREFIX/bin/mhstart" << 'STARTEOF'
#!/data/data/com.termux/files/usr/bin/bash
if curl -sf http://localhost:5757/ping > /dev/null 2>&1; then
  echo "MaxedHealth already running ✓"
  exit 0
fi
echo "Starting MaxedHealth..."
cd /storage/emulated/0/maxhealth/app/maxhealth || { echo "✗ App folder not found — is MaxedHealth installed?"; exit 1; }
python server.py &
sleep 2
curl -sf http://localhost:5757/ping > /dev/null 2>&1 && echo "MaxedHealth running ✓" || echo "Starting — check in a moment"
STARTEOF
chmod +x "$PREFIX/bin/mhstart"

# Crontab — watchdog every minute, auto-update check every 30 minutes
(echo "* * * * * ~/mh_watchdog.sh"; echo "*/30 * * * * ~/mh_autoupdate.sh") | crontab -

# Boot script 1 — starts crond, which then runs the watchdog every minute
mkdir -p "$BOOT_DIR"
cat > "$BOOT_DIR/start-crond.sh" << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 5
crond
BOOTEOF
chmod +x "$BOOT_DIR/start-crond.sh"

# Boot script 2 — holds a wake-lock (stops Doze suspending things overnight)
# and runs the watchdog immediately on boot, before the first cron tick
cat > "$BOOT_DIR/start-watchdog.sh" << 'WAKEEOF'
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
bash ~/mh_watchdog.sh &
WAKEEOF
chmod +x "$BOOT_DIR/start-watchdog.sh"

# Boot script 3 — checks for an update immediately on boot (rather than
# waiting up to 30 min for the next cron tick), then starts the server
cat > "$BOOT_DIR/maxhealth.sh" << 'MHBOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 5
bash ~/mh_autoupdate.sh > /dev/null 2>&1
mhstart > /dev/null 2>&1
MHBOOTEOF
chmod +x "$BOOT_DIR/maxhealth.sh"

# Start crond now for this session
crond

echo "  ✓ Self-healing watchdog installed"
echo "  ✓ Auto-update installed (checks GitHub every 30 min)"
echo "  ✓ Cron configured (watchdog every 60s, updates every 30 min)"
echo "  ✓ Boot scripts installed (wake-lock + auto-update + auto-restart on reboot)"
echo ""

# ── Step 5: Start server ──────────────────────────────────────────────────────
echo "━━━ Step 5/6: Starting MaxedHealth ━━━"
bash "$HOME/mh_watchdog.sh"
sleep 2
echo ""

# ── Done ──────────────────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════╗"
echo "║         SETUP COMPLETE ✓            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  ┌─────────────────────────────────┐"
echo "  │  Open Chrome and go to:         │"
echo "  │                                 │"
echo "  │    localhost:5757               │"
echo "  │                                 │"
echo "  │  Add THIS page to your Home     │"
echo "  │  Screen (not github.io) — that  │"
echo "  │  way it always opens in full    │"
echo "  │  Local Mode, with no extra      │"
echo "  │  taps needed.                   │"
echo "  └─────────────────────────────────┘"
echo ""
echo "  The server is self-healing — it checks"
echo "  itself every minute and restarts if it"
echo "  ever stops. You don't need to keep"
echo "  Termux open, and it will survive phone"
echo "  restarts automatically."
echo ""
