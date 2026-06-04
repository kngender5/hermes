# LobeHub Marketplace — Session Notes

## Verified Install Results (2026-06-01)

40+ skills installed from LobeHub. Key patterns:

### Installed to `~/.agents/skills/`
LobeHub default — move to `~/.hermes/skills/` if Hermes-native needed:
```bash
cp -r ~/.agents/skills/<name> ~/.hermes/skills/<category>/
```

### Failed installs
These identifiers appear in web search but NOT in CLI:
- `sickn33-antigravity-awesome-skills-daily-news-report` → "Skill not found"
- `memodb-io-acontext-daily-logs` → "Skill not found"
- `tylersahagun/pm-workspace` → GitHub auth required (private)

### LobeHub CLI
- Register: `npx -y @lobehub/market-cli register --name "..." --source open-claw`
- Credentials: `~/.lobehub-market/credentials.json`
- Rate limit: 5 register attempts per 30 min per IP
- Identifier format: all lowercase, hyphens (e.g. `openclaw-skills-lofy`)

### web_extract does NOT work for lobehub.com
SearXNG is search-only. For skill.md content, use:
```bash
curl -sL "https://lobehub.com/skills/<identifier>/skill.md"
```
