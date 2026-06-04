# Ground Truth Pipeline — Execution Notes

## Subagent Granularity for EXTRACT Stage

**CRITICAL**: One subagent per source file for files >5MB. Do NOT batch multiple large PDFs into a single subagent — they will timeout at 600s.

**Pattern that works (one file per subagent):**
```
delegate_task(goal="Extract knowledge from 2025 EKOM - Del 1.pdf (4.7 MB)")
delegate_task(goal="Extract knowledge from 2025 EKOM - Del 2 (701).pdf (9.9 MB)")
```

**Pattern that fails (batching large PDFs):**
```
delegate_task(goal="Extract knowledge from Del 1, Del 2, Del 3, Del 4 (30 MB total)")
# → TIMEOUT at 600s
```

For files <2MB, batching 2-3 per subagent is acceptable.

## PDF Text Extraction Best Practice

Always extract to `/tmp` first, then read from there:
```bash
pdftotext -layout "/path/to/file.pdf" /tmp/file.txt
# Then read /tmp/file.txt in 500-line chunks
```

**Pitfall**: Some PDFs have layout artifacts (single-character lines from scanned/OCR'd documents). For these, mark extraction_status as "partial".

## SRT Transcript Extraction

Whisper-generated SRT files contain Norwegian transcription artifacts. Use grep for key terms:
```bash
grep -oE '[A-Za-zæøåÆØÅ]{4,}' file.srt | sort | uniq -c | sort -rn | head -20
```
Mark status as "partial" — full structured extraction is not worthwhile.

## CONSOLIDATE Stage — Do NOT Delegate

Always execute CONSOLIDATE directly. Reading 20+ extract JSONs and writing large documents exceeds subagent limits.

## Typical Pipeline Timing (23 PDFs + 15 SRTs)

| Stage | Method | Time |
|-------|--------|------|
| DISCOVER | Single subagent | ~5 min |
| EXTRACT | 1 subagent per large PDF | ~30-60 min total |
| VERIFY | execute_code directly | ~1 min |
| CONSOLIDATE | Direct | ~10 min |
| GAP-FILL | Direct or subagent | ~5 min |
| REVIEW | Direct | ~2 min |

Total: ~60-90 minutes for 38 source files.
