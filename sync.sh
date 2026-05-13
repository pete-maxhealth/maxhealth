#!/data/data/com.termux/files/usr/bin/bash
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
echo -e "${BOLD}Step 1/3 — Checking Download folder...${NC}"
mkdir -p "$INBOX"
moved=0; amazfit_found=false; needs_zarchiver=false
move_to_inbox() {
  local file="$1"; local name=$(basename "$file")
  if [ -f "$INBOX/$name" ]; then echo -e "  ${DIM}skipped — $name already in inbox${NC}"
  else mv "$file" "$INBOX/$name"; echo -e "  ${GREEN}✓${NC} $name → inbox"; moved=$((moved+1)); fi
}
while IFS= read -r -d '' file; do
  name=$(basename "$file"); lower=$(echo "$name" | tr '[:upper:]' '[:lower:]')
  if echo "$name" | grep -qE '^[0-9]+.*\.zip$'; then
    move_to_inbox "$file"; amazfit_found=true; needs_zarchiver=true
  elif echo "$lower" | grep -qE '^(export_|data.?export|withings|healthmate).*\.(zip)$'; then
    move_to_inbox "$file"
  elif echo "$lower" | grep -qE '^(ringconn|ring_conn|data_pet_).*\.(zip|csv)$'; then
    move_to_inbox "$file"
  elif echo "$lower" | grep -qE '^(garmin|activity).*\.(zip|csv)$'; then
    move_to_inbox "$file"
  fi
done < <(find "$DOWNLOAD" -maxdepth 1 \( -name "*.zip" -o -name "*.csv" \) -print0 2>/dev/null)
if [ -d "$INBOX/ACTIVITY" ] || [ -d "$INBOX/SLEEP" ] || [ -d "$INBOX/HEARTRATE_AUTO" ]; then
  amazfit_found=true; needs_zarchiver=false; echo -e "  ${GREEN}✓${NC} Zepp pre-extracted folders found"
fi
if [ "$moved" -eq 0 ] && [ "$amazfit_found" = false ]; then
  inbox_count=$(ls "$INBOX" 2>/dev/null | grep -v "^old$" | wc -l)
  if [ "$inbox_count" -gt 0 ]; then echo -e "  ${GREEN}✓${NC} $inbox_count item(s) already in inbox"
  else
    echo -e "\n  ${YELLOW}Nothing found.${NC}"; echo -e "  Export from your wearable app first."
    echo -e "\n  Expected in $DOWNLOAD:"; echo "    Zepp: 7084918973_xxxx.zip"; echo "    Withings: Data Export-xxx.zip or export_xxx.zip"; echo "    RingConn: data_PET_xxx.zip or RingConn_xxx.csv"
    exit 0; fi
fi
if [ "$needs_zarchiver" = true ]; then
  echo -e "\n  ${YELLOW}Zepp zip detected — extract with ZArchiver first:${NC}"
  echo "    1. Open ZArchiver → navigate to $INBOX"; echo "    2. Tap zip → extract here → enter Zepp password"; echo "    3. Re-run sync.sh"
  exit 0
fi
echo ""
echo -e "${BOLD}Step 2/3 — Running pipeline...${NC}"
echo ""
cd "$APP" && python update_health.py
PIPELINE_EXIT=$?
echo ""
if [ $PIPELINE_EXIT -ne 0 ]; then echo -e "${RED}Pipeline error — check $LOG${NC}"; exit 1; fi
echo -e "${BOLD}Step 3/3 — Import into MaxedHealth${NC}"
echo ""
echo -e "  Open MaxedHealth → Import tab → Load combined.csv"
echo -e "  ${GREEN}$ROOT/data/tables/combined.csv${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}${BOLD}Sync complete.${NC}"
echo ""
