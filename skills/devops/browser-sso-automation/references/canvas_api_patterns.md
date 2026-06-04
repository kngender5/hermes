# Canvas LMS — Practical API Patterns

> Techniques discovered while working with Fagskolen i Nord Canvas instance.

## Module Items (the right way to find downloadable files)

The Canvas Files API (`/api/v1/courses/{id}/files`) often returns 403. Instead, use **module items** which expose downloadable files with their `content_id`:

```bash
# List all modules
curl -s '{BASE}/api/v1/courses/{COURSE_ID}/modules?access_token={KEY}'

# List items in a module (this exposes downloadable files)
curl -s '{BASE}/api/v1/courses/{COURSE_ID}/modules/{MODULE_ID}/items?access_token={KEY}'

# Each item has a type (File, Page, Assignment, ExternalUrl, ExternalTool)
# For type=File, the content_id is the file_id you can download
```

## Downloading Files

Once you have a `content_id` from module items:

```bash
# Get file metadata (includes download URL)
curl -s '{BASE}/api/v1/files/{CONTENT_ID}?access_token={KEY}'

# Download the file (requires -L for redirect following!)
curl -s -L -o 'output.file' '{BASE}/api/v1/files/{CONTENT_ID}/download?access_token={KEY}&download_frd=1'
```

**Pitfall:** The `url` field in the file metadata response is a signed URL that requires a redirect. Use `curl -L` to follow redirects, or use the `/download?download_frd=1` endpoint directly.

## Assignment Attachments

Assignments can have file attachments embedded in the HTML description. Extract file IDs from the HTML:

```python
import re
file_ids = re.findall(r'/files/(\d+)', assignment_description_html)
```

Then download each file using the method above.

## Course Structure

Norwegian Canvas instances often use this structure:
- **Generelt** module: Course plan, general information
- **Forelesninger** module: Lecture pages (often with embedded Panopto videos)
- **Fagstoff** module: Core reading materials (PDFs)
- **Tilleggsstoff** module: Supplementary materials
- **Programvare** module: Software downloads
- **Oppgaver** module: Assignments

Wiki pages (`/courses/{id}/pages/{slug}`) may be disabled for some courses.

## File Naming

Canvas returns URL-encoded filenames. Always sanitize:
```python
import re
safe_name = re.sub(r'[^\w\-.]', '_', filename)
```
