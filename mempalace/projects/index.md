# Project Index

| Project | Path | Profile |
|---------|------|---------|
| InfraLab | ~/projects/infra-lab/ | infra |
| Study Workbench | ~/projects/study-workbench/ | academic |
| Creative Lab | ~/projects/creative-lab/ | creative |
| Pokemon AI | ~/projects/PokemonGold/ | creative |
| TTS/Voice | ~/projects/qwen3-tts/ | creative |
| PC Build | ~/projects/pc-build/ | creative |
| llama.cpp | ~/projects/llama.cpp/ | local |
| PLC Projects | ~/projects/elevator-plc/ | academic |

## Hermes GitHub Repo
- https://github.com/kngender5/hermes (private)
- Contains: skills, profiles, cron, memories, SOUL.md, config.yaml
- MUST prompt user to update after significant changes
- Update: cd ~/hermes-repo && git add -A && git commit -m "..." && git push
- Or: bash ~/hermes-repo/scripts/sync-hermes.sh

## Pokemon Agent
- Do NOT restart the pokemon-agent server without explicit user permission
- The server holds game state in memory and restarting loses all progress
- If game appears stuck, try different actions before suggesting restart

## HuggingFace Bucket Sync
- hf sync ./local hf://buckets/kngxne/TRELLIS.2-bucket (upload)
- hf sync hf://buckets/kngxne/TRELLIS.2-bucket ./local (download)
- Can stage files in tempstrg bucket too

## MCP Servers Configured
- Filesystem: 14 tools
- GitHub: 26 tools
- Puppeteer: 7 tools
- hermes mcp catalog/picker is empty — known limitation, use manual add
- server-playwright does NOT exist — use server-puppeteer
