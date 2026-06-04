---
name: third-party-skill-install
description: Install third-party skills/agents/tools from GitHub repos and other sources into Hermes Agent's skill library (~/.hermes/skills/). Use when the user wants to install skills from a GitHub URL, npx skills add, git clone, or any external source into the Hermes skills directory.
---

# Third-Party Skill Installation for Hermes

Hermes skills live in `~/.hermes/skills/<category>/<skill-name>/` or `~/.hermes/skills/<skill-name>/`. External repos use different structures — adapt the install approach per repo.

## Installation Methods

### Method 1: `npx skills add` (vercel-labs/agent-skills)

The `npx skills` CLI installs to `~/.agents/skills/` by default. It does **NOT** support a `--target` flag — any `--target ~/.hermes/skills` argument is silently ignored.

```bash
# This does NOT install to ~/.hermes/skills:
npx skills add owner/repo --target ~/.hermes/skills  # WRONG — ignores --target
```

**Correct approach when `npx skills` is wanted (installs to `~/.agents/skills/`):**
```bash
npx skills add owner/repo
```

For Hermes, prefer Method 2 instead.

### Method 1: LobeHub Skills Marketplace (preferred for community skills)

**This is the fastest method — no GitHub auth needed.** See the dedicated `lobehub-skills-marketplace` skill for full details, and [references/lobehub-marketplace.md](references/lobehub-marketplace.md) for verified identifiers and session notes. Quick reference:

```bash
# One-time register
npx -y @lobehub/market-cli register --name "<name>" --description "<desc>" --source open-claw

# Search + install
npx -y @lobehub/market-cli skills search --q "keyword"
npx -y @lobehub/market-cli skills install <identifier>

# Batch install (parallel)
npx -y @lobehub/market-cli skills install skill-a 2>&1 &
npx -y @lobehub/market-cli skills install skill-b 2>&1 &
wait
```

Installs to `~/.agents/skills/` by default. Move to `~/.hermes/skills/` if needed.
```bash
cd /tmp && git clone https://github.com/owner/repo.git

# Inspect repo structure first:
ls repo/
ls repo/skills/ 2>/dev/null   # Case A: has skills/ subdir
# or                          # Case B: SKILL.md at root + sub-packs
find repo -name "SKILL.md" | head -10
```

**Case A — Repo has `skills/` subdir** (e.g. felo-skills, taste-skill, seo-geo-claude-skills):
```bash
for dir in /tmp/repo/skills/*/; do
  name=$(basename "$dir")
  cp -r "$dir" ~/.hermes/skills/${PREFIX}-${name}
done
```

Use a prefix (f-, taste-, seo-geo-) when the skill names are generic or may collide.

**Case B — SKILL.md at root with sub-pack directories** (e.g. playwright-skill):
```bash
# Copy root as a whole skill
cp -r /tmp/repo ~/.hermes/skills/repo-name

# Also copy sub-packs as standalone skills
for dir in /tmp/repo/core /tmp/repo/ci /tmp/repo/pom; do
  pack=$(basename "$dir")
  cp -r "$dir" ~/.hermes/skills/${repo-name}-${pack}
done
```

**Case C — Single SKILL.md at root, no sub-packs:**
```bash
mkdir -p ~/.hermes/skills/skill-name
cp /tmp/repo/SKILL.md ~/.hermes/skills/skill-name/
# Also copy any references/, templates/, scripts/ dirs
cp -r /tmp/repo/references ~/.hermes/skills/skill-name/ 2>/dev/null
```

### Method 3: `bash install-hermes.sh` (repo provides its own installer)

Some repos (e.g. felo-skills) ship an `install-hermes.sh` script. It typically needs the repo root as an argument:

```bash
cd /tmp && git clone https://github.com/owner/repo.git
bash repo/scripts/install-hermes.sh /path/to/repo-root
```

If the script errors with "Cannot find skills", pass the repo root path explicitly — `SCRIPT_DIR` resolves to the `scripts/` subdirectory.

## Repo Structure Detection

Before copying, inspect the repo to determine which case applies:

```bash
# Check for skills/ directory
ls /tmp/repo/skills/ 2>/dev/null && echo "HAS skills/ subdir"

# Check for SKILL.md at root
ls /tmp/repo/SKILL.md 2>/dev/null && echo "HAS root SKILL.md"

# Check for install script
ls /tmp/repo/scripts/install-hermes.sh 2>/dev/null && echo "HAS installer"

# Full search
find /tmp/repo -name "SKILL.md" -o -name "install-hermes.sh" | head -10
```

### Method 4: pip/CLI tool + SKILL.md from GitHub raw

Some skills are both a CLI tool (pip/npm) and a SKILL.md file hosted on GitHub. Common pattern for OSINT tools:

```bash
# Step 1: Install the CLI tool
pip install --break-system-packages <package>
# or: pipx install <package>

# Step 2: Fetch SKILL.md from GitHub raw
mkdir -p ~/.hermes/skills/security/<tool-name>
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/main/optional-skills/security/<tool-name>/SKILL.md" \
  > ~/.hermes/skills/security/<tool-name>/SKILL.md
```

**Verified examples:**
- Sherlock: `pip install --break-system-packages sherlock-project` + SKILL.md from `NousResearch/hermes-agent/main/optional-skills/security/sherlock/SKILL.md`
- The SKILL.md lives in the Hermes repo under `optional-skills/`, not in the tool's own repo

After installing, verify with `<tool> --version` and read the SKILL.md.

## Pitfalls

- **Shell redirect in git clone args**: `git clone URL dir1 dir2` — the second path argument is NOT a second clone target. In some contexts `dir2` can be interpreted as a redirect target. Always use exactly two positional args: URL + dest.
- **Subagent naming/encoding**: When subagents write skill files, Norwegian chars (ÆØÅ) may be corrupted in transport (Ø→OER, Å→AA). Always verify output encoding after delegation.
- **Name collisions**: If a skill name already exists, the copy will overwrite. Check first with `ls ~/.hermes/skills/<name>` or use a prefix.
- **`npx skills add --target`**: This flag does NOT exist in `vercel-labs/agent-skills`. The CLI always installs to `~/.agents/skills/`. Use manual copy for Hermes.
- **GitHub PAT auth for git clone**: When `GITHUB_TOKEN` is set in `~/.hermes/.env` (auto-loaded by Hermes), `gh auth login --with-token` will REFUSE to store credentials and print "The value of the GITHUB_TOKEN environment variable is being used for authentication." It reads the env var instead of the stdin token. Workaround: use `execute_code` (Python subprocess) with `GITHUB_TOKEN` cleared from env, or set up git credential.helper store manually.
- **GitHub PAT shell-quoting hazard**: Tokens like `github_pat_XX...` contain characters (`/`, `$`, spaces) that break bash single-quotes, `$()`, `<<<` heredoc, `<<< 'EOF'` variants, `echo '...'|`, and `--with-token` variants. DO NOT try to pass PATs through shell constructs. Use `execute_code` (Python) to read the `.env` token and invoke git clone with token embedded in the URL:

## LobeHub CLI (Alternative GitHub-free install path)

When `npx skills add` / `git clone` fail due to missing GitHub auth, use the LobeHub Marketplace CLI:

```bash
# Register (one-time, rate-limited 5 per 30 min per IP):
npx -y @lobehub/market-cli register \
  --name "<AgentName>" \
  --description "<description>" --source open-claw

# Install skills (no GitHub auth needed):
npx -y @lobehub/market-cli skills install <skill-identifier>

# Search:
npx -y @lobehub/market-cli skills search --q "<keyword>"
```

- Credentials stored at `~/.lobehub-market/credentials.json`
- Works without `gh auth login`, `GITHUB_TOKEN`, or SSH keys
- Larger library than GitHub-sourced skills; many skills exist ONLY here
- `daily-news-report` and `daily-logs` are NOT on LobeHub (GitHub-only)
- Some skill identifiers differ from LobeHub web slugs — search by name if slug fails

## Camoufox for Norwegian Retailers

Norwegian retailers (Komplett, Proshop, Prisjakt) block standard HTTP requests with Cloudflare/bot detection. Use Camoufox:

```bash
camofox open "https://www.komplett.no/search?q=<product>"
camofox snapshot | grep -i 'pris\|kr\|lager'
```

- Komplett: Shows products after cookie consent; use category pages instead of search for better results
- Proshop: Blocks with Cloudflare challenge page — Camoufox bypasses this
- Prisjakt: Returns 403 for API; use Camoufox for product scraping
  ```python
  # In execute_code:
  import subprocess, os
  env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
  result = subprocess.run(["git", "clone", f"https://{token}@github.com/owner/repo", "/tmp/repo"], env=env, ...)
  ```
  This is the only reliable method when `GITHUB_TOKEN` is already in `.env` and `gh` CLI refuses stdin auth.
- **`~/.hermes/.env` is protected**: `read_file`, `write_file`, and `patch` all block writes to `~/.hermes/.env`. To add tokens, use `hermes config edit`, `hermes config set`, or tell the user to run `echo 'KEY=value' >> ~/.hermes/.env` in their terminal.
- **`web_extract` backend**: The default SearXNG backend is search-only and cannot extract URL content (`HTTP 400`). For `web_extract`, `web_search` with `site:` operators can sometimes substitute. For full extraction, set `web.extract_backend` to `firecrawl`, `tavily`, or `exa` in config. As fallback, use `curl -sL <url>` + text processing, or use the `browser` tool.

## Multi-Component Skills

Some skills require more than a `git clone + copy`. See [references/camofox-browser-setup.md](references/camofox-browser-setup.md) for the camofox-browser pattern: Python package + Node.js REST server + bash CLI wrapper, all orchestrated by a setup script.
