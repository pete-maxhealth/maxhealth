#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════════
#  MaxedHealth — Zero-friction setup
#
#  Run once in Termux:
#    curl -sSL https://raw.githubusercontent.com/pete-maxhealth/maxhealth/main/setup.sh | bash
#
# ═══════════════════════════════════════════════════════════════

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
OK="${GREEN}✓${NC}"; WAIT="${YELLOW}…${NC}"; FAIL="${RED}✗${NC}"

clear
echo ""
echo -e "${BOLD}${GREEN}  ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗ ${NC}"
echo -e "${BOLD}${GREEN}  ████╗ ████║██╔══██╗╚██╗██╔╝██╔════╝██╔══██╗${NC}"
echo -e "${BOLD}${GREEN}  ██╔████╔██║███████║ ╚███╔╝ █████╗  ██║  ██║${NC}"
echo -e "${BOLD}${GREEN}  ██║╚██╔╝██║██╔══██║ ██╔██╗ ██╔══╝  ██║  ██║${NC}"
echo -e "${BOLD}${GREEN}  ██║ ╚═╝ ██║██║  ██║██╔╝ ██╗███████╗██████╔╝${NC}"
echo -e "${BOLD}${GREEN}  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝ ${NC}"
echo ""
echo -e "${BOLD}  Health Intelligence Platform — Setup${NC}"
echo -e "  ${CYAN}pete-maxhealth.github.io/maxhealth/maxhealth.html${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Step 1: Storage permission ───────────────────────────────
echo -e "${WAIT} Requesting storage access..."
echo -e "  ${YELLOW}► Tap ALLOW on the permission popup that appears${NC}"
termux-setup-storage
# Wait for user to grant permission
sleep 3
if [ ! -d "/storage/emulated/0" ]; then
  echo -e "${FAIL} Storage access denied. Re-run setup and tap Allow."
  exit 1
fi
echo -e "${OK} Storage access granted"
echo ""

# ── Step 2: Packages ─────────────────────────────────────────
echo -e "${WAIT} Installing packages (this may take a minute)..."
pkg update -y -q 2>/dev/null
pkg install -y -q python git curl openssh 2>/dev/null
pip install --quiet --break-system-packages requests 2>/dev/null || true
echo -e "${OK} Packages ready"
echo ""

# ── Step 3: Folder structure ─────────────────────────────────
echo -e "${WAIT} Creating folder structure..."
ROOT="/storage/emulated/0/maxhealth"
mkdir -p "$ROOT/app/extractors"
mkdir -p "$ROOT/data/inbox/old"
mkdir -p "$ROOT/data/tables"
mkdir -p "$ROOT/data/backup"
mkdir -p "$ROOT/logs"
echo -e "${OK} Folders created at $ROOT"
echo ""

# ── Step 4: Clone repo ───────────────────────────────────────
echo -e "${WAIT} Cloning MaxedHealth repo..."
REPO="$ROOT/app/maxhealth"
if [ -d "$REPO/.git" ]; then
  echo -e "  Repo exists — pulling latest..."
  cd "$REPO" && git pull -q
else
  git clone -q https://github.com/pete-maxhealth/maxhealth.git "$REPO"
fi
echo -e "${OK} App repo ready"
echo ""

# ── Step 5: Pipeline files ───────────────────────────────────
echo -e "${WAIT} Setting up pipeline..."
# Copy pipeline files from repo to app directory
cp "$REPO/pipeline/update_health.py" "$ROOT/app/update_health.py" 2>/dev/null || true
cp "$REPO/pipeline/amazfit.py"       "$ROOT/app/extractors/amazfit.py" 2>/dev/null || true
cp "$REPO/pipeline/withings.py"      "$ROOT/app/extractors/withings.py" 2>/dev/null || true
cp "$REPO/pipeline/ringconn.py"      "$ROOT/app/extractors/ringconn.py" 2>/dev/null || true
echo -e "${OK} Pipeline ready"
echo ""

# ── Step 6: Termux:Widget shortcut ───────────────────────────
echo -e "${WAIT} Creating home screen shortcut..."
mkdir -p ~/.shortcuts
cat > ~/.shortcuts/MaxedHealth-Sync.sh << 'SHORTCUTEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd /storage/emulated/0/maxhealth/app
bash /storage/emulated/0/maxhealth/app/maxhealth/sync.sh
SHORTCUTEOF
chmod +x ~/.shortcuts/MaxedHealth-Sync.sh
echo -e "${OK} Shortcut created (add via Termux:Widget)"
echo ""

# ── Step 7: Auto-start on boot ───────────────────────────────
echo -e "${WAIT} Setting up auto-start..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/maxedhealth.sh << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth auto-sync on device boot
sleep 10  # Wait for storage to mount
ROOT="/storage/emulated/0/maxhealth"
LOG="$ROOT/logs/boot.log"
echo "$(date) | boot sync started" >> "$LOG"
bash "$ROOT/app/maxhealth/sync.sh" >> "$LOG" 2>&1
echo "$(date) | boot sync complete" >> "$LOG"
BOOTEOF
chmod +x ~/.termux/boot/maxedhealth.sh
echo -e "${OK} Auto-start configured (requires Termux:Boot app)"
echo ""

# ── Step 8: Git identity (silent defaults) ───────────────────
git config --global user.name  "MaxedHealth" 2>/dev/null || true
git config --global user.email "maxedhealth@local" 2>/dev/null || true
git config --global pull.rebase false 2>/dev/null || true

# ── Open the app ─────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BOLD}${GREEN}  Setup complete! 🎉${NC}"
echo ""
echo -e "  ${BOLD}Open MaxedHealth:${NC}"
echo -e "  ${CYAN}pete-maxhealth.github.io/maxhealth/maxhealth.html${NC}"
echo ""
echo -e "  ${BOLD}To sync wearable data:${NC}"
echo -e "  Add Termux:Widget to your home screen"
echo -e "  → Long press home → Widgets → Termux:Widget"
echo -e "  → Drag MaxedHealth-Sync onto your home screen"
echo ""
echo -e "  ${BOLD}To update MaxedHealth:${NC}"
echo -e "  bash $REPO/setup.sh"
echo ""
# Try to open the app in browser
termux-open-url "https://pete-maxhealth.github.io/maxhealth/maxhealth.html" 2>/dev/null || true
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
