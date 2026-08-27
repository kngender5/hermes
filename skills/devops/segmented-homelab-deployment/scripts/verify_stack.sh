#!/usr/bin/env bash
set -euo pipefail

OPENWRT_SSH_HOST="192.168.1.2"
OPENWRT_SSH_USER="root"
VLAN40_PROBE_HOST="10.10.40.10"
VLAN20_PROBE_HOST="10.10.20.10"
VLAN30_PROBE_HOST="10.10.30.10"
MGMT_TARGET="192.168.1.10"
COMPUTE_TARGET="10.10.20.5"
DMZ_TARGET="10.10.30.10"
CROWDSEC_LAPI_HOST="10.10.20.5"
CROWDSEC_LAPI_PORT="8080"
CROWDSEC_CTID="205"
PROM_METRICS_URL="http://192.168.1.2:9100/metrics"
IPERF_SERVER_HOST="10.10.20.20"
MAX_DOWNLOAD_BPS=997500000

log() {
  printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required command: $1" >&2; exit 1; }
}

assert_ping_blocked() {
  local src="$1"
  local dst="$2"
  if ssh "$src" "ping -c 1 -W 1 $dst >/dev/null 2>&1"; then
    echo "FAIL: expected blocked path $src -> $dst" >&2
    exit 1
  fi
}

assert_ping_allowed() {
  local src="$1"
  local dst="$2"
  if ! ssh "$src" "ping -c 2 -W 1 $dst >/dev/null 2>&1"; then
    echo "FAIL: expected allowed path $src -> $dst" >&2
    exit 1
  fi
}

require_cmd ssh
require_cmd curl
require_cmd jq
require_cmd timeout

log "Starting Layer 2 / VLAN segmentation checks"
assert_ping_blocked "$VLAN40_PROBE_HOST" "$MGMT_TARGET"
assert_ping_blocked "$VLAN40_PROBE_HOST" "$COMPUTE_TARGET"
assert_ping_allowed "$VLAN20_PROBE_HOST" "$DMZ_TARGET"
log "VLAN isolation checks passed"

log "Checking nftables threat sets and CrowdSec chain hooks"
ssh "${OPENWRT_SSH_USER}@${OPENWRT_SSH_HOST}" "nft list ruleset" > /tmp/openwrt_ruleset.txt
if ! grep -Eiq 'banip|doh|tor|threatstop' /tmp/openwrt_ruleset.txt; then
  echo "FAIL: banIP threat feed sets not found in nftables ruleset" >&2
  exit 1
fi
if ! grep -Eiq 'crowdsec.*(input|forward)' /tmp/openwrt_ruleset.txt; then
  echo "FAIL: CrowdSec bouncer rules are not active in input/forward chains" >&2
  exit 1
fi
log "Threat set verification passed"

log "Triggering simulated malicious request"
ATTACKER_IP="$(ip -4 route get "$CROWDSEC_LAPI_HOST" | awk '/src/ {print $7; exit}')"
if [ -z "$ATTACKER_IP" ]; then
  echo "FAIL: unable to determine attacker/source IP" >&2
  exit 1
fi

curl -fsS "http://10.10.30.20/?q=%27%20OR%201%3D1--" \
  -A 'sqlmap/1.8#stable (http://sqlmap.org)' >/dev/null || true

log "Waiting up to 15s for CrowdSec decision propagation"
FOUND=0
for _ in $(seq 1 15); do
  if ssh "$VLAN20_PROBE_HOST" "pct exec $CROWDSEC_CTID -- cscli decisions list -o json" | jq -e --arg ip "$ATTACKER_IP" '.[] | select(.value==$ip)' >/dev/null; then
    if ssh "${OPENWRT_SSH_USER}@${OPENWRT_SSH_HOST}" "nft list ruleset | grep -w '$ATTACKER_IP'" >/dev/null 2>&1; then
      FOUND=1
      break
    fi
  fi
  sleep 1
done

if [ "$FOUND" -ne 1 ]; then
  echo "FAIL: attacker IP not propagated to OpenWrt drop set within 15 seconds" >&2
  exit 1
fi
log "CrowdSec propagation check passed"

log "Running CAKE throughput audit"
IPERF_JSON="$(ssh "$VLAN20_PROBE_HOST" "iperf3 -c $IPERF_SERVER_HOST -t 15 -J")"
OBSERVED_BPS="$(echo "$IPERF_JSON" | jq -r '.end.sum_received.bits_per_second')"
if [ "${OBSERVED_BPS%.*}" -gt "$MAX_DOWNLOAD_BPS" ]; then
  echo "FAIL: observed throughput $OBSERVED_BPS bps exceeds expected CAKE-limited threshold" >&2
  exit 1
fi
log "CAKE throughput check passed: ${OBSERVED_BPS} bps"

log "Checking Prometheus metrics exposure and counter increments"
BEFORE_RX="$(curl -fsS "$PROM_METRICS_URL" | awk '/^node_network_receive_bytes_total\{device="eth0"\}/ {print $2; exit}')"
ssh "$VLAN20_PROBE_HOST" "ping -c 20 -W 1 192.168.1.2 >/dev/null"
AFTER_RX="$(curl -fsS "$PROM_METRICS_URL" | awk '/^node_network_receive_bytes_total\{device="eth0"\}/ {print $2; exit}')"

if [ -z "$BEFORE_RX" ] || [ -z "$AFTER_RX" ]; then
  echo "FAIL: unable to read node_network_receive_bytes_total from Prometheus endpoint" >&2
  exit 1
fi

python3 - << PY
before_val = float("$BEFORE_RX")
after_val = float("$AFTER_RX")
if after_val <= before_val:
    raise SystemExit("FAIL: Prometheus metric counter did not increment")
print("Prometheus counter increment validated")
PY

log "All validation and compliance checks passed"
