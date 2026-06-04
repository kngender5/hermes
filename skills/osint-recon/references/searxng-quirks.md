# SearXNG Quirks & Workarounds

## format=json Triggers 403

When SearXNG has `limiter: false` in settings, `format=json` still returns HTTP 403.
This is SearXNG's built-in bot detection on the JSON endpoint. The `limiter` setting
only controls the external rate limiter (e.g., redis-based), not the built-in
bot detection middleware.

**Workaround**: Use default HTML format and parse with regex:
```bash
curl -s "http://localhost:8080/search?q=QUERY&categories=CAT&pageno=N"
```

Result parsing regex:
```python
articles = re.findall(r'<article class="result[^"]*">(.*?)</article>', html, re.DOTALL)
for art in articles:
    url   = re.search(r'<a[^>]+href="(https?://[^"]+)"[^>]*class="url_header"', art)
    title = re.search(r'<h3><a[^>]+rel="noreferrer"[^>]*>(.*?)</a></h3>', art, re.DOTALL)
    snippet = re.search(r'<p class="content">\s*(.*?)(?:</p>|<span)', art, re.DOTALL)
```

`format=rss` also works and is easier to parse than HTML if available.

## Engine Suspension

When SearXNG's upstream search engines (Brave, Google, DuckDuckGo, Startpage)
suspend or rate-limit, queries return 0 results. The SearXNG status page shows
which engines are suspended. Recovery can take minutes to hours.

**Workaround**: Fall back to direct HTTP probes and platform-specific APIs.

## web_extract Incompatibility

`web_extract` does not work with SearXNG as the search backend -- SearXNG is
search-only and cannot extract URL content. Use curl or the browser instead.

## SearXNG Version Noted

Tested with `searxng/2026.5.15+afafca93f`. Behavior may differ in other versions.

## Multi-Word Queries Return Empty Results

During audits, observed that SearXNG sometimes returns 0 results for multi-word
queries even when single-word queries work. Example: `"urbabij josephine"`
returns 0 but `urbabij` returns results.

**Workaround**: Use single-word queries for initial discovery, then filter
results client-side. Or use the bare handle/username as the query and parse
all results manually.

## Boolean/Complex Queries Not Supported

SearXNG's upstream engines (Brave, DDG, etc.) may not support complex boolean
queries like `site:github.com HANDLE OR HANDLE2`. Use simple single-term queries
and iterate.

## SearXNG Down After Container Restart

SearXNG may show as `Up` in `docker ps` but still return 403 or empty responses
after a restart. The internal uwsgi/granian process may need additional time to
initialize. If getting 403s consistently:
```bash
docker logs searxng --tail 20
docker restart searxng
# Wait 30s before retrying
```
