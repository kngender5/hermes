User prefers direct and technical responses - skip basic explanations unless asked, prefer CLI solutions over GUI, show full commands (not pseudocode), use Norwegian keyboard layout considerations, metric units, and 24h time format.
§
2026-06-01: llama.cpp local model: Qwen3-14B-128K-Q3_K_M (~6.9GB) at ~/models/Qwen3-14B-128K-Q3_K_M/. Standard Qwen3-14B=40K ctx (below Hermes 64K min) — must use Unsloth 128K variant. RTX 4060 8GB: --n-gpu-layers 20 partial offload. ctx-size 65536, port 18080. hf download CLI: --local-dir only (not Python API flags). Profile config: ~/.hermes/profiles/local/config.yaml — context_length 65536, model default must match /v1/models ID exactly.
§
ntfy.sh topic: hermes-alerts. Helper: ~/bin/ntfy-alert.
§
2026-06-03: Created 3 Hermes profiles: infra, academic, creative — each with SOUL.md, config.yaml, AGENTS.md. Project index at ~/projects/PROJECTS.md. Consolidated 6 cron jobs → 3 (unified security-check.sh, countermeasures hourly, daily report 08:00, heartbeat 12/18). Created devops skills: proxmox-logging, opnsense-logging.
§
2026-06-03: Created devops skills: proxmox-logging (ProxmoxLogger Python class, JSONL logging, error handling patterns, CLI wrapper, task polling, retry with backoff). opnsense-logging (OPNsenseLogger Python class, IDS alert processing, firewall rule manager with validation/batch rollback, VPN event tracking, configctl wrapper).
§
Do NOT delete user scripts/notebooks without explicit instruction. Clarify target env (Colab vs WSL) before writing setup. HF bucket sync: hf sync ./local hf://buckets/kngxne/TRELLIS.2-bucket (upload) or hf sync hf://buckets/kngxne/TRELLIS.2-bucket ./local (download). Can stage files in tempstrg bucket too.
§
2026-06-04: Configured 3 MCP servers: filesystem (14 tools), github (26 tools), puppeteer (7 tools) via hermes mcp add. hermes mcp catalog/picker empty — known limitation, use manual add. server-playwright does NOT exist on npm — use server-puppeteer. Pre-install with npm install -g to avoid npx timeout on first connect.