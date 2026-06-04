---
name: opnsense-logging
description: >
  Error handling, structured logging, and event tracking for OPNsense firewall
  automation. Covers the REST API (firewall, NAT, IDS, DNS, VPN, system) and
  CLI (pfctl, configctl, pluginctl). Use when: writing OPNsense automation
  scripts, debugging firewall API failures, adding logging to rule changes,
  tracking Suricata alerts, managing WireGuard tunnels, audit trails for
  firewall configuration changes.
tags: [opnsense, logging, error-handling, events, firewall, ids, automation]
---

# OPNsense Logging — Error Handling & Structured Event Tracking

Robust error handling and structured logging for OPNsense firewall automation
scripts (REST API and shell CLI wrappers).

## Architecture

```
[Automation Script]
    |
    +-- OPNsenseLogger (structured JSONL log)
    |     ~/data/opnsense-logs/
    |     +-- events.jsonl        # All operations (rules, NAT, VPN, DNS, IDS)
    |     +-- errors.jsonl        # Error-only subset with full context
    |     +-- ids-alerts.jsonl    # Suricata IDS/IPS alerts
    |     +-- audit.jsonl         # Config changes for rollback tracing
    |     +-- dns.jsonl           # DNS query/override logging (optional)
    |     +-- vpn.jsonl           # VPN tunnel up/down events
    |
    +-- Error Handler
    |     +-- Retry with jitter
    |     +-- Connection health checks
    |     +-- Config validation before apply
    |     +-- Alert escalation (ntfy.sh integration)
    |
    +-- Event Categories
          +-- firewall.*    (rule_add, rule_delete, rule_modify, apply, block, pass)
          +-- nat.*         (port_forward, outbound, 1-to-1)
          +-- ids.*         (alert, rule_reload, status_change, threshold)
          +-- dns.*         (override, reconfigure, query)
          +-- vpn.*         (tunnel_up, tunnel_down, peer_add, handshake)
          +-- system.*      (reboot, firmware_update, backup, restore)
          +-- auth.*        (login, session, api_key)
          +-- interface.*   (up, down, ip_change, vlan)
```

## Quick Start

```python
from opnsense_logging import OPNsenseLogger

log = OPNsenseLogger(
    base_dir="~/data/opnsense-logs",
    host="opnsense.local",
)

# Firewall events
log.event("firewall.rule_add", rule_id="allow-https",
          interface="wan", dest="10.0.1.10", port=443,
          protocol="TCP", action="pass")

log.event("firewall.apply", rules_count=1, interface="wan")

# IDS alerts
log.ids_alert(timestamp="2026-06-03T12:00:00Z",
              severity="high",
              signature="ET SCAN Nmap Scripting Engine",
              src_ip="198.51.100.42", dst_ip="10.0.1.1",
              src_port=12345, dst_port=22,
              protocol="TCP", action="allowed",
              sid=2010937)

# VPN events
log.vpn_event("wireguard.peer_connected",
              peer_name="laptop",
              peer_pubkey="abcdef...",
              tunnel_ip="10.100.0.2",
              remote_endpoint="203.0.113.50:51820")

# Error with context
try:
    fw.add_rule("Block malicious", "192.0.2.100", "any")
except Exception as e:
    log.error("firewall.rule_add_failed",
              exception=e, rule="Block malicious")

# Audit trail
log.audit("firewall.rule_change",
          rule_id="allow-https",
          field="destination",
          old="10.0.1.10", new="10.0.1.20",
          reason="server migration")

# Get summaries
summary = log.get_summary(hours=24)
errors = log.get_errors(hours=1, severity="critical")
ids_stats = log.get_ids_summary(hours=24)
```

## Python Module — opnsense_logging.py

Save to `~/bin/opnsense_logging.py`:

```python
#!/usr/bin/env python3
"""
OPNsenseLogger — structured JSONL logging for OPNsense firewall automation.

Usage:
    from opnsense_logging import OPNsenseLogger

    log = OPNsenseLogger(base_dir="~/data/opnsense-logs", host="opnsense.local")

    log.event("firewall.rule_add", rule_id="allow-https", port=443)
    log.error("firewall.rule_add_failed", exception=e)
    log.ids_alert(timestamp=..., signature="...", src_ip="...", ...)
    log.audit("firewall.rule_change", rule_id="allow-https", ...)
"""

import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class OPNsenseLogger:
    """Structured JSONL logger for OPNsense firewall operations."""

    LOG_FILES = {
        "events": "events.jsonl",
        "errors": "errors.jsonl",
        "ids_alerts": "ids-alerts.jsonl",
        "audit": "audit.jsonl",
        "dns": "dns.jsonl",
        "vpn": "vpn.jsonl",
    }

    # HTTP status classifications
    ERROR_CATEGORIES = {
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
        "ConnectionError": "connection_failure",
        "TimeoutError": "timeout",
        "SSLError": "ssl_error",
        "JSONDecodeError": "malformed_response",
    }

    # Signature severity keywords (Suricata rule matching)
    SEVERITY_PATTERNS = {
        "critical": ["MALWARE", "EXPLOIT", "C2", "BACKDOOR", "RANSOMWARE",
                     "TROJAN"],
        "high": ["SCAN", "BRUTE", "ATTACK", "SHELLCODE", "DOS",
                 "POLICY VIOLATION"],
        "medium": ["SUSPICIOUS", "ANOMAL", "POLICY", "SPAM"],
        "low": ["INFO", "NOTICE", "DNS", "HTTP"],
    }

    def __init__(self, base_dir: str = "~/data/opnsense-logs",
                 host: str = "opnsense.local",
                 alert_topic: Optional[str] = None):
        self.base_dir = Path(base_dir).expanduser()
        self.host = host
        self.alert_topic = alert_topic
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        for name in self.LOG_FILES:
            path = self.base_dir / self.LOG_FILES[name]
            if not path.exists():
                path.touch()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def _write(self, log_type: str, entry: dict):
        path = self.base_dir / self.LOG_FILES[log_type]
        with open(path, "a") as f:
            f.write(json.dumps(entry, default=str, ensure_ascii=False) + "\n")

    def _build_entry(self, event_type: str, **kwargs) -> dict:
        return {
            "timestamp": self._now(),
            "host": self.host,
            "type": event_type,
            **kwargs,
        }

    # ── Event Logging ────────────────────────────────────────────

    def event(self, event_type: str, **kwargs):
        """
        Log a normal operation event.

        Examples:
            log.event("firewall.rule_add", rule_id="allow-https",
                      interface="wan", dest="10.0.1.10", port=443)
            log.event("nat.port_forward_added", ext_port=443,
                      int_ip="10.0.1.10", int_port=443)
            log.event("vpn.wireguard.peer_connected",
                      peer_name="laptop", tunnel_ip="10.100.0.2")
            log.event("ids.rule_reload", rules_loaded=28473)
            log.event("dns.override_added", hostname="nas",
                      domain="home.local", ip="10.0.1.5")
        """
        entry = self._build_entry(event_type, **kwargs)
        self._write("events", entry)
        return entry

    def ids_alert(self, signature: str, src_ip: str, dst_ip: str,
                  src_port: int, dst_port: int,
                  protocol: str = "TCP", action: str = "allowed",
                  timestamp: Optional[str] = None,
                  sid: Optional[int] = None, gid: Optional[int] = None,
                  rev: Optional[int] = None, category: Optional[str] = None,
                  **kwargs):
        """
        Log a Suricata IDS/IPS alert from eve.json.

        Args:
            signature: The rule signature text
            src_ip/dst_ip: Source and destination IPs
            src_port/dst_port: Ports
            protocol: TCP/UDP/ICMP/etc
            action: "allowed", "blocked", "rejected"
            timestamp: Event ISO timestamp (from Suricata)
            sid/gid/rev: Rule identifiers
            category: Rule category
        """
        entry = self._build_entry(
            "ids.alert",
            signature=signature,
            src_ip=src_ip, dst_ip=dst_ip,
            src_port=src_port, dst_port=dst_port,
            protocol=protocol, action=action,
            sid=sid, gid=gid, rev=rev, category=category,
            event_timestamp=timestamp,
            **kwargs,
        )
        # Auto-classify severity from signature
        entry["severity"] = self._classify_ids_severity(signature)
        self._write("ids_alerts", entry)

        # Alert on critical/high severity
        if entry["severity"] in ("critical", "high") and self.alert_topic:
            self._send_alert(entry, prefix="IDS Alert")

        return entry

    def _classify_ids_severity(self, signature: str) -> str:
        """Classify Suricata alert severity from signature text."""
        sig_upper = signature.upper()
        for severity, patterns in self.SEVERITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in sig_upper:
                    return severity
        return "info"

    def vpn_event(self, event_type: str, **kwargs):
        """Log a VPN-related event."""
        entry = self._build_entry(f"vpn.{event_type}", **kwargs)
        self._write("vpn", entry)
        # Also write to events for unified timeline
        self._write("events", entry)
        return entry

    def audit(self, change_type: str, **kwargs):
        """
        Log a configuration change for audit trail.

        Examples:
            log.audit("firewall.rule_change",
                      rule_id="allow-https", field="destination",
                      old="10.0.1.10", new="10.0.1.20",
                      reason="server migration")
            log.audit("nat.forward_removed", rule_id="pf-http",
                      target="10.0.1.10", port=80,
                      reason="decommissioned service")
            log.audit("system.config_backup",
                      reason="pre-change backup")
        """
        entry = self._build_entry(change_type, **kwargs)
        self._write("audit", entry)
        return entry

    def error(self, error_type: str,
              exception: Optional[Exception] = None,
              http_status: Optional[int] = None,
              **kwargs):
        """
        Log an error with full context.

        Args:
            error_type: Error classification
            exception: Caught exception object
            http_status: HTTP status code if from API call
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
        elif exception:
            entry["category"] = self.ERROR_CATEGORIES.get(
                type(exception).__name__, "unknown"
            )
        else:
            entry["category"] = "unknown"

        entry["severity"] = self._classify_severity(entry)
        self._write("errors", entry)

        if entry["severity"] == "critical" and self.alert_topic:
            self._send_alert(entry)

        return entry

    def _classify_severity(self, entry: dict) -> str:
        category = entry.get("category", "")
        if category in {"internal_error", "service_unavailable",
                        "disk_full", "quota_exceeded"}:
            return "critical"
        if category in {"connection_failure", "timeout", "bad_gateway",
                        "gateway_timeout", "ssl_error"}:
            return "warning"
        if category in {"auth_failure", "permission_denied"}:
            return "warning"
        if category in {"not_found", "validation_error",
                        "bad_request", "malformed_response"}:
            return "error"
        return "error"

    def _send_alert(self, entry: dict, prefix: str = "OPNsense Error"):
        """Send alert via ntfy.sh."""
        import subprocess
        title = f"{prefix} — {entry.get('type', 'unknown')}"
        # Build message from entry fields
        skip_fields = {"timestamp", "traceback", "node", "host",
                       "severity", "type", "category"}
        parts = [f"Host: {self.host}"]
        for k, v in sorted(entry.items()):
            if k not in skip_fields and v is not None:
                parts.append(f"{k}: {v}")
        msg = "\n".join(parts)
        try:
            subprocess.run(
                ["curl", "-s", "-X", "POST", f"https://ntfy.sh/{self.alert_topic}",
                 "-H", f"Title: {title}",
                 "-H", "Priority: 5",
                 "-H", "Tags: fire,shield",
                 "-d", msg],
                timeout=10, capture_output=True,
            )
        except Exception:
            pass

    # ── Query helpers ────────────────────────────────────────────

    def _read_jsonl(self, log_type: str) -> list[dict]:
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
                        continue
        return entries

    def get_errors(self, hours: int = 24, limit: int = 100,
                   severity: Optional[str] = None) -> list[dict]:
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

    def get_ids_alerts(self, hours: int = 24, limit: int = 500,
                       severity: Optional[str] = None,
                       src_ip: Optional[str] = None) -> list[dict]:
        import datetime as dt
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
        alerts = self._read_jsonl("ids_alerts")
        filtered = []
        for a in alerts:
            ts = a.get("timestamp") or a.get("event_timestamp", "")
            if ts and dt.datetime.fromisoformat(ts) >= cutoff:
                if severity and a.get("severity") != severity:
                    continue
                if src_ip and a.get("src_ip") != src_ip:
                    continue
                filtered.append(a)
        return filtered[-limit:]

    def get_summary(self, hours: int = 24) -> dict:
        """Get event type frequency summary."""
        import datetime as dt
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)

        summary = {
            "period_hours": hours,
            "total_events": 0,
            "total_errors": 0,
            "total_ids_alerts": 0,
            "by_type": {},
            "by_severity": {},
            "ids_by_severity": {},
            "ids_top_attackers": {},
            "vpn_events": 0,
        }

        for e in self._read_jsonl("events"):
            if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff:
                summary["total_events"] += 1
                t = e["type"]
                summary["by_type"][t] = summary["by_type"].get(t, 0) + 1

        for e in self._read_jsonl("errors"):
            if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff:
                summary["total_errors"] += 1
                sev = e.get("severity", "unknown")
                summary["by_severity"][sev] = (
                    summary["by_severity"].get(sev, 0) + 1
                )

        for a in self._read_jsonl("ids_alerts"):
            ts = a.get("timestamp") or a.get("event_timestamp", "")
            if ts and dt.datetime.fromisoformat(ts) >= cutoff:
                summary["total_ids_alerts"] += 1
                sev = a.get("severity", "unknown")
                summary["ids_by_severity"][sev] = (
                    summary["ids_by_severity"].get(sev, 0) + 1
                )
                # Track top attacker IPs
                src = a.get("src_ip", "unknown")
                summary["ids_top_attackers"][src] = (
                    summary["ids_top_attackers"].get(src, 0) + 1
                )

        # Sort top attackers
        summary["ids_top_attackers"] = dict(
            sorted(summary["ids_top_attackers"].items(),
                   key=lambda x: -x[1])[:10]
        )

        summary["vpn_events"] = len([
            e for e in self._read_jsonl("vpn")
            if dt.datetime.fromisoformat(e["timestamp"]) >= cutoff
        ])

        return summary

    def tail(self, log_type: str = "events", n: int = 20) -> list[dict]:
        entries = self._read_jsonl(log_type)
        return entries[-n:]

    def clear(self, log_type: Optional[str] = None,
              older_than_days: int = 30):
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

### Pattern 1: API Call with Retry + Health Check

```python
import time
import requests
from opnsense_logging import OPNsenseLogger

log = OPNsenseLogger(host="opnsense.local")

def api_call_with_retry(self, method: str, path: str,
                        max_attempts=3, base_delay=2.0,
                        **kwargs):
    """
    Make an OPNsense API call with retry and logging.
    `self` is the OPNsense client instance.
    """
    url = f"{self.base_url}{path}"
    last_exc = None

    for attempt in range(1, max_attempts + 1):
        try:
            log.event("api.request", method=method, path=path,
                      attempt=attempt)

            if method == "GET":
                resp = requests.get(url, headers=self.headers,
                                    verify=self.verify, timeout=30)
            else:
                resp = requests.post(url, headers=self.headers,
                                     json=kwargs.get("data"),
                                     verify=self.verify, timeout=30)

            if resp.status_code == 200:
                log.event("api.success", method=method, path=path,
                          attempt=attempt)
                return resp.json()

            # Handle specific status codes
            if resp.status_code == 401:
                log.error("api.auth_failure",
                          http_status=401,
                          path=method, method=path)
                raise PermissionError(f"Auth failed for {path}")

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 10))
                log.error("api.rate_limited",
                          http_status=429,
                          retry_after=retry_after,
                          path=path)
                time.sleep(retry_after)
                continue

            # Other HTTP errors
            log.error("api.http_error",
                      http_status=resp.status_code,
                      path=path,
                      response_body=resp.text[:500])
            resp.raise_for_status()

        except (requests.ConnectionError, requests.Timeout) as e:
            last_exc = e
            log.error("api.connection_error",
                      exception=e, path=path, attempt=attempt)
            delay = min(base_delay * (2 ** (attempt - 1)), 30)
            jitter = delay * 0.2 * (hash(f"{path}{attempt}") % 10 - 5) / 5
            time.sleep(delay + jitter)
            continue

    # All retries exhausted
    log.error("api.all_retries_failed",
              path=path, max_attempts=max_attempts,
              error=str(last_exc))
    raise last_exc
```

### Pattern 2: Firewall Rule Change with Validation + Audit

```python
from opnsense_logging import OPNsenseLogger
import requests, json

log = OPNsenseLogger(host="opnsense.local", alert_topic="hermes-alerts")

class FirewallManager:
    def __init__(self, host, api_key, api_secret, verify_ssl=False):
        self.log = log
        self.base_url = f"https://{host}"
        import base64
        auth = base64.b64encode(
            f"{api_key}:{api_secret}".encode()
        ).decode()
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        }
        self.verify = verify_ssl

    def add_rule_safe(self, description, dest, port,
                      protocol="TCP", action="pass",
                      interface=None, validate=True):
        """Add a firewall rule with validation, logging, and audit trail."""

        log.audit("firewall.rule_add_initiated",
                  description=description, dest=dest,
                  port=port, protocol=protocol, action=action)

        # 1. Validate: don't add duplicate rules
        if validate:
            existing = self._get(f"/api/firewall/filter/getRule/{{}}")
            if existing and isinstance(existing, dict):
                for uuid, rule in existing.get("rule", {}).items():
                    if (rule.get("destination_net") == dest
                            and rule.get("destination_port") == str(port)
                            and rule.get("protocol", "TCP")
                                .upper() == protocol.upper()):
                        log.error("firewall.duplicate_rule",
                                  dest=dest, port=port,
                                  protocol=protocol,
                                  existing_uuid=uuid)
                        raise ValueError(
                            f"Duplicate rule exists: {dest}:{port}"
                        )

        # 2. Add the rule
        rule_data = {
            "rule": {
                "description": description,
                "source_net": "any",
                "destination_net": dest,
                "destination_port": str(port),
                "protocol": protocol,
                "action": action,
                "enabled": "1",
            }
        }
        if interface:
            rule_data["rule"]["interface"] = interface

        try:
            result = self._post(
                "/api/firewall/filter/addRule/{}",
                data=rule_data,
            )
            rule_uuid = result.get("uuid", "unknown")

            log.event("firewall.rule_add",
                      rule_id=rule_uuid,
                      description=description,
                      dest=dest, port=port,
                      protocol=protocol, action=action,
                      interface=interface)

        except Exception as e:
            log.error("firewall.rule_add_failed",
                      exception=e,
                      description=description,
                      dest=dest, port=port)
            raise

        # 3. Apply rules
        try:
            self._post("/api/firewall/filter/apply")
            log.event("firewall.apply",
                      rule_uuid=rule_uuid, rules_count=1)
        except Exception as e:
            log.error("firewall.apply_failed",
                      exception=e,
                      rule_uuid=rule_uuid)
            # Rule exists but not applied — critical state
            raise

        # 4. Verify (read back)
        try:
            verify = self._get("/api/firewall/filter/getRule/{}")
            log.event("firewall.rule_verified",
                      rule_id=rule_uuid)
        except Exception as e:
            log.error("firewall.rule_verify_failed",
                      exception=e, rule_uuid=rule_uuid)

        return rule_uuid

    def _get(self, path):
        resp = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers, verify=self.verify, timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path, data=None):
        resp = requests.post(
            f"{self.base_url}{path}",
            headers=self.headers, json=data or {},
            verify=self.verify, timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # Bulk operations
    def add_rules_batch(self, rules: list[dict]):
        """Add multiple rules, log each, rollback on any failure."""
        added = []
        log.event("firewall.batch_initiated", count=len(rules))

        for rule in rules:
            try:
                uuid = self.add_rule_safe(validate=False, **rule)
                added.append(uuid)
            except Exception as e:
                log.error("firewall.batch_failed",
                          exception=e,
                          rule=rule,
                          completed=len(added),
                          total=len(rules))
                # Rollback: remove successfully added rules
                for uuid in added:
                    try:
                        self._post(
                            f"/api/firewall/filter/delRule/{uuid}"
                        )
                        log.audit("firewall.rollback",
                                  rule_uuid=uuid,
                                  reason="batch failure")
                    except Exception:
                        pass
                raise

        # Apply all at once
        self._post("/api/firewall/filter/apply")
        log.event("firewall.batch_completed",
                  count=len(added))
        return added
```

### Pattern 3: IDS Alert Processing (from Suricata eve.json)

```python
import json, subprocess
from opnsense_logging import OPNsenseLogger

log = OPNsenseLogger(host="opnsense.local",
                     alert_topic="hermes-alerts")

def process_ids_alerts(eve_json_path: str = "/var/log/suricata/eve.json",
                       tail_lines: int = 100):
    """
    Read recent Suricata alerts from eve.json and log them.
    Run via cron every few minutes.
    """
    try:
        # Read last N lines
        result = subprocess.run(
            ["tail", "-n", str(tail_lines), eve_json_path],
            capture_output=True, text=True, timeout=10,
        )
        alerts_processed = 0

        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Only process alert events
            if event.get("event_type") != "alert":
                continue

            alert = event.get("alert", {})
            log.ids_alert(
                timestamp=event.get("timestamp", ""),
                signature=alert.get("signature", "Unknown"),
                category=alert.get("category", ""),
                severity_num=alert.get("severity", 3),
                action=event.get("dest_ip", "N/A")  # fallback
                              and "blocked" or "allowed",
                src_ip=event.get("src_ip", "unknown"),
                dst_ip=event.get("dest_ip", "unknown"),
                src_port=event.get("src_port", 0),
                dst_port=event.get("dest_port", 0),
                protocol=event.get("proto", "TCP"),
                sid=alert.get("signature_id"),
                gid=alert.get("generator_id"),
                rev=alert.get("rev"),
            )
            alerts_processed += 1

        log.event("ids.processing_complete",
                  alerts_processed=alerts_processed)
        return alerts_processed

    except Exception as e:
        log.error("ids.processing_failed",
                  exception=e,
                  source=eve_json_path)
        raise
```

### Pattern 4: Shell CLI Logging (pfctl/configctl wrapper)

```bash
#!/bin/bash
# Add to bash scripts using OPNsense CLI (via SSH or shell)

OPN_LOG="${HOME}/data/opnsense-logs"
mkdir -p "$OPN_LOG"

opn_log() {
    local type="$1"; shift
    local msg="$*"
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
    echo "{\"timestamp\":\"$ts\",\"host\":\"$(hostname)\",\"type\":\"$type\",\"msg\":\"${msg//\"/\\\"}\"}" \
        >> "$OPN_LOG/events.jsonl"
}

opn_error() {
    local type="$1"; shift
    local msg="$*"
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
    echo "{\"timestamp\":\"$ts\",\"host\":\"$(hostname)\",\"type\":\"$type\",\"severity\":\"error\",\"msg\":\"${msg//\"/\\\"}\"}" \
        >> "$OPN_LOG/errors.jsonl"
}

# Helper: run configctl and auto-log
configctl_logged() {
    local service="$1"; shift
    local action="$*"
    opn_log "configctl.exec" "service=$service action=$action"

    output=$(configctl "$service" "$action" 2>&1)
    rc=$?

    if [ $rc -ne 0 ]; then
        opn_error "configctl.failed" \
            "service=$service" "action=$action" \
            "rc=$rc" "output=$output"
    else
        opn_log "configctl.success" "service=$service action=$action"
    fi
    echo "$output"
    return $rc
}

# Usage
configctl_logged firewall filter reload     # Reload rules, auto-logged
configctl_logged unbound dnsbl             # DNSBL check, auto-logged
configctl_logged ids reload                # Reload IDS, auto-logged
```

## Common Error Scenarios & Context

| Scenario | What to Log |
|----------|-------------|
| API 401 | api_key, user, endpoint, timestamp |
| API 403 | action attempted, required privilege |
| Rule conflict | existing rule UUID, conflicting params |
| Rules not applying | interface, pfctl output, configctl return |
| Suricata not starting | interface assignment, rule count, disk space |
| WireGuard tunnel down | peer, pubkey, tunnel IP, last handshake |
| DNS not resolving | hostname, upstream, Unbound status |
| Config corrupt | backup being restored, timestamp |
| Firmware update fail | current/target version, available disk space |
| Reboot triggered | reason, initiator, services affected |

## Query Examples

```bash
# Recent errors
python3 -c "
from bin.opnsense_logging import OPNsenseLogger
log = OPNsenseLogger()
for e in log.get_errors(hours=1):
    print(f\"{e['timestamp']} [{e.get('severity','?')}] {e['type']}: {e.get('error','')}\")"

# IDS critical alerts
python3 -c "
from bin.opnsense_logging import OPNsenseLogger
log = OPNsenseLogger()
for a in log.get_ids_alerts(hours=1, severity='critical'):
    print(f\"{a['signature']} — {a['src_ip']}:{a['src_port']} -> {a['dst_ip']}:{a['dst_port']}\")"

# Daily summary
python3 -c "
from bin.opnsense_logging import OPNsenseLogger
import json
log = OPNsenseLogger()
print(json.dumps(log.get_summary(hours=24), indent=2))"

# Top attacker IPs
python3 -c "
from bin.opnsense_logging import OPNsenseLogger
log = OPNsenseLogger()
s = log.get_summary(hours=24)
print('Top attacker IPs:')
for ip, count in s['ids_top_attackers'].items():
    print(f'  {ip}: {count} alerts')"

# VPN events
python3 -c "
from bin.opnsense_logging import OPNsenseLogger
log = OPNsenseLogger()
for e in log.get_events(event_prefix='vpn', hours=24):
    print(f\"{e['timestamp']} {e['type']}\")"

# Config audit trail
python3 -c "
from bin.opnsense_logging import OPNsenseLogger
log = OPNsenseLogger()
for e in log._read_jsonl('audit'):
    print(f\"{e['timestamp']} {e['type']}: {e}\")"
```

## Log Rotation

```bash
#!/bin/bash
# ~/bin/opnsense-log-rotate.sh — call from cron daily
LOG_DIR="$HOME/data/opnsense-logs"
MAX_MB=10

for f in "$LOG_DIR"/*.jsonl; do
    size_mb=$(du -m "$f" | cut -f1)
    if [ "$size_mb" -gt "$MAX_MB" ]; then
        lines=$(wc -l < "$f")
        tail -1000 "$f" > "${f}.tmp"
        mv "${f}.tmp" "$f"
        echo "$(date): Rotated $f (${size_mb}MB, ${lines} lines)"
    fi
done
```

## Cron Integration

```cron
# IDS alert processing — every 5 minutes
*/5 * * * * python3 /home/kng/bin/process_ids_alerts.py >> /tmp/opnsense-ids.log 2>&1

# Log rotation — daily 03:30
30 3 * * * /home/kng/bin/opnsense-log-rotate.sh >> /tmp/opnsense-log-rotate.log 2>&1

# Daily summary — 08:00
0 8 * * * python3 -c "
from bin.opnsense_logging import OPNsenseLogger
import json, subprocess
log = OPNsenseLogger(alert_topic='hermes-alerts')
s = log.get_summary(hours=24)
msg = json.dumps(s, indent=2)
subprocess.run(['curl','-s','-X','POST','https://ntfy.sh/hermes-alerts',
    '-H','Title: OPNsense Daily Summary',
    '-H','Priority: 2', '-d', msg], timeout=10)
"

# Firewall rule audit (daily config backup + diff)
0 4 * * * python3 -c "
from bin.opnsense_logging import OPNsenseLogger
log = OPNsenseLogger()
log.audit('system.config_backup', reason='daily automated backup')
" && curl -s -u 'api-key:api-secret' \
    'https://opnsense.local/api/core/backup/download/this' \
    -o ~/backups/opnsense-$(date +%Y%m%d).xml
```
