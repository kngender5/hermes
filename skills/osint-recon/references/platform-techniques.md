# Platform-Specific OSINT Techniques

## Twitter/X via Nitter

Nitter is a privacy-reserving Twitter frontend. Multiple public instances exist
but most are unreliable. Test in order:

1. nitter.net
2. nitter.poast.org
3. nitter.1d4.us
4. nitter.themndo.com
5. nitter.rawbit.ninja
6. nitter.privacydev.net

RSS endpoint (most reliable): `https://INSTANCE/HANDLE/rss`
Parse with regex:
```python
titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', rss)
links  = re.findall(r'<link>(https?://[^<]+)</link>', rss)
dates  = re.findall(r'<pubDate>([^<]+)</pubDate>', rss)
```

Many instances now require JavaScript verification (return "Verifying your
browser"). If all instances blocked, rely on SearXNG social media category
and og-tag scraping from x.com/HANDLE.

## Reddit JSON API

Append `.json` to any Reddit URL:
- `reddit.com/user/HANDLE/about.json` -- karma, created, verified email
- `reddit.com/user/HANDLE/submitted.json?limit=25` -- post history
- `reddit.com/user/HANDLE/comments.json?limit=25` -- comment history

Parse for cross-links, emails, and contact info in selftext/body.

## Spotify

URL pattern: `open.spotify.com/user/USERID` (numeric ID, not display name).
OG tags contain display name and image presence. No JSON API available without
authentication.

## Telegram

URL pattern: `t.me/HANDLE`
OG tags reveal: title, description, type (profile/channel/group), avatar image.
A valid Telegram profile always has `og:site_name` set to "Telegram".

## Instagram

JS-rendered SPA. curl gets empty shell. Alternatives:
- OG tags: partial data (og:title, og:description, og:image)
- `?__a=1&__d=dis` JSON endpoint (increasingly blocked)
- SearXNG is the primary source for Instagram profile data

## Linktree

OG title and description are reliable. Extract linked platforms from embedded
JSON patterns: `"url":"https://onlyfans.com/HANDLE"` etc. Linktree pages also
contain affiliate/spam links -- filter for platform domains of interest.

## TikTok

JS-rendered. curl gets minimal content. og:title and og:description often
empty. Relies on SearXNG for discovery.

## Snapchat

curl to `snapchat.com/add/HANDLE` returns JS-rendered shell. OG tags often
empty. Check SearXNG for references. Snapchat Stories/Spotlight API not
publicly accessible.

## Wayback Machine CDX API

```bash
# List all archived URLs matching pattern
curl -s "https://web.archive.org/cdx/search/cdx?url=DOMAIN*&output=text&limit=50&fl=original,timestamp,statuscode&filter=statuscode:200"

# List snapshots of specific URL
curl -s "https://web.archive.org/cdx/search/cdx?url=EXACT_URL&output=json&limit=20"
```

JSON output format: `["urlkey","timestamp","original","mimetype","statuscode","digest","length"]`
