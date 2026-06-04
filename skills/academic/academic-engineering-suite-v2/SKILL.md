---
name: academic-engineering-suite-v2
description: Advanced high-performance pipeline for documentation extraction, mathematical modeling, local VLM RAG searching, IEC PLC validation, telemetry plotting, Typst compilation, and exam preparation.
category: academic
triggers:
  - Canvas data
  - canvas courses
  - canvas assignments
  - canvas download
  - canvas pages
  - Panopto video
  - Panopto folder
  - Panopto captions
  - whisper transcription
  - Feide SSO
  - engineering equations
  - NEK 400
  - Maskinforskriften
  - risk assessment
  - IEEE report
  - PLC code
  - plot responses
  - compile PDF
  - exam prep
  - formelsamling
  - pensumsrevisjon
  - arbeidsområde
  - study-workbench
  - ingeniørarbeid
---

# Academic Engineering Execution Suite V2

## Referanser
- `references/workspace-provisioning.md` — Katalogstruktur, filkrav, pitfalls
- `references/siteringsregler.md` — IEEE- og Kildekompasset-siteringsmaler
- `references/compliance-matrix.md` — fullstendig matrise over norske forskrifter og EU-standarder
- `references/uit_setup.md` — Canvas API-konfigurasjonsreferanse, kursliste, CLI-verktøydokumentasjon
- `references/ekom-curriculum-map.md` — EKOM-fagets pensumdekning: fil-til-tema-mapping, nøkkeltabeller, formler, output-filer
- `references/ekom-exam-patterns.md` — EKOM eksamensmønstre: fiberbudsjett, kabel-TV signalnivå, splitter-beregninger, separasjonsavstand, nøkkelreferansetabeller, vanlige eksamensfeil

## Scripts
- `scripts/canvas` — Canvas LMS CLI (courses, assignments, files, download, syllabus, calendar, grades, announce, lectures, extract-captions). Symlink til ~/.local/bin/canvas.
- `scripts/ingest_lecture.sh` — Panopto lecture ingestion pipeline (download → audio extract → caption check → whisper)
- `scripts/clean_and_whisper.py` — SRT cleaning + whisper transcription for videos without captions
- `scripts/canvas_panopto_captions.py` — Panopto caption/transcript endpoint testing

## Kalkulatorer
- `workspace_calculations/ekom_solver.py` — Smart utregningsverktøy v3.0 (8 systemer: fiber, dB, spenningsfall, last, EMC, kabel-TV, Shannon, DOCSIS)
- `workspace_calculations/ekom_calculator.py` — Funksjonsbasert kalkulator v3.0 (fiber, dB, spenningsfall, last, EMC, kabel-TV, PoE, DOCSIS)
- `workspace_calculations/ekom_kalkulator.ipynb` — Interaktiv Jupyter-kalkulator (ipywidgets)
- `workspace_calculations/otdr_simulator.py` — OTDR-trace-simulator

## Compliance Verification
See `references/compliance-verification.md` for Norwegian regulatory source priority,
search patterns, and claim status markers. Key rule: always cite Norwegian sources first
(Nkom, Lovdata, NEK), verify EU directives against Norwegian FOR-forskrift implementation. (FEL, NEK 400, Ekomloven, NEK 700, maskinsikkerhet, AML, fiberoptikk, kabel-TV, DOCSIS, PoE)
- `curriculum/AUT23_-_Ekom/fagstoff_files/` — Kildemateriale (14 PDF-filer)
- `curriculum/AUT23_-_Ekom/panopto_recordings/` — Forelesningsopptak + transkripsjoner

## Ground Truth Pipeline
Se `kanban-ground-truth-pipeline` skill for detaljert workflow for iterativ
kildeprosessering og verifisering. Kort oppsummert:
1. DISCOVER — Inventarer alle kildefiler
2. EXTRACT — Leser hver fil og ekstraherer strukturert kunnskap
3. VERIFY — Kryssverifiserer mot offisielle kilder (NEK, Nkom, Lovdata, ITU-T)
4. CONSOLIDATE — Samler til enhetlige eksamensnotater
5. GAP-FILL — Identifiserer og fyller kunnskapshull
6. REVIEW — Kvalitetskontroll av output

Nye filer legges til → pipeline kjører automatisk på nye elementer (idempotent).

## Sandboxed Dependency Provisions

```bash
# Python-pakker
uv pip install canvasapi pandas openpyxl pypdf python-docx sympy numpy scipy chromadb langchain-community matplotlib yt-dlp whisper-ctranslate2 jupyter notebook ipywidgets

# Systempakker (apt)
sudo apt-get install -y ffmpeg tesseract-ocr tesseract-ocr-nor tesseract-ocr-eng pandoc texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-lang-european poppler-utils graphviz jq bc tree htop exiftool

# Typst (IKKE i apt — installer fra GitHub releases)
curl -fsSL "https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz" -o /tmp/typst.tar.xz
tar -xf /tmp/typst.tar.xz -C /tmp/
sudo mv /tmp/typst-x86_64-unknown-linux-musl/typst /usr/local/bin/
chmod +x /usr/local/bin/typst
```

**Merk:** `typst` er ikke tilgjengelig i standard Ubuntu-apt-repoet. Den installeres alltid fra GitHub releases (se over). Ved pip-installasjon på system-Python, bruk `--break-system-packages` flagget (PEP 668).

## UiT-spesifikk konfigurasjonsreferanse
Se `references/uit_setup.md` for Canvas API-tokenoppsett, kurskoder og installasjonsnotater for WSL2-miljøet. GPU: RTX 4060 CUDA.

- `references/panopto-download.md` — Panopto video/caption download: Feide SSO flow, DeliveryInfo API, embedded caption extraction, whisper transcription
- `references/canvas-module-download.md` — Canvas module item download pattern: API-based file discovery when `canvas files` returns 403

## GPU/CUDA Configuration for Whisper

`whisper-ctranslate2` uses CUDA automatically but may fail with `libcublas.so.12 not found`. Fix:
```bash
sudo apt-get install -y libcublas12
# If still failing, set env var:
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```
GPU: RTX 4060, use `compute_type=float16` for speed.

## Avanserte Sub-Agent-allokeringer (RPC-moduler)

1. **DOC-PARSE:** Ekstraherer rådata, pensumlister og datablader fra PDF/Excel.
2. **AUDIO-PARSE:** Henter og transkriberer Panopto/Zoom-videoer. For Panopto: bruk DeliveryInfo API for nedlasting (`PodcastStreams[0].StreamUrl`), ekstrahér embedded captions med ffmpeg, eller transkriber med whisper-ctranslate2. Se `references/panopto-download.md` for fullstegvis oppskrift inkludert Feide SSO-flow.
3. **MATH-SOLVE:** Kjører symbolske beregninger via `sympy`. Enforcer streng LaTeX-visning ($$...$$).
4. **REG-CHECK:** Kjører kryssverifikasjon mot `COMPLIANCE_PROTOCOL.md` og genererer norske samsvarserklæringer.
5. **DATA-RAG:** Semantisk og lynhurtig lokalt vektorsøk i NEK-standarder og manualer lagret i `./laws/`.
6. **PLC-CHECK:** Validerer logikk og syntaks for Strukturert Tekst (ST) etter IEC 61131-3-standarden under `./plc_code/`.
7. **PLOT-MATRIC:** Kjører simuleringer og genererer automatiske plots (sprangrespons, bodediagrammer) til `./artifacts/`.
8. **PROJECT-WRITE / COMPILER-NODE:** Kompilerer lynraske ingeniøravhandlinger direkte fra Markdown til ferdig PDF ved hjelp av Typst-CLI.
9. **EXAM-PREP:** Kjører `audit_syllabus.py` for å sammenligne Canvas-data mot eksamensutkast under `./drafts/`. Genererer strukturerte formelsamlinger og tvinger frem trinnvise matematiske og regulatoriske løsningsmetodikker (Løsningsworkflows) i feilfritt norsk bokmål med IEEE-formatering.

      **Ved eksamensnotatsarbeid — faktisk workflow (2026-05-25):**
   1. Finn alle relevante PDF-filer: `find <dir> -type f -name "*.pdf"`
   2. Ekstraher tekst fra hver PDF: `pdftotext -layout "$f" -` (beholder tabellstruktur)
   3. Les systematisk gjennom hver PDF og katalogiser hovedtemaer, formler, tabeller, definisjoner
   4. Kartlegg mot studieplan/læringsmål for å identifisere dekningsgrad
   5. Lag to formater:
      - **Markdown** (`EKOM_EKSAMENSNOTATER.md`) — rask referanse, søkbar, printbar
      - **HTML med SVG-diagrammer** (`EKOM_EKSAMENSNOTATER.html`) — visuelt rikt med nettarkitektur, frekvensspekter, budsjett-diagrammer
   6. Inkluder: formler (LaTeX-stil i kodeblokker), tabeller (alle verdier), definisjoner (norsk + engelsk), arkitektur-SVG-er, eksamentips
   7. Bruk subagents for parallel ekstraksjon av store PDF-er (pdftotext + head for første pass, deretter målrettet lesing)
   8. Ved store PDF-er (>500 linjer): les i chunk med offset/limit, ikke alt på en gang
   9. Bruk `write_file` for å skrive output — del opp i to filer (md + html) hvis >30KB
   10. Inkluder alltid: lovhenvisninger med §-nummer, standardhenvisninger med fullt navn, splitterdempning-tabell, fiberbudsjett-eksempel, kontakttype-oversikt
10. **CANVAS-FETCH:** Henter kursdata, oppgaver, filer, karakterer og kunngjøringer fra Canvas LMS via `scripts/canvas`-CLI. Se `references/uit_setup.md` for API-konfigurasjon og kommandoreferanse.

## Typst Compilation Pitfalls

**CRITICAL:** Typst uses its own math syntax, NOT LaTeX:
- Use `times` NOT `\times` for multiplication
- Use `div` NOT `\div` for division  
- Use `dot` NOT `\cdot` for dot product
- Use `^` for superscript, `_` for subscript (same as LaTeX)
- Greek letters: `alpha`, `beta`, `Delta`, `Sigma` (NOT `\alpha`, `\beta`)
- Subscript with quotes: `P_"mottatt"` (NOT `P_{\text{mottatt}}`)
- Fractions: `a / b` or `frac(a, b)` (NOT `\frac{a}{b}`)

**Footer counter fix:** Wrap in `context`:
```typst
footer: [
  #align(center)[#context counter(page).display("1 / 1")]
]
```

**Compilation command:**
```bash
cd ~/projects/study-workbench/drafts && typst compile eksamensnotater.typ OUTPUT.pdf
```

## EXAM-PREP: Transcript Extraction Workflow (2026-05-25)

When extracting from whisper transcripts for exam notes:

1. **Spawn parallel subagents** — each gets 1-2 SRT files to process
2. **Each subagent reads the COMPLETE file** using offset/limit chunks
3. **Extract:** technical terms, formulas, definitions, standards, numerical values, exam tips
4. **Output** to `drafts/transcript_extract_<video_name>.md`
5. **After all subagents complete**, read all extracts and build consolidated exam notes
6. **Cross-reference** with existing PDF materials and compliance matrix
7. **Generate both Markdown AND PDF** (via Typst)

**Subagent task template:**
```
Context: Files: <path_to_srt> (size, lines). Norwegian whisper transcript from EKOM lecture.
Goal: Extract all key technical content. 1) Parse SRT to extract text, 2) Identify technical terms/formulas/definitions/standards, 3) Extract numerical values/specs, 4) Identify main topics, 5) Note exam tips. Output as structured markdown. Write to drafts/transcript_extract_<name>.md
Toolsets: [file, terminal]
```

**SRT reading pattern for large files:**
- Read in chunks of 500 lines using read_file offset/limit
- SRT files can be 10,000+ lines — never read all at once

## Exam Solution Format (2026-05-26)

When solving exam questions or providing exam-style answers:

1. **Show ALL calculations** — every step must be visible, not just final results. The user explicitly said "vis alle utregninger i svar". Never skip arithmetic steps.

2. **Answer as if taking the exam** — use first-person, direct exam-style responses ("Svar:", "Utregning:", "Formel:"). The user said "svar som om du besvarer eksamensoppgaver".

3. **Use the Jupyter notebook tools actively** — when calculators/tools exist in the notebook, reference them and use them for verification. The user said "bruk notatboken og kalkulatoren samt verktøyene til å løse oppgavene".

4. **Verify against provided solutions** — when sensorveiledning or answer keys are available, cross-reference and confirm results match. The user said "verifiser svar". Always state whether your answer matches the key.

5. **Structure for each sub-question** — clearly label a), b), c) etc. Show the formula first, then substitution, then result with unit.

6. **Norwegian technical terms** — use Norwegian terminology throughout (e.g. "dempning" not "attenuation", "budsjett" not "budget", "skjøt" not "splice").

7. **Include sensorveiledning alignment** — when the sensorveiledning specifies point thresholds or acceptable deviations, note whether the answer meets those criteria.

## Output Format Preference

When user says "disregard last steer" or gives a correction: follow the NEW instruction immediately without explaining or justifying. Do not carry forward contradicted framing from earlier in the conversation.

## Konsolideringsmerknad
V1 (`academic-engineering-suite`) er funksjonellt overtatt av V2. V2 inneholder alle V1s moduler plus DATA-RAG, PLC-CHECK, PLOT-MATRIC, COMPILER-NODE, EXAM-PREP og CANVAS-FETCH. V1 beholdes for bakoverkompatibilitet men bør ikke utvides.

## Canvas API — Module Items Pattern (2026-05-26)

`canvas files` and `canvas download` often return 403 for file access. Use the **module items API** instead:

```bash
# 1. Get modules for a course
curl -s "$CANVAS_BASE_URL/api/v1/courses/{course_id}/modules?access_token=$CANVAS_API_KEY"

# 2. Get items for each module (reveals file IDs, page URLs, external tools)
curl -s "$CANVAS_BASE_URL/api/v1/courses/{course_id}/modules/{module_id}/items?access_token=$CANVAS_API_KEY"

# 3. Download file by ID (from module item content_id)
curl -s -L -o output.pdf "$CANVAS_BASE_URL/api/v1/files/{file_id}?access_token=$CANVAS_API_KEY"
```

Module items reveal: Files (type=File, content_id=file_id), Pages (type=Page), ExternalUrl, ExternalTool (e.g., Panopto LTI), Assignments. This is the most reliable way to discover all course materials.

## Pitfalls (2026-05-25)

### Canvas Files Unauthorized Pattern
When `canvas files` or `canvas download --only <course_id>` returns
`"unauthorized"` for a specific course (while other courses work), the API token
lacks file-scoped access for that course. Mitigation:
1. Use Feide SSO browser login to access files via the web UI
2. Navigate to `/courses/{id}/files` and `/courses/{id}/pages` in browser
3. Download materials manually via browser automation
4. This pattern has been observed specifically for kurs 1624 (Programmering og digitalisering)

### Canvas Module Item Download Pattern
When `canvas files` or `canvas download` returns 403 for a course, use the module items API
to discover and download files directly:
```bash
# 1. List modules to find module IDs
curl -s '{CANVAS_BASE_URL}/api/v1/courses/{id}/modules?access_token={key}&per_page=50'

# 2. List items per module
curl -s '{CANVAS_BASE_URL}/api/v1/courses/{id}/modules/{module_id}/items?access_token={key}&per_page=100'

# 3. Items with type="File" have content_id = file_id
#    Items with type="Page" are wiki pages with embedded content
#    Items with type="ExternalUrl" are links (e.g., Panopto LTI tool)
#    Items with type="Assignment" link to assignment details

# 4. For assignment attachments (files listed in assignment description HTML):
#    Extract file IDs from description using regex: /files/(\d+)/download
#    Then download: curl -s -L -o output.pdf '{CANVAS_BASE_URL}/files/{file_id}/download?access_token={key}'
#    The assignment description HTML embeds attachment links — parse with regex, not the API

# 5. For Page items with Panopto content:
#    Page body references Panopto via embedded HTML (iframes, links)
#    Delivery IDs may NOT be extractable from Canvas API alone
#    Use Feide SSO browser login to navigate to the page and extract from rendered HTML
```

### Feide SSO with Credentials
When automating Feide SSO login with known credentials:
1. Navigate to course URL → redirects to Feide org selector
2. Find `#org_selector_filter` input
3. **CRITICAL:** Use `page.keyboard.type("troms fylkeskommune", delay=50)` NOT `.fill()` — Feide's typeahead filter doesn't respond to programmatic fill
4. Wait 2-3s, then click `li.orglist_item` with matching `.orglist_name`
5. Click Continue button
6. Fill `input#username` and `input#password` (these DO respond to `.fill()`)
7. Submit, handle OAuth confirm ("Godta")
8. Save cookies immediately: `json.dump(await context.cookies(), f)`
9. **In headless mode:** `DISPLAY=:0` must be set AND Playwright must use `executable_path="/usr/bin/chromium-browser"` with `--no-sandbox`
10. **Interactive mode (user watching):** launch non-headless so user can interact

### browser_tool Timeout Pattern
The `browser_navigate` tool consistently times out (60s) on HTTPS pages that redirect to SSO.
This is a known limitation — use Playwright scripts via `terminal` instead for SSO flows.
The `browser_navigate` tool works fine for non-auth pages.

### WSLg Chromium Launch
Launching Chromium browser on WSLg for interactive use:
```bash
DISPLAY=:0 chromium-browser --no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage &
# Browser window appears on Windows desktop
# Downloads go to /mnt/c/Users/rkarl/Downloads (not WSL home)
```

### Plan Skill Workflow-Capture
When the plan skill is invoked and the task involves processing lecture recordings
or course transcripts, the plan MUST include a "Workflow Capture" section that
instructs the executing agent to create class-level skills for any detailed
workflows found in source material. This is a first-class planning requirement.
The user wants domain knowledge from lectures preserved as reusable skills.

### Jupyter Notebook Cell Corruption
When writing Jupyter notebooks via Python json.dump, cell source content can get split
into single-character strings instead of proper line strings. Always verify with:
```python
import json
with open('notebook.ipynb') as f:
    nb = json.load(f)
for i, cell in enumerate(nb['cells']):
    src = cell.get('source', [])
    if len(src) > 100 and all(len(l.strip()) <= 1 for l in src if l.strip()):
        print(f"Cell {i}: CORRUPTED ({len(src)} lines)")
```
Fix by rewriting cell source as proper line strings (each ending with \\n). This happens
when content is written character-by-character instead of line-by-line.

### Compliance Verification Pattern
When verifying technical claims against Norwegian regulatory sources, priority order:
1. Local cache (laws/COMPLIANCE_PROTOCOL.md, NEK reference files)
2. Norwegian authorities: Nkom (nkom.no), Lovdata (lovdata.no)
3. Standards bodies: NEK (nek.no), ITU-T (itu.int), ISO (iso.org)
4. Industry: Fiberforeningen, operator docs
5. Academic: arXiv, university pages
6. International fallback: Wikipedia (mark PROVISIONAL)
Always cite Norwegian sources first. For EU directives, check Norwegian FOR-forskrift
implementation via Lovdata. Use `site:nek.no` and `site:lovdata.no` for targeted search.

### OTDR Physical Model
For realistic OTDR traces model: fiber break (Fresnel -14.7 dB then noise floor),
connectors (PC: -45 dB refl, UPC: -50 dB, APC: -60 dB + loss), splices (-70 dB refl + 0.1 dB loss),
macro bends (2-5 dB loss, no reflection), bad splices (0.3-1.0 dB + small refl).
See `workspace_calculations/otdr_simulator.py` v2 for reference.
