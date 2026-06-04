# Media Scraping & Forensic Download Pipeline

## Full Workflow

When asked to scrape all pictures and metadata from an OSINT target:

### 1. Directory Structure

```
~/projects/osint-recon/TARGET_media/
├── reddit/           # Reddit post images
├── bunkr/            # Bunkr album files
├── instagram/        # IG profile/content images
├── onlyfans/         # OF profile images
├── twitch/           # Channel metadata/thumbs
├── telegram/         # TG profile/channel media
├── linktree/         # Profile/avatar images
├── aggregators/      # Mirror/aggregate sites
│   ├── fapello/
│   ├── xxxbunker/
│   ├── leakedfans/
│   └── ...
├── videos/           # Downloaded video files
├── gifs/             # Downloaded GIF/MP4 files
└── deduplicated/     # SHA256-deduped unique files
```

### 2. Reddit Media Extraction

Use the Reddit JSON API with `after` token pagination to get ALL posts:

```python
all_posts = []
after = None
for page in range(10):  # max 10 pages = 1000 posts
    url = f"https://www.reddit.com/user/HANDLE/submitted.json?limit=100"
    if after:
        url += f"&after={after}"
    data = json.loads(fetch_html(url))
    posts = data['data']['children']
    all_posts.extend(posts)
    after = data['data'].get('after')
    if not after:
        break
```

Media extraction from each post — check these sources in order:

1. **Direct URL** (`d['url']`) — check for `.jpg`, `.jpeg`, `.png`, `.gif`, `.mp4`, `.webm`, `.webp`
2. **Reddit gallery** (`d['media_metadata']`) — iterate keys, extract `val['s']['u']` (replace `&amp;` with `&`)
3. **Preview images** (`d['preview']['images']`) — `img['source']['url']` + `img['resolutions'][n]['url']`
4. **Reddit video** (`d['media']['reddit_video']['fallback_url']`)
5. **External links** — Redgifs, Imgur, etc.

Also scrape comments for external links and contact info:
```python
url = f"https://www.reddit.com/user/HANDLE/comments.json?limit=100"
```

### 3. Bunkr Album Scraping

```python
html = fetch_html("https://bunkr.cr/a/ALBUM_ID")
file_links = re.findall(
    r'(?:data-src|src|href)="(https?://[^"]*\.(?:mp4|jpg|jpeg|png|gif|webm|webp)[^"]*)"',
    html, re.IGNORECASE
)
```

Bunkr serves files as direct links. Download with curl. Check sub-pages if album spans multiple pages.

### 4. Redgifs Video Download

Redgifs requires API authentication. The endpoint `https://api.redgifs.com/v2/gifs/GIF_ID`
requires a bearer token. Scraping the HTML page for `og:video` also fails because
Redgifs renders video sources via JavaScript.

**In practice**: Document Redgifs URLs as evidence but note that direct download
requires authentication. The URLs can be visited manually or via a browser with
Redgifs credentials.

### 5. File Deduplication Pipeline

Use `sha256sum` batch mode for speed with 100s of files:

```python
from collections import defaultdict
import subprocess

hash_to_files = defaultdict(list)
all_files = []  # all file paths

for i in range(0, len(all_files), 100):
    batch = all_files[i:i+100]
    r = subprocess.run(
        ["xargs", "-d", '\n', "sha256sum"],
        input='\n'.join(batch), capture_output=True, text=True, timeout=60
    )
    for line in r.stdout.strip().split('\n'):
        sha256, filepath = line.strip().split('  ', 1)
        hash_to_files[sha256].append(filepath)
```

Copy unique files to `deduplicated/` with naming scheme `{source}_{sha256[:16]}.{ext}`. Determine source from the original file path.

### 6. EXIF/Metadata extraction

```bash
# Install exiftool if missing
sudo apt-get install -y libimage-exiftool-perl

# Batch extract all metadata as JSON
exiftool -json -g -n \
  -ImageSize -FileSize -MIMEType \
  -Make -Model -Software \
  -DateTimeOriginal -CreateDate -ModifyDate \
  -GPSLatitude -GPSLongitude -GPSAltitude \
  -Artist -Copyright -Description -Comment \
  -ImageWidth -ImageHeight \
  /path/to/dedup/dir/*.jpg
```

**Critical finding**: Reddit/i.reddits strips ALL EXIF data on upload. Aggregator
sites (Fapello, XXXBunker, etc.) serve resized thumbnails without metadata.
GPS coordinates are almost never available in rehosted social media content.
Camera/software metadata is stripped. Date information survives only in Reddit
post timestamps, not in image files themselves.

### 7. Metadata Catalog Output

For the final manifest, record per file:
- `sha256` — for dedup tracking
- `source` — which platform it came from
- `file` — filename in dedup directory
- `size_bytes` — file size
- `original_paths` — all source locations (for cross-reference)
- `duplicate_count` — how many copies were found

Save as `deduplicated/manifest.json`.

### 8. Platform Image/Video URL Quick Reference

| Platform | URL Pattern | EXIF Preserved? |
|----------|-------------|-----------------|
| Reddit i.redd.it | `https://i.redd.it/HASH.jpg` | No — all stripped |
| Reddit preview | `https://preview.redd.it/...` | No — thumbnails |
| Bunkr | `https://i.bunkr.cr/...` | Sometimes |
| Linktree avatar | `ugc.production.linktr.ee/...` | No |
| Aggregator thumbs | Varies | No — resized |
| Redgifs | `https://redgifs.com/watch/ID` | N/A — video |

### 9. Common Pitfalls

- **Reddit rate limits JSON API**: Limit to ~1 request per second for user endpoints
- **Bunkr uses CDN URLs**: May need to follow redirects (`curl -sL`)
- **Aggregator sites return different content**: Some serve different images on each request due to CDN/rotation
- **sha256sum not in PATH in execute_code sandbox**: Use Python `hashlib.sha256()` as fallback
- **Thousands of preview images**: Reddit generates multiple resolutions per image. Filter to `source` resolution only for meaningful dedup
