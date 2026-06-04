# Referanse: Canvas LMS og kursoppsett

## Canvas API-konfigurasjon
Fil: `~/.hermes/.env` (globalt for alle Hermes-sesjoner)

```
CANVAS_BASE_URL=https://fagskoleninord.instructure.com/
CANVAS_API_KEY=<token>
# Bakoverkompatibilitet med eldre skript:
CANVAS_API_URL=https://fagskoleninord.instructure.com/
CANVAS_API_TOKEN=<token>
```

**Pitfall:** Eldre skript (f.eks. `extract_canvas.py`) bruker `CANVAS_API_URL`/`CANVAS_API_TOKEN`.
Nye skript bruker `CANVAS_BASE_URL`/`CANVAS_API_KEY`. Begge navneformater bør settes i `.env`.

**Hente API-token:**
1. Logg inn på https://fagskoleninord.instructure.com
2. Settings → Approved Integrations → + New Access Token
3. Kopier token (starter med `12677~...`)

## Instansinfo
- **Instans:** Fagskolen i Nord (`fagskoleninord.instructure.com`)
- **Tidssone:** Europe/Stockholm
- **Lagringskvote per kurs:** 1048 MB

## Aktive kurs (AUT23-kohorten, per 2026-05-25)
| ID   | Kurs |
|------|------|
| 1627 | AUT23 - Ekom (Elektroniske kommunikasjonssystemer) |
| 1616 | AUT23 - Elektriske systemer |
| 1617 | AUT23 - Elektroniske systemer |
| 1622 | AUT23 - Hovedprosjekt |
| 1543 | AUT23 - Klasserom |
| 1621 | AUT23 - Måle- og reguleringsteknikk |
| 1624 | AUT23 - Programmering og digitalisering |
| 1625 | AUT23 - Robot og motordrifter |
| 1619 | AUT23 - Styringssystemer |
| 1614 | AUT23/ITDS23 - LØM |
| 1601 | AUT23/ITDS23 - Realfaglige redskap |
| 1605 | AUT23/ITDS23 - Yrkesrettet kommunikasjon |
| 1702 | ELK23-A - Y-komm |
| 816  | IKT informasjon |

Totalt 133 oppgaver, 14 aktive kurs.

## Canvas CLI-verktøy
`scripts/canvas` — CLI-verktøy for Canvas LMS. Symlinket til `~/.local/bin/canvas`.

Kommandoer:
- `canvas courses` — liste aktive kurs
- `canvas assignments` — alle oppgaver sortert etter frist
- `canvas assignments <id>` — oppgaver for ett kurs
- `canvas files` — nedlastbare filer per kurs
- `canvas download` — last ned alle filer + sider til `curriculum/`. Støtter `--skip ID,ID,...` for å hoppe over store fag, `--only ID,ID,...` for kun bestemte fag, `--no-pages` for å hoppe over wiki-sider.
- `canvas syllabus` — eksportér oppgaveoversikt til `curriculum/syllabus_master.xlsx`
- `canvas calendar` — kommende frister (14 dager)
- `canvas grades` — karakterer per kurs
- `canvas announce` — siste kunngjøringer

## Installasjonsnotater
- `canvasapi` Python-bibliotek: `pip install canvasapi --break-system-packages`
- typst: Ikke i apt — installer fra GitHub releases
- GPU: RTX 4060 CUDA → whisper-ctranslate2 --device cuda --compute_type float16
- Tesseract OCR: tesseract -l nor+eng for norske PDF-scans
- Ved pip-install på Ubuntu: bruk alltid `--break-system-packages` (PEP 668)
