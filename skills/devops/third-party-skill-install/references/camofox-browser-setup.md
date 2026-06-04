# Camofox-Browser Installation Pattern

Camofox-browser is a multi-component setup: Python library + Node.js REST server + bash wrapper CLI.
It does NOT work as a simple `pip install` or `npx` install.

## Components

1. **Python**: `pip install camoufox` (provides the anti-detection Firefox-fork browser binary)
2. **Node.js server**: `@askjo/camofox-browser` (REST API wrapper for browser automation)
3. **Bash CLI wrapper**: `camofox.sh` in the skill's `scripts/` directory

## Installation Steps

```bash
# Step 1: Install Python dependency
pip install --break-system-packages camoufox  # or use a venv

# Step 2: Run skill setup script (installs Node.js server + creates state dirs)
bash ~/.hermes/skills/camofox-browser/scripts/setup.sh

# Step 3: Make CLI wrapper available in PATH
chmod +x ~/.hermes/skills/camofox-browser/scripts/camofox.sh
ln -sf ~/.hermes/skills/camofox-browser/scripts/camofox.sh ~/bin/camofox

# Step 4: Verify
camofox health
```

## Verification

Health check returns JSON:
```json
{"ok":true,"engine":"camofox","browserConnected":true,"activeTabs":0}
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CAMOFOX_PORT` | 9377 | Server port |
| `CAMOFOX_SESSION` | default | Session name |
| `CAMOFOX_HEADLESS` | true | Headless mode |
| `HTTPS_PROXY` | — | Proxy for anti-detection |

## Troubleshooting

- **Server won't start**: Check Node.js >= 18: `node -v`
- **Browser download hangs**: First launch downloads ~300MB Camoufox binary. Wait up to 2 min.
- **Port conflict**: Change `CAMOFOX_PORT` before starting.
- **Still getting blocked**: Use `HTTPS_PROXY=socks5://127.0.0.1:1080 camofox open <url>`
