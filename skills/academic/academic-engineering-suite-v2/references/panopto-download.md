# Panopto Video & Caption Download — Reference

## SSO Login Flow (Feide → Canvas OAuth → Panopto)

Norwegian schools using Feide SSO require this chain:

1. **Panopto login page** → click "Sign in" link
2. **Feide org selector** (on Panopto page or idp.feide.no):
   - Find search input: `#org_selector_filter` or `input[placeholder*='Search']`
   - Type partial name (e.g. "tr" for "Troms fylkeskommune")
   - Wait 3s for filtered list to render
   - Click the `li.orglist_item` element (NOT parent div/span) with exact text match:
     ```js
     for (const item of document.querySelectorAll('li.orglist_item')) {
       const name = item.querySelector('.orglist_name');
       if (name && name.textContent.trim() === 'Troms fylkeskommune') { item.click(); break; }
     }
     ```
   - Click "Continue" / "Neste" button
3. **Feide credentials** → fill `input#username` / `input#password`, submit
4. **Canvas OAuth confirm** → click "OK" / "Ja" / "Godta" / "Allow" / `input[type='submit']`
5. Land on Panopto video page with session cookies

**Pitfall:** The org selector may render on the Panopto domain (embedded) OR redirect to idp.feide.no. Check both URL patterns. The `li.orglist_item` elements have class `match` when filtered.

**Pitfall:** Clicking by text match on parent elements (DIV, SPAN) can hit the wrong org. Always target `li.orglist_item` directly. The visible text is in a child `.orglist_name` SPAN.

## Panopto Folder Access

Courses may have videos in a Panopto folder accessible by direct URL:
```
https://{institution}.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx?embedded=1#folderID="{uuid}"
```
For Ekom: folderID = `1437cae6-104e-414c-ba8c-b341008b9fa0`

Navigate to this URL in the browser (after SSO) to list all recordings in the folder.

## Canvas Content Structure

Course materials may be in different locations:
- **Files** — `/courses/{id}/files` (file browser, requires API permissions)
- **Pages** — `/courses/{id}/pages/{slug}` (wiki pages with downloadable attachments)
- **Fagstoff** — may be under Pages (e.g., `/courses/1627/pages/fagstoff`)
- **Embedded tools** — BigBlueButton, Zoom, Panopto, OneDrive (iframes)

For Ekom: Fagstoff (course materials) was under Pages, NOT under Files.

## Video Download via DeliveryInfo API

```
GET /Panopto/Pages/Viewer/DeliveryInfo.aspx?deliveryId={UUID}&responseType=json
```

Response structure:
- `DownloadUrl` — **ALWAYS null in practice**, never rely on it
- `Delivery.PodcastStreams[0].StreamUrl` — direct MP4 download URL (preferred)
- `Delivery.Streams[0].StreamUrl` — HLS stream URL (fallback, use ffmpeg)
- `Delivery.Streams[0].Variants` — HLS quality variants with bandwidth info

Download with cookies from browser session (Playwright `context.cookies()`).

## Caption Extraction

### Embedded captions (Panopto auto-generated)
- Check with ffprobe: `ffprobe -v quiet -print_format json -show_streams file.mp4`
- Look for `codec_type: "subtitle"` streams (usually `mov_text`, lang=nor)
- Extract: `ffmpeg -y -i input.mp4 -map 0:<idx> -c:s srt output.srt`
- Language code 19 = Norwegian
- **Quality: ~70-80% accuracy** — frequent word salad errors, especially for technical terms.
- **Clean SRT:** Strip HTML tags: `re.sub(r'<font[^>]*>', '', content)` and `re.sub(r'</font>', '', content)`

### Whisper transcription (recommended for study use)
```bash
LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH \
  whisper-ctranslate2 --language no --model large-v3 \
  --output_format srt --output_dir . input.mp4
```

**Pitfall:** `libcublas.so.12` error even when installed. Must set `LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu` explicitly. Install with `sudo apt-get install -y libcublas12`.

**Pitfall:** Filenames with colons break commands. Use `./` prefix or underscores.

**Pitfall:** Watermark-burned videos fail — detect by >50% repeated phrases. Skip whisper on these. Typically affects classroom recordings (AUT23 Ekom) but NOT web-recorded lectures (WEB series).

### Parallel whisper processing
```bash
cd /path/to/videos
for vid in *.mp4; do
  LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH whisper-ctranslate2 --language no --model large-v3 --output_format srt --output_dir . ./"$vid" 2>&1 &
done
wait
```
Each job ~2.5 GB RAM + GPU. ~30 min per hour on RTX 4060.

## Web vs Classroom Recordings
- **WEB series** (web recorder): No watermark. Whisper works excellently.
- **Classroom recordings** (AUT23 Ekom): Often have burned-in "Teksting av [name]" watermark. Whisper fails. Use embedded Panopto captions instead.

## Quality Comparison

| Aspect | Panopto Embedded | Whisper large-v3 |
|---|---|---|
| Accuracy | ~70-80% — word salad errors | ~90-95% — clean Norwegian |
| Technical terms | Often garbled | Correct (splitter, OTDR, dB) |
| Timing | 30s blocks | ~2s segments |
| Availability | Only videos with captions | Works on all (non-watermarked) |
| Speed | Free (embedded) | GPU time (~30 min/hour) |

**Recommendation:** Use Panopto captions for keyword search. Use whisper for study notes/exam prep. Run whisper on ALL non-watermarked videos for consistency.

## File Naming Convention
- Videos: `{safe_name}.mp4` (replace special chars with `_`)
- Embedded captions: `{video_stem}_track{idx}.srt`
- Whisper captions: named by whisper (same stem + .srt in output_dir)
