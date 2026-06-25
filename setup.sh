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
echo "║       MAXEDHEALTH SETUP v3.1        ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "This will take about 2 minutes."
echo "Keep this screen open throughout."
echo ""

# ── Step 1: Packages ──────────────────────────────────────────────────────────
echo "━━━ Step 1/5: Installing packages ━━━"
pkg update -y -q 2>/dev/null
pkg install -y -q git python openssh cronie 2>/dev/null
pip install pyzipper --break-system-packages -q 2>/dev/null
echo "  ✓ Done"
echo ""

# ── Step 2: Storage permission ────────────────────────────────────────────────
echo "━━━ Step 2/5: Storage permission ━━━"
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
echo "━━━ Step 3/5: Downloading MaxedHealth ━━━"
if [ -d "$APP_DIR/app" ]; then
  echo "  Updating existing installation..."
  cd "$APP_DIR/app" && git pull -q
else
  echo "  Cloning repository..."
  git clone -q "$REPO" "$APP_DIR/app"
fi
echo "  ✓ MaxedHealth ready"
echo ""

# ── Step 4: Self-healing watchdog ────────────────────────────────────────────
echo "━━━ Step 4/5: Configuring self-healing server ━━━"

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

# Crontab — check every minute
echo "* * * * * ~/mh_watchdog.sh" | crontab -

# Boot script — starts crond, which then runs the watchdog automatically
mkdir -p "$BOOT_DIR"
cat > "$BOOT_DIR/start-crond.sh" << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 5
crond
BOOTEOF
chmod +x "$BOOT_DIR/start-crond.sh"

# Start crond now for this session
crond

echo "  ✓ Self-healing watchdog installed"
echo "  ✓ Cron configured (checks every 60s)"
echo "  ✓ Boot script installed (Termux:Boot required for auto-start after reboot)"
echo ""

# ── Step 5: Start server ──────────────────────────────────────────────────────
echo "━━━ Step 5/5: Starting MaxedHealth ━━━"
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
echo "  │  Bookmark it or Add to          │"
echo "  │  Home Screen for easy access.   │"
echo "  └─────────────────────────────────┘"
echo ""
echo "  The server is self-healing — it checks"
echo "  itself every minute and restarts if it"
echo "  ever stops. You don't need to keep"
echo "  Termux open."
echo ""
echo "  IMPORTANT: Install Termux:Boot from"
echo "  F-Droid (not Play Store) so this"
echo "  survives a phone restart."
echo ""
