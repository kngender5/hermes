# Cron Consolidation Pattern

## When to Apply
When multiple cron jobs run similar scripts on overlapping intervals, consolidate into fewer jobs that do more per run. This reduces: token usage, scheduler load, log fragmentation, and alert noise.

## Example from Session 2026-06-03

### Before (6 jobs, all deliver to local)
| Job | Interval | Script |
|-----|----------|--------|
| security-check-wsl-windows | `*/5` | `~/bin/security-check` |
| inject-detect-scan | `*/10` | `~/bin/inject-detect scan` |
| canary-integrity-check | `*/15` | `~/bin/canary check` |
| security-logging-collect | `*/30` | `~/bin/security-logging collect` |
| countermeasures-auto | `0 * * *` | `~/bin/countermeasures` |
| daily-security-report | `0 8 * *` | `~/bin/security-logging report` |

### After (3 jobs + 1 heartbeat)
| Job | Interval | Script | Notes |
|-----|----------|--------|-------|
| unified-security-check | `*/5` | `~/bin/security-check.sh` | Combines WSL check + canary + inject + countermeasures dry-run |
| countermeasures-auto | `0 * * *` | `~/bin/countermeasures` | Dry-run first, auto only on real threats |
| daily-infra-report | `0 8 * * *` | multiple | Aggregated summary, deliver=origin |
| hermes-heartbeat | `0 12,18 * *` | inline | Quick health, alert only if wrong |

### Key Techniques
1. **Unify overlapping scripts** into one script that runs all checks sequentially
2. **Smart filtering** — suppress known false positives (apt/dpkg noise, localhost triggers, IN_ACCESS vs IN_MODIFY)
3. **Silent-by-default** — only alert when `ALERTS` found, otherwise log locally
4. **deliver=origin** on daily reports so one summary arrives instead of 6 separate pings
5. **Heartbeat pattern** — periodic "am I alive?" that stays green, only surfaces on failure

### Anti-Pattern to Flag During Audits
`N` cron jobs where `N/3` run the same underlying script or scripts in the same domain with staggered intervals. Consolidate.

### Script Template for Unified Checks
```bash
#!/bin/bash
# unified-check.sh — combine multiple checks, alert only on real issues
set -euo pipefail
ALERTS=()

# Run check A
if ! output_A=$(script-A 2>&1); then
    ALERTS+=("Check A: issue found")
fi

# Run check B (filter known noise)
output_B=$(script-B 2>&1) || true
REAL=$(echo "$output_B" | grep "ALERT" | grep -v "known_noise_pattern" || true)
if [ -n "$REAL" ]; then
    ALERTS+=("Check B: $REAL")
fi

# Deliver only if real alerts
if [ ${#ALERTS[@]} -gt 0 ]; then
    curl -s ntfy.sh/topic -d "$(printf '%s\n' "${ALERTS[@]}")" \
        -H "Priority: 4" -H "Title: Alert"
fi
```
