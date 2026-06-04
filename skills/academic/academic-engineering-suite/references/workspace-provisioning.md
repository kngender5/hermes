# Workspace Provisioning — Opprettelse av Akademisk Arbeidsområde

## Katalogstruktur (Standard)

```
~/projects/<workspace-name>/
├── SOUL.md                    # Identitet, språk- og resonneringsmandat
├── MEMORY.md                  # Minnebindinger, kataloglås, pre-eksekveringsregler
├── extract_canvas.py          # Canvas API-ekstraktor
├── ingest_lecture.sh          # Forelesningstranskripsjon ( chmod +x )
├── curriculum/                # Lærebøker, fagplaner, syllabus_master.xlsx
├── laws/
│   └── COMPLIANCE_PROTOCOL.md # Regulatorisk verifikasjonsprotokoll
├── video_transcripts/         # Forelesningslogger, lydspor, transkripsjoner
├── workspace_calculations/    # SymPy-skript, Jupyter-notatbøker
├── drafts/
│   └── IEEE_RAPPORT_MAL.md    # IEEE-rapportmal
├── artifacts/                 # Genererte artefakter
├── logs/                      # Kjørelogger
├── reports/                   # Risikovurderinger, samsvarserklæringer
├── references/                # Eksterne referanser
├── scripts/                   # Hjelpeskript
├── templates/                 # Dokumentmaler
└── docs/
    ├── IEEE/                  # IEEE-standardreferanser
    ├── Kildekompasset/        # Kildekompasset-retningslinjer
    └── kurs/                  # Kurs-spesifikt materiell
```

## Innholdsmessige Krav til Hovedfiler

### SOUL.md
- Kjerneidentitet med ekspertrolle
- Språk- og siteringsmandat (IEEE + Kildekompasset)
- Resonneringstoken-protokoll (PLAN, INNER_MONOLOGUE, REFLECTION)
- Matematisk rendringsregel (LaTeX for formler, ren tekst for enheter)

### MEMORY.md
- Katalogstruktur med beskrivelser per mappe
- Pre-eksekveringsport: kryssreferanse mot lokale referanser
- Eksplisitt begrensning: skal ikke påvirke global SOUL.md/MEMORY.md

### COMPLIANCE_PROTOCOL.md (under laws/)
- Elektriske lavspenningsanlegg (FEL + NEK 400)
- Elektronisk kommunikasjon (Ekomloven + NEK 700)
- Maskinsikkerhet (Maskinforskrift + ISO-standarder)
- Arbeidsmiljø (AML + Internkontrollforskriften)
- Sluttdokumentasjonsjekkliste (4 obligatoriske dokumenter)

### IEEE_RAPPORT_MAL.md (under drafts/)
- Numerisk seksjonsstruktur (I., II., III.)
- Klammesitering før tegnsetting
- Referanseliste: kronologisk rekkefølge, aldri punktum etter URL

### extract_canvas.py
- `canvasapi` + `pandas` + `dotenv`
- Laster ned alle aktive kursos filer per kurskode
- Genererer syllabus_master.xlsx med oppgaver, frister, poeng

### ingest_lecture.sh
- `yt-dlp` med cookies for autentiserte nettsteder (Panopto)
- `ffmpeg` for lydekstraksjon (mono, 16kHz, MP3)
- `whisper-ctranslate2 --model large-v3 --compute_type float16 --device cuda --language no`
- Skriptet skal kjoeres med: `./ingest_lecture.sh <VIDEO_URL>`
- Krev at cookies.txt ligger foerst i video_transcripts/-mappen

## Alias-registrering (Etter oppsett)

Brukeren bør registere et alias i ~/.bashrc for raat tilgang:
```bash
echo 'alias <navn>="cd ~/projects/<workspace>/ && hermes"' >> ~/.bashrc
```

**VIKTIG PITFALL — `.bashrc`-alias i ikke-interaktiv kontekst:**
Terminal-verktoeyets `terminal()`-kall kjoerer i en ikke-interaktiv sub-shell. Alias som er registrert i `.bashrc` er IKKE tilgjengelige der fordi `.bashrc` har en guard (`# If not running interactively, don't do anything`). Alias brukes kun i nye interaktive terminal-oekter eller etter manuelt `source ~/.bashrc`.

**VIKTIG PITFALL — Sikkerhetspolicy for dotfile-skriving:**
Kommandoer som skriver til dotfiler via `>>` (f.eks. `echo ... >> ~/.bashrc`) triggere `HIGH`-sekvensikkerhetsregelen (Dotfile overwrite detected). Disse blokkere inntil brukeren eksplisitt godkoenner. Itererende samme kommando foerer til ytterligere blokkering — vent paa brukerbekreftelse i stedet.
