# Multi-Agent Tmux Orchestration

## Pattern: Orchestrator + N Workers

Main agent (orchestrator) coordinates tasks across Hermes instances running in tmux windows.

```
tmux session: my-project
├── [0] orchestrator  (main Hermes)
├── [1] planner       (research + planning)
├── [2] builder       (implementation)
└── [3] reviewer      (QA + code review)
```

## Quick Start

```bash
# Create session
python3 ~/bin/tmux_agent.py create my-project /working/dir

# Spawn agents (each in new tmux window)
python3 ~/bin/tmux_agent.py interactive my-project planner
python3 ~/bin/tmux_agent.py interactive my-project builder
python3 ~/bin/tmux_agent.py interactive my-project reviewer

# View live
tmux attach -t my-project
```

## Sending Tasks

```bash
# From terminal
python3 ~/bin/tmux_agent.py send my-project planner "Analyze the auth system"

# From Hermes execute_code
from hermes_tools import terminal
terminal(command="python3 ~/bin/tmux_agent.py capture my-project planner 30", timeout=10)
```

## Model Override Per Agent

Different agents can use different models:

```bash
python3 ~/bin/tmux_agent.py interactive my-project planner -m openrouter/owl-alpha
python3 ~/bin/tmux_agent.py interactive my-project builder -m openrouter/claude-sonnet-4
python3 ~/bin/tmux_agent.py interactive my-project reviewer -m openrouter/owl-alpha
```

## delegate_task vs Tmux

| | `delegate_task` | Tmux agents |
|---|---|---|
| Isolation | Same process, isolated context | Separate process |
| Duration | Minutes (parent must stay alive) | Hours/days (independent) |
| Interactive | No | Yes |
| Overhead | Low | Higher (full Hermes instance) |
| Best for | Quick parallel subtasks | Long-running interactive work |

## Scripts

| Script | Location | Purpose |
|---|---|---|
| `tmux_agent.py` | `~/bin/` or `skill:discord-voice/scripts/` | Create/send/capture/list/kill |
| `orchestrate.py` | `~/bin/` or `skill:discord-voice/scripts/` | Higher-level task delegation |
