---
name: dmux-multi-agent
description: "Multi-agent orchestration with dmux and tmux. Spawn parallel Hermes agents, delegate tasks, and collect results."
version: 1.1.0
author: agent
triggers:
  - multi agent
  - parallel agents
  - delegate
  - orchestrate
  - dmux
  - tmux agents
  - spawn agent
  - worker agents
---

# Multi-Agent Orchestration

Spawn and coordinate multiple Hermes agents in tmux panes for parallel work.

## Prerequisites

```bash
sudo apt-get install -y tmux
npm install -g dmux --prefix /home/kng/.local  # or /usr/local with sudo
```

## Quick Start

### Create tmux session with agent panes

```bash
# Create session
tmux new-session -d -s agents -n main -x 160 -y 40

# Split into 4 panes (2×2)
tmux split-window -t agents:0 -h
tmux split-window -t agents:0 -v
tmux split-window -t agents:0.1 -v

# Launch Hermes in each pane
tmux send-keys -t agents:0.0 "hermes 2>&1 | cat" Enter
tmux send-keys -t agents:0.1 "hermes 2>&1 | cat" Enter
tmux send-keys -t agents:0.2 "hermes 2>&1 | cat" Enter
tmux send-keys -t agents:0.3 "hermes 2>&1 | cat" Enter

# Wait for startup, then assign roles
sleep 10
tmux send-keys -t agents:0.0 "You are the ORCHESTRATOR. Coordinate tasks." Enter
tmux send-keys -t agents:0.1 "You are the RESEARCHER. Search and analyze." Enter
tmux send-keys -t agents:0.2 "You are the CODER. Write and edit code." Enter
tmux send-keys -t agents:0.3 "You are the REVIEWER. Review for bugs and quality." Enter

# Attach to view all agents
tmux attach -t agents
```

### Send task to specific agent

```bash
tmux send-keys -t agents:0.1 "Research topic X and write findings to /tmp/research.md" Enter
```

### Collect output from agent

```bash
tmux capture-pane -t agents:0.1 -p -S -20  # Last 20 lines
tmux capture-pane -t agents:0.1 -p           # Full buffer
```

### Kill session

```bash
tmux kill-session -t agents
```

## Layout Reference

```
┌─────────────────┬─────────────────┐
│ Pane 0.0        │ Pane 0.1        │
│ ORCHESTRATOR    │ RESEARCHER      │
├─────────────────┼─────────────────┤
│ Pane 0.2        │ Pane 0.3        │
│ CODER           │ REVIEWER        │
└─────────────────┴─────────────────┘
```

## Roles

| Role | Purpose | Typical tools |
|------|---------|---------------|
| Orchestrator | Delegate tasks, collect results, make decisions | All |
| Researcher | Search, analyze, document findings | web, file |
| Coder | Write and edit code | terminal, file |
| Reviewer | Review code, find bugs, suggest improvements | file, terminal |
| Tester | Run tests, report results | terminal |

## Best Practices

- **Independent tasks only** — Don't parallelize interdependent work
- **Max 5-6 panes** — Each pane consumes API tokens
- **Assign clear boundaries** — Each agent works on different files/tasks
- **Wait for startup** — Hermes takes 10-15s to boot on WSL. Send role messages after readiness check.
- **Use `/mnt/c/` paths** — Windows filesystem accessible from all agents

## dmux Config-Based Approach

dmux can also manage agents via its TUI. Create `~/.dmux/dmux.config.json`:

```json
{
  "projectName": "kng",
  "projectRoot": "/home/kng",
  "panes": [],
  "sidebarProjects": [
    {"projectName": "kng", "projectRoot": "/home/kng"}
  ],
  "settings": {
    "openRouterApiKey": "sk-or-...",
    "preferredAgent": "hermes-local-35b",
    "agents": {
      "hermes-local-27b": {
        "command": "/home/kng/.local/bin/local",
        "args": ["-m", "Qwen3.6-27B-Q4_K_M.gguf"],
        "enabled": true
      },
      "hermes-local-35b": {
        "command": "/home/kng/.local/bin/local",
        "args": ["-m", "Qwen3.6-35B-A3B-IQ4_NL.gguf"],
        "enabled": true
      },
      "hermes": {
        "command": "/home/kng/.local/bin/hermes",
        "args": [],
        "enabled": true
      },
      "claude": {
        "command": "/home/kng/.local/bin/claude",
        "args": [],
        "enabled": true
      }
    }
  },
  "controlPaneSize": 40
}
```

Install agent CLIs to `~/.local/bin/`:
```bash
npm install -g @anthropic-ai/claude-code --prefix /home/kng/.local
```

**API key propagation:** dmux reads `OPENRouter_API_KEY` from the shell environment, NOT from Hermes config. Add to `~/.bashrc`:
```bash
set -a; source "$HOME/data/hermes/.env" 2>/dev/null; set +a
```

Run dmux from a terminal (requires TTY — cannot run headlessly):
```bash
cd /home/kng
dmux
```

Inside dmux: press `n` for new pane, pick agent, type prompt. Each pane gets its own git worktree.

## dmux vs Raw tmux

| | dmux | Raw tmux |
|---|---|---|
| Interface | Interactive TUI | Manual commands |
| Worktrees | Auto per pane | Manual git worktree |
| Agent CLIs | Claude, Codex, Hermes, etc. | Any command |
| Best for | Parallel coding agents | Custom setups, headless |

## Wrapper Scripts

`~/bin/tmux_agent.py` provides higher-level management:

```bash
python3 ~/bin/tmux_agent.py create mysession /working/dir
python3 ~/bin/tmux_agent.py interactive mysession planner
python3 ~/bin/tmux_agent.py send mysession planner "Your task"
python3 ~/bin/tmux_agent.py capture mysession planner 30
python3 ~/bin/tmux_agent.py list mysession
python3 ~/bin/tmux_agent.py kill mysession
```

## Pitfalls

- **Hermes startup delay** — Wait 10-15s after sending `hermes` command before sending role messages
- **Non-interactive dmux** — `dmux` is a TUI that requires a terminal. For headless spawning, use `tmux` directly as shown above
- **WSL path confusion** — `~/Desktop/` doesn't exist. Use `/mnt/c/Users/<username>/Desktop/`
- **API key propagation** — dmux reads `OPENROUTER_API_KEY` from the shell environment, NOT from Hermes config. Source `~/.hermes/.env` in `.bashrc`.
- **Bash reserved word** — `local` is a bash reserved word. Always use full path `~/.local/bin/local` in configs and scripts.
- **Multiple model profiles** — Create separate dmux agents (`hermes-local-27b`, `hermes-local-35b`) with `-m <model_id>` args for each local model. Query exact model IDs from `curl http://127.0.0.1:18080/v1/models`.
