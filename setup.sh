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
echo "║       MAXEDHEALTH SETUP v3.0        ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "This will take about 2 minutes."
echo "Keep this screen open throughout."
echo ""

# ── Step 1: Packages ──────────────────────────────────────────────────────────
echo "━━━ Step 1/5: Installing packages ━━━"
pkg update -y -q 2>/dev/null
pkg install -y -q git python openssh 2>/dev/null
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

# ── Step 4: Create mhstart command ───────────────────────────────────────────
echo "━━━ Step 4/5: Configuring commands ━━━"

# Create mhstart alias
if ! grep -q "alias mhstart" "$BASHRC" 2>/dev/null; then
  echo "" >> "$BASHRC"
  echo "alias mhstart="mkdir -p /storage/emulated/0/maxhealth/data/tables /storage/emulated/0/maxhealth/data/inbox /storage/emulated/0/maxhealth/data/archive /storage/emulated/0/maxhealth/app/maxhealth; pkill -f server.py 2>/dev/null; sleep 1; cd /storage/emulated/0/maxhealth/app && python server.py &"" >> "$BASHRC"
fi

# Auto-start when Termux opens
if ! grep -q "mhstart > /dev/null" "$BASHRC" 2>/dev/null; then
  echo "" >> "$BASHRC"
  echo "# MaxedHealth — auto-start server" >> "$BASHRC"
  echo "mhstart > /dev/null 2>&1 &" >> "$BASHRC"
fi

# Make mhstart available immediately in this session
alias mhstart="mkdir -p /storage/emulated/0/maxhealth/data/tables /storage/emulated/0/maxhealth/data/inbox /storage/emulated/0/maxhealth/data/archive /storage/emulated/0/maxhealth/app/maxhealth; pkill -f server.py 2>/dev/null; sleep 1; cd /storage/emulated/0/maxhealth/app && python server.py &"


# Boot auto-start
mkdir -p "$BOOT_DIR"
cat > "$BOOT_DIR/maxhealth.sh" << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 10
mhstart > /dev/null 2>&1
BOOTEOF
chmod +x "$BOOT_DIR/maxhealth.sh"

echo "  ✓ mhstart command ready"
echo "  ✓ Auto-start on Termux open configured"
echo "  ✓ Boot script installed"
echo ""

# ── Step 5: Start server ──────────────────────────────────────────────────────
echo "━━━ Step 5/5: Starting MaxedHealth ━━━"
mhstart
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
echo "  The server starts automatically every"
echo "  time you open Termux. You can minimise"
echo "  Termux — it runs in the background."
echo ""
echo "  Optional: Install Termux:Boot from"
echo "  F-Droid to start automatically after"
echo "  your phone restarts."
echo ""
