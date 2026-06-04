---
name: lobehub-skills-marketplace
description: "Install and manage skills from the LobeHub Skills Marketplace (lobehub.com). Search, install, and rate community skills."
version: 1.0.0
author: agent
triggers:
  - lobehub
  - skill marketplace
  - install skill from url
  - community skill
---

# LobeHub Skills Marketplace

Install skills from https://lobehub.com — 100,000+ community skills.

## Prerequisites

```bash
# npm is needed (already installed with Hermes)
which npm  # verify
```

## Register (one-time)

The credentials are stored at `~/.lobehub-market/credentials.json`. If already registered, the CLI returns existing credentials.

```bash
npx -y @lobehub/market-cli register \
  --name "<unique-bot-name>" \
  --description "<short description of this agent>" \
  --source open-claw
```

**Rate limit:** 5 attempts per 30 min per IP. Don't retry in tight loops.

## Search

```bash
# LobeHub CLI search
npx -y @lobehub/market-cli skills search --q "3D printing"
npx -y @lobehub/market-cli skills search --q "multi agent"

# For broader web search, use the web_search tool directly:
# web_search(query="site:lobehub.com skills <keyword>")
```

## Install

```bash
# Single skill — installs to ~/.agents/skills/<id>/
npx -y @lobehub/market-cli skills install <skill-identifier>

# With version pin
npx -y @lobehub/market-cli skills install <identifier> --version 1.0.4

# Install for specific platform
npx -y @lobehub/market-cli skills install <id> --agent open-claw   # ~/.openclaw/skills/
npx -y @lobehub/market-cli skills install <id> --agent claude-code # ./.claude/skills/
npx -y @lobehub/market-cli skills install <id> --agent codex       # ./.agents/skills/
npx -y @lobehub/market-cli skills install <id> --agent cursor      # ./.cursor/skills/
```

## Install from URL / skill page

When given a LobeHub skill URL like `https://lobehub.com/skills/<identifier>/skill.md`:

```bash
# Fetch the skill.md content (SearXNG can't extract, must use curl)
curl -sL "https://lobehub.com/skills/<identifier>/skill.md" | head -100

# Install by identifier
npx -y @lobehub/market-cli skills install <identifier>
```

## Batch Installation (when user says "all" or "alle")

When the user wants multiple skills installed, do NOT ask per-skill. Collect identifiers and install in parallel:

```bash
# Batch install in parallel
npx -y @lobehub/market-cli skills install skill-a 2>&1 &
npx -y @lobehub/market-cli skills install skill-b 2>&1 &
npx -y @lobehub/market-cli skills install skill-c 2>&1 &
wait
echo "All done"
```

Then read each SKILL.md and follow its instructions.

## Update

```bash
npx -y @lobehub/market-cli skills update <identifier>
```

## List Installed

```bash
ls ~/.agents/skills/           # Default install location
ls ~/.openclaw/skills/         # OpenClaw platform
ls ~/.hermes/skills/           # Hermes platform (manual copy required)
```

**Note:** LobeHub CLI installs to `~/.agents/skills/` by default, NOT `~/.hermes/skills/`. Move if needed:
```bash
cp -r ~/.agents/skills/<name> ~/.hermes/skills<category>/
```

## Pitfalls

- **Some search results don't install** — Skills like `daily-news-report` and `daily-logs` appear in LubeHub web search but return "Skill not found" via CLI. They may be GitHub-only (not uploaded to LobeHub marketplace). Fall back to `npx skills add` or manual git clone for these.
- **`web_extract` doesn't work for lobehub.com`** — SearXNG is search-only and cannot extract URL content. Always use `curl -sL <url>` to fetch skill markdown content.
- **Register rate limit** — 5 attempts per 30 minutes per IP. Don't retry in tight loops.
- **Skills may be platform-specific** — Some skills target Claude Code, Codex, or Cursor specifically. Check the skill's compatibility before relying on it.
- **Not all skills are Hermes-compatible** — Some use tool names or APIs that don't exist in Hermes. Read the SKILL.md and adapt as needed.
- **pip installs may need `--break-system-packages`** — On managed Python installs (Ubuntu 23.10+, Debian 12+), `pip install` without `--break-system-packages` is blocked. Add the flag or use `pipx`.