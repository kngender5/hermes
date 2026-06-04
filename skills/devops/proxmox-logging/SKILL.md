---
name: proxmox-logging
description: >
  Error handling, structured logging, and event tracking for Proxmox VE
  automation. Covers the proxmoxer Python API and CLI (qm/pct/pvesm).
  Use when: writing Proxmox automation scripts, debugging PVE API failures,
  adding logging to VM/LXC/storage operations, building Proxmox cron jobs,
  handling cluster quorum errors, tracking task progress.
tags: [proxmox, logging, error-handling, events, automation, pve]
---

# Proxmox Logging — Error Handling & Structured Event Tracking

Robust error handling and structured logging for Proxmox VE automation
scripts (Python proxmoxer API and shell CLI wrappers).

## Architecture

```
[Automation Script]
    |
    +-- ProxmoxLogger (structured JSONL log)
    |     ~/data/proxmox-logs/
    |     +-- events.jsonl        # All operations (create/start/stop/migrate)
    |     +-- errors.jsonl        # Error-only subset with full context
    |     +-- tasks.jsonl         # Task tracking (UPID-based)
    |     +-- audit.jsonl         # Config changes for rollback tracing
    |
    +-- Error Handler
    |     +-- Retry with exponential backoff
    |     +-- Context capture (what failed + surrounding state)
    |     +-- Alert escalation (ntfy.sh integration)
    |
    +-- Event Categories
          +-- vm.*          (create, start, stop, migrate, snapshot, clone, destroy)
          +-- ct.*          (create, start, stop, exec, snapshot)
          +-- storage.*     (add, resize, move-disk, backup, restore)
          +-- cluster.*     (join, leave, quorum, ha, corosync)
          +-- network.*     (bridge, vlan, firewall)
          +-- auth.*        (login, token, permission changes)
          +-- task.*        (upid, status polling, completion)
```

## Quick Start

```python
from proxmox_logging import ProxmoxLogger

log = ProxmoxLogger(
    base_dir="~/data/proxmox-logs",
    node="pve1",
)

# Log an event
log.event("vm.start", vmid=100, name="web-server")
log.event("vm.stop", vmid=100, name="web-server", method="shutdown")

# Log an error with full context
try:
    proxmox.nodes("pve1").qemu(100).status.start.post()
except Exception as e:
    log.error("vm.start_failed", vmid=100, error=str(e))

# Log a task and poll it
upid = log.start_task("vm.backup", vmid=100)
# ... poll proxmox nodes('pve1').tasks(upid).status.get() ...
log.end_task(upid, status="ok", duration=45.2)

# Log a config change for audit trail
log.audit("vm.config_change", vmid=100,
         field="memory", old=2048, new=4096,
         reason="scaling for traffic spike")

# Get recent errors
recent = log.get_errors(hours=24, limit=50)

# Get operation summary
summary = log.get_summary(hours=24)
# Returns: {"vm.start": 5, "vm.stop": 3, "vm.start_failed": 1, ...}
```

## Python Module — proxmox_logging.py

Save to `~/bin/proxmox_logging.py` or your project directory:

```python
#!/usr/bin/env python3
"""
ProxmoxLogger — structured JSONL logging for Proxmox VE automation.

Usage:
    from proxmox_logging import ProxmoxLogger

    log = ProxmoxLogger(base_dir="~/data/proxmox-logs", node="pve1")

    log.event("vm.start", vmid=100)
    log.error("vm.start_failed", vmid=100, error="timeout")
    log.audit("vm.config_change", vmid=100, field="memory", old=2048, new=4096)
    upid = log.start_task("vm.backup", vmid=100)
    log.end_task(upid, status="ok", duration=42.0)
"""

import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class ProxmoxLogger:
    """Structured JSONL logger for Proxmox VE operations."""

    LOG_FILES = {
        "events": "events.jsonl",
        "errors": "errors.jsonl",
        "tasks": "tasks.jsonl",
        "audit": "audit.jsonl",
    }

    # Error categories for classification
    ERROR_CATEGORIES = {
        # Proxmox API HTTP errors
        400: "bad_request",
        401: "auth_failure",
        403: "permission_denied",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        429: "rate_limited",
        500: "internal_error",
        502: "bad_gateway",
        503: "service_unavailable",
        504: "gateway_timeout",
        # Connection errors
        "ConnectionError": "connection_failure",
        "TimeoutError": "timeout",
        "SSLError": "ssl_error",
        # Application errors
        "LockError": "vm_locked",
        "QuotaExceeded": "quota_exceeded",
        "DiskFull": "disk_full",
        "OutOfMemory": "out_of_memory",
    }

    def __init__(self, base_dir: str = "~/data/proxmox-logs",
                 node: str = "pve1", alert_topic: Optional[str] = None):
        self.base_dir = Path(base_dir).expanduser()
        self.node = node
        self.alert_topic = alert_topic  # ntfy.sh topic for critical alerts
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create log directory structure."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        for name in self.LOG_FILES:
            path = self.base_dir / self.LOG_FILES[name]
            if not path.exists():
                path.touch()

    def _now(self) -> str:
        """ISO 8601 timestamp with timezone."""
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _write(self, log_type: str, entry: dict):
        """Append a JSONL entry to the specified log file."""
        path = self.base_dir / self.LOG_FILES[log_type]
        with open(path, "a") as f:
            f.write(json.dumps(entry, default=str, ensure_ascii=False) + "\n")

    def _build_entry(self, event_type: str, **kwargs) -> dict:
        """Build a standard log entry."""
        return {
            "timestamp": self._now(),
            "node": self.node,
            "type": event_type,
            **kwargs,
        }

    def event(self, event_type: str, **kwargs):
        """
        Log a normal operation event.

        Examples:
            log.event("vm.create", vmid=100, name="web-server")
            log.event("ct.start", vmid=200)
            log.event("storage.move_disk", vmid=100, disk="scsi0",
                      src="local-lvm", dst="zfs-pool")
        """
        entry = self._build_entry(event_type, **kwargs)
        self._write("events", entry)
        return entry

    def error(self, error_type: str, exception: Optional[Exception] = None,
              http_status: Optional[int] = None, **kwargs):
        """
        Log an error with full context capture.

        Args:
            error_type: Error classification (e.g. "vm.start_failed")
            exception: The caught exception object
            http_status: HTTP status code if from API call
            **kwargs: Additional context (vmid, node, operation, etc.)
        """
        entry = self._build_entry(error_type, **kwargs)

        if exception:
            entry["error"] = str(exception)
            entry["error_type"] = type(exception).__name__
            entry["traceback"] = traceback.format_exc()

        if http_status:
            entry["http_status"] = http_status
            entry["category"] = self.ERROR_CATEGORIES.get(
                http_status, "unknown"
            )

        # Classify error severity
        entry["severity"] = self._classify_error(entry)

        self._write("errors", entry)

        # Alert on critical errors
        if entry["severity"] == "critical" and self.alert_topic:
            self._send_alert(entry)

        return entry

    def _classify_error(self, entry: dict) -> str:
        """Classify error severity based on category."""
        category = entry.get("category", "")
        node = entry.get("node", self.node)

        critical_categories = {
            "internal_error", "disk_full", "out_of_memory",
            "quota_exceeded", "service_unavailable",
        }
        warning_categories = {
            "timeout", "connection_failure", "rate_limited",
            "bad_gateway", "gateway_timeout", "vm_locked",
            "auth_failure", "permission_denied",
        }

        if category in critical_categories:
            return "critical"
        elif category in warning_categories:
            return "warning"
        elif category in ("not_found", "validation_error", "bad_request"):
            return "error"
        return "error"

    def _send_alert(self, entry: dict):
        """Send critical error alert via ntfy.sh."""
        import subprocess
        topic = self.alert_topic
        title = f"Proxmox CRITICAL — {entry.get('type', 'unknown')}"
        msg = (
            f"Node: {entry.get('node', self.node)}\n"
            f"Error: {entry.get('error', 'N/A')}\n"
            f"Context: {json.dumps({k: v for k, v in entry.items()
                                     if k not in ('timestamp','traceback',
                                                  'node','severity')},
                                    default=str)}"
        )
        try:
            subprocess.run(
                ["curl", "-s", "-X", "POST", f"https://ntfy.sh/{topic}",
                 "-H", f"Title: {title}",
                 "-H", "Priority: 5",
                 "-H", "Tags: fire,negative_squared_cross_mark",
                 "-d", msg],
                timeout=10,
                capture_output=True,
            )
        except Exception:
            pass  # Don't let alert failure mask the original error

    def audit(self, change_type: str, **kwargs):
        """
        Log a configuration change for audit trail / rollback tracing.

        Examples:
            log.audit("vm.config_change", vmid=100,
                      field="memory", old=2048, new=4096,
                      reason="traffic spike")
            log.audit("firewall.rule_add", rule_id="allow-https",
                      interface="wan", action="pass", dport=443)
            log.audit("storage.add", name="nfs-backup",
                      type="nfs", server="10.0.0.100")
        """
        entry = self._build_entry(change_type, **kwargs)
        self._write("audit", entry)
        return entry

    def start_task(self, task_type: str, **kwargs) -> str:
        """
        Log the start of a long-running task. Returns a task ID for tracking.

        The task ID is a synthetic unique identifier (not the Proxmox UPID).
        Use the UPID from kwargs if you have one.
        """
        task_id = kwargs.get("upid") or f"{task_type}-{int(time.time() * 1000)}"
        entry = self._build_entry(f"{task_type}.started",
                                  task_id=task_id, **kwargs)
        self._write("tasks", entry)
        return task_id

    def end_task(self, task_id: str, status: str = "ok",
                 duration: Optional[float] = None, error: Optional[str] = None,
                 **kwargs):
        """
        Log the completion of a tracked task.

        Args:
            task_id: The task ID from start_task()
            status: "ok", "failed", "cancelled", "timeout"
            duration: Seconds elapsed
            error: Error message if failed
        """
        entry = self._build_entry("task.completed", task_id=task_id,
                                  status=status, duration=duration,
                                  error=error, **kwargs)
        self._write("tasks", entry)
        return entry

    # ── Query helpers ──────────────────────────────────────────────

    def _read_jsonl(self, log_type: str) -> list[dict]:
        """Read all entries from a JSONL log file."""
        path = self.base_dir / self.LOG_FILES[log_type]
        if not path.exists():
            return []
        entries = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # Skip corrupted lines
        return entries

    def get_errors(self, hours: int = 24, limit: int = 100,
                   severity: Optional[str] = None) -> list[dict]:
        """Get recent errors, optionally filtered by severity."""
        import datetime as dt
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
        errors = self._read_jsonl("errors")
        filtered = [
            e for e in errors
            if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff
            and (severity is None or e.get("severity") == severity)
        ]
        return filtered[-limit:]

    def get_events(self, event_prefix: Optional[str] = None,
                   hours: int = 24, limit: int = 200) -> list[dict]:
        """Get recent events, optionally filtered by type prefix."""
        import datetime as dt
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
        events = self._read_jsonl("events")
        filtered = [
            e for e in events
            if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff
            and (event_prefix is None
                 or e["type"].startswith(event_prefix))
        ]
        return filtered[-limit:]

    def get_summary(self, hours: int = 24) -> dict:
        """Get event type frequency summary."""
        events = self._read_jsonl("events")
        errors = self._read_jsonl("errors")
        import datetime as dt
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)

        summary = {
            "period_hours": hours,
            "total_events": 0,
            "total_errors": 0,
            "by_type": {},
            "by_severity": {},
            "tasks_completed": 0,
            "tasks_failed": 0,
        }

        for e in events:
            if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff:
                summary["total_events"] += 1
                t = e["type"]
                summary["by_type"][t] = summary["by_type"].get(t, 0) + 1

        for e in errors:
            if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff:
                summary["total_errors"] += 1
                sev = e.get("severity", "unknown")
                summary["by_severity"][sev] = (
                    summary["by_severity"].get(sev, 0) + 1
                )

        for e in self._read_jsonl("tasks"):
            if (e.get("type") == "task.completed"
                    and dt.datetime.fromisoformat(e["timestamp"]) >= cutoff):
                if e.get("status") == "ok":
                    summary["tasks_completed"] += 1
                else:
                    summary["tasks_failed"] += 1

        return summary

    def tail(self, log_type: str = "events", n: int = 20) -> list[dict]:
        """Get the N most recent entries from a log."""
        entries = self._read_jsonl(log_type)
        return entries[-n:]

    def clear(self, log_type: Optional[str] = None, older_than_days: int = 30):
        """Clear log files. Keep entries newer than older_than_days."""
        import datetime as dt
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(
            days=older_than_days
        )

        types_to_clear = [log_type] if log_type else list(self.LOG_FILES.keys())
        for lt in types_to_clear:
            entries = self._read_jsonl(lt)
            kept = [
                e for e in entries
                if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff
            ]
            path = self.base_dir / self.LOG_FILES[lt]
            with open(path, "w") as f:
                for e in kept:
                    f.write(json.dumps(e, default=str, ensure_ascii=False) + "\n")
```

## Error Handling Patterns

### Pattern 1: Retry with Backoff (API calls)

```python
import time
from proxmox_logging import ProxmoxLogger

log = ProxmoxLogger(node="pve1")

def with_retry(func, max_attempts=3, delay=2.0, backoff=2.0, **kwargs):
    """Retry a Proxmox API call with exponential backoff."""
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func(**kwargs)
        except Exception as e:
            last_exc = e
            status = getattr(e, "status_code",
                             type(e).__name__)
            log.error(
                "api.retry",
                exception=e,
                http_status=getattr(e, "status_code", None),
                attempt=attempt,
                max_attempts=max_attempts,
                function=func.__name__,
            )
            if attempt < max_attempts:
                time.sleep(min(delay * (backoff ** (attempt - 1)), 30))
    raise last_exc

# Usage
try:
    with_retry(
        proxmox.nodes("pve1").qemu(100).status.start.post,
        max_attempts=3,
    )
except Exception as e:
    log.error("vm.start_failed", vmid=100,
              error=f"Failed after 3 retries: {e}")
```

### Pattern 2: VM Operation with Full Context

```python
def start_vm(proxmox, log: ProxmoxLogger, vmid: int):
    """Start a VM with error handling and logging."""
    log.start_task("vm.start", vmid=vmid)

    try:
        # Get VM info for context before operation
        config = proxmox.nodes(log.node).qemu(vmid).config.get()
        log.event("vm.start_initiated", vmid=vmid,
                  name=config.get("name", "unknown"),
                  current_status="stopped")

        # Execute
        result = proxmox.nodes(log.node).qemu(
            vmid
        ).status.start.post()

        log.end_task(f"vm.start-{vmid}", status="ok",
                     upid=result)
        log.event("vm.started", vmid=vmid,
                  name=config.get("name", "unknown"))
        return result

    except Exception as e:
        # Capture surrounding state for debugging
        context = {"vmid": vmid}
        try:
            current = proxmox.nodes(log.node).qemu(
                vmid
            ).status.current.get()
            context["current_status"] = current.get("status")
            context["current_cpu"] = current.get("cpu")
            context["current_mem"] = current.get("mem")
        except Exception:
            context["current_status"] = "unreachable"

        log.end_task(f"vm.start-{vmid}", status="failed",
                     error=str(e))
        log.error("vm.start_failed", exception=e, **context)
        raise
```

### Pattern 3: Snapshot Before Destructive Operation

```bash
#!/bin/bash
# destroy-vm.sh — safe VM destruction with logging

PROXMOX_NODE="pve1"
VMID="$1"
LOG_DIR="$HOME/data/proxmox-logs"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
ALERT_TOPIC="${NTFY_TOPIC:-hermes-alerts}"

mkdir -p "$LOG_DIR"

log_event() {
    local type="$1"; shift
    local extras=""
    for kv in "$@"; do extras+=",\"$kv\""; done
    echo "{\"timestamp\":\"$TIMESTAMP\",\"node\":\"$PROXMOX_NODE\",\"type\":\"$type\"${extras}}" \
        >> "$LOG_DIR/events.jsonl"
}

log_error() {
    local type="$1"; shift
    local extras=""
    for kv in "$#"; do extras+=",\"$kv\""; done
    echo "{\"timestamp\":\"$TIMESTAMP\",\"node\":\"$PROXMOX_NODE\",\"type\":\"$type\",\"severity\":\"error\"${extras}}" \
        >> "$LOG_DIR/errors.jsonl"
}

# Safety check
if [ -z "$VMID" ]; then
    log_error("vm.destroy_rejected", "reason=missing_vmid")
    echo "ERROR: No VMID provided" >&2
    exit 1
fi

# Get VM name for logging
VM_NAME=$(qm config "$VMID" 2>/dev/null | grep "^name:" | cut -d' ' -f2)
if [ -z "$VM_NAME" ]; then
    log_error("vm.destroy_rejected", "vmid=$VMID", "reason=vm_not_found")
    echo "ERROR: VM $VMID not found" >&2
    exit 1
fi

# Snapshot before destruction
log_event("vm.destroy_initiated", "vmid=$VMID", "name=$VM_NAME")
SNAPNAME="pre-destroy-$(date +%Y%m%d-%H%M%S)"

if qm snapshot "$VMID" "$SNAPNAME" --description "Auto snapshot before destroy" 2>/dev/null; then
    log_event("vm.snapshot_created", "vmid=$VMID", "name=$VM_NAME",
              "snapname=$SNAPNAME")
else
    log_error("vm.snapshot_failed", "vmid=$VMID", "name=$VM_NAME")
    echo "WARNING: Snapshot failed, aborting destroy" >&2
    exit 1
fi

# Stop if running
VM_STATUS=$(qm status "$VMID" 2>/dev/null | awk '{print $2}')
if [ "$VM_STATUS" = "running" ]; then
    qm stop "$VMID" >> /dev/null 2>&1
    log_event("vm.stopped_for_destroy", "vmid=$VMID", "name=$VM_NAME")
    sleep 2
fi

# Destroy
if qm destroy "$VMID" --purge >> /dev/null 2>&1; then
    log_event("vm.destroyed", "vmid=$VMID", "name=$VM_NAME",
              "snapname=$SNAPNAME")
    echo "VM $VMID ($VM_NAME) destroyed. Snapshot: $SNAPNAME"
else
    log_error("vm.destroy_failed", "vmid=$VMID", "name=$VM_NAME")
    echo "ERROR: Failed to destroy VM $VMID" >&2
    exit 1
fi
```

### Pattern 4: Task Polling with Timeout

```python
import time
from proxmox_logging import ProxmoxLogger

log = ProxmoxLogger(node="pve1")

def wait_for_task(proxmox, node: str, upid: str,
                  task_type: str, timeout: int = 300,
                  poll_interval: int = 2):
    """
    Poll a Proxmox task until completion.

    Args:
        proxmox: ProxmoxAPI instance
        node: Node name
        upid: Proxmox UPID task ID
        task_type: Human-readable task type for logging
        timeout: Max seconds to wait
        poll_interval: Seconds between polls
    """
    task_id = f"{task_type}-{upid}"
    log.start_task(task_type, upid=upid)
    start = time.time()

    while time.time() - start < timeout:
        try:
            status = proxmox.nodes(node).tasks(
                upid
            ).status.get()
            exitstatus = status.get("exitstatus", "")

            if status.get("status") == "stopped":
                duration = time.time() - start
                if exitstatus == "OK":
                    log.end_task(task_id, status="ok",
                                 duration=duration, upid=upid)
                    log.event(f"{task_type}.completed", upid=upid,
                              duration=duration)
                    return status
                else:
                    log.end_task(task_id, status="failed",
                                 duration=duration, upid=upid,
                                 error=exitstatus)
                    log.error(f"{task_type}.failed", upid=upid,
                              exitstatus=exitstatus,
                              duration=duration)
                    raise RuntimeError(
                        f"Task {upid} failed: {exitstatus}"
                    )
        except Exception as e:
            if "failed" in str(e).lower():
                raise
            log.error(f"{task_type}.poll_error",
                      exception=e, upid=upid)

        time.sleep(poll_interval)

    # Timeout
    log.end_task(task_id, status="timeout",
                 error=f"Exceeded {timeout}s timeout",
                 upid=upid)
    log.error(f"{task_type}.timeout", upid=upid,
              duration=timeout)
    raise TimeoutError(
        f"Task {upid} did not complete within {timeout}s"
    )
```

## Shell CLI Logging (qm/pct wrapper)

For bash scripts using `qm`, `pct`, `pvesm` directly:

```bash
#!/bin/bash
# Add to bash scripts using Proxmox CLI

PVE_LOG="${HOME}/data/proxmox-logs"
mkdir -p "$PVE_LOG"

pve_log() {
    local type="$1"; shift
    local msg="$*"
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
    echo "{\"timestamp\":\"$ts\",\"node\":\"$(hostname)\",\"type\":\"$type\",\"msg\":\"${msg//\"/\\\"}\"}" \
        >> "$PVE_LOG/events.jsonl"
}

pve_error() {
    local type="$1"; shift
    local msg="$*"
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
    echo "{\"timestamp\":\"$ts\",\"node\":\"$(hostname)\",\"type\":\"$type\",\"severity\":\"error\",\"msg\":\"${msg//\"/\\\"}\"}" \
        >> "$PVE_LOG/errors.jsonl"
}

# Helper: run qm command and auto-log
qm_logged() {
    local cmd="qm $*"
    pve_log "qm.exec" "cmd=$cmd"
    output=$(qm "$@" 2>&1)
    rc=$?
    if [ $rc -ne 0 ]; then
        pve_error "qm.failed" "cmd=$cmd" "rc=$rc" "output=$output"
    else
        pve_log "qm.success" "cmd=$cmd"
    fi
    echo "$output"
    return $rc
}

# Usage
qm_logged start 100       # Auto-logged start
qm_logged stop 100        # Auto-logged stop
qm_logged destroy 100     # Auto-logged destroy
```

## Common Error Scenarios & Context Capture

| Scenario | What to Log |
|----------|-------------|
| VM won't start | vmid, config, disk space, recent snapshots, lock status |
| Auth failure | user, realm, token_name, endpoint |
| Network error | target host, port, timeout, retry count |
| Cluster quorum lost | node count, corosync status, expected votes |
| Disk full | storage, used%, affected VMs/LXC |
| Migration fail | vmid, source/dest node, CPU type, shared storage |
| Backup fail | vmid, storage, mode, existing snapshots |
| Task timeout | upid, task type, duration, last known status |
| Lock conflict | vmid, lock type, who holds lock |

## Query Examples

```bash
# Recent errors (last hour)
python3 -c "
from bin.proxmox_logging import ProxmoxLogger
log = ProxmoxLogger()
for e in log.get_errors(hours=1):
    print(f\"{e['timestamp']} [{e.get('severity','?')}] {e['type']}: {e.get('error','')}\")"

# Daily summary
python3 -c "
from bin.proxmox_logging import ProxmoxLogger
import json
log = ProxmoxLogger()
print(json.dumps(log.get_summary(hours=24), indent=2))"

# Events for a specific VM
python3 -c "
from bin.proxmox_logging import ProxmoxLogger
log = ProxmoxLogger()
for e in log.get_events(event_prefix='vm'):
    if e.get('vmid') == 100:
        print(f\"{e['timestamp']} {e['type']}\")"
```

## Log Rotation

Logs grow unbounded. Rotate daily or when files exceed 10MB:

```bash
#!/bin/bash
# ~/bin/proxmox-log-rotate.sh — call from cron daily
LOG_DIR="$HOME/data/proxmox-logs"
MAX_MB=10

for f in "$LOG_DIR"/*.jsonl; do
    size_mb=$(du -m "$f" | cut -f1)
    if [ "$size_mb" -gt "$MAX_MB" ]; then
        # Keep last 1000 lines, compress older entries
        lines=$(wc -l < "$f")
        tail -1000 "$f" > "${f}.tmp"
        mv "${f}.tmp" "$f"
        echo "$(date): Rotated $f (${size_mb}MB, ${lines} lines)"
    fi
done
```

## Cron Integration

```cron
# Log rotation — daily 03:00
0 3 * * * /home/kng/bin/proxmox-log-rotate.sh >> /tmp/proxmox-log-rotate.log 2>&1

# Daily summary report — 08:00
0 8 * * * python3 -c "
from bin.proxmox_logging import ProxmoxLogger
import json, subprocess
log = ProxmoxLogger()
s = log.get_summary(hours=24)
msg = json.dumps(s, indent=2)
subprocess.run(['curl','-s','-X','POST','https://ntfy.sh/hermes-alerts',
    '-H','Title: Proxmox Daily Summary',
    '-H','Priority: 2', '-d', msg], timeout=10)
"
```
