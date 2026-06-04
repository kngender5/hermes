---
name: system-notifications-monitoring
description: "Push notifications via ntfy.sh, system health monitoring, weather alerts, Docker checks, and cron-based alerts. Triggered by: setup notifications, push alerts, monitor system, health check cron, weather alerts, ntfy, cron alerts."
tags: [monitoring, notifications, ntfy, cron, alerts, health-check]
---

# System Notifications & Monitoring

Set up notification pipelines and system monitoring via cron.

## Architecture

```
[cron] → [bash script] → [curl → ntfy.sh] → [phone push]
```

Multiple topics allow per-category notification control in the ntfy app.

## ntfy.sh Setup

### Server choice
- **nttfy.sh public** (recommended for quick start) — free, no setup, unlimited
- **Self-hosted** — Docker + domain + Caddy for HTTPS, full control

### Topic design
One topic per notification category so users control per-topic settings in the app:

| Topic | Purpose | Default priority |
|-------|---------|-----------------|
| `hermes-alerts` | System health issues | 4 (high) |
| `hermes-heartbeat` | Daily alive signal | 2 (low) |
| `hermes-weather` | Weather forecasts | 2 (low) |
| `hermes-security` | Security updates | 4 when critical |
| `hermes-docker` | Container issues | 4 (high) |

## Notification Scripts

Place in `~/bin/`, `chmod +x`, schedule via `crontab -e`.

### Threshold alert pattern (push only when unhealthy)
```bash
#!/bin/bash
export TERM=dumb
NTFY_TOPIC="hermes-alerts"
SERVER="https://ntfy.sh"
ALERTS=()

USAGE=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$USAGE" -gt 85 ]; then
    ALERTS+=("Disk: ${USAGE}%")
fi

if [ ${#ALERTS[@]} -gt 0 ]; then
    MSG=$(printf '%s\n' "${ALERTS[@]}")
    curl -s -X POST "$SERVER/$NTFY_TOPIC" \
        -H "Title: Alert — $(hostname)" \
        -H "Priority: 4" \
        -H "Tags: warning" \
        -d "$MSG"
else
    echo "$(date '+%Y-%m-%d %H:%M') — OK"
fi
```

### Periodic status pattern (always push)
```bash
#!/bin/bash
export TERM=dumb
# ... gather data into MSG ...
curl -s -X POST "https://ntfy.sh/hermes-heartbeat" \
    -H "Title: Hermes OK — $(date '+%A %d.%m')" \
    -H "Priority: 2" \
    -d "$MSG"
```

## ntfy v2 Pitfalls

- **Subscribe syntax changed:** `ntfy hermes-alerts --poll` does NOT work in v2. Use `ntfy subscribe hermes-alerts` instead.
- **No message history on free tier:** ntfy.sh does not support retrieving past messages. If you weren't subscribed when a message was sent, it's gone. Log alerts locally for audit trail.
- **Long-poll blocks:** `ntfy subscribe` blocks indefinitely waiting for new messages. Use `terminal(background=true)`. The HTTP `/json?poll=1` endpoint also blocks -- it does NOT return historical messages.
- **curl long-poll also blocks:** `curl "https://ntfy.sh/topic/json?since=1h&poll=0"` will still time out. There is no non-blocking history fetch.

## Shell Gotchas

- **`export TERM=dumb`** — prevents xterm-256color escapes in variable output from scripts
- **`grep -c || echo "0"`** — AVOID. `grep` exit 1 + prints `0`, `||` adds another `0` → "0\n0" breaks numeric comparison. Fix: `$(grep -c "pattern" ; true)` then `${VAR:-0}`
- **`IFS='|' read -r A B C <<< "$VAR"`** — cleaner than multiple `cut` for multi-field parsing
- **JSON via python3** — pipe via stdin, avoid string interpolation of untrusted data

## Cron Schedule

```cron
SHELL=/bin/bash
PATH=/home/kng/bin:/usr/local/bin:/usr/bin:/bin

# System health — hourly
0 * * * * /home/kng/bin/system-health-check >> /tmp/hermes-health.log 2>&1
# Heartbeat — daily 08:00
0 8 * * * /home/kng/bin/hermes-heartbeat >> /tmp/hermes-heartbeat.log 2>&1
# Weather — 5x daily
0 7 * * * /home/kng/bin/vaermelding >> /tmp/hermes-weather.log 2>&1
30 11 * * * /home/kng/bin/vaermelding >> /tmp/hermes-weather.log 2>&1
20 14 * * * /home/kng/bin/vaermelding >> /tmp/hermes-weather.log 2>&1
20 16 * * * /home/kng/bin/vaermelding >> /tmp/hermes-weather.log 2>&1
30 19 * * * /home/kng/bin/vaermelding >> /tmp/hermes-weather.log 2>&1
# Security updates — 08:00 + 20:00
0 8,20 * * * /home/kng/bin/security-updates-check >> /tmp/hermes-security.log 2>&1
# Docker health — every 30 min
*/30 * * * * /home/kng/bin/docker-health-check >> /tmp/hermes-docker.log 2>&1
```

## Health Check Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Disk | >80% | >90% |
| Memory | >85% | >95% |
| CPU load | >nproc | >nproc×2 |
| Swap | >50% | >80% |

## Docker Health

Check both stopped containers and unhealthy state. Distinguish manual stops (restart policy = `no`) from unexpected exits (restart policy = `always` or `unless-stopped`).

## Verification

1. Run each script manually: `~/bin/script-name`
2. Confirm receipt in ntfy app
3. `crontab -l` to verify cron entries
4. `tail /tmp/hermes-*.log` for debugging

## References

- `references/ntfy-cli-usage.md` — ntfy CLI reference
- `references/met-no-weather-api.md` — MET Norway API details
