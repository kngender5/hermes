# Platform Extraction Patterns

Techniques discovered during OSINT audits for extracting profile data
from platforms that don't provide clean APIs.

## SoundCloud — Hydration Data

SoundCloud embeds full user/profile JSON in a script tag:

```python
sd_match = re.search(r'window\.__sc_hydration\s*=\s*(\[.+?\]);', html, re.DOTALL)
if sd_match:
    sd = json.loads(sd_match.group(1))
    for item in sd:
        if isinstance(item, dict) and item.get("hydratable") == "user":
            data = item.get("data", {})
```

Key fields in `data`:
- `full_name`, `username` — identity
- `city`, `country_code` — location (user-editable, may be outdated)
- `description` — bio text
- `track_count`, `playlist_count`, `followers_count`, `followings_count`, `likes_count` — activity metrics
- `verified` — bool, true if SoundCloud-verified
- `last_modified` — ISO 8601 timestamp, last profile update

The hydration array also contains `hydratable: "sound"` entries for
individual tracks — each has `title`, `permalink_url`, `playback_count`,
`likes_count`, `created_at`.

## Gravatar — Profile Bio

Gravatar profiles at `https://en.gravatar.com/HANDLE` include display
name and free-form bio text in the rendered HTML. Extraction:

```python
no_script = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
no_style = re.sub(r'<style[^>]*>.*?</style>', '', no_script, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', ' ', no_style)
text = re.sub(r'\s+', ' ', text).strip()
```

Look for patterns like "Hi, my name is..." or the `og:title` for display
name (may differ from Gravatar username).

## Telegram — OG Title Signatures

Telegram profile pages return OG titles that encode account state:

| OG title pattern | Meaning |
|-----------------|---------|
| `Telegram: @HANDLE` | Channel exists |
| `Telegram: Contact @HANDLE` | User account exists |
| `Telegram – a new era of messaging` | Handle unclaimed |
| `Custom Name` | User has set display name |

The `og:image` contains the profile avatar URL. The `og:description`
contains the bio text if set.

## Snapchat — Profile Photo as Existence Proof

Snapchat returns `og:image` with a real photo URL even for accounts
with minimal data. The URL pattern is:
```
https://us-east1-aws.api.snapchat.com/web-capture/www.snapchat.com/@HANDLE/preview/square.jpeg
```
This is NOT a default ghost icon — it's a custom-uploaded avatar.
Treat as strong evidence of active account usage.

## Linktree — Affiliate Link Correlation

Linktree pages encode all linked URLs as JSON `"url":"..."` patterns.
Multiple Linktree pages with identical link sets (same same ordering)
indicate a single operator or coordinated group. Also look for matching
`thanks.is/direct/` links — these are unique per affiliate account.

## Steam — Persona Extraction

Steam vanity URLs return HTTP 200 for any handle (even unclaimed).
To confirm existence:
```python
persona = re.search(r'actual_persona_name[^>]*>([^<]*)', html)
if persona and persona.group(1).strip():
    # Account exists — persona name is the display name
```

The `og:title` "Steam Community :: Error" = profile does not exist.

## Instagram — Unreliable via curl

All known Instagram JSON endpoints (`?__a=1`, `?__a=1&__d=dis`,
`window._sharedData`) return empty/generic content for most handles
via urllib. Do NOT use curl-based extraction for Instagram. Options:
1. Browser tool (only reliable method)
2. Instalibr/instaloader CLI tools
3. Note as "unverifiable" in report

## Reddit — JSON API Signatures

| Status | Meaning |
|--------|---------|
| HTTP 200 + `data.children` array | Profile exists (may be empty) |
| HTTP 404 | Profile does not exist (definitive) |
| HTTP 429 | Rate-limited (retry with backoff) |
| `is_suspended: true` | Account suspended (still exists) |

A profile with `total_karma: 0` and no posts/comments is a dormant
account — note as "dormant" not "inactive".

## DuckDuckGo HTML — Fallback When web_search Unavailable

When the Hermes `web_search` tool fails ("No web search provider"),
use DDG HTML directly in `execute_code`:
```python
import urllib.request, urllib.parse, re
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
titles = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
```
DDG returns max ~10 results per page, no pagination tokens. For more
results, iterate with `&s=N` (offset in multiples of 10).
