---
name: ekom-solver
description: Smart utregningsverktøy + full case workflow for EKOM-fag (Fagskolen i Nord, AUT23). Dekk fiberbudsjett, dB, spenningsfall, last, EMC, kabel-TV, Shannon, DOCSIS, PoE, OTDR — med grounded reasoning fra kunnskapsgraf og interaktiv dashboard-UI.
category: academic
triggers:
  - ekom kalkulator
  - ekom regn ut
  - ekom variabler
  - ekom solver
  - fiberbudsjett kalkulator
  - dB kalkulator
  - spenningsfall kalkulator
  - EMC separasjon
  - lastberegning
  - kabel-TV kalkulator
  - PoE kalkulator
  - DOCSIS kalkulator
  - Shannon kapasitet
  - otdr simulator
  - kalkulator
  - regn ut
  - hva kan jeg regne ut
  - ekom øvelser
  - ekom eksamen
  - ekom case
  - ekom case workflow
  - ekom dashboard
  - eksamensforberedelse
---

# EKOM Utregningsverktøy + Case Workflow + Dashboard

Fiberbudsjett, dB, spenningsfall, lastberegning, EMC, kabel-TV, Shannon, DOCSIS, PoE.

**Eksamen er CASE-basert.** Hvert svar krever grounded reasoning — ikke bare tall.

## Arkitektur (3 lag + dashboard)

| Lag | Fil | Formål |
|-----|-----|--------|
| **Solver** | `workspace_calculations/ekom_solver.py` | Beregn alle variabler fra kjente verdier (9 systemer, ~70 variabler) |
| **Kalkulator** | `workspace_calculations/ekom_calculator.py` | Funksjonsbibliotek for direkte kall |
| **Case Workflow** | `workspace_calculations/ekom_case_workflow.py` | Les case → solve → generer grounded reasoning → konkluder |
| **Dashboard** | `ekom-dashboard.html` | Interaktiv nettleser-UI med kalkulatorer, formler, sjekkliste |
| **Case Bank** | `workspace_groundtruth/case_bank.jsonl` | 11 verifiserte caser med mark scheme |
| **Kunnskapsgraf** | `workspace_groundtruth/knowledge_graph/*.jsonl` | 210 noder med kilderef for grounded reasoning |

## Grounded Reasoning-prinsipp (EKSAMENSKRITISK)

Hvert beregningssteg i case-løsning må dokumentere:

1. **FAKTA FRA CASE**: Hvilke parametre gir case?
2. **FAGLIG GRUNNLAG**: Formel/standard fra kurset (med kilderef)
3. **BEREGNING**: Stegvis aritmetikk med enheter
4. **DEVIASJON (hvis aktuelt)**: Hvis case-verdi bryter standard → eksplisitt begrunnelse

Reasoning er gyldig grounded i KOMBINASJON av case-fakta + kunnskapsgraf-kilder.

**Deviasjonsregel:** Hvis case oppgir en annen verdi enn standardverdi (f.eks. 0,25 dB/km fibertap i stedet for 0,3), bruk ALLTID case-verdien og marker eksplisitt hvorfor den avviker fra standard. Begrunnelsen må være teknisk gyldig (f.eks. "G.652D ved 1550nm", "case spesifiserer annen fibertype").

```
Eksempel:
  ⚠️ DEVIASJON: Standard α for G.652D ved 1310nm = 0,35 dB/km.
  Case oppgir 0,25 dB/km. Mulig grunn: G.652D ved 1490nm (GPON nedstrøm)
  hvor α er lavere. Bruker case-verdi.
```

## Case Workflow CLI

```bash
cd ~/projects/study-workbench/workspace_calculations
python3 ekom_case_workflow.py list
python3 ekom_case_workflow.py solve --case-id case-01-gpon-design
python3 ekom_case_workflow.py practice --difficulty hard
python3 ekom_case_workflow.py practice --topic fiber
python3 ekom_case_workflow.py show case-01-gpon-design
python3 ekom_case_workflow.py sources --topic fiber
```

**Case bank:** 11 caser (3 easy, 5 medium, 3 hard). Inkluderer "Fiber til kunde 2025" (SFP-10GE-ZR).

**Case workflow guide (format, mark scheme, slik opprette nye caser):** `references/case_workflow_guide.md`

**Formel-tabeller og nøkkeltall:** `references/formulas_and_tables.md`

## Dashboard (nettleser-UI)

Interaktiv eksamens-dashboard: `ekom-dashboard.html` (study-workbench-rot).

**Inneholder:** Fiberbudsjett-kalkulator (live sliders), dB-konvertering, spenningsfall (1/3-fase), PoE, lastberegning, formelsamling, splitter-tabell, GPON SFP-klasser, NEK-krav, flashkort, forberedelses-sjekkliste, case-parser.

**Åpning:** Dobbeltklikk `ekom-dashboard.html` i filutforsker, eller `file:///home/kng/projects/study-workbench/ekom-dashboard.html`. Filen kopieres også til Windows Desktop for enkel tilgang.

**Hvis kalkulatorfaner/referanser/formler ikke bytter innhold ved klikk:**
Rotårsak er ID-mismatch i `ekom-dashboard.html`. Tab-knapper har `data-tab="ref-splitter"` mens
tab-content-div-er mangler `tab-` prefix. Fix: Sørg for at alle tab-content-IDer for ikke-calc
tabs starter med `tab-` (f.eks. `id="tab-ref-splitter"`). Kalkulator-tabs bruker `calc-{id}`
(f.eks. `id="calc-fiber"`). JS-handleren i linje 288-296 søker `getElementById('tab-'+targetId)`
og fallerer stille hvis den ikke finnes → alle tabs deaktivert, ingen aktivert.

**Bonuspoeng/godvilje fra sensor:** Sensor gir "defacto bonuspoeng" for å vise fagforståelse utover
kun tall. Inkluder ALLTID i eksamenssvar:
- Prinsippskisse (alltid påkrevd — tekstbasert hvis ikke tegning)
- Lovverk-referanser: forskrift + standard + paragraf (ikke bare "NEK sier...")
- Deviasjonsforklaringer når case-verdier avviker fra standard
- Worst-case-beregning (TX min, lengste avstand, max temperatur)
- Dynamisk rekkevidde (kort vs lang kunde i PON)
- Måleoppgave med instrumenter og forventede verdier/toleranser
- 2-3 alternativer med fordeler/ulemper
- Risikovurdering og dokumentasjonskrav (Elsikkerhetsforskriften § 9)
- Fremtidig utvidelse/vedlikehold

Se `ekom-exam-writer` og `ekom-lovverk` skills for detaljert bonuspoeng-mal.
**Dashboard-debugging:** `references/dashboard-debug-guide.md` for tab-ID-mismatch-fix.

## Variabel-key mapping (KRITISK)

Bruk ALLTID disse nøklene i solver-kall (ikke symboler):

| Variabel | Key | Merknad |
|----------|-----|---------|
| Sendeffekt | `P_tx` | dBm |
| Mottatt effekt | `P_rx` | dBm |
| Min mottakseffekt | `P_rx_min` | dBm |
| Max mottakseffekt | `P_rx_max` | dBm |
| Fiberlengde | `L` | km |
| Dempningskoeffisient | `alpha` | dB/km |
| Konnektorer | `N_conn` | stk |
| Skjøt | `N_splice` | stk |
| Splittertap fiber | `L_split` | dB — IKKE `L_split_kt` |
| Systemmargin fiber | `M` | dB — IKKE `M_qam` |
| Totalt tap | `L_tot` | dB |
| Gjenstående margin | `margin` | dB (NB: ikke M) |
| Snittertap kabel-TV | `L_split_kt` | dB — suffiks `_kt` |
| QAM-nivå DOCSIS | `M_qam` | — suffiks `_qam` |
| Kabeltap kabel-TV | `L_kabel` | dB |
| PoE PSE-effekt | `P_pse` | W |
| PoE PD-effekt | `P_pd` | W |
| PoE spenning | `V_poe` | V |
| PoE strøm | `I_poe` | A |
| Kabelresistans | `R_loss` | Ω |
| PoE kabeltap | `P_loss` | W |
| Virkningsgrad | `eff_poe` | — |
| EMC N-tot | `N_tot` | stk — delt med last-N! |
| Samtidighetsfaktor | `ks` | — |

**PITFALL — Dict-kollisjon:** `V = { dict }` i solver: siste `dict[key] =` vinner. Alltid bruk namespaced keys (`_kt`, `_qam`). Ved endring: sjekk duplikater.

## Verifisering av svar

```bash
# GPON B+ budsjett
python3 ekom_solver.py -k '{"P_tx":3,"L":10,"alpha":0.35,"N_conn":4,"N_splice":6,"L_split":15,"M":3,"P_rx_min":-28}'

# PoE: PSE, kabeltap, PD
python3 ekom_solver.py -k '{"V_poe":48,"I_poe":0.5,"R_loss":10,"eff_poe":0.88}'

# DOCSIS: kapasitet per 8MHz-kanal (EuroDOCSIS)
python3 ekom_solver.py -k '{"B":8e6,"M_qam":256,"overhead":0.1}'

# Shannon
python3 ekom_solver.py -k '{"B":1e6,"SNR_dB":30}'

# Spenningsfall 1-fase
python3 ekom_solver.py -k '{"I":15,"L":80,"rho":0.0175,"A":4}'
```

## Korrigerte verdier (PITFALL)

| Parameter | Feil (før) | Rett (etter) | Kilde |
|-----------|-----------|-------------|-------|
| SM_1550 dB/km | 0,20 | **0,22** | Fiberoptikk PDF |
| MM_850 dB/km | 3,0 | **2,5** | Fiber-types |
| MM_1300 dB/km | 1,0 | **0,6** | Fiber-types |

**G.652D:** Bruk 0,35 dB/km ved 1310nm (typisk design), 0,22 dB/km ved 1550nm. 0,40 er ITU-T maks.

## GPON SFP-klasser (MÅ KJENNE)

| Klasse | TX min | TX max | RX følsomhet | Overload | Budsjett |
|--------|--------|--------|--------------|----------|----------|
| **B+** | 1,5 dBm | 5,0 dBm | **−28 dBm** | −8 dBm | 29–33 dB |
| **C+** | 3,0 dBm | 7,0 dBm | **−32 dBm** | −12 dBm | 35–39 dB |

## PoE-standarder (MÅ KJENNE)

| Standard | Navn | PSE max | PD max | Par | Spenning |
|----------|------|---------|--------|-----|----------|
| 802.3af | PoE | 15,4 W | 12,95 W | 2 | 44–57 V |
| 802.3at | PoE+ | 30 W | 25,5 W | 2 | 50–57 V |
| 802.3bt T3 | PoE++ | 60 W | 51 W | 4 | 52–57 V |
| 802.3bt T4 | UPoE | 100 W | 71 W | 4 | 52–57 V |

## Eksamensfallgruber

- **10·log₁₀ for EFFEKT, 20·log₁₀ for SPENNING**
- **Splittertap gjelder BEGGE retninger** (ned og opp i PON)
- **Shannon = teoretisk maks** — praktisk er alltid lavere
- **EuroDOCSIS = 8 MHz kanaler**, ikke 6 MHz
- **ρ kobber = 0,0175 Ω·mm²/m**
- **Margin = LB − L_tot** (bruk key `margin`, ikke `M`)

## TX-min-fallgruke (kritisk)

**ALLTID test både TX min og TX max.** En link kan passere ved TX max (+5 dBm) men feile ved TX min (0 dBm) når margin < TX-variasjonsrekke (5 dB for B+). Krev minimum 2 dB ekstra margin i anbefalingen, eller spesifiser minimum TX i konklusjonen.

## Filer

| Fil | Beskrivelse |
|-----|-------------|
| `workspace_calculations/ekom_solver.py` | Hovedsolver (9 systemer) |
| `workspace_calculations/ekom_calculator.py` | Funksjonskalkulator |
| `workspace_calculations/ekom_case_workflow.py` | Case workflow |
| `workspace_calculations/otdr_simulator.py` | OTDR-simulator |
| `workspace_groundtruth/case_bank.jsonl` | 11 verifiserte caser |
| `workspace_groundtruth/knowledge_graph/` | 210 kunnskapsnoder |
| `workspace_groundtruth/verification.json` | 215 verifiserte verdier |
| `drafts/EKOM_EKSAMENSNOTATER.md` | Eksamensnotater (18 kap.) |
| `drafts/EKOM_PRACTICE_PROBLEMS.md` | Øvelsesoppgaver |
| `drafts/EKOM_CHEAT_SHEET.md` | Hurtigreferanse |
| `drafts/CASE_FIBER_TIL_KUNDE_2025.md` | Løst case |
| `ekom-dashboard.html` | Interaktiv dashboard-UI |
| **Skills** | `ekom-exam-writer` — 6-delt eksamenssvar med bonuspoeng |
| | `ekom-signal-calc` — Kabel-TV/HFC signalberegninger |
| | `ekom-lovverk` — Forskrift/standard-mapping for grounded reasoning |
