# MEMORY.md — Hermes Agent Memory

**Primary memory: MemPalace** (`~/mempalace/`)
- MCP tools: `mempalace_search`, `mempalace_kg_query`, `mempalace_add_drawer`, etc.
- Wings: general, technical, projects, infra, academic, creative
- Knowledge graph: temporal entity-relationship facts

This file is a fallback/summary. Always query MemPalace first for detailed info.

## Quick Reference

- User: Robert Karlsen, automation engineering student, Kvaløysletta/Tromsø
- School: Fagskolen i Nord (AUT23)
- Email: kng.wizi@gmail.com
- GitHub repo: https://github.com/kngender5/hermes (private)
- ntfy topic: hermes-alerts

## MemPalace Protocol
1. ON WAKE-UP: Call `mempalace_status` to load palace overview
2. BEFORE RESPONDING about any person, project, or past event: call `mempalace_kg_query` or `mempalace_search` FIRST
3. AFTER EACH SESSION: call `mempalace_diary_write` to record what happened
4. WHEN FACTS CHANGE: call `mempalace_kg_invalidate` on old fact, `mempalace_kg_add` for new one
§
2026-06-05: MEMORY.md and USER.md updated to reference MemPalace as primary memory. Fallback files only.