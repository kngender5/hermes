# Canary Event Analysis — Forensic Playbook

## Session: 2026-06-02 Canary Warning Investigation

### What happened
- Canary daemon (`~/bin/canary monitor`, PID 5447) watching `/etc`, `/home/kng`, `/tmp`, etc.
- At 22:26 UTC: burst of 842 events in ~2 minutes
- All 5 canary files "accessed" (IN_ACCESS), all critical files showed IN_ACCESS
- `/etc/passwd` and `/etc/group` hash mismatches triggered integrity alerts

### Root cause: self-inflicted
1. **Hermes agent** building security-monitor skill (reading files, installing scripts at 22:30)
2. **apt install** at 22:38 installed 20+ packages (tcpdump, inotify-tools, auditd, socat, ncat + PulseAudio)
   - dpkg added users: ntfy, tcpdump; groups: pulse, rtkit, rdma, pulse-access
   - dpkg created 26 `.dpkg-new` temporary binaries in /usr/bin
   - dpkg read /etc/passwd and /etc/group repeatedly for user lookups

### Forensic indicators: self-inflicted vs real

Self-inflicted: IN_ACCESS only, burst of 100-1000+ events in seconds, .dpkg-new files in /usr/bin, passwd/group mode/owner intact with new standard users, all canaries hit in &lt;2s, dpkg.log correlation.

Real intrusion: IN_MODIFY/IN_ATTRIB/IN_CLOSE_WRITE/IN_DELETE, sustained low-volume changes, modified existing entries, single canary hit, no package activity correlation.

### Resolution
`~/bin/canary init` to re-baseline after package installs.
