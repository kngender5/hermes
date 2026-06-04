# About Me

**Name:** Robert Karlsen
**Location:** Kvaløysletta, Tromsø, Norway
**Role:** Automation engineering student

# My Stack

- **OS:** Windows 11 + WSL2 (Ubuntu), Docker
- **Languages:** Python, C#, Bash, Rust, JSON, G-code
- **AI/ML:** vLLM, OpenRouter, local LLMs (llama.cpp)
- **Hardware:** ESP32, Raspberry Pi, Snapmaker A350T
- **Automation:** PLC/SCADA (Siemens TIA V19), Node-RED, cron workflows
- **3D Printing:** Luban, OrcaSlicer, dual-extruder config
- **Infra:** Proxmox VE, OPNsense, Docker

# Preferences

- Be direct and technical — skip basic explanations unless asked
- Prefer CLI solutions over GUI
- Show full commands, not pseudocode
- I use Norwegian keyboard (AltGr combos for special chars)
- Metric units, 24h time

# Active Profiles

| Profile | Purpose | SOUL.md |
|---------|---------|---------|
| `default` | General purpose / Discord | `~/data/hermes/SOUL.md` |
| `local` | llama.cpp local LLM | `~/data/hermes/profiles/local/SOUL.md` |
| `infra` | Proxmox, OPNsense, security | `~/data/hermes/profiles/infra/SOUL.md` |
| `academic` | Study workbench, EKOM exams | `~/data/hermes/profiles/academic/SOUL.md` |
| `creative` | Media, 3D print, hardware | `~/data/hermes/profiles/creative/SOUL.md` |

# Project Map

| Project | Path | Profile |
|---------|------|---------|
| InfraLab | `~/projects/infra-lab/` | infra |
| Study Workbench | `~/projects/study-workbench/` | academic |
| Creative Lab | `~/projects/creative-lab/` | creative |
| Pokemon AI | `~/projects/PokemonGold/` | creative |
| TTS/Voice | `~/projects/qwen3-tts/` | creative |
| PC Build | `~/projects/pc-build/` | creative |
| llama.cpp | `~/projects/llama.cpp/` | local |
| PLC Projects | `~/projects/elevator-plc/` | academic |

# System Notes

- WSL2 Ubuntu on H: drive
- `sudo apt` and `sudo apt-get` are passwordless (no sudo prompt)
- Always use `sudo apt-get install -y` for missing system packages
- Voice response: edge-tts → ffmpeg .opus → Discord MEDIA
- ntfy topic: `hermes-alerts`
- Log dirs: `~/data/proxmox-logs/`, `~/data/opnsense-logs/`, `~/data/security-monitor/`

## llama.cpp
- Model: Qwen3-14B-128K-Q3_K_M (~6.9GB)
- ctx-size 65536, port 18080
- RTX 4060 8GB: `--n-gpu-layers 20`

## Voice
- TTS: edge-tts (PernilleNeural/FinnNeural)
- STT: Whisper NbAiLab/nb-whisper-medium (CUDA)
- Pipeline: text → edge-tts .ogg → ffmpeg .opus → Discord MEDIA
- Scripts: `~/bin/{tts,voice-input,voice_transcribe.py}`
