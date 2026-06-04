#!/usr/bin/env bash
# sync-hermes.sh — Sync ~/data/hermes/ to ~/hermes-repo/ and push
set -euo pipefail

SRC="$HOME/data/hermes"
DST="$HOME/hermes-repo"

echo "→ Syncing skills..."
rsync -a --delete "$SRC/skills/" "$DST/skills/"

echo "→ Syncing profiles..."
rsync -a --delete "$SRC/profiles/" "$DST/profiles/"

echo "→ Syncing cron..."
rsync -a --delete "$SRC/cron/" "$DST/cron/"

echo "→ Syncing memories..."
rsync -a --delete "$SRC/memories/" "$DST/memories/"

echo "→ Syncing SOUL.md..."
cp "$SRC/SOUL.md" "$DST/SOUL.md"

echo "→ Syncing config.yaml (sanitized)..."
cp "$SRC/config.yaml" "$DST/config.yaml"
sed -i 's/^  token: .*/  token: YOUR_DISCORD_TOKEN_HERE/' "$DST/config.yaml"

echo "→ Committing..."
cd "$DST"
git add -A
if git diff --cached --quiet; then
    echo "✓ No changes to commit"
else
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    git commit -m "Sync from Hermes — $TIMESTAMP"
    git push
    echo "✓ Pushed to GitHub"
fi
