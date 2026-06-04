---
name: plc-change-log
description: "Endringslogg og fremdriftssporing for PLC-prosjekter. ALLLES les taskID i endringsloggen FØR endringer utføres, og ALLTID oppdater endringsloggen når arbeid avsluttes. Brukes sammen med plc-project-prosjekt og andre PLC skills."
version: 1.0.0
category: plc
triggers:
  - working on a PLC project that needs change tracking
  - need to update project progress log (endringslogg)
  - starting a new work session on an existing PLC project
  - completing a task in a PLC project
  - need to hand over a PLC project to another person
  - resuming PLC work after a break
---

# PLC Endringslogg — Workflow og Fremdriftssporing

Denne skillen definerer hvordan endringslogg skal brukes i alle PLC-prosjekter.
Den skal brukes sammen med `plc-project-planning` og andre PLC skills.

---

## Hovedregel: LES FØR, ETTERPÅ OPPDATER

**FØR arbeid:**
1. Åpne og les endringsloggen for prosjektet (f.eks. `endringslogg.md`)
2. Finn de igjenstående oppgavene (merket med `[ ]`)
3. Noter deg taskID for oppgaven du skal jobbe med
4. Sjekk prioritet og trussel for oppgaven
5. Les risikoen og unngåelsesmetoden i `RISIKO_` seksjonen

**ETTER arbeid:**
1. Oppdater endringsloggen → sett `[x]` for oppgaven
2. Legg til ny seksjon under UTFØRTE ENDRINGER med dato/tid
3. Skriv Hva, Hvorfor, og Hva oppnådd (referer til taskID)
4. Noter eventuelle nye problemer funnet — inkludert risikoer og hvordan de unngås
5. Oppdater session-loggen nederst
6. Skriv neste oppgave som bør gjøres

---

## TaskID-prefiks

Hver oppgave i endringsloggen har en taskID med prefiks som forteller hvor den hører til:

| Prefiks    | Betydning                              | Eksempel       |
|------------|----------------------------------------|----------------|
| `DB_`      | Datablokker (DB1-DB12)                 | `DB_001`       |
| `OB_`      | Organisasjonsblokker (OB1, OB100)      | `OB_001`       |
| `FC_`      | Funksjoner (FC1-FC5, Step0-11)         | `FC_013`       |
| `FB_`      | Funksjonsblokker (FB1-FB3)             | `FB_001`       |
| `IO_`      | I/O-liste og TIA-import filer          | `IO_001`       |
| `HMI_`     | HMI-skjermer og VBScript               | `HMI_001`      |
| `DOC_`     | Dokumentasjon (sekvensdiag, FAT, rapport) | `DOC_001`   |
| `RISIKO_`  | Risikohåndtering og -unngåelse         | `RISIKO_001`   |

---

## Prioritet

| Nivå | Betydning |
|------|-----------|
| 1    | **Kritisk** — Sikkerhet eller hovedlogikk. Må fullføres før testing. |
| 2    | **Viktig** — påvirker funksjonalitet. Bør fullføres raskt. |
| 3    | **Medium** — logging, HMI-visning, import-filer. |
| 4    | **Dokumentasjon** — rapport, sekvensdiagram, FAT-protokoll. Venter til koden er ferdig. |

---

## Trussel

| Nivå | Betydning | Hvordan unngå |
|------|-----------|---------------|
| HØY  | Feil kan føre til kollisjon, personskade, eller at sikkerhet ikke fungerer. | Test grundig i FAT. Dobbelsjekk logikk mot IO-liste. |
| MEDIUM | Feil kan føre til feil funksjon eller produksjonsstopp. | Test i FAT. Sjekk referanser mot DB-strukturer. |
| LAV  | Feil påvirker ikke sikkerhet eller kjernefunksjon. | Kan etterfølges i rapport. |

---

## Endringslogg-struktur

```markdown
================================================================================
ENDRINGSLOGG — [Prosjektnavn]
================================================================================

## UTFØRTE ENDRINGER
[DB_001] Kort beskrivelse
  Hva:    Endret fra X til Y
  Hvorfor: Problemet var Z
  Hva oppnådd: Konsistent struktur
  Status:  UTFØRT YYYY-MM-DD

## IGJENSTÅENDE OPPGAVER
[x] FC_001 Oppgavebeskrivelse (allerede krysset av)
[ ] FC_002 Oppgavebeskrivelse (igjen)
  Beskrivelse: Hva oppgaven går ut på
  Prioritet:   1-4
  Trussel:     HØY/MEDIUM/LAV

## RISIKOER OG UNNGÅELSE
[RISIKO_001] Kort risikobeskrivelse
  Trussel:   HØY — hva kan gå galt
  Unngåelse: Konkrete tiltak for å unngå risikoen
  (Dersom en risiko er nevnt, DOKUMENTER alltid hvordan den unngås)

## DESIGN-BESLUTNINGER
1. Beslutning: Hvorfor valgte vi X fremfor Y

## SESSION-LOGG
YYYY-MM-DD session N:
  UTFØRT: liste av taskIDs
  NESTE: neste oppgave
  NOTATER: Eventuelle nye problemer eller funn
```

---

## Workflow for arbeidsøkt

### 1. Start av økt
```
1. Åpne endringslogg
2. Les session-loggen for siste økt
3. Identifiser neste oppgave (_prioritet 1_)
```

### 2. Under arbeid
```
1. Referer til taskID i alle kommentarer
2. Sjekk RISIKO_ for oppgaven
3. Kryss av DB_ foer FC_ (DB-er må vaere ferdige foer FC-er som bruker dem)
4. Kryss av FC_ foer FB_ (FB-er brukes av FC-er)
```

### 3. Slutt på økt
```
1. Oppdater session-loggen
2. Noter UTFØRT taskIDs
3. Skriv NESTE oppgave
4. Oppdater statuslinjen
```

---

## Pitfalls

- **ALDRI** skriv kode foer taskID er notert fra endringslogg
- **ALDRI** stopp med halvferdig kode (foerer til inkonsistens)
- **ALDRI** endre DB-struktur uten å oppdatere alle FC/FB som referer til den
- **ALDRI** glemme å oppdatere session-loggen
- **ALLTID** sjekk at filen faktisk finnes foen du skriver om den
