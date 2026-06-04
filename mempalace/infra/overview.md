# Infrastructure

## Proxmox VE
- Primary hypervisor for VMs and LXC containers
- Managed via devops/proxmox-admin skill
- Logging: devops/proxmox-logging skill (ProxmoxLogger Python class, JSONL logging)

## OPNsense
- Firewall/router
- Managed via devops/opnsense-admin skill
- Logging: devops/opnsense-logging skill (OPNsenseLogger Python class, IDS alert processing)
- VPN event tracking, configctl wrapper

## Security Monitoring
- devops/security-monitor skill
- Log dirs: ~/data/proxmox-logs/, ~/data/opnsense-logs/, ~/data/security-monitor/

## Cron Jobs (3 active)
- Unified security-check.sh
- Countermeasures: hourly
- Daily report: 08:00
- Heartbeat: 12/18
