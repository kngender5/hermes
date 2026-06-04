---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
version: 2.3.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pdftotext (fastest) | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|---------------------|-----------------|---------------------|
| **Text-based PDF** | ✅ (layout mode) | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ❌ | ✅ (90+ languages) |
| **Tables** | Basic | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ❌ | ✅ |
| **Speed** | Instant | Instant | ~1-14s/page |
| **Install** | Pre-installed | pip install | ~3-5GB download |

**Decision order:** `pdftotext -layout` first (fastest, preserves layout) → pymupdf if programmatic access needed → marker-pdf only for OCR/scanned docs/equations.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```
## Handling Empty Text Extraction

Sometimes standard text extraction (pymupdf, pdftotext) returns empty text even though the PDF contains text. This happens when:
  - The text is actually embedded as images (scanned documents without OCR layer)
  - The PDF uses unusual fonts or encoding that the extractor can't interpret
  - The PDF is encrypted or restricted

In such cases, fall back to OCR:
1. Convert PDF pages to images: `pdftoppm -r 150 -png document.pdf page`
2. Run OCR on each image: `tesseract page-*.png stdout -l nor+eng > output.txt` (adjust language as needed)
3. Combine the OCR output

You can automate this with a helper script. Consider installing `ocrmypdf` which does this internally: `ocrmypdf input.pdf output.pdf --skip-text` then extract text from the OCR'ed PDF.

Note: OCR is slower and less accurate than native text extraction, so only use when needed.

## Batch PDF Processing for Knowledge Bases

When processing multiple PDFs into structured knowledge documents (e.g., extracting technical content from a course library):

**Recommended workflow:**
1. Extract all PDFs to text in batch:
   ```bash
   for f in /path/to/*.pdf; do
     pdftotext -layout "$f" "/tmp/$(basename $f .pdf).txt"
   done
   ```
2. Read extracted text files directly in the main agent (not via subagents — subagents timeout on large file I/O + document generation tasks)
3. Organize content into structured markdown documents by topic/category
4. Write documents directly using `write_file`

**When to use OCR:** If `pdftotext` produces garbled or empty output for a PDF, the content may be image-based. Use the OCR fallback above. For Norwegian language materials, use `-l nor+eng` with Tesseract.

**Important:** Do NOT delegate large document generation tasks (reading multiple source files + writing large output) to subagents. The 600s timeout is insufficient for this pattern. Handle it in the main agent.

## Notes

- `web_extract` is always first choice for URLs
- `pdftotext -layout` is the fastest local extraction for text-based PDFs — use as first attempt
- pymupdf is the safe default for programmatic extraction — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
