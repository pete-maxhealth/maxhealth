#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════════
#  MaxedHealth — sync.sh
#
#  One command to sync all wearable data into the app.
#
#  What it does:
#    1. Scans Download folder for wearable exports
#    2. Moves them to the pipeline inbox
#    3. Runs the pipeline (extracts, merges, writes combined.csv)
#    4. Tells you to import in the app
#
#  Usage:
#    bash /storage/emulated/0/maxhealth/app/maxhealth/sync.sh
#
#  Or add to your home screen as a Termux shortcut.
# ═══════════════════════════════════════════════════════════════

set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

ROOT="/storage/emulated/0/maxhealth"
APP="$ROOT/app"
INBOX="$ROOT/data/inbox"
DOWNLOAD="/storage/emulated/0/Download"
LOG="$ROOT/logs/pipeline.log"

echo ""
echo -e "${BOLD}${GREEN}MaxedHealth — Sync${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Step 1: Find exports in Download ────────────────────────
echo -e "${BOLD}Step 1/3 — Checking Download folder...${NC}"
mkdir -p "$INBOX"

moved=0
amazfit_found=false
needs_zarchiver=false

move_to_inbox() {
  local file="$1"
  local name=$(basename "$file")
  if [ -f "$INBOX/$name" ]; then
    echo -e "  ${DIM}skipped — $name already in inbox${NC}"
  else
    cp "$file" "$INBOX/$name"
    echo -e "  ${GREEN}✓${NC} $name"
    moved=$((moved+1))
  fi
}

# Zepp/Amazfit numeric zip
for f in "$DOWNLOAD"/[0-9]*.zip; do
  [ -f "$f" ] && move_to_inbox "$f" && amazfit_found=true && needs_zarchiver=true
done

# Withings
for f in "$DOWNLOAD"/export_*.zip "$DOWNLOAD"/[Ww]ithings*.zip "$DOWNLOAD"/[Hh]ealth[Mm]ate*.zip; do
  [ -f "$f" ] && move_to_inbox "$f"
done

# RingConn
for f in "$DOWNLOAD"/[Rr]ing*.csv "$DOWNLOAD"/[Rr]ingConn*.csv; do
  [ -f "$f" ] && move_to_inbox "$f"
done

# Garmin
for f in "$DOWNLOAD"/[Gg]armin*.zip "$DOWNLOAD"/[Gg]armin*.csv; do
  [ -f "$f" ] && move_to_inbox "$f"
done

# Check if inbox already has pre-extracted Zepp folders
if [ -d "$INBOX/ACTIVITY" ] || [ -d "$INBOX/SLEEP" ] || [ -d "$INBOX/HEARTRATE_AUTO" ]; then
  amazfit_found=true
  needs_zarchiver=false
  echo -e "  ${GREEN}✓${NC} Zepp pre-extracted folders found in inbox"
fi

if [ "$moved" -eq 0 ] && [ "$amazfit_found" = false ]; then
  # Check if inbox already has files from a previous move
  inbox_count=$(ls "$INBOX" 2>/dev/null | grep -v "^old$" | wc -l)
  if [ "$inbox_count" -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} $inbox_count item(s) already in inbox from previous move"
  else
    echo ""
    echo -e "  ${YELLOW}Nothing found.${NC}"
    echo -e "  Export from your wearable app first, then re-run sync.sh."
    echo ""
    echo "  Expected files in $DOWNLOAD:"
    echo "    Zepp/Amazfit: 7084918973_xxxx.zip (numeric prefix)"
    echo "    Withings:     export_xxxx.zip"
    echo "    RingConn:     RingConn_xxxx.csv"
    echo ""
    exit 0
  fi
fi

# ── Amazfit/Zepp ZArchiver warning ──────────────────────────
if [ "$needs_zarchiver" = true ]; then
  echo ""
  echo -e "  ${YELLOW}Zepp zip detected.${NC}"
  echo -e "  Zepp exports are AES-256 encrypted — Python can't open them directly."
  echo -e "  Before continuing:"
  echo -e "    1. Open ${BOLD}ZArchiver${NC} (Play Store, free)"
  echo -e "    2. Navigate to: $INBOX"
  echo -e "    3. Tap the zip → extract here → enter your Zepp password"
  echo -e "    4. Re-run this script"
  echo ""
  echo -e "  ${DIM}Already extracted? The script will detect the folders automatically.${NC}"
  echo ""
  exit 0
fi

echo ""

# ── Step 2: Run pipeline ─────────────────────────────────────
echo -e "${BOLD}Step 2/3 — Running pipeline...${NC}"
echo ""

cd "$APP"
python update_health.py

PIPELINE_EXIT=$?

echo ""

if [ $PIPELINE_EXIT -ne 0 ]; then
  echo -e "${RED}Pipeline encountered an error. Check the log:${NC}"
  echo -e "  $LOG"
  echo ""
  exit 1
fi

# ── Step 3: Done ─────────────────────────────────────────────
echo -e "${BOLD}Step 3/3 — Import into MaxedHealth${NC}"
echo ""
echo -e "  Open MaxedHealth → ${BOLD}Import${NC} tab"
echo -e "  Tap ${BOLD}Load combined.csv${NC}"
echo -e "  File is at:"
echo -e "  ${GREEN}$ROOT/data/tables/combined.csv${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}${BOLD}Sync complete.${NC}"
echo ""
