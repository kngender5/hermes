#!/usr/bin/env python3
"""
tmux_agent.py - Spawn Hermes agent sessions in new tmux panes/windows

Actions:
  create   <session>                Create tmux session
  add      <session> <name> [cmd]  Add agent window (default: interactive hermes)
  send     <session> <name> <msg>  Send message to agent pane
  capture  <session> <name> [n]    Capture last n lines of output
  list     <session>               List windows
  kill     <session>               Kill session

If no cmd given for 'add', spawns interactive `hermes` in the pane.
"""
import subprocess, sys, os, time, json

TMUX = "tmux"

def tmux_run(*args):
    r = subprocess.run([TMUX] + list(args), capture_output=True, text=True)
    return r.stdout.strip(), r.returncode

def has_session(s):
    _, rc = tmux_run("has-session", "-t", s)
    return rc == 0

def create(s, cwd=None):
    if has_session(s): return False
    args = ["new-session", "-d", "-s", s, "-x", "180", "-y", "45"]
    if cwd: args += ["-c", cwd]
    tmux_run(*args)
    return True

def add_window(s, name, cmd=None, cwd=None):
    if not has_session(s): create(s, cwd)
    tmux_run("new-window", "-t", s, "-n", name)
    if cmd:
        tmux_run("send-keys", "-t", f"{s}:{name}", cmd, "Enter")
    return True

def add_interactive(s, name, cwd=None, hermes_args=""):
    """Spawn interactive Hermes CLI in a new tmux window."""
    cmd = f"hermes {hermes_args} 2>&1 | cat".strip()
    return add_window(s, name, cmd, cwd)

def send_keys(s, name, text):
    tmux_run("send-keys", "-t", f"{s}:{name}", text, "Enter")

def capture(s, name, lines=40):
    tmux_run("capture-pane", "-t", f"{s}:{name}", "-p", "-S", f"-{lines}")
    out, _ = tmux_run("capture-pane", "-t", f"{s}:{name}", "-p", "-S", f"-{lines}")
    return out

def list_windows(s):
    out, rc = tmux_run("list-windows", "-t", s,
                       "-F", "#{window_index}|#{window_name}|#{pane_current_command}|#{pane_current_path}")
    if rc != 0: return []
    wins = []
    for line in out.splitlines():
        p = line.split("|")
        if len(p) >= 4:
            wins.append({"idx": p[0], "name": p[1], "cmd": p[2], "cwd": p[3]})
    return wins

def kill(s):
    tmux_run("kill-session", "-t", s)

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(0)

    action = args[0]

    if action == "create":
        s = args[1]; cwd = args[2] if len(args) > 2 else None
        create(s, cwd); print(f"✓ Created session '{s}'")

    elif action == "add":
        s, name = args[1], args[2]
        cmd = " ".join(args[3:]) if len(args) > 3 else None
        add_window(s, name, cmd)
        print(f"✓ Added window '{name}' in '{s}'")

    elif action == "interactive":
        s, name = args[1], args[2]
        ha = " ".join(args[3:]) if len(args) > 3 else ""
        add_interactive(s, name, hermes_args=ha)
        print(f"✓ Added interactive hermes '{name}' in '{s}'")

    elif action == "send":
        s, name, msg = args[1], args[2], " ".join(args[3:])
        send_keys(s, name, msg)
        print(f"✓ Sent to '{name}'")

    elif action == "capture":
        s, name = args[1], args[2]
        n = int(args[3]) if len(args) > 3 else 40
        print(capture(s, name, n))

    elif action == "list":
        wins = list_windows(args[1])
        for w in wins:
            print(f"  [{w['idx']}] {w['name']}  ({w['cmd']})  {w['cwd']}")

    elif action == "kill":
        kill(args[1]); print(f"✓ Killed '{args[1]}'")

    else:
        print(f"Unknown action: {action}")
