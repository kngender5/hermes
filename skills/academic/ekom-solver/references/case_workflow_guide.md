# Case Workflow Guide — EKSAMENSSTRATEGI

## Grunnprinsipp for case-basert eksamen

**Hvert svar må vise REASONING** — ikke bare tall. Reasoning kan være grounded i:
- (a) FAKTA FRA CASE SELV (parametre, kontekst, gitte verdier)
- (b) FAGLIG GRUNNLAG (kunnskapsgraf, NEK-standarder, kurs-PDF-er)
- (c) DEVIASJON med eksplisitt begrunnelse (hvis case bryter standard)

## Case workflow-steg

```
1. LES case → marker parametre, spørsmål, kontekst
2. IDENTIFISER → hvilke solver-systemer? (fiber, dB, poe, docsis...)
3. KJØR solver → få alle beregnbare variabler  
4. VERIFISER → er svaret fysisk rimeligt?
5. SKRIV konklusjon → grounded reasoning fra (a)+(b)+(c)
6. POENGVIS → vis alle mellomregninger
```

## Grounded reasoning-format (per steg)

```
Steg N — [Hva beregnes]  (X poeng)
  Formel: [matematisk uttrykk]
  Beregning: [stegvis aritmetikk]
  → [resultat med enhet]

  REASONING:
  Case oppgir: [relevante parametre]
  Kilde [KG-node-label] (kildefil): [siter definisjon/prinsipp]
  Relevans: [hvorfor denne formelen passer denne case-parametern]
  
  [Hvis deviasjon:]
  ⚠️ DEVIASJON: Case bruker X, standard er Y.
  Begrunnelse: [hvorfor avviket er akseptabelt]
```

## Case bank-struktur

10 caser i `workspace_groundtruth/case_bank.jsonl`:

```
case-01: FTTH GPON B+ (medium, 10p) — fiber, pon
case-02: Signalstyrke/SNR (easy, 8p) — dB, fiber  
case-03: PoE kameraer (medium, 6p) — poe
case-04: DOCSIS 3.1 (medium, 8p) — docsis, shannon
case-05: EMC-separasjon (medium, 8p) — emc, lovverk
case-06: CWDM design (hard, 8p) — fiber, wdm
case-07: Kabel-TV budzett (easy, 5p) — kabeltv
case-08: Spenningsfall (easy, 6p) — elektro, last
case-09: Skole multi (hard, 10p) — fiber, poe, docsis, emc
case-10: Boligområde full (hard, 10p) — alt
```

Hver case inneholder: `scenario` (norsk), `params`, `steps` med `grounded_sources`, `mark_scheme`.

## Kunnskapsgraf-oppslag

210 noder i `workspace_groundtruth/knowledge_graph/`:
- `domain_fiber.jsonl` — fiber, PON, GPON, OTDR, skjøting, kabler, WDM
- `domain_db_poe_emc.jsonl` — EMC, PoE, dB, lovverk, dokumentasjon
- `domain_fiber_nodes_new.jsonl` — fiber-ny
- `domain_nek_hms_reg.jsonl` — NEK-standarder, HMS, forskrifter

Søk: `python3 ekom_case_workflow.py sources --topic <emne>`

## Verifisering av caser

Alle case-løsninger i case bank er verifisert mot `ekom_solver.py`:
```bash
# Verifiser case 1
python3 ekom_solver.py \
  -k '{"P_tx":3,"L":15,"alpha":0.35,"N_conn":4,"N_splice":8,"L_split":15,"M":3,"P_rx_min":-28}' \
  -t P_rx
# Forventet: P_rx ≈ -22,05 dBm
```

## Tilpasse egen case

Lag nye caser med samme struktur som JSONL-banken. Hvert steg må ha:
- `grounded_sources`: liste med KG-node-ID-er
- `formula`: matematisk uttrykk
- `calc`: stegvis beregning
- `result`: dict med verdi+enhet
- `points`: poeng for steget
- `grounding_reasoning`: forklaring på hvorfor valgt
