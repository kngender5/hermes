# Hermes Agent — Private Repository

> Configuration, skills, profiles, and automation for the Hermes AI Agent ecosystem.

## Overview

This repository contains the complete Hermes Agent setup including:
- **40+ specialized skills** for AI-assisted workflows
- **4 agent profiles** (default, infra, academic, creative, local)
- **Cron jobs** for automated monitoring and reporting
- **Memory files** for persistent agent context

## Repository Structure

```
hermes/
├── README.md              # This file
├── AGENTS.md              # Guidelines for AI agents (Copilot, Jules)
├── SOUL.md                # Root agent personality definition
├── config.yaml            # Sanitized agent configuration (no secrets)
├── skills/                # Reusable AI skills (SKILL.md format)
│   ├── academic/          # EKOM exam tools, engineering suite
│   ├── creative/          # Media, 3D printing, ASCII art
│   ├── devops/            # Proxmox, OPNsense, Docker, security
│   ├── mlops/             # Colab, LLM inference, quantization
│   ├── plc/               # Siemens TIA Portal, SCL automation
│   ├── github/            # PR workflows, code review, issues
│   ├── software-dev/      # Debugging, TDD, planning
│   └── ... (20+ more)
├── profiles/              # Agent profile configurations
│   ├── infra/             # Proxmox, OPNsense, security focus
│   ├── academic/          # Study workbench, EKOM exams
│   ├── creative/          # Media, 3D print, hardware
│   └── local/             # llama.cpp local LLM
├── cron/                  # Scheduled jobs and output
│   ├── jobs.json          # Job definitions
│   └── output/            # Historical job output
└── memories/              # Persistent agent memory
    ├── MEMORY.md          # Agent's personal notes
    └── USER.md            # User profile and preferences
```

## Skills Format

Each skill follows the **SKILL.md** convention:

```yaml
---
name: skill-name
description: What this skill does
---

# Skill Title
...
```

Skills may include:
- `references/` — detailed documentation
- `scripts/` — executable Python/Bash scripts
- `templates/` — reusable file templates
- `assets/` — images, data files

## AI Agent Guidelines

See **[AGENTS.md](AGENTS.md)** for detailed guidelines on how Copilot, Jules, and other AI agents should work with this repository.

## Security

- **No secrets in this repo.** All tokens, API keys, and credentials are redacted.
- `config.yaml` contains placeholders (`YOUR_*_HERE`) for sensitive values.
- `.gitignore` excludes auth files, databases, caches, and runtime state.

## Updating

After significant changes to skills, profiles, or configuration:

### Quick update (if already synced)
```bash
cd ~/hermes-repo
git add -A
git commit -m "Description of changes"
git push
```

### Full sync from Hermes
```bash
cd ~/hermes-repo
cp -r ~/data/hermes/skills .
cp -r ~/data/hermes/profiles .
cp -r ~/data/hermes/cron .
cp -r ~/data/hermes/memories .
cp ~/data/hermes/SOUL.md .
# config.yaml must be sanitized (remove tokens) before committing
git add -A
git commit -m "Description of changes"
git push
```

### Automated sync
```bash
bash ~/hermes-repo/scripts/sync-hermes.sh
```

## License

Private — All rights reserved.
