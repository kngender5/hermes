# Eksempel på struktur for funksjonsbeskrivelse

Dette dokumentet viser et eksempel på hvordan en funksjonsbeskrivelse kan struktureres basert på arbeidet i prosjektoppgaven.

## 1. Systemoversikt
- Kort beskrivelse av hva systemet gjør
- Begrunnelse for valg av løsning (f.eks. valg av PLC-modell, kommunikasjonsmetode)

## 2. Maskinvare (I/O)
- Detaljert liste over digitale inn- og utganger
- For hver I/O-punkt: adresse, funksjon, begrunnelse for valg av adresse/type

## 3. Programmstruktur
### 3.1 Datablokker
- For hver DB: navn, formål, variabler (navn, datatype, beskrivelse)
- Begrunnelse for valg av datatyper og struktur

### 3.2 Sekvensstyring
- Beskrivelse av tilstandsmaskinen
- For hvert trinn: nummer, beskrivelse, hovedhandlinger, betingelse for neste trinn
- Begrunnelse for sekvenslogikken

## 4. Sikkerhetskrets
- Fysisk tilkobling av nødstopp, sensorer osv.
- PLC-logikk for sikkerhetshåndtering
- Begrunnelse for sikkerhetsarkitekturen

## 5. HMI – WinCC Flexible Runtime
- Kommunikasjon mellom PLC og HMI
- Taggkobling
- Skjermstruktur
- Begrunnelse for HMI-valg

## 6. Testing og FAT
- Referanse til detaljert testplan
- Begrunnelse for testdekning

## 7. Konklusjon
- Oppsummering av at løsningen møter kravene
- Eventuelle begrensninger eller fremtidige forbedringer

## Viktige prinsipper
- Alle tekniske valg må ha en begrunnelse
- Dokumentet skal være på norsk
- Bruk punktvis struktur for enkel lesbarhet
- Seksiér dokumentet logisk fra overordnet til detaljnivå
