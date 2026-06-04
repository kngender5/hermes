# Search Fallback Reference

## When SearXNG Fails (HTTP 403 or 0 results)

### DuckDuckGo HTML Endpoint
```
https://html.duckduckgo.com/html/?q=QUERY
```
Parse with:
```python
import re, urllib.request, urllib.parse

query = "ylrlqt narvik"
url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")

titles = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)

for i, (link, title) in enumerate(titles[:10]):
    clean_title = re.sub(r'<[^>]+>', '', title).strip()
    clean_link = re.sub(r'<[^>]+>', '', link).strip()
    print(f"[{i+1}] {clean_title}")
    print(f"    {clean_link}")
    if i < len(snippets):
        print(f"    {re.sub(r'<[^>]+>', '', snippets[i]).strip()[:120]}")
```

### SearXNG HTML Parsing (Python, not grep)
```python
import re, urllib.request

url = "http://localhost:8080/search?q=HANDLE&categories=general&pageno=1"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")

result_urls = re.findall(r'class="url_header"[^>]*href="(https?://[^"]+)"', html)
result_titles = re.findall(r'<h3><a[^>]+rel="noreferrer"[^>]*>(.*?)</a></h3>', html, re.DOTALL)
clean_titles = [re.sub(r'<[^>]+>', '', t).strip() for t in result_titles]
```

## Confidence Indicators

| Signal | Confidence |
|--------|-----------|
| SearXNG 0 results + DDG 0 results | Strong evidence of zero web presence |
| All platforms 404 or SPA shell | Handle likely unused/inactive |
| Maigret 0 hits on 510 sites | No username presence on major platforms |
| All domains NXDOMAIN | No personal domain registered |
| Nitter all instances down | Twitter/X presence unverifiable |

## Platform-Specific Notes

### Platforms That Always Return 200 (SPA shells)
These return generic content for ANY handle — never count HTTP 200 alone as proof of account:
- Instagram (og:title = "Instagram")
- TikTok (og:title = "TikTok - Make Your Day")
- Twitch (og:title = "Twitch")
- OnlyFans (og:title = "OnlyFans")
- X/Twitter (no OG tags, generic shell)
- Pinterest (no OG tags)
- Medium (og:title = "Medium")
- Fansly (og:title = "Fansly.com")
- JustForFans (og:title = "JustFor.Fans")
- Discord (og:title = "Discord - Group Chat...")

### Platforms Where 404 = Definite No
- GitHub
- Reddit (also check /user/HANDLE/about.json)
- YouTube
- SoundCloud
- Flickr
- Dribbble
- Behance
- DeviantArt
- Gravatar
- Keybase
- CodePen
- Stack Overflow
- LeetCode
- Substack
- Tumblr
- VSCO
- FINN.no

### Platforms Requiring Content Verification
- Replit (redirects to sign-up for non-existent users)
- GeeksforGeeks (shows "undefined" og:title for non-existent users)
- HackerRank (generic shell for any handle)
- Steam (shows error page but returns 200)
