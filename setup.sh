#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth setup script
# Run with: curl -sL https://pete-maxhealth.github.io/maxhealth/setup.sh | bash

set -e

REPO="https://github.com/pete-maxhealth/maxhealth.git"
APP_DIR="/storage/emulated/0/maxhealth"
BOOT_DIR="/data/data/com.termux/files/home/.termux/boot"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     MAXEDHEALTH SETUP               ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. Update packages ────────────────────────────────────
echo "→ Updating packages..."
pkg update -y -q
pkg install -y -q git python openssh

# ── 2. Storage permission ─────────────────────────────────
echo "→ Requesting storage permission..."
termux-setup-storage
sleep 2

# ── 3. Clone repo ─────────────────────────────────────────
echo "→ Downloading MaxedHealth..."
if [ -d "$APP_DIR" ]; then
  echo "  Updating existing installation..."
  cd "$APP_DIR/app" && git pull
else
  mkdir -p "$APP_DIR"
  git clone "$REPO" "$APP_DIR/app"
fi

# ── 4. Create folder structure ────────────────────────────
mkdir -p "$APP_DIR/data/tables"
mkdir -p "$APP_DIR/data/inbox"
mkdir -p "$APP_DIR/data/backup"
mkdir -p "$APP_DIR/logs"

# ── 5. Termux:Boot auto-start ─────────────────────────────
echo "→ Setting up auto-start..."
mkdir -p "$BOOT_DIR"
cat > "$BOOT_DIR/maxhealth.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd /storage/emulated/0/maxhealth/app
python server.py &
EOF
chmod +x "$BOOT_DIR/maxhealth.sh"

# ── 6. Start server now ───────────────────────────────────
echo "→ Starting server..."
cd "$APP_DIR/app"
python server.py &
sleep 2

echo ""
echo "✓ Setup complete!"
echo ""
echo "  MaxedHealth is running at http://localhost:5757"
echo "  The server will start automatically on every reboot."
echo ""
echo "  Open Chrome and visit: http://localhost:5757"
echo "  Then tap ⋮ → Add to Home Screen"
echo ""
