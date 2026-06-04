---
name: security-monitor
description: >
  Comprehensive security monitoring, intrusion detection, and active defense
  for WSL2 + Windows dual-environment. Monitors remote connections (SSH, RDP,
  VNC, WinRM, TeamViewer, AnyDesk), port scans, brute-force attempts, process
  injection, file integrity, and network anomalies. Includes honeytrap decoy
  services, canary tripwire files, automated countermeasures, forensic snapshots,
  and centralized event logging. Alerts via ntfy.sh push notifications.
  Use when: security monitoring, intrusion detection, threat hunting, incident
  response, port scanning detection, brute-force detection, file integrity
  monitoring, honeypot deployment, active defense, countermeasures, WSL security,
  Windows security, network monitoring, process injection detection.
tags: [security, monitoring, intrusion-detection, honeypot, canary, active-defense,
       countermeasures, forensics, ntfy, wsl, windows, incident-response]
---

# Security Monitor — Full-Spectrum IDS/IPS for WSL2 + Windows

Autonomous security monitoring with active defense capabilities across both WSL2 and Windows environments.

## Architecture

```
[Security Monitor]
+-- WSL Side (Ubuntu)                    +-- Windows Side
|   +-- wsl-security-check.sh            |   +-- windows-security-check.ps1
|   +-- honeytrap.py (decoy listeners)   |   +-- Windows Firewall rules
|   +-- canary.py (file integrity)       |   +-- Security Event Log
|   +-- inject-detect.py                 |   +-- PowerShell monitoring
|   +-- net-sandbox.py                   |
|   +-- security-logging.py              |
|   +-- countermeasures.py               |
|                                         |
+-- Central Event Log                     +-- Alerting
|   ~/data/security-monitor/             |   +-- ntfy.sh/hermes-alerts
|   +-- security-events.jsonl            |
|                                         |
+-- Cron Jobs (persistent monitoring)     +-- Forensic Snapshots
    +-- Every 5 min: security check          +-- ~/data/security-monitor/snapshots/
    +-- Every 10 min: inject detect
    +-- Every 15 min: integrity check
    +-- Every 30 min: event collection
    +-- Every 60 min: countermeasures
```

## Quick Start

```bash
# Create baselines for both WSL and Windows
~/bin/wsl-security-check --baseline
~/bin/windows-security-check --baseline

# Initialize canary files and file integrity baseline
~/bin/canary init

# Start honeytrap decoy listeners (use Hermes background=true for daemon)
terminal(background=true, command="~/bin/honeytrap run")

# Verify all systems
~/bin/security-check --report
~/bin/honeytrap status
~/bin/canary status
~/bin/net-sandbox status
```

## Modules

### Module 1: Connection Monitor (wsl-security-check.sh + windows-security-check.ps1)

**WSL checks:** SSH sessions, auth failures, port baselines, suspicious processes, new users, sudo abuse, WSL interop, cron integrity, file integrity, outbound connections.

**Windows checks:** RDP status, VNC/remote tools, WinRM, firewall, port baselines, Security Event Log (4625/4720/4728/4732/7045), scheduled tasks, shares.

### Module 2: Honeytrap (honeytrap.py)

Decoy listeners on ports 2222 (SSH), 5900 (VNC), 4444 (reverse shell), 5555 (ADB), 8081 (HTTP proxy), 9090 (mgmt). Any connection = instant alert with client fingerprinting.

```bash
~/bin/honeytrap start       # Start decoys (daemonizes via fork)
~/bin/honeytrap run         # Run in foreground (use terminal background=true)
~/bin/honeytrap status      # Check status (verify with ss -tlnp for accuracy)
~/bin/honeytrap stop        # Stop all
```

### Module 3: Canary Files (canary.py)

Tripwire hidden files in ~/.ssh/, ~/.config/, ~/.bashrc.canary, /tmp/, /var/tmp/. Integrity baseline of 9 critical files. Real-time inotify watches on /etc, ~/.ssh, /tmp, /usr/bin.

```bash
~/bin/canary init           # Setup canaries + baseline
~/bin/canary check          # One-shot integrity check (triggers IN_ACCESS on baseline files — expected)
~/bin/canary monitor        # Continuous inotify daemon (use terminal background=true)
```

### Module 4: Process Injection Detection (inject-detect.py)

Scans: LD_PRELOAD, ptrace, hidden processes, suspicious .so files, shell backdoors, SSH key changes, SUID changes, /proc/pid/mem access.

```bash
~/bin/inject-detect scan    # One-shot scan (SUID module may take 30s)
~/bin/inject-detect monitor # Continuous (5min interval)
```

### Module 5: Network Sandbox (net-sandbox.py)

Per-IP rate limiting, suspicious port detection, blocklist/allowlist, connection forensics.

```bash
~/bin/net-sandbox monitor   # Continuous monitoring (use terminal background=true)
~/bin/net-sandbox status    # Active connections
~/bin/net-sandbox block --ip 1.2.3.4   # Block an IP (--ip AFTER subcommand)
~/bin/net-sandbox allow --ip 1.2.3.4   # Allow an IP
```

### Module 6: Centralized Logging (security-logging.py)

Aggregates all module events into single JSONL log. Timeline, reports, analysis.

```bash
~/bin/security-logging collect   # Collect from all sources
~/bin/security-logging timeline --hours 6  # Chronological view
~/bin/security-logging report --hours 24   # Formatted report
~/bin/security-logging analyze --hours 24  # JSON analysis
```

### Module 7: Automated Countermeasures (countermeasures.py)

**Always run --dry-run first.** Auto-blocks IPs (auth failures, honeytrap hits, rate limits), kills suspicious processes, forensic snapshots. All actions logged with rollback.

```bash
~/bin/countermeasures dry-run        # Preview (safe)
~/bin/countermeasures auto           # Execute (skips localhost)
~/bin/countermeasures review         # Recent actions
~/bin/countermeasures rollback ID    # Undo an action
~/bin/countermeasures snapshot       # Manual forensic snapshot
```

## Persistent Daemons

Long-running daemons (like `tts-daemon`) should use a PID file pattern:
- Write PID to `/tmp/{name}.pid` on startup
- Check for stale PID before starting (kill if process dead)
- Use `pkill -f {name}` for cleanup
- Never use `&`/`nohup`/`disown` in shell scripts — blocked by Hermes security scanner
- Use `terminal(background=true)` from Hermes instead

## Cron schedule

| Job | Interval |
|-----|----------|
| Full security check (WSL+Windows) | Every 5 min |
| Process injection scan | Every 10 min |
| File integrity check | Every 15 min |
| Event collection | Every 30 min |
| Countermeasures (dry-run + auto) | Every 60 min |
| Daily report | 08:00 |

## WSL2 Kernel Limitations (read before debugging)

| Missing | Impact | Workaround |
|---------|--------|------------|
| CONFIG_AUDIT | No auditd/auditctl | Use inotify (inotify-tools + Python inotify) |
| iptables/nftables | No WSL-side firewall | Use Windows Firewall via powershell.exe |
| AF_PACKET (unprivileged) | No raw sockets for tcpdump | Run tcpdump with sudo, or use Windows-side tools |
| systemd-dbus | Some services unavailable | Use direct service commands |

## WSL2 Security-Monitor Pitfalls (verified in testing)

**Canary inotify self-noise:** `canary check` reads all critical files which triggers `critical_file_change` IN_ACCESS events. During testing this produced 656 events in the central log. This is expected — real tampering shows IN_MODIFY/IN_ATTRIB/IN_CLOSE_WRITE, not IN_ACCESS. Focus alerting on write events, not read events.

**apt/dpkg triggers massive event storms:** Running `apt install` or `apt-get install` while the canary monitor is active generates 500-1000+ events across all three channels: `critical_file_change` (dpkg reads /etc/passwd, /etc/group for user lookups), `canary_accessed` (dpkg traverses /tmp, /home, canary watch dirs), and `new_binary` (dpkg writes .dpkg-new files in /usr/bin). Verified: one `apt install` session produced 842 events in 2 minutes. This is normal package manager activity. Before installing packages, either:
  - Stop the canary monitor: `kill $(cat ~/data/security-monitor/state/honeytrap.pid)` (or just `pkill -f "canary monitor"`)
  - Or accept the flood and re-baseline afterwards: `~/bin/canary init`

**passwd/group hash changes from package installs:** `apt install` often adds system users and groups (e.g., `ntfy`, `tcpdump`, `pulse`, `rtkit`, `rdma`). This changes the MD5 of `/etc/passwd` and `/etc/group`, triggering integrity alerts. This is a **known false positive** — not tampering. After any `apt install`, re-baseline: `~/bin/canary init`

**.dpkg-new binary false positives:** During package installation, dpkg creates temporary `.dpkg-new` files in `/usr/bin/` (e.g., `pulseaudio.dpkg-new`, `pacat.dpkg-new`). Each triggers a `new_binary` alert (26 events per apt session). These are temporary files that dpkg renames to the final name. Not suspicious — ignore or stop the canary monitor during installs.

**Honeytrap localhost exemption:** Test connections from 127.0.0.1 trigger countermeasure block thresholds. The countermeasures module excludes localhost (127.0.0.1, ::1) from blocking by default.

**Honeytrap status may show false INACTIVE:** The status command checks a PID file and reports INACTIVE even when ports are bound. Verify with: `ss -tlnp | grep -E "2222|4444|5555|5900|8081|9090"`

**net-sandbox CLI arg order:** `--ip` is a subcommand option, not positional. Correct: `net-sandbox block --ip 1.2.3.4`. Wrong: `net-sandbox block 1.2.3.4` (argparse error).

**SUID scan is slow:** `find / -perm /6000` takes 30s+ in WSL2. The SUID scanner has a 30s timeout and may not complete. This is cosmetic — other scanners still run.

**grep -c integer safety:** Always use the `tail -1` pattern to avoid multi-line grep -c output breaking numeric comparison.

**PowerShell em-dash:** Never use em-dash (—) in .ps1 string literals written from bash heredocs. It corrupts the PowerShell parser. Use ASCII hyphen (-) instead.

**pip3 on Python 3.14+:** Always pass `--break-system-packages` flag.

**Hermes terminal backgrounding:** Never use `&`, `nohup`, `disown`. Always use `terminal(background=true, command="...")`.

**WSL → Windows Event Log access denied:** `Get-WinEvent` on `Microsoft-Windows-Sysmon/Operational` and `Security` logs throws `UnauthorizedAccessException` when called from WSL via `powershell.exe` or `cmd.exe`. The WSL-spawned PowerShell process inherits a non-elevated token that lacks Event Log Readers membership. Don't attempt to fix from WSL — use one of:
  - Run the script from an elevated Windows PowerShell: `Start-Process powershell -Verb RunAs -ArgumentList "-File C:\path\script.ps1"` (requires interactive logon)
  - Add the Windows user to the `Event Log Readers` group from admin PowerShell: `Add-LocalGroupMember -Group "Event Log Readers" -Member "USERNAME"` then log off/on
  - Use Windows Task Scheduler to run the script at logon with highest privileges

**WSL /tmp invisible to Windows:** `cmd.exe start` and Windows PowerShell cannot access WSL's `/tmp`. Always write scripts to a Windows-accessible path (e.g., `C:\Users\<user>\AppData\Local\Temp\`, or via `/mnt/c/...` from WSL's `write_file`).

**ntfy.sh has no message history:** The free ntfy.sh tier delivers messages in real-time only. You cannot retrieve past alerts via `ntfy subscribe` or the HTTP API. If you need an audit trail, log alerts to a local file (`~/data/security-monitor/alerts.log`) in addition to pushing to ntfy.

**ntfy v2 CLI syntax:** `ntfy hermes-alerts --poll` does NOT work. Use `ntfy subscribe hermes-alerts` instead.

**cmd.exe `start` with paths:** `start "title" powershell -File "C:\path with spaces\script.ps1"` fails — the first quoted string is the window title, and the path gets truncated. Use either: `start "" powershell -File "C:\path\script.ps1"` (empty title), or bypass `start` and call `powershell.exe` directly from WSL.

## Incident Response — Canary Event Analysis

When canary alerts fire, use this timeline reconstruction process:

### Step 1: Correlate with package manager
```bash
# Check if dpkg/apt was active at the alert time
grep "2026-06-02 22:2" /var/log/dpkg.log
# Check auth.log for the window
awk '$0 ~ /Jun 2 22:2[0-9]/' /var/log/auth.log
```

### Step 2: Identify event patterns
```bash
# Categorize events by type and count
cat ~/data/security-monitor/canary/events.jsonl | python3 -c "
import json, sys
events = [json.loads(l) for l in sys.stdin]
types = {}
for e in events:
    t = e.get('type','')
    types[t] = types.get(t, 0) + 1
for t, c in sorted(types.items(), key=lambda x: -x[1]):
    print(f'{c:4d}  {t}')
"
```

### Step 3: Check for self-inflicted causes (in order)
1. Was `apt install` or `apt-get install` running? → 500-1000 event flood, all FP
2. Was `canary check` or `canary init` run? → IN_ACCESS on all critical files, FP
3. Did WSL just boot? → systemd creates users/groups, changes passwd/group hashes
4. Did the security-monitor skill setup scripts run? → Hermes agent reads files during installation
5. Any cron jobs firing? → Check `cronjob list` for scheduled security scans reading files

### Step 4: Confirm or escalate
- If all events are IN_ACCESS (reads) with no IN_MODIFY/IN_ATTRIB/IN_CLOSE_WRITE → likely self-inflicted
- If events include `new_binary` in /usr/bin with `.dpkg-new` suffix → package install, FP
- If passwd/group hash changed but mode/owner intact → likely useradd/groupadd from package install
- If events are concentrated in a <5 second burst across many files → automated scan (AV or script), not interactive attacker

### Step 5: Re-baseline if clean
```bash
~/bin/canary init
```

## TTS Voice Alerts (Optional Enhancement)

Security alerts can be spoken aloud using the Qwen3-TTS dynamic voice system:

```bash
# Alert with voice matching severity
~/bin/tts-speak "Warning. Port scan detected from 192.168.1.100." --mood alert

# Critical alert
~/bin/tts-speak "Critical. Honeytrap triggered. Unauthorized access attempt." --mood urgent
```

The TTS system auto-detects mood from alert text using keyword matching. Severity keywords map to appropriate voice profiles (critical→urgent voice, warning→alert voice, etc.).

## Log Locations

```
~/data/security-monitor/
+-- security-events.jsonl     # Central event log
+-- honeytrap/events.jsonl    # Honeytrap events (JSONL)
+-- honeytrap/honeytrap.log   # Honeytrap operational log
+-- canary/events.jsonl       # Canary inotify events (JSONL)
+-- canary/canary.log         # Canary operational log
+-- canary/baseline.json      # File integrity baseline (MD5 hashes)
+-- injection/events.jsonl    # Injection detection events
+-- injection/inject-detect.log
+-- network/events.jsonl      # Network events
+-- network/connections.jsonl # Full connection forensics log
+-- network/blocklist.json    # Blocked IPs
+-- network/allowlist.json    # Allowed IPs
+-- countermeasures.jsonl     # Countermeasure audit trail (for rollback)
+-- countermeasures.log
+-- quarantine/               # Quarantined files
+-- snapshots/                # Forensic snapshots
+-- reports/                  # Generated daily reports
```

## WSL2 Kernel Limitations (IMPORTANT)

The WSL2 kernel lacks several subsystems that standard Linux security tools depend on:

| Feature | Status | Workaround |
|---------|--------|------------|
| **auditd** | NOT supported | Use `inotify-tools` for file monitoring |
| **iptables/nftables** | NOT available | Use Windows Firewall via `powershell.exe` |
| **AF_PACKET** | Needs root | Avoid raw socket approaches |
| **ptrace_scope** | Read-only (value=1) | Detection-only for ptrace |

**DO NOT attempt**: `auditd`, `iptables`, `nftables`, `fail2ban` — WSL2 kernel lacks these.

## Canary File Noise

The inotify watches on `/etc` directories generate high event volume from normal system activity (MD5 reads during baseline checks, systemd reads on `/etc/hosts`, etc.). This is expected — filter by `canary_accessed` event type for genuine tripwire alerts. The `critical_file_change` events on `/etc/passwd`, `/etc/group`, `/etc/sudoers` from baseline integrity checks are also normal.

## WSL-Specific Notes

- Windows checks run via `powershell.exe` from WSL
- Windows Firewall is used for IP blocking (WSL has no iptables)
- Security Event Log requires Administrator privileges for full audit log access
- Windows baselines stored at `C:\Users\<user>\.security-monitor\baselines\`
- WinRM is RUNNING by default — disable if not needed:
  ```powershell
  Stop-Service WinRM; Set-Service WinRM -StartupType Disabled
  ```
- RDP is DISABLED by default (fDenyTSConnections=1) — keep it that way

## Performance Notes

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Full WSL check | 5-10s | Excluding SUID scan |
| SUID binary scan | 30-60s | `find / -perm /6000`; consider limiting scope |
| Windows check | 5-15s | PowerShell startup overhead |
| Honeytrap hit-to-alert | <1s | Direct ntfy push |
| Canary check | 2-5s | MD5 of 9 files + canary verification |
| Injection scan | 30-60s | SUID scan is bottleneck |

## Known False Positives

- **WSL Interop warning**: Always reported; informational only
- **Unusual root processes**: plan9, chronyd, networkd-dispatcher, cups, agetty, unattended-upgrades are normal in WSL2
- **Firewall DefaultInboundAction**: May show "NotConfigured" on fresh Windows installs — normal
- **Canary inotify noise**: Running `canary check` triggers IN_ACCESS on all watched files (MD5 reads). Expected.
- **apt/dpkg event flood**: Package installations generate 500-1000+ canary events (see Pitfalls below). Stop canary monitor before apt operations, or re-baseline after.
- **passwd/group hash changes after apt**: System users/groups added by packages change MD5 hashes. Re-baseline with `~/bin/canary init` after any install.
- **Canary parent-dir reads**: Legitimate processes reading files in watched parent directories (/home/kng, /tmp, /var/tmp, /etc) trigger IN_ACCESS on canary files. This is inotify working as designed — the canary files are *in* those directories, not the targets themselves. Normal file operations in these dirs are not suspicious.

## Overlap Note

This skill supersedes `system-notifications-monitoring` for security-specific alerting.
Keep `system-notifications-monitoring` for general health (disk, memory, CPU, weather, Docker).
Both can coexist — different ntfy topics and different scripts.

## References

- `references/wsl2-compatibility.md` — WSL2 kernel limitations, tool compatibility matrix, performance benchmarks
- `references/port-reference.md` — Honeytrap ports, C2/suspicious ports, Windows Security Event IDs
- `references/event-id-reference.md` — Detailed Windows Security Event ID reference
- `references/canary-event-analysis.md` — Forensic playbook: investigating canary alerts, self-inflicted vs real intrusion indicators, apt/dpkg false positive patterns
- `references/sysmon-realtime-monitor.md` — Sysmon real-time Event Log monitor: deployment from WSL, access requirements, launch options, output format

---

*Skill created 2026-06-02. Tested end-to-end on WSL2 Ubuntu 24.04 + Windows 11, RTX 4060.*