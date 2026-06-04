---
name: osint-recon
description: >-
  OSINT identity resolution and cross-platform tracking audit. Use when the user
  asks to investigate a handle, username, email, phone number, or identity across platforms
  including social media presence, domain registration, dev platform accounts, content
  distribution, breach data parsing, and exposure assessment. Triggers include: audit handle,
  OSINT, identity resolution, cross-platform lookup, track username, SOCMINT, investigate
  presence, who is, find accounts, phone lookup, email lookup, breach dump, leak parse,
  normalize data.
---

# OSINT Recon — Identity Resolution & Cross-Platform Audit

## Workflow

1. **Sherlock first** — if `sherlock` is installed (`which sherlock`), run it immediately: `cd /tmp && sherlock --timeout 10 --print-all HANDLE 2>&1 | cat`. This probes 300+ platforms in parallel and is faster than manual probing. Parse `[+]` lines for confirmed presence, `[-]` for absence. Note "Blocked by bot detection" and "Timeout Error" — these need manual follow-up.
2. **Broad discovery** — search handle across all categories (general, social media, it, news)
3. **Direct platform probes** — HTTP status checks on platforms Sherlock couldn't reach (adult platforms, Twitter/X, or sites with bot detection blocks)
4. **Geolocation anchor** — query Chess.com API first (`https://api.chess.com/pub/player/{HANDLE}`) for country code + last_online. This is the fastest high-signal geolocation data point.
5. **Content extraction** — scrape active profiles for metadata, links, emails
6. **Alt-handle discovery** — search name variants, real name, alternate spellings
7. **Domain audit** — check common TLDs, Wayback Machine
8. **Dev platform sweep** — GitHub, GitLab, Bitbucket, dev.to, Medium, Keybase
9. **Phone OSINT** — if phone number available: phoneinfoga + ignorant (see `references/phone-osint.md`)
10. **Email deep-dive** — if email available: holehe + maigret on prefix + Google Dorks + ProtonMail PKS lookup (see `references/email-osint.md`)
11. **Breach data normalization** — if raw text/leak dump provided: parse and normalize (see `references/leak-normalizer.md`)
12. **Cross-reference** — build linkage graph with Graphviz DOT (see `references/graphviz-scheme.md`), compile report

## Search Strategy

### Primary: SearXNG
SearXNG is the primary search backend. Critical quirks:

- **`format=json` triggers HTTP 403** even when `limiter: false` is configured. Always use default HTML format:
  ```
  curl -s "http://localhost:8080/search?q=HANDLE&categories=CAT&pageno=N"
  ```
- Parse results with Python regex (NOT grep — `grep -oP` fails with variable-length lookbehind):
  ```python
  import re, urllib.request
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
  result_urls = re.findall(r'class="url_header"[^>]*href="(https?://[^"]+)"', html)
  result_titles = re.findall(r'<h3><a[^>]+rel="noreferrer"[^>]*>(.*?)</a></h3>', html, re.DOTALL)
  clean_titles = [re.sub(r'<[^>]+>', '', t).strip() for t in result_titles]
  ```
- Categories: `general`, `social+media`, `it`, `news`, `images`, `videos`, `files`
- SearXNG engines can be rate-limited or suspended — results may be intermittent.

### Fallback: DuckDuckGo HTML
When SearXNG returns 0 results or HTTP 403, use DuckDuckGo's HTML endpoint:
```python
import urllib.request, urllib.parse, re
# CRITICAL: DDG HTML requires + for spaces, not %20
# urllib.parse.quote() produces %20 — replace with +
query_encoded = urllib.parse.quote(query).replace('%20', '+')
url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
titles = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
```
DuckDuckGo HTML returns 0 results for truly obscure handles — this is a strong signal of zero web presence.

### Last Resort: Browser
Browser Google search is slow and may time out. Only use when both SearXNG and DDG fail AND the target is high-priority.

### `web_extract` Limitation
`web_extract` does NOT work with SearXNG (search-only backend). Use curl plus regex or the browser.

## Platform Probing

### HTTP Status Checks
Check handle existence across platforms with HEAD or GET requests:

| Platform | URL Pattern |
|----------|------------|
| GitHub | `https://github.com/HANDLE` |
| GitLab | `https://gitlab.com/HANDLE` |
| Bitbucket | `https://bitbucket.org/HANDLE` |
| Replit | `https://replit.com/@HANDLE` |
| CodePen | `https://codepen.io/HANDLE` |
| Stack Overflow | `https://stackoverflow.com/users/HANDLE` |
| HackerRank | `https://www.hackerrank.com/HANDLE` |
| LeetCode | `https://leetcode.com/HANDLE` |
| GeeksforGeeks | `https://auth.geeksforgeeks.org/user/HANDLE` |
| Instagram | `https://www.instagram.com/HANDLE/` |
| X or Twitter | `https://x.com/HANDLE` or `https://twitter.com/HANDLE` |
| Reddit | `https://www.reddit.com/user/HANDLE/` |
| OnlyFans | `https://onlyfans.com/HANDLE` |
| Fansly | `https://fansly.com/HANDLE` |
| JustForFans | `https://justfor.fans/HANDLE` |
| Linktree | `https://linktr.ee/HANDLE` |
| Telegram | `https://t.me/HANDLE` |
| Twitch | `https://www.twitch.tv/HANDLE` |
| Pinterest | `https://www.pinterest.com/HANDLE/` |
| Snapchat | `https://www.snapchat.com/add/HANDLE` |
| TikTok | `https://www.tiktok.com/@HANDLE` |
| YouTube | `https://www.youtube.com/@HANDLE` |
| dev.to | `https://dev.to/HANDLE` |
| Medium | `https://medium.com/@HANDLE` |
| Keybase | `https://keybase.io/HANDLE` |
| Spotify | `https://open.spotify.com/user/USERID` |
| Facebook | `https://www.facebook.com/HANDLE` |
| VSCO | `https://vsco.co/HANDLE` |
| Tumblr | `https://HANDLE.tumblr.com` |
| SoundCloud | `https://soundcloud.com/HANDLE` |
| Steam | `https://steamcommunity.com/id/HANDLE` |
| Discord invite | `https://discord.gg/HANDLE` |
| Discord user | `https://discord.com/users/HANDLE` |
| Flickr | `https://www.flickr.com/people/HANDLE/` |
| Dribbble | `https://dribbble.com/HANDLE` |
| Behance | `https://www.behance.net/HANDLE` |
| DeviantArt | `https://www.deviantart.com/HANDLE` |
| Etsy | `https://www.etsy.com/shop/HANDLE` |
| Redbubble | `https://www.redbubble.com/people/HANDLE` |
| Patreon | `https://www.patreon.com/HANDLE` |
| Substack | `https://HANDLE.substack.com` |
| Gravatar | `https://en.gravatar.com/HANDLE` |
| GitHub Gist | `https://gist.github.com/HANDLE` |
| FINN.no | `https://www.finn.no/typo/HANDLE` |

HTTP 200, 301, 302 = likely exists. 404 = not found. 403 = blocked but may still exist.

### JS-Rendered SPAs
Instagram, TikTok, Snapchat, OnlyFans, and similar SPAs return empty shells via curl. Use these alternatives:

- **Reddit**: Append `.json` to any URL (for example `reddit.com/user/HANDLE/about.json`, `reddit.com/user/HANDLE/submitted.json`)
- **Spotify**: OG tags in HTML contain display name and description
- **Telegram**: OG tags show title, description, type (channel vs user)
- **Nitter** (Twitter mirror): As of 2026-06, ALL major public Nitter instances are non-functional (403, 404, or DNS failure). Tested: nitter.net (404), nitter.poast.org (403), nitter.1d4.us (DNS fail). Do NOT rely on Nitter for Twitter/X intelligence. If you must check Twitter, use the browser tool or note as "unverifiable".
- **Instagram**: Try `?__a=1&__d=dis` JSON endpoint (often blocked). OG tags may have partial data.
- **Linktree**: OG title and description plus extract `"url":"..."` JSON patterns for linked platforms

### DNS and Domain Checks
When `dig` and `host` are unavailable, use Python:
```python
import socket
try:
    ip = socket.gethostbyname("handle.com")
    print(f"Resolves to {ip}")
except socket.gaierror:
    print("NXDOMAIN")
```

### Wayback Machine
```bash
# CDX API — list archived URLs
curl -s "https://web.archive.org/cdx/search/cdx?url=handle.com*&output=text&limit=20&fl=original,timestamp"

# Check specific URL snapshots
curl -s "https://web.archive.org/web/2024*/https://instagram.com/handle"
```

## Content Extraction Patterns

### Email Discovery
```python
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
# Filter out false positives
real = [e for e in set(emails) if not any(x in e for x in [
    'example.com', 'sentry', 'w3.org', 'schema.org', 'localhost',
    'dmca@', 'noreply@', 'no-reply@'
])]
```

### Social Handle Extraction from Page Content
```python
patterns = [
    (r'instagram\.com/([A-Za-z0-9_.]+)', 'Instagram'),
    (r'x\.com/([A-Za-z0-9_]+)', 'X'),
    (r't\.me/([A-Za-z0-9_]+)', 'Telegram'),
    (r'twitch\.tv/([A-Za-z0-9_]+)', 'Twitch'),
    (r'snapchat\.com/add/([A-Za-z0-9_.]+)', 'Snapchat'),
    (r'tiktok\.com/@([A-Za-z0-9_.]+)', 'TikTok'),
]
# Filter out common false positives like: reel, p, explore, home, channel, etc.
```

## Installed OSINT Tools Reference

| Tool | Purpose |
|------|---------|
| `sherlock` | Username search across 400+ platforms |

### Sherlock Usage

```bash
sherlock --print-found --no-color "<username>" --timeout 90
```

Takes 30-120 seconds. Scans 400+ social networks.

## Report Structure

Save to `~/projects/osint-recon/HANDLE_audit_report.txt`:

1. Executive Summary
2. Resolved Identity Attributes (real name, nationality, age bracket, language)
3. Active Platform Presence (table with platform, handle, URL, notes)
4. Alternate Handles and Name Variants
5. Email and Contact Registrations
6. Development Platform Audit
7. Domain Registration Audit
8. Cross-Platform Linkage Map (ASCII graph)
9. Content Distribution Analysis
10. Leak and Exposure Assessment
11. Operational Security Notes (strengths and weaknesses)
12. Data Quality and Limitations

## Reference Files

- `references/searxng-quirks.md` -- SearXNG bot detection, engine suspension, format workaround
- `references/search-fallbacks.md` -- DDG HTML parsing, grep pitfalls, confidence indicators, platform-by-platform shell behavior
- `references/platform-techniques.md` -- Reddit JSON API, Spotify OG tags, Telegram og: extraction, Wayback CDX patterns
- `references/media-scraping-pipeline.md` -- Full media download, dedup (SHA256), EXIF extraction, Reddit/Bunkr/aggregator scraping patterns
- `references/phone-osint.md` -- PhoneInfoga + ignorant setup, scanning, normalization to E.164
- `references/email-osint.md` -- holehe platform checks, maigret on email prefix, Google Dork queries, corporate domain analysis, ProtonMail PKS lookup
- `references/leak-normalizer.md` -- Parsing breach dumps: extract emails, phones, handles, wallets, system paths; normalize and correlate
- `references/graphviz-scheme.md` -- Color schema (red/yellow/green/blue), node shapes, edge styles, export commands
- `references/platform-extraction-patterns.md` -- SoundCloud hydration, Gravatar bio, Telegram OG signatures, Snapchat avatars, Linktree correlation, Steam persona, Instagram unreliability, Reddit JSON states, DDG HTML fallback
- `references/country-geolocation-via-gaming-apis.md` -- Chess.com country codes (highest-value geolocation signal), Steam XML + email leak, Roblox account age, Lichess minimal data, multi-country conflict analysis

## Advanced Extraction Techniques

### Arabic / Levantine Naming Convention
When a full name has the structure "First X Y Last" (3+ name parts before
the surname), it may follow Arabic patronymic naming:
  - Given name + father's name + mother's name + family surname
  - Example: "Rami Fayez izzat Milhem" = Rami (given), Fayez (father),
    izzat (mother), Milhem (surname)
  - Chess.com country=JO (Jordan) or Levantine codes (PS, SY, LB, SA)
    confirms the pattern
  - The handle is typically `firstname` or `firstnamefathername` on gaming
    platforms, NOT the full legal name
- Always analyze name structure before treating it as a composite alias
  — a 4-part name is often a real legal identity, not two people combined

### Composite Names — Split Before Searching
When a full name ("First Middle Last") yields zero search results,
split into components and search each separately:
- "Erian Nocete Abrasaldo" → search "Erian Nocete", "Erian Abrasaldo",
  "Nocete Abrasaldo", plus individual words as handles
- Generate handle variants: `first+last`, `first_last`, `first.last`,
  `first+shortlast`, `shortfirst+last`
- The composite may be two people combined (partners, friends, gaming duo)
  rather than a single identity — look for separate real names resolving
  from different handle variants

### SoundCloud Hydration Data
SoundCloud embeds full profile JSON directly in page HTML. Most reliable
extraction method for location, real name, and activity metrics:
```python
import json
sd_match = re.search(r'window\.__sc_hydration\s*=\s*(\[.+?\]);', html, re.DOTALL)
if sd_match:
    sd = json.loads(sd_match.group(1))
    for item in sd:
        if isinstance(item, dict) and item.get("hydratable") == "user":
            data = item.get("data", {})
            # Key fields: full_name, username, city, country_code,
            # description, track_count, followers_count, followings_count,
            # likes_count, playlist_count, verified, last_modified
```
Hydration data is more reliable than OG tags for SoundCloud — always
parse it when present.

### Gravatar Profile Extraction
Gravatar profiles at `https://en.gravatar.com/HANDLE` can reveal:
- **og:title**: Display name (may be nickname, e.g. "Jojie Hym's")
- **Bio text**: Real names in prose (e.g. "Hi, My name is Jojie Abrasaldo")
- **Location data**: City/country if filled in
Parse the rendered HTML and extract the profile card text — strip scripts
and styles first, then look for name patterns in the remaining text.

### Telegram Handle Verification
Telegram OG titles distinguish real vs unclaimed accounts:
- `"Telegram: Contact @HANDLE"` → account EXISTS (may have no custom data)
- `"Telegram – a new era of messaging"` (generic description) → UNCLAIMED
- Custom name (e.g. `"Kyle Abrasaldo"`) → real name set in profile

### Linktree as Identity Linker
Linktree pages that share identical link sets (same affiliate URLs in
same order) are strong evidence of a common operator. Extract all
linked URLs from Linktree pages and cross-compare between suspected
handles. Use `re.findall(r'"url":"([^"]+)"', html)` on the page source.

### Instagram JSON Endpoints Unreliable via curl
The `?__a=1&__d=dis` and `window._sharedData` approaches frequently
return empty/generic content. Treat Instagram as UNVERIFIABLE through
programmatic access — note in report rather than claiming absence.
Only the browser tool with visual verification is reliable for Instagram.

## Pitfalls

- **Do not assume 404 means no account**. Some platforms return 403 or 429 for blocked or scraped requests. Cross-reference with search results.
- **Handle variants matter**. Users often use slightly different handles across platforms such as double letters, underscores, or suffixes. Always check variants.
- **SearXNG rate limits**. If you get 0 results across multiple queries, engines may be suspended. Wait and retry, or fall back to direct probes.
- **Nitter is dead as of 2026-06.** All tested public instances (nitter.net, nitter.poast.org, nitter.1d4.us) return 403/404/DNS errors. Do not waste time trying multiple instances. Mark Twitter/X as "unverifiable" unless the browser tool is available.
- **Spotify user IDs are numeric**. The handle in the URL is a numeric ID, not the display name. Extract display name from OG tags.
- **Pinterest URL mismatch**. Pinterest profile URLs may resolve to a different user than expected. Verify via search results.
- **Reddit JSON API is rate-limited**. Use sparingly. One request per user (about.json, submitted.json, comments.json) is usually fine.
- **Do not capture transient failures as constraints**. If a tool is temporarily unavailable, note it in the report limitations section, not as a permanent tool limitation.
- **execute_code sandbox restrictions**. `dig` and `host` may be missing or permission-denied in the sandbox. Use `socket.gethostbyname()` as fallback. `sha256sum` may also be unavailable — use Python `hashlib.sha256()`.
- **Media scraping: filter preview images**. Reddit generates 6+ resolution variants per image (preview.redd.it). Download only `source` resolution or `i.redd.it` originals to avoid bloating with thumbnails. Use `media_metadata` for galleries.
- **EXIF is stripped on rehosted content**. Reddit, Twitter, Instagram — all strip EXIF on upload. Don't expect GPS or camera data from scraped social media images. Only original file uploads (e.g., Bunkr direct links) might retain metadata.
- **Redgifs requires auth**. Direct video download from Redgifs is blocked without API bearer token. Document URLs as evidence but note download limitation.
- **Reddit comment scraping for alt-handles**. Reddit comments frequently contain links to alternate accounts (other Instagram handles, Telegram groups, private channels). Always scrape `comments.json` in addition to `submitted.json` — external links in comments often reveal the most valuable cross-platform connections not visible from bio or post content alone.
- **Linktree → Spotify real name resolution**. Linktree pages embed all linked platforms as `"url":"..."` JSON patterns. Follow each linked platform and extract OG tags. Spotify profiles (`open.spotify.com/user/USERID`) expose the real display name in `og:title` — this frequently reveals the person's real name even when social handles are pseudonymous. Always check Linktree links for Spotify, as creators commonly link it.
- **Reddit preview dedup ratio**: Expect ~8-10% duplicate rate when downloading all Reddit media URLs (preview.redd.it generates multiple resolutions per image). Use SHA256 dedup across all sources. The `media_metadata` source URL is the canonical version — prefer it over `preview.redd.it` URLs.
- **Sherlock false positives on adult platforms.** Sherlock may report "Not Found" for OnlyFans/Fansly because these sites return HTTP 200 with generic SPA shells for any handle. A Sherlock "Not Found" on adult platforms is NOT conclusive — verify with browser or OG tag analysis.
- **Sherlock bot detection blocks.** Many platforms (1337x, BOOTH, CodeSandbox, DMOJ, DigitalSpy, etc.) block Sherlock's requests. These show as "Blocked by bot detection (proxy may help)" — treat as inconclusive, not negative. Follow up with direct browser probes if the platform is high-priority.
- **SPA shell detection via OG tags**: JS-rendered SPAs (Instagram, TikTok, X, Twitch, OnlyFans, Pinterest, Medium, etc.) return HTTP 200 with generic content for any handle. To distinguish real accounts from shells, check `og:title` and `og:description`: if they contain the handle name or profile-specific content, the account likely exists; if they show generic branding ("Instagram", "TikTok - Make Your Day", "OnlyFans") the handle is unclaimed or the profile is private.
- **grep -oP lookbehind failures**: Some systems reject `grep -oP` with variable-length lookbehind assertions. Always use Python `re` module for parsing SearXNG HTML output, not grep with lookbehind.
- **DuckDuckGo zero results = strong signal**: If both SearXNG and DuckDuckGo HTML return 0 results for a handle, this is strong evidence of zero web presence. Document this in the report as a confidence indicator.
- **Nitter instance rot**: Most public Nitter instances are permanently down. Do not rely on Nitter as a primary Twitter/X intelligence source. If all instances fail, note Twitter as "unverifiable" in the report.
- **Steam `/id/` vanity URLs return 200 for non-existent profiles.** Steam returns HTTP 200 with a generic "Steam Community :: Error" page for any vanity URL, even unclaimed ones. The OG title "Steam Community :: Error" = profile does not exist. To confirm existence, check for `actual_persona_name` in the HTML, or use the numeric SteamID64 (`/profiles/76561198XXXXXXXX`) which returns proper data or a clear 404.
- **SearXNG category encoding.** The `categories` parameter must NOT contain literal spaces. `social media` (space) causes `URL can't contain control characters`. Use `social+media` or `social%20media`. All multi-word categories must be URL-encoded.
- **DDG space encoding.** DuckDuckGo HTML treats `%20` (from `urllib.parse.quote()`) differently from `+`. Always replace: `urllib.parse.quote(query).replace('%20', '+')`. Using raw `%20` can return 0 results even for valid queries.
- **urllib.request import in execute_code sandbox.** `urllib.Request` does not exist — the correct import path is `urllib.request.Request`. Always use `import urllib.request` explicitly, never rely on `from urllib import *` or bare `urllib.Request`.
- **Reddit JSON API 404 = confirmed absence.** A clean HTTP 404 across all three endpoints (about.json, submitted.json, comments.json) is strong confirmation the user does not exist on Reddit. Do not treat it as "blocked" — it is a definitive negative.
- **Handle squatting creates noise.** Common names may have handles registered by different, unrelated people. Always verify with profile data (Steam persona, SoundCloud real name, Facebook profile pic) before correlating. Telegram especially has unclaimed handles that return 200.
- **Snapchat profile photos exist even for empty accounts.** A Snapchat profile photo endpoint returning a real image (not a default ghost) confirms the user has actively set an avatar — treat as evidence of a real account, not just a name reservation.
- **DuckDuckGo `web_search` may fail silently.** The Hermes `web_search` tool requires a configured provider. If it returns "No web search provider configured", fall back immediately to DuckDuckGo HTML via `execute_code` + `urllib` — do not attempt the tool again.
- **SoundCloud location != SoundCloud city field.** The `city` field in SoundCloud hydration is user-editable and may be outdated. Cross-reference location data across platforms.
- **Steam profile HTML can leak email addresses.** Even on "private" Steam profiles, the rendered HTML sometimes contains the user's plaintext email. Extract with `re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)` and report as HIGH exposure. Also scan for phone numbers in the same way.
- **Chess.com is the single highest-value geolocation source.** Its public API returns ISO country codes, account age, last online timestamp, and game history — all via a simple GET request. Always probe `https://api.chess.com/pub/player/{handle}` early in any investigation. Use `User-Agent: Mozilla/5.0 (hermes-osint)` (generic bot UA is blocked). When multiple platforms return different country codes for the same handle, treat this as evidence of account squatting or unrelated people sharing a name.
