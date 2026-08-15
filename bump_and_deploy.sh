#!/bin/bash
# bump_and_deploy.sh — bumps MaxHealth version string, commits, and pushes.
# Usage: ./bump_and_deploy.sh 3.10.135 "Fix: description of change"
#
# There are TWO places the version lives in maxhealth.html:
#   1. The static "MaxedHealth v3.10.X" display text (settingsVersionDisplay)
#   2. const APP_VERSION = 'v3.10.X'  — a separate JS constant that OVERWRITES
#      #1 at runtime via initSettings(). These drifted apart for a long time
#      because only #1 was ever being bumped — the live app kept showing the
#      old APP_VERSION no matter what the file said. Both must always be
#      updated together, in the same commit, or this happens again.
set -e

NEW_VERSION="$1"
MESSAGE="$2"

if [ -z "$NEW_VERSION" ] || [ -z "$MESSAGE" ]; then
  echo "Usage: ./bump_and_deploy.sh <version> \"<commit message>\""
  echo "Example: ./bump_and_deploy.sh 3.10.135 \"Fix: whatever\""
  exit 1
fi

FILE="maxhealth.html"
DOWNLOADED="/storage/emulated/0/Download/maxhealth.html"

# Copies the freshly-downloaded file into place before anything else runs -
# folds the manual "cp ... && cd ... && bash bump_and_deploy.sh" three-step
# into one command. If nothing new was downloaded, fails loudly here rather
# than silently re-bumping whatever old copy already happens to be in place.
if [ ! -f "$DOWNLOADED" ]; then
  echo "❌ No file found at $DOWNLOADED — nothing to deploy."
  echo "Download the updated maxhealth.html first, then run this again."
  exit 1
fi
cp "$DOWNLOADED" "$FILE"
echo "Copied $DOWNLOADED into place."

CURRENT=$(grep -oP 'MaxedHealth v\K[0-9.]+' "$FILE" || echo "NOT FOUND")
APP_VER_CURRENT=$(grep -oP "const APP_VERSION = 'v\K[0-9.]+" "$FILE" || echo "NOT FOUND")
echo "Current display version:     v$CURRENT"
echo "Current APP_VERSION const:   v$APP_VER_CURRENT"
if [ "$CURRENT" != "$APP_VER_CURRENT" ]; then
  echo "WARNING: display version and APP_VERSION constant are already out of sync!"
  echo "This bump will bring both back in line at v$NEW_VERSION, but flagging it so you know it happened."
fi
echo "New version will be:         v$NEW_VERSION"
read -p "Proceed? (y/n) " CONFIRM
if [ "$CONFIRM" != "y" ]; then
  echo "Aborted."
  exit 1
fi

DISPLAY_COUNT=$(grep -c "MaxedHealth v$CURRENT" "$FILE")
if [ "$DISPLAY_COUNT" != "1" ]; then
  echo "WARNING: expected exactly 1 occurrence of the display version string, found $DISPLAY_COUNT. Aborting — check manually."
  exit 1
fi
sed -i "s/MaxedHealth v$CURRENT/MaxedHealth v$NEW_VERSION/" "$FILE"

APPVER_COUNT=$(grep -c "const APP_VERSION = 'v$APP_VER_CURRENT'" "$FILE")
if [ "$APPVER_COUNT" != "1" ]; then
  echo "WARNING: expected exactly 1 occurrence of the APP_VERSION constant, found $APPVER_COUNT. Aborting — check manually."
  exit 1
fi
sed -i "s/const APP_VERSION = 'v$APP_VER_CURRENT'/const APP_VERSION = 'v$NEW_VERSION'/" "$FILE"

OPEN=$(grep -o '<div' "$FILE" | wc -l)
CLOSE=$(grep -o '</div>' "$FILE" | wc -l)
if [ "$OPEN" != "$CLOSE" ]; then
  echo "WARNING: div mismatch — open=$OPEN close=$CLOSE. Aborting, do not commit."
  exit 1
fi
echo "Div balance OK: $OPEN open / $CLOSE close"

FINAL_DISPLAY=$(grep -oP 'MaxedHealth v\K[0-9.]+' "$FILE")
FINAL_APPVER=$(grep -oP "const APP_VERSION = 'v\K[0-9.]+" "$FILE")
if [ "$FINAL_DISPLAY" != "$NEW_VERSION" ] || [ "$FINAL_APPVER" != "$NEW_VERSION" ]; then
  echo "WARNING: post-update check failed — display=$FINAL_DISPLAY, APP_VERSION=$FINAL_APPVER, expected=$NEW_VERSION. Aborting, do not commit."
  exit 1
fi
echo "Version sync confirmed: both display text and APP_VERSION now read v$NEW_VERSION"

git add "$FILE"
git commit -m "v$NEW_VERSION: $MESSAGE"

if ! git push; then
  echo ""
  echo "❌ PUSH FAILED — the commit exists locally but was NOT sent to GitHub."
  echo "The cloud version has NOT been updated. Fix the error above, then run:"
  echo "  git push"
  echo "manually, and verify with: git log origin/main -1"
  exit 1
fi

git fetch origin main --quiet
LOCAL_HEAD=$(git rev-parse HEAD)
REMOTE_HEAD=$(git rev-parse origin/main)
if [ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]; then
  echo ""
  echo "❌ PUSH VERIFICATION FAILED"
  echo "Local HEAD:  $LOCAL_HEAD"
  echo "Remote HEAD: $REMOTE_HEAD"
  echo "These don't match — something is wrong even though git push didn't error."
  echo "Do NOT assume the cloud version updated. Investigate before continuing."
  exit 1
fi

echo "✓ Push verified — origin/main now matches local HEAD ($LOCAL_HEAD)"
echo "Done. Deployed v$NEW_VERSION to cloud."
