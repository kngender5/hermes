# Panopto DeliveryInfo API Reference

## Endpoint

```
GET {PANOPTO_BASE}/Panopto/Pages/Viewer/DeliveryInfo.aspx?deliveryId={uuid}&responseType=json
```

Requires session cookies from SSO login (Panopto → Feide → Canvas OAuth).

## Response Structure (Key Fields)

### Top-Level
- `DownloadUrl`: Usually **null** — do not use
- `EmbedUrl`: Viewer embed URL
- `InvitationId`: Unique request ID
- `SessionId`: Session tracking ID
- `SessionRole`: Viewer role (1 = viewer, 2 = creator, etc.)
- `UserEmail`: Logged-in user email
- `CompletionPercentage`: Watch progress

### `Delivery` Object
- `PublicID`: Video public ID (same as deliveryId)
- `SessionFileId`: File UUID
- `SessionName`: Video title
- `Duration`: Duration in seconds
- `SessionGroupPublicID`: Folder ID
- `SessionGroupLongName`: Folder name
- `HasCaptions`: Boolean
- `AvailableCaptions`: Array of `{Language: int, ShowDisclaimer: bool}`
  - Language 19 = Norwegian
- `IsPodcastEncodeComplete`: Boolean — ready for download

### Download URLs (in priority order)

1. **`Delivery.PodcastStreams[0].StreamUrl`** — Direct MP4 download (preferred)
   ```
   https://{cloudfront}.cloudfront.net:443/sessions/{fileId}/{deliveryId}-{streamId}.mp4?InvocationID=...&tid=...&StreamID=...&ServerName=...
   ```

2. **`Delivery.Streams[0].StreamUrl`** — HLS master playlist
   ```
   https://{cloudfront}.cloudfront.net:443/sessions/{fileId}/{deliveryId}-{streamId}.hls/master.m3u8?...
   ```

3. **`Delivery.Streams[0].Variants`** — Quality-specific HLS streams
   ```json
   [
     {"Bandwidth": 703314, "Url": ".../213827/index.m3u8"},   // low
     {"Bandwidth": 1052412, "Url": ".../281482/index.m3u8"}, // medium
     {"Bandwidth": 1453853, "Url": ".../383544/index.m3u8"}  // high
   ]
   ```

### Stream Object Fields
- `PublicID`: Stream UUID
- `StreamFileId`: Same as PublicID for archival
- `StreamUrl`: Download/playback URL
- `StreamHttpUrl`: Same as StreamUrl for archival
- `StreamType`: 1 = Archival
- `StreamTypeName`: "Archival"
- `ViewerMediaFileType`: 3 = MP4, 11 = HLS
- `EditMediaFileType`: 11 = HLS
- `SourceMediaFileType`: 3 = MP4
- `Name`: Stream name (often video title + ".mp4")
- `Tag`: "dv" for default video

## Download Scripts

### Direct MP4 (Python requests)
```python
import requests
session = requests.Session()
# ... set cookies from browser SSO ...
r = session.get(delivery_api_url, timeout=30)
data = r.json()
mp4_url = data['Delivery']['PodcastStreams'][0]['StreamUrl']
dl = session.get(mp4_url, stream=True, timeout=300)
with open('output.mp4', 'wb') as f:
    for chunk in dl.iter_content(chunk_size=65536):
        if chunk: f.write(chunk)
```

### HLS via ffmpeg
```bash
ffmpeg -i "master.m3u8_url" -c copy -bsf:a aac_adtstoasc output.mp4
```

### Embedded Captions Extraction
```bash
# Check for subtitle streams
ffprobe -v quiet -show_streams video.mp4 | grep "codec_type=subtitle"

# Extract (usually stream index 2)
ffmpeg -i video.mp4 -map 0:2 -c:s srt output.srt
```

## Panopto Folder Listing

The Panopto folder page (`/Panopto/Pages/Sessions/List.aspx#folderID="{folder_uuid}"`) renders video list via JavaScript. Video links are at:

```
/Panopto/Pages/Viewer.aspx?id={video_uuid}
```

The folder page requires SSO cookies to load. Once authenticated, scrape all `a[href*="Viewer.aspx"]` links to get video IDs.

## Authentication Chain

1. Navigate to video URL → redirects to Panopto Auth/Login
2. Click "Sign in" → Feide SSO org selector (embedded on Panopto page)
3. Type in `#org_selector_filter` to filter orgs
4. Click `li.orglist_item` matching exact org name via `.orglist_name`
5. Click Continue → Feide login form
6. Fill `input#username` and `input#password`
7. Submit → Canvas OAuth confirm
8. Click "OK"/"Ja"/"Godta" → back to Panopto video page
9. Extract `context.cookies()` for API access
