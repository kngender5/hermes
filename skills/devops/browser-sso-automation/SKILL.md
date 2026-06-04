---
name: browser-sso-automation
description: "Automate browser-based SSO login flows (Feide, Canvas LMS, Panopto) on WSL2 with Playwright. Handles org selectors, multi-step auth, cookie extraction for API access, video/download scraping from educational platforms, and Canvas CLI/course management for Norwegian LMS instances."
metadata:
  hermes:
    tags: [browser, automation, sso, feide, canvas, panopto, wsl2, playwright, norwegian-lms]
---

# Browser SSO Automation

Automate browser-based SSO authentication flows on WSL2 using Playwright with system Chromium. Covers Feide (Norwegian federated login), Canvas LMS, Panopto, and similar SAML/OAuth chains.

## When to Use

- Canvas API returns 403 for file downloads (school API restrictions)
- Panopto videos require session cookies from SSO login
- Any SSO flow that needs browser cookies for subsequent API access
- Headless browser automation on WSL2 with WSLg

## WSL2 Browser Setup

Playwright's bundled Chromium doesn't work on Ubuntu 26.04. Use system Chromium:

```python
browser = p.chromium.launch(
    headless=False,  # or True
    executable_path="/usr/bin/chromium-browser",
    args=[
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
    ],
)
```

**Requirements:**
- WSLg must be available: `echo $DISPLAY` should show `:0`
- System Chromium: `which chromium-browser`
- `playwright` and `playwright-stealth` pip packages installed
- Note: `playwright_stealth.stealth_sync` doesn't exist in newer versions; use `Stealth(page)` class instead, or skip stealth entirely with system Chromium

## Feide SSO Flow

Feide is Norway's federated identity provider. Common pattern: service → Feide org selector → Feide login form → service.

### Step 1: Org Selector Page

Feide org selector has a searchable dropdown. The page at `idp.feide.no/simplesaml/module.php/feide/selectorg` contains:

- Search input: `#org_selector_filter` (placeholder: "Search or choose from the list")
- Org list items: `li.orglist_item` with child `span.orglist_name`
- Hidden field: `#org_selector` (stores selected org ID)
- Continue button: `button:has-text('Continue')` or `button[type='submit']`

```python
# Type in search to filter orgs — MUST use keyboard.type(), NOT .fill()
# Feide's typeahead filter doesn't respond to programmatic .fill()
search = page.query_selector("#org_selector_filter")
search.click()
page.keyboard.type("troms fylkeskommune", delay=50)  # key-by-key input
time.sleep(3)

# Click specific org by exact name match
page.evaluate("""() => {
    for (const item of document.querySelectorAll('li.orglist_item')) {
        const name = item.querySelector('.orglist_name');
        if (name && name.textContent.trim() === 'Troms fylkeskommune') {
            item.click();
            return;
        }
    }
}""")
time.sleep(1)

# Click Continue
page.query_selector("button:has-text('Continue')").click()
```

**Pattern:** The text filter works like a typeahead — type partial text to narrow the list, then click the exact `li.orglist_item`.

### Step 2: Login Form

After org selection, Feide shows credentials form:

- Username: `input#username` or `input[name='feidename']` (autocomplete="username webauthn")
- Password: `input#password`
- Submit: `button[type='submit']` or `button:has-text('Logg inn')`

### Step 3: Service OAuth Confirm

After Feide auth, many services (Canvas, Panopto) show an OAuth consent page:

- Look for buttons: "OK", "Ja", "Godta", "Accept", "Allow", "Tillat"
- Also check `input[type='submit']` and `button[type='submit']`

### Canvas OAuth Confirm URL Pattern

Canvas OAuth confirm: `canvas.instructure.com/login/oauth/confirm`

## Canvas LMS Integration

### API Key Setup

Store in `~/.hermes/.env`:
```
CANVAS_API_KEY=your_token_here
CANVAS_BASE_URL=https://your-school.instructure.com
CANVAS_API_URL=https://your-school.instructure.com  # legacy var name
CANVAS_API_TOKEN=your_token_here  # legacy var name
```

Note: Both old-style (`CANVAS_API_URL`/`CANVAS_API_TOKEN`) and new-style (`CANVAS_BASE_URL`/`CANVAS_API_KEY`) variable names are used by different scripts.

### API Limitations

- Files API often returns 403 even with valid key (school restriction)
- Use browser SSO + cookie extraction as fallback
- Folders API works: `/api/v1/courses/{id}/folders`

### Canvas CLI Tool

`scripts/canvas` provides: `canvas courses`, `canvas assignments`, `canvas files`, `canvas download`, `canvas syllabus`, `canvas calendar`, `canvas grades`, `canvas announce`. Supports `--skip ID,ID` and `--only ID,ID` flags for selective downloads. See `references/canvas_cli.md`.

### Canvas API Patterns

Key techniques for Norwegian Canvas instances:
- **Module items** bypass Files API 403: query `/api/v1/courses/{id}/modules/{module_id}/items` to get downloadable file `content_id` values
- **File download**: use `/api/v1/files/{id}/download?download_frd=1` with `curl -L` (follow redirects)
- **Assignment attachments**: extract file IDs from assignment HTML descriptions with `re.findall(r'/files/(\d+)', html)`
- Typical Norwegian course structure: Generelt → Forelesninger → Fagstoff → Tilleggsstoff → Programvare → Oppgaver

See `references/canvas_api_patterns.md` for detailed patterns.

### SSO Flow

Panopto → "Sign in" → Feide SSO → Feide org select → credentials → Canvas OAuth → Panopto

The Panopto login page is at: `school.cloud.panopto.eu/Panopto/Pages/Auth/Login.aspx`

The "Sign in" link shows the Feide org selector directly (embedded in Panopto page, no redirect).

### Video Download via DeliveryInfo API

```python
delivery_url = f"{PANOPTO_BASE}/Panopto/Pages/Viewer/DeliveryInfo.aspx?deliveryId={video_id}&responseType=json"
response = session.get(delivery_url, cookies=panopto_cookies)
data = response.json()
```

**Important:** `DownloadUrl` is often `null`. The actual download URLs are at:

1. **Direct MP4 (preferred):** `data['Delivery']['PodcastStreams'][0]['StreamUrl']`
2. **HLS stream:** `data['Delivery']['Streams'][0]['StreamUrl']` (ends with `.hls/master.m3u8`)
3. **HLS variants:** `data['Delivery']['Streams'][0]['Variants']` — array of `{Bandwidth, Url}` objects

### Embedded Captions Extraction

Panopto videos may have embedded Norwegian subtitles (codec: `mov_text`, lang: `nor`). Extract with ffmpeg:

```bash
ffmpeg -i video.mp4 -map 0:2 -c:s srt output.srt
```

Check streams first:
```bash
ffprobe -v quiet -show_streams video.mp4 | grep codec_type=subtitle
```

Note: Caption download endpoints (`CaptionDownload.ashx`) return 404 on most Panopto instances — the captions are embedded in the video file itself.

### SRT Cleanup

Panopto's embedded captions may contain HTML font tags. Clean with regex:
```python
content = re.sub(r'<font[^>]*>', '', content)
content = re.sub(r'</font>', '', content)
```

## Whisper Transcription

For videos without embedded captions, use `whisper-ctranslate2`:

```bash
whisper-ctranslate2 --language no --model large-v3 --output_format srt --output_dir . video.mp4
```

**GPU requirements:** Requires `libcublas.so.12`. Install with:
```bash
sudo apt-get install -y libcublas12
```

If library not found at runtime:
```bash
LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH whisper-ctranslate2 ...
```

**Note:** Short intro/slide videos (e.g., < 5 min) may produce poor transcription — whisper picks up watermarks/slide text instead of speech.

## Cookie Extraction Pattern

After browser SSO, extract cookies for requests session:

```python
cookies = context.cookies()
# Panopto cookies work with the Panopto domain
import requests
session = requests.Session()
for c in cookies:
    session.cookies.set(c["name"], c["value"], domain=panopto_domain)
session.headers["User-Agent"] = ua
```

## Common Pitfalls

1. **Feide org search:** Must use `li.orglist_item` CSS selector, not generic `text=` selectors which may hit wrong elements
2. **Feide org typeahead filter — `.fill()` does NOT work:** Playwright's `.fill()` method on `#org_selector_filter` frequently does NOT trigger the typeahead JavaScript filter. Use `page.keyboard.type("troms fylkeskommune", delay=50)` instead, then wait 3 seconds for filtered results to render, then click `li.orglist_item` by exact text match via `.evaluate()`.
2. **Filename colons:** Filenames with `:` (e.g., `13:45`) cause issues — sanitize to `_`
3. **Panopto DownloadUrl:** Always null; use `PodcastStreams[0].StreamUrl` for direct MP4
4. **Canvas files 403:** Browser SSO bypasses this; API key approach fails
5. **WSLg display:** `DISPLAY=:0` must be set; verify with `echo $DISPLAY`
6. **Playwright Chromium on Ubuntu 26.04:**Bundled Chromium incompatible; use system Chromium at `/usr/bin/chromium-browser`
7. **whisper-ctranslate2 libcublas:** Install `libcublas12` and set `LD_LIBRARY_PATH` if needed
8. **Whisper watermark issue:** Videos with burned-in text watermarks (e.g., "Teksting av Nicolai Winther" in classroom recordings) cause whisper to transcribe the watermark instead of speech. Check first few minutes of output. Panopto web recordings (WEB prefix) don't have this issue; classroom recordings (AUT23 prefix) do.
9. **Parallel whisper:** Running 4+ whisper processes in parallel on RTX 4060 divides GPU memory. Each gets ~25% GPU, so processing time increases ~4x per job. For 435 min of video, expect 3-4 hours total.
10. **Panopto caption endpoints:** `CaptionDownload.ashx` returns 404 on most instances. Captions are embedded in the video file (mov_text codec), not available as separate downloads. Use ffmpeg to extract.
11. **Canvas custom page navigation:** Files may be under `/courses/{id}/pages/{page-name}` (e.g., "fagstoff") not the standard `/files` tab. Check course navigation tabs.

## Reference Scripts

- `~/projects/study-workbench/scripts/canvas_panopto_download.py` — Complete Panopto download with Feide SSO, DeliveryInfo API, caption extraction
- `~/projects/study-workbench/scripts/canvas_ekom_download.py` — Targeted Ekom course downloader (Fagstoff + Panopto)
- `~/projects/study-workbench/scripts/extract_captions.py` — ffmpeg-based embedded caption extraction from MP4
- `~/projects/study-workbench/scripts/clean_and_whisper.py` — SRT cleanup + whisper transcription pipeline
