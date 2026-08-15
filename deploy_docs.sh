#!/usr/bin/env bash
# deploy_docs.sh — distributes documentation files (CHANGELOG.md, README.md,
# TECHNICAL.md, user-guide.html) from Downloads into docs/, then commits
# and pushes.
#
# Deliberately separate from bump_and_deploy.sh, which is specifically for
# maxhealth.html (version bumping, div-balance check, PWA cache-busting).
# These are plain docs — no version bump, no div check needed — but they
# still get the same "verify the push actually landed" treatment, since
# git push printing something reassuring isn't proof it reached origin/main
# (this silently failed for ~100 versions before that check existed
# elsewhere in this project, per README.md's own account of it).
#
# HISTORY WORTH KNOWING: this repo used to carry two copies of these docs —
# one at the repo root, one inside docs/ — while GitHub Pages only ever
# served docs/. An earlier version of this script updated both copies to
# stay safe either way, after user-guide.html sat silently stale in docs/
# for a full night despite every root-copy deploy reporting genuine
# success. Once story.html turned out to already have been cleaned up to a
# single copy in docs/ with no root duplicate at all, that became the
# obvious permanent fix rather than a script that has to remember to sync
# two places forever: docs/ is now the only copy, for these too. Simpler,
# and the specific failure mode that caused a night of confusion literally
# cannot happen again, because there's nothing left for it to get out of
# sync with.
#
# Usage:
#   cd /storage/emulated/0/maxhealth/app/maxhealth
#   bash deploy_docs.sh "commit message describing the doc changes"

set -e

MSG="${1:-Update documentation}"
APP_DIR="$(pwd)"
DOCS_DIR="$APP_DIR/docs"
DOWNLOAD_DIR="/storage/emulated/0/Download"

FILES=(CHANGELOG.md README.md TECHNICAL.md user-guide.html)
STAGED=()

if [ ! -d "$DOCS_DIR" ]; then
  echo "⚠ docs/ folder not found at $DOCS_DIR — is this the right directory?"
  exit 1
fi

echo "── Copying updated docs from Downloads into docs/ ──"
for f in "${FILES[@]}"; do
  if [ -f "$DOWNLOAD_DIR/$f" ]; then
    cp "$DOWNLOAD_DIR/$f" "$DOCS_DIR/$f"
    STAGED+=("docs/$f")
    echo "  ✓ $f"
  else
    echo "  ⚠ $f not found in Downloads — skipping (make sure you downloaded it from the chat first)"
  fi
done

if [ ${#STAGED[@]} -eq 0 ]; then
  echo ""
  echo "Nothing to deploy — no files found in Downloads."
  exit 0
fi

echo ""
echo "── Committing only these files, not git add -A ──"
# Explicit file list, matching this project's own established caution about
# git add -A happily staging __pycache__/, stray backups, and other trash
# alongside real changes (see README.md's "Deploy after update" section).
git add "${STAGED[@]}"

if git diff --cached --quiet; then
  echo "Nothing changed — all staged files already match what's committed. Nothing to push."
  exit 0
fi

git commit -m "$MSG"

echo ""
echo "── Pushing ──"
git push

echo ""
echo "── Verifying the push actually landed on origin/main ──"
git fetch origin main --quiet
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
  echo "✓ Confirmed — origin/main now matches local HEAD ($LOCAL_HASH)"
else
  echo "⚠ MISMATCH — local HEAD ($LOCAL_HASH) does not match origin/main ($REMOTE_HASH)."
  echo "  The push may not have actually landed. Check your connection and try:"
  echo "    git push"
  echo "  again, then re-run this verification manually."
  exit 1
fi

echo ""
echo "Done. Live at:"
echo "  https://pete-maxhealth.github.io/maxhealth/CHANGELOG.md"
echo "  https://pete-maxhealth.github.io/maxhealth/README.md"
echo "  https://pete-maxhealth.github.io/maxhealth/TECHNICAL.md"
echo "  https://pete-maxhealth.github.io/maxhealth/user-guide.html"
