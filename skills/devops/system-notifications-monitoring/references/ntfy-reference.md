# ntfy CLI & API Reference

## Installation

```bash
curl -fsSL "https://github.com/binwiederhier/ntfy/releases/download/v2.23.0/ntfy_2.23.0_linux_amd64.deb" -o /tmp/ntfy.deb
sudo dpkg -i /tmp/ntfy.deb
```

## CLI Syntax (v2.x)

ntfy v2 uses subcommands. The old `ntfy <topic> --poll` syntax does NOT work.

### Subscribe (listen for messages)

```bash
# Subscribe and print messages as they arrive (long-poll, blocks until message)
ntfy subscribe mytopic

# Subscribe with extra fields (ID, timestamp, etc.)
ntfy subscribe mytopic --poll

# Specific server
ntfy subscribe mytopic --server https://ntfy.sh
```

**IMPORTANT:** `ntfy subscribe` is a long-running command that blocks until messages arrive. Use `terminal(background=true)` for it. There is no non-blocking "check now and exit" mode -- the CLI is pub/sub only.

### Publish

```bash
ntfy publish mytopic "Message"
ntfy publish mytopic "Message" --title "Title" --priority 4 --tags warning
```

### NO message history API (free tier)

ntfy.sh free tier delivers messages in real-time only. There is NO way to retrieve past messages:
- `ntfy subscribe` only gets NEW messages arriving after you connect
- The HTTP long-poll endpoint (`/json?poll=1`) also only waits for new messages -- it does not return old ones
- If you weren't subscribed when a message was sent, it's gone
- Self-hosted ntfy with `message-cache` enabled *does* support history (add `?since=<timestamp>`)

Workaround for audit trail: have scripts log alerts to a local file before/after pushing to ntfy.

## Publishing via curl (recommended for scripts)

```bash
# Simple
curl -s -X POST "https://ntfy.sh/mytopic" -d "Hello"

# With options
curl -s -X POST "https://ntfy.sh/mytopic" \
    -H "Title: My Title" \
    -H "Priority: 4" \
    -H "Tags: warning,computer" \
    -d "Message body"

# Priority: 1=min 2=low 3=default 4=high 5=max
```

**Note:** ntfy CLI can mangle flags with dashes. Use curl directly for reliable scripting.

## Topics

Topics auto-created on first publish. No registration.
- Subscribe in app: enter topic name
- Web UI: `https://ntfy.sh/mytopic`

## Rate Limits (public ntfy.sh)

- Messages: 30/15 min per visitor
- For higher limits: self-host via Docker

## Hermes Topic Map

| Topic | Purpose | Priority |
|-------|---------|----------|
| `hermes-alerts` | System health + security issues | 4 (high) |
| `hermes-heartbeat` | Daily alive signal | 2 (low) |
| `hermes-security` | Dedicated security alerts | 4+ when critical |
