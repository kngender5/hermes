---
name: opnsense-admin
description: Manage OPNsense firewall — rules, NAT, VLANs, DNS, IDS/IPS, VPN, backups via REST API and SSH. Use when administering OPNsense firewall, configuring network security, managing Suricata, Unbound DNS, WireGuard/OpenVPN, or automating firewall operations.
---

# OPNsense Admin — Firewall Management

Manage OPNsense firewall through REST API and SSH. Covers firewall rules, NAT, VLANs, DNS, IDS/IPS, VPN, backups, and service management.

## OPNsense Overview

OPNsense is an open-source FreeBSD-based firewall and routing platform. Fork of pfSense, with modern UI and frequent updates.

**Key Components:**
- **Firewall:** Stateful packet filtering, NAT, rules
- **IDS/IPS:** Suricata (Snort-compatible)
- **DNS:** Unbound (resolver), DNS forwarding
- **VPN:** WireGuard, OpenVPN, IPsec
- **VLAN:** 802.1Q tagging
- **HA:** CARP, failover
- **API:** REST API for automation

## Connection

### API Access
```bash
# Base URL
https://opnsense.example.com

# Auth: API Key + Secret
# Generate in: System → Access → Users → API Keys
Header: Authorization: Basic $(echo -n "api-key:api-secret" | base64)
```

### SSH Access
```bash
ssh root@opnsense.example.com
# or
ssh -i ~/.ssh/opnsense admin@opnsense.example.com
```

## REST API Reference

### Firewall Rules

#### List Rules
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/firewall/filter/getRule/{}" | jq .
```

#### Add Rule
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/firewall/filter/addRule/{}" \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {
      "description": "Allow HTTPS to web server",
      "source_net": "any",
      "destination_net": "10.0.1.10",
      "destination_port": "443",
      "protocol": "TCP",
      "action": "pass",
      "enabled": "1",
      "sequence": "1",
      "direction": "in"
    }
  }'
```

#### Apply Rules
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/firewall/filter/apply"
```

### NAT

#### List NAT Rules
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/firewall/source_nat/getRule/{}" | jq .
```

#### Add Port Forward
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/firewall/source_nat/addRule/{}" \
  -H "Content-Type: application/json" \
  -d '{
    "rule": {
      "description": "Port forward HTTPS to internal server",
      "source": "any",
      "destination": "any",
      "destination_port": "443",
      "target": "10.0.1.10",
      "target_port": "443",
      "protocol": "TCP",
      "interface": "WAN"
    }
  }'
```

### VLANs

#### List VLANs
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/interfaces/vlan/getItem/{}" | jq .
```

#### Create VLAN
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/interfaces/vlan/addItem/{}" \
  -H "Content-Type: application/json" \
  -d '{
    "vlan": {
      "if": "igb0",
      "tag": "100",
      "descr": "IoT Network",
      "mode": "normal"
    }
  }'
```

### DNS (Unbound)

#### Get DNS Settings
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/unbound/settings/get" | jq .
```

#### Add DNS Override
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/unbound/settings/addHost/{}" \
  -H "Content-Type: application/json" \
  -d '{
    "host": {
      "hostname": "nas",
      "domain": "home.local",
      "rr": "A",
      "server": "10.0.1.5",
      "description": "NAS server"
    }
  }'
```

#### Apply DNS
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/unbound/service/reconfigure"
```

### IDS/IPS (Suricata)

#### Get Suricata Status
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/ids/service/status" | jq .
```

#### Enable IDS on Interface
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/ids/settings/set" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": {
      "enabled": "1",
      "ips": "1",
      "promisc": "0",
      "interfaces": ["wan", "lan"]
    }
  }'
```

#### Update Rules
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/ids/service/reloadRules"
```

### VPN

#### WireGuard — List Tunnels
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/wireguard/client/get" | jq .
```

#### WireGuard — Add Peer
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/wireguard/client/addItem/{}" \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "name": "laptop",
      "pubkey": "client-public-key-here",
      "tunnel-address": "10.100.0.2/32",
      "serveraddress": "10.100.0.1",
      "serverport": "51820"
    }
  }'
```

### Backups

#### Download Config Backup
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/core/backup/download/this" \
  -o opnsense-backup-$(date +%Y%m%d).xml
```

#### List Backups (if using Nextcloud/SFTP)
```bash
# Via SSH
ssh root@opnsense "ls -la /conf/backup/"
```

### System

#### Reboot
```bash
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/core/system/reboot"
```

#### Firmware Update
```bash
# Check for updates
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/core/firmware/status" | jq .

# Upgrade
curl -s -X POST -u "api-key:api-secret" \
  "https://opnsense.example.com/api/core/firmware/upgrade" \
  -H "Content-Type: application/json" \
  -d '{"upgrade": "1"}'
```

#### Get System Info
```bash
curl -s -u "api-key:api-secret" \
  "https://opnsense.example.com/api/diagnostics/system/systemInformation" | jq .
```

## Python API Client

```python
import requests, json
from base64 import b64encode

class OPNsense:
    def __init__(self, host, api_key, api_secret, verify_ssl=True):
        self.base_url = f"https://{host}"
        auth = b64encode(f"{api_key}:{api_secret}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        }
        self.verify = verify_ssl
    
    def get(self, path):
        resp = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            verify=self.verify,
        )
        return resp.json()
    
    def post(self, path, data=None):
        resp = requests.post(
            f"{self.base_url}{path}",
            headers=self.headers,
            json=data or {},
            verify=self.verify,
        )
        return resp.json()
    
    # Firewall rules
    def list_rules(self):
        return self.get("/api/firewall/filter/getRule/{}")
    
    def add_rule(self, description, dest, port, protocol="TCP", action="pass"):
        return self.post("/api/firewall/filter/addRule/{}", {
            "rule": {
                "description": description,
                "source_net": "any",
                "destination_net": dest,
                "destination_port": port,
                "protocol": protocol,
                "action": action,
                "enabled": "1",
            }
        })
    
    def apply_rules(self):
        return self.post("/api/firewall/filter/apply")
    
    # NAT
    def list_nat(self):
        return self.get("/api/firewall/source_nat/getRule/{}")
    
    def add_port_forward(self, desc, ext_port, int_ip, int_port, protocol="TCP"):
        return self.post("/api/firewall/source_nat/addRule/{}", {
            "rule": {
                "description": desc,
                "source": "any",
                "destination": "any",
                "destination_port": ext_port,
                "target": int_ip,
                "target_port": int_port,
                "protocol": protocol,
                "interface": "WAN",
            }
        })
    
    # DNS
    def add_dns_override(self, hostname, domain, ip, rr="A"):
        return self.post("/api/unbound/settings/addHost/{}", {
            "host": {
                "hostname": hostname,
                "domain": domain,
                "rr": rr,
                "server": ip,
            }
        })
    
    def apply_dns(self):
        return self.post("/api/unbound/service/reconfigure")
    
    # IDS/IPS
    def get_ids_status(self):
        return self.get("/api/ids/service/status")
    
    def enable_ids(self, interfaces=None):
        return self.post("/api/ids/settings/set", {
            "ids": {
                "enabled": "1",
                "ips": "1",
                "interfaces": interfaces or ["wan"],
            }
        })
    
    # Backup
    def download_backup(self, path="opnsense-backup.xml"):
        auth = self.headers["Authorization"]
        resp = requests.get(
            f"{self.base_url}/api/core/backup/download/this",
            headers={"Authorization": auth},
            verify=self.verify,
        )
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    
    # System
    def get_status(self):
        return self.get("/api/diagnostics/system/systemInformation")
    
    def reboot(self):
        return self.post("/api/core/system/reboot")

# Usage
fw = OPNsense("opnsense.example.com", "api-key", "api-secret", verify_ssl=False)

# Add firewall rule
fw.add_rule("Allow HTTPS", "10.0.1.10", "443")
fw.apply_rules()

# Add port forward
fw.add_port_forward("Web Server", "443", "10.0.1.10", "443")

# DNS override
fw.add_dns_override("nas", "home.local", "10.0.1.5")
fw.apply_dns()

# Check IDS status
print(fw.get_ids_status())

# Download backup
fw.download_backup("backup.xml")
```

## SSH Management

```bash
# Enter shell
ssh root@opnsense

# View firewall rules
pfctl -sr

# View NAT rules
pfctl -sn

# View states
pfctl -ss

# Restart firewall
pfctl -f /etc/pf.conf

# View Suricata logs
tail -f /var/log/suricata/eve.json

# View system logs
clog /var/log/system.log

# Backup config
cp /conf/config.xml /conf/backup/config-$(date +%Y%m%d).xml

# Restore config
cp /conf/backup/config-good.xml /conf/config.xml
# Reboot to apply
reboot

# Update OPNsense
opnsense-update
# or via GUI: System → Firmware → Update

# Install packages
pkg install os-wireguard
pkg install os-zabbix-agent
```

## Common Tasks

### Block an IP
```bash
# Via API
fw.add_rule("Block malicious IP", "192.0.2.100", "any", action="block")
fw.apply_rules()

# Via SSH (quick block)
echo "block drop quick from 192.0.2.100 to any" >> /etc/pf.conf
pfctl -f /etc/pf.conf
```

### Allow LAN to WAN
```bash
# Usually default, but if needed:
fw.add_rule("Allow LAN to WAN", "10.0.1.0/24", "any")
fw.apply_rules()
```

### Set up WireGuard VPN
```bash
# 1. Generate keys
wg genkey | tee privatekey | wg pubkey > publickey

# 2. Add tunnel via API
fw.post("/api/wireguard/server/addItem/{}", {
    "server": {
        "name": "wg0",
        "enabled": "1",
        "instance": "0",
        "pubkey": open("publickey").read().strip(),
        "privkey": open("privatekey").read().strip(),
        "port": "51820",
        "tunneladdress": "10.100.0.1/24",
    }
})

# 3. Add peer
fw.post("/api/wireguard/client/addItem/{}", {
    "client": {
        "name": "laptop",
        "pubkey": "client-pubkey",
        "tunneladdress": "10.100.0.2/32",
    }
})

# 4. Add firewall rule for WireGuard
fw.add_rule("Allow WireGuard", "any", "51820", "UDP")
fw.apply_rules()
```

### Schedule Automated Backups
```bash
# Via SSH — add to cron
cat >> /etc/crontab << 'EOF'
0 3 * * * root cp /conf/config.xml /conf/backup/config-$(date +\%Y\%m\%d).xml
EOF

# Or via API — create a script that downloads backup
# Add to Hermes cron:
# 0 3 * * * /home/kng/bin/opnsense-backup.sh
```

## Home Assistant Integration

```yaml
# configuration.yaml
opnsense:
  host: 10.0.1.1
  api_key: !secret opnsense_api_key
  api_secret: !secret opnsense_api_secret
  ssl: false

# Sensors
sensor:
  - platform: opnsense
    host: 10.0.1.1
    api_key: !secret opnsense_api_key
    api_secret: !secret opnsense_api_secret
    monitored_conditions:
      - cpu
      - memory
      - wan_status
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| API returns 401 | Check API key/secret, user has API access permission |
| Can't connect to web UI | `configctl webgui restart` via SSH |
| Firewall rules not applying | Run `pfctl -f /etc/pf.conf` or use API apply endpoint |
| Suricata not starting | Check interface assignment, rule download: `ids/service/reloadRules` |
| WireGuard tunnel down | Verify keys, check firewall rule for UDP port |
| Config corrupt | Restore from backup: `cp /conf/backup/config-good.xml /conf/config.xml` |
| Update fails | Check disk space: `df -h`; try `opnsense-update -f` |
| DNS not resolving | Check Unbound: `unbound-control status`; restart: `unbound-control reload` |

## Security Best Practices

1. **Use API keys** instead of password auth
2. **Restrict API access** to specific IPs
3. **Enable HTTPS** with valid certificate
4. **Regular backups** — automate daily config backups
5. **Keep updated** — apply security patches promptly
6. **Least privilege** — create dedicated API user with minimal permissions
7. **Enable IDS/IPS** — Suricata on WAN interface
8. **Disable unused services** — turn off what you don't need
9. **Strong passwords** — for all user accounts
10. **2FA** — enable for web UI access

## Source

- **API Docs:** https://docs.opnsense.org/development/api.html
- **GitHub:** https://github.com/opnsense/core
- **LobeHub Skill:** https://lobehub.com/skills/openclaw-skills-opnsense-admin
- **Python Client:** https://github.com/O-X-L/opnsense-api-client
- **CLI Tool:** https://github.com/andreas-stuerz/opn-cli
