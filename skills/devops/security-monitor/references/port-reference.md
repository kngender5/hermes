# Honeytrap Port Reference

## Decoy Ports

| Port | Service | Fake Banner | Intelligence Gathered |
|------|---------|-------------|----------------------|
| 2222 | SSH honeypot | `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.10` | Client version string, payload |
| 4444 | Reverse shell trap | none | Raw payload bytes |
| 5555 | ADB backdoor trap | none | Raw payload bytes |
| 5900 | VNC honeypot | `RFB 003.008\n` | Client handshake |
| 8081 | HTTP proxy trap | `HTTP/1.1 403 Forbidden / nginx/1.24.0` | Full HTTP request (method, path, headers) |
| 9090 | Mgmt interface trap | Fake admin panel HTML | Full HTTP request |

## Known C2 / Suspicious Ports (monitored by net-sandbox)

| Port | Name | Severity |
|------|------|----------|
| 4444 | Metasploit default | Critical |
| 5555 | Android ADB / backdoor | Critical |
| 6666-6667 | IRC C2 | High |
| 1080 | SOCKS proxy / tunneling | Medium |
| 31337 | Back Orifice | Critical |
| 12345-12346 | NetBus | Critical |
| 50050 | Cobalt Strike team server | Critical |
| 8080 | HTTP proxy / alt HTTP | Medium |
| 8443 | HTTPS alt / common C2 | Medium |
| 9050 | Tor SOCKS (exfiltration) | Medium |
| 20000 | Millennium backdoor | High |

## Windows Security Event IDs

| Event ID | Description | Priority |
|----------|-------------|----------|
| 4624 | Successful logon | Medium |
| 4625 | Failed logon | High (brute-force) |
| 4634 | Logon session ended | Low |
| 4648 | Explicit credential logon | High (pass-the-hash) |
| 4672 | Special privileges assigned | High (admin logon) |
| 4720 | User account created | Critical |
| 4722 | User account enabled | Critical |
| 4728 | Member added to security group | Critical |
| 4732 | Member added to local group | Critical |
| 7045 | New service installed | Critical |
