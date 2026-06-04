---
name: kanban-ground-truth-pipeline
description: Kanban workflow for iterative reading/processing of source/course material files with ground truth verification. Workers read curriculum files, extract knowledge, iterate as more info is added, and verify against web sources for regional correctness.
category: devops
triggers:
  - ground truth
  - curriculum processing
  - course material
  - iterative reading
  - source verification
  - material pipeline
  - knowledge extraction
  - study pipeline
  - fagstoff
  - kildeverifisering
---

# Kanban Ground Truth Pipeline

## Purpose

A specialized kanban workflow for systematically reading through source/course material
files (PDFs, SRT transcripts, Canvas pages, web sources) and building a verified
ground truth knowledge base.

## When to Use

Use this workflow when:
- Processing a batch of course material PDFs from Canvas
- Extracting knowledge from lecture transcripts (SRT/whisper)
- Building exam notes that need to be iteratively refined
- Verifying technical claims against official sources (NEK, Nkom, Lovdata)
- Comparing existing notes against new source material to find gaps
- Accumulating knowledge across multiple files with cross-referencing

## Architecture

```
[DISCOVER] → [EXTRACT] → [VERIFY] → [CONSOLIDATE] → [GAP-FILL] → [REVIEW]
     ↑                                                           |
     └────────────────────── iterate ────────────────────────────┘
```

Each stage is a kanban card. Workers are spawned per-file or per-topic depending on
parallelism needs.

## Workflow Stages

### Stage 1: DISCOVER — Inventory all source material

**Use a single subagent** for DISCOVER — it only lists files and creates one JSON.

*Goal:* Scan all available source files and create an inventory.

```
Task: "Discover all EKOM source materials"
Actions:
  1. List all PDFs in curriculum/AUT23_-_Ekom/fagstoff_files/
  2. List all SRT files in curriculum/AUT23_-_Ekom/panopto_recordings/
  3. List all transcript extracts in drafts/transcript_extract_*.md
  4. Check Canvas for new files: canvas files
  5. Output inventory to workspace_groundtruth/inventory.json
  6. Mark each file as: unprocessed | in-progress | extracted | verified
```

Output: `workspace_groundtruth/inventory.json`

### Stage 2: EXTRACT — Read and extract knowledge per file

**CRITICAL — Subagent granularity**: One subagent per source file for files >5MB. Do NOT batch multiple large PDFs into a single subagent — they will timeout at 600s. For files <2MB, batching 2-3 per subagent is acceptable.

**PDF extraction method** (extract to /tmp first):
```bash
pdftotext -layout "/path/to/file.pdf" /tmp/file.txt
# Then read /tmp/file.txt in 500-line chunks
```

**SRT extraction method** (sample, don't fully parse):
```bash
grep -oE '[A-Za-zæøåÆØÅ]{4,}' file.srt | sort | uniq -c | sort -rn | head -20
```

See `references/execution-notes.md` for detailed timing data and pitfalls from production runs.

*Goal:* Read each source file and extract structured knowledge.

One card per file (parallelizable). For a PDF:
```
Task: "Extract knowledge from 2025 EKOM - Del 1.pdf"
Actions:
  1. Run: pdftotext -layout "curriculum/AUT23_-_Ekom/fagstoff_files/2025 EKOM - Del 1.pdf" -
  2. Read output in chunks (500 lines at a time for large files)
  3. Extract:
     - Main topics (hierarchical)
     - Formulas (with LaTeX)
     - Tables (with all values)
     - Definitions (Norwegian + English)
     - Standard references (NEK, ITU-T, ISO)
     - Numerical values and specifications
     - Exam-relevant tips
  4. Output to workspace_groundtruth/extracts/ekom_del1.json
  5. Mark file as "extracted" in inventory
```

For SRT transcripts:
```
Task: "Extract knowledge from WEB_12_februar_2026.srt"
Actions:
  1. Read SRT file in chunks (500 lines)
  2. Parse to plain text (remove timestamps, sequence numbers)
  3. Extract technical terms, formulas, definitions
  4. Identify main topics discussed
  5. Note exam-relevant statements
  6. Output to workspace_groundtruth/extracts/web_12_feb.json
  7. Mark as "extracted" in inventory
```

### Stage 3: VERIFY — Cross-reference and verify claims

*Goal:* Verify technical claims against official sources.

```
Task: "Verify fiber splitter loss values against NEK/ITU-T standards"
Actions:
  1. Read all extracts from Stage 2
  2. Identify all numerical claims:
     - Splitter loss values
     - Fiber attenuation coefficients
     - GPON SFP specifications
     - Frequency bands
     - Signal level requirements
  3. For each claim, verify against:
     - laws/COMPLIANCE_PROTOCOL.md (local cache)
     - NEK standard references
     - ITU-T recommendations (via web search if needed)
     - Nkom regulations
  4. Mark each claim as: VERIFIED | DERIVED | PROVISIONAL | CONFLICT
  5. Output verification report to workspace_groundtruth/verification.json
```

Web verification pattern:
```
For each unverified claim:
  1. Search: site:nek.no "<claim keyword>" OR site:nkom.no "<claim keyword>"
  2. Search: site:lovdata.no "<law reference>"
  3. Search: site:itu.int "<recommendation>"
  4. If Norwegian regional info needed: add "Norge" or "Norway" to query
  5. Cross-check with local curriculum materials
  6: Record source URL and status
```

### Stage 4: CONSOLIDATE — Merge all extracts into unified notes

**Do NOT delegate CONSOLIDATE to subagents.** Reading 20+ extract JSONs and writing large output documents (>100KB) exceeds subagent context limits and timeout constraints. Always execute CONSOLIDATE directly in the main agent.

*Goal:* Combine all verified extracts into consolidated exam notes.

```
Task: "Consolidate all EKOM extracts into unified notes"
Actions:
  1. Read all extraction JSON files from Stage 2
  2. Read verification report from Stage 3
  3. Merge topics hierarchically (avoid duplicates)
  4. Resolve conflicts using verification status
  5. Generate:
     a. Markdown notes → drafts/EKOM_EKSAMENSNOTATER.md
     b. HTML with diagrams → drafts/EKOM_EKSAMENSNOTATER.html
     c. Update Jupyter notebook → drafts/EKOM_Eksamensnotater_v2.ipynb
  6. Update the extraction-status.json tracker
```

### Stage 5: GAP-FILL — Identify and fill knowledge gaps

*Goal:* Find topics covered in the curriculum but missing from notes.

```
Task: "Identify gaps in EKOM notes vs Canvas syllabus"
Actions:
  1. Read Canvas syllabus: canvas assignments
  2. Compare against current notes (markdown headings)
  3. Identify topics in syllabus but missing from notes
  4. For each gap:
     a. Check if source material exists but wasn't extracted → create EXTRACT card
     b. Check if source material is missing → flag for user
     c. Estimate importance (based on exam frequency)
  5. Output gap report to workspace_groundtruth/gaps.json
  6. Create new EXTRACT cards for gaps that can be filled
```

### Stage 6: REVIEW — Human or agent review of consolidated output

*Goal:* Final quality check before considering the iteration complete.

```
Task: "Review consolidated EKOM exam notes"
Actions:
  1. Read all generated output files
  2. Check for:
     - Completeness (all topics covered)
     - Accuracy (formulas match source)
     - Formatting (consistent markdown)
     - Norwegian technical terms (bokmål)
     - IEEE citation format
  3. Create new cards for any issues found
  4. Mark pipeline iteration as complete if no blocking issues
```

## Iteration Pattern

When NEW files are added (new lecture recorded, new PDF uploaded):

1. **DISCOVER** runs again — picks up new files
2. **EXTRACT** cards spawned for each new file
3. **VERIFY** re-runs on new claims
4. **CONSOLIDATE** merges new knowledge into existing notes
5. **GAP-FILL** checks if new material fills existing gaps
6. **REVIEW** validates the updated output

The pipeline is idempotent — re-running on already-processed files skips them
(checked via inventory.json status).

## Assignee Strategy

For a single-profile setup (default):
- All stages run on the `default` profile
- Sequential execution per stage, parallel within stage

For multi-profile setups:
- `default` or `researcher`: DISCOVER, EXTRACT, GAP-FILL
- `verifier` or `researcher`: VERIFY
- `writer`: CONSOLIDATE
- `reviewer`: REVIEW

## File Layout

See `references/extract-schema.md` for the JSON schema of extract files and inventory.

```
~/projects/study-workbench/
├── workspace_groundtruth/
│   ├── inventory.json          # All source files + status
│   ├── extraction-status.json  # Track which extracts are merged
│   ├── extracts/
│   │   ├── ekom_del1.json      # Per-file extraction results
│   │   ├── ekom_del2.json
│   │   └── web_12_feb.json
│   ├── verification.json      # Verified claims + sources
│   ├── gaps.json              # Identified knowledge gaps
│   └── pipeline-log.md        # Human-readable pipeline log
├── drafts/
│   ├── EKOM_EKSAMENSNOTATER.md
│   ├── EKOM_EKSAMENSNOTATER.html
│   └── EKOM_Eksamensnotater_v2.ipynb
└── curriculum/
    └── AUT23_-_Ekom/
        ├── fagstoff_files/    # Source PDFs
        └── panopto_recordings/ # Lecture recordings + SRT
```

## Ground Truth Verification Sources

Priority order for verification:
1. **Local cache** — laws/COMPLIANCE_PROTOCOL.md, NEK reference files
2. **Norwegian authorities** — Nkom (nkom.no), Lovdata (lovdata.no), DSB (dirforEach.no)
3. **Standards bodies** — NEK (nek.no), ITU-T (itu.int), ISO (iso.org)
4. **Industry** — Fiberforeningen, Telenor, Altibox technical docs
5. **Academic** — arXiv, university course pages for technical concepts
6. **International** — Wikipedia (as fallback only, mark as PROVISIONAL)

## Regional/Language Verification

For Norwegian-specific content:
- Always verify against Norwegian sources first (Nkom, Lovdata, NEK)
- Use Norwegian search terms: "ekom-forskriften", "NEK 400", "Nkom"
- For EU directives: check Norwegian implementation (FOR-forskrifter)
- Preserve original Norwegian legal text when citing §-references
- Cross-check EEA relevance where EU directives apply to Norway
