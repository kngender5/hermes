---
name: hermes-device-provisioning
description: "Provision Hermes Agent on embedded Linux devices (Raspberry Pi, SBCs, ARM boards). Covers OS update, system tooling, SD card longevity, SSH hardening, firewall, Docker, and Hermes install with device-tuned config. Use when setting up Hermes on RPi4B, RPi5, Orange Pi, or any Debian/Ubuntu-based ARM SBC."
---

# Hermes Device Provisioning

Provision and configure Hermes Agent on embedded Linux devices — Raspberry Pi 4B/5, Orange Pi, Rock Pi, or any Debian/Ubuntu-based ARM SBC.

## When to Use

- Setting up Hermes on a Raspberry Pi or ARM SBC
- Fresh OS flash that needs full tooling + Hermes install
- Headless server setup (no GUI, SSH-only access)
- IoT/edge automation gateway with Hermes as the agent layer

## Key Constraints

- **ARM64/aarch64** — some Python wheels compile from source (slow on RPi)
- **1–8 GB RAM** — no local LLM inference realistic; cloud provider required
- **SD card / eMMC** — minimize writes (log2ram, noatime, Docker log rotation)
- **No GPU** — default to cloud LLM provider (OpenRouter recommended)
- **Headless** — all config via CLI/TUI, no GUI assumptions

## Setup Script

The canonical setup script is at `~/hermes-rpi4b-setup.sh` (or copy from `templates/hermes-rpi4b-setup.sh`).

### Usage

```bash
# Interactive (prompts for each option)
./hermes-rpi4b-setup.sh

# Non-interactive, all defaults
./hermes-rpi4b-setup.sh --auto

# Non-interactive with specific options
./hermes-rpi4b-setup.sh --auto \
  --model openrouter/anthropic/claude-sonnet-4 \
  --key sk-or-v1-...

# Skip specific components
./hermes-rpi4b-setup.sh --auto --no-docker --no-node
```

### What the Script Does

1. **OS Update** — `apt-get update && upgrade && dist-upgrade && autoremove`
2. **System Tools** — core utils, networking, monitoring, terminal, build tools, media, security, IoT (mosquitto, wireguard)
3. **SD Card Longevity** — log2ram, noatime mount option
4. **Docker** (optional) — CE + buildx + compose, daemon tuned for SD
5. **Python Tools** — venv, httpie, rich, pydantic, pytest, black, ruff
6. **Node.js + Node-RED** (optional) — NodeSource 22 LTS, Node-RED with systemd
7. **SSH Hardening** — disable root login, disable password auth, max 3 tries
8. **UFW Firewall** — deny incoming, allow SSH/MQTT/Node-RED
9. **Hermes Agent** — pip install in venv
10. **Toolset Selection** — interactive or auto selection of Hermes toolsets
11. **Configuration** — config.yaml + .env with device-tuned settings
12. **Helper Scripts** — hermes-start, hermes-health, hermes-update, rpi-info
13. **Shell Enhancements** — aliases, starship prompt
14. **Systemd Service** (optional) — hermes-gateway with linger

## Device-Tuned Hermes Config

```yaml
model:
  default: openrouter/google/gemini-2.0-flash  # fast, cheap for TUI
  provider: openrouter
  context_length: 32768        # RPi RAM is limited

agent:
  max_turns: 50                # prevent runaway on slow API

compression:
  enabled: true
  threshold: 0.60              # compress earlier
  target_ratio: 0.25

tools:
  enabled:
    - terminal
    - file
    - memory
    - session_search
    - skills
    - cronjob
    - clarify
    - todo
    - web
    - code_execution
    - vision
    - delegation
    - messaging
    - docker
    - debugging
```

## Toolset Selection Guide

### Always Enable (Core)
`terminal`, `file`, `memory`, `session_search`, `skills`, `cronjob`, `clarify`, `todo`, `web`, `code_execution`, `vision`, `delegation`, `messaging`

### Recommended for Server Use
`docker`, `debugging`

### Enable On Demand
| Toolset | When |
|---------|------|
| `discord` | Discord gateway connected |
| `spotify` | Spotify playback needed |
| `homeassistant` | Home Assistant integration |
| `tts` | Voice gateway (Discord/Telegram) |
| `image_gen` | AI image generation via API |
| `browser` | Web automation (heavy — Chromium) |
| `video` | Video analysis (heavy) |
| `x_search` | X/Twitter monitoring |
| `feishu_doc` | Feishu/Lark integration |
| `kanban` | Multi-agent workflows |

### Never Enable on RPi
`rl` (reinforcement learning), `moa` (mixture of agents — too expensive/slow)

## SD Card Longevity

Critical for RPi on SD card:

```bash
# log2ram — logs in RAM, sync hourly
sudo apt-get install log2ram

# noatime — reduce write ops
# Add to /etc/fstab for root mount:
# UUID=xxxx / ext4 defaults,noatime 0 1

# Docker log rotation
# /etc/docker/daemon.json:
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "storage-driver": "overlay2"
}
```

**Recommendation**: For heavy Docker/container use, boot from USB SSD instead of SD card.

## SSH Hardening

```bash
# Disable root login
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

# Disable password auth (key-only)
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config

# Max auth attempts
sudo sed -i 's/^#\?MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config

# Validate before restarting
sudo sshd -t && sudo systemctl restart sshd
```

**WARNING**: Only disable password auth if key-based auth is already set up.

## UFW Defaults for RPi Server

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh comment "SSH"
sudo ufw allow 1883 comment "MQTT"
sudo ufw allow 8883 comment "MQTT TLS"
sudo ufw allow 1880 comment "Node-RED"
sudo ufw --force enable
```

## Docker on ARM

- Images **must** be `arm64` or `arm/v7` — not all popular images have ARM builds
- Check hub.docker.com for arm64 tags before assuming compatibility
- Buildx works on ARM but cross-compiling x86 images is very slow
- For production container workloads, use USB SSD boot

## Verification

```bash
# Full system + Hermes health check
rpi-info
hermes-health

# Hermes doctor
hermes doctor

# Check toolsets
hermes tools list
```

## Reference

- `references/rpi4b-setup.md` — detailed breakdown of every install step, ARM considerations, and verification commands
- Full setup script: `~/hermes-rpi4b-setup.sh` (copy to target device before running)

## Helper Scripts (installed to ~/bin/)

| Script | Purpose |
|--------|---------|
| `hermes-start` | Activate venv + run hermes |
| `hermes-health` | Version, RAM, disk, CPU temp, doctor |
| `hermes-update` | OS + Hermes update |
| `rpi-info` | Full system info (model, temp, network, Docker, MQTT, UFW) |

## Pitfalls

- **Don't run as root** — script checks and exits
- **Don't skip OS update first** — old kernels cause Docker issues
- **Don't enable password auth disable without keys** — you'll lock yourself out
- **Don't install browser toolset on RPi** — Chromium is heavy and slow on ARM
- **Don't use local LLM on RPi** — no GPU, not enough RAM for useful models
- **Don't forget `source ~/.bashrc`** after install for aliases + PATH
