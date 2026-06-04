---
name: hermes-gateway-troubleshooting
description: "Troubleshoot and fix Hermes gateway platform connections — Discord, Telegram, Slack, and other messaging platforms. Covers token configuration, allowlists, connection failures, and platform-specific quirks."
metadata:
  hermes:
    tags: [hermes, gateway, discord, telegram, slack, troubleshooting, configuration]
---

# Hermes Gateway Troubleshooting

Diagnose and fix gateway connection issues for messaging platforms and related services.

## Quick Diagnosis

```bash
hermes gateway status          # Check if gateway is running
hermes gateway run             # Start in foreground to see errors
```

If the gateway is running but a platform isn't connecting, check the process output:

```bash
hermes gateway run > /tmp/hermes-gateway.log 2>&1 &
sleep 15
cat /tmp/hermes-gateway.log
```

Look for lines containing `[PlatformName]`, `failed to connect`, `No bot token`, or `Unauthorized user`.

## Platform Token Configuration

### Critical: Tokens in .env vs config.yaml

Many platform adapters read credentials from `~/.hermes/.env` (or `~/.hermes/.env`),
**NOT** from `config.yaml`. Even if a token appears in `config.yaml` under the platform section, the adapter may ignore it.

**Always set tokens in BOTH places:**

```bash
# config.yaml — structural metadata (application_id, user_id, enabled, etc.)
hermes config set discord.token YOUR_TOKEN

# .env — actual secrets the adapters read at runtime
echo "DISCORD_BOT_TOKEN=YOUR_TOKEN" >> ~/.hermes/.env
```

### Platform-Specific .env Variables

| Platform | .env Variable | config.yaml Key |
|----------|--------------|-----------------|
| Discord | `DISCORD_BOT_TOKEN` | `discord.token` |
| Telegram | `TELEGRAM_BOT_TOKEN` | `telegram.token` |
| Slack | `SLACK_BOT_TOKEN` | `slack.token` |

**Note on Discord:** The Discord adapter reads the token from `config.yaml` (`discord.token`). You do NOT need `DISCORD_BOT_TOKEN` in `.env` unless you have a specific reason. Most setups work with the token in `config.yaml` only.

### Deprecated .env Variables

Hermes warns about `TERMINAL_CWD` in `.env`. Unset from shell environment:

```bash
unset TERMINAL_CWD
```

Also remove any active (uncommented) `TERMINAL_CWD=` lines from `~/.hermes/.env`.

## Gateway Allowlist Configuration

By default, the gateway denies all unauthorized users. You must configure allowlists:

### Per-Platform Allowlists (Recommended)

Add to `~/.hermes/.env`:

```bash
DISCORD_ALLOWED_USERS=your_discord_user_id
TELEGRAM_ALLOWED_USERS=your_telegram_user_id
SLACK_ALLOWED_USERS=your_slack_user_id
```

### Open Access (Development Only)

```bash
GATEWAY_ALLOW_ALL_USERS=true
```

⚠️ Never use `GATEWAY_ALLOW_ALL_USERS=true` in production — anyone with the bot link can trigger your agent.

## Discordspecific Quirks

### Application ID vs User ID

- `application_id` — your Discord application's client ID (found in Developer Portal → General Information)
- `user_id` — your own Discord user ID (for allowlist and identification)
- Both go in `config.yaml` under `discord:`

### Discord Developer Portal Settings

Ensure these are enabled under Bot → Privileged Gateway Intents:
- **Message Content Intent** — required for the bot to read message content
- **Server Members Intent** — required for member-related features

### Token Regeneration

If a token is exposed in chat or logs, regenerate it immediately in the Discord Developer Portal → Bot → Reset Token. Then update both `config.yaml` and `.env`.

## Discord Mention & Channel Configuration

### require_mention + free_response_channels

By default `require_mention: true` — the bot ONLY responds when @mentioned. To allow free-form conversation in specific channels:

```yaml
discord:
  require_mention: false
  free_response_channels: "channel_id_1,channel_id_2"
```

How the combination works:

| require_mention | free_response_channels | Behavior |
|---|---|---|
| `true` | empty | Bot responds ONLY when @mentioned, in all channels |
| `true` | set | Same as above — `free_response_channels` is IGNORED when `require_mention: true` |
| `false` | empty | Bot responds to ALL messages in ALL channels (no mention needed anywhere) |
| `false` | set | Bot responds to ALL messages in listed channels, requires @mention in all OTHER channels |

Common mistake: setting `require_mention: true` with empty `free_response_channels` — bot stays silent everywhere unless @mentioned. Users think the bot is broken when they're just not @mentioning it.

### allowed_channels

Restricts which channels the bot can see at all. Empty = bot sees all channels it has access to.

```yaml
discord:
  allowed_channels: "channel_id_1,channel_id_2"  # bot ignores everything else
```

## Common Errors

### `[Discord] No bot token configured`
Token not found in environment. Add `DISCORD_BOT_TOKEN` to `.env` and restart gateway.

### `Unauthorized user: <id> (<name>) on discord`
User not in allowlist. Add their ID to `DISCORD_ALLOWED_USERS` in `.env`.

### `Gateway started with no connected platforms`
All platforms failed to connect. Check individual platform errors above. Common causes:
- Missing tokens in `.env`
- Invalid/expired tokens
- Network connectivity issues

### WARNING: `No user allowlists configured`
Gateway is running but no allowlists are set. Set per-platform `ALLOWED_USERS` in `.env`.

### Discord Developer Portal: "Instant invite not supported"

If the OAuth2 URL Generator says "not supported for this type of application", the app is likely set to **User Install** instead of **Guild Install**. User-installable apps cannot generate traditional bot invite links.

**Fix:**
1. Go to Developer Portal → Application → Information
2. Under **Install Link**, ensure it's set to **Guild Install** (not User Install)
3. If stuck on User Install, you may need to recreate the application from scratch

**Required settings for bot invites to work:**
- **Public Bot**: ON (Bot page)
- **Requires OAuth2 Code Grant**: OFF (Bot page)
- **Redirect URI**: Add at least one (e.g., `http://localhost:3000`) under OAuth2 → Redirects — saves the app configuration
- **Privileged Gateway Intents**: Enable all three — Message Content, Server Members, Presence (Bot page)

### Discord Voice Setup

For voice channel support (join, speak, listen via STT/TTS):

1. In OAuth2 URL Generator, add scopes: `bot`, `applications.commands`, `voice`, `messages.read`
2. Permissions: `Administrator` (or manually: Connect, Speak, Read Messages, Send Messages, Read Message History)
3. The bot needs `discord.py[voice]` installed — check with `pip show discord.py`
4. STT pipeline: Whisper local (base/medium) for transcription. TTS: Edge TTS (default, free) for voice output.
5. Hermes voice config: `voice.enabled: true` (default), STT provider, TTS provider — see `stt:` and `tts:` sections in config.yaml

## Gateway Process Management on WSL

`hermes gateway restart` often times out on WSL (foreground process, no systemd). Use this pattern instead:

```bash
# Stop the running gateway
hermes gateway stop

# Start fresh — use terminal(background=true) in Hermes tools:
# terminal(background=true, command="hermes gateway run --replace", notify_on_complete=true)
```

`--replace` auto-kills any existing gateway process for the profile. Without it, you get "Gateway already running" error.

**Do NOT use** shell-level background wrappers (`nohup`, `&`, `disown`) — Hermes blocks these. Use `terminal(background=true)` so Hermes can track the process lifecycle.
