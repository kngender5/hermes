#!/usr/bin/env python3
"""
orchestrate.py - Delegate tasks to Hermes agents running in tmux

Called from Hermes execute_code to:
  1. Spawn agents in new tmux windows (if not already running)
  2. Send tasks to specific agents
  3. Collect results
  4. List agent status

Usage:
  python3 orchestrate.py ensure <session> <name>     # Ensure agent exists
  python3 orchestrate.py task <session> <name> <task> # Send task, wait for result
  python3 orchestrate.py collect <session> <name>     # Collect output
  python3 orchestrate.py status <session>             # Status of all agents
"""
import subprocess, sys, os, time, json

TMUX = "tmux"

def tmux_run(*args):
    r = subprocess.run([TMUX] + list(args), capture_output=True, text=True)
    return r.stdout.strip(), r.returncode

def has_session(s):
    _, rc = tmux_run("has-session", "-t", s)
    return rc == 0

def create_session(s, cwd=None):
    if has_session(s): return
    args = ["new-session", "-d", "-s", s, "-x", "180", "-y", "45"]
    if cwd: args += ["-c", cwd]
    tmux_run(*args)

def ensure_agent(s, name, model=None):
    """Ensure a Hermes agent is running in the session."""
    create_session(s)
    out, _ = tmux_run("list-windows", "-t", s, "-F", "#{window_name}")
    if name not in out.splitlines():
        model_args = f"-m {model}" if model else ""
        tmux_run("new-window", "-t", s, "-n", name)
        cmd = f"hermes {model_args} 2>&1 | cat".strip()
        tmux_run("send-keys", "-t", f"{s}:{name}", cmd, "Enter")
        time.sleep(4)  # Wait for Hermes to boot
        tmux_run("send-keys", "-t", f"{s}:{name}", "Enter")
        time.sleep(1)
    return True

def send_task(s, name, task, wait=30):
    """Send a task to an agent and wait for response."""
    tmux_run("send-keys", "-t", f"{s}:{name}", "C-c", "Enter")
    time.sleep(0.5)
    tmux_run("send-keys", "-t", f"{s}:{name}", task, "Enter")
    time.sleep(min(wait, 5))
    for i in range(wait):
        out = capture(s, name, 50)
        lines = out.splitlines()
        if lines and "❯" in lines[-1]:
            break
        time.sleep(1)
    return capture(s, name, 60)

def capture(s, name, lines=40):
    tmux_run("capture-pane", "-t", f"{s}:{name}", "-p", "-S", f"-{lines}")
    out, _ = tmux_run("capture-pane", "-t", f"{s}:{name}", "-p", "-S", f"-{lines}")
    return out

def list_agents(s):
    out, rc = tmux_run("list-windows", "-t", s,
                       "-F", "#{window_index}|#{window_name}|#{pane_current_command}|#{pane_current_path}")
    if rc != 0: return []
    return [dict(zip(["idx","name","cmd","cwd"], l.split("|"))) for l in out.splitlines() if "|" in l]

def kill_session(s):
    tmux_run("kill-session", "-t", s)

if __name__ == "__main__":
    args = sys.argv[1:]
    action = args[0] if args else "help"

    if action == "ensure":
        s, name = args[1], args[2]
        model = args[3] if len(args) > 3 else None
        ensure_agent(s, name, model)
        print(f"✓ Agent '{name}' ready in '{s}'")

    elif action == "task":
        s, name, task = args[1], args[2], " ".join(args[3:])
        wait = 30
        result = send_task(s, name, task, wait)
        print(result)

    elif action == "collect":
        s, name = args[1], args[2]
        lines = int(args[3]) if len(args) > 3 else 40
        print(capture(s, name, lines))

    elif action == "status":
        agents = list_agents(args[1])
        for a in agents:
            print(f"  [{a['idx']}] {a['name']}  ({a['cmd']})  {a['cwd']}")

    elif action == "kill":
        kill_session(args[1])
        print(f"✓ Killed '{args[1]}'")

    else:
        print(__doc__)
