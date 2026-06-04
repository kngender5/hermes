# AGENTS.md — AI Agent Guidelines

> For GitHub Copilot, Google Jules, and other AI coding agents working in this repo.

## First Run

When starting work in this repository:

1. Read `README.md` for overview
2. Read `config.yaml` for agent configuration
3. Read `SOUL.md` for agent personality
4. Read relevant `skills/<category>/<skill>/SKILL.md` before working in that domain
5. Read `memories/MEMORY.md` for recent context

## Repository Map

| Path | Purpose | AI Use |
|------|---------|--------|
| `skills/` | Reusable skill definitions (SKILL.md) | Read before domain work |
| `skills/*/scripts/` | Executable Python/Bash | Can be run directly |
| `skills/*/templates/` | File templates | Copy and adapt |
| `skills/*/references/` | Detailed docs | Deep reference |
| `profiles/` | Agent profile configs | Environment-specific settings |
| `cron/jobs.json` | Scheduled job definitions | Monitoring/automation |
| `memories/MEMORY.md` | Agent memory | Context persistence |
| `memories/USER.md` | User profile | User preferences |
| `config.yaml` | Agent config (sanitized) | Runtime configuration |
| `SOUL.md` | Agent personality | Behavior guidelines |

## Working with Skills

### Reading a Skill
Every skill has a `SKILL.md` with YAML frontmatter:
```yaml
---
name: skill-name
description: What this skill does
---
```
Read the SKILL.md before performing any task in that domain.

### Creating a New Skill
1. Create directory: `skills/<category>/<skill-name>/`
2. Write `SKILL.md` with frontmatter + markdown body
3. Add `references/`, `scripts/`, `templates/` as needed
4. Follow existing skills for format consistency

### Modifying a Skill
1. Read the existing SKILL.md fully
2. Make targeted changes
3. Update the description if scope changes
4. Commit with clear message about what changed

## Code Guidelines

### Python
- Target Python 3.12+ (matches WSL2 Ubuntu environment)
- Use type hints for function signatures
- Use `pathlib.Path` over `os.path`
- Prefer f-strings over `.format()`
- Use `argparse` for CLI scripts
- Add shebang `#!/usr/bin/env python3` for executable scripts

### Bash
- Use `#!/usr/bin/env bash`
- Set `set -euo pipefail` at the top
- Quote all variables: `"$VAR"`
- Use `$(command)` over backticks
- Prefer `[[ ]]` over `[ ]`

### G-code
- Follow existing patterns in `skills/mechanical/`
- Comment every tool change and major operation
- Include safety lines (G28, G90) at start

## File Conventions

### Never Commit
- Secrets, tokens, API keys (use placeholders)
- Database files (`*.db`, `*.sqlite`)
- Runtime state (`*.pid`, `*.lock`)
- Cache directories
- Large binary files (>1MB)

### Always Commit
- Source code (`*.py`, `*.sh`, `*.js`)
- Configuration templates
- Documentation and references
- Skill definitions

## Git Workflow

### Commit Messages
Use conventional commits:
```
feat: add new colab skill for audio inference
bfix: correct VRAM calculation in gpu-inference
docs: update README with new profile info
refactor: restructure devops skills
chore: update .gitignore
```

### Before Committing
1. Run syntax checks on Python files: `python3 -m py_compile script.py`
2. Run shellcheck on Bash scripts: `shellcheck script.sh`
3. Verify no secrets in diff: `git diff --cached | grep -i "token\|key\|secret\|password"`

## Domain-Specific Notes

### Colab Notebooks (`mlops/colab-*`)
- Prefer `uv pip install` over `pip install` (10-100x faster)
- Target T4 GPU (free tier) as default
- Include GPU verification cell at start
- T4 does NOT support bf16 — use float16

### PLC / TIA Portal (`plc/*`)
- SCL is the primary language
- Export format is `.scl` files
- Always backup before modifying PLC code

### DevOps (`devops/*`)
- Proxmox and OPNsense are primary targets
- Use Python for automation scripts
- Log to JSONL format for structured logging

### Academic (`academic/*`)
- Norwegian language (bokmål) for course materials
- EKOM exams are case-based
- Jupyter notebooks preferred over CLI for calculators

## AI Agent Coordination

When multiple AI agents work in this repo:

1. **Copilot** — inline code completion, suggestions during editing
2. **Jules** — autonomous task execution, multi-file changes
3. **Hermes** (local) — orchestration, task delegation, cron jobs

Each agent should:
- Check for existing files before creating new ones
- Follow the established directory structure
- Use existing patterns and conventions
- Write commit messages that other agents can understand

## Verification

Before pushing changes:
1. Parse all YAML files: `python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"`
2. Check Python syntax: `python3 -m py_compile file.py`
3. Validate markdown links where applicable
4. Ensure SKILL.md frontmatter is valid YAML
