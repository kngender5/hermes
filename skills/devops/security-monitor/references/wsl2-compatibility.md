# WSL2 Security Tool Compatibility

## What Works in WSL2

| Tool | Status | Notes |
|------|--------|-------|
| `inotify-tools` | WORKS | File monitoring — primary replacement for auditd |
| `ss` / `netstat` | WORKS | Socket/connection monitoring |
| `ps aux` | WORKS | Process listing |
| `/proc/net/tcp` | WORKS | Raw connection table parsing |
| `journalctl` | WORKS | systemd journal (auth, sshd, login) |
| `last` / `lastb` | WORKS | Login/failed login history |
| `find -perm` | WORKS | SUID binary discovery (slow: 30-60s) |
| `md5sum` | WORKS | File integrity hashing |
| `socat` / `ncat` | WORKS | Network listeners, honeypots |
| `tcpdump` | WORKS | Packet capture (needs root) |
| `python3 + psutil` | WORKS | Process monitoring, /proc parsing |
| `python3 + inotify` | WORKS | Real-time file event monitoring |
| `powershell.exe` | WORKS | Windows-side checks from WSL |

## What Does NOT Work in WSL2

| Tool | Why | Replacement |
|------|-----|-------------|
| `auditd` | Kernel lacks audit syscall | `inotify-tools` + `/proc` parsing |
| `iptables` | No netfilter in WSL2 kernel | Windows Firewall via `powershell.exe` |
| `nftables` | Same as above | Windows Firewall via `powershell.exe` |
| `fail2ban` | Depends on iptables | Custom countermeasures via Windows Firewall |

## WSL2-Specific Behaviors

- **WSL Interop**: Enabled by default. Windows `.exe` runnable from WSL. Lateral movement path.
- **Windows filesystem**: Mounted at `/mnt/c/`. Credential files exposed to WSL.
- **ptrace_scope**: Set to 1 (restricted). Cannot be changed.
- **Root processes**: plan9, chronyd, networkd-dispatcher, cups snap, agetty, unattended-upgrades are NORMAL in WSL2.
- **No audit kernel messages**: `journalctl` works for systemd units but auditd is absent.

## Windows Firewall from WSL

```bash
# Block an IP
powershell.exe -Command 'New-NetFirewallRule -DisplayName "hermes-block-1-2-3-4" -Direction Outbound -RemoteAddress 1.2.3.4 -Action Block'

# Remove block
powershell.exe -Command 'Remove-NetFirewallRule -DisplayName "hermes-block-1-2-3-4"'
```

## Performance Benchmarks (RTX 4060, WSL2 Ubuntu 24.04)

| Operation | Time | Notes |
|-----------|------|-------|
| `ss -tlnp` | <100ms | Socket listing |
| `find / -perm /6000` | 30-60s | Full SUID scan — slow |
| `find /usr -perm /6000` | 2-5s | Limited scope — fast |
| Canary integrity check | 2-5s | MD5 of 9 files |
| PowerShell startup | 3-5s | First call overhead |
| `inotifywait` setup | <1s | Per-directory watch |
