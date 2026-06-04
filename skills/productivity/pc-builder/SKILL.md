---
name: pc-builder
description: "Build, configure, and recommend PC hardware — custom desktops, laptops, workstations, and pre-built alternatives. Handle component selection, compatibility checking, price comparison across Norwegian and international retailers, and build optimization for specific use cases (gaming, music production, office, AI/ML). Triggered by: build a PC, PC build, recommend hardware, upgrade computer, kjøpe PC, bygge PC, kjøpe laptop, anbefal hardware."
---

# PC Build & Hardware Recommendation

Configure custom PCs, recommend hardware, compare prices across retailers, and optimize builds for specific use cases.

## Workflow

1. **Gather requirements** — Use cases, budget, must-haves (optical drive, USB4, etc.)
2. **Select components** — Match components to requirements and each other
3. **Check compatibility** — Socket, chipset, RAM type, PSU wattage, case clearance
4. **Price comparison** — Norwegian retailers (Komplett, Proshop) via Camoufox
5. **Alternative check** — Consider pre-builts (ThinkCentre, etc.) when cheaper
6. **Present build** — Component table with prices and links

## Key Principles

- **Right-size the GPU**: Office/music/browsing → integrated graphics fine. Gaming → match resolution. AI/ML → NVIDIA only (CUDA).
- **Don't overshoot PSU**: No dGPU = 650-750W. Single dGPU = 750-850W. Dual GPU = 1000W+.
- **DDR5 price crisis**: Prices ~4x since Sept 2025 (AI demand). Wait, buy used, or start 16GB.
- **Optical drives**: Rare in modern cases. Cooler Master CM695 is one option. Most pre-builts still have them.
- **Pre-built alternative**: Lenovo ThinkCentre M-series, Dell OptiPlex, HP ProDesk — often cheaper with Windows license included.
- **Listen to user hints**: If the user mentions a specific product (e.g. "ThinkCentre M70t"), treat it as a strong signal to evaluate that option, not ignore it.

## Scraping Norwegian Retailers (Camoufox)

Norwegian retailers block standard HTTP/bot detection. Use `camofox` for price scraping:

### Working Technique (discovered 2026-06-02)

**Direct product pages work better than search.** Search results often require cookie consent before showing prices. Navigate directly to product URLs when possible.

```bash
# Start camofox
camofox start

# Navigate directly to known product page
camofox open "https://www.komplett.no/product/<PRODUCT_ID>/path"
sleep 3

# Get snapshot and extract prices
camofox snapshot | grep -oP '[\d]{1,3}(?:[\s.])?[\d]{3}(?=,-| kr)'

# Clean up
camofox close
camofox stop
```

### Camofox Pitfalls
- **Do NOT delegate camofox crawling to subagents** — each subagent gets its own camofox server instance, and multiple instances cause port conflicts and timeouts
- **Sequential crawling is faster** than parallel — use one session, navigate between product pages
- **Cookie consent walls**: Komplett shows cookie banner on first visit. The snapshot will show the banner. Prices still accessible in same snapshot via grep
- **Stealth scrape script path**: Template references `~/.claude/skills/camofox-browser/scripts/camofox.sh` but actual path is `~/bin/camofox`. Use `~/bin/camofox` directly.

### Retailer-Specific Tips

| Retailer | Notes |
|----------|-------|
| komplett.no | Direct product pages work best. Category pages need cookie consent acceptance first |
| proshop.no | Cloudflare-protected. Camoufox works but search pages may not render product listings — use direct product URLs |
| prisjakt.no | Price comparison, but blocks bot requests. Requires full browser rendering |
| finn.no | **Blocks bot scraping completely** — both standard HTTP and browser automation (Camoufox, Playwright) get blocked. Cannot scrape prices programmatically. User must search manually. Good for finding used parts (cases with 5.25" bays, optical drives) — use `web_search` with `site:finn.no` to find listings, then ask user to verify |

### Norwegian Product Search URLs

When product IDs are unknown, use category browsing:
- Komplett category: `https://www.komplett.no/category/<CAT_ID>/path`
- Komplett search: `https://www.komplett.no/search?q=<encoded_name>`
- Better approach: Use `web_search` with `site:komplett.no` to find product pages, then navigate directly

## Reference Files

- [references/pc-build-config.md](references/pc-build-config.md) — Common build configurations, DDR5 crisis, audio interfaces, ThinkCentre M70t specs, compatibility checklist
- [references/wsl2-cli-tools.md](references/wsl2-cli-tools.md) — WSL2 Ubuntu CLI tool install patterns (Ollama, cargo timeout, bat→batcat, ntfy, retailer scraping status)
