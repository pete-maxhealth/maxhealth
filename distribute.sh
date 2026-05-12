#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════════
#  MaxedHealth — distribute.sh
#
#  Run this after every git pull to:
#    1. Copy updated web files from repo to their serving location
#    2. Move wearable exports from Download folder to pipeline inbox
#    3. Report what was done and flag any issues
#
#  Usage:
#    cd /storage/emulated/0/MaxHealth/app/maxhealth
#    bash distribute.sh
#
#  Or from anywhere:
#    bash /storage/emulated/0/MaxHealth/app/maxhealth/distribute.sh
# ═══════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# ── Paths ────────────────────────────────────────────────────
REPO="/storage/emulated/0/MaxHealth/app/maxhealth"
APP="/storage/emulated/0/MaxHealth/app"
ROOT="/storage/emulated/0/MaxHealth"
INBOX="$ROOT/data/inbox"
DOWNLOAD="/storage/emulated/0/Download"
LOG="$ROOT/logs/distribute.log"

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "$(timestamp) | $1" >> "$LOG" 2>/dev/null || true; }

echo ""
echo -e "${BOLD}${GREEN}MaxedHealth — distribute.sh${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p "$ROOT/logs"
log "distribute.sh started"

# ── Section 1: Verify repo location ─────────────────────────
if [ ! -f "$REPO/maxhealth.html" ]; then
  echo -e "${RED}Error: Cannot find repo at $REPO${NC}"
  echo "Run this script from inside the maxhealth repo, or check the path."
  exit 1
fi
echo -e "${GREEN}✓${NC} Repo found at $REPO"

# ── Section 2: Clean up root-level duplicates ────────────────
echo ""
echo -e "${BOLD}Cleaning up orphaned files at MaxHealth root...${NC}"

ORPHANS=(
  "maxhealth.html" "sw.js" "manifest.json" "carer.html"
  "why-free.html" "update_health.py" "setup.sh"
  "README.md" "README.txt" "TECHNICAL.md" "INSTALL.md"
  "gbm_patient_guide.html" "icon-512.png"
)

cleaned=0
for f in "${ORPHANS[@]}"; do
  if [ -f "$ROOT/$f" ]; then
    rm "$ROOT/$f"
    echo -e "  ${YELLOW}removed${NC} $ROOT/$f"
    log "removed orphan: $ROOT/$f"
    ((cleaned++)) || true
  fi
done

# Clean orphaned directories at root level (not app/, data/, docs/, logs/, icons/, system/, cloudflare/, tracker/, launch/)
KEEP_DIRS=("app" "data" "docs" "logs" "icons" "system" "cloudflare" "tracker" "launch")
for d in "$ROOT"/*/; do
  dirname=$(basename "$d")
  keep=false
  for k in "${KEEP_DIRS[@]}"; do
    [ "$dirname" = "$k" ] && keep=true && break
  done
  if [ "$keep" = false ] && [ -d "$d" ]; then
    echo -e "  ${YELLOW}skipping dir${NC} $d — review manually before removing"
  fi
done

if [ "$cleaned" -eq 0 ]; then
  echo -e "  ${GREEN}Nothing to clean — root is already tidy${NC}"
else
  echo -e "  ${GREEN}Removed $cleaned orphaned file(s)${NC}"
fi

# ── Section 3: Move wearable exports from Download to inbox ──
echo ""
echo -e "${BOLD}Checking Download folder for wearable exports...${NC}"
mkdir -p "$INBOX"

moved=0
skipped=0

# Move known wearable export patterns
move_to_inbox() {
  local file="$1"
  local name=$(basename "$file")
  if [ -f "$INBOX/$name" ]; then
    echo -e "  ${YELLOW}skipped${NC} $name — already in inbox"
    log "skipped (already exists): $name"
    ((skipped++)) || true
  else
    cp "$file" "$INBOX/$name"
    echo -e "  ${GREEN}moved${NC}  $name → inbox"
    log "moved to inbox: $name"
    ((moved++)) || true
    # Ask user if they want to remove from Download
    echo -e "         ${BLUE}Remove from Download? (y/n):${NC} \c"
    read -r answer < /dev/tty
    [ "$answer" = "y" ] && rm "$file" && echo -e "         ${GREEN}removed from Download${NC}"
  fi
}

# Zepp/Amazfit: numeric-prefixed zip
for f in "$DOWNLOAD"/[0-9]*.zip; do
  [ -f "$f" ] && move_to_inbox "$f"
done

# Withings: export_ prefix zip
for f in "$DOWNLOAD"/export_*.zip "$DOWNLOAD"/withings*.zip "$DOWNLOAD"/Withings*.zip; do
  [ -f "$f" ] && move_to_inbox "$f"
done

# RingConn: csv files with ring in name
for f in "$DOWNLOAD"/[Rr]ing*.csv "$DOWNLOAD"/[Rr]ingConn*.csv; do
  [ -f "$f" ] && move_to_inbox "$f"
done

# Garmin: activity csv
for f in "$DOWNLOAD"/garmin*.zip "$DOWNLOAD"/Garmin*.zip; do
  [ -f "$f" ] && move_to_inbox "$f"
done

if [ "$moved" -eq 0 ] && [ "$skipped" -eq 0 ]; then
  echo -e "  No wearable exports found in $DOWNLOAD"
  echo -e "  (Looking for: numeric*.zip, export_*.zip, Ring*.csv)"
fi

# ── Section 4: Report inbox contents ─────────────────────────
echo ""
echo -e "${BOLD}Inbox contents:${NC}"
if [ "$(ls -A $INBOX 2>/dev/null)" ]; then
  ls -lh "$INBOX" | tail -n +2 | while read line; do
    echo -e "  $line"
  done
else
  echo -e "  ${YELLOW}Inbox is empty${NC} — no exports to process"
fi

# ── Section 5: Run pipeline if inbox has files ───────────────
echo ""
if [ "$(ls -A $INBOX 2>/dev/null)" ]; then
  echo -e "${BOLD}Inbox has files. Run the pipeline now?${NC}"
  echo -e "  ${BLUE}(y) Run pipeline   (a) Amazfit with password   (d) Dry run   (n) Skip:${NC} \c"
  read -r answer < /dev/tty

  case "$answer" in
    y)
      echo ""
      cd "$APP"
      python update_health.py
      ;;
    a)
      echo -e "  ${BLUE}Zepp/Amazfit password:${NC} \c"
      read -r pw < /dev/tty
      echo ""
      cd "$APP"
      python update_health.py --device amazfit --password "$pw"
      ;;
    d)
      echo ""
      cd "$APP"
      python update_health.py --dry-run
      ;;
    *)
      echo -e "  ${YELLOW}Skipped — run manually:${NC}"
      echo -e "  cd $APP && python update_health.py"
      ;;
  esac
else
  echo -e "${YELLOW}Pipeline not run — inbox is empty.${NC}"
  echo -e "Export from your wearable and re-run distribute.sh, or copy files to:"
  echo -e "  $INBOX"
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Done.${NC}"
echo ""
echo "  Next: open MaxedHealth → Import tab → Select combined.csv"
echo "  Path: $ROOT/data/tables/combined.csv"
echo ""
log "distribute.sh complete (moved=$moved, cleaned=$cleaned)"
