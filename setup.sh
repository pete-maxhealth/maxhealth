#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth setup script
# Run with: curl -sL https://pete-maxhealth.github.io/maxhealth/setup.sh | bash

REPO="https://github.com/pete-maxhealth/maxhealth.git"
APP_DIR="/storage/emulated/0/maxhealth"
BOOT_DIR="/data/data/com.termux/files/home/.termux/boot"
BASHRC="/data/data/com.termux/files/home/.bashrc"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║       MAXEDHEALTH SETUP v2.0        ║"
echo "╚══════════════════════════════════════╝"
echo ""

echo "→ Updating packages..."
pkg update -y -q 2>/dev/null
pkg install -y -q git python openssh 2>/dev/null
echo "  ✓ Packages ready"

echo "→ Installing Python dependencies..."
pip install pyzipper --break-system-packages -q 2>/dev/null
echo "  ✓ Dependencies ready"

echo "→ Requesting storage permission..."
if [ ! -d "/storage/emulated/0" ]; then
  termux-setup-storage
  sleep 3
else
  echo "  ✓ Storage already accessible"
fi

echo "→ Downloading MaxedHealth..."
if [ -d "$APP_DIR/app" ]; then
  cd "$APP_DIR/app" && git pull -q
else
  mkdir -p "$APP_DIR"
  git clone -q "$REPO" "$APP_DIR/app"
fi
echo "  ✓ MaxedHealth ready"

mkdir -p "$APP_DIR/data/tables" "$APP_DIR/data/inbox" "$APP_DIR/data/backup" "$APP_DIR/logs"

echo "→ Creating mhstart command..."
cat > /data/data/com.termux/files/usr/bin/mhstart << 'MHEOF'
#!/data/data/com.termux/files/usr/bin/bash
if curl -sf http://localhost:5757/ping > /dev/null 2>&1; then
  echo "MaxedHealth already running ✓"
  exit 0
fi
echo "Starting MaxedHealth..."
cd /storage/emulated/0/maxhealth/app
python server.py &
sleep 2
curl -sf http://localhost:5757/ping > /dev/null 2>&1 && echo "MaxedHealth running ✓" || echo "Starting — check in a moment"
MHEOF
chmod +x /data/data/com.termux/files/usr/bin/mhstart
echo "  ✓ mhstart command created"

echo "→ Setting up auto-start on Termux open..."
if ! grep -q "mhstart" "$BASHRC" 2>/dev/null; then
  echo "" >> "$BASHRC"
  echo "# MaxedHealth — start server automatically" >> "$BASHRC"
  echo "mhstart > /dev/null 2>&1 &" >> "$BASHRC"
  echo "  ✓ Auto-start added"
else
  echo "  ✓ Already configured"
fi

echo "→ Setting up boot auto-start..."
mkdir -p "$BOOT_DIR"
cat > "$BOOT_DIR/maxhealth.sh" << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
sleep 5
mhstart > /dev/null 2>&1
BOOTEOF
chmod +x "$BOOT_DIR/maxhealth.sh"
echo "  ✓ Boot script ready"

if [ ! -d "/data/data/com.termux.boot" ]; then
  echo ""
  echo "  ℹ Optional: Install Termux:Boot from F-Droid"
  echo "    Starts MaxedHealth after phone restarts."
  echo "    Not required — opens automatically with Termux."
fi

echo "→ Starting server..."
mhstart

echo ""
echo "╔══════════════════════════════════════╗"
echo "║         SETUP COMPLETE ✓            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  Open Chrome and visit:"
echo "  pete-maxhealth.github.io/maxhealth/"
echo ""
echo "  Tap Menu → Add to Home Screen"
echo "  The app detects the server automatically."
echo ""
echo "  Server starts every time you open Termux."
echo ""
