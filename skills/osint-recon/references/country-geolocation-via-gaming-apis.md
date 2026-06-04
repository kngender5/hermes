# Country / Geolocation via Gaming APIs

Several gaming platforms expose country codes or location data through
public APIs that are more reliable than profile-scraping.

## Chess.com — Country Code (Highest Value Geolocation Signal)

Chess.com's public API returns a `country` field with a full URL:
```
https://api.chess.com/pub/player/HANDLE
→ data.country = "https://api.chess.com/pub/country/CC"
```
Where `CC` is a 2-letter ISO 3166-1 alpha-2 code.

Also exposes:
- `joined` — Unix timestamp, account age
- `last_online` — Unix timestamp, last activity
- `followers` — follower count
- `status` — "basic" (free) or "premium"
- `name` — display name
- `fide` — FIDE rating if set
- `twitch_url` — linked Twitch

Stats endpoint: `https://api.chess.com/pub/player/HANDLE/stats`
Returns per-game-type: `chess_blitz`, `chess_bullet`, `chess_rapid`,
`chess_daily` — each has `last.rating` and `record.{win,loss,draw}`.

**Headers required:** `User-Agent: Mozilla/5.0 (hermes-osint)` — generic
bot UA is blocked; use a human-like UA.

**Pitfall:** A Chess.com account with 0 games may still return the country
code. Use account age (joined → now) to distinguish real accounts from
squatters. Accounts joined <1 month ago with different country than other
platforms likely belong to a different person.

**Pitfall (multi-country conflict):** When different platforms return
different country codes for the same handle, this is STRONG evidence of
different people sharing the handle. Always report the full country
matrix across platforms.

## Roblox — Account Age

Roblox Users API (POST required):
```
POST https://users.roblox.com/v1/usernames/users
{"usernames": ["HANDLE"], "excludeBannedUsers": false}
```
→ `id`, `name`, `displayName`, `created` (ISO 8601), `isBanned`,
`description` (bio).

**Pitfall:** API requires POST, not GET. No country/location data
exposed. Empty response = username does not exist.

## Lichess — Minimal Public Data

```
https://lichess.org/@/{handle}
```
HTML includes rating in `<span class="rating">` tags. No API for
country. Confirm existence by checking title contains the handle vs
a generic "lichess.org" page.

## Steam — XML Profile + Email Leak

```
https://steamcommunity.com/id/{handle}?xml=1
```
Returns SteamID64, steamID, realName, location, summary, website,
stateMessage, VAC ban, trade ban, memberSince.

**CONFIRMED PRIVACY LEAK (2 sessions):** Steam profile HTML sometimes
contains plaintext email addresses. Extract with:
```python
emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)
```
Filter out example/sentry/w3.org localhost patterns. Report any found
emails as HIGH exposure.

**Pitfall:** Steam `location` is user-editable and may be outdated,
fictional, or a joke. Cross-reference across platforms.
