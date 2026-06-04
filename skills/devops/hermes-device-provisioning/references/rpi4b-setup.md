# RPi4B Hermes Agent — Setup Reference

## Full Script Location

The canonical setup script is at: `~/hermes-rpi-4b-setup.sh` (on the user's WSL/home directory)

Copy to RPi before running:
```bash
scp ~/hermes-rpi4b-setup.sh pi@raspberrypi:~/
ssh pi@raspberrypi 'chmod +x hermes-rpi4b-setup.sh && ./hermes-rpi4b-setup.sh'
```

## Non-interactive Mode (for automation/Ansible)

```bash
# Full install, all defaults
./hermes-rpi4b-setup.sh --auto

# With model + key
./hermes-rpi4b-setup.sh --auto \
  --model openrouter/anthropic/claude-sonnet-4 \
  --key sk-or-v1-...

# Skip Docker and Node
./hermes-rpi4b-setup.sh --auto --no-docker --no-node
```

## What Gets Installed

### Step 1 — OS Update
Full `apt-get update && upgrade && dist-upgrade && autoremove`. Reboots if kernel updated.

### Step 2 — System Tools
- **Core**: curl, wget, git, jq, sqlite3, unzip, zip, pigz, lz4
- **Networking**: nmap, rsync, socat, netcat, ufw, wireguard, ethtool, openssh-server
- **Monitoring**: htop, iotop, iftop, nethogs, sysstat, lm-sensors, ncdu, duf
- **Terminal**: tmux, neovim, vim, bat, fd-find, ripgrep, fzf, tldr, shellcheck
- **Build**: build-essential, gcc, g++, cmake, pkg-config, libffi-dev, libssl-dev
- **Media**: ffmpeg, imagemagick, exiftool
- **Security**: fail2ban, gnupg, auditd
- **IoT**: mosquitto, mosquitto-clients
- **Extras**: eza, starship, lazydocker

### Step 3 — SD Card Longevity
- `log2ram` — logs in RAM, syncs to SD hourly
- `noatime` mount option in `/etc/fstab`

### Step 4 — Docker (optional)
- Docker CE + buildx + compose-plugin
- Daemon config: log rotation (10m x 3), overlay2, buildkit
- User added to docker group

### Step 5 — Python Tools
- Venv at `~/.venvs/hermes`
- pip tools: httpie, requests, rich, typer, pydantic, pyyaml, pytest, black, ruff

### Step 6 — Node.js 22 LTS + Node-RED (optional)
- Via NodeSource repo
- Node-RED with `--production` flag for faster ARM install
- Optional systemd service

### Step 7 — SSH Hardening
- Disables root login, password auth, sets max 3 auth tries
- Validates config with `sshd -t` before restarting
- Backs up original config

### Step 8 — UFW Firewall
- Default deny incoming, allow outgoing
- Opens: SSH (22), MQTT (1883/8883), Node-RED (1880)

### Step 9 — Hermes Agent
- `pip install hermes-agent` in venv
- Venv bin added to PATH in `.bashrc`

### Step 10 — Toolset Selection
User selects which Hermes toolsets to enable:
- **Always on**: terminal, file, memory, session_search, skills, cronjob, clarify, todo, web, code_execution, vision, delegation, messaging
- **Optional**: docker, debugging, discord, spotify, homeassistant, tts, image_gen, video, browser, x_search, feishu_doc, feishu_drive, yuanbao, kanban
- Auto mode defaults: docker + debugging

### Step 11 — Hermes Configuration
Writes `~/.hermes/config.yaml` and `~/.hermes/.env`:
- Model: `openrouter/google/gemini-2.0-flash` (default, override with `--model`)
- Context: 32768 (RPi RAM limited)
- Compression: enabled at 60% threshold
- Toolsets: dynamic list from Step 10 selections

### Step 12 — Helper Scripts (`~/bin/`)
- `hermes-start` — activate venv + run
- `hermes-health` — version, RAM, disk, CPU temp, doctor
- `hermes-update` — OS + Hermes update
- `rpi-info` — full system info (model, temp, network, Docker, MQTT, UFW)

### Step 13 — Shell Enhancements
- Bash aliases: `update`, `temp`, `myip`, `docker-stop-all`, `mqtt-sub`, etc.
- Starship prompt (minimal, fast config)

### Step 14 — Systemd Service (optional)
- `hermes-gateway.service` as user service
- `loginctl enable-linger` for boot persistence

## Key ARM/RPi Considerations

| Issue | Mitigation |
|-------|------------|
| SD card writes | log2ram + noatime + Docker log rotation |
| Slow pip builds | PIP_TIMEOUT=600 for ARM wheel compilation |
| No local LLM | Default to cloud provider (OpenRouter) |
| Docker images | Must be arm64 — not all images support ARM |
| RAM pressure | 32K context, early compression, 50 max turns |
| Node-RED on ARM | `--production` flag, expect slow npm install |

## RPi4B Container Warning

Docker on RPi4B only runs `arm64` or `arm/v7` images. Many popular images
(some databases, niche tools) don't have ARM builds. For heavy container
workloads, boot from USB SSD — SD card I/O is a bottleneck.

## Verification Commands

```bash
# System info
rpi-info

# Hermes health
hermes-health

# Hermes doctor
hermes doctor

# Check toolsets
hermes tools list
```
