#!/usr/bin/env bash
# Template: Stealth scraping with anti-detection
# Usage: bash stealth-scrape.sh <url> [output-dir]
set -euo pipefail

CAMOFOX="${CAMOFOX:-$HOME/bin/camofox}"
URL="${1:?Usage: stealth-scrape.sh <url> [output-dir]}"
OUTPUT_DIR="${2:-/tmp/camofox-scrape}"

mkdir -p "$OUTPUT_DIR"
echo "Stealth scraping: $URL"
echo "Output: $OUTPUT_DIR"

# ── Step 1: Start server if needed ──
if ! $CAMOFOX health &>/dev/null; then
    echo "Starting camofox server..."
    $CAMOFOX start
    sleep 2
fi

# ── Step 2: Open with anti-detection ──
echo "Opening page..."
$CAMOFOX open "$URL"

# ── Step 3: Wait for page to stabilize ──
sleep 4

# ── Step 4: Take screenshot for verification ──
echo "Taking screenshot..."
$CAMOFOX screenshot "$OUTPUT_DIR/page.png"

# ── Step 5: Get accessibility snapshot ──
echo "Getting snapshot..."
$CAMOFOX snapshot > "$OUTPUT_DIR/snapshot.txt"

# ── Step 6: Get all links ──
echo "Getting links..."
$CAMOFOX links > "$OUTPUT_DIR/links.json" 2>/dev/null || true

# ── Step 7: Scroll and capture more content ──
for i in 1 2 3; do
    echo "Scrolling down ($i/3)..."
    $CAMOFOX scroll down
    sleep 1
done

# Final snapshot after scrolling
$CAMOFOX snapshot > "$OUTPUT_DIR/snapshot-scrolled.txt"
$CMOOFOX screenshot "$OUTPUT_DIR/page-scrolled.png"

echo ""
echo "Done! Files saved to $OUTPUT_DIR:"
ls -la "$OUTPUT_DIR"

# ── Cleanup ──
$CAMOFOX close
