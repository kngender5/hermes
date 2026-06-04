# Sysmon Real-Time Monitor — Windows Event Log Reference

## Overview

Real-time Sysmon + Security log monitor with periodic commentary output.
Designed to run in a background PowerShell process.

## Event Coverage

| Source | Event IDs | Detection |
|--------|-----------|-----------|
| Sysmon 1 | Process creation | LOLBins, encoded commands, suspicious parents |
| Sysmon 3 | Network connections | Non-browser processes making web connections |
| Sysmon 22 | DNS queries | Tunnel/redirect domains (duckdns, ngrok, etc.) |
| Sysmon 15 | File creation | Alternate Data Streams in user paths |
| Sysmon 12/13/14 | Registry | Persistence (Run keys, Winlogon, Services) |
| Security 4688 | Process creation | Security log process auditing |
| Security 7045 | Service install | New service installation |
| Security 1102 | Log clearing | Security log tampering |

## Deployment

### From WSL — write script to Windows filesystem first

Write the .ps1 to a Windows-accessible path. WSL `/tmp` is NOT visible to Windows.

```bash
# From WSL, write directly via /mnt/c/
# (Use write_file tool which handles this automatically)
```

### Launch options

**Option A: Background from WSL (no visible window, no output capture)**
```bash
cmd.exe /c "start \"\" powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File \"C:\Users\rkarl\AppData\Local\Temp\sysmon-monitor.ps1\""
```

**Option B: Inline from WSL (visible output, Ctrl+C to stop)**
```bash
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "C:\Users\rkarl\AppData\Local\Temp\sysmon-monitor.ps1"
```

**Option C: Elevated (required for Security + Sysmon log access)**
Run from an admin PowerShell on Windows:
```powershell
& "C:\Users\rkarl\AppData\Local\Temp\sysmon-monitor.ps1"
```

## Access Requirements

`Get-WinEvent` on `Microsoft-Windows-Sysmon/Operational` and `Security` logs
requires Administrator or Event Log Readers group membership.

From WSL, `powershell.exe` inherits a non-elevated token. Even if the Windows
user is in Event Log Readers, the WSL-spawned process may not have the privilege.
Test first:
```powershell
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 1
```
If this throws `UnauthorizedAccessException`, use Option C (elevated Windows terminal).

## Customization

Edit the parameters at the top of the script:
- `$PollSeconds` — event polling interval (default: 5)
- `$CommentaryInterval` — seconds between status commentaries (default: 20)
- `$SuspiciousDnsPatterns` — DNS tunnel domain patterns
- `$SuspiciousAdsPaths` — paths to watch for ADS

## Output Format

```
=== COMMENTARY [14:23:01] (elapsed: 2.1m | events: 47 | alerts: 3) ===
[NET] [powershell.exe] Client web -> example.com (93.184.216.34):443
[DNS] [svchost.exe] Tunnel DNS: tunnel.duckdns.org
=== Next commentary in 20s ===
```

Color coding:
- Red: PROC, TAMPER (critical)
- Yellow: DNS, ADS, PERSIST (suspicious)
- DarkYellow: NET, REG (unusual)
- Green: Clean status
