# Technical Environment

## System
- OS: Windows 11 + WSL2 (Ubuntu), Docker
- Languages: Python, C#, Bash, Rust, JSON, G-code
- AI/ML: vLLM, OpenRouter, local LLMs (llama.cpp)
- Hardware: ESP32, Raspberry Pi, Snapmaker A350T
- Automation: PLC/SCADA (Siemens TIA V19), Node-RED, cron workflows
- 3D Printing: Luban, OrcaSlicer, dual-extruder config
- Infra: Proxmox VE, OPNsense, Docker

## WSL2
- Ubuntu on H: drive
- sudo apt and sudo apt-get are passwordless
- Always use `sudo apt-get install -y` for missing system packages
- Prefer absolute paths — CWD is often /mnt/c/Users/rkarl causing "file not found" when mixing Windows/WSL paths

## llama.cpp
- Model: Qwen3-14B-128K-Q3_K_M (~6.9GB) at ~/models/Qwen3-14B-128K-Q3_K_M/
- Standard Qwen3-14B=40K ctx (below Hermes 64K min) — must use Unsloth 128K variant
- RTX 4060 8GB: --n-gpu-layers 20 partial offload
- ctx-size 65536, port 18080
- hf download CLI: --local-dir only (not Python API flags)
- Profile config: ~/.hermes/profiles/local/config.yaml — context_length 65536, model default must match /v1/models ID exactly

## Voice Pipeline
- TTS: edge-tts (PernilleNeural/FinnNeural)
- STT: Whisper NbAiLab/nb-whisper-medium (CUDA)
- Pipeline: text → edge-tts .ogg → ffmpeg .opus → Discord MEDIA
- Scripts: ~/bin/{tts,voice-input,voice_transcribe.py}

## ntfy
- Topic: hermes-alerts
- Helper: ~/bin/ntfy-alert

## Git Credential
- `git config --global credential.helper '!gh auth git-credential'`
