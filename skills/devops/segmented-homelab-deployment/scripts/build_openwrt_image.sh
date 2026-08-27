#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORK_DIR="$SKILL_ROOT/build"
OPENWRT_VERSION="24.10.0"
TARGET="bcm27xx"
SUBTARGET="bcm2711"
PROFILE="rpi-4"
IMAGEBUILDER_TARBALL="openwrt-imagebuilder-${OPENWRT_VERSION}-${TARGET}-${SUBTARGET}.Linux-x86_64.tar.zst"
IMAGEBUILDER_URL="https://downloads.openwrt.org/releases/${OPENWRT_VERSION}/targets/${TARGET}/${SUBTARGET}/${IMAGEBUILDER_TARBALL}"
OUTPUT_DIR="$WORK_DIR/output"
FILES_OVERLAY="$SKILL_ROOT/templates/openwrt-image/files"

PACKAGES="\
banip \
crowdsec-firewall-bouncer \
luci-app-bcp38 \
sqm-scripts \
luci-app-sqm \
prometheus-node-exporter-lua \
tcpdump \
parted \
resize2fs \
kmod-8021q \
ip-full \
ca-bundle \
curl \
jq \
nftables \
kmod-nft-core \
kmod-nft-offload \
luci \
dropbear \
openssh-sftp-server \
coreutils-timeout \
coreutils-stat \
"

rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR" "$OUTPUT_DIR"
cd "$WORK_DIR"

echo "[1/5] Downloading OpenWrt Image Builder ${OPENWRT_VERSION} (${TARGET}/${SUBTARGET})"
curl -fsSLO "$IMAGEBUILDER_URL"

echo "[2/5] Extracting Image Builder"
tar --zstd -xf "$IMAGEBUILDER_TARBALL"
IB_DIR="$(find . -maxdepth 1 -type d -name "openwrt-imagebuilder-*" | head -n1)"
cd "$IB_DIR"

echo "[3/5] Syncing files overlay"
rm -rf files
mkdir -p files
cp -a "$FILES_OVERLAY"/. files/

echo "[4/5] Building image"
make image \
  PROFILE="$PROFILE" \
  PACKAGES="$PACKAGES" \
  FILES="files"

echo "[5/5] Collecting artifacts"
find bin/targets -type f \( -name "*.img.gz" -o -name "sha256sums" -o -name "profiles.json" \) -exec cp -f {} "$OUTPUT_DIR/" \;

ls -lh "$OUTPUT_DIR"
echo "Build completed successfully."
