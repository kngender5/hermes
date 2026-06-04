# Canvas Module Item Download Pattern

When `canvas files` or `canvas download --only <course_id>` returns 403/unauthorized,
use the module items API to discover and download files directly.

## Workflow

### 1. List modules
```
GET /api/v1/courses/{id}/modules?access_token={key}&per_page=50
```
Returns module IDs, names, positions, item counts.

### 2. List items per module
```
GET /api/v1/courses/{id}/modules/{module_id}/items?access_token={key}&per_page=100
```
Item types:
- `File` — has `content_id` = file_id, downloadable via `/files/{id}/download`
- `Page` — wiki page, may contain embedded Panopto/video content
- `ExternalUrl` — external link (e.g., Panopto LTI tool, Siemens docs)
- `ExternalTool` — LTI tool (e.g., Panopto at `external_tools/309`)
- `Assignment` — links to assignment, attachments in description HTML

### 3. Download file by ID
```
GET /api/v1/files/{file_id}?access_token={key}  # metadata
GET /files/{file_id}/download?download_frd=1    # actual file (follow redirects)
```

### 4. Extract assignment attachments
Assignment description HTML embeds file attachment links. Parse with regex:
```python
file_ids = re.findall(r'/files/(\d+)/download', html)
```
Then download each file_id as above.

### 5. Handle Panopto content
- Panopto LTI tool: `GET /api/v1/courses/{id}/external_tools/{tool_id}`
- Page items with Panopto: page body has embedded iframes/links
- Delivery IDs may NOT be extractable from Canvas API — use browser SSO

## Example: Kurs 1624 (Programmering og digitalisering)

Modules:
- 7381: GENERELT (Gjennomføringsplan, Dokumentmaler page)
- 7450: FORELESNINGER (6 pages, 4 with Panopto)
- 7375: FAGSTOFF (3 PDF files)
- 7377: TILLEGGSSTOFF (4 PDF files + 1 external URL)
- 7378: PROGRAMVARE (Factory IO page)
- 7379: OPPGAVER (7 assignments)

Files discovered via module items API (not via `canvas files`):
- 378439: Gjennomføringsplan.pdf
- 351729: Programmerbare_systemer.pdf
- 351730: Industriell_datakommunikasjon.pdf
- 378373: Siemens_TIA_Videregaende_programmering.pdf
- 351734-393317: Tilleggsstoff PDFs
- 351862-429226: Assignment PDFs and Kontinuasjon attachments