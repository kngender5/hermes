---
name: academic-engineering-suite
description: High-performance pipeline for data extraction, mathematical modeling, video transcription, and compliance validation. Also handles provisioning of isolated academic workspaces with SOUL.md, MEMORY.md, compliance protocols, IEEE templates, and automation scripts.
category: academic
triggers:
  - Canvas data
  - Panopto video
  - engineering equations
  - NEK 400
  - Maskinforskriften
  - risk assessment
  - IEEE report
  - arbeidsområde
  - study-workbench
  - ingeniørarbeid
---

# Academic Engineering Execution Suite

## Formål

Dette ferdigheten dekker hele leiingen for akademisk ingeniørarbeid: fra opprettelse av isolerte arbeidsområder, via datautvinning og matematisk modellering, til regulatorisk samsvarsverifikasjon og teknisk rapportskriving.

## Overordnede Arbeidsflyt

### Fase 1 — Opprettelse av Arbeidsområde
Se `references/workspace-provisioning.md` for fullstendig oppsett av katalogstruktur, SOUL.md, MEMORY.md, compliance-protokoll, maler og skript.

### Fase 2 — Datainnsamling
Bruk sub-agent-allokeringer beskrevet under for å ekstrahere, kalkulere og verifisere.

### Fase 3 — Rapportering
Kompiler output etter IEEE-referansestil med Kildekompasset-siteringsregler.

## Sub-Agent Allokering via RPC

| Rolle | Funksjon | Verktøy |
|-------|----------|---------|
| **DOC-PARSE** | Ekstraherer pensum og dataark | `pandas`, `openpyxl`, `pypdf` |
| **AUDIO-PARSE** | GPU-akselerert transkripsjon av forelesningsvideoer | `yt-dlp`, `whisper-ctranslate2 --compute_type=float16 --device cuda` |
| **MATH-SOLVE** | Symbolske beregninger og LaTeX-rendring | `sympy`, Jupyter-notatbøker |
| **REG-CHECK** | Kryssverifikasjon mot COMPLIANCE_PROTOCOL.md, genererer samsvarserklæringer | Regex, dokumentanalyse |
| **PROJECT-WRITE** | Kompilerer oppgaver, tabeller og rapporter i IEEE-stil | Typst, markdown, LaTeX |

## Språk- og Siteringsmandat
- Alle utdata skal være på feilfritt, profesjonelt norsk (Bokmål)
- IEEE-sitrering i tekst: numeriske klammeparenteser `[#]` før tegnsetting
- URL-adresser skal ALDRI avsluttes med punktum (Kildekompasset-regelen)
- Klammeregler for standarder: `...som spesifisert i NEK 400 [2].`
- Klammeregler for lover: `...i henhold til FEL [1, § 16].`

## Matematiske Uttrykk
- Frittstående ligninger: `$$...$$`
- Inline-uttrykk: `$...$`
- Enkle enheter og verdier (23 cm, 180°C, 24V): REN teikst, ALDRI LaTeX

## Verifikasjonsliste for Hvert Prosjekt
Ethvert fullført ingeniørprosjekt skal inneholde:
1. Risikovurdering (matrise over farer, risiko, standarder, restrekkevidde)
2. Samsvarserklæring (eksplisitte forskrifts- og normreferanser)
3. Sluttkontroll (måltekniske resultater: isolasjon, kontinuitet, utløsertider)
4. Brukerveiledning (norsk, med nødstopp og vedlikeholdsrutiner)

## Eksterne Referanser
- `references/workspace-provisioning.md` — Fullstendig guide for opprettelse av nye arbeidsområder
- `references/siteringsregler.md` — Detaljerte Kildekompasset- og IEEE-siteringseksempler
- `references/compliance-matrix.md` — Komplett matrise over norske forskrifter og EU-standarder
