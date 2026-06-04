# WSL2 Ubuntu CLI Tool Installation — Quick Reference

## Cargo (Rust) Tools — Timeout Prevention

Large Rust crates (aichat, bottom, dust) take 2-8 minutes to compile. **Always use background execution** with `background=true, notify_on_complete=true` in the Hermes terminal tool. Foreground timeout is max 600s which may not be enough.

## Ollama Install on Ubuntu/WSL2

```bash
# 1. Install zstd FIRST (required by ollama installer)
sudo apt-get install -y zstd

# 2. Download installer (don't pipe curl to sh — save first)
curl -fsSL https://ollama.com/install.sh -o /tmp/ollama_install.sh
sudo bash /tmp/ollama_install.sh

# 3. If systemd service doesn't auto-enable:
sudo systemctl daemon-reload
sudo systemctl enable --now ollama
```

## bat → batcat Symlink (Debian/Ubuntu)

```bash
sudo ln -sf /usr/bin/batcat /usr/local/bin/bat
```

## ntfy Install

Use `.deb` from GitHub releases (not tar.gz — easier):
```bash
curl -fsSL "https://github.com/binwiederhier/ntfy/releases/download/v<VERSION>/ntfy_<VERSION>_linux_amd64.deb" -o /tmp/ntfy.deb
sudo dpkg -i /tmp/ntfy.deb
```

## Norwegian Retailer Scraping Status (2026-06-03)

| Retailer | Scrapable? | Method |
|----------|-----------|--------|
| komplett.no | Yes | Camoufox direct product pages |
| proshop.no | Partial | Camoufox, search pages may not render |
| prisjakt.no | No | Blocks all bot requests |
| finn.no | No | Blocks all bot + browser automation |

For blocked retailers: use `web_search` with `site:<retailer>` then ask user to verify.
