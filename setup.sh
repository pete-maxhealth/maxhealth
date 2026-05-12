#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════════
#  MaxedHealth — One-Command Setup Script
#
#  Run this once in Termux:
#    curl -sSL https://raw.githubusercontent.com/pete-maxhealth/maxhealth/main/setup.sh | bash
#
#  Real on-device structure after setup:
#    /storage/emulated/0/MaxHealth/
#    ├── app/
#    │   ├── maxhealth/          ← git repo (web app + docs)
#    │   ├── extractors/         ← pipeline extractors
#    │   ├── update_health.py    ← pipeline entry point
#    │   └── server.py
#    ├── data/
#    │   ├── inbox/              ← drop wearable exports here
#    │   ├── tables/             ← combined.csv lives here
#    │   └── backup/
#    └── logs/
# ═══════════════════════════════════════════════════════════════

set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

echo ""
echo -e "${BOLD}${GREEN}MAXEDHEALTH — Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Step 1: Storage ─────────────────────────────────────────
echo -e "${YELLOW}Step 1/5: Requesting storage access...${NC}"
termux-setup-storage
sleep 2
echo -e "${GREEN}✓ Storage access granted${NC}"
echo ""

# ── Step 2: Packages ────────────────────────────────────────
echo -e "${YELLOW}Step 2/5: Installing packages...${NC}"
pkg update -y -q
pkg install -y -q python git curl
echo -e "${GREEN}✓ Packages ready${NC}"
echo ""

# ── Step 3: Folder structure ────────────────────────────────
echo -e "${YELLOW}Step 3/5: Creating folder structure...${NC}"
ROOT="/storage/emulated/0/MaxHealth"
mkdir -p "$ROOT/app"
mkdir -p "$ROOT/data/inbox"
mkdir -p "$ROOT/data/tables"
mkdir -p "$ROOT/data/backup"
mkdir -p "$ROOT/logs"
echo -e "${GREEN}✓ Folders created${NC}"
echo ""

# ── Step 4: Clone or update repo ────────────────────────────
echo -e "${YELLOW}Step 4/5: Setting up git repo...${NC}"
REPO="$ROOT/app/maxhealth"
if [ -d "$REPO/.git" ]; then
  echo -e "  Repo exists — pulling latest..."
  cd "$REPO" && git pull
else
  echo -e "  Cloning repo..."
  git clone https://github.com/pete-maxhealth/maxhealth.git "$REPO"
fi
echo -e "${GREEN}✓ Repo ready at $REPO${NC}"
echo ""

# ── Step 5: Boot script ─────────────────────────────────────
echo -e "${YELLOW}Step 5/5: Setting up auto-run on boot...${NC}"
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start-maxedhealth.sh << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
# MaxedHealth — auto-run on boot
# Moves any wearable exports from Download to inbox, then runs pipeline
ROOT="/storage/emulated/0/MaxHealth"
APP="$ROOT/app"
INBOX="$ROOT/data/inbox"
LOG="$ROOT/logs/pipeline.log"
DOWNLOAD="/storage/emulated/0/Download"

# Move wearable exports from Download to inbox
for f in "$DOWNLOAD"/[0-9]*.zip "$DOWNLOAD"/export_*.zip "$DOWNLOAD"/[Rr]ing*.csv; do
  [ -f "$f" ] && cp "$f" "$INBOX/" && echo "$(date '+%Y-%m-%d %H:%M:%S') | boot | inbox | moved | $(basename $f)" >> "$LOG"
done

# Run pipeline if inbox has files
if [ "$(ls -A $INBOX 2>/dev/null)" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') | boot | pipeline | start | inbox has files" >> "$LOG"
  cd "$APP" && python update_health.py >> "$LOG" 2>&1
fi
BOOTEOF
chmod +x ~/.termux/boot/start-maxedhealth.sh
echo -e "${GREEN}✓ Boot script installed${NC}"
echo ""

# ── Run distribute.sh to complete setup ─────────────────────
echo -e "${YELLOW}Running initial file distribution...${NC}"
bash "$REPO/distribute.sh"

# ── Done ────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}${BOLD}Setup complete!${NC}"
echo ""
echo "  Open MaxedHealth in Chrome:"
echo "  pete-maxhealth.github.io/maxhealth/maxhealth.html"
echo ""
echo "  After every git pull, run:"
echo "  bash /storage/emulated/0/MaxHealth/app/maxhealth/distribute.sh"
echo ""
