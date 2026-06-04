---
name: ekom-exam-writer
description: Skriv fullstendige eksamenssvar for EKOM-fag (Fagskolen i Nord, AUT23). Genererer case-svar med 6-delt mal: innledning, problembeskrivelse, analyse, alternativer, anbefaling, avslutning. Inkluderer prinsippskisse, måleoppgave, lovverk-referanser og bonuspoeng-elementer. Brukes sammen med ekom-solver for beregninger og ekom-lovverk for forskrift-mapping.
category: academic
triggers:
  - ekom eksamen
  - ekom case skriv
  - svar på case
  - case-løsning skriftlig
  - eksamenssvar
  - skriv oppgave
  - svar case
  - case analyse
  - eksamensk candidate
  - begrunn
  - prinsippskisse
  - måleoppgave
---

# EKOM Eksamensskriving — Full Draft Generator

Generer fullstendige, sensor-optimerte eksamenssvar for EKOM.
Skillen bruker `ekom-solver` for beregninger og `ekom-lovverk` for
lovverk-referanser. Alle beregninger KALLES via solver — estimer aldri.

## NÅR DENNE SKILLEN BRUKES

Alltid kall denne skillen når brukeren vil:
- Skrive et fullstendig eksamenssvar / case-svar
- Ha hjelp til struktur og sensor-optimering
- Generere prinsippskisser for en løsning
- Lage måleoppgaver og instrumentliste
- Vurdere alternativer med fordeler/ulemper

**Skillen KAN ikke brukes alene.** Den må kombineres med:
- `ekom-solver` — for alle beregninger (ALTIKKE estimer)
- `ekom-signal-calc` — for kabel-TV/HFC-signalberegninger spesifikt
- `ekom-lovverk` — for forskrift/standard-mapping i analyse-seksjonen

Last disse skillene ved behov.

## Eksamensformatet (3 uavhengige caser, 5 timer)

| Case | Typisk type | Varighet |
|------|-------------|----------|
| Case 1 | Felleskabling / installasjon | ~1.5t |
| Case 2 | Boligblokk med Kabel-TV | ~1.5t |
| Case 3 | Boligblokk med fiber (FTTH/PON) | ~2t |

## 6-Delt Svarstruktur (OBLIGATORISK)

Hvert case-svar SKAL følge denne strukjonen:

### Del 1 — Innledning (~0.5-1 side)
```
- Kort oppsummering av caset (2-3 setninger)
- Antakelser du gjør (eksplisitt liste)
- Oversikt over hva svaret dekker
- Oppstilling av gitt utstyr/komponenter

BONUSPOENG: Referer til relevant forskrift i innledningen.
  "I henhold til Elsikkerhetsforskriften § 4 skal ..."
```

### Del 2 — Problembeskrivelse (kort)
```
- Hovedutfordringen — hva spør case egentlig om?
- Delproblemer (a, b, c, d...)
- Kontekst: boligblokk, borettslag, antall husstander etc.

BONUSPOENG: Bruk fagterminologi korrekt.
  Ikke "fibersikkerhet" → "link budget"
  Ikke "signalsikkerhet" → "signal-nivå / SNR margin"
```

### Del 3 — Analyse (HOVEDDELEN)
```
For hvert delproblem:

a) Beregn (kall ekom-solver for alle tall)
b) Nevn formel med kilde (fra kunnskapsgraf)
c) Stegvis aritmetikk med enheter
d) Sjekk mot standard/lovverk (kall ekom-lovverk)
e) Deviasjon: Hvis case-verdi ≠ standard → forklar

MÅ HA I ANALYSE:
- Prinsippskisse (tekst-basert hvis ikke tegning)
- Lovverk-referanser (forskrift + standard + paragraf)
- Sjekk mot min/max-verdier (RX-sensitivitet, spenningsfall etc.)
- Margin-beregning (link budget – totalt tap)

PRINSIPPSKISSE (ALLTID PÅKREVDS):
```
For kabel-TV-case:
```
Amplifier → Tap XX dB → Splitter 4-vei → Tap XX dB → Avgrener XX dB → Uttak
                                                                  → Videre ...
```
For fiber-case:
```
OLT → SFP B+/C+ → Splitter 1:2 → XX km fiber → Splitter 1:32 → XX km → ONT
       TX: X dBm      Tap: X dB      Tap: X dB        Tap: X dB    P_rx: X dBm
```

BONUSPOENG i analyse:
- Referer til både forskrift OG standard
- Vis worst-case beregning (TX min, longest distance, max temperature)
- Nevn dynamisk rekkevidde (kort vs lang kunde)
```

### Del 4 — Alternativer (2-3 realistiske løsninger)
```
For HVERT alternativ:
- Beskrivelse
- Fordeler (teknisk + økonomisk)
- Ulemper (teknisk + økonomisk)
- Hvem passer dette for?

Eksempel på alternativer for fiber-case:
  Alt 1: GPON B+ med 1:32 splitter (lavt budsjett, kort rekkevidde)
  Alt 2: GPON C+ med 1:64 splitter (høy budsjett, lang rekkevidde)
  Alt 3: Aktiv Ethernet (spesielt for store avstander)

BONUSPOENG:
- Vurder fremtidig utvidelse (XGS-PON kompatibilitet?)
- Vurder hybrid løsninger (GPON + Punkt-til-punkt)
```

### Del 5 — Anbefaling (kort, tydelig)
```
- Velg ÉN løsning
- Begrunn med forskrift/standard (ikke subjektivt "den er best")
- Spesifiseringsliste (type, klasse, antall)
- Instalasjonshensyn

BONUSPOENG:
- Begrunn HVORFOR de andre alternativene ikke ble valgt
- Nevn kostnadsbesparelser eller vedlikeholdsfordeler
```

### Del 6 — Avslutning (kort)
```
- Oppsummering
- Måleoppgave (instrumenter + forventede resultater)
- Fremtidige tiltak
- Risikovurdering

MÅ HA I AVSLUTNING:
- Måleoppgave: Hvilke instrumenter? Hvilke forventede verdier?
- Risiko: Hva kan gå galt? Hvordan unngå det?

BONUSPOENG i avslutning:
- Referer til dokumentasjonskrav (Elsikkerhetsforskriften § 9)
- Nevn vedlikeholdsplan
- Vurder klimautvirkning (temperatur på fibertap)
```

## Bonuspoeng-elementer (sensor-godvilje)

Disse elementene gir "defacto bonuspoeng" ved å vise fagforståelse:

| Element | Hvor | Eksempel |
|---------|------|----------|
| **Lovverk-referanse** | Analyse | "NEK 400 krever... ifølge Elsikkerhetsforskriften § 6" |
| **Deviasjon** | Analyse | "Case oppgir 0,25 dB/km — avviker fra standard 0,35. Grunn: 1490nm GPON nedstrøm." |
| **Worst-case** | Analyse | "Ved TX min (1,5 dBm) og 20km: P_rx = -29,5 dBm < -28 dBm → UTENFOR" |
| **Dynamisk rekkevidde** | Analyse | "Kort kunde: -18 dBm, lang kunde: -26 dBm → dynamikk = 8 dB" |
| **Prinsippskisse** | Analyse | Se format over |
| **Måleoppgave** | Avslutning | "OTDR for fiber, signalnivåmeter for kabel-TV" |
| **Alternativer** | Del 4 | Minst 2 realistiske alternativer |
| **Fremtidig utvidelse** | Alt 4/6 | "Vurder XGS-PON for fremtidig oppgradering" |
| **Risiko** | Avslutning | "Feil dimensjonering kan føre til..." |
| **Dokumentasjon** | Avslutning | "Dokumentasjon oppbevares ifølge Elsikkerhetsforskriften § 9" |

## Arbeidsflyt for case-løsning

```
1. LES caset 2 ganger, marker nøkkelord
2. IDENTIFISER hvilke delproblemer (a, b, c...)
3. EKSTRAHER parametre fra case-tekst
4. KALL ekom-solver for hver beregning
5. KALL ekom-lovverk for relevante forskrifter/standarder
6. GENERER prinsippskisse
7. SKRIV analyse med grounded reasoning
8. GENERER alternativer
9. VELG og begrunn anbefaling
10. SKRIV avslutning med måleoppgave
11. GJENNOMGÅ: Er alt dekt? Er det noe mer?
```

## Kvalitetssjekk før levering

Før du leverer et case-svar, SJEKK:

```
□ Alle beregninger kjørt via ekom-solver (ikke estimert)?
□ Prinsippskisse inkludert?
□ Lovverk-referanser (forskrift + standard + paragraf)?
□ Deviasjoner forklart (hvis case-verdi ≠ standard)?
□ Sjekket mot min/max (RX-sensitivitet, spenningsfall)?
□ Minst 2 alternativer med fordeler/ulemper?
□ Anbefaling begrunnet med forskrift/standard?
□ Måleoppgave med instrumenter og forventede verdier?
□ Risikovurdering?
□ Dokumentasjonskrav nevnt?
□ Bonuspoeng-elementer inkludert?
```

## Output-format

Skriv svaret i markdown med tydelig seksjonsinndeling.
Bruk tabeller for alle beregninger og sammenligninger.
Bruk prinsippskisser i tekst-format (eller SVG hvis mulig).

Lagre til: `~/projects/study-workbench/drafts/CASE_<NAVN>.md`
