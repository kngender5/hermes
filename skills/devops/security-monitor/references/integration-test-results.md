# WSL2 Integration Test Results (2026-06-02)

## Test Environment
- WSL2 Ubuntu on Windows 11, Kernel 6.6.87.2-microsoft-standard-WSL2
- Python 3.14.4, psutil 7.2.2, inotify 0.2.12
- Windows PowerShell 5.1

## Results Summary

### Test 1: Connection Monitoring — PASS
- WSL detected new listening ports, new users (apt-get), file hash changes
- Windows: clean (no RDP/VNC/WinRM issues)

### Test 2: Honeytrap — PASS
- All 6 decoy ports responded correctly with fake banners
- SSH captured client version strings; HTTP traps captured full request paths
- 16 events logged; all include service, port, source IP:port, hit count

### Test 3: Canary + Inotify — PASS
- All 6 canary files triggered `canary_accessed` on read
- 641 IN_ACCESS events from baseline reads (expected noise — focus on IN_MODIFY/IN_ATTRIB for real tampering)

### Test 4: Injection Detection — PASS
- All 8 scanners clean; SUID module slow (30s+)
- LD_PRELOAD env test correctly handled

### Test 5: Network Sandbox — PASS
- Block/allow via Windows Firewall working
- CLI arg order: `--ip` must come AFTER subcommand

### Test 6: Centralized Logging — PASS
- 672 events from 4 sources collected in first run
- Timeline, analysis, reporting all functional

### Test 7: Countermeasures — PASS
- Dry-run correctly identified honeytrap hits; localhost excluded from blocking
- Rollback support confirmed

### Test 8: Cron Jobs — PASS
- 6 jobs enabled, all scheduled correctly

## Noise Baseline (no attacks)
- Canary: ~100-700 IN_ACCESS events per 15 min (baseline reads — normal)
- Honeytrap: 0 events (any hit = real)
- Injection: 0 events (any = investigate)
- Network: 0-2 events per 30 min (normal outbound)
