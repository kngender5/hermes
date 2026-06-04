# Compliance Verification Reference (2026-05-25)

## Norwegian Regulatory Source Priority

When verifying any technical or regulatory claim, search in this order:

### 1. Local Cache (fastest, most reliable)
- `~/projects/study-workbench/laws/COMPLIANCE_PROTOCOL.md` — Expanded reference with tables
- `~/projects/study-workbench/curriculum/` — Course-specific PDF materials
- `~/projects/study-workbench/drafts/NEK_701_702_DETALJERT.md` — NEK standard details

### 2. Norwegian Authorities (authoritative)
- **Nkom** (Nasjonal kommunikasjonsmyndighet): `site:nkom.no <query>`
  - Ekomloven, Ekomforskriften, Autorisasjonsforskriften, frekvensallokering
- **Lovdata**: `site:lovdata.no <lov/forskrift> <§-nummer>`
  - FEL, Ekomloven, AML, Internkontrollforskriften, Maskinforskriften

### 3. Standards Bodies
- **NEK** (Norsk Elektroteknisk Komite): `site:nek.no <standard-nummer>`
  - NEK 400, NEK 700-serien, fiber standarder
- **ITU-T**: `site:itu.int <G-series/O-series>`
  - G.652, G.984 (GPON), G.987 (XG-PON), G.694.1 (CWDM)
- **ISO/IEC**: `site:iso.org <standard-nummer>`
  - ISO 12100, ISO 13849, ISO 10218

### 4. Industry Sources
- **Fiberforeningen**: Splitterdempning, installasjonsstandarder
- **Telenor/Altibox**: Teknisk dokumentasjon, produktspesifikasjoner

### 5. Academic (for theoretical concepts)
- `site:arxiv.org <query>` — Research papers
- University course pages (NTNU, UiT)

### 6. International Fallback
- Wikipedia — mark as `PROVISIONAL` in notes

## Search Patterns for Common Claims

| Claim Type | Search Pattern |
|-----------|----------------|
| Fiber splitter loss | `site:nek.no splitterdempning fiber` or check SPLITTER_LOSS table |
| GPON SFP specs | `site:itu.int G.984 SFP class` or GPON SFP table |
| NEK 700 structure | `site:nek.no NEK 701 702` or NEK_701_702_DETALJERT.md |
| Cable-TV signal levels | `site:nkom.no kabel-TV signalnivå` or HFC frequency plan table |
| PoE power levels | Check POE_STANDARDS table in ekom_calculator.py |
| DOCSIS versions | Check DOCSIS_VERSIONS table in ekom_calculator.py |
| EMC separation | Check EMC separation table in COMPLIANCE_PROTOCOL.md |

## Status Markers for Claims
- `VERIFIED_SOURCE` — Confirmed against primary source (NEK, Nkom, Lovdata)
- `DERIVED` — Calculated from verified primary values
- `PROVISIONAL` — From secondary source (Wikipedia, industry blog), needs primary verification
- `CONFLICT` — Contradicts another source, needs resolution
